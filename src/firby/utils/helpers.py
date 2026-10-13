# -*- coding: utf-8 -*-
from __future__ import annotations
import hashlib
import json
import logging
import secrets
import re
from typing import Any, Dict, List, Optional, Callable

log = logging.getLogger("firby.helpers")

ACTIVATION_PREFIX = "ACTV-"
INVITE_PREFIX = "JINV-"

def is_activation_token(text: str) -> bool:
    """Detecta si el mensaje es un token de activacion."""
    t = text.strip().upper()
    return (t.startswith(ACTIVATION_PREFIX) or t.startswith("ADMN-")) and len(t) >= 20

def is_admin_activation_token(text: str) -> bool:
    """Detecta si el mensaje es un token de activacion de administrador."""
    t = text.strip().upper()
    return t.startswith("ADMN-") and len(t) >= 20

def is_invite_token(text: str) -> bool:
    """Detecta si el mensaje es un token de invitacion."""
    t = text.strip().upper()
    return t.startswith(INVITE_PREFIX) and len(t) >= 15

def generate_activation_token(label: str = "firby") -> str:
    """
    Genera un token de activacion de alta entropia.
    Formato: ACTV-[label_sanitizado]-[32_chars_hex]
    """
    sanitized = re.sub(r'[^a-zA-Z0-9]', '', (label or "firby").lower())[:10]
    if not sanitized or sanitized == "firby":
        sanitized = "firby"
    entropy = secrets.token_hex(16).upper()
    return f"{ACTIVATION_PREFIX}{sanitized.upper()}-{entropy}"

def generate_admin_activation_token(label: str = "firby") -> str:
    """
    Genera un token de activacion de administrador de alta entropia.
    Formato: ADMN-[label_sanitizado]-[32_chars_hex]
    """
    sanitized = re.sub(r'[^a-zA-Z0-9]', '', (label or "firby").lower())[:10]
    if not sanitized or sanitized == "firby":
        sanitized = "firby"
    entropy = secrets.token_hex(16).upper()
    return f"ADMN-{sanitized.upper()}-{entropy}"

def hash_password(password: str) -> str:
    """Hash de contrasena con PBKDF2 + salt."""
    salt = secrets.token_hex(16)
    key = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        260_000
    ).hex()
    return f"{salt}:{key}"

def verify_password(password: str, stored_hash: str) -> bool:
    """Verifica contrasena contra hash almacenado."""
    try:
        salt, key = stored_hash.split(":", 1)
        test = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt.encode("utf-8"),
            260_000
        ).hex()
        return test == key
    except Exception:
        return False

def _parse_admin_ids(raw) -> list:
    """Parsea admin_chat_ids de forma segura."""
    if not raw: return []
    if isinstance(raw, list): return [str(i) for i in raw]
    if isinstance(raw, str):
        try:
            data = json.loads(raw)
            if isinstance(data, list): return [str(i) for i in data]
            return [str(data)]
        except Exception:
            return [i.strip() for i in raw.split(",") if i.strip()]
    return []

def extract_model_request_from_text(text: str) -> Optional[str]:
    """Extrae solicitud de cambio de modelo del lenguaje natural."""
    t = text.lower().strip()
    if not t.startswith("/modelo"):
        if "cambia el modelo a" in t: return t.split("cambia el modelo a")[-1].strip()
        if "usa el modelo" in t: return t.split("usa el modelo")[-1].strip()
        return None
    parts = t.split()
    return parts[1] if len(parts) > 1 else "reset"

def normalize_model_arg(arg: str) -> str:
    """Normaliza el nombre del modelo solicitado."""
    m = arg.lower().strip()
    if m in ("flash", "gemini"): return "google/gemini-2.5-flash"
    if m in ("pro", "sonnet"): return "anthropic/claude-3-5-sonnet"
    if m in ("fast", "haiku"): return "anthropic/claude-3-haiku"
    return m

_ACCENT_MAP = str.maketrans({
    "á": "a", "é": "e", "í": "i", "ó": "o", "ú": "u", "ü": "u", "ñ": "n",
})

def _normalize_yn(text: str) -> str:
    t = (text or "").strip().lower().translate(_ACCENT_MAP)
    t = re.sub(r"[^a-z0-9\s]", " ", t)
    return re.sub(r"\s+", " ", t).strip()

_AMBIGUOUS_YES = {"si", "sisas", "siii", "ok", "oki", "va", "sip", "simon"}
_AMBIGUOUS_NO = {"no", "nel", "nop", "nope"}

_UNAMBIGUOUS_YES = {
    "dale", "claro", "obvio", "de una", "de una vez", "correcto",
    "asi es", "eso es", "eso mismo", "exacto", "exactamente", "vale",
    "listo", "perfecto", "bacano", "hagale", "confirmo", "confirmado",
    "afirmativo", "positivo", "yes", "yep", "yeah", "de acuerdo",
    "estoy de acuerdo", "me parece bien", "asi mismo",
}
_UNAMBIGUOUS_NO = {
    "negativo", "para nada", "que va", "ni de riesgos", "no gracias",
    "no quiero", "cancela", "cancelar", "olvidalo", "mejor no",
    "ni de vainas", "nada que ver", "salte", "salir", "sal de ahi",
    "salte de la simulacion", "salir de la simulacion", "salte de la demo",
}

def _contains_phrase(t: str, phrases) -> bool:
    for p in phrases:
        if re.search(r"\b" + re.escape(p) + r"\b", t):
            return True
    return False

def is_affirmative(text: str) -> bool:
    """
    True si el texto es una afirmacion clara en espanol coloquial/colombiano.
    """
    t = _normalize_yn(text)
    if not t:
        return False
    if t in _AMBIGUOUS_YES:
        return True
    return _contains_phrase(t, _UNAMBIGUOUS_YES)

def is_negative(text: str) -> bool:
    """True si el texto es una negacion clara en espanol coloquial/colombiano."""
    t = _normalize_yn(text)
    if not t:
        return False
    if t in _AMBIGUOUS_NO:
        return True
    return _contains_phrase(t, _UNAMBIGUOUS_NO)

def get_key_cascade(env: Dict[str, str], base_name: str, max_keys: int = 20) -> List[str]:
    """
    Devuelve todas las keys disponibles de una cascada tipo KEY, KEY_2, KEY_3...
    """
    keys: List[str] = []
    base = env.get(base_name)
    if base:
        keys.append(base)
    i = 2
    while i <= max_keys:
        k = env.get(f"{base_name}_{i}")
        if k:
            keys.append(k)
        i += 1
    return keys

async def notify_owner_of_ai_failure(
    send_fn: Callable[[str, str], Any],
    admin_ids: List[str],
    chat_id: str,
    last_message: str,
    context: str = "paciente",
) -> bool:
    """
    Avisa a todos los admins vinculados que la IA no pudo generar ninguna respuesta.
    """
    if not admin_ids:
        log.error(
            f"[ai_failure] la IA no pudo responderle a {chat_id} ({context}) y "
            f"NO hay ningun admin vinculado para avisar."
        )
        return False

    alert = (
        f"⚠️ Firby no pudo generarle ninguna respuesta a un {context} — "
        f"no le mande nada (asi lo configuraste, nunca un mensaje generico).\n\n"
        f"Chat: {chat_id}\n"
        f"Su ultimo mensaje: \"{(last_message or '').strip()[:300]}\"\n\n"
        f"Escribe directo en cuanto puedas."
    )
    notified = 0
    for admin_id in admin_ids:
        if admin_id == chat_id:
            continue
        try:
            await send_fn(admin_id, alert)
            notified += 1
        except Exception as e:
            log.error(f"[ai_failure] no pude avisarle al admin {admin_id}: {e}")

    if notified == 0:
        log.error(f"[ai_failure] habia {len(admin_ids)} admin(es) vinculados pero no le pude avisar a NINGUNO")
    return notified > 0

async def handle_ai_failure(
    chat_id: str,
    last_message: str,
    error: Exception,
    send_fn: Callable[[str, str], Any],
) -> None:
    """
    Reporta un fallo tecnico de la IA.
    """
    import os
    import httpx
    from src.core.globals import db

    instance = os.getenv("INSTANCE_NAME", "default")
    error_msg = str(error)

    # 1. Reportar error a OVNI (Dev)
    try:
        master_key = os.getenv("MASTER_API_KEY", "8432e72097f64c2340fc48920b16cb03da3378207a8f19942b528a43979c4ac2")
        payload = {
            "instance": instance,
            "chat_id": chat_id,
            "error": error_msg,
            "last_message": last_message
        }
        async with httpx.AsyncClient(timeout=5.0) as client:
            await client.post(
                "http://127.0.0.1:8008/api/dev/report_error",
                json=payload,
                headers={"X-Master-Key": master_key}
            )
    except Exception as e:
        log.error(f"[ovni_report] No se pudo notificar a OVNI sobre el error en {instance}:{chat_id}: {e}")

    # 2. Notificar al admin de la clinica (solo en producción real y excluyendo al propio chat_id)
    try:
        from firby_config import Config
        if not getattr(Config, "DEMO_MODE", False):
            clinic = db.get_clinic()
            admin_ids = [aid for aid in _parse_admin_ids(clinic.get("admin_chat_ids", [])) if aid != chat_id]
            if admin_ids:
                alert_text = (
                    f"🤖 [Asistente Firby] Hola. Acabo de tener un inconveniente técnico para "
                    f"procesar la respuesta al usuario con chat ID {chat_id}. Por favor, atiende "
                    f"la conversación de manera manual.\n\n"
                    f"Último mensaje recibido: \"{(last_message or '').strip()[:300]}\""
                )
                for admin_id in admin_ids:
                    try:
                        await send_fn(admin_id, alert_text)
                    except Exception as e_adm:
                        log.error(f"[admin_notify] Falló el envío de alerta al admin {admin_id}: {e_adm}")
    except Exception as e_glob:
        log.error(f"[admin_notify] Error general notificando a los admins de la clínica: {e_glob}")

    # 3. Notificar al paciente/usuario con calidez para que nunca quede en visto
    try:
        if chat_id and send_fn:
            patient_msg = "En este momento estoy consultando la disponibilidad del sistema. Dame un momentito y ya te respondo con gusto! 🙌"
            await send_fn(chat_id, patient_msg)
    except Exception as e_pat:
        log.warning(f"[patient_notify] No se pudo enviar mensaje de contingencia a {chat_id}: {e_pat}")

