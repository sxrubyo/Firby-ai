# -*- coding: utf-8 -*-
"""Payment Bridge integration."""
from __future__ import annotations

import logging
import os
import json
import httpx
from src.firby.core.proxy import GlobalProxy

log = logging.getLogger("firby.payments")

db = GlobalProxy("db")


class PaymentBridge:
    def __init__(self):
        self._provider = None
        self._api_key = None
        self._webhook_secret = None
        
    def _load_config(self):
        try:
            clinic = db.get_clinic()
            cfg = clinic.get("payment_config") or {}
            if isinstance(cfg, str):
                cfg = json.loads(cfg)
            self._provider = cfg.get("provider")
            self._api_key = cfg.get("api_key") or os.getenv("STRIPE_SECRET_KEY")
            self._webhook_secret = cfg.get("webhook_secret")
        except Exception:
            pass

    def get_deposit_amount(self, service_name: str) -> int:
        try:
            clinic = db.get_clinic()
            rules = clinic.get("payment_rules") or {}
            if isinstance(rules, str):
                rules = json.loads(rules)
            return rules.get(service_name, 0)
        except Exception:
            return 0

    async def create_payment_link(self, appointment_id: int, service: str, amount: int, chat_id: str) -> str:
        self._load_config()
        if not self._provider:
            self._provider = "mock"
            
        if self._provider == "stripe" and self._api_key:
            try:
                url = "https://api.stripe.com/v1/checkout/sessions"
                headers = {
                    "Authorization": f"Bearer {self._api_key}",
                    "Content-Type": "application/x-www-form-urlencoded"
                }
                
                success_url = f"https://firby.ai/payment/success?apt_id={appointment_id}"
                cancel_url = f"https://firby.ai/payment/cancel?apt_id={appointment_id}"
                amount_cents = int(amount) * 100
                
                data = {
                    "success_url": success_url,
                    "cancel_url": cancel_url,
                    "mode": "payment",
                    "client_reference_id": str(appointment_id),
                    "line_items[0][price_data][currency]": "cop",
                    "line_items[0][price_data][unit_amount]": str(amount_cents),
                    "line_items[0][price_data][product_data][name]": f"Abono Cita: {service}",
                    "line_items[0][quantity]": "1",
                    "metadata[appointment_id]": str(appointment_id),
                    "metadata[chat_id]": chat_id,
                }
                
                async with httpx.AsyncClient() as client:
                    resp = await client.post(url, headers=headers, data=data, timeout=10.0)
                    if resp.status_code in (200, 201):
                        session_data = resp.json()
                        return session_data.get("url") or ""
                    else:
                        log.error(f"[payments] Stripe session creation failed: {resp.status_code} - {resp.text}")
            except Exception as e:
                log.error(f"[payments] Error calling Stripe: {e}")
                
        elif self._provider == "bold" and self._api_key:
            try:
                url = "https://api.bold.co/v2/payment-links"
                headers = {
                    "Authorization": f"Bearer {self._api_key}",
                    "Content-Type": "application/json"
                }
                
                payload = {
                    "title": f"Abono Cita: {service}",
                    "description": f"Reserva de cita de {service}",
                    "currency": "COP",
                    "amount": int(amount),
                    "redirect_url": f"https://firby.ai/payment/success?apt_id={appointment_id}",
                    "reference": f"apt_{appointment_id}",
                    "metadata": {
                        "appointment_id": str(appointment_id),
                        "chat_id": chat_id
                    }
                }
                
                async with httpx.AsyncClient() as client:
                    resp = await client.post(url, headers=headers, json=payload, timeout=10.0)
                    if resp.status_code in (200, 201):
                        res_data = resp.json()
                        return res_data.get("url") or res_data.get("payment_url") or ""
                    else:
                        log.error(f"[payments] Bold link creation failed: {resp.status_code} - {resp.text}")
            except Exception as e:
                log.error(f"[payments] Error calling Bold: {e}")
        elif self._provider == "wompi" and self._api_key:
            try:
                # Wompi Payment Link API (Bancolombia, Nequi, PSE)
                url = "https://production.wompi.co/v1/payment_links"
                headers = {
                    "Authorization": f"Bearer {self._api_key}",
                    "Content-Type": "application/json"
                }
                amount_cents = int(amount) * 100
                payload = {
                    "name": f"Abono Cita: {service}",
                    "description": f"Reserva médica para cita #{appointment_id}",
                    "single_use": True,
                    "collect_shipping": False,
                    "currency": "COP",
                    "amount_in_cents": amount_cents,
                    "redirect_url": f"https://firbyai.com/payment/success?apt_id={appointment_id}"
                }
                async with httpx.AsyncClient() as client:
                    resp = await client.post(url, headers=headers, json=payload, timeout=10.0)
                    if resp.status_code in (200, 201):
                        res_data = resp.json()
                        link_id = res_data.get("data", {}).get("id")
                        if link_id:
                            return f"https://checkout.wompi.co/l/{link_id}"
            except Exception as e:
                log.error(f"[payments] Error calling Wompi: {e}")

        # Link seguro de pago por defecto
        return f"https://firbyai.com/pay/apt_{appointment_id}?monto={amount}&servicio={service.replace(' ', '+')}"
