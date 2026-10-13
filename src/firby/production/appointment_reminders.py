# -*- coding: utf-8 -*-
"""
Firby Appointment Reminder Engine
Automated WhatsApp reminders for upcoming appointments.

Runs as a background cron job every 15 minutes and sends:
  - 24h before: Reminder with date, doctor, and preparation instructions
  - 2h before:  Final reminder with clinic location (Google Maps)
  - 24h after:  Post-visit follow-up asking for feedback and next appointment
"""
from __future__ import annotations

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import httpx

log = logging.getLogger("firby.appointment_reminders")


class AppointmentReminderEngine:
    """Scans upcoming appointments and dispatches WhatsApp reminders automatically."""

    def __init__(self, db, bridge_url: str = "http://127.0.0.1:8002"):
        self.db = db
        self.bridge_url = bridge_url
        self._clinic_name = ""
        self._assistant_name = ""
        self._clinic_address = ""
        self._clinic_maps_url = ""
        self._load_clinic_info()

    def _load_clinic_info(self):
        """Load clinic metadata for personalized messages."""
        try:
            clinic = self.db.get_clinic()
            self._clinic_name = clinic.get("name") or "la clínica"
            self._assistant_name = clinic.get("assistant_name") or "Firby"
            self._clinic_address = clinic.get("address") or ""
            self._clinic_maps_url = clinic.get("maps_url") or ""
        except Exception:
            self._clinic_name = "la clínica"
            self._assistant_name = "Firby"

    async def scan_and_send_reminders(self):
        """
        Main entry point — called by APScheduler every 15 minutes.
        Scans appointments and sends reminders at the right moment.
        """
        now = datetime.utcnow()
        log.info(f"[Reminders] Scanning appointments at {now.isoformat()}")

        sent_count = 0
        sent_count += await self._send_24h_reminders(now)
        sent_count += await self._send_2h_reminders(now)
        sent_count += await self._send_post_visit_followups(now)

        if sent_count > 0:
            log.info(f"[Reminders] ✅ Sent {sent_count} reminders this cycle")

    # ── 24 Hours Before ──────────────────────────────────────────────────────

    async def _send_24h_reminders(self, now: datetime) -> int:
        """Send reminder 24 hours before the appointment."""
        window_start = now + timedelta(hours=23, minutes=30)
        window_end = now + timedelta(hours=24, minutes=30)

        appointments = self._get_appointments_in_window(
            window_start, window_end, reminder_level=0
        )
        count = 0
        for apt in appointments:
            patient_name = apt.get("patient_name") or "paciente"
            first_name = patient_name.split()[0] if patient_name else "paciente"
            service = apt.get("service") or "tu consulta"
            dt_slot = apt.get("datetime_slot", "")

            try:
                apt_dt = datetime.fromisoformat(dt_slot)
                time_str = apt_dt.strftime("%-I:%M %p").lower().replace("am", "de la mañana").replace("pm", "de la tarde")
                date_str = self._friendly_date(apt_dt)
            except Exception:
                time_str = dt_slot
                date_str = "pronto"

            msg = (
                f"Hola {first_name}! Te recuerdo que {date_str} tienes tu cita "
                f"de {service} a las {time_str} en {self._clinic_name} ||| "
                f"Recuerda llegar 15 minutos antes con tu documento de identidad. "
                f"Si necesitas reagendar o cancelar, me avisas por aquí y te ayudo"
            )

            await self._send_whatsapp(apt["chat_id"], msg)
            self._mark_reminder_sent(apt["id"], level=1)
            count += 1

        return count

    # ── 2 Hours Before ───────────────────────────────────────────────────────

    async def _send_2h_reminders(self, now: datetime) -> int:
        """Send final reminder 2 hours before with location."""
        window_start = now + timedelta(hours=1, minutes=45)
        window_end = now + timedelta(hours=2, minutes=15)

        appointments = self._get_appointments_in_window(
            window_start, window_end, reminder_level=1
        )
        count = 0
        for apt in appointments:
            patient_name = apt.get("patient_name") or ""
            first_name = patient_name.split()[0] if patient_name else ""

            location_msg = ""
            if self._clinic_maps_url:
                location_msg = f" ||| Aqui te dejo la ubicacion: {self._clinic_maps_url}"
            elif self._clinic_address:
                location_msg = f" ||| Estamos en: {self._clinic_address}"

            msg = (
                f"{'Hola ' + first_name + '! ' if first_name else ''}"
                f"Tu cita es en 2 horas, te esperamos!{location_msg}"
            )

            await self._send_whatsapp(apt["chat_id"], msg)
            self._mark_reminder_sent(apt["id"], level=2)
            count += 1

        return count

    # ── Post-Visit Follow-up (24h after) ─────────────────────────────────────

    async def _send_post_visit_followups(self, now: datetime) -> int:
        """Send follow-up message 24 hours after the appointment."""
        window_start = now - timedelta(hours=24, minutes=30)
        window_end = now - timedelta(hours=23, minutes=30)

        appointments = self._get_appointments_in_window(
            window_start, window_end, reminder_level=2, status="completada"
        )
        count = 0
        for apt in appointments:
            patient_name = apt.get("patient_name") or ""
            first_name = patient_name.split()[0] if patient_name else ""
            service = apt.get("service") or "tu consulta"

            msg = (
                f"{'Hola ' + first_name + '! ' if first_name else 'Hola! '}"
                f"Como te fue ayer en {service}? Esperamos que todo haya salido bien ||| "
                f"Si necesitas agendar un control o tienes alguna duda sobre las indicaciones "
                f"del doctor, me escribes por aqui y con gusto te ayudo"
            )

            await self._send_whatsapp(apt["chat_id"], msg)
            self._mark_reminder_sent(apt["id"], level=3)
            count += 1

        return count

    # ── Database Helpers ─────────────────────────────────────────────────────

    def _get_appointments_in_window(
        self, window_start: datetime, window_end: datetime,
        reminder_level: int = 0, status: str = "confirmada"
    ) -> List[Dict]:
        """Get appointments within a time window that haven't been reminded at this level."""
        try:
            with self.db._conn() as c:
                rows = c.execute("""
                    SELECT id, chat_id, patient_name, patient_phone, service,
                           datetime_slot, duration_minutes, notes, status, reminder_sent
                    FROM appointments
                    WHERE datetime_slot BETWEEN ? AND ?
                      AND (status = ? OR status = 'pendiente')
                      AND reminder_sent < ?
                """, (
                    window_start.isoformat(),
                    window_end.isoformat(),
                    status,
                    reminder_level + 1
                )).fetchall()
                return [dict(r) for r in rows]
        except Exception as e:
            log.warning(f"[Reminders] DB query error: {e}")
            return []

    def _mark_reminder_sent(self, apt_id: int, level: int):
        """Update the reminder_sent level for an appointment."""
        try:
            with self.db._conn() as c:
                c.execute(
                    "UPDATE appointments SET reminder_sent = ?, updated_at = datetime('now') WHERE id = ?",
                    (level, apt_id)
                )
        except Exception as e:
            log.warning(f"[Reminders] Failed to mark reminder for apt {apt_id}: {e}")

    # ── WhatsApp Sender ──────────────────────────────────────────────────────

    async def _send_whatsapp(self, chat_id: str, message: str):
        """Send a multi-bubble WhatsApp message with human-like typing delays."""
        try:
            bubbles = [b.strip() for b in message.split("|||") if b.strip()]
            async with httpx.AsyncClient(timeout=10.0) as client:
                for bubble in bubbles:
                    # Typing indicator
                    try:
                        await client.post(
                            f"{self.bridge_url}/typing",
                            json={"to": chat_id, "duration": 2500}
                        )
                    except Exception:
                        pass
                    await asyncio.sleep(2.0)

                    # Send message
                    resp = await client.post(
                        f"{self.bridge_url}/send",
                        json={"to": chat_id, "text": bubble}
                    )
                    if resp.status_code == 200:
                        log.info(f"[Reminders] ✅ Sent to {chat_id}: {bubble[:60]}...")
                    else:
                        log.warning(f"[Reminders] Send failed ({resp.status_code}): {bubble[:60]}")

                    await asyncio.sleep(1.5)
        except Exception as e:
            log.error(f"[Reminders] WhatsApp send error for {chat_id}: {e}")

    # ── Date Formatting ──────────────────────────────────────────────────────

    @staticmethod
    def _friendly_date(dt: datetime) -> str:
        """Convert datetime to friendly Spanish like 'mañana' or 'el martes'."""
        now = datetime.utcnow()
        diff = (dt.date() - now.date()).days

        if diff == 0:
            return "hoy"
        elif diff == 1:
            return "mañana"
        else:
            dias = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]
            return f"el {dias[dt.weekday()]}"
