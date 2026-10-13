# -*- coding: utf-8 -*-
"""Puente de integración con Google Calendar y Calendly modularizado de globals.py."""
from __future__ import annotations
import time
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional, Any

log = logging.getLogger("firby.calendar")

# Proxies dinámicos para evitar import circular en la inicialización
from src.firby.core.proxy import GlobalProxy

Config = GlobalProxy("Config")
httpx = GlobalProxy("httpx")

class CalendarBridge:
    """
    Puente inteligente entre Firby, el admin y su agenda.

    Jerarquia:
      1. Google Calendar vinculado -> consulta disponibilidad real en tiempo real
      2. Calendly configurado      -> manda el link directo al paciente
      3. Sin nada configurado      -> notifica al admin autonomamente y espera respuesta

    El admin vincula su Google Calendar una sola vez via OAuth (/vincular-agenda).
    Desde ahi Firby sabe su disponibilidad sin preguntarle.
    """

    GCAL_BASE = "https://www.googleapis.com/calendar/v3"
    GCAL_AUTH = "https://oauth2.googleapis.com/token"
    GCAL_SCOPE = "https://www.googleapis.com/auth/calendar.readonly"

    # Palabras que indican que el paciente pregunta por disponibilidad
    AVAILABILITY_SIGNALS = [
        "cuando", "que dia", "que días", "disponib", "horario", "cita",
        "agendar", "reservar", "puede ser", "tienes espacio", "hay espacio",
        "puedo ir", "cuando puedo", "que horas", "turno",
        "lunes", "martes", "miercoles", "jueves", "viernes", "sabado",
        "esta semana", "proxima semana", "hoy", "manana", "mañana",
        "tarde", "mañana", "medio dia", "mediodía",
    ]

    def __init__(self):
        self._access_token  = Config.GCAL_ACCESS_TOKEN
        self._refresh_token = Config.GCAL_REFRESH_TOKEN
        self._client_id     = Config.GCAL_CLIENT_ID
        self._client_secret = Config.GCAL_CLIENT_SECRET
        self._calendar_id   = Config.GCAL_CALENDAR_ID or "primary"
        self._calendly_link = Config.CALENDLY_LINK
        self._token_expiry  = 0.0  # timestamp when access token expires

    # ── Deteccion ──────────────────────────────────────────────────────────────

    def needs_calendar(self, text: str) -> bool:
        """Detecta si el mensaje del paciente requiere info de disponibilidad."""
        text_low = text.lower()
        return any(s in text_low for s in self.AVAILABILITY_SIGNALS)

    # ── Estado del puente ──────────────────────────────────────────────────────

    def has_google_calendar(self) -> bool:
        return bool(self._refresh_token and self._client_id and self._client_secret)

    def has_calendly(self) -> bool:
        return bool(self._calendly_link)

    def is_configured(self) -> bool:
        return self.has_google_calendar() or self.has_calendly()

    # ── OAuth — obtener/refrescar access token ─────────────────────────────────

    async def _ensure_token(self) -> bool:
        """Refresca el access token si expiró. Retorna True si hay token válido."""
        if not self.has_google_calendar():
            return False
        if time.time() < self._token_expiry - 60 and self._access_token:
            return True
        try:
            async with httpx.AsyncClient(timeout=10.0) as c:
                r = await c.post(self.GCAL_AUTH, data={
                    "grant_type":    "refresh_token",
                    "refresh_token": self._refresh_token,
                    "client_id":     self._client_id,
                    "client_secret": self._client_secret,
                })
                r.raise_for_status()
                data = r.json()
            self._access_token = data["access_token"]
            self._token_expiry = time.time() + data.get("expires_in", 3600)
            log.info("[calendar] token refrescado OK")
            return True
        except Exception as e:
            log.warning(f"[calendar] error refrescando token: {e}")
            return False

    # ── Consulta de disponibilidad ─────────────────────────────────────────────

    async def get_free_slots(self, days_ahead: int = 7) -> List[Dict]:
        """
        Retorna slots libres en los próximos N días.
        Consulta Google Calendar en tiempo real.
        """
        if not await self._ensure_token():
            return []

        now = datetime.now()
        time_min = now.isoformat() + "Z"
        time_max = (now + timedelta(days=days_ahead)).isoformat() + "Z"

        try:
            # Obtener eventos existentes (ocupados)
            async with httpx.AsyncClient(timeout=12.0) as c:
                r = await c.get(
                    f"{self.GCAL_BASE}/calendars/{self._calendar_id}/events",
                    headers={"Authorization": f"Bearer {self._access_token}"},
                    params={
                        "timeMin":      time_min,
                        "timeMax":      time_max,
                        "singleEvents": "true",
                        "orderBy":      "startTime",
                        "maxResults":   100,
                    }
                )
                r.raise_for_status()
                events = r.json().get("items", [])

            # Construir set de horarios ocupados
            busy_slots = set()
            for ev in events:
                start = ev.get("start", {}).get("dateTime", "")
                if start:
                    busy_slots.add(start[:16])  # "2025-03-15T10:00"

            # Generar slots disponibles (9am-6pm, cada 30 min)
            free = []
            for day_offset in range(days_ahead):
                day = now + timedelta(days=day_offset + 1)
                if day.weekday() >= 6:   # domingo = 6
                    continue
                for hour in range(9, 18):
                    for minute in (0, 30):
                        slot_dt = day.replace(hour=hour, minute=minute,
                                              second=0, microsecond=0)
                        slot_key = slot_dt.strftime("%Y-%m-%dT%H:%M")
                        if slot_key not in busy_slots:
                            free.append({
                                "datetime":  slot_dt.strftime("%Y-%m-%d %H:%M"),
                                "day_label": slot_dt.strftime("%A %d de %B"),
                                "time":      slot_dt.strftime("%I:%M %p"),
                                "iso":       slot_key,
                            })

            log.info(f"[calendar] {len(free)} slots libres en {days_ahead} dias")
            return free

        except Exception as e:
            log.warning(f"[calendar] error obteniendo slots: {e}")
            return []

    async def get_availability_summary(self) -> str:
        """
        Resumen de disponibilidad para inyectar en el system prompt de Firby.
        Máximo 3-4 días con los primeros slots de cada día.
        """
        slots = await self.get_free_slots(days_ahead=7)
        if not slots:
            return ""

        # Agrupar por día
        by_day: Dict[str, List[str]] = {}
        for s in slots:
            day = s["day_label"]
            by_day.setdefault(day, []).append(s["time"])

        lines = ["AGENDA REAL (Google Calendar — disponibilidad actual):"]
        count = 0
        for day, times in by_day.items():
            if count >= 4:
                break
            times_str = ", ".join(times[:4]) + (" y más" if len(times) > 4 else "")
            lines.append(f"  {day}: {times_str}")
            count += 1

        return "\n".join(lines)

    # ── Notificacion autonoma al admin ─────────────────────────────────────────

    async def notify_admin_availability_request(
        self,
        admin_ids: List[str],
        patient_name: str,
        patient_question: str,
        send_fn  # _send_message de FirbyUltra
    ):
        """
        Cuando no hay calendario vinculado, Firby le escribe al admin
        autónomamente para preguntarle su disponibilidad.
        """
        patient_str = patient_name if patient_name else "Un paciente"
        msg = (
            f"Hola! {patient_str} me preguntó sobre disponibilidad:\n\n"
            f"\"{patient_question[:120]}\"\n\n"
            f"No tengo acceso a tu agenda. Qué días y horas tienes disponibles "
            f"esta semana para decirle?"
        )
        for admin_id in admin_ids:
            try:
                await send_fn(admin_id, msg)
                log.info(f"[calendar] notificado admin {admin_id} sobre disponibilidad")
            except Exception as e:
                log.warning(f"[calendar] error notificando admin {admin_id}: {e}")

    # ── OAuth setup ────────────────────────────────────────────────────────────

    def get_oauth_url(self, redirect_uri: str) -> str:
        """Genera la URL de autorización de Google OAuth."""
        import urllib.parse
        scopes = [
            self.GCAL_SCOPE,
            "https://www.googleapis.com/auth/calendar.events",
            "https://www.googleapis.com/auth/userinfo.profile",
            "https://www.googleapis.com/auth/userinfo.email",
            "openid"
        ]
        params = {
            "client_id":     self._client_id,
            "redirect_uri":  redirect_uri,
            "response_type": "code",
            "scope":         " ".join(scopes),
            "access_type":   "offline",
            "prompt":        "consent",
        }
        return "https://accounts.google.com/o/oauth2/v2/auth?" + urllib.parse.urlencode(params)

    async def exchange_code(self, code: str, redirect_uri: str) -> Dict:
        """Intercambia el código OAuth por access + refresh tokens."""
        async with httpx.AsyncClient(timeout=15.0) as c:
            r = await c.post(self.GCAL_AUTH, data={
                "grant_type":   "authorization_code",
                "code":         code,
                "redirect_uri": redirect_uri,
                "client_id":    self._client_id,
                "client_secret": self._client_secret,
            })
            r.raise_for_status()
            return r.json()

    def update_tokens(self, access_token: str, refresh_token: str):
        """Actualiza los tokens en memoria (y debe guardarse en .env o DB)."""
        self._access_token  = access_token
        self._refresh_token = refresh_token
        self._token_expiry  = time.time() + 3600
        log.info("[calendar] tokens actualizados en memoria")

    async def create_event(
        self,
        patient_name: str,
        phone: str,
        service: str,
        date_time: str,
        duration_minutes: int = 60,
        notes: str = ""
    ) -> Optional[str]:
        """Crea un evento en Google Calendar para la cita confirmada."""
        if not await self._ensure_token():
            log.warning("[calendar] No valid Google Calendar token for creating event")
            return None

        try:
            # Parse datetime. date_time can be "2026-07-15 10:00" or ISO format "2026-07-15T10:00:00"
            dt_str = date_time.replace(" ", "T")
            if len(dt_str) == 16:  # "YYYY-MM-DDTHH:MM"
                dt_str += ":00"
            start_dt = datetime.fromisoformat(dt_str)
        except Exception as e:
            log.warning(f"[calendar] Invalid date format for create_event: {date_time} (error: {e})")
            return None

        end_dt = start_dt + timedelta(minutes=duration_minutes)

        event = {
            "summary": f"Cita: {patient_name} — {service}",
            "description": f"Paciente: {patient_name}\nTeléfono: {phone}\nServicio: {service}\nNotas: {notes}\nAgendado automáticamente por Firby AI",
            "start": {"dateTime": start_dt.isoformat(), "timeZone": "America/Bogota"},
            "end": {"dateTime": end_dt.isoformat(), "timeZone": "America/Bogota"},
            "reminders": {
                "useDefault": False,
                "overrides": [
                    {"method": "popup", "minutes": 60},
                    {"method": "popup", "minutes": 1440},
                ],
            },
        }

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                r = await client.post(
                    f"{self.GCAL_BASE}/calendars/{self._calendar_id}/events",
                    headers={"Authorization": f"Bearer {self._access_token}", "Content-Type": "application/json"},
                    json=event,
                )
                if r.status_code in (200, 201):
                    created = r.json()
                    event_id = created.get("id")
                    log.info(f"[calendar] Google Calendar event created successfully: {event_id}")
                    return event_id
                else:
                    log.error(f"[calendar] Google Calendar event creation failed: {r.status_code} {r.text[:200]}")
                    return None
        except Exception as e:
            log.error(f"[calendar] Error creating Google Calendar event: {e}")
            return None

    async def update_event(self, event_id: str, **kwargs) -> bool:
        """Actualiza un evento existente en Google Calendar."""
        if not await self._ensure_token():
            log.warning("[calendar] No valid Google Calendar token for updating event")
            return False

        try:
            url = f"{self.GCAL_BASE}/calendars/{self._calendar_id}/events/{event_id}"
            headers = {
                "Authorization": f"Bearer {self._access_token}",
                "Content-Type": "application/json"
            }
            async with httpx.AsyncClient(timeout=15.0) as client:
                r = await client.patch(url, headers=headers, json=kwargs)
                if r.status_code == 200:
                    log.info(f"[calendar] Google Calendar event updated: {event_id}")
                    return True
                else:
                    log.warning(f"[calendar] Failed to update Google Calendar event: {r.status_code} - {r.text}")
                    return False
        except Exception as e:
            log.error(f"[calendar] Exception updating Google Calendar event: {e}")
            return False


# Instancia global
calendar_bridge: CalendarBridge = None

def init_calendar():
    import src.core.globals as g
    global calendar_bridge
    calendar_bridge = CalendarBridge()
    g.calendar_bridge = calendar_bridge
    if calendar_bridge.has_google_calendar():
        log.info("[calendar] Google Calendar configurado")
    elif calendar_bridge.has_calendly():
        log.info("[calendar] Calendly configurado")
    else:
        log.info("[calendar] sin calendario vinculado — modo autonomo activo")


# ═══════════════════════════════════════════════════════════════════════════════
# PASARELA DE PAGOS (STRIPE / BOLD)
# ═══════════════════════════════════════════════════════════════════════════════

