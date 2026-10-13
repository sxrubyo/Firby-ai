# -*- coding: utf-8 -*-
"""Centralized Configuration for Firby."""
from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Dict, List, Any, Optional

def _split_env_values(text: str) -> List[str]:
    values = []
    if text:
        text = text.strip()
        parsed = None
        if text.startswith("[") and text.endswith("]"):
            try:
                parsed = json.loads(text)
            except Exception:
                parsed = None
        if isinstance(parsed, list):
            values = [str(x).strip() for x in parsed if str(x).strip()]
        else:
            values = [part.strip() for part in re.split(r"[\n,]+", text) if part.strip()]
    deduped = []
    seen = set()
    for value in values:
        if value not in seen:
            deduped.append(value)
            seen.add(value)
    return deduped

def _collect_env_series(base_name: str, *extra_names: str) -> List[str]:
    """Recolecta BASE, BASE_2..BASE_N y también listas BASES/BASE_LIST."""
    pattern = re.compile(rf"^{re.escape(base_name)}(?:_(\d+))?$")
    ranked = []
    for env_name, env_value in os.environ.items():
        match = pattern.match(env_name)
        if not match:
            continue
        rank = int(match.group(1) or 1)
        for value in _split_env_values(env_value):
            ranked.append((rank, value))
    ranked.sort(key=lambda item: item[0])
    ordered = [value for _, value in ranked]
    for alias in extra_names or (f"{base_name}S", f"{base_name}_LIST"):
        ordered.extend(_split_env_values(os.getenv(alias, "")))
    deduped = []
    seen = set()
    for value in ordered:
        if value and value not in seen:
            deduped.append(value)
            seen.add(value)
    return deduped


class Config:
    """Configuración centralizada con validación."""
    
    # ── Tokens de mensajería ──────────────────────────────────────────────────
    TELEGRAM_TOKEN     = os.getenv("TELEGRAM_TOKEN", "")

    # ── APIs de LLM — cascada de prioridad ────────────────────────────────────
    # Groq (el más rápido — prioridad 1)
    GROQ_API_KEY       = os.getenv("GROQ_API_KEY", "")

    # Gemini directo — 6 claves rotan si una falla (prioridad 2-7)
    GEMINI_API_KEY     = os.getenv("GEMINI_API_KEY",   "")
    GEMINI_API_KEY_2   = os.getenv("GEMINI_API_KEY_2", "")
    GEMINI_API_KEY_3   = os.getenv("GEMINI_API_KEY_3", "")
    GEMINI_API_KEY_4   = os.getenv("GEMINI_API_KEY_4", "")
    GEMINI_API_KEY_5   = os.getenv("GEMINI_API_KEY_5", "")
    GEMINI_API_KEY_6   = os.getenv("GEMINI_API_KEY_6", "")
    GEMINI_API_KEYS    = _collect_env_series("GEMINI_API_KEY")

    # OpenRouter — acceso a todos los modelos (prioridad 5)
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")

    # OpenAI — último recurso (prioridad 6)
    OPENAI_API_KEY     = os.getenv("OPENAI_API_KEY", "")

    # Nvidia NIM — Vision & LLM
    NVIDIA_API_KEY     = os.getenv("NVIDIA_API_KEY", "")

    # Anthropic directo (opcional, ya está en OpenRouter)
    ANTHROPIC_API_KEY  = os.getenv("ANTHROPIC_API_KEY", "")

    # ── APIs de búsqueda ──────────────────────────────────────────────────────
    BRAVE_API_KEY      = os.getenv("BRAVE_API_KEY", "")
    BRAVE_API_KEYS     = _collect_env_series("BRAVE_API_KEY")
    APIFY_API_KEY      = os.getenv("APIFY_API_KEY", "")
    APIFY_API_KEYS     = _collect_env_series("APIFY_API_KEY")
    SERP_API_KEY       = os.getenv("SERP_API_KEY", "")
    SERP_API_KEYS      = _collect_env_series("SERP_API_KEY")

    # ── Calendario ────────────────────────────────────────────────────────────
    # Calendly — link directo que Firby puede enviar al paciente
    CALENDLY_LINK      = os.getenv("CALENDLY_LINK", "")
    # Google Calendar — OAuth tokens (se obtienen via /vincular-agenda)
    GCAL_ACCESS_TOKEN  = os.getenv("GCAL_ACCESS_TOKEN", "")
    GCAL_REFRESH_TOKEN = os.getenv("GCAL_REFRESH_TOKEN", "")
    GCAL_CLIENT_ID     = os.getenv("GCAL_CLIENT_ID", "")
    GCAL_CLIENT_SECRET = os.getenv("GCAL_CLIENT_SECRET", "")
    GCAL_CALENDAR_ID   = os.getenv("GCAL_CALENDAR_ID", "primary")

    # ── Meta App (de Santiago — para auto-registrar webhooks de todos los clientes) ──
    META_APP_ID        = os.getenv("META_APP_ID", "")
    META_APP_SECRET    = os.getenv("META_APP_SECRET", "")

    # ── Nova — Motor de Gobernanza ────────────────────────────────────────────
    NOVA_URL           = os.getenv("NOVA_URL",     "http://localhost:9003")
    NOVA_TOKEN         = os.getenv("NOVA_TOKEN",   "")   # Token del agente Firby
    NOVA_API_KEY       = os.getenv("NOVA_API_KEY", "")   # API key de Nova
    NOVA_ENABLED       = os.getenv("NOVA_ENABLED", "false").lower() == "true"
    
    # Webhook
    WEBHOOK_SECRET     = os.getenv("WEBHOOK_SECRET", "firby_ultra_5")
    BASE_URL           = os.getenv("BASE_URL", "")
    TELEGRAM_SHARED    = os.getenv("TELEGRAM_SHARED", "false").lower() == "true"
    TELEGRAM_SHARED_ROUTER = os.getenv("TELEGRAM_SHARED_ROUTER", "false").lower() == "true"
    TELEGRAM_SHARED_SECRET = os.getenv("TELEGRAM_SHARED_SECRET", "firby_shared_telegram")
    TELEGRAM_DEFAULT_INSTANCE = os.getenv("TELEGRAM_DEFAULT_INSTANCE", "").strip()
    TELEGRAM_SHARED_ALLOW_DEFAULT_FALLBACK = os.getenv(
        "TELEGRAM_SHARED_ALLOW_DEFAULT_FALLBACK", "false"
    ).lower() == "true"
    _FIRBY_HOME = os.getenv("FIRBY_HOME", str(Path.home() / ".firby"))
    TELEGRAM_SHARED_ROUTES_PATH = os.getenv(
        "TELEGRAM_SHARED_ROUTES_PATH",
        str(Path(_FIRBY_HOME) / "shared_telegram_routes.json"),
    )
    TELEGRAM_SHARED_INSTANCES_DIR = os.getenv(
        "TELEGRAM_SHARED_INSTANCES_DIR",
        str(Path(_FIRBY_HOME) / "instances"),
    )

    # Plataforma: "telegram" | "whatsapp_cloud" | "evolution" | "whatsapp"
    PLATFORM           = os.getenv("PLATFORM", "telegram")

    # WhatsApp Bridge (Baileys)
    WHATSAPP_BRIDGE_URL = os.getenv("WHATSAPP_BRIDGE_URL", "http://127.0.0.1:8002")

    # Sector del negocio (sincronizado con firby_cli.py)
    SECTOR             = os.getenv("SECTOR", "otro")

    # WhatsApp Cloud API (Meta oficial)
    WA_PHONE_ID        = os.getenv("WA_PHONE_ID", "")         # Phone Number ID de Meta
    WA_ACCESS_TOKEN    = os.getenv("WA_ACCESS_TOKEN", "")     # Token permanente de Meta
    WA_VERIFY_TOKEN    = os.getenv("WA_VERIFY_TOKEN", "")     # Para verificar webhook

    # Evolution API (auto-hospedado, alternativa economica)
    EVOLUTION_URL      = os.getenv("EVOLUTION_URL", "")       # http://tu-server:8080
    EVOLUTION_API_KEY  = os.getenv("EVOLUTION_API_KEY", "")
    EVOLUTION_INSTANCE = os.getenv("EVOLUTION_INSTANCE", "firby")

    # Auth — sistema de activacion multi-admin
    MASTER_API_KEY     = os.getenv("MASTER_API_KEY", "")           # Clave de Santiago para crear tokens
    N8N_WEBHOOK_URL    = os.getenv("N8N_WEBHOOK_URL", "")          # URL N8N para notificaciones
    TOKEN_EXPIRY_HOURS = int(os.getenv("TOKEN_EXPIRY_HOURS", "72")) # Tokens expiran en 72h

    # ── MODO DEMO ─────────────────────────────────────────────────────────────
    DEMO_MODE          = os.getenv("DEMO_MODE", "false").lower() == "true"
    DEMO_BUSINESS_NAME = os.getenv("DEMO_BUSINESS_NAME", "tu negocio")
    DEMO_SECTOR        = os.getenv("DEMO_SECTOR", "estetica")
    DEMO_SESSION_TTL   = int(os.getenv("DEMO_SESSION_TTL", "1800"))  # 30 min por persona
    GREETING_ONLY_IDLE_SECONDS = int(os.getenv("GREETING_ONLY_IDLE_SECONDS", "5"))

    # ── V8.0 — Gestión dinámica de modelos ─────────────────────────────────────
    V8_ACTIVE_MODEL_REASONING = os.getenv("V8_ACTIVE_MODEL_REASONING", "")
    V8_ACTIVE_MODEL_FAST      = os.getenv("V8_ACTIVE_MODEL_FAST", "")
    V8_ACTIVE_MODEL_LITE      = os.getenv("V8_ACTIVE_MODEL_LITE", "")

    # Catálogo de modelos disponibles para cambio en caliente
    V8_MODEL_CATALOG = {
        # ── Anthropic ──────────────────────────────────────────────
        "claude-opus":    ("anthropic/claude-opus-4",          "reasoning", "Más inteligente. Más caro."),
        "claude-sonnet":  ("anthropic/claude-sonnet-4",        "reasoning", "Balance inteligencia/costo. Recomendado."),
        "claude-haiku":   ("anthropic/claude-haiku-3-5",       "fast",      "Rapidísimo y económico."),
        # ── Google ─────────────────────────────────────────────────
        "gemini-pro":     ("google/gemini-2.5-pro",            "reasoning", "Google Pro. Muy capaz."),
        "gemini-flash":   ("google/gemini-2.5-flash",          "fast",      "Velocidad + calidad Google."),
        "gemini-lite":    ("google/gemini-2.5-flash-lite",     "lite",      "El más económico de Google."),
        # ── Meta Llama ─────────────────────────────────────────────
        "llama-70b":      ("meta-llama/llama-3.3-70b-instruct","fast",      "Open source, excelente español."),
        "llama-8b":       ("meta-llama/llama-3.1-8b-instruct", "lite",      "Ultrarrápido, básico."),
        # ── OpenAI ─────────────────────────────────────────────────
        "gpt4o":          ("openai/gpt-4o",                    "reasoning", "OpenAI flagship."),
        "gpt4o-mini":     ("openai/gpt-4o-mini",               "fast",      "OpenAI económico."),
        # ── Mistral ────────────────────────────────────────────────
        "mistral-large":  ("mistralai/mistral-large",          "reasoning", "Europeo, buen español."),
        "mistral-small":  ("mistralai/mistral-small",          "fast",      "Rápido y asequible."),
    }

    # Calidad de respuesta — forzar regeneración si score bajo
    V8_QUALITY_THRESHOLD  = float(os.getenv("V8_QUALITY_THRESHOLD", "0.72"))
    V8_MAX_RETRIES        = int(os.getenv("V8_MAX_RETRIES", "3"))
    FIRBY_COMPACT_PROMPT = os.getenv("FIRBY_COMPACT_PROMPT", "true").lower() in ("1", "true", "yes", "on")
    FIRBY_CONTEXT_RECENT_MESSAGES = int(os.getenv("FIRBY_CONTEXT_RECENT_MESSAGES", "12"))
    FIRBY_CORE_ENABLED = os.getenv("FIRBY_CORE_ENABLED", "true").lower() in ("1", "true", "yes", "on")
    FIRBY_CORE_PERSONAS_DIR = os.getenv(
        "FIRBY_CORE_PERSONAS_DIR",
        str(Path(__file__).resolve().parent.parent.parent / "core" / "personas" / "firby" / "base"),
    )

    # AntiRobotFilter — nivel de agresividad (1=suave, 2=normal, 3=estricto)
    V8_FILTER_LEVEL       = int(os.getenv("V8_FILTER_LEVEL", "2"))

    # Database
    DB_PATH            = os.getenv("DB_PATH", "/home/ubuntu/firby/firby_ultra.db")
    VECTOR_DB_PATH     = os.getenv("VECTOR_DB_PATH", "/home/ubuntu/firby/vectors.db")
    
    # Modelos LLM (cascada de calidad)
    LLM_MODELS = {
        "reasoning": os.getenv("LLM_REASONING", "google/gemini-3.5-flash"),
        "fast": os.getenv("LLM_FAST", "google/gemini-2.5-flash"),
        "lite": os.getenv("LLM_LITE", "google/gemini-2.5-flash-lite"),
        "embedding": os.getenv("LLM_EMBEDDING", "openai/text-embedding-3-small"),
    }
    
    # Whisper
    WHISPER_MODEL = os.getenv("WHISPER_MODEL", "openai/whisper-large-v3")
    
    # Buffer inteligente
    BUFFER_WAIT_MIN    = int(os.getenv("BUFFER_WAIT_MIN", "25"))
    BUFFER_WAIT_MAX    = int(os.getenv("BUFFER_WAIT_MAX", "45"))
    BUBBLE_PAUSE_MIN   = float(os.getenv("BUBBLE_PAUSE_MIN", "1.2"))
    BUBBLE_PAUSE_MAX   = float(os.getenv("BUBBLE_PAUSE_MAX", "3.0"))
    BRAND_ASSETS_BASE_DIR = os.getenv(
        "BRAND_ASSETS_BASE_DIR",
        "/home/ubuntu/firby/brand-assets",
    )
    
    # Auto-mejora
    SELF_IMPROVE_INTERVAL = int(os.getenv("SELF_IMPROVE_INTERVAL", "3600"))  # cada hora
    LEARNING_RATE         = float(os.getenv("LEARNING_RATE", "0.1"))
    
    # Límites
    MAX_CONTEXT_MESSAGES = int(os.getenv("MAX_CONTEXT", "150"))
    MAX_MEMORY_ITEMS     = int(os.getenv("MAX_MEMORY", "1000"))
    
    @classmethod
    def validate(cls) -> List[str]:
        """Valida configuración y retorna errores."""
        errors = []
        if not cls.TELEGRAM_TOKEN:
            errors.append("TELEGRAM_TOKEN requerido")
        if not cls.OPENROUTER_API_KEY and not cls.GEMINI_API_KEY:
            errors.append("Se requiere al menos OPENROUTER_API_KEY o GEMINI_API_KEY")
        return errors