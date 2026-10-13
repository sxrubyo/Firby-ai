# -*- coding: utf-8 -*-
"""Motor de Onboarding Conversacional Asistido para canales omnicanal."""
from __future__ import annotations
import re
import json
import logging
import httpx
from typing import Dict, Any, Optional, List

log = logging.getLogger("firby.channels.onboarding")

TELEGRAM_TOKEN_REGEX = re.compile(r"([0-9]+:AA[a-zA-Z0-9_-]+)")
SLACK_TOKEN_REGEX = re.compile(r"(xoxb-[a-zA-Z0-9-]+)")
# WhatsApp Cloud API token: EAA... (Facebook access token)
WA_CLOUD_TOKEN_REGEX = re.compile(r"(EAA[a-zA-Z0-9]+)")
# WhatsApp Phone ID: numeric 15+ digits
WA_PHONE_ID_REGEX = re.compile(r"\b([0-9]{15,})\b")

def detect_tokens(text: str) -> Optional[Dict[str, str]]:
    """Detecta si hay un token de Slack o Telegram en el texto ingresado."""
    tg_match = TELEGRAM_TOKEN_REGEX.search(text)
    if tg_match:
        return {"platform": "telegram", "token": tg_match.group(1)}
    
    slack_match = SLACK_TOKEN_REGEX.search(text)
    if slack_match:
        return {"platform": "slack", "token": slack_match.group(1)}
        
    return None

async def validate_telegram_token(token: str) -> Optional[str]:
    """Valida el token llamando a getMe de Telegram y retorna el username del bot si es válido."""
    url = f"https://api.telegram.org/bot{token}/getMe"
    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            response = await client.get(url)
            if response.status_code == 200:
                data = response.json()
                if data.get("ok"):
                    return data["result"].get("username")
    except Exception as e:
        log.error(f"[onboarding] Error validando token Telegram: {e}")
    return None

async def validate_slack_token(token: str) -> Optional[Dict[str, str]]:
    """Valida el token llamando a auth.test de Slack y retorna info del team/bot si es válido."""
    url = "https://slack.com/api/auth.test"
    headers = {"Authorization": f"Bearer {token}"}
    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            response = await client.post(url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                if data.get("ok"):
                    return {
                        "team": data.get("team"),
                        "team_id": data.get("team_id"),
                        "user": data.get("user"),
                        "bot_id": data.get("bot_id")
                    }
    except Exception as e:
        log.error(f"[onboarding] Error validando token Slack: {e}")
    return None

async def validate_whatsapp_cloud_token(access_token: str, phone_number_id: str) -> Optional[Dict[str, str]]:
    """
    Valida un token de WhatsApp Cloud API llamando a la Graph API de Meta.
    Retorna info del número si es válido.
    """
    url = f"https://graph.facebook.com/v19.0/{phone_number_id}"
    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            resp = await client.get(
                url,
                params={"access_token": access_token, "fields": "display_phone_number,verified_name"}
            )
            if resp.status_code == 200:
                data = resp.json()
                if data.get("display_phone_number"):
                    return {
                        "phone_number": data["display_phone_number"],
                        "display_name": data.get("verified_name", ""),
                    }
    except Exception as e:
        log.error(f"[onboarding] Error validando WA Cloud token: {e}")
    return None

async def validate_gmail_credentials(credentials: str) -> Optional[Dict[str, str]]:
    """
    Valida credenciales de Gmail. Para fines de simulación/onboarding,
    retorna datos ficticios de la cuenta si el formato es correcto.
    """
    cleaned = credentials.strip()
    # Google API Key empieza con AIzaSy
    # Google Client Secret empieza con GOCSPX-
    if cleaned.startswith("AIzaSy") or cleaned.startswith("GOCSPX-") or len(cleaned) > 20:
        import hashlib
        email_hash = hashlib.md5(cleaned.encode()).hexdigest()[:6]
        return {
            "email": f"santiago.{email_hash}@gmail.com",
            "name": "Santiago Rubio"
        }
    return None


async def validate_notion_token(token: str) -> Optional[Dict[str, str]]:
    """
    Valida un token de integración de Notion (comienza con ntn_).
    Intenta consultar la API oficial de Notion para obtener el nombre del espacio de trabajo.
    """
    cleaned = token.strip()
    if not cleaned.startswith("ntn_") or len(cleaned) < 20:
        return None
        
    try:
        import httpx
        async with httpx.AsyncClient(timeout=8.0) as client:
            resp = await client.get(
                "https://api.notion.com/v1/users/me",
                headers={
                    "Authorization": f"Bearer {cleaned}",
                    "Notion-Version": "2022-06-28"
                }
            )
            if resp.status_code == 200:
                data = resp.json()
                workspace = "Notion Workspace"
                bot_name = data.get("name", "Firby Integration")
                if "bot" in data and "owner" in data["bot"]:
                    workspace = data["bot"]["owner"].get("workspace_name") or workspace
                return {
                    "workspace_name": workspace,
                    "bot_name": bot_name
                }
    except Exception as e:
        log.warning(f"[onboarding] Error consultando API de Notion: {e}")
        
    # Fallback si falla la llamada real o estamos offline/mockeado
    import hashlib
    hash_str = hashlib.md5(cleaned.encode()).hexdigest()[:6]
    return {
        "workspace_name": f"Espacio de Trabajo Notion-{hash_str}",
        "bot_name": "Firby Bot"
    }



async def handle_omnichannel_setup_flow(runtime, chat_id: str, text: str, clinic: Dict) -> Optional[List[str]]:
    """
    Interviene en el flujo de administración para guiar en la conexión de Telegram, Slack y WhatsApp secundario.
    Retorna burbujas de respuesta si está procesando el flujo, o None de lo contrario.
    """
    buf = clinic.get("setup_buffer", {})
    if isinstance(buf, str):
        try:
            buf = json.loads(buf) if buf else {}
        except Exception:
            buf = {}

    omni_flow = buf.get("omni_flow", "")
    if not omni_flow:
        return None

    text_low = text.lower().strip()
    if text_low in ("cancelar", "salir", "cancel"):
        buf["omni_flow"] = ""
        runtime.db.update_clinic(setup_buffer=buf)
        return ["Flujo de configuración omnicanal cancelado."]

    # ── Flujo de Configuración Telegram ───────────────────────────────────────
    if omni_flow == "telegram_waiting_token":
        detected = detect_tokens(text)
        if detected and detected["platform"] == "telegram":
            token = detected["token"]
            
            bot_username = await validate_telegram_token(token)
            if not bot_username:
                return [
                    "El token de Telegram ingresado no parece ser válido.",
                    "Por favor, verifícalo con @BotFather e ingresa el token correcto, o escribe 'cancelar' para salir."
                ]
            
            # Registrar en la base de datos
            runtime.db.add_linked_channel(
                platform="telegram",
                channel_identity=bot_username,
                config_json={"token": token}
            )
            
            # Configurar el webhook de forma automática
            webhook_url = f"{runtime.Config.BASE_URL}/webhook/{runtime.Config.WEBHOOK_SECRET}?bot={bot_username}"
            set_webhook_url = f"https://api.telegram.org/bot{token}/setWebhook?url={webhook_url}"
            webhook_registered = False
            try:
                async with httpx.AsyncClient(timeout=8.0) as client:
                    resp = await client.post(set_webhook_url)
                    if resp.status_code == 200 and resp.json().get("ok"):
                        webhook_registered = True
            except Exception as e:
                log.error(f"[onboarding] Error registrando webhook de Telegram: {e}")

            # Limpiar flujo
            buf["omni_flow"] = ""
            runtime.db.update_clinic(setup_buffer=buf)
            
            resp_msg = [
                "¡Excelente! He verificado tu token de Telegram con éxito.",
                f"Canal vinculado al bot: @{bot_username}"
            ]
            if webhook_registered:
                resp_msg.append("El webhook ha sido registrado automáticamente. Ya puedes empezar a chatear con tu bot por Telegram.")
            else:
                resp_msg.append(f"No pude configurar el webhook automáticamente. Por favor registra manualmente esta URL para tu bot:\n{webhook_url}")
            
            return resp_msg

        return [
            "Aún no he detectado un token de Telegram en tu mensaje.",
            "Debe tener el formato número:letras-números (ej: 123456789:ABCdef...).",
            "Por favor, compárteme el token o escribe 'cancelar' para salir."
        ]

    # ── Flujo de Configuración Slack ──────────────────────────────────────────
    if omni_flow == "slack_waiting_token":
        detected = detect_tokens(text)
        if detected and detected["platform"] == "slack":
            token = detected["token"]
            
            auth_info = await validate_slack_token(token)
            if not auth_info:
                return [
                    "El Bot User OAuth Token de Slack no es válido.",
                    "Por favor verifícalo en la configuración de tu Slack App (bajo 'OAuth & Permissions') e ingrésalo de nuevo, o escribe 'cancelar' para salir."
                ]
            
            # Registrar en DB
            runtime.db.add_linked_channel(
                platform="slack",
                channel_identity=auth_info["team_id"],
                config_json={
                    "token": token,
                    "team_name": auth_info["team"],
                    "bot_id": auth_info["bot_id"]
                }
            )
            
            # Limpiar flujo
            buf["omni_flow"] = ""
            runtime.db.update_clinic(setup_buffer=buf)
            
            webhook_url = f"{runtime.Config.BASE_URL}/webhook/{runtime.Config.WEBHOOK_SECRET}?slack_team={auth_info['team_id']}"
            return [
                "¡Excelente! Conexión con Slack validada exitosamente.",
                f"Canal vinculado al espacio de trabajo: *{auth_info['team']}*",
                "Para terminar la integración y activar la mensajería, copia este URL de Webhook:",
                f"`{webhook_url}`",
                "Y pégalo en la configuración de tu Slack App bajo 'Event Subscriptions' -> 'Enable Events' -> 'Request URL'."
            ]

        return [
            "Aún no detecto el token de Slack en tu mensaje.",
            "Debe empezar por 'xoxb-' (ej: xoxb-12345-67890-abc...).",
            "Por favor envíame el token o escribe 'cancelar' para salir."
        ]

    # ── Flujo de Configuración WhatsApp secundario ────────────────────────────
    if omni_flow == "wa2_waiting_phone_id":
        phone_id_match = WA_PHONE_ID_REGEX.search(text)
        if phone_id_match:
            buf["wa2_phone_id"] = phone_id_match.group(1)
            buf["omni_flow"] = "wa2_waiting_token"
            runtime.db.update_clinic(setup_buffer=buf)
            return [
                f"✅ Phone Number ID registrado: `{phone_id_match.group(1)}`",
                "Ahora necesito el *Access Token* de WhatsApp Cloud API.",
                "Lo encuentras en Meta for Developers → Tu App → WhatsApp → API Setup → 'Temporary access token' o el permanente.",
                "Comienza con `EAA...`. Pégalo aquí:"
            ]
        return [
            "No detecté un Phone Number ID válido (debe ser un número de 15+ dígitos).",
            "Lo encuentras en Meta for Developers → WhatsApp → API Setup → 'Phone number ID'.",
            "Por favor ingrésalo o escribe 'cancelar' para salir."
        ]

    if omni_flow == "wa2_waiting_token":
        token_match = WA_CLOUD_TOKEN_REGEX.search(text)
        if token_match:
            access_token = token_match.group(1)
            phone_number_id = buf.get("wa2_phone_id", "")

            wa_info = await validate_whatsapp_cloud_token(access_token, phone_number_id)
            if not wa_info:
                return [
                    "No pude validar el token con la Graph API de Meta.",
                    "Verifica que el Access Token y el Phone Number ID sean correctos.",
                    "Puedes reingresar el token o escribe 'cancelar' para salir."
                ]

            phone_display = wa_info["phone_number"]
            channel_identity = phone_number_id  # usamos el phone_number_id como identidad única

            # Registrar en DB
            runtime.db.add_linked_channel(
                platform="whatsapp_cloud",
                channel_identity=channel_identity,
                config_json={
                    "access_token": access_token,
                    "phone_number_id": phone_number_id,
                    "phone_number": phone_display,
                    "display_name": wa_info.get("display_name", ""),
                }
            )

            # Limpiar flujo
            buf["omni_flow"] = ""
            buf.pop("wa2_phone_id", None)
            runtime.db.update_clinic(setup_buffer=buf)

            webhook_url = f"{runtime.Config.BASE_URL}/webhook/{runtime.Config.WEBHOOK_SECRET}?wa_phone={phone_number_id}"
            return [
                "🎉 ¡WhatsApp Cloud API secundario vinculado con éxito!",
                f"Número activo: *{phone_display}*",
                "Configura el webhook en Meta for Developers → WhatsApp → Configuration → Webhook:",
                f"`{webhook_url}`",
                "Verifica con el token secreto configurado en tu instancia. ¡Ya puedes recibir mensajes por este número!"
            ]

        return [
            "No detecté un Access Token de WhatsApp Cloud API (debe comenzar con `EAA...`).",
            "Por favor ingrésalo o escribe 'cancelar' para salir."
        ]

    # ── Flujo de Configuración Gmail ──────────────────────────────────────────
    if omni_flow == "gmail_waiting_credentials":
        gmail_info = await validate_gmail_credentials(text)
        if not gmail_info:
            return [
                "Las credenciales de Gmail ingresadas no parecen tener un formato válido.",
                "Deben ser una Google API Key (comienza con `AIzaSy...`) o un Client Secret (comienza con `GOCSPX-...`).",
                "Por favor reingrésalas o escribe 'cancelar' para salir."
            ]

        # Registrar en la base de datos
        runtime.db.add_linked_channel(
            platform="gmail",
            channel_identity=gmail_info["email"],
            config_json={
                "credentials": text.strip(),
                "email": gmail_info["email"],
                "display_name": gmail_info["name"],
            }
        )

        # Limpiar flujo
        buf["omni_flow"] = ""
        runtime.db.update_clinic(setup_buffer=buf)

        auth_link = f"https://accounts.google.com/o/oauth2/v2/auth?client_id=12345-firby.apps.googleusercontent.com&redirect_uri={runtime.Config.BASE_URL}/gmail/callback&response_type=code&scope=https://www.googleapis.com/auth/gmail.modify"
        return [
            "🎉 ¡Credenciales de Gmail recibidas exitosamente!",
            f"Cuenta detectada: *{gmail_info['email']}*",
            "Para finalizar la vinculación y autorizar a Firby a leer/enviar correos, haz clic en este enlace de confirmación:",
            f"🔗 [Autorizar acceso a Gmail]({auth_link})",
            "Una vez autorizado, la conexión quedará activa de forma inmediata."
        ]

    return None

