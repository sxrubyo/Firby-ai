# -*- coding: utf-8 -*-
"""
Firby SaaS Subscription Router
Public endpoints for client signup, subscription checkout, webhook payments, and tier validation.
"""
from __future__ import annotations

import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from pydantic import BaseModel

from fastapi import APIRouter, Request, HTTPException, Depends
from src.core.globals import db, Config
from src.firby.core.membership import MembershipManager, MembershipTier, MembershipStatus, MEMBERSHIP_PLANS

log = logging.getLogger("firby.saas_routes")
saas_router = APIRouter(prefix="/api/saas", tags=["SaaS & Memberships"])


class SubscribeRequest(BaseModel):
    tenant_id: str
    tier: str = "pro"
    clinic_name: str = "Clínica"
    billing_email: str = ""
    billing_phone: str = ""
    currency: str = "COP"


@saas_router.get("/plans")
async def get_plans():
    """Retorna los planes de membresía disponibles con sus características y precios."""
    return {
        "ok": True,
        "plans": MEMBERSHIP_PLANS
    }


@saas_router.get("/status")
async def get_membership_status(tenant_id: str = "default"):
    """Consulta el estado de membresía de un cliente."""
    mgr = MembershipManager(db)
    mem = mgr.get_membership(tenant_id)
    tier_info = MEMBERSHIP_PLANS.get(MembershipTier(mem.get("tier", "pro")), {})
    return {
        "ok": True,
        "membership": mem,
        "plan_details": tier_info
    }


@saas_router.post("/checkout")
async def create_membership_checkout(req: SubscribeRequest):
    """Genera un link de pago/suscripción para activar o renovar una membresía."""
    mgr = MembershipManager(db)
    tier_enum = MembershipTier(req.tier.lower()) if req.tier.lower() in MembershipTier._value2member_map_ else MembershipTier.PRO
    plan = MEMBERSHIP_PLANS[tier_enum]
    price = plan["price_cop"] if req.currency == "COP" else plan["price_usd"]

    # Generar link de pago Wompi / Stripe
    checkout_url = f"https://firbyai.com/pay/sub_{req.tenant_id}?tier={tier_enum.value}&monto={price}"

    try:
        from src.firby.integrations.payments import PaymentBridge
        bridge = PaymentBridge()
        bridge._load_config()
        if bridge._provider == "wompi" and bridge._api_key:
            import httpx
            url = "https://production.wompi.co/v1/payment_links"
            headers = {"Authorization": f"Bearer {bridge._api_key}", "Content-Type": "application/json"}
            payload = {
                "name": f"Suscripción Firby: {plan['name']}",
                "description": f"Membresía mensual para {req.clinic_name}",
                "single_use": False,
                "currency": "COP",
                "amount_in_cents": int(price) * 100,
                "redirect_url": f"https://firbyai.com/workspace?subscribed=true"
            }
            async with httpx.AsyncClient() as client:
                res = await client.post(url, headers=headers, json=payload, timeout=10.0)
                if res.status_code in (200, 201):
                    link_id = res.json().get("data", {}).get("id")
                    if link_id:
                        checkout_url = f"https://checkout.wompi.co/l/{link_id}"
    except Exception as e:
        log.warning(f"[saas_routes] Error creando link directo Wompi: {e}")

    return {
        "ok": True,
        "tenant_id": req.tenant_id,
        "tier": tier_enum.value,
        "plan_name": plan["name"],
        "price": price,
        "currency": req.currency,
        "checkout_url": checkout_url
    }


@saas_router.post("/webhook/wompi")
async def handle_wompi_membership_webhook(request: Request):
    """Webhook receptor de Wompi para confirmación automática de pagos de suscripción."""
    try:
        payload = await request.json()
        event = payload.get("event", "")
        data = payload.get("data", {}).get("transaction", {})
        
        status = data.get("status")
        reference = data.get("reference", "")
        
        log.info(f"[saas_webhook] Evento Wompi recibido: {event} | ref: {reference} | status: {status}")

        if status == "APPROVED":
            # Extraer tenant_id si viene como sub_<tenant_id>
            tenant_id = "default"
            if reference.startswith("sub_"):
                tenant_id = reference.replace("sub_", "").split("_")[0]

            mgr = MembershipManager(db)
            mgr.renew_subscription(tenant_id=tenant_id, months=1, payment_ref=reference)
            log.info(f"[saas_webhook] ✅ Membresía de {tenant_id} renovada por 30 días.")

        return {"status": "ok"}
    except Exception as e:
        log.error(f"[saas_webhook] Error procesando webhook de Wompi: {e}")
        return {"status": "error", "message": str(e)}
