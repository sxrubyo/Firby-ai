# -*- coding: utf-8 -*-
"""Motor LLM Multi-Proveedor modularizado de globals.py."""
from __future__ import annotations
import os
import re
import json
import time
import random
import logging
import asyncio
import httpx
from typing import List, Dict, Tuple, Optional, Any, Set, Union
from abc import ABC, abstractmethod
import hashlib

log = logging.getLogger("firby.llm_engine")

# Proxies dinámicos para evitar import circular en la inicialización
from src.firby.core.proxy import GlobalProxy

db = GlobalProxy("db")
Config = GlobalProxy("Config")
sector_closing_scripts = GlobalProxy("sector_closing_scripts")
now_col = GlobalProxy("now_col")
owner_style_controller = GlobalProxy("owner_style_controller")
v8_build_quality_system_prompt_addon = GlobalProxy("v8_build_quality_system_prompt_addon")
trainer_get_system_prompt_addon = GlobalProxy("trainer_get_system_prompt_addon")

def _nuke_robot_apply(*args, **kwargs):
    import src.core.globals as g
    return g._nuke_robot_apply(*args, **kwargs)

# Imports estáticos seguros (clases, enums y helpers necesarios para la definición de firmas y ejecución)
from src.firby.core.models import (
    IntentType, SentimentType, UrgencyLevel, MessageAnalysis, ConversationState,
    PersonalityProfile, MemoryItem, Task, MCPPlugin
)
get_sector_info = GlobalProxy("get_sector_info")
apply_archetype = GlobalProxy("apply_archetype")
_first_contact_intro = GlobalProxy("_first_contact_intro")
_normalize_conv_text = GlobalProxy("_normalize_conv_text")
_KB_AVAILABLE = GlobalProxy("_KB_AVAILABLE")
format_kb_context = GlobalProxy("format_kb_context")
looks_fragmented_reply = GlobalProxy("looks_fragmented_reply")
_I18N_BOT = GlobalProxy("_I18N_BOT")
detect_user_language = GlobalProxy("detect_user_language")
SUPPORTED_LANGUAGES = GlobalProxy("SUPPORTED_LANGUAGES")
PromptBuilderDeps = GlobalProxy("PromptBuilderDeps")

class LLMProvider:
    """Interfaz base para proveedores LLM."""
    name: str = "base"

    async def complete(self, messages: List[Dict], model: str,
                       temperature: float = 0.7, max_tokens: int = 1000,
                       **kwargs) -> Tuple[str, Dict]:
        raise NotImplementedError

    async def embed(self, text: str) -> List[float]:
        raise NotImplementedError


def _parse_http_json_response(response: httpx.Response, provider_name: str) -> Dict[str, Any]:
    body = response.text or ""
    stripped = body.strip()
    content_type = (response.headers.get("content-type") or "").strip() or "unknown"
    if not stripped:
        raise ValueError(f"{provider_name} devolvió body vacío [{content_type}]")
    try:
        parsed = response.json()
    except Exception as exc:
        snippet = re.sub(r"\s+", " ", stripped)[:220]
        raise ValueError(
            f"{provider_name} devolvió body no-JSON [{content_type}]: {snippet}"
        ) from exc
    if not isinstance(parsed, dict):
        raise ValueError(f"{provider_name} devolvió JSON no-objeto [{content_type}]")
    return parsed


class GroqProvider(LLMProvider):
    """Groq — el mas rapido (~500ms). Llama-3.3-70b."""
    name = "groq"
    BASE  = "https://api.groq.com/openai/v1"
    MDLS  = {"reasoning": "llama-3.3-70b-versatile",
              "fast":      "llama-3.3-70b-versatile",
              "lite":      "llama-3.1-8b-instant"}

    def __init__(self, key: str): self.key = key

    async def complete(self, messages, model="fast", temperature=0.7, max_tokens=1000, **kw):
        start = time.time()
        if isinstance(model, str) and model in self.MDLS:
            m = self.MDLS[model]
        elif isinstance(model, str) and model.startswith("groq/"):
            m = model.split("/", 1)[1]
        elif isinstance(model, str) and model not in ("fast", "reasoning", "lite"):
            m = model
        else:
            m = self.MDLS["fast"]
        async with httpx.AsyncClient(timeout=15.0) as c:
            r = await c.post(f"{self.BASE}/chat/completions",
                headers={"Authorization": f"Bearer {self.key}", "Content-Type": "application/json"},
                json={"model": m, "messages": messages, "temperature": temperature, "max_tokens": max_tokens})
            r.raise_for_status()
        payload = _parse_http_json_response(r, self.name)
        text = payload["choices"][0]["message"]["content"].strip()
        return text, {"model": m, "latency_ms": int((time.time()-start)*1000), "provider": "groq"}

    async def embed(self, text):
        raise NotImplementedError


class GeminiProvider(LLMProvider):
    """Google Gemini directo. Soporta rotacion de claves."""
    name = "gemini"
    BASE  = "https://generativelanguage.googleapis.com/v1beta"
    MDLS  = {"reasoning": "gemini-3.5-flash",        # Pro / Reasoning vanguardia 3.5
              "fast":      "gemini-2.5-flash",        # Flash ultra-rápido 2.5
              "lite":      "gemini-2.5-flash-lite"}

    def __init__(self, key: str, label: str = "gemini"):
        self.key   = key
        self.name  = label

    async def complete(self, messages, model="fast", temperature=0.7, max_tokens=1000, **kw):
        start = time.time()
        if isinstance(model, str) and "lite" in model:
            gm = "gemini-2.5-flash-lite"
        elif isinstance(model, str) and "pro" in model:
            gm = "gemini-2.5-pro"
        else:
            gm = "gemini-2.5-flash"
        system_parts, contents = [], []
        for m in messages:
            if m["role"] == "system":
                system_parts.append({"text": m["content"]})
            elif m["role"] == "user":
                contents.append({"role": "user",  "parts": [{"text": m["content"]}]})
            elif m["role"] == "assistant":
                contents.append({"role": "model", "parts": [{"text": m["content"]}]})
        gen_config = {"temperature": temperature, "maxOutputTokens": max_tokens}
        if "gemini-2.5-flash" in gm:
            gen_config["thinkingConfig"] = {"thinkingBudget": 0}
        elif "gemini-2.5-pro" in gm:
            # Pro utiliza razonamiento obligatorio que cuenta hacia maxOutputTokens; subimos el límite
            gen_config["maxOutputTokens"] = max(max_tokens, 4000)
            
        payload = {"contents": contents, "generationConfig": gen_config}
        if kw.get("tools"):
            payload["tools"] = kw["tools"]
        if system_parts:
            payload["systemInstruction"] = {"parts": system_parts}
        url = f"{self.BASE}/models/{gm}:generateContent?key={self.key}"
        async with httpx.AsyncClient(timeout=12.0) as c:
            r = await c.post(url, json=payload)
            r.raise_for_status()
        payload = _parse_http_json_response(r, self.name)
        text = payload["candidates"][0]["content"]["parts"][0]["text"].strip()
        return text, {"model": gm, "latency_ms": int((time.time()-start)*1000), "provider": self.name}

    async def embed(self, text):
        url = f"{self.BASE}/models/text-embedding-004:embedContent?key={self.key}"
        async with httpx.AsyncClient(timeout=30.0) as c:
            r = await c.post(url, json={"content": {"parts": [{"text": text}]}})
            r.raise_for_status()
        return r.json()["embedding"]["values"]


class OpenRouterProvider(LLMProvider):
    """OpenRouter — acceso a todos los modelos."""
    name = "openrouter"
    BASE  = "https://openrouter.ai/api/v1"
    MDLS  = {"reasoning": "google/gemini-3.5-flash",
              "fast":      "google/gemini-2.5-flash",
              "lite":      "google/gemini-2.5-flash-lite"}

    def __init__(self, key: str): self.key = key

    async def complete(self, messages, model="fast", temperature=0.7, max_tokens=1000, **kw):
        start = time.time()
        m = self.MDLS.get(model, model if isinstance(model, str) else self.MDLS["fast"])
        async with httpx.AsyncClient(timeout=25.0) as c:
            r = await c.post(f"{self.BASE}/chat/completions",
                headers={"Authorization": f"Bearer {self.key}", "Content-Type": "application/json",
                         "HTTP-Referer": "https://firby.ai", "X-Title": "Firby Ultra"},
                json={"model": m, "messages": messages, "temperature": temperature, "max_tokens": max_tokens})
            r.raise_for_status()
        payload = _parse_http_json_response(r, self.name)
        text = payload["choices"][0]["message"]["content"].strip()
        return text, {"model": m, "latency_ms": int((time.time()-start)*1000), "provider": "openrouter"}

    async def embed(self, text):
        async with httpx.AsyncClient(timeout=30.0) as c:
            r = await c.post(f"{self.BASE}/embeddings",
                headers={"Authorization": f"Bearer {self.key}", "Content-Type": "application/json"},
                json={"model": "openai/text-embedding-3-small", "input": text})
            r.raise_for_status()
        return r.json()["data"][0]["embedding"]


class OpenAIProvider(LLMProvider):
    """OpenAI — ultimo recurso."""
    name = "openai"
    BASE  = "https://api.openai.com/v1"
    MDLS  = {"reasoning": "gpt-4o", "fast": "gpt-4o-mini", "lite": "gpt-4o-mini"}

    def __init__(self, key: str): self.key = key

    async def complete(self, messages, model="fast", temperature=0.7, max_tokens=1000, **kw):
        start = time.time()
        if isinstance(model, str) and model in self.MDLS:
            m = self.MDLS[model]
        elif isinstance(model, str) and model.startswith("openai/"):
            m = model.split("/", 1)[1]
        elif isinstance(model, str) and model.startswith("gpt-"):
            m = model
        else:
            m = self.MDLS["fast"]
        async with httpx.AsyncClient(timeout=25.0) as c:
            r = await c.post(f"{self.BASE}/chat/completions",
                headers={"Authorization": f"Bearer {self.key}", "Content-Type": "application/json"},
                json={"model": m, "messages": messages, "temperature": temperature, "max_tokens": max_tokens})
            r.raise_for_status()
        payload = _parse_http_json_response(r, self.name)
        text = payload["choices"][0]["message"]["content"].strip()
        return text, {"model": m, "latency_ms": int((time.time()-start)*1000), "provider": "openai"}

    async def embed(self, text):
        async with httpx.AsyncClient(timeout=30.0) as c:
            r = await c.post(f"{self.BASE}/embeddings",
                headers={"Authorization": f"Bearer {self.key}", "Content-Type": "application/json"},
                json={"model": "text-embedding-3-small", "input": text})
            r.raise_for_status()
        return r.json()["data"][0]["embedding"]


class LLMServiceError(RuntimeError):
    """Raised when all LLM providers fail and callers must not hide the real cause."""

    def __init__(self, message: str, *, attempted: Optional[List[str]] = None, last_error: Optional[Exception] = None):
        super().__init__(message)
        self.attempted = attempted or []
        self.last_error = last_error
        self.public_message = self._build_public_message()

    def _build_public_message(self) -> str:
        raw = str(self.last_error or self)
        low = raw.lower()
        provider_txt = ", ".join(self.attempted) if self.attempted else "proveedor LLM"
        if "429" in raw or "resource_exhausted" in low or "quota" in low or "rate" in low:
            return (
                f"El modelo no respondió porque la API llegó al límite de cuota/rate limit en {provider_txt}.\n"
                f"Detalle técnico: {raw[:700]}"
            )
        if "401" in raw or "403" in raw or "api key" in low or "unauthorized" in low:
            return (
                f"El modelo no respondió porque la API key parece inválida o sin permisos en {provider_txt}.\n"
                f"Detalle técnico: {raw[:700]}"
            )
        return f"El modelo no respondió en {provider_txt}.\nDetalle técnico: {raw[:700]}"


class LLMEngine:
    """
    Motor LLM con cascada de 6 proveedores.
    Groq -> Gemini(key1) -> Gemini(key2) -> Gemini(key3) -> OpenRouter -> OpenAI

    V8.1 — Fixes de fallos silenciosos:
    - Blacklist temporal (60s) en vez de permanente
    - Detección de respuesta vacía o inválida
    - Timeout de provider < timeout de caller (nunca zombie)
    - _push_to_engine solo en OpenRouter (único multi-modelo real)
    - Métricas de fallo por provider en DB para diagnóstico
    """

    # Providers que soportan modelos externos (OpenRouter puede usar cualquier modelo)
    _MULTI_MODEL_PROVIDERS = {"openrouter"}

    def __init__(self):
        self.providers: List[LLMProvider] = []
        self._failures:     Dict[str, int]   = {}   # conteo de fallos
        self._blocked_until: Dict[str, float] = {}  # timestamp hasta cuando está bloqueado
        self._last_success: Dict[str, float] = {}
        self._blacklist_ttl  = 15.0   # segundos de bloqueo tras 3 fallos consecutivos
        self._cache: Dict[str, Tuple[str, float]] = {}
        self._cache_ttl = 300

        if Config.GROQ_API_KEY:
            self.providers.append(GroqProvider(Config.GROQ_API_KEY))
            log.info("[llm] Groq OK")
        _all_gemini_keys = Config.GEMINI_API_KEYS or [
            Config.GEMINI_API_KEY,   Config.GEMINI_API_KEY_2,
            Config.GEMINI_API_KEY_3, Config.GEMINI_API_KEY_4,
            Config.GEMINI_API_KEY_5, Config.GEMINI_API_KEY_6,
        ]
        for i, key in enumerate(_all_gemini_keys):
            if key:
                self.providers.append(GeminiProvider(key, f"gemini_k{i+1}"))
                log.info(f"[llm] Gemini key{i+1} OK")
        if Config.OPENROUTER_API_KEY:
            self.providers.append(OpenRouterProvider(Config.OPENROUTER_API_KEY))
            log.info("[llm] OpenRouter OK")
        if Config.OPENAI_API_KEY:
            self.providers.append(OpenAIProvider(Config.OPENAI_API_KEY))
            log.info("[llm] OpenAI OK")

        n = len(self.providers)
        if n == 0:
            log.critical("[llm] SIN PROVEEDORES — el bot no podra generar respuestas inteligentes")
        else:
            log.info(f"[llm] cascada lista: {n} proveedores")

    def _hash(self, messages, **kw):
        return hashlib.md5((json.dumps(messages, sort_keys=True) + json.dumps(kw, sort_keys=True)).encode(), usedforsecurity=False).hexdigest()

    def _get_requested_model(self, model_tier: str) -> str:
        try:
            if model_manager:
                effective = model_manager.get_effective_models()
                chosen = effective.get(model_tier)
                if chosen:
                    return chosen
        except Exception:
            pass
        return Config.LLM_MODELS.get(model_tier, model_tier)

    def _ordered_providers(self, requested_model: str) -> List[LLMProvider]:
        providers = list(self.providers)

        def _priority(provider: LLMProvider) -> int:
            name = provider.name
            if requested_model.startswith("google/") or requested_model.startswith("gemini-"):
                if name.startswith("gemini"):
                    return 0
                if name == "openrouter":
                    return 1
                return 2
            if requested_model.startswith("anthropic/") or requested_model.startswith("meta-llama/") or requested_model.startswith("mistralai/"):
                if name == "openrouter":
                    return 0
                return 2
            if requested_model.startswith("openai/") or requested_model.startswith("gpt-"):
                if name == "openai":
                    return 0
                if name == "openrouter":
                    return 1
                return 2
            if requested_model.startswith("groq/") or requested_model.startswith("llama-"):
                if name == "groq":
                    return 0
                if name == "openrouter":
                    return 1
                return 2
            return 0

        return sorted(
            providers,
            key=lambda provider: (
                _priority(provider),
                self._failures.get(provider.name, 0),
                -self._last_success.get(provider.name, 0.0),
                provider.name,
            ),
        )

    def _resolve_provider_model(self, provider: LLMProvider,
                                requested_model: str,
                                model_tier: str) -> str:
        name = provider.name
        if name.startswith("gemini") and (
            requested_model.startswith("google/") or requested_model.startswith("gemini-")
        ):
            return requested_model
        if name == "openai" and (
            requested_model.startswith("openai/") or requested_model.startswith("gpt-")
        ):
            return requested_model
        if name == "groq" and (
            requested_model.startswith("groq/") or requested_model.startswith("llama-")
        ):
            return requested_model
        if name == "openrouter":
            return requested_model
        return model_tier

    def _is_blocked(self, provider_name: str) -> bool:
        """Blacklist temporal: bloqueado solo por _blacklist_ttl segundos."""
        until = self._blocked_until.get(provider_name, 0)
        if until and time.time() < until:
            return True
        # Tiempo expirado — resetear fallos para darle otra oportunidad
        if until and time.time() >= until:
            self._failures[provider_name] = 0
            self._blocked_until[provider_name] = 0
            log.info(f"[llm] {provider_name} desbloqueado (blacklist expirado)")
        return False

    def _register_failure(self, provider_name: str, error: Exception):
        """Registra un fallo y bloquea si acumula 3 consecutivos."""
        self._failures[provider_name] = self._failures.get(provider_name, 0) + 1
        count = self._failures[provider_name]
        log.warning(f"[llm] {provider_name} fallo #{count}: {str(error)[:100]}")
        status_code = getattr(getattr(error, "response", None), "status_code", None)
        block_after = 3
        block_ttl = self._blacklist_ttl  # 15s
        if status_code in (401, 402, 403):
            block_after = 1
            block_ttl = 1800.0  # 30 min para auth/payment errors
        elif status_code in (429, 500, 502, 503, 504) or isinstance(error, (asyncio.TimeoutError, TimeoutError)):
            block_after = 3  # 3 fallos consecutivos antes de bloquear
            block_ttl = 15.0  # solo 15s de bloqueo
        if count >= block_after:
            self._blocked_until[provider_name] = time.time() + block_ttl
            log.error(f"[llm] {provider_name} BLOQUEADO por {block_ttl}s tras {count} fallo(s)")

    def clear_blocks(self):
        """Desbloquea todos los proveedores de LLM inmediatamente."""
        self._blocked_until.clear()
        self._failures.clear()
        # Guardar métrica en DB para que el admin pueda ver con /v8
        try:
            if db:
                db.record_metric("llm_failure", provider_name, count,
                                 {"error": str(error)[:80], "blocked": count >= block_after, "status_code": status_code})
        except Exception:
            pass

    def _is_valid_response(self, text: str) -> bool:
        """Detecta respuestas vacías o inválidas que no deben llegar al usuario."""
        if not text or not text.strip():
            return False
        stripped = text.strip()
        # Respuesta puramente de error del API
        if stripped.startswith("Error") and len(stripped) < 30:
            return False
        # JSON de error de OpenRouter / Gemini que se filtró
        if stripped.startswith('{"error"') or stripped.startswith('{"status"'):
            return False
        return True

    async def complete(self, messages: List[Dict],
                       model_tier: str = "fast",
                       temperature: float = 0.7,
                       max_tokens: int = 1000,
                       use_cache: bool = True,
                       **kwargs) -> Tuple[str, Dict]:
        requested_model = self._get_requested_model(model_tier)
        if use_cache and db:
            ck = self._hash(messages, t=temperature, m=max_tokens,
                            tier=model_tier, requested_model=requested_model)
            cached = db.get_cached_response(ck)
            if cached and self._is_valid_response(cached):
                return cached, {"cached": True}

        last_error = None
        attempted  = []
        for provider in self._ordered_providers(requested_model):
            if self._is_blocked(provider.name):
                log.debug(f"[llm] {provider.name} saltado (blacklist activo)")
                continue
            attempted.append(provider.name)
            try:
                provider_model = self._resolve_provider_model(provider, requested_model, model_tier)
                # Timeout del provider siempre menor que el del caller
                # para evitar zombies. El caller (admin_brain) usa 12s,
                # los providers internos usan hasta 25s — reducimos aquí.
                response, metadata = await asyncio.wait_for(
                    provider.complete(
                        messages, model=provider_model,
                        temperature=temperature, max_tokens=max_tokens, **kwargs),
                    timeout=9.0   # 9.0s por proveedor para acomodar respuestas razonadas sin falsos timeouts
                )

                # Verificar que la respuesta sea válida — no vacía ni error
                if not self._is_valid_response(response):
                    err = ValueError(f"respuesta inválida/vacía: '{response[:40]}'")
                    self._register_failure(provider.name, err)
                    last_error = err
                    log.warning(f"[llm] {provider.name} devolvió respuesta inválida — siguiente")
                    continue

                # Éxito — resetear fallos
                self._failures[provider.name] = 0
                self._last_success[provider.name] = time.time()
                if use_cache and db:
                    db.cache_response(ck, response)
                if db:
                    db.record_metric("llm", "completion",
                                     metadata.get("latency_ms", 0),
                                     {"provider": metadata.get("provider"), "tier": model_tier,
                                      "requested_model": requested_model})
                log.info(
                    f"[llm] {provider.name} OK ({metadata.get('latency_ms',0)}ms) | "
                    f"tier={model_tier} requested={requested_model}"
                )
                return response, metadata

            except asyncio.TimeoutError as e:
                te = TimeoutError(f"timeout 10s")
                self._register_failure(provider.name, te)
                last_error = te
            except Exception as e:
                self._register_failure(provider.name, e)
                last_error = e

        providers_tried = ", ".join(attempted) if attempted else "ninguno"
        raise RuntimeError(f"Todos los LLM fallaron [{providers_tried}]: {last_error}")

    def get_health(self) -> Dict:
        """Estado de salud de cada provider. Usado por /v8 y diagnóstico."""
        now = time.time()
        result = {}
        for p in self.providers:
            blocked_until = self._blocked_until.get(p.name, 0)
            result[p.name] = {
                "failures": self._failures.get(p.name, 0),
                "blocked":  now < blocked_until,
                "unblocks_in": max(0, int(blocked_until - now)) if now < blocked_until else 0,
            }
        return result

    async def embed(self, text: str) -> List[float]:
        for p in self.providers:
            try:
                return await p.embed(text)
            except Exception:
                continue
        return self._simple_embedding(text)

    def _simple_embedding(self, text: str, dim: int = 384) -> List[float]:
        words = text.lower().split()
        vec = [0.0] * dim
        for i, w in enumerate(words[:dim]):
            vec[i % dim] += hash(w) % 100 / 100.0
        norm = math.sqrt(sum(x*x for x in vec))
        return [x/norm for x in vec] if norm > 0 else vec


# Instancia global
llm_engine: LLMEngine = None

def init_llm():
    import src.core.globals as g
    global llm_engine
    llm_engine = LLMEngine()
    g.llm_engine = llm_engine

# ═══════════════════════════════════════════════════════════════════════════════
# ANALIZADOR DE MENSAJES AVANZADO
# ═══════════════════════════════════════════════════════════════════════════════

class MessageAnalyzer:
    """Analizador de mensajes con múltiples capas."""
    
    # Patrones de intención
    INTENT_PATTERNS = {
        IntentType.GREETING: [
            r'\b(hola|buenas?|hey|hi|saludos|buenos?\s*(dias?|tardes?|noches?))\b',
            r'^(que\s*tal|como\s*estas?|que\s*hay)\b'
        ],
        IntentType.APPOINTMENT_REQUEST: [
            r'\b(cita|agendar|reservar|programar|turno|horario\s*disponible)\b',
            r'\b(quiero|necesito|puedo|podria|quisiera)\s*(una?\s*)?(cita|turno|hora)\b',
            r'\b(cuando\s*puedo\s*ir|tienen\s*disponibilidad)\b'
        ],
        IntentType.APPOINTMENT_CANCEL: [
            r'\b(cancelar?|anular?)\s*(mi)?\s*(cita|turno)\b',
            r'\bno\s*puedo\s*(ir|asistir)\b'
        ],
        IntentType.APPOINTMENT_RESCHEDULE: [
            r'\b(cambiar?|reprogramar?|mover?|reagendar?)\s*(mi)?\s*(cita|turno)\b',
            r'\b(otro\s*dia|otra\s*hora|otra\s*fecha)\b'
        ],
        IntentType.PRICE_INQUIRY: [
            r'\b(precio|costo|valor|cuanto\s*(vale|cuesta|cobran?|es)|tarifa|cotizacion)\b',
            r'\b(que\s*precio|cual\s*es\s*el\s*precio)\b'
        ],
        IntentType.SERVICE_INFO: [
            r'\b(que\s*es|como\s*(es|funciona|se\s*hace)|en\s*que\s*consiste)\b',
            r'\b(informacion|info|detalles?|explicar?)\s*(sobre|de|del)\b',
            r'\b(duele|durar?|resultados?|recuperacion|contraindicaciones?)\b'
        ],
        IntentType.LOCATION_INQUIRY: [
            r'\b(donde\s*(esta[ns]?|queda[ns]?)|direccion|ubicacion|como\s*llego)\b',
            r'\b(mapa|ruta|transporte)\b'
        ],
        IntentType.HOURS_INQUIRY: [
            r'\b(horario|hora|cuando\s*(abren|cierran|atienden))\b',
            r'\b(a\s*que\s*hora|hasta\s*que\s*hora)\b'
        ],
        IntentType.COMPLAINT: [
            r'\b(queja|reclamo|molest[ao]|mal\s*servicio|decepcionad[ao])\b',
            r'\b(no\s*me\s*gust[oa]|muy\s*mal|pesimo|horrible)\b'
        ],
        IntentType.COMPLIMENT: [
            r'\b(excelente|gracias?|genial|increible|muy\s*bien|perfecto)\b',
            r'\b(buen\s*servicio|me\s*encant[oa]|recomiendo)\b'
        ],
        IntentType.EMERGENCY: [
            r'\b(urgente|emergencia|urgencia|dolor\s*fuerte|sangr[ae]|accidente)\b',
            r'\b(ayuda|socorro|grave)\b'
        ],
        IntentType.CONFIRMATION: [
            r'^(si|sip|sep|ok|okay|vale|listo|correcto|exacto|claro|por\s*supuesto|dale)$',
            r'\b(confirm[ao]|de\s*acuerdo|asi\s*es)\b'
        ],
        IntentType.DENIAL: [
            r'^(no|nop|nel|nah|negativo)$',
            r'\b(no\s*gracias|no\s*quiero|no\s*puedo|cancelar?)\b'
        ]
    }
    
    # Palabras de sentimiento
    SENTIMENT_WORDS = {
        "positive": [
            "gracias", "excelente", "genial", "perfecto", "increible", "maravilloso",
            "encanta", "amor", "feliz", "contento", "satisfecho", "recomiendo",
            "profesional", "amable", "rapido", "eficiente", "bien"
        ],
        "negative": [
            "mal", "terrible", "horrible", "pesimo", "decepcion", "molesto",
            "enojado", "frustrado", "lento", "caro", "malo", "odio", "nunca",
            "jamas", "peor", "queja", "reclamo", "problema", "error"
        ]
    }
    
    # Palabras de urgencia
    URGENCY_WORDS = {
        UrgencyLevel.CRITICAL: ["emergencia", "urgente", "sangre", "accidente", "grave", "ayuda"],
        UrgencyLevel.HIGH: ["dolor", "molestia", "hoy", "ahora", "rapido", "inmediato"],
        UrgencyLevel.MEDIUM: ["pronto", "esta semana", "necesito", "importante"],
    }
    
    def __init__(self):
        self._compiled_patterns = {}
        for intent, patterns in self.INTENT_PATTERNS.items():
            self._compiled_patterns[intent] = [
                re.compile(p, re.IGNORECASE | re.UNICODE) 
                for p in patterns
            ]
    
    def analyze(self, text: str, context: List[Dict] = None) -> MessageAnalysis:
        """Análisis completo del mensaje."""
        cleaned = self._clean_text(text)
        
        # Detectar intención
        intent, confidence, secondary = self._detect_intent(cleaned)
        
        # Detectar sentimiento
        sentiment, sentiment_score = self._detect_sentiment(cleaned)
        
        # Detectar urgencia
        urgency = self._detect_urgency(cleaned)
        
        # Extraer entidades
        entities = self._extract_entities(cleaned)
        
        # Extraer keywords
        keywords = self._extract_keywords(cleaned)
        
        # Determinar estado emocional
        emotional_state = self._infer_emotional_state(sentiment, urgency, cleaned)
        
        # Determinar si requiere acción
        requires_action = intent in [
            IntentType.APPOINTMENT_REQUEST,
            IntentType.APPOINTMENT_CANCEL,
            IntentType.APPOINTMENT_RESCHEDULE,
            IntentType.EMERGENCY,
            IntentType.COMPLAINT
        ]
        
        # Determinar si requiere búsqueda
        requires_search = intent in [
            IntentType.PRICE_INQUIRY,
            IntentType.SERVICE_INFO
        ] or any(kw in cleaned.lower() for kw in [
            "cuanto", "precio", "costo", "como funciona", "que es", 
            "efectos", "resultados", "duracion"
        ])
        
        # ── Closing score y temperatura del lead ─────────────────────────────
        closing_score, lead_temperature = self._calc_closing_score(
            cleaned, intent, sentiment, urgency, context or []
        )

        # ── Detección de idioma ───────────────────────────────────────────────
        language = self._detect_language(cleaned)

        return MessageAnalysis(
            raw_text=text,
            cleaned_text=cleaned,
            intent=intent,
            intent_confidence=confidence,
            secondary_intents=secondary,
            sentiment=sentiment,
            sentiment_score=sentiment_score,
            urgency=urgency,
            entities=entities,
            keywords=keywords,
            language=language,
            is_question="?" in text or any(q in cleaned.lower() for q in [
                "que", "como", "cuando", "donde", "cual", "cuanto", "porque"
            ]),
            requires_action=requires_action,
            requires_search=requires_search,
            emotional_state=emotional_state,
            context_references=self._find_context_references(cleaned, context or []),
            closing_score=closing_score,
            lead_temperature=lead_temperature,
        )
    
    def _calc_closing_score(self, text: str, intent: IntentType,
                             sentiment: SentimentType, urgency: UrgencyLevel,
                             context: List[Dict]) -> tuple:
        """
        Calcula la probabilidad de cierre (0-1) y la temperatura del lead.
        Se basa en señales de compra detectadas en el texto y el contexto.
        """
        score = 0.0
        text_low = text.lower()

        # Señales de intención directa de compra/cita
        HOT_SIGNALS = [
            "cuándo puedo", "cómo agendo", "quiero ir", "quiero venir",
            "voy a ir", "apártame", "sepáralo", "lo quiero", "lo reservo",
            "cuándo tienen espacio", "para mañana", "para hoy",
            "dónde quedan", "cómo llego", "me dan el precio",
            "qué necesito llevar", "se necesita cita", "cuánto demora",
        ]
        WARM_SIGNALS = [
            "me interesa", "cuánto vale", "qué precio", "tienen disponible",
            "qué incluye", "me puedes contar", "qué diferencia",
            "han trabajado con", "tienen experiencia", "cuánto tiempo",
        ]
        COLD_SIGNALS = [
            "lo voy a pensar", "después te escribo", "no sé si",
            "no tengo plata", "está caro", "en otro lado",
        ]

        hot_count  = sum(1 for s in HOT_SIGNALS  if s in text_low)
        warm_count = sum(1 for s in WARM_SIGNALS if s in text_low)
        cold_count = sum(1 for s in COLD_SIGNALS if s in text_low)

        score += hot_count  * 0.25
        score += warm_count * 0.12
        score -= cold_count * 0.20

        # Ajuste por intención
        if intent == IntentType.APPOINTMENT_REQUEST:    score += 0.35
        elif intent == IntentType.PRICE_INQUIRY:        score += 0.15
        elif intent == IntentType.SERVICE_INFO:         score += 0.10
        elif intent == IntentType.COMPLAINT:            score -= 0.15

        # Ajuste por sentimiento
        if sentiment in (SentimentType.POSITIVE, SentimentType.VERY_POSITIVE): score += 0.10
        elif sentiment == SentimentType.VERY_NEGATIVE:  score -= 0.20

        # Ajuste por urgencia
        if urgency == UrgencyLevel.CRITICAL: score += 0.20
        elif urgency == UrgencyLevel.HIGH:   score += 0.10

        # Ajuste por contexto — cuántos mensajes lleva (más msgs = más caliente)
        msg_count = len(context)
        if msg_count >= 4:  score += 0.05
        if msg_count >= 8:  score += 0.10

        # Clamp 0-1
        score = max(0.0, min(1.0, score))

        # Temperatura
        if score >= 0.75:   temperature = "boiling"
        elif score >= 0.50: temperature = "hot"
        elif score >= 0.25: temperature = "warm"
        else:               temperature = "cold"

        return score, temperature

    def _detect_language(self, text: str) -> str:
        """Detección de idioma usando módulo i18n o heurística."""
        if _I18N_BOT:
            detected = detect_user_language(text)
            if detected in SUPPORTED_LANGUAGES:
                return detected
        
        text_low = text.lower()
        ES_WORDS = ["que", "por", "para", "con", "una", "del", "los", "las",
                    "hola", "buenas", "gracias", "claro", "sí", "cómo", "qué"]
        EN_WORDS = ["the", "and", "for", "with", "you", "what", "how",
                    "hello", "thanks", "please", "have", "that", "this"]
        PT_WORDS = ["que", "para", "com", "uma", "obrigado", "boa", "sim",
                    "olá", "você", "como", "fazer"]
        FR_WORDS = ["bonjour", "merci", "vous", "pour", "avec", "une", "les",
                    "je", "que", "comment"]
        DE_WORDS = ["hallo", "danke", "für", "mit", "eine", "die",
                    "ich", "wie", "was", "haben"]

        es = sum(1 for w in ES_WORDS if f" {w} " in f" {text_low} ")
        en = sum(1 for w in EN_WORDS if f" {w} " in f" {text_low} ")
        pt = sum(1 for w in PT_WORDS if f" {w} " in f" {text_low} ")
        fr = sum(1 for w in FR_WORDS if f" {w} " in f" {text_low} ")
        de = sum(1 for w in DE_WORDS if f" {w} " in f" {text_low} ")

        scores = {"es": es, "en": en, "pt": pt, "fr": fr, "de": de}
        best = max(scores.items(), key=lambda x: x[1])
        
        if best[1] > 0:
            return best[0]
        return "es"

    def _clean_text(self, text: str) -> str:
        """Limpia el texto para análisis."""
        # Remover emojis
        emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"
            "\U0001F300-\U0001F5FF"
            "\U0001F680-\U0001F6FF"
            "\U0001F1E0-\U0001F1FF"
            "\U00002500-\U00002BEF"
            "\U00002702-\U000027B0"
            "\U0001F900-\U0001F9FF"
            "\U0001FA00-\U0001FAFF"
            "]+",
            flags=re.UNICODE
        )
        text = emoji_pattern.sub("", text)
        
        # Normalizar espacios
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def _detect_intent(self, text: str) -> Tuple[IntentType, float, List[Tuple[IntentType, float]]]:
        """Detecta intención con confianza."""
        scores = {}
        
        for intent, patterns in self._compiled_patterns.items():
            score = 0
            for pattern in patterns:
                matches = pattern.findall(text)
                score += len(matches) * (1.0 / len(patterns))
            scores[intent] = min(score, 1.0)
        
        # Ordenar por score
        sorted_intents = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        
        if sorted_intents[0][1] > 0:
            primary = sorted_intents[0][0]
            confidence = sorted_intents[0][1]
            secondary = [(i, s) for i, s in sorted_intents[1:4] if s > 0.2]
        else:
            # Sin match claro
            if "?" in text:
                primary = IntentType.GENERAL_QUESTION
            else:
                primary = IntentType.CHITCHAT
            confidence = 0.5
            secondary = []
        
        return primary, confidence, secondary
    
    def _detect_sentiment(self, text: str) -> Tuple[SentimentType, float]:
        """Detecta sentimiento."""
        text_lower = text.lower()
        
        pos_count = sum(1 for w in self.SENTIMENT_WORDS["positive"] if w in text_lower)
        neg_count = sum(1 for w in self.SENTIMENT_WORDS["negative"] if w in text_lower)
        
        # Score de -1 a 1
        total = pos_count + neg_count
        if total == 0:
            return SentimentType.NEUTRAL, 0.0
        
        score = (pos_count - neg_count) / total
        
        if score > 0.5:
            return SentimentType.VERY_POSITIVE, score
        elif score > 0.1:
            return SentimentType.POSITIVE, score
        elif score < -0.5:
            return SentimentType.VERY_NEGATIVE, score
        elif score < -0.1:
            return SentimentType.NEGATIVE, score
        else:
            return SentimentType.NEUTRAL, score
    
    def _detect_urgency(self, text: str) -> UrgencyLevel:
        """Detecta nivel de urgencia."""
        text_lower = text.lower()
        
        for level in [UrgencyLevel.CRITICAL, UrgencyLevel.HIGH, UrgencyLevel.MEDIUM]:
            if any(w in text_lower for w in self.URGENCY_WORDS.get(level, [])):
                return level
        
        return UrgencyLevel.NONE
    
    def _extract_entities(self, text: str) -> Dict[str, Any]:
        """Extrae entidades del texto."""
        entities = {}
        
        # Teléfonos
        phone_pattern = r'[\+]?[\d\s\-\(\)]{7,15}'
        phones = re.findall(phone_pattern, text)
        if phones:
            entities["phones"] = [p.strip() for p in phones]
        
        # Emails
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        emails = re.findall(email_pattern, text)
        if emails:
            entities["emails"] = emails
        
        # Fechas (patrones comunes en español)
        date_patterns = [
            r'\b(\d{1,2})\s*(?:de\s*)?(enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre)\b',
            r'\b(lunes|martes|miercoles|jueves|viernes|sabado|domingo)\b',
            r'\b(hoy|mañana|pasado\s*mañana|esta\s*semana|proxima?\s*semana)\b',
            r'\b(\d{1,2})[/\-](\d{1,2})(?:[/\-](\d{2,4}))?\b'
        ]
        
        dates = []
        for pattern in date_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            dates.extend(matches)
        if dates:
            entities["dates"] = dates
        
        # Horas
        time_pattern = r'\b(\d{1,2})(?::(\d{2}))?\s*(am|pm|hrs?|horas?)?\b'
        times = re.findall(time_pattern, text, re.IGNORECASE)
        if times:
            entities["times"] = times
        
        # Nombres propios (mayúsculas después de saludos comunes)
        name_pattern = r'(?:soy|me\s*llamo|mi\s*nombre\s*es)\s+([A-ZÁÉÍÓÚÑ][a-záéíóúñ]+(?:\s+[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+)*)'
        names = re.findall(name_pattern, text)
        if names:
            entities["names"] = names
        
        return entities
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extrae palabras clave."""
        # Stopwords en español
        stopwords = {
            "el", "la", "los", "las", "un", "una", "unos", "unas",
            "de", "del", "al", "a", "en", "con", "por", "para",
            "que", "como", "cuando", "donde", "cual", "quien",
            "este", "esta", "estos", "estas", "ese", "esa",
            "mi", "tu", "su", "me", "te", "se", "nos", "les",
            "y", "o", "pero", "si", "no", "mas", "muy", "ya",
            "es", "son", "era", "fue", "ser", "estar", "hay",
            "hola", "buenas", "gracias", "por favor"
        }
        
        words = re.findall(r'\b[a-záéíóúüñ]{3,}\b', text.lower())
        keywords = [w for w in words if w not in stopwords]
        
        # Frecuencia
        freq = {}
        for w in keywords:
            freq[w] = freq.get(w, 0) + 1
        
        # Top keywords
        sorted_kw = sorted(freq.items(), key=lambda x: x[1], reverse=True)
        return [kw for kw, _ in sorted_kw[:10]]
    
    def _infer_emotional_state(self, sentiment: SentimentType, 
                               urgency: UrgencyLevel, text: str) -> str:
        """Infiere estado emocional."""
        if urgency == UrgencyLevel.CRITICAL:
            return "ansioso/urgente"
        
        if sentiment == SentimentType.VERY_NEGATIVE:
            return "frustrado/molesto"
        elif sentiment == SentimentType.NEGATIVE:
            return "insatisfecho"
        elif sentiment == SentimentType.VERY_POSITIVE:
            return "entusiasta/agradecido"
        elif sentiment == SentimentType.POSITIVE:
            return "satisfecho"
        
        # Analizar patrones específicos
        text_lower = text.lower()
        if any(w in text_lower for w in ["nervios", "miedo", "preocupa"]):
            return "nervioso/preocupado"
        if any(w in text_lower for w in ["duda", "no se", "no estoy segur"]):
            return "indeciso"
        if any(w in text_lower for w in ["curioso", "interesa", "quiero saber"]):
            return "curioso"
        
        return "neutral"
    
    def _find_context_references(self, text: str, context: List[Dict]) -> List[str]:
        """Encuentra referencias al contexto previo."""
        references = []
        
        pronouns = ["eso", "esto", "aquello", "lo", "la", "el", "ella", "ellos"]
        text_lower = text.lower()
        
        for pronoun in pronouns:
            if re.search(rf'\b{pronoun}\b', text_lower):
                # Buscar a qué podría referirse en el contexto
                for i, msg in enumerate(reversed(context[-5:])):
                    content = msg.get("content", "").lower()
                    # Heurística simple: buscar sustantivos en contexto reciente
                    nouns = re.findall(r'\b[a-z]{4,}\b', content)
                    if nouns:
                        references.append(f"posible_ref:{nouns[0]}")
                        break
        
        return references

# Instancia global
analyzer = MessageAnalyzer()

# ═══════════════════════════════════════════════════════════════════════════════
# MOTOR DE RAZONAMIENTO CHAIN-OF-THOUGHT
# ═══════════════════════════════════════════════════════════════════════════════

class ReasoningEngine:
    """Motor de razonamiento avanzado con Chain-of-Thought."""
    
    REASONING_PROMPT = """Eres un sistema de razonamiento avanzado. Tu tarea es analizar la situación y generar una estrategia de respuesta óptima.

## ANÁLISIS RECIBIDO
Intención detectada: {intent}
Confianza: {confidence}%
Sentimiento: {sentiment}
Urgencia: {urgency}
Estado emocional: {emotional_state}
Entidades extraídas: {entities}
Requiere búsqueda: {requires_search}

## CONTEXTO DE LA CLÍNICA
{clinic_context}

## HISTORIAL RECIENTE
{history}

## MENSAJE ACTUAL
"{message}"

## INSTRUCCIONES
Razona paso a paso:

1. **Comprensión**: Qué está pidiendo realmente el paciente?
2. **Contexto**: Hay información previa relevante?
3. **Recursos necesarios**: Necesito buscar información? Consultar agenda?
4. **Estrategia de respuesta**: Cómo debo estructurar la respuesta?
5. **Tono**: Qué tono es apropiado dado el estado emocional?
6. **Acciones**: Qué acciones concretas debo tomar?

Responde en formato JSON:
```json
{{
  "understanding": "...",
  "context_relevance": "...",
  "resources_needed": ["..."],
  "response_strategy": "...",
  "tone_recommendation": "...",
  "actions": ["..."],
  "response_outline": "...",
  "confidence": 0.0-1.0
}}
```"""

    def __init__(self, llm: LLMEngine):
        self.llm = llm

    def _extract_json_candidates(self, raw: str) -> List[str]:
        text = (raw or "").strip()
        if not text:
            return []
        candidates: List[str] = []

        for block in re.findall(r"```(?:json)?\s*(.*?)\s*```", text, re.DOTALL | re.IGNORECASE):
            block = (block or "").strip()
            if block:
                candidates.append(block)

        if text.startswith("{") and text.endswith("}"):
            candidates.append(text)

        start_positions = [idx for idx, ch in enumerate(text) if ch == "{"][:8]
        for start in start_positions:
            depth = 0
            in_string = False
            escaped = False
            for idx in range(start, len(text)):
                ch = text[idx]
                if in_string:
                    if escaped:
                        escaped = False
                    elif ch == "\\":
                        escaped = True
                    elif ch == '"':
                        in_string = False
                    continue
                if ch == '"':
                    in_string = True
                    continue
                if ch == "{":
                    depth += 1
                elif ch == "}":
                    depth -= 1
                    if depth == 0:
                        snippet = text[start : idx + 1].strip()
                        if snippet:
                            candidates.append(snippet)
                        break
        deduped: List[str] = []
        seen: Set[str] = set()
        for candidate in candidates:
            normalized = candidate.strip()
            if not normalized or normalized in seen:
                continue
            seen.add(normalized)
            deduped.append(normalized)
        return deduped

    def _parse_reasoning_response(self, raw: str) -> Optional[Dict[str, Any]]:
        for candidate in self._extract_json_candidates(raw):
            try:
                parsed = json.loads(candidate)
            except Exception:
                continue
            if isinstance(parsed, dict):
                return parsed
        return None

    def _extract_labeled_value(self, raw: str, labels: List[str]) -> str:
        text = (raw or "").strip()
        for label in labels:
            match = re.search(
                rf"{label}\s*[:\-]\s*(.+?)(?:\n[A-ZÁÉÍÓÚÜÑ][^:\n]{{0,40}}[:\-]|\n\d+\.\s|\Z)",
                text,
                flags=re.IGNORECASE | re.DOTALL,
            )
            if match:
                value = re.sub(r"\s+", " ", match.group(1)).strip(" \n\t\"'`")
                if value:
                    return value
        return ""

    def _extract_actions_from_text(self, raw: str, analysis: MessageAnalysis) -> List[str]:
        lines = []
        for line in (raw or "").splitlines():
            cleaned = line.strip().lstrip("-*•0123456789. ").strip()
            if len(cleaned) >= 4:
                lines.append(cleaned)
        if not lines:
            if analysis.requires_search:
                lines.append("validar información antes de responder")
            if analysis.intent.name in {"book_appointment", "ask_schedule"}:
                lines.append("guiar hacia disponibilidad o valoración")
        deduped: List[str] = []
        seen: Set[str] = set()
        for line in lines[:6]:
            key = _normalize_conv_text(line)
            if key and key not in seen:
                seen.add(key)
                deduped.append(line)
        return deduped

    def _fallback_reasoning_payload(
        self,
        raw: str,
        message: str,
        analysis: MessageAnalysis,
        clinic: Dict,
        history: List[Dict],
        conv_state: Optional["ConversationState"] = None,
    ) -> Dict[str, Any]:
        outline = re.sub(r"\s+", " ", (raw or "").strip())
        if len(outline) > 280:
            outline = outline[:277].rstrip() + "..."
        context_hint = "hay historial útil" if history else "primer contacto"
        phase_hint = getattr(conv_state, "phase", "") or ""
        pending = getattr(conv_state, "pending_questions", []) or []
        last_intent = getattr(getattr(conv_state, "last_intent", None), "name", "") or ""
        strategy = "respuesta clara y útil"
        if phase_hint == "appointment":
            strategy = "cerrar la cita o pedir el dato mínimo faltante"
        elif phase_hint == "info_gathering":
            strategy = "resolver la duda y pedir solo el dato mínimo faltante"
        elif analysis.requires_search:
            strategy = "responder con cautela y validar información antes de afirmar algo"
        if pending:
            strategy += f"; pendiente: {pending[0]}"
        return {
            "understanding": self._extract_labeled_value(raw, ["understanding", "comprension", "comprensión"]) or message[:180],
            "context_relevance": self._extract_labeled_value(raw, ["context_relevance", "contexto", "context"]) or (f"{context_hint}; fase={phase_hint or 'sin fase'}"),
            "resources_needed": ["búsqueda"] if analysis.requires_search else [],
            "response_strategy": self._extract_labeled_value(raw, ["response_strategy", "estrategia", "strategy"]) or strategy,
            "tone_recommendation": self._extract_labeled_value(raw, ["tone_recommendation", "tono", "tone"]) or "profesional y humana",
            "actions": self._extract_actions_from_text(raw, analysis) + ([f"respetar continuidad con {last_intent}"] if last_intent else []),
            "response_outline": self._extract_labeled_value(raw, ["response_outline", "outline", "respuesta"]) or outline,
            "confidence": max(0.35, min(0.95, float(getattr(analysis, "intent_confidence", 0.5) or 0.5))),
            "_parse_mode": "text-fallback",
        }

    def _normalize_reasoning_payload(
        self,
        parsed: Dict[str, Any],
        raw: str,
        message: str,
        analysis: MessageAnalysis,
        clinic: Dict,
        history: List[Dict],
        conv_state: Optional["ConversationState"] = None,
    ) -> Dict[str, Any]:
        payload = dict(parsed or {})
        fallback = self._fallback_reasoning_payload(raw, message, analysis, clinic, history, conv_state=conv_state)
        for key, value in fallback.items():
            current = payload.get(key)
            if current in (None, "", []):
                payload[key] = value
        actions = payload.get("actions")
        if isinstance(actions, str):
            payload["actions"] = [actions.strip()] if actions.strip() else []
        elif not isinstance(actions, list):
            payload["actions"] = fallback.get("actions", [])
        resources = payload.get("resources_needed")
        if isinstance(resources, str):
            payload["resources_needed"] = [resources.strip()] if resources.strip() else []
        elif not isinstance(resources, list):
            payload["resources_needed"] = fallback.get("resources_needed", [])
        try:
            payload["confidence"] = max(0.0, min(1.0, float(payload.get("confidence", fallback["confidence"]))))
        except Exception:
            payload["confidence"] = fallback["confidence"]
        return payload
    
    async def reason(self, 
                    message: str,
                    analysis: MessageAnalysis,
                    clinic: Dict,
                    history: List[Dict],
                    conv_state: ConversationState) -> Dict:
        """Ejecuta razonamiento sobre el mensaje."""
        
        # Preparar contexto de la clínica
        clinic_context = self._format_clinic_context(clinic)
        
        # Formatear historial
        history_str = self._format_history(history[-10:])
        
        # Construir prompt de razonamiento
        prompt = self.REASONING_PROMPT.format(
            intent=analysis.intent.name,
            confidence=int(analysis.intent_confidence * 100),
            sentiment=analysis.sentiment.name,
            urgency=analysis.urgency.name,
            emotional_state=analysis.emotional_state,
            entities=json.dumps(analysis.entities, ensure_ascii=False),
            requires_search=analysis.requires_search,
            clinic_context=clinic_context,
            history=history_str,
            message=message
        )
        
        messages = [
            {
                "role": "system",
                "content": "Analiza la situación y responde únicamente con JSON válido."
            },
            {"role": "user", "content": prompt}
        ]
        
        try:
            response, metadata = await self.llm.complete(
                messages,
                model_tier="reasoning",
                temperature=0.3,
                max_tokens=800
            )

            reasoning = self._parse_reasoning_response(response)
            if reasoning is None:
                reasoning = self._fallback_reasoning_payload(
                    response,
                    message,
                    analysis,
                    clinic,
                    history,
                    conv_state=conv_state,
                )
            else:
                reasoning = self._normalize_reasoning_payload(
                    reasoning,
                    response,
                    message,
                    analysis,
                    clinic,
                    history,
                    conv_state=conv_state,
                )
            reasoning["_metadata"] = metadata
            return reasoning
            
        except Exception as e:
            log.warning(f"Reasoning failed: {e}")
            fallback = self._fallback_reasoning_payload(
                "",
                message,
                analysis,
                clinic,
                history,
                conv_state=conv_state,
            )
            fallback["_parse_mode"] = "exception-fallback"
            fallback["_error"] = str(e)
            fallback["_error_type"] = type(e).__name__
            fallback["_metadata"] = {"provider": "local-fallback", "model": "reasoning-fallback"}
            return fallback
    
    def _format_clinic_context(self, clinic: Dict) -> str:
        services = clinic.get("services", [])
        schedule = clinic.get("schedule", {})
        
        return f"""Nombre: {clinic.get('name', 'Sin nombre')}
Servicios: {', '.join(services) if services else 'No definidos'}
Horario: {json.dumps(schedule, ensure_ascii=False) if schedule else 'No definido'}
Teléfono: {clinic.get('phone', 'No disponible')}
Dirección: {clinic.get('address', 'No disponible')}"""
    
    def _format_history(self, history: List[Dict]) -> str:
        if not history:
            return "(Primera interacción)"
        
        lines = []
        for msg in history:
            role = "Paciente" if msg["role"] == "user" else "Firby"
            content = msg['content'][:300]
            suffix = "..." if len(msg['content']) > 300 else ""
            lines.append(f"{role}: {content}{suffix}")
        
        return "\n".join(lines[-6:])

# ═══════════════════════════════════════════════════════════════════════════════
# GENERADOR DE RESPUESTAS
# ═══════════════════════════════════════════════════════════════════════════════

class ResponseGenerator:
    """Generador de respuestas humanizadas."""
    
    def __init__(self, llm: LLMEngine, learning_engine: AdminLearningEngine = None):
        self.llm = llm
        self.learning = learning_engine
    
    async def generate(self,
                      message: str,
                      analysis: MessageAnalysis,
                      reasoning: Dict,
                      clinic: Dict,
                      patient: Dict,
                      history: List[Dict],
                      search_context: str = "",
                      personality: PersonalityProfile = None,
                      kb_context: str = "",
                      chat_id: str = "") -> str:
        """Genera respuesta óptima."""
        
        # --- SWARM V3 INTERCEPT ---
        try:
            from src.domain.swarm.queen import swarm_queen
            import json
            persona_config = clinic.get("persona_config", {})
            if isinstance(persona_config, str):
                try:
                    persona_config = json.loads(persona_config) if persona_config else {}
                except Exception:
                    persona_config = {}
            agent_name = persona_config.get("name", "Firby")
            swarm_res = await swarm_queen.process(message, {**clinic, "agent_name": agent_name}, history=history)
            if swarm_res and len(swarm_res) > 0:
                return json.dumps(swarm_res, ensure_ascii=False)
        except ImportError:
            pass # Aún no está listo el paquete en todos los tests
        except Exception as e:
            import logging
            logging.getLogger("firby.swarm").warning(f"[swarm] QueenCoordinator fallback: {e}")
        # --- END SWARM V3 ---
        
        personality = personality or self._get_default_personality(clinic)
        effective_history = list(history or [])
        compact_summary = ""
        pre_prompt_injection = ""

        # Resolver ID de instancia y cargar memoria/conocimiento del cliente
        instance_id = "default"
        instance_mem = ""
        try:
            from src.core.globals import db
            remembered_slug = (db.recall("instance_slug") or "").strip() if db else ""
            meta = _load_instance_metadata()
            meta_slug = str(meta.get("name") or "").strip() if isinstance(meta, dict) else ""
            
            import os
            from pathlib import Path
            cwd_name = Path.cwd().name
            cwd_fallback = cwd_name if cwd_name in ("clinica-de-las-americas", "melissa-x", "test") else ""
            
            clinic_slug = ""
            if clinic:
                clinic_name = clinic.get("name") or clinic.get("tagline") or ""
                if clinic_name:
                    import re
                    clinic_slug = re.sub(r'[^a-z0-9_-]', '', clinic_name.lower().replace(" ", "-"))
            
            candidates = [remembered_slug, meta_slug, os.getenv("INSTANCE_ID", "").strip(), cwd_fallback, clinic_slug]
            for c in candidates:
                if c:
                    c_clean = c.strip().lower()
                    if c_clean:
                        for base_dir in [Path("/home/ubuntu/firby-instances"), Path("/home/ubuntu/firby/instances"), Path("instances")]:
                            if (base_dir / c_clean).exists():
                                instance_id = c_clean
                                break
                    if instance_id != "default":
                        break
            if instance_id == "default":
                for c in candidates:
                    if c and c.strip():
                        instance_id = c.strip().lower()
                        break

            from firby_memory import get_memory
            mem = get_memory(instance_id)
            mem.init_instance()
            instance_mem = mem.load_context()
        except Exception as e:
            import logging
            logging.getLogger("firby").warning(f"[prompt] error loading memory for instance {instance_id}: {e}")

        # Inyectar aprendizaje natural
        if self.learning:
            learning_injection = self.learning.get_prompt_injection()
            if learning_injection:
                pre_prompt_injection += learning_injection + "\n"

        if instance_mem:
            pre_prompt_injection += (
                f"\n## CONOCIMIENTO Y APRENDIZAJE DE LA INSTANCIA ({instance_id}):\n"
                f"{instance_mem}\n"
            )

        if Config.FIRBY_COMPACT_PROMPT:
            effective_history, compact_summary = self._prepare_effective_history(
                chat_id=chat_id,
                history=effective_history,
            )
            if chat_id:
                from src.interfaces.web.app import v8_extended_pre_prompt_injection
                pre_prompt_injection += v8_extended_pre_prompt_injection(
                    chat_id=chat_id,
                    user_msg=message,
                    history=effective_history,
                    clinic=clinic,
                )
            system_prompt = self._build_compact_system_prompt(
                clinic=clinic,
                patient=patient,
                personality=personality,
                search_context=search_context,
                reasoning=reasoning,
                kb_context=kb_context,
                context_summary=compact_summary,
                pre_prompt_injection=pre_prompt_injection,
                chat_id=chat_id,
                history=effective_history,
            )
        else:
            effective_kb_context = kb_context or ""
            if pre_prompt_injection:
                effective_kb_context += "\n" + pre_prompt_injection
            system_prompt = self._build_system_prompt(
                clinic, patient, personality, search_context, reasoning, effective_kb_context,
                user_msg=message, chat_id=chat_id, history=history
            )
        
        messages = [{"role": "system", "content": system_prompt}]
        
        # Agregar historial
        for msg in effective_history:
            messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })
        
        # Mensaje actual
        messages.append({"role": "user", "content": message})
        
        # Determinar modelo según complejidad.
        # En primer contacto priorizamos naturalidad y velocidad.
        model_tier = "fast"
        is_first_turn = not any(msg.get("role") == "assistant" for msg in (history or []))
        if analysis.intent in [IntentType.COMPLAINT, IntentType.EMERGENCY]:
            model_tier = "reasoning"
        elif reasoning.get("confidence", 1) < 0.6 and not is_first_turn:
            model_tier = "reasoning"
        
        # Temperatura dinámica: sube progresivamente con la conversación
        # Turno 1-2 → 0.45 (predecible, cordial)  |  6+ → 0.88 (natural, creativa)
        _turns = sum(1 for m in (history or []) if m.get("role") == "user")
        if analysis.intent in ("COMPLAINT", "EMERGENCY", "complaint", "emergency"):
            _dyn_temp = 0.35  # emergencias: precisión > creatividad
        elif _turns <= 2:  _dyn_temp = 0.45
        elif _turns <= 5:  _dyn_temp = 0.65
        elif _turns <= 10: _dyn_temp = 0.80
        else:              _dyn_temp = 0.88

        response, metadata = await self.llm.complete(
            messages,
            model_tier=model_tier,
            temperature=_dyn_temp,
            max_tokens=600,
            use_cache=False,  # cada conversación merece respuesta fresca del LLM
        )
        
        # Post-procesamiento + reintento si sigue sonando bot o rompe reglas del dueño
        response = self._apply_output_pipeline(
            response=response,
            personality=personality,
            chat_id=chat_id,
            clinic=clinic,
            user_msg=message,
            history=history,
        )
        response = await self._retry_until_human(
            messages=messages,
            response=response,
            model_tier=model_tier,
            personality=personality,
            chat_id=chat_id,
            clinic=clinic,
            user_msg=message,
            history=history,
        )
        
        return response
    
    def _get_default_personality(self, clinic: Dict) -> PersonalityProfile:
        """
        Obtiene perfil de personalidad.
        Si tiene archetype configurado → usa apply_archetype().
        Si tiene config manual → respeta los valores.
        Si no tiene nada → amigable por defecto.
        """
        persona_config = clinic.get("persona_config", {})
        if isinstance(persona_config, str):
            try:
                persona_config = json.loads(persona_config) if persona_config else {}
            except Exception:
                persona_config = {}

        agent_name = clinic.get("assistant_name") or persona_config.get("name") or persona_config.get("assistant_name") or "Valentina"
        if agent_name.lower() in ("firby", "lucia", "lucía"):
            agent_name = clinic.get("assistant_name") or "Valentina"

        # Si tiene un arquetipo configurado → aplicarlo como base
        archetype_id = persona_config.get("archetype", "amigable")
        profile = apply_archetype(archetype_id, agent_name)

        # Overrides manuales (si el admin ajustó algo por encima del arquetipo)
        if "formality_level" in persona_config:
            profile.formality_level = float(persona_config["formality_level"])
        if "warmth_level" in persona_config:
            profile.warmth_level = float(persona_config["warmth_level"])
        if "humor_level" in persona_config:
            profile.humor_level = float(persona_config["humor_level"])
        if "forbidden_words" in persona_config:
            profile.forbidden_words = persona_config["forbidden_words"]
        if "custom_phrases" in persona_config:
            profile.custom_phrases = persona_config["custom_phrases"]
        if "tone_instruction" in persona_config:
            profile.tone_instruction = persona_config["tone_instruction"]

        return profile

    def _is_greeting_only(self, user_msg: str) -> bool:
        normalized = _normalize_conv_text(user_msg or "")
        normalized = re.sub(r"[!¡?¿.,;:]+", "", normalized).strip()
        if not normalized:
            return False
        return normalized in {
            "hola",
            "hola que tal",
            "hola como estas",
            "hola que mas",
            "hola buenas",
            "buenas",
            "buenas tardes",
            "buenos dias",
            "buenas noches",
            "como estas",
            "como vas",
            "todo bien",
            "hey",
            "holi",
            "que mas",
            "que tal",
        }

    def _is_status_opening(self, user_msg: str) -> bool:
        normalized = _normalize_conv_text(user_msg or "")
        normalized = re.sub(r"[!¡?¿.,;:]+", "", normalized).strip()
        if not normalized:
            return False
        return normalized in {
            "hola como estas",
            "como estas",
            "como vas",
            "todo bien",
            "hola que tal",
            "que tal",
        }

    def _history_gap_hours(self, history: Optional[List[Dict]]) -> Optional[float]:
        if not history:
            return None
        for item in reversed(history):
            raw_ts = str(item.get("ts") or "").strip()
            if not raw_ts:
                continue
            try:
                last_dt = datetime.fromisoformat(raw_ts.replace("Z", "+00:00"))
                if last_dt.tzinfo is not None:
                    last_dt = last_dt.astimezone().replace(tzinfo=None)
                return max(0.0, (datetime.now() - last_dt).total_seconds() / 3600.0)
            except Exception:
                continue
        return None

    def _extract_recent_topic_from_history(self, history: Optional[List[Dict]], clinic: Dict) -> str:
        if not history:
            return ""
        combined = " ".join(
            str(item.get("content") or "").strip()
            for item in history[-6:]
            if str(item.get("content") or "").strip()
        )
        if not combined:
            return ""
        return self._extract_message_topic(combined, clinic)

    def _looks_like_reentry_turn(self, user_msg: str, history: Optional[List[Dict]]) -> bool:
        if not history or not any((msg.get("role") == "assistant") for msg in (history or [])):
            return False

        if not (self._is_greeting_only(user_msg) or self._is_status_opening(user_msg)):
            return False

        recent_text = " ||| ".join(
            _normalize_conv_text(str(item.get("content") or ""))
            for item in (history or [])[-6:]
        )
        closing_markers = (
            "gracias luego te escribo",
            "gracias por tu ayuda",
            "lo dejamos hasta aqui",
            "lo dejamos hasta aquí",
            "hasta aqui",
            "hasta aquí",
            "si luego quiere retomarlo",
            "si luego quieres retomarlo",
            "seguimos desde ahi",
            "seguimos desde ahí",
            "cuando quiera volver",
            "cuando quieras volver",
        )
        if any(marker in recent_text for marker in closing_markers):
            return True

        gap_hours = self._history_gap_hours(history)
        return gap_hours is not None and gap_hours >= 24.0

    def _build_first_contact_intro(self, clinic: Dict, personality: PersonalityProfile) -> str:
        clinic_name = (clinic.get("name") or "").strip()
        agent_name = clinic.get("assistant_name") or getattr(personality, "name", "") or "Firby"
        if clinic_name:
            return f"¡Hola! Soy {agent_name} de {clinic_name}."
        return f"¡Hola! Soy {agent_name}."

    def _build_first_contact_follow_up(self, clinic: Dict) -> str:
        sector = _normalize_conv_text(str(clinic.get("sector") or ""))
        services = clinic.get("services") if isinstance(clinic.get("services"), list) else []
        normalized_services = [_normalize_conv_text(str(service)) for service in services if str(service).strip()]
        is_estetica = sector == "estetica" or any(
            token in " ".join(normalized_services)
            for token in ["botox", "relleno", "laser", "láser", "peeling", "mesoterapia"]
        )
        if services:
            lead_services = ", ".join(str(service).strip() for service in services[:3] if str(service).strip())
            if lead_services:
                if is_estetica:
                    return (
                        f"Te ubico con {lead_services}, valoración y disponibilidad. "
                        "Si quieres, cuéntame qué te interesa o qué tratamiento estás mirando."
                    )
                return (
                    f"Te ubico con información, valoración y disponibilidad de servicios como {lead_services}. "
                    "Cuéntame qué te gustaría revisar."
                )
        if is_estetica:
            return (
                "Te ubico con tratamientos, valoración y disponibilidad. "
                "Si quieres, cuéntame qué te interesa o qué tratamiento estás mirando."
            )
        return "Te ubico con información, valoración y disponibilidad. Cuéntame qué te gustaría revisar."

    def _is_low_quality_first_turn_bubble(self, text: str) -> bool:
        current = (text or "").strip()
        if not current:
            return True
        normalized = _normalize_conv_text(current)
        if not normalized:
            return True
        if looks_fragmented_reply(current):
            return True
        if len(normalized.split()) <= 2:
            return True
        if any(
            marker in normalized
            for marker in (
                "asistente virtual",
                "recepcionista virtual",
                "soy firby",
                "te habla firby",
                "hoy",
            )
        ):
            return True
        return normalized in {"hola", "hola hoy", "hoy"}

    def _is_identity_probe(self, user_msg: str) -> bool:
        normalized = _normalize_conv_text(user_msg or "")
        if not normalized:
            return False
        probes = (
            "que eres",
            "qué eres",
            "eres una ia",
            "eres ia",
            "eres un bot",
            "eres bot",
            "como funcionas",
            "cómo funcionas",
            "quien eres",
            "quién eres",
            "que haces",
            "qué haces",
            "quiero probarte",
            "me gustaria probarte",
            "me gustaría probarte",
            "demo",
            "mi negocio",
            "mi empresa",
        )
        return any(marker in normalized for marker in probes)

    def _build_identity_probe_bubbles(self, clinic: Dict, personality: PersonalityProfile, user_msg: str) -> List[str]:
        clinic_name = (clinic.get("name") or "").strip()
        agent_name = clinic.get("assistant_name") or getattr(personality, "name", "") or "Valentina"
        if agent_name.lower() in ("firby", "lucia", "lucía"):
            agent_name = clinic.get("assistant_name") or "Valentina"
        normalized = _normalize_conv_text(user_msg or "")

        intro_variants = [
            f"¡Hola! Soy {agent_name}, asesora virtual con IA de {clinic_name if clinic_name else 'la clínica'}",
            f"¡Hola! Claro que sí, soy {agent_name}, asesora virtual con IA en {clinic_name if clinic_name else 'nuestra clínica'}",
            f"¡Hola! Soy {agent_name}, asesora virtual con IA, y con gusto te ayudo en {clinic_name if clinic_name else 'nuestra clínica'}",
        ]
        intro = intro_variants[len(normalized) % len(intro_variants)]

        services = clinic.get("services") if isinstance(clinic.get("services"), list) else []
        lead_services = [str(service).strip() for service in services[:3] if str(service).strip()]
        if lead_services:
            capabilities = (
                "Te puedo ayudar con información, horarios, disponibilidad, valoración y orientación inicial"
                f" sobre servicios como {', '.join(lead_services)}"
            )
        else:
            capabilities = (
                "Te puedo ayudar con información, horarios, disponibilidad, valoración y orientación inicial"
                " para que el primer contacto se sienta claro, útil y bien llevado"
            )

        cta = "Si quieres, cuéntame qué te gustaría revisar y lo vemos"
        if any(token in normalized for token in ("probarte", "demo", "negocio", "empresa", "funcionas", "eres")):
            cta = "Si quieres probarme en serio, escríbeme el nombre de tu negocio y te muestro cómo trabajaría contigo"

        return [intro, capabilities, cta]

    def _extract_message_topic(self, user_msg: str, clinic: Dict) -> str:
        normalized = _normalize_conv_text(user_msg or "")
        services = clinic.get("services") if isinstance(clinic.get("services"), list) else []
        for service in services:
            service_text = str(service).strip()
            if not service_text:
                continue
            service_norm = _normalize_conv_text(service_text)
            if service_norm and service_norm in normalized:
                return service_text

        known_topics = {
            "botox": "Botox",
            "relleno": "Rellenos",
            "rellenos": "Rellenos",
            "laser": "Láser",
            "làser": "Láser",
            "peeling": "Peeling",
            "mesoterapia": "Mesoterapia",
            "limpieza": "Limpieza",
            "blanqueamiento": "Blanqueamiento",
            "ortodoncia": "Ortodoncia",
            "consulta": "Consulta",
            "valoracion": "Valoración",
            "valoración": "Valoración",
            "agenda": "Cita",
            "cita": "Cita",
            "citas": "Cita",
        }
        for keyword, label in known_topics.items():
            if keyword in normalized:
                return label
        return ""

    def _build_contextual_first_turn_follow_up(self, clinic: Dict, user_msg: str) -> str:
        normalized = _normalize_conv_text(user_msg or "")
        sector = _normalize_conv_text(str(clinic.get("sector") or ""))
        services = clinic.get("services") if isinstance(clinic.get("services"), list) else []
        normalized_services = [_normalize_conv_text(str(service)) for service in services if str(service).strip()]
        is_estetica = sector == "estetica" or any(
            token in " ".join(normalized_services)
            for token in ["botox", "relleno", "laser", "láser", "peeling", "mesoterapia"]
        )
        if any(marker in normalized for marker in ["soy tu admin", "soy el admin", "soy admin", "no hables asi", "no hables así"]):
            return "Entendido. Ajusto el tono contigo. Dime si lo prefieres más directo, más ejecutivo o más corto."

        topic = self._extract_message_topic(user_msg, clinic)
        if topic:
            if any(token in normalized for token in ["precio", "cuanto", "cuánto", "vale", "costo"]):
                if is_estetica:
                    return (
                        f"{topic} lo manejan acá. Si quieres, te ubico cómo lo trabajan, "
                        "qué influye en el valor y si te conviene valoración o disponibilidad."
                    )
                return f"{topic} lo manejan acá. Si quieres, te ubico precio, valoración o disponibilidad. Cuéntame qué prefieres revisar primero."
            if any(token in normalized for token in ["agenda", "agendar", "cita", "citas", "disponibilidad", "horario"]):
                if is_estetica:
                    return (
                        f"{topic} lo manejan acá. Si quieres, te ayudo a revisar disponibilidad "
                        "o a dejar la valoración encaminada para esa zona."
                    )
                return f"{topic} lo manejan acá. Si quieres, te ayudo a revisar disponibilidad o a dejar la valoración encaminada. Cuéntame qué te sirve más."
            if is_estetica:
                return (
                    f"{topic} lo manejan acá. Si quieres, te cuento cómo lo trabajan "
                    "y qué suelen revisar para que se vea natural."
                )
            return f"{topic} lo manejan acá. Si quieres, te cuento cómo lo trabajan o revisamos valoración y disponibilidad. Cuéntame qué te gustaría revisar primero."

        if any(token in normalized for token in ["agenda", "agendar", "cita", "citas", "disponibilidad", "horario"]):
            return "Te ayudo a revisar disponibilidad o a dejar la cita encaminada. Cuéntame qué fecha o servicio te interesa."

        if is_estetica:
            return "Cuéntame qué te gustaría mejorar y te ayudo con eso."

        return "Cuéntame qué estás buscando y te ubico rápido."

    def _normalize_first_patient_turn(
        self,
        response: str,
        clinic: Dict,
        personality: PersonalityProfile,
        user_msg: str,
        history: List[Dict],
    ) -> str:
        if response and response.strip() and not self._is_low_quality_first_turn_bubble(response):
            return response.strip()
        intro = self._build_first_contact_intro(clinic, personality)
        follow_up = self._build_first_contact_follow_up(clinic)
        return f"{intro} ||| {follow_up}"

    def _prepare_effective_history(self, chat_id: str, history: List[Dict]) -> Tuple[List[Dict], str]:
        effective_history = list(history or [])
        context_summary = ""

        if not effective_history:
            return effective_history, context_summary

        if smart_context_manager:
            try:
                effective_history, context_summary = smart_context_manager.prepare_context(
                    chat_id=chat_id,
                    history=effective_history,
                    max_messages=Config.FIRBY_CONTEXT_RECENT_MESSAGES,
                )
            except Exception as exc:
                log.debug(f"[compact_prompt] no se pudo preparar contexto: {exc}")
                effective_history = effective_history[-Config.FIRBY_CONTEXT_RECENT_MESSAGES:]
        else:
            effective_history = effective_history[-Config.FIRBY_CONTEXT_RECENT_MESSAGES:]

        if not context_summary and smart_context_manager and chat_id:
            context_summary = smart_context_manager.get_cached_summary(chat_id)

        return effective_history, context_summary

    def _resolve_persona_forbidden_patterns(self, clinic: Dict[str, Any]) -> List[str]:
        try:
            if getattr(self, "_conversation_registry", None):
                persona_profile = self._conversation_registry.resolve_for_clinic(clinic or {})
                return list(getattr(persona_profile, "forbidden_patterns", []) or [])
        except Exception:
            pass
        return []

    def _build_short_memory_block(self, history: List[Dict[str, Any]]) -> str:
        if not history:
            return ""
        try:
            from firby_brain_v10 import extract_short_memory, format_memory_block

            return format_memory_block(extract_short_memory(history))
        except Exception:
            return ""

    def _prompt_builder_deps(self) -> PromptBuilderDeps:
        return PromptBuilderDeps(
            build_fewshot_examples=self._build_fewshot_examples,
            get_sector_info=get_sector_info,
            now_provider=now_col,
            sector_default=Config.SECTOR,
            db=db,
            owner_style_controller=owner_style_controller,
            kb_available=_KB_AVAILABLE,
            format_kb_context=format_kb_context if _KB_AVAILABLE else None,
            resolve_persona_forbidden=self._resolve_persona_forbidden_patterns,
            v8_addon_builder=v8_build_quality_system_prompt_addon,
            trainer_addon_builder=trainer_get_system_prompt_addon,
            short_memory_builder=self._build_short_memory_block,
            apply_archetype=apply_archetype,
        )

    def _truncate_block(self, text: str, max_chars: int) -> str:
        return _truncate_block_core(text, max_chars)

    def _build_compact_examples(self, sector_id: str, clinic_name: str, agent_name: str) -> str:
        return _build_compact_examples_core(
            self._build_fewshot_examples(sector_id, clinic_name, agent_name)
        )

    def _build_compact_system_prompt(
        self,
        clinic: Dict,
        patient: Dict,
        personality: PersonalityProfile,
        search_context: str,
        reasoning: Dict,
        kb_context: str = "",
        context_summary: str = "",
        pre_prompt_injection: str = "",
        chat_id: str = "",
        history: List[Dict] = None,
    ) -> str:
        return _build_compact_system_prompt_core(
            clinic=clinic,
            patient=patient,
            personality=personality,
            search_context=search_context,
            reasoning=reasoning,
            kb_context=kb_context,
            context_summary=context_summary,
            pre_prompt_injection=pre_prompt_injection,
            chat_id=chat_id,
            history=history or [],
            deps=self._prompt_builder_deps(),
        )
    
    def _build_system_prompt(self, clinic: Dict, patient: Dict,
                             personality: PersonalityProfile,
                             search_context: str,
                             reasoning: Dict,
                             kb_context: str = "",
                             user_msg: str = "",
                             chat_id: str = "",
                             history: List[Dict] = None) -> str:
        return _build_system_prompt_core(
            clinic=clinic,
            patient=patient,
            personality=personality,
            search_context=search_context,
            reasoning=reasoning,
            kb_context=kb_context,
            user_msg=user_msg,
            chat_id=chat_id,
            history=history or [],
            deps=self._prompt_builder_deps(),
        )

    def _build_fewshot_examples(self, sector_id: str, clinic_name: str, agent_name: str) -> str:
        """
        Devuelve 3-4 conversaciones cortas calibradas por sector.
        Escritas en voz de Firby — el modelo aprende el patrón, no obedece reglas.
        Principio: show don't tell. Los ejemplos enseñan el tono que las instrucciones no capturan.
        """

        # Mapa sector → conversaciones con FRICCIÓN REAL (v10)
        # Incluye objeciones de precio, indecisión, miedos, silencio.
        # El LLM aprende del patrón — no de las reglas.
        _examples: Dict[str, str] = {

            "estetica": f"""cliente: hola cuánto vale el botox
{agent_name}: depende de las zonas, el número exacto te lo da la dra en la valoración ||| qué zona te está molestando más

cliente: la frente, ya se marcan mucho
{agent_name}: eso es exactamente lo que trata el botox en frente — relaja el músculo y en una semana no se notan ||| la valoración es gratis, esta semana el jueves hay espacio, te queda

cliente: me da miedo quedar tiesa o exagerada
{agent_name}: ese miedo lo tiene la mayoría antes de venir ||| la dra trabaja muy conservador, el objetivo es que te veas descansada, no diferente. en la valoración te muestra casos reales y tú decides si sigues

cliente: lo voy a pensar
{agent_name}: claro, sin prisa ||| si en algún momento quieres agendar la valoración que es sin compromiso, aquí estoy

cliente: es que está caro
{agent_name}: entiendo ||| si quieres te cuento qué incluye y por qué vale lo que vale. qué zona te interesa exactamente""",

            "dental": f"""cliente: hola necesito una limpieza
{agent_name}: cuándo fue la última vez que fuiste al odontólogo

cliente: hace como 2 años
{agent_name}: no te preocupes, eso es más común de lo que crees ||| esta semana el jueves hay espacio, te queda

cliente: me da pereza, siempre me regañan
{agent_name}: acá no regañamos, en serio ||| lo que sí hacemos es dejar todo limpio y decirte qué hay que revisar. qué te parece si agendamos

cliente: cuánto vale
{agent_name}: la profilaxis está en 80, incluye el examen general ||| si encuentran algo te dicen ese día

cliente: tengo mucho miedo, soy muy nervioso con el odontólogo
{agent_name}: cuéntame qué fue lo que pasó antes para que te quedara ese miedo ||| acá trabajan con anestesia tópica primero y van despacio""",

            "gimnasio": f"""cliente: quiero inscribirme cuánto vale
{agent_name}: qué quieres trabajar primero, es más cardio, pesas, o los dos

cliente: bajar de peso principalmente, tengo como 12 kilos de más
{agent_name}: hace cuánto no entrenas

cliente: como un año y medio
{agent_name}: arrancamos con la evaluación física, es gratis y en 30 minutos el entrenador te dice de dónde partir ||| esta semana el miércoles en la tarde hay espacio

cliente: es que no tengo mucho tiempo
{agent_name}: cuántas veces a la semana podrías venir, aunque sea

cliente: tal vez 3
{agent_name}: con 3 veces bien trabajadas ya se ve resultado ||| mañana o tarde te queda mejor""",

            "veterinaria": f"""cliente: hola mi perrito no ha querido comer desde ayer
{agent_name}: cómo se llama y qué más síntomas tiene, está quieto o vomitó algo

cliente: teo, está quieto y no se levanta
{agent_name}: eso hay que verlo hoy, no esperar ||| puedes traer a teo ahora, dime cuándo sales

cliente: es que queda lejos, como 40 minutos
{agent_name}: cuando hay decaimiento y sin apetito más de 24 horas es mejor no esperar ||| llama al llegar para que lo reciban directo

cliente: cuánto vale la consulta
{agent_name}: la consulta está en 60, incluye examen completo ||| si necesita algo adicional te dicen ese día con el precio antes de proceder""",

            "restaurante": f"""cliente: hola quiero reservar para este sábado
{agent_name}: para cuántas personas y a qué hora

cliente: somos 8 como a las 7
{agent_name}: verifico disponibilidad ||| es para alguna ocasión especial

cliente: cumpleaños de mi mamá
{agent_name}: lindo ||| tenemos decoración sin costo, torta y canción tienen costo extra. quieren incluir algo

cliente: cuánto vale la torta
{agent_name}: la torta para 8 está en 45 ||| la dejamos incluida o prefieren traer la de ustedes

cliente: la traemos nosotros
{agent_name}: perfecto ||| a nombre de quién hago la reserva y un número de contacto""",

            "belleza": f"""cliente: quiero teñirme de rubio
{agent_name}: qué color tienes ahora

cliente: castaño oscuro casi negro
{agent_name}: ese proceso toma varias sesiones para no quemar el cabello ||| cuándo puedes venir para que la estilista evalúe el estado

cliente: cuánto me va a costar todo
{agent_name}: puede ir desde 200 hasta 450 en total dependiendo del estado ||| la evaluación es gratis y te dan el presupuesto exacto. cuándo puedes

cliente: es mucha plata
{agent_name}: sí, los procesos de aclarado son los más costosos porque hay que hacerlo bien ||| hay opción de hacerlo por etapas para distribuirlo""",

            "spa": f"""cliente: quiero un masaje cuánto vale
{agent_name}: tienes algo específico, es relajante o tienes algún dolor

cliente: muy estresada, necesito desconectarme
{agent_name}: el sueco de 60 minutos es justo para eso ||| esta semana el jueves en la tarde hay espacio

cliente: somos dos podemos ir juntas
{agent_name}: verifico que haya dos cabinas disponibles ||| para qué día lo tienen pensado

cliente: el sábado
{agent_name}: sábado hay espacio a las 11 o a las 3 ||| cuál les queda mejor""",

            "medico": f"""cliente: necesito cita con el médico
{agent_name}: es urgente o es consulta de control

cliente: llevo una semana con dolor de cabeza fuerte, no se me quita
{agent_name}: eso hay que verlo esta semana ||| el jueves en la mañana hay espacio, te queda

cliente: no sé si es tan grave para ir
{agent_name}: una semana de dolor que no cede sí merece revisión ||| te agendo el jueves y si antes empeora me avisas

cliente: cuánto vale
{agent_name}: la consulta está en 80 ||| la tiene por seguro o paga particular""",

            "psicologo": f"""cliente: hola quisiera hablar con alguien
{agent_name}: qué te animó a escribir hoy

cliente: llevo meses muy ansioso, ya no estoy durmiendo bien
{agent_name}: bien que lo decidiste ||| prefieren sesión presencial o virtual

cliente: virtual, da un poco de pena ir en persona
{agent_name}: no te preocupes, muchos arrancan así ||| esta semana el miércoles a las 6pm hay espacio con la psicóloga

cliente: cuánto vale
{agent_name}: la sesión inicial es de 120 ||| si decides continuar hay paquetes de 4 con descuento

cliente: no sé si puedo sostener ese costo
{agent_name}: cuéntame un poco tu situación y vemos qué opción se acomoda ||| lo importante es arrancar""",

            "abogado": f"""cliente: necesito asesoría legal
{agent_name}: qué tipo de situación le trajo

cliente: me despidieron sin justa causa hace 10 días
{agent_name}: eso tiene proceso ||| le dieron algo por escrito o fue verbal

cliente: una carta y me pidieron que firmara
{agent_name}: no firme nada todavía, esa firma puede afectar lo que puede reclamar ||| le agendo consulta esta semana, lleve la carta y el contrato

cliente: cuánto cuesta
{agent_name}: la consulta inicial está en 150, dura una hora ||| cuándo tiene disponibilidad""",

            "inmobiliaria": f"""cliente: busco apartamento en arriendo
{agent_name}: en qué zona y cuánto presupuesto manejas

cliente: laureles, hasta dos millones
{agent_name}: cuántas habitaciones y para cuántas personas

cliente: dos habitaciones, somos 3
{agent_name}: tengo dos opciones en ese rango en laureles ||| cuándo podrías visitar

cliente: son muchos requisitos eso me estresa
{agent_name}: cuéntame qué te ha pasado antes ||| acá te decimos desde el principio qué piden y si aplicas, sin hacerte perder tiempo""",

            "taller": f"""cliente: mi carro está haciendo un ruido raro
{agent_name}: qué tipo de ruido y cuándo lo hace, al arrancar o en movimiento

cliente: al arrancar como un golpe seco
{agent_name}: puede ser el arranque o la batería ||| puedes traerlo hoy, el diagnóstico es gratis y en 2 horas te decimos qué tiene

cliente: cuánto cuesta la reparación
{agent_name}: eso depende de lo que encuentren ||| el presupuesto te lo dan antes de tocar nada. qué marca y modelo tiene""",

            "nutricion": f"""cliente: quiero bajar de peso
{agent_name}: cuántas veces lo has intentado y qué te ha pasado

cliente: varias, siempre empiezo bien y lo dejo
{agent_name}: qué crees que pasa para que siempre se rompa

cliente: me estreso y empiezo a comer mal
{agent_name}: eso es exactamente lo que trabajamos acá, no solo la dieta sino el patrón detrás ||| esta semana el jueves hay consulta

cliente: ya gasté mucha plata en dietas que no funcionan
{agent_name}: tiene sentido que lo dudes ||| en la primera consulta te cuento el enfoque y decides si tiene sentido para ti. es sin compromiso""",

            "academia": f"""cliente: quiero aprender inglés por dónde empiezo
{agent_name}: qué nivel tienes ahora, entiendes algo o es desde cero

cliente: sé algo pero nunca lo estudié formalmente
{agent_name}: haría falta un diagnóstico para saber en qué nivel entras ||| es para algo específico

cliente: trabajo, me están pidiendo inglés para ascender
{agent_name}: con esa motivación específica es más fácil estructurar el avance ||| el diagnóstico es gratis y dura 20 minutos. cuándo puedes

cliente: cuánto cuestan las clases
{agent_name}: las grupales están en 280 al mes, las individuales en 180 por sesión ||| con la prioridad que tienes, las individuales avanzan más rápido""",

            "fisioterapia": f"""cliente: tengo dolor de espalda baja desde hace semanas
{agent_name}: fue de golpe o fue acumulando

cliente: creo que fue por levantarme mal
{agent_name}: tienes diagnóstico médico o es lo que estás sintiendo

cliente: lo que siento, no he ido al médico
{agent_name}: en la evaluación el fisio te dice qué tiene y cuántas sesiones necesitas ||| esta semana el martes hay espacio

cliente: no sé si realmente necesito fisio o con reposo se pasa
{agent_name}: semanas con el mismo dolor ya indican que el reposo solo no alcanza ||| la evaluación es sin compromiso, y es la que te dice exactamente qué necesitas""",

            "fotografia": f"""cliente: quiero cotizar fotos para una boda
{agent_name}: para qué fecha y cuántas horas necesitan

cliente: 15 de marzo unas 8 horas
{agent_name}: verifico disponibilidad ||| incluye solo fotos o también video

cliente: solo fotos
{agent_name}: para 8 horas el paquete está en 2.800, incluye 300 fotos editadas ||| es para bloquear ya o todavía están evaluando

cliente: está un poco caro para nosotros
{agent_name}: cuánto presupuesto manejan ||| hay paquetes de 5 o 6 horas que se acomodan mejor""",

            "tattoo": f"""cliente: quiero hacerme un tatuaje
{agent_name}: ya tienes el diseño claro o todavía estás explorando

cliente: tengo una idea pero no sé exactamente cómo
{agent_name}: en qué zona y qué tamaño aproximado

cliente: antebrazo, como la palma de la mano
{agent_name}: me mandas referencias y el artista te hace el diseño y el presupuesto

cliente: me da miedo arrepentirme
{agent_name}: cuéntame la idea que tienes, qué significa para ti ||| eso ayuda al artista a hacer algo que te represente de verdad y no algo que después incomoda""",

            "hotel": f"""cliente: quiero reservar para este fin de semana
{agent_name}: para cuántas personas y cuántas noches

cliente: dos personas viernes a domingo
{agent_name}: incluye desayuno o sin

cliente: con desayuno
{agent_name}: habitación doble con desayuno viernes-domingo está en 760 en total ||| a nombre de quién la hago

cliente: tienen estacionamiento
{agent_name}: sí, incluido para huéspedes ||| alguna solicitud especial para la habitación""",

            "coworking": f"""cliente: hola info sobre los espacios
{agent_name}: buscas escritorio compartido, privado, o sala de reuniones

cliente: escritorio por ahora, estoy trabajando solo
{agent_name}: cuántos días a la semana necesitas

cliente: tal vez 3 o 4, no sé por cuánto tiempo
{agent_name}: tenemos plan flexible sin contrato mínimo ||| cuándo quieres venir a conocer el espacio

cliente: cuánto vale mensual
{agent_name}: el de 3 días por semana está en 280, el de 5 días en 380 ||| sin contrato, pagas mes a mes""",

            "otro": f"""cliente: hola buenas
{agent_name}: hola ||| cuéntame qué te gustaría revisar

cliente: quería información sobre sus servicios
{agent_name}: claro, qué fue lo que te hizo buscarnos hoy

cliente: lo vi en redes y me llamó la atención
{agent_name}: qué fue lo que viste ||| así te cuento exactamente qué tenemos para eso""",
        }

        return _examples.get(sector_id, _examples["otro"])

    def _postprocess(self, response: str, personality: PersonalityProfile) -> str:
        """
        Post-procesador limpio y 100% fiel al LLM:
        - Conserva el texto exacto generado por el modelo sin recortes ni listas de palabras prohibidas.
        - Solamente remueve signos invertidos ('¿' e '¡') para WhatsApp.
        - Preserva emojis, frases y puntuación sin mutilar.
        """
        if not response:
            return response

        # Remoción de signos invertidos de apertura
        response = response.replace('¿', '').replace('¡', '')
        
        # Limpieza suave de espacios
        response = re.sub(r'\s+', ' ', response).strip()
        response = re.sub(r'\s*\|\|\|\s*', ' ||| ', response)

        return response

    def _apply_output_pipeline(self, response: str, personality: PersonalityProfile,
                               chat_id: str, clinic: Dict, user_msg: str,
                               history: List[Dict], is_admin: bool = False) -> str:
        """Aplica todos los filtros que deben tocar la salida final."""
        response = self._postprocess(response, personality)
        first_turn = not any((m.get("role") == "assistant") for m in (history or []))
        response = trainer_post_process_response(response, chat_id=chat_id)
        response = v8_extended_postprocess(
            response=response,
            chat_id=chat_id,
            clinic=clinic,
            user_msg=user_msg,
            history=history,
            archetype=getattr(personality, "archetype", "amigable"),
        )
        response = self._normalize_first_patient_turn(
            response=response,
            clinic=clinic,
            personality=personality,
            user_msg=user_msg,
            history=history,
        )
        response = self._repair_fragmented_response(
            response,
            clinic,
            user_msg,
            personality=personality,
            history=history,
        )
        if owner_style_controller:
            response = owner_style_controller.enforce_output(
                response,
                is_admin=is_admin,
                first_turn=first_turn,
                chat_id=chat_id,
                clinic=clinic,
                user_msg=user_msg,
            )
        return response

    def _repair_fragmented_response(
        self,
        response: str,
        clinic: Dict,
        user_msg: str,
        personality: Optional[PersonalityProfile] = None,
        history: Optional[List[Dict]] = None,
    ) -> str:
        """Solo repara respuestas genuinamente rotas (truncadas, cortadas).
        No reemplaza respuestas válidas del LLM con strings hardcodeados."""
        current = (response or "").strip()
        if not current:
            return current

        # Solo reparar si hay señales claras de respuesta truncada o cortada
        cut_markers = [
            "se me corto el mensaje",
            "se me cortó el mensaje",
            "te decia",
            "te decía",
        ]
        current_low = _normalize_conv_text(current)
        if any(marker in current_low for marker in cut_markers):
            return self._build_first_contact_intro(clinic, personality) if personality else current
        if looks_fragmented_reply(current):
            return self._build_first_contact_intro(clinic, personality) if personality else current

        # Respuesta del LLM válida — no tocar
        return current

    def _build_owner_rule_retry_injection(self, response: str) -> Tuple[List[str], str]:
        """
        Reúne las reglas del dueño y marca conflictos evidentes contra la respuesta actual.
        Esto refuerza que el feedback no solo se guarde, sino que se cumpla.
        """
        if not db:
            return [], ""

        try:
            rules = db.get_trust_rules(limit=8)
        except Exception:
            rules = []

        response_lower = (response or "").lower()
        conflicts: List[str] = []
        reminders: List[str] = []

        for rule in rules[:8]:
            rule_text = (rule.get("rule") or "").strip()
            example_bad = (rule.get("example_bad") or "").strip()
            example_good = (rule.get("example_good") or "").strip()

            if rule_text:
                line = f"→ {rule_text}"
                if example_good:
                    line += f' Ejemplo bueno: "{example_good}"'
                reminders.append(line)

            if example_bad and example_bad.lower() in response_lower:
                conflict = f'No uses "{example_bad}"'
                if example_good:
                    conflict += f'; mejor: "{example_good}"'
                conflicts.append(conflict)

            if rule_text:
                patterns = [
                    r'(?:no digas|nunca digas|evita decir|no menciones|evita mencionar)\s+[\"“]?([^\"”.;\n]+)',
                    r'(?:quita|prohibido)\s+[\"“]?([^\"”.;\n]+)',
                ]
                for pattern in patterns:
                    m = re.search(pattern, rule_text, flags=re.IGNORECASE)
                    if not m:
                        continue
                    forbidden = m.group(1).strip(" \"'“”.,:;")
                    if len(forbidden) >= 3 and forbidden.lower() in response_lower:
                        conflicts.append(f'Quita "{forbidden}"')
                        break

        if owner_style_controller:
            try:
                admin_cfg = owner_style_controller._merged_bucket("admin")
                patient_cfg = owner_style_controller._merged_bucket("patient")
                all_forbidden = list(admin_cfg.get("forbidden_phrases", [])) + list(patient_cfg.get("forbidden_phrases", []))
                all_starts = list(admin_cfg.get("forbidden_starts", [])) + list(patient_cfg.get("forbidden_starts", []))
                if all_forbidden or all_starts:
                    reminders.append("→ Respeta el plano de control del admin.")
                for phrase in all_forbidden[:12]:
                    phrase = str(phrase).strip()
                    if phrase and phrase.lower() in response_lower:
                        conflicts.append(f'Quita "{phrase}"')
                for start in all_starts[:12]:
                    start = str(start).strip().lower()
                    if start and response_lower.startswith(start):
                        conflicts.append(f'No abras con "{start}"')
            except Exception:
                pass

        if not reminders and not conflicts:
            return [], ""

        lines = [
            "REGLAS DEL DUEÑO A RESPETAR EN ESTA RESPUESTA:",
            *reminders[:5],
        ]

        if conflicts:
            lines.append("INCUMPLISTE ESTAS REGLAS:")
            lines.extend(f"→ {c}" for c in conflicts[:4])

        lines.append("Reescribe manteniendo la intención, pero ahora sí cumpliendo esto al pie de la letra.")
        return conflicts, "\n".join(lines)

    async def _retry_until_human(self, messages: List[Dict], response: str,
                                 model_tier: str, personality: PersonalityProfile,
                                 chat_id: str, clinic: Dict, user_msg: str,
                                 history: List[Dict]) -> str:
        """
        v10 — Retry limpio basado en contexto.
        V9 Upgrade: Bloquea 'conversational apologies' (Uy, qué pena!).
        """
        current = response
        first_turn = not any((m.get("role") == "assistant") for m in (history or []))
        reentry_turn = self._looks_like_reentry_turn(user_msg, history)
        greeting_only = self._is_greeting_only(user_msg)

        # ── EXCEPCIÓN: No hacer retry para saludos simples (evita over-correction)
        if greeting_only and not first_turn:
            return current

        # ── Detectar problemas ──────────────────────────────────────────────
        conflicts, owner_block = self._build_owner_rule_retry_injection(current)
        redundant_question = detect_redundant_question(user_msg, current, history=history)
        unanswered_price = detect_unanswered_price_request(user_msg, current)
        fragmented = looks_fragmented_reply(current)
        current_lower = (current or "").lower().strip()

        if first_turn and len((current or "").split()) > 35:
            conflicts.append("primer_turno_largo")

        if not first_turn and not reentry_turn:
            if re.match(r"^(hola[,!]?\s|buenas[,!]?\s)", current_lower):
                conflicts.append("saludo_redundante")

        if redundant_question: conflicts.append("pregunta_redundante")
        if unanswered_price:   conflicts.append("precio_ignorado")
        if fragmented:         conflicts.append("respuesta_cortada")

        # v12: si esta respuesta se parece demasiado a algo que Firby ya
        # dijo hace poco en esta misma conversación (mismo vocabulario clave),
        # se marca como repetitiva — evita que suene a que reutiliza el mismo
        # libreto turno tras turno.
        recent_assistant_msgs = [
            m.get("content", "") for m in (history or [])[-8:]
            if m.get("role") == "assistant"
        ][-2:]
        if recent_assistant_msgs:
            cur_words = set(re.findall(r"[a-záéíóúñ]{4,}", current_lower))
            for prev in recent_assistant_msgs:
                prev_words = set(re.findall(r"[a-záéíóúñ]{4,}", (prev or "").lower()))
                if cur_words and prev_words:
                    overlap = len(cur_words & prev_words) / min(len(cur_words), len(prev_words))
                    if overlap > 0.65:
                        conflicts.append("respuesta_repetitiva")
                        break

        if not conflicts and not owner_block:
            return current

        # ── Un solo retry — Formato 'Inner Monologue' ───────────────────────
        problem_parts = []
        if "primer_turno_largo" in conflicts: problem_parts.append("demasiado largo para el primer mensaje")
        if "saludo_redundante" in conflicts:   problem_parts.append("saludo innecesario (ya vienen hablando)")
        if "pregunta_redundante" in conflicts: problem_parts.append("ya preguntaste eso antes")
        if "precio_ignorado" in conflicts:     problem_parts.append("no respondiste al precio")
        if "respuesta_cortada" in conflicts:   problem_parts.append("respuesta incompleta")
        if "respuesta_repetitiva" in conflicts: problem_parts.append("suena casi igual a algo que ya dijiste antes en esta misma conversación")
        if owner_block:                        problem_parts.append(owner_block.strip())

        if not problem_parts:
            return current

        # Prompt de instrucción interna (System-style para no romper personaje)
        retry_note = (
            f"[INSTRUCCIÓN INTERNA DE CALIDAD: Tu respuesta anterior fue rechazada porque {', '.join(problem_parts)}. "
            "Genera una nueva respuesta final para el paciente. NO te disculpes, NO menciones este error, "
            "solo responde directamente al paciente manteniendo tu personaje.]"
        )

        retry_messages = list(messages)
        retry_messages.append({"role": "assistant", "content": current})
        retry_messages.append({"role": "system", "content": retry_note})

        try:
            # En retry usamos un modelo razonador si es posible para asegurar calidad
            retry_tier = "reasoning" if model_tier == "fast" else model_tier
            current, _ = await self.llm.complete(
                retry_messages,
                model_tier=retry_tier,
                temperature=0.6, # un poco más conservador en el retry
                max_tokens=300,
                use_cache=False,
            )
        except Exception as e:
            log.warning(f"[human_retry] error en retry: {e}")
            return response

        # Limpieza final
        current = self._apply_output_pipeline(
            response=current,
            personality=personality,
            chat_id=chat_id,
            clinic=clinic,
            user_msg=user_msg,
            history=history,
            is_admin=False,
        )
        return current

    def _strip_redundant_turn_opening(
        self, response: str, *, user_msg: str = "", history: list = None
    ) -> str:
        """Elimina saludos e introducciones redundantes cuando el bot ya se presentó."""
        import re as _re

        history = history or []
        if not response:
            return response

        # Solo aplicar si ya hubo un turno previo del asistente
        prev_assistant = [m for m in history if m.get("role") == "assistant"]
        if not prev_assistant:
            return response

        lower = response.lower().strip()

        # Patrones de re-introducción completa
        reintro_patterns = [
            r"^hola[!.,]*\s*(soy\s+\w+[\s,]*)?.*?(recepcionista|asistente|asesora)\s+(virtual|de\s+)",
            r"^hola[!.,]*\s*soy\s+\w+[\s,]*de\s+",
            r"^hola[!.,]*\s*bienvenid[oa]",
            r"^hola[!.,]*\s*(en\s+qu[eé]\s+(te\s+)?puedo\s+ayudar)",
        ]

        # Si el usuario pregunta por identidad, preservar la parte de identidad
        identity_triggers = ["eres una ia", "eres un bot", "quien eres", "quién eres",
                             "eres real", "eres humana", "eres robot"]
        is_identity_question = any(t in user_msg.lower() for t in identity_triggers)

        if is_identity_question:
            # Solo quitar el "Hola!" redundante del inicio, dejar el resto
            cleaned = _re.sub(r"^¡?hola[!.,]*\s*", "", response, flags=_re.IGNORECASE).strip()
            return cleaned if cleaned else response

        # Para mensajes normales: si es una re-introducción completa, eliminar
        for pattern in reintro_patterns:
            if _re.search(pattern, lower):
                return ""

        # Limpiar solo el saludo inicial redundante
        cleaned = _re.sub(r"^¡?hola[!.,]*\s*", "", response, flags=_re.IGNORECASE).strip()
        if cleaned and cleaned != response.strip():
            return cleaned

        return response

# ═══════════════════════════════════════════════════════════════════════════════
# AUTO-CONEXIÓN WHATSAPP
# El cliente da sus credenciales de Meta → Firby se auto-conecta
# ═══════════════════════════════════════════════════════════════════════════════

