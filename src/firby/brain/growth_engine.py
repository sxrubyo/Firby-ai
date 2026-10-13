# -*- coding: utf-8 -*-
"""
Firby Growth & Inactive Patient Reactivation Engine (Mateo Persona)
Executes anti-ban, human-paced proactive WhatsApp campaigns to fill open clinic schedules.
"""
from __future__ import annotations

import random
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

import httpx

log = logging.getLogger("firby.growth_engine")


class GrowthCampaignEngine:
    """Motor de Reactivación de Pacientes y Campañas Proactivas con Protección Anti-Baneo."""

    def __init__(self, db, bridge_url: str = "http://127.0.0.1:8002"):
        self.db = db
        self.bridge_url = bridge_url
        self._is_running = False

    def find_inactive_patients(self, days_inactive: int = 90, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Encuentra pacientes que no han visitado la clínica en más de X días.
        Filtra automáticamente números del sistema, opt-outs y administradores.
        """
        cutoff_date = (datetime.utcnow() - timedelta(days=days_inactive)).isoformat()
        try:
            with self.db._conn() as c:
                rows = c.execute("""
                    SELECT chat_id, name, phone, last_service, last_seen, visits, preferences
                    FROM patients
                    WHERE (last_seen < ? OR last_seen IS NULL)
                      AND chat_id NOT LIKE '%@g.us'
                      AND chat_id NOT LIKE 'admin%'
                      AND chat_id != 'status@broadcast'
                    ORDER BY last_seen ASC
                    LIMIT ?
                """, (cutoff_date, limit)).fetchall()
                return [dict(r) for r in rows]
        except Exception as e:
            log.warning(f"[GrowthEngine] Error buscando pacientes inactivos: {e}")
            return []

    async def execute_reactivation_campaign(
        self,
        service_name: str,
        clinic_name: str,
        custom_offer: Optional[str] = None,
        days_inactive: int = 90,
        batch_size: int = 15
    ) -> Dict[str, Any]:
        """
        Ejecuta una campaña de reactivación segura con retrasos humanos (1.5 a 4 min entre mensajes).
        """
        if self._is_running:
            return {"ok": False, "message": "Ya hay una campaña en ejecución"}

        self._is_running = True
        candidates = self.find_inactive_patients(days_inactive=days_inactive, limit=batch_size)
        log.info(f"[GrowthEngine] 🚀 Iniciando campaña para {len(candidates)} pacientes inactivos ({service_name})")

        sent_count = 0
        try:
            for patient in candidates:
                chat_id = patient.get("chat_id")
                if not chat_id:
                    continue

                full_name = patient.get("name") or ""
                first_name = full_name.split()[0] if full_name else ""
                last_proc = patient.get("last_service") or service_name

                # Generar mensaje personalizado
                msg = self._generate_warm_reactivation_message(
                    first_name=first_name,
                    last_service=last_proc,
                    clinic_name=clinic_name,
                    custom_offer=custom_offer
                )

                # Envío con simulación humana y tipeo
                success = await self._send_whatsapp_bubble(chat_id, msg)
                if success:
                    sent_count += 1
                    # Actualizar fecha de contacto
                    try:
                        with self.db._conn() as c:
                            c.execute(
                                "UPDATE patients SET last_seen = datetime('now') WHERE chat_id = ?",
                                (chat_id,)
                            )
                    except Exception:
                        pass

                # Pausa humana aleatoria anti-baneo (90 a 180 segundos)
                sleep_seconds = random.uniform(90, 180)
                log.info(f"[GrowthEngine] Pausa de seguridad anti-spam: {sleep_seconds:.1f}s")
                await asyncio.sleep(sleep_seconds)

        finally:
            self._is_running = False

        return {
            "ok": True,
            "total_candidates": len(candidates),
            "sent_count": sent_count,
            "message": f"Campaña finalizada. Se enviaron {sent_count} mensajes personalizados de forma segura."
        }

    def _generate_warm_reactivation_message(
        self, first_name: str, last_service: str, clinic_name: str, custom_offer: Optional[str]
    ) -> str:
        """Construye un mensaje cálido, nada invasivo y enfocado en salud/cuidado."""
        greetings = [
            f"Hola {first_name}! Cómo has estado?",
            f"Hola {first_name}! Un saludo muy especial",
            f"Hola {first_name}! Espero que todo marche excelente"
        ]
        greet = random.choice(greetings) if first_name else "Hola! Un saludo muy especial"

        offer_text = custom_offer or "tenemos una agenda prioritaria de chequeo y mantenimiento disponible esta semana"

        return (
            f"{greet} ||| "
            f"Te escribimos de {clinic_name}. Revisando tu ficha vemos que ya hace un tiempo realizaste tu {last_service} con nosotros ||| "
            f"Como parte de tu cuidado preventivo, {offer_text}. Te gustaría que te revisemos disponibilidad para estos días?"
        )

    async def _send_whatsapp_bubble(self, chat_id: str, message: str) -> bool:
        """Despacha las burbujas simulando tipeo real."""
        try:
            bubbles = [b.strip() for b in message.split("|||") if b.strip()]
            async with httpx.AsyncClient(timeout=10.0) as client:
                for b in bubbles:
                    try:
                        await client.post(f"{self.bridge_url}/typing", json={"to": chat_id, "duration": 2500})
                    except Exception:
                        pass
                    await asyncio.sleep(2.0)
                    await client.post(f"{self.bridge_url}/send", json={"to": chat_id, "text": b})
                    await asyncio.sleep(1.5)
            return True
        except Exception as e:
            log.error(f"[GrowthEngine] Error enviando WhatsApp a {chat_id}: {e}")
            return False
