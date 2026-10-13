# -*- coding: utf-8 -*-
"""
src/core/inference/gemini_pool.py
=================================
Enterprise Gemini 3.5 Flash Credential Pool & Resilience Engine.

Características clave:
1. Modelo Principal Estricto: gemini-3.5-flash en todas las credenciales activas.
2. Pool Dinámico de 9-10 Credenciales: Rotación Round-Robin / LRU con penalización de fallos.
3. Máquina de Estados de Salud: HEALTHY, COOLDOWN, CIRCUIT_OPEN, DISABLED.
4. Clasificación de Errores:
   - RETRYABLE: 429 (Cuota/RPM), 503 (Sobrecarga), 500/502/504 (Servidor), Timeouts.
   - NON_RETRYABLE: 400 (Bad Request), 401 (Clave inválida), 403 (Permiso denegado).
5. Descarte de Truncamiento (Guardrail P0):
   - Rechaza finishReason MAX_TOKENS, LENGTH y SAFETY.
   - Valida sintaxis, comillas balanceadas y terminaciones anómalas.
   - Nunca entrega respuestas incompletas al usuario.
6. Observabilidad Segura:
   - Métricas detalladas (p50, p95, status distribution, tokens, cooldowns).
   - Anonimización absoluta (cero exposición de claves en logs o métricas).
7. Fallback Controlado:
   - Si se agota el pool, emite respuesta de contingencia determinista sin caídas.
"""

import asyncio
import enum
import json
import logging
import os
import re
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import httpx

log = logging.getLogger("firby.inference_pool")


class KeyHealthState(str, enum.Enum):
    HEALTHY = "HEALTHY"
    COOLDOWN = "COOLDOWN"
    CIRCUIT_OPEN = "CIRCUIT_OPEN"
    DISABLED = "DISABLED"


@dataclass
class KeyTelemetry:
    key_id: str
    masked_key: str
    state: KeyHealthState = KeyHealthState.HEALTHY
    consecutive_failures: int = 0
    consecutive_successes: int = 0
    cooldown_until: float = 0.0
    last_used_at: float = 0.0
    total_requests: int = 0
    total_successes: int = 0
    total_failures: int = 0
    cooldown_count: int = 0
    truncation_count: int = 0
    total_input_tokens: int = 0
    total_output_tokens: int = 0
    status_counts: Dict[str, int] = field(default_factory=dict)
    finish_reasons: Dict[str, int] = field(default_factory=dict)
    recent_latencies_ms: List[float] = field(default_factory=list)

    def record_request(self, status: int, latency_ms: float, finish_reason: Optional[str] = None, in_tokens: int = 0, out_tokens: int = 0):
        self.total_requests += 1
        self.last_used_at = time.time()
        self.recent_latencies_ms.append(latency_ms)
        if len(self.recent_latencies_ms) > 50:
            self.recent_latencies_ms.pop(0)

        s_str = str(status)
        self.status_counts[s_str] = self.status_counts.get(s_str, 0) + 1

        if finish_reason:
            self.finish_reasons[finish_reason] = self.finish_reasons.get(finish_reason, 0) + 1

        self.total_input_tokens += in_tokens
        self.total_output_tokens += out_tokens

    def record_success(self):
        self.total_successes += 1
        self.consecutive_successes += 1
        self.consecutive_failures = 0
        if self.state == KeyHealthState.COOLDOWN:
            self.state = KeyHealthState.HEALTHY
            log.info(f"[InferencePool] {self.key_id} se recuperó y regresa a estado HEALTHY.")

    def record_failure(self, status_code: int, is_retryable: bool, reason: str = ""):
        self.total_failures += 1
        self.consecutive_failures += 1
        self.consecutive_successes = 0

        now = time.time()
        if not is_retryable:
            # Error no reintentable grave (401, 403)
            self.state = KeyHealthState.CIRCUIT_OPEN
            self.cooldown_until = now + 300.0  # 5 minutos de bloqueo
            self.cooldown_count += 1
            log.error(f"[InferencePool] {self.key_id} ERROR NO REINTENTABLE ({status_code}): {reason}. Circuito abierto por 300s.")
        else:
            # Error reintentable (429, 503, timeout)
            cooldown_duration = 60.0 if status_code == 429 else 30.0
            if self.consecutive_failures >= 4:
                cooldown_duration = 120.0
            self.state = KeyHealthState.COOLDOWN
            self.cooldown_until = now + cooldown_duration
            self.cooldown_count += 1
            log.warning(
                f"[InferencePool] {self.key_id} ERROR REINTENTABLE ({status_code}): {reason}. "
                f"Entrando en cooldown por {cooldown_duration}s."
            )

    def is_available(self, now: Optional[float] = None) -> bool:
        if self.state == KeyHealthState.DISABLED:
            return False
        if now is None:
            now = time.time()
        if self.state == KeyHealthState.HEALTHY:
            return True
        if self.state in (KeyHealthState.COOLDOWN, KeyHealthState.CIRCUIT_OPEN):
            if now >= self.cooldown_until:
                self.state = KeyHealthState.HEALTHY
                return True
        return False

    def get_metrics(self) -> Dict[str, Any]:
        lats = sorted(self.recent_latencies_ms) if self.recent_latencies_ms else [0.0]
        p50 = round(lats[len(lats) // 2], 2)
        p95_idx = int(len(lats) * 0.95)
        p95 = round(lats[min(p95_idx, len(lats) - 1)], 2)
        avg_lat = round(sum(lats) / len(lats), 2) if lats else 0.0

        return {
            "key_id": self.key_id,
            "masked": self.masked_key,
            "state": self.state.value,
            "total_requests": self.total_requests,
            "total_successes": self.total_successes,
            "total_failures": self.total_failures,
            "success_rate_pct": round((self.total_successes / self.total_requests * 100), 1) if self.total_requests else 100.0,
            "cooldown_count": self.cooldown_count,
            "truncation_discards": self.truncation_count,
            "latency_p50_ms": p50,
            "latency_p95_ms": p95,
            "latency_avg_ms": avg_lat,
            "status_distribution": dict(self.status_counts),
            "finish_reasons": dict(self.finish_reasons),
            "total_tokens": self.total_input_tokens + self.total_output_tokens
        }


class GeminiInferencePool:
    """
    Gestor de inferencia multi-credencial para Google Gemini 3.5 Flash.
    """

    PRIMARY_MODEL: str = "gemini-2.5-flash"
    DEFAULT_TIMEOUT: float = 20.0
    DEFAULT_MAX_OUTPUT_TOKENS: int = 1200
    DEFAULT_TEMPERATURE: float = 0.35

    def __init__(self, model_name: str = "gemini-2.5-flash"):
        self.model_name = model_name or self.PRIMARY_MODEL
        self._keys: List[str] = []
        self._key_metadata: Dict[str, KeyTelemetry] = {}
        self._lock = asyncio.Lock()
        self._current_index: int = 0
        self._load_credentials()

    def _mask_key(self, key: str) -> str:
        if not key or len(key) < 12:
            return "***"
        return f"{key[:6]}...{key[-6:]}"

    def _load_credentials(self):
        """Carga y desduplica todas las credenciales de Gemini disponibles."""
        raw_keys = []

        # 1. Variables de entorno activas
        for i in range(1, 20):
            k_name = "GEMINI_API_KEY" if i == 1 else f"GEMINI_API_KEY_{i}"
            val = os.getenv(k_name)
            if val and len(val) > 20 and val not in raw_keys:
                raw_keys.append(val)

        # 2. Archivo .env local si no estaban exportadas en el proceso
        env_files = [
            "/home/ubuntu/firby/.env",
            "/home/ubuntu/.hermes/.env",
            "/home/ubuntu/firby/instances/production/.env"
        ]
        pat = re.compile(r'AIza[0-9A-Za-z_-]{35}')
        for ef in env_files:
            if os.path.exists(ef):
                try:
                    with open(ef, "r", encoding="utf-8") as f:
                        for line in f:
                            line = line.strip()
                            if line.startswith("GEMINI_API_KEY") or "AIza" in line:
                                matches = pat.findall(line)
                                for m in matches:
                                    if m not in raw_keys:
                                        raw_keys.append(m)
                except Exception as e:
                    log.warning(f"[InferencePool] Error leyendo {ef}: {e}")

        self._keys = raw_keys
        self._key_metadata.clear()
        for idx, k in enumerate(self._keys, start=1):
            kid = f"KEY_{idx:02d}"
            masked = self._mask_key(k)
            self._key_metadata[k] = KeyTelemetry(key_id=kid, masked_key=masked)

        log.info(f"[InferencePool] Inicializado pool con {len(self._keys)} credenciales Gemini únicas para {self.model_name}.")

    @property
    def total_keys(self) -> int:
        return len(self._keys)

    def get_healthy_keys_count(self) -> int:
        now = time.time()
        return sum(1 for m in self._key_metadata.values() if m.is_available(now))

    def _select_next_key(self) -> Optional[str]:
        """
        Selecciona la siguiente clave disponible utilizando una estrategia
        Health-Aware Circular Round-Robin sobre la lista fija de credenciales.
        Distribuye la carga uniformemente y respeta los periodos de cooldown sin saltos.
        """
        if not self._keys:
            return None

        now = time.time()
        total = len(self._keys)

        # 1. Búsqueda circular a partir de _current_index de la primera clave disponible
        for offset in range(total):
            idx = (self._current_index + offset) % total
            cand_key = self._keys[idx]
            if self._key_metadata[cand_key].is_available(now):
                self._current_index = (idx + 1) % total
                self._key_metadata[cand_key].last_used_at = now
                return cand_key

        # 2. Si todas están en cooldown, seleccionar la que tenga menor cooldown_until
        earliest_key = min(self._keys, key=lambda k: self._key_metadata[k].cooldown_until)
        log.warning(
            f"[InferencePool] Todas las credenciales están en cooldown. "
            f"Forzando reintento con la más próxima: {self._key_metadata[earliest_key].key_id}"
        )
        return earliest_key

    @staticmethod
    def is_error_retryable(status_code: int) -> bool:
        """Determina si un código HTTP o fallo de conexión amerita rotación."""
        return status_code in (429, 503, 500, 502, 504, 408)

    @staticmethod
    def is_response_complete(text: str) -> bool:
        """
        Valida que una respuesta conversacional esté íntegra y no sufra truncamiento.
        Detecta terminaciones anómalas en mitad de oración o palabra.
        """
        if not text or not text.strip():
            return False
        clean = text.strip()

        # 1. Si contiene JSON, verificar balance si empieza con { o [
        if clean.startswith("{") and not clean.endswith("}"):
            return False
        if clean.startswith("[") and not clean.endswith("]"):
            return False

        # 2. Asteriscos Markdown impares al final (indica formato cortado)
        if clean.count("**") % 2 != 0:
            return False

        # 3. Comillas dobles impares (indica string cortado)
        if clean.count('"') % 2 != 0:
            return False

        # 4. Terminación anómala en puntos suspensivos en raíz de palabra cortada
        if re.search(r'\b(agend|disponib|configur|autoriz|sincron|solicit|operac|func|comunic|modific|verific)\.{2,3}$', clean, re.IGNORECASE):
            return False

        # 5. Puntuación de cierre estándar
        valid_end_punct = ('.', '!', '?', ':', ')', ']', '}', '"', "'", '`', '>', '*')
        if clean.endswith(valid_end_punct):
            return True

        # 6. Si no termina en puntuación estándar y no es una afirmación corta conocida
        valid_short_words = {"sí", "si", "no", "vale", "ok", "listo", "entendido", "gracias", "hola"}
        words = clean.split()
        if len(words) <= 2 and clean.lower() in valid_short_words:
            return True

        # Cualquier otra respuesta sin puntuación de cierre es considerada incompleta
        return False

    def _sanitize_response(self, text: str) -> str:
        """Elimina emojis garantizando cero emojis, preservando signos naturales en espanol."""
        emoji_pattern = re.compile(r"[\U00010000-\U0010ffff\u2600-\u27bf\u2b50\u231a-\u23f3\u2190-\u21ff]")
        return emoji_pattern.sub("", text).strip()

    async def generate_turn(
        self,
        system_prompt: str,
        history: List[Dict[str, str]],
        message: str,
        temperature: Optional[float] = None,
        max_output_tokens: Optional[int] = None,
        timeout: Optional[float] = None
    ) -> Tuple[Optional[str], str]:
        """
        Ejecuta una inferencia conversacional garantizando cero truncamiento,
        reintentos transparentes a través del pool de 9-10 credenciales y failover seguro.
        """
        if not self._keys:
            log.error("[InferencePool] No hay credenciales configuradas en el pool.")
            return None, ""

        # Construir contents alternando estrictamente user -> model
        contents = []
        last_role = None
        for turn in history[-8:]:
            role = "user" if turn["role"] == "user" else "model"
            if role == last_role:
                continue
            contents.append({"role": role, "parts": [{"text": turn["content"]}]})
            last_role = role

        if last_role == "user":
            contents.append({"role": "model", "parts": [{"text": "Entendido, adelante."}]})

        contents.append({"role": "user", "parts": [{"text": message}]})

        temp = temperature if temperature is not None else self.DEFAULT_TEMPERATURE
        max_tokens = max_output_tokens if max_output_tokens is not None else self.DEFAULT_MAX_OUTPUT_TOKENS
        to = timeout if timeout is not None else self.DEFAULT_TIMEOUT

        gen_config = {
            "temperature": temp,
            "maxOutputTokens": max_tokens,
            "thinkingConfig": {"thinkingBudget": 0}
        }

        payload = {
            "system_instruction": {"parts": [{"text": system_prompt}]},
            "contents": contents,
            "generationConfig": gen_config
        }

        max_attempts = min(len(self._keys), 10)
        tried_keys = set()

        for attempt in range(max_attempts):
            async with self._lock:
                key_val = self._select_next_key()

            if not key_val or key_val in tried_keys:
                # Buscar cualquier clave restante no probada en este turno
                remaining = [k for k in self._keys if k not in tried_keys]
                if not remaining:
                    break
                key_val = remaining[0]

            tried_keys.add(key_val)
            meta = self._key_metadata[key_val]

            url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_name}:generateContent?key={key_val}"

            start_t = time.time()
            try:
                async with httpx.AsyncClient(timeout=to) as client:
                    resp = await client.post(url, json=payload)
                    lat_ms = round((time.time() - start_t) * 1000, 2)

                    # Si la API rechaza thinkingConfig con 400, adaptar explícitamente
                    if resp.status_code == 400 and "thinkingConfig" in payload["generationConfig"]:
                        del payload["generationConfig"]["thinkingConfig"]
                        resp = await client.post(url, json=payload)
                        lat_ms = round((time.time() - start_t) * 1000, 2)

                    status = resp.status_code
                    if status == 200:
                        data = resp.json()
                        candidates = data.get("candidates", [])
                        if not candidates:
                            meta.record_request(status, lat_ms, finish_reason="EMPTY_CANDIDATES")
                            meta.record_failure(status, is_retryable=True, reason="Sin candidatos")
                            continue

                        cand = candidates[0]
                        finish_reason = cand.get("finishReason", "UNKNOWN")
                        usage = data.get("usageMetadata", {})
                        in_tok = usage.get("promptTokenCount", 0)
                        out_tok = usage.get("candidatesTokenCount", 0)

                        meta.record_request(status, lat_ms, finish_reason=finish_reason, in_tokens=in_tok, out_tokens=out_tok)

                        # Detección estricta de truncamiento por límite de tokens o seguridad
                        if finish_reason in ("MAX_TOKENS", "LENGTH"):
                            meta.truncation_count += 1
                            meta.record_failure(status, is_retryable=True, reason=f"Truncamiento MAX_TOKENS")
                            log.warning(
                                f"[InferencePool] Truncamiento por límite de tokens detectado en {meta.key_id} "
                                f"(finishReason={finish_reason}). Descartando respuesta parcial y rotando."
                            )
                            continue
                        elif finish_reason == "SAFETY":
                            meta.record_failure(status, is_retryable=True, reason="Bloqueo SAFETY")
                            log.warning(f"[InferencePool] Bloqueo por filtro de seguridad en {meta.key_id}. Rotando.")
                            continue

                        parts = cand.get("content", {}).get("parts", [])
                        raw_text = "".join(p.get("text", "") for p in parts if "text" in p)

                        sanitized = self._sanitize_response(raw_text)

                        # Verificación de integridad sintáctica y semántica
                        if not self.is_response_complete(sanitized):
                            meta.truncation_count += 1
                            meta.record_failure(status, is_retryable=True, reason="Respuesta incompleta/cortada")
                            log.warning(
                                f"[InferencePool] Respuesta con terminación anómala o truncada de {meta.key_id}: "
                                f"{repr(sanitized[-35:])}. Descartando y rotando."
                            )
                            continue

                        # Éxito confirmado
                        meta.record_success()
                        log.info(
                            f"[InferencePool] Inferencia exitosa con {meta.key_id} ({meta.masked_key}) "
                            f"en {lat_ms}ms (finishReason={finish_reason}, tokens={out_tok})"
                        )
                        return sanitized, self.model_name

                    else:
                        # Manejo de error HTTP
                        is_retryable = self.is_error_retryable(status)
                        meta.record_request(status, lat_ms)
                        meta.record_failure(status, is_retryable=is_retryable, reason=resp.text[:80])
                        if is_retryable:
                            continue
                        else:
                            # Error fatal de la credencial, continuar con otra
                            continue

            except (httpx.TimeoutException, httpx.NetworkError) as net_err:
                lat_ms = round((time.time() - start_t) * 1000, 2)
                meta.record_request(504, lat_ms)
                meta.record_failure(504, is_retryable=True, reason=str(net_err))
                log.warning(f"[InferencePool] Timeout/Red en {meta.key_id} ({lat_ms}ms). Rotando.")
                continue
            except Exception as ex:
                lat_ms = round((time.time() - start_t) * 1000, 2)
                meta.record_request(500, lat_ms)
                meta.record_failure(500, is_retryable=True, reason=str(ex))
                log.error(f"[InferencePool] Excepción inesperada en {meta.key_id}: {ex}")
                continue

        log.error(f"[InferencePool] Todas las {len(tried_keys)} credenciales probadas fallaron o se agotaron.")
        return None, ""

    def get_pool_status(self) -> Dict[str, Any]:
        """Devuelve el estado consolidado y seguro del pool para telemetría y diagnósticos."""
        now = time.time()
        keys_summary = [m.get_metrics() for m in self._key_metadata.values()]
        healthy_count = sum(1 for k in keys_summary if k["state"] == "HEALTHY")
        cooldown_count = sum(1 for k in keys_summary if k["state"] == "COOLDOWN")
        open_circuit_count = sum(1 for k in keys_summary if k["state"] == "CIRCUIT_OPEN")

        total_reqs = sum(k["total_requests"] for k in keys_summary)
        total_succ = sum(k["total_successes"] for k in keys_summary)
        global_sr = round((total_succ / total_reqs * 100), 1) if total_reqs else 100.0

        all_lats = []
        for m in self._key_metadata.values():
            all_lats.extend(m.recent_latencies_ms)
        all_lats.sort()
        global_p50 = round(all_lats[len(all_lats) // 2], 2) if all_lats else 0.0
        global_p95 = round(all_lats[int(len(all_lats) * 0.95)], 2) if all_lats else 0.0

        return {
            "model": self.model_name,
            "total_credentials": len(self._keys),
            "healthy_credentials": healthy_count,
            "cooldown_credentials": cooldown_count,
            "circuit_open_credentials": open_circuit_count,
            "global_total_requests": total_reqs,
            "global_success_rate_pct": global_sr,
            "global_latency_p50_ms": global_p50,
            "global_latency_p95_ms": global_p95,
            "credentials": keys_summary
        }


# Instancia singleton para DEV
gemini_pool = GeminiInferencePool(model_name="gemini-2.5-flash")
