# -*- coding: utf-8 -*-
"""
Firby SaaS Membership & Subscription Engine
Manages tenant subscription tiers, billing cycles, automated renewal alerts,
and graceful service throttling upon membership expiration.
"""
from __future__ import annotations

import json
import logging
from enum import Enum
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

log = logging.getLogger("firby.membership")


class MembershipTier(str, Enum):
    STARTER = "starter"         # WhatsApp 24/7 + Calendario + Recordatorios
    PRO = "pro"                 # Starter + Closer de Ventas + Llamadas Telefónicas (Vapi)
    ENTERPRISE = "enterprise"   # 5 Empleados Digitales + n8n Workflows + Campañas Growth


class MembershipStatus(str, Enum):
    TRIAL = "trial"             # 7 días de prueba gratis
    ACTIVE = "active"           # Membresía al día
    PAST_DUE = "past_due"       # Período de gracia (3 días)
    SUSPENDED = "suspended"     # Pausado por falta de pago
    CANCELLED = "cancelled"


MEMBERSHIP_PLANS = {
    MembershipTier.STARTER: {
        "name": "Plan Starter (Recepcionista Digital)",
        "price_cop": 299000,
        "price_usd": 75,
        "features": [
            "Atención WhatsApp 24/7",
            "Agendamiento Google Calendar",
            "Recordatorios 24h y 2h antes",
            "Seguimiento post-cita 24h",
            "Panel de control básico"
        ]
    },
    MembershipTier.PRO: {
        "name": "Plan Pro (Recepción + Ventas + Llamadas de Voz)",
        "price_cop": 690000,
        "price_usd": 175,
        "features": [
            "Todo lo del Plan Starter",
            "Recepcionista Telefónica con Voz Humana (Vapi + ElevenLabs)",
            "Línea Telefónica Local Dedicada",
            "Closer de Ventas y Links de Pago (Wompi/PSE/Stripe)",
            "Manejo de Objeciones y Recuperación de Leads",
            "Continuidad Omnicanal Teléfono ➔ WhatsApp"
        ]
    },
    MembershipTier.ENTERPRISE: {
        "name": "Plan Enterprise (Sistema Operativo Total)",
        "price_cop": 1490000,
        "price_usd": 375,
        "features": [
            "Los 5 Empleados Digitales Autónomos",
            "Creador de Automatizaciones por Chat (n8n)",
            "Campañas Proactivas de Growth & Reactivación",
            "Triaje Médico & Código Rojo con Alertas de Urgencia",
            "Métricas Avanzadas y Soporte VIP Prioritario"
        ]
    }
}


class MembershipManager:
    """Gestiona el estado de membresía y facturación de una instancia/clínica."""

    def __init__(self, db):
        self.db = db
        self._ensure_membership_table()

    def _ensure_membership_table(self):
        """Crea la tabla de membresías si no existe."""
        try:
            with self.db._conn() as c:
                c.execute("""
                    CREATE TABLE IF NOT EXISTS tenant_memberships (
                        tenant_id TEXT PRIMARY KEY,
                        tier TEXT DEFAULT 'trial',
                        status TEXT DEFAULT 'trial',
                        started_at TEXT,
                        expires_at TEXT,
                        monthly_price REAL DEFAULT 0,
                        currency TEXT DEFAULT 'COP',
                        billing_email TEXT DEFAULT '',
                        billing_phone TEXT DEFAULT '',
                        auto_renew INTEGER DEFAULT 1,
                        updated_at TEXT DEFAULT (datetime('now'))
                    )
                """)
        except Exception as e:
            log.warning(f"[Membership] Error creando tabla: {e}")

    def get_membership(self, tenant_id: str = "default") -> Dict[str, Any]:
        """Obtiene el estado actual de la membresía del cliente."""
        try:
            with self.db._conn() as c:
                row = c.execute(
                    "SELECT * FROM tenant_memberships WHERE tenant_id = ?", (tenant_id,)
                ).fetchone()
                if row:
                    return dict(row)
        except Exception:
            pass

        # Membresía por defecto (Trial de 7 días)
        default_trial = {
            "tenant_id": tenant_id,
            "tier": MembershipTier.PRO.value,
            "status": MembershipStatus.TRIAL.value,
            "started_at": datetime.utcnow().isoformat(),
            "expires_at": (datetime.utcnow() + timedelta(days=7)).isoformat(),
            "monthly_price": 690000,
            "currency": "COP"
        }
        self.save_membership(default_trial)
        return default_trial

    def save_membership(self, data: Dict[str, Any]):
        """Guarda o actualiza la membresía."""
        try:
            with self.db._conn() as c:
                c.execute("""
                    INSERT INTO tenant_memberships (
                        tenant_id, tier, status, started_at, expires_at,
                        monthly_price, currency, billing_email, billing_phone,
                        auto_renew, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
                    ON CONFLICT(tenant_id) DO UPDATE SET
                        tier=excluded.tier,
                        status=excluded.status,
                        expires_at=excluded.expires_at,
                        monthly_price=excluded.monthly_price,
                        updated_at=datetime('now')
                """, (
                    data.get("tenant_id", "default"),
                    data.get("tier", "pro"),
                    data.get("status", "active"),
                    data.get("started_at", datetime.utcnow().isoformat()),
                    data.get("expires_at", (datetime.utcnow() + timedelta(days=30)).isoformat()),
                    data.get("monthly_price", 690000),
                    data.get("currency", "COP"),
                    data.get("billing_email", ""),
                    data.get("billing_phone", ""),
                    data.get("auto_renew", 1)
                ))
        except Exception as e:
            log.error(f"[Membership] Error guardando membresía: {e}")

    def is_service_allowed(self, feature_name: str, tenant_id: str = "default") -> Tuple[bool, str]:
        """
        Verifica si la membresía actual del cliente le permite usar una función específica.
        Devuelve (permitido, mensaje_explicativo).
        """
        mem = self.get_membership(tenant_id)
        status = mem.get("status", MembershipStatus.TRIAL.value)
        tier = mem.get("tier", MembershipTier.STARTER.value)
        expires_str = mem.get("expires_at", "")

        # Verificar si expiró
        if expires_str:
            try:
                exp_dt = datetime.fromisoformat(expires_str)
                if datetime.utcnow() > exp_dt:
                    if status not in (MembershipStatus.SUSPENDED.value, MembershipStatus.PAST_DUE.value):
                        self.save_membership({**mem, "status": MembershipStatus.PAST_DUE.value})
                    return False, "Tu membresía de Firby ha vencido. Por favor renueva tu suscripción para continuar disfrutando del servicio."
            except Exception:
                pass

        if status == MembershipStatus.SUSPENDED.value:
            return False, "El servicio se encuentra temporalmente pausado por vencimiento de membresía."

        # Validaciones por tier
        if feature_name == "voice_calls" and tier == MembershipTier.STARTER.value:
            return False, "Las llamadas telefónicas con voz humana están disponibles en el Plan Pro y Enterprise."

        if feature_name == "automations" and tier not in (MembershipTier.ENTERPRISE.value,):
            return False, "La creación autónoma de automatizaciones está disponible en el Plan Enterprise."

        if feature_name == "growth_campaigns" and tier not in (MembershipTier.ENTERPRISE.value,):
            return False, "Las campañas de reactivación están disponibles en el Plan Enterprise."

        return True, "OK"

    def renew_subscription(self, tenant_id: str = "default", months: int = 1, payment_ref: str = "") -> Dict[str, Any]:
        """Extiende la membresía por X meses y la marca como activa."""
        mem = self.get_membership(tenant_id)
        current_exp_str = mem.get("expires_at")
        try:
            current_exp = datetime.fromisoformat(current_exp_str)
            base_dt = max(current_exp, datetime.utcnow())
        except Exception:
            base_dt = datetime.utcnow()

        new_expires = base_dt + timedelta(days=30 * months)
        mem["status"] = MembershipStatus.ACTIVE.value
        mem["expires_at"] = new_expires.isoformat()
        self.save_membership(mem)
        log.info(f"[Membership] 🌟 Suscripción de {tenant_id} renovada hasta {new_expires.isoformat()}")
        return mem

    async def check_daily_renewals_and_notify(self, bridge_url: str = "http://127.0.0.1:8002"):
        """
        Escanea la base de datos diariamente y envía recordatorios al dueño si la membresía vence pronto.
        """
        now = datetime.utcnow()
        try:
            with self.db._conn() as c:
                rows = c.execute("SELECT * FROM tenant_memberships WHERE status IN ('active', 'trial')").fetchall()
                for r in rows:
                    mem = dict(r)
                    exp_str = mem.get("expires_at")
                    if not exp_str:
                        continue
                    try:
                        exp_dt = datetime.fromisoformat(exp_str)
                        days_left = (exp_dt - now).days

                        # Notificar 3 días antes del vencimiento
                        if days_left == 3:
                            billing_phone = mem.get("billing_phone")
                            if billing_phone:
                                import httpx
                                tier_name = mem.get("tier", "pro").upper()
                                checkout_url = f"https://firbyai.lat/pay/sub_{mem.get('tenant_id')}?monto={mem.get('monthly_price')}"
                                alert_msg = (
                                    f"Hola! Le recordamos que su membresía {tier_name} de Firby vence en 3 días ({exp_str[:10]}) ||| "
                                    f"Para mantener a su equipo de empleados digitales activo 24/7 sin interrupciones, puede renovar aquí: {checkout_url}"
                                )
                                async with httpx.AsyncClient(timeout=10.0) as client:
                                    for b in alert_msg.split("|||"):
                                        await client.post(f"{bridge_url}/send", json={"to": billing_phone, "text": b.strip()})
                    except Exception as _e:
                        log.warning(f"[Membership] Error evaluando vencimiento: {_e}")
        except Exception as e:
            log.warning(f"[Membership] Error en cron de membresías: {e}")
