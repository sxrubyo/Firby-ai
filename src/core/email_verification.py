"""
Módulo de Verificación de Seguridad por Correo Electrónico (OTP 6 Dígitos)
Integración con Resend API para Firby AI (firbyai.lat)
"""
import os
import re
import json
import time
import hmac
import hashlib
import secrets
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Tuple
import httpx

log = logging.getLogger("firby.email_verification")

# Configuración por defecto
RESEND_API_URL = "https://api.resend.com/emails"
DEFAULT_FROM_EMAIL = "Firby <contacto@firbyai.lat>"
FALLBACK_FROM_EMAIL = "Firby <noreply@firbyai.lat>"
OTP_EXPIRATION_MINUTES = 10
MAX_VERIFICATION_ATTEMPTS = 5
MAX_REQUESTS_PER_EMAIL_HOUR = 3
MAX_REQUESTS_PER_IP_10MIN = 5
RESEND_COOLDOWN_SECONDS = 60

EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")


def get_resend_api_key() -> str:
    """Obtiene la clave de API de Resend desde el entorno o archivo .env."""
    key = os.getenv("RESEND_API_KEY", "").strip()
    if key:
        return key

    # Buscar en .env local o en la raíz
    candidate_paths = [
        "/home/ubuntu/firby/.env",
        "/home/ubuntu/firby/instances/clinica-de-las-americas/.env",
        ".env"
    ]
    for p in candidate_paths:
        if os.path.exists(p):
            try:
                with open(p, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith("RESEND_API_KEY="):
                            val = line.split("=", 1)[1].strip().strip('"').strip("'")
                            if val:
                                return val
            except Exception:
                pass
    return ""


def validate_email_address(email: str) -> bool:
    """Valida sintácticamente una dirección de correo."""
    if not email or len(email) > 254:
        return False
    return bool(EMAIL_REGEX.match(email.strip()))


def generate_otp_code() -> str:
    """Genera un código numérico aleatorio de 6 dígitos criptográficamente seguro."""
    return f"{secrets.randbelow(900000) + 100000}"


def generate_salt() -> str:
    """Genera un salt hexadecimal criptográficamente seguro."""
    return secrets.token_hex(16)


def hash_otp_code(email: str, code: str, salt: str) -> str:
    """Calcula el hash SHA-256 del código con salt y normalización de correo."""
    payload = f"{salt}:{email.strip().lower()}:{code.strip()}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def generate_signed_verification_token(email: str, secret_key: str, expires_hours: int = 2) -> str:
    """Genera un token firmado que certifica que el correo fue verificado."""
    email_clean = email.strip().lower()
    exp = int(time.time()) + (expires_hours * 3600)
    payload_data = {
        "email": email_clean,
        "verified": True,
        "exp": exp,
        "nonce": secrets.token_hex(8)
    }
    payload_str = json.dumps(payload_data, sort_keys=True)
    signature = hmac.new(secret_key.encode("utf-8"), payload_str.encode("utf-8"), hashlib.sha256).hexdigest()
    combined = f"{payload_str}||{signature}"
    import base64
    return base64.urlsafe_b64encode(combined.encode("utf-8")).decode("utf-8")


def verify_signed_verification_token(token: str, secret_key: str) -> Optional[str]:
    """Valida el token firmado y retorna el correo si es válido y vigente."""
    try:
        import base64
        decoded = base64.urlsafe_b64decode(token.encode("utf-8")).decode("utf-8")
        if "||" not in decoded:
            return None
        payload_str, signature = decoded.split("||", 1)
        expected_sig = hmac.new(secret_key.encode("utf-8"), payload_str.encode("utf-8"), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(signature, expected_sig):
            return None
        data = json.loads(payload_str)
        if not data.get("verified"):
            return None
        if data.get("exp", 0) < time.time():
            return None
        return data.get("email")
    except Exception:
        return None


def render_otp_email_html(code: str, email: str, purpose_label: str = "acceder a tu cuenta", ip_address: str = "") -> str:
    """
    Plantilla HTML pura, ultra-minimalista inspirada exactamente en el correo transaccional de Canva.
    Sin fondos duros, sin tarjetas, sin marcos ni bloques de 'Verificación de seguridad'.
    Usa tipografía limpia, espaciado generoso, respeta el tema claro/oscuro del cliente
    y muestra el isotipo original transparente de Firby en el pie de página.
    """
    action_text = (
        "iniciar sesión en tu cuenta de Firby"
        if ("iniciar" in purpose_label.lower() or "login" in purpose_label.lower())
        else ("activar tu cuenta de Firby" if ("crear" in purpose_label.lower() or "register" in purpose_label.lower()) else "acceder a tu cuenta de Firby")
    )

    return f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{code} es tu código de Firby</title>
    <style>
        body {{
            margin: 0;
            padding: 0;
            -webkit-text-size-adjust: 100%;
            -ms-text-size-adjust: 100%;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            color: #111827;
        }}
        @media (prefers-color-scheme: dark) {{
            .firby-email-body {{
                color: #f3f4f6 !important;
            }}
            .firby-title {{
                color: #ffffff !important;
            }}
            .firby-code {{
                color: #ffffff !important;
            }}
            .firby-notice {{
                color: #9ca3af !important;
            }}
            .firby-footer {{
                color: #9ca3af !important;
            }}
            .firby-link {{
                color: #d1d5db !important;
            }}
        }}
    </style>
</head>
<body style="margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; color: #111827; background-color: transparent;">
    <div style="max-width: 520px; margin: 0 auto; padding: 48px 24px 32px 24px; text-align: left;" class="firby-email-body">
        <!-- Título principal -->
        <h1 class="firby-title" style="margin: 0 0 16px 0; font-size: 24px; font-weight: 700; color: #111827; letter-spacing: -0.02em; line-height: 1.3;">
            Inicia sesión en tu cuenta de Firby
        </h1>

        <!-- Subtítulo / Indicación -->
        <p style="margin: 0 0 28px 0; font-size: 15px; line-height: 1.6; color: inherit;">
            Ingresa este código en los próximos 10 minutos para {action_text}.
        </p>

        <!-- Código de 6 dígitos limpio sin bordes ni cajas -->
        <div class="firby-code" style="margin: 28px 0 36px 0; font-size: 38px; font-weight: 700; letter-spacing: 6px; color: #111827; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;">
            {code}
        </div>

        <!-- Descargo transaccional estilo Canva -->
        <p class="firby-notice" style="margin: 36px 0 32px 0; font-size: 13px; line-height: 1.6; color: #6b7280;">
            Recibes este correo porque tienes una cuenta en Firby. Este no es un correo publicitario ni promocional, por lo que no incluye un enlace para cancelar la suscripción. Recibirás este correo incluso si te has dado de baja de los correos comerciales de Firby.
        </p>

        <!-- Isotipo original abajo sin fondo para no dañar el tema de color -->
        <div style="margin-top: 40px; padding-top: 24px; border-top: 1px solid rgba(156, 163, 175, 0.25);">
            <a href="https://firbyai.lat" target="_blank" style="text-decoration: none; display: inline-block; margin: 0; padding: 0;">
                <img src="https://firbyai.lat/firby_logo_flush.png" width="110" height="auto" alt="Firby" style="display: block; width: 110px; height: auto; border: 0; outline: none; margin: 0 0 16px 0; padding: 0;" />
            </a>

            <!-- Datos de pie de página -->
            <div class="firby-footer" style="font-size: 12px; line-height: 1.6; color: #9ca3af;">
                <span style="font-weight: 600; color: inherit;">Firby AI</span><br>
                Firby AI Inc. &middot; <a href="https://firbyai.lat" target="_blank" class="firby-link" style="color: #6b7280; text-decoration: none;">firbyai.lat</a><br>
                <a href="https://firbyai.lat/privacy" target="_blank" class="firby-link" style="color: #6b7280; text-decoration: underline; margin-right: 8px;">Política de Privacidad</a>
                <a href="https://firbyai.lat/terms" target="_blank" class="firby-link" style="color: #6b7280; text-decoration: underline;">Términos de Servicio</a>
            </div>
        </div>
    </div>
</body>
</html>
"""


def render_otp_email_text(code: str, email: str, purpose_label: str = "acceder a tu cuenta", ip_address: str = "") -> str:
    """Versión en texto plano pura estilo Canva."""
    action_text = (
        "iniciar sesion en tu cuenta de Firby"
        if ("iniciar" in purpose_label.lower() or "login" in purpose_label.lower())
        else ("activar tu cuenta de Firby" if ("crear" in purpose_label.lower() or "register" in purpose_label.lower()) else "acceder a tu cuenta de Firby")
    )
    return (
        f"Inicia sesion en tu cuenta de Firby\n\n"
        f"Ingresa este codigo en los proximos 10 minutos para {action_text}.\n\n"
        f"{code}\n\n"
        f"Recibes este correo porque tienes una cuenta en Firby. Este no es un correo publicitario ni promocional, por lo que no incluye un enlace para cancelar la suscripcion. Recibiras este correo incluso si te has dado de baja de los correos comerciales de Firby.\n\n"
        f"Firby AI\n"
        f"Firby AI Inc. - firbyai.lat\n"
        f"https://firbyai.lat/privacy | https://firbyai.lat/terms"
    )


def send_verification_email(
    to_email: str,
    code: str,
    purpose_label: str = "acceder a tu cuenta",
    ip_address: str = "",
    from_email: Optional[str] = None
) -> Tuple[bool, str]:
    """
    Envía el correo electrónico con el código de 6 dígitos a través de Resend API.
    Retorna (éxito: bool, id_o_error: str).
    """
    api_key = get_resend_api_key()
    if not api_key:
        err = "Clave RESEND_API_KEY no configurada en el sistema."
        log.error(f"[send_verification_email] {err}")
        return False, err

    subject = f"{code} es tu código de Firby"
    html_content = render_otp_email_html(code, to_email, purpose_label, ip_address)
    text_content = render_otp_email_text(code, to_email, purpose_label, ip_address)
    sender = (from_email or "").strip() or DEFAULT_FROM_EMAIL

    payload = {
        "from": sender,
        "to": [to_email.strip().lower()],
        "subject": subject,
        "html": html_content,
        "text": text_content
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    try:
        with httpx.Client(timeout=10.0) as client:
            resp = client.post(RESEND_API_URL, headers=headers, json=payload)
            if resp.status_code in (200, 201):
                data = resp.json()
                email_id = data.get("id", "")
                log.info(f"[send_verification_email] Correo enviado exitosamente a {to_email} (ID: {email_id})")
                return True, email_id
            elif resp.status_code == 403 or "domain" in resp.text.lower():
                payload["from"] = FALLBACK_FROM_EMAIL
                resp2 = client.post(RESEND_API_URL, headers=headers, json=payload)
                if resp2.status_code in (200, 201):
                    data2 = resp2.json()
                    email_id2 = data2.get("id", "")
                    log.info(f"[send_verification_email] Correo enviado via fallback a {to_email} (ID: {email_id2})")
                    return True, email_id2
                error_msg = f"Error Resend ({resp2.status_code}): {resp2.text}"
                log.error(f"[send_verification_email] {error_msg}")
                return False, error_msg
            else:
                error_msg = f"Error Resend ({resp.status_code}): {resp.text}"
                log.error(f"[send_verification_email] {error_msg}")
                return False, error_msg
    except Exception as e:
        error_msg = f"Excepción enviando correo con Resend: {str(e)}"
        log.error(f"[send_verification_email] {error_msg}")
        return False, error_msg


async def send_verification_email_async(
    to_email: str,
    code: str,
    purpose_label: str = "verificar tu identidad",
    ip_address: str = "",
    from_email: Optional[str] = None
) -> Tuple[bool, str]:
    """Envío asíncrono no bloqueante de correo con httpx.AsyncClient."""
    api_key = get_resend_api_key()
    if not api_key:
        err = "Clave RESEND_API_KEY no configurada en el sistema."
        log.error(f"[send_verification_email_async] {err}")
        return False, err

    subject = f"{code} es tu código de Firby"
    html_content = render_otp_email_html(code, to_email, purpose_label, ip_address)
    text_content = render_otp_email_text(code, to_email, purpose_label, ip_address)
    sender = (from_email or "").strip() or DEFAULT_FROM_EMAIL

    payload = {
        "from": sender,
        "to": [to_email.strip().lower()],
        "subject": subject,
        "html": html_content,
        "text": text_content
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(RESEND_API_URL, headers=headers, json=payload)
            if resp.status_code in (200, 201):
                data = resp.json()
                return True, data.get("id", "")
            elif resp.status_code == 403 or "domain" in resp.text.lower():
                payload["from"] = FALLBACK_FROM_EMAIL
                resp2 = await client.post(RESEND_API_URL, headers=headers, json=payload)
                if resp2.status_code in (200, 201):
                    return True, resp2.json().get("id", "")
                return False, f"Error Resend ({resp2.status_code}): {resp2.text}"
            return False, f"Error Resend ({resp.status_code}): {resp.text}"
    except Exception as e:
        return False, f"Excepción enviando correo: {str(e)}"


class EmailVerificationService:
    """
    Servicio central de emisión, rate-limiting, almacenamiento y validación
    de códigos de verificación OTP de 6 dígitos.
    """

    def __init__(self, db_manager, secret_key: str = ""):
        self.db = db_manager
        self.secret_key = secret_key or os.getenv("MASTER_API_KEY") or os.getenv("SECRET_KEY", "firby-security-secret-master")

    def request_code(
        self,
        email: str,
        purpose: str = "verification",
        ip_address: str = "",
        user_agent: str = "",
        from_email: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Genera y envía un código de 6 dígitos al correo indicado si cumple los límites de tasa.
        """
        email_clean = (email or "").strip().lower()
        if not validate_email_address(email_clean):
            return {
                "ok": False,
                "error": "Dirección de correo electrónico inválida.",
                "status_code": 400
            }

        # 1. Rate Limiting por IP (Máx 5 solicitudes cada 10 min)
        if ip_address:
            ip_requests = self.db.count_recent_ip_verification_requests(ip_address, minutes=10)
            if ip_requests >= MAX_REQUESTS_PER_IP_10MIN:
                log.warning(f"[request_code] Rate limit excedido para IP {ip_address}")
                try:
                    self.db.log_auth_event(
                        email=email_clean,
                        provider="resend_otp",
                        action="send_code",
                        status="rate_limited",
                        ip_address=ip_address,
                        user_agent=user_agent,
                        details={"reason": "ip_rate_limit", "count": ip_requests}
                    )
                except Exception:
                    pass
                return {
                    "ok": False,
                    "error": "Demasiadas solicitudes desde esta dirección IP. Intenta nuevamente en unos minutos.",
                    "status_code": 429
                }

        # 2. Rate Limiting por Email (Máx 3 códigos por hora)
        email_requests = self.db.count_recent_verification_requests(email_clean, minutes=60)
        if email_requests >= MAX_REQUESTS_PER_EMAIL_HOUR:
            log.warning(f"[request_code] Rate limit excedido para correo {email_clean}")
            try:
                self.db.log_auth_event(
                    email=email_clean,
                    provider="resend_otp",
                    action="send_code",
                    status="rate_limited",
                    ip_address=ip_address,
                    user_agent=user_agent,
                    details={"reason": "email_rate_limit", "count": email_requests}
                )
            except Exception:
                pass
            return {
                "ok": False,
                "error": "Has alcanzado el límite de códigos por hora. Revisa tu bandeja de entrada o intenta más tarde.",
                "status_code": 429
            }

        # 3. Cooldown de 60 segundos entre reenvíos al mismo email
        latest = self.db.get_latest_verification_code(email_clean, purpose)
        if latest:
            created_at_str = latest.get("created_at")
            if created_at_str:
                try:
                    created_time = datetime.fromisoformat(created_at_str.replace("Z", ""))
                    diff_seconds = (datetime.now() - created_time).total_seconds()
                    if diff_seconds < RESEND_COOLDOWN_SECONDS:
                        wait_seconds = int(RESEND_COOLDOWN_SECONDS - diff_seconds)
                        return {
                            "ok": False,
                            "error": f"Por favor espera {wait_seconds} segundos antes de solicitar otro código.",
                            "status_code": 429,
                            "cooldown_seconds": wait_seconds
                        }
                except Exception:
                    pass

        # 4. Generación criptográfica del código y cálculo de hash + salt
        code = generate_otp_code()
        salt = generate_salt()
        code_hash = hash_otp_code(email_clean, code, salt)
        expires_at = (datetime.now() + timedelta(minutes=OTP_EXPIRATION_MINUTES)).strftime("%Y-%m-%d %H:%M:%S")

        # 5. Persistencia segura en base de datos
        code_id = self.db.store_verification_code(
            email=email_clean,
            code_hash=code_hash,
            salt=salt,
            purpose=purpose,
            expires_at=expires_at,
            ip_address=ip_address,
            user_agent=user_agent
        )

        if not code_id:
            return {
                "ok": False,
                "error": "Error interno al inicializar el registro de verificación.",
                "status_code": 500
            }

        # 6. Despacho por Resend
        purpose_label = "iniciar sesión" if purpose == "login" else ("crear tu cuenta" if purpose == "register" else "verificar tu correo")
        sent, detail = send_verification_email(email_clean, code, purpose_label, ip_address, from_email=from_email)

        if not sent:
            log.error(f"[request_code] Falló el despacho de correo para {email_clean}: {detail}")
            try:
                self.db.log_auth_event(
                    email=email_clean,
                    provider="resend_otp",
                    action="send_code",
                    status="failed",
                    ip_address=ip_address,
                    user_agent=user_agent,
                    details={"error": detail}
                )
            except Exception:
                pass
            return {
                "ok": False,
                "error": "No se pudo enviar el correo de verificación. Intenta nuevamente.",
                "status_code": 502
            }

        # Auditoría de éxito
        try:
            self.db.log_auth_event(
                email=email_clean,
                provider="resend_otp",
                action="send_code",
                status="success",
                ip_address=ip_address,
                user_agent=user_agent,
                details={"code_id": code_id, "resend_id": detail, "purpose": purpose}
            )
        except Exception:
            pass

        return {
            "ok": True,
            "message": "Código de verificación de 6 dígitos enviado a tu correo.",
            "expires_in_seconds": OTP_EXPIRATION_MINUTES * 60,
            "status_code": 200
        }

    def verify_code(
        self,
        email: str,
        code: str,
        purpose: str = "verification",
        ip_address: str = "",
        user_agent: str = ""
    ) -> Dict[str, Any]:
        """
        Valida el código de 6 dígitos ingresado por el usuario con protección anti-fuerza bruta.
        """
        email_clean = (email or "").strip().lower()
        code_clean = (code or "").strip()

        if not email_clean or not code_clean:
            return {
                "ok": False,
                "error": "Correo y código son obligatorios.",
                "status_code": 400
            }

        if len(code_clean) != 6 or not code_clean.isdigit():
            return {
                "ok": False,
                "error": "El código debe contener exactamente 6 dígitos numéricos.",
                "status_code": 400
            }

        record = self.db.get_latest_verification_code(email_clean, purpose)
        if not record:
            return {
                "ok": False,
                "error": "No hay ningún código de verificación activo para este correo.",
                "status_code": 404
            }

        code_id = record["id"]
        attempts = record.get("attempts", 0)
        max_attempts = record.get("max_attempts", MAX_VERIFICATION_ATTEMPTS)

        # 1. Comprobar si el código superó los intentos permitidos
        if attempts >= max_attempts:
            self.db.mark_verification_code_used(code_id)
            try:
                self.db.log_auth_event(
                    email=email_clean,
                    provider="resend_otp",
                    action="verify_code",
                    status="locked",
                    ip_address=ip_address,
                    user_agent=user_agent,
                    details={"reason": "max_attempts_exceeded", "code_id": code_id}
                )
            except Exception:
                pass
            return {
                "ok": False,
                "error": "Este código ha sido bloqueado por exceder el número máximo de intentos. Solicita uno nuevo.",
                "status_code": 429
            }

        # 2. Comprobar si ya expiró
        expires_at_str = record.get("expires_at", "")
        try:
            exp_time = datetime.strptime(expires_at_str, "%Y-%m-%d %H:%M:%S")
            if datetime.now() > exp_time:
                self.db.mark_verification_code_used(code_id)
                return {
                    "ok": False,
                    "error": "El código de verificación ha expirado. Por favor solicita uno nuevo.",
                    "status_code": 410
                }
        except Exception as e:
            log.warning(f"[verify_code] Error comparando expiración: {e}")

        # 3. Comprobar hash con comparación segura de tiempo constante
        salt = record.get("salt", "")
        expected_hash = record.get("code_hash", "")
        computed_hash = hash_otp_code(email_clean, code_clean, salt)

        if not hmac.compare_digest(computed_hash, expected_hash):
            new_attempts = self.db.increment_verification_attempts(code_id)
            remaining = max_attempts - new_attempts
            try:
                self.db.log_auth_event(
                    email=email_clean,
                    provider="resend_otp",
                    action="verify_code",
                    status="failed",
                    ip_address=ip_address,
                    user_agent=user_agent,
                    details={"attempts": new_attempts, "remaining": max(remaining, 0), "code_id": code_id}
                )
            except Exception:
                pass

            if remaining <= 0:
                self.db.mark_verification_code_used(code_id)
                return {
                    "ok": False,
                    "error": "Código incorrecto. Has superado el límite de intentos. Solicita un código nuevo.",
                    "status_code": 401
                }
            return {
                "ok": False,
                "error": f"Código incorrecto. Te quedan {remaining} intentos.",
                "status_code": 401,
                "remaining_attempts": remaining
            }

        # 4. Código VÁLIDO: Marcar como utilizado para que no pueda reusarse
        self.db.mark_verification_code_used(code_id)

        # 5. Generar token firmado de verificación
        auth_token = generate_signed_verification_token(email_clean, self.secret_key)

        try:
            self.db.log_auth_event(
                email=email_clean,
                provider="resend_otp",
                action="verify_code",
                status="success",
                ip_address=ip_address,
                user_agent=user_agent,
                details={"code_id": code_id, "purpose": purpose}
            )
        except Exception:
            pass

        return {
            "ok": True,
            "verified": True,
            "email": email_clean,
            "verification_token": auth_token,
            "message": "Correo electrónico verificado exitosamente.",
            "status_code": 200
        }
