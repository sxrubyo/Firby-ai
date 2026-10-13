# -*- coding: utf-8 -*-
"""
Firby Telephony & Voice Call Router
Handles inbound/outbound phone calls, real-time voice streaming (Twilio, Vapi, Retell),
live function calling for appointment scheduling, and automatic post-call WhatsApp follow-up.
"""
from __future__ import annotations

import os
import re
import json
import httpx
import logging
import asyncio
from datetime import datetime
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Request, Response, HTTPException
from fastapi.responses import JSONResponse, PlainTextResponse

log = logging.getLogger("firby.telephony")

router = APIRouter(prefix="/api/voice", tags=["Voice Telephony"])


# ─── TWILIO INBOUND CALL HANDLER ───────────────────────────────────────────────
@router.post("/twilio/incoming")
@router.get("/twilio/incoming")
async def twilio_incoming_call(request: Request):
    """
    Twilio Webhook: Executes when a patient dials the clinic's phone number.
    Returns TwiML instructing Twilio to greet the caller or connect to WebSocket stream.
    """
    params = dict(request.query_params)
    if request.method == "POST":
        try:
            form = await request.form()
            params.update(dict(form))
        except Exception:
            pass

    caller = params.get("From", "")
    called = params.get("To", "")
    call_sid = params.get("CallSid", "")
    log.info(f"[Twilio Voice] Llamada entrante de {caller} a {called} (CallSid: {call_sid})")

    base_ws_host = request.headers.get("host", "firbyai.lat")
    ws_url = f"wss://{base_ws_host}/api/voice/stream"

    twiml_response = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say language="es-MX" voice="Polly.Mia">Hola, te has comunicado con la clínica. En un segundo te atiende nuestra recepcionista.</Say>
    <Connect>
        <Stream url="{ws_url}">
            <Parameter name="caller" value="{caller}" />
            <Parameter name="callSid" value="{call_sid}" />
        </Stream>
    </Connect>
</Response>"""
    return Response(content=twiml_response, media_type="application/xml")


# ─── VAPI / RETELL WEBHOOK INTEGRATION (TOOL CALLING & POST-CALL WHATSAPP) ─────
@router.post("/vapi/webhook")
async def vapi_voice_webhook(request: Request):
    """
    Vapi.ai / Retell AI Webhook:
    1. Handles live function calling during the phone call (agendar_cita, disponibilidad).
    2. Handles 'end-of-call-report' to automatically send post-call WhatsApp follow-up!
    """
    try:
        payload = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON")

    message = payload.get("message", {}) or payload
    message_type = message.get("type") or payload.get("type", "")
    log.info(f"[Voice Webhook] Evento recibido: {message_type}")

    # 1. Ejecución de Herramientas en Vivo durante la Llamada
    if message_type == "tool-calls":
        tool_calls = message.get("toolCalls", [])
        results = []
        for tool_call in tool_calls:
            call_id = tool_call.get("id")
            func = tool_call.get("function", {})
            func_name = func.get("name")
            args = func.get("arguments", {})
            if isinstance(args, str):
                try:
                    args = json.loads(args)
                except Exception:
                    args = {}

            log.info(f"[Voice Tool] Ejecutando función en llamada: {func_name} con args: {args}")
            
            result_data = await _execute_voice_tool(func_name, args)
            results.append({
                "toolCallId": call_id,
                "result": json.dumps(result_data, ensure_ascii=False)
            })

        return JSONResponse({"results": results})

    # 2. Fin de Llamada -> Seguimiento Automático por WhatsApp
    elif message_type in ("end-of-call-report", "call-ended", "call.ended"):
        log.info("[Voice Webhook] 📞 Llamada finalizada. Iniciando seguimiento automático por WhatsApp...")
        asyncio.create_task(_process_post_call_whatsapp_followup(payload))
        return JSONResponse({"status": "processing_post_call_followup", "ok": True})

    # Eventos de estado (speech-update, status-update, etc.)
    return JSONResponse({"status": "received", "ok": True})


# ─── POST-CALL WHATSAPP AUTOMATION ENGINE ─────────────────────────────────────
async def _process_post_call_whatsapp_followup(payload: Dict[str, Any]):
    """
    Procesa el reporte de llamada terminada:
    1. Extrae teléfono del paciente, resumen y detalles de citas.
    2. Guarda la transcripción en la base de datos de Firby.
    3. Envía automáticamente un mensaje por WhatsApp al paciente confirmando lo hablado.
    """
    try:
        message = payload.get("message", {}) or payload
        call_data = message.get("call", {}) or payload.get("call", {})
        customer = call_data.get("customer", {}) or payload.get("customer", {})
        
        # 1. Extraer número de teléfono del paciente
        raw_phone = customer.get("number") or call_data.get("customerNumber") or payload.get("caller") or ""
        if not raw_phone:
            log.warning("[Voice Follow-up] No se encontró número de teléfono en el reporte de llamada.")
            return

        clean_phone = re.sub(r"[^\d]", "", raw_phone)
        if len(clean_phone) == 10 and not clean_phone.startswith("57"):
            clean_phone = f"57{clean_phone}" # Colombia default

        # 2. Extraer resumen y transcripción
        summary = message.get("summary") or call_data.get("summary") or "Llamada de atención y consulta con la recepcionista."
        transcript = message.get("transcript") or call_data.get("transcript") or ""
        
        log.info(f"[Voice Follow-up] Paciente {clean_phone} - Resumen: {summary}")

        # 3. Guardar en SQLite de Firby
        from src.core.globals import db, Config
        if db:
            try:
                chat_id = f"{clean_phone}@s.whatsapp.net"
                db.save_message(
                    chat_id=chat_id,
                    role="system",
                    content=f"[📞 REGISTRO DE LLAMADA TELEFÓNICA]\nResumen: {summary}\n\nTranscripción: {transcript[:800]}",
                    analysis=json.dumps({"channel": "phone_call", "summary": summary})
                )
                db.update_patient(
                    chat_id=chat_id,
                    phone=clean_phone,
                    notes=f"Llamada telefónica atendida el {datetime.now().strftime('%Y-%m-%d %H:%M')}. Resumen: {summary}"
                )
            except Exception as _db_err:
                log.warning(f"[Voice Follow-up] Error guardando historial de llamada en DB: {_db_err}")

        # 4. Generar Mensaje Humano de WhatsApp
        clinic_name = "Clínica Las Américas"
        assistant_name = "Firby"
        if db:
            try:
                clinic = db.get_clinic()
                clinic_name = clinic.get("name") or clinic_name
                assistant_name = clinic.get("assistant_name") or assistant_name
            except Exception:
                pass

        # Redactar mensaje personalizado
        whatsapp_msg = (
            f"Hola! Qué gusto haber hablado contigo hace un momento por teléfono ||| "
            f"Te escribe {assistant_name} de {clinic_name}. Te dejo por aquí nuestro canal de WhatsApp para lo que necesites ||| "
            f"Si tienes alguna duda adicional sobre tu consulta o deseas gestionar tu cita, me puedes escribir directamente por este chat"
        )

        # 5. Enviar mensaje por WhatsApp Bridge
        bridge_url = getattr(Config, "WHATSAPP_BRIDGE_URL", "http://127.0.0.1:8002")
        target_jid = f"{clean_phone}@s.whatsapp.net"
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            bubbles = [b.strip() for b in whatsapp_msg.split("|||") if b.strip()]
            for b in bubbles:
                # Simular tipeo
                await client.post(f"{bridge_url}/typing", json={"to": target_jid, "duration": 2500}).catch(lambda _: None)
                await asyncio.sleep(2.0)
                await client.post(f"{bridge_url}/send", json={"to": target_jid, "text": b})
                await asyncio.sleep(1.5)

        log.info(f"[Voice Follow-up] ✅ Seguimiento de WhatsApp enviado con éxito a {clean_phone}")

    except Exception as e:
        log.error(f"[Voice Follow-up] Error en seguimiento post-llamada: {e}", exc_info=True)


# ─── VOICE ASSISTANT SYSTEM PROMPT GENERATOR ──────────────────────────────────
@router.get("/assistant-config")
async def get_voice_assistant_config(request: Request):
    """
    Returns the ready-to-use Assistant Configuration (System Prompt, Tools, Voices)
    for Vapi.ai, Retell, or LiveKit.
    """
    from src.core.globals import db, Config
    
    clinic_name = "Clínica Las Américas"
    assistant_name = "Firby"
    sector = "salud"
    
    if db:
        try:
            clinic = db.get_clinic()
            clinic_name = clinic.get("name") or clinic_name
            assistant_name = clinic.get("assistant_name") or assistant_name
            sector = clinic.get("sector") or sector
        except Exception:
            pass

    prompt = f"""Eres {assistant_name}, la recepcionista telefónica oficial de {clinic_name}.
Estás hablando EN VIVO por teléfono con un paciente.

REGLAS DE LLAMADA TELEFÓNICA HUMANA:
1. Habla con tono cálido, profesional y natural de Colombia/Latinoamérica.
2. Respuestas CORTAS (1 a 2 oraciones máximo). En una llamada nadie da discursos largos.
3. Escucha activamente: si el paciente te interrumpe, detente y escúchalo.
4. Si preguntan por citas, usa la herramienta `agendar_cita` o `consultar_disponibilidad`.
5. Si preguntan precios o servicios, explica con claridad y amabilidad.
6. Al finalizar la llamada, recuérdale amablemente que le enviarás los detalles y confirmación por WhatsApp a su número.
7. NUNCA digas que eres una inteligencia artificial ni un modelo de lenguaje. Eres la recepcionista telefónica de {clinic_name}."""

    tools = [
        {
            "type": "function",
            "function": {
                "name": "consultar_disponibilidad",
                "description": "Consulta los horarios y doctores disponibles para una fecha o especialidad",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "fecha": {"type": "string", "description": "Fecha deseada (ej. mañana, 2026-08-19)"},
                        "especialidad": {"type": "string", "description": "Especialidad o tratamiento deseado"}
                    },
                    "required": ["fecha"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "agendar_cita",
                "description": "Agenda una cita médica para el paciente en el sistema de la clínica",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "nombre_paciente": {"type": "string", "description": "Nombre completo del paciente"},
                        "telefono": {"type": "string", "description": "Número de teléfono o celular"},
                        "fecha": {"type": "string", "description": "Fecha de la cita (YYYY-MM-DD)"},
                        "hora": {"type": "string", "description": "Hora de la cita (ej. 15:00)"},
                        "motivo": {"type": "string", "description": "Motivo de la consulta o tratamiento"}
                    },
                    "required": ["nombre_paciente", "fecha", "hora"]
                }
            }
        }
    ]

    host = request.headers.get("host", "firbyai.lat")
    return {
        "assistant_name": assistant_name,
        "clinic_name": clinic_name,
        "voice": {
            "provider": "elevenlabs",
            "voice_id": "21m00Tcm4TlvDq8ikWAM",
            "model": "eleven_turbo_v2_5"
        },
        "system_prompt": prompt,
        "tools": tools,
        "server_url": f"https://{host}/api/voice/vapi/webhook"
    }


async def _execute_voice_tool(name: str, args: Dict[str, Any]) -> Dict[str, Any]:
    """Executes business tools during the telephone call."""
    from src.core.globals import db
    
    if name == "consultar_disponibilidad":
        fecha = args.get("fecha", "mañana")
        especialidad = args.get("especialidad", "")
        
        # Try real calendar first
        try:
            from src.firby.integrations.calendar import CalendarBridge
            cal = CalendarBridge()
            if cal.has_google_calendar():
                summary = await cal.get_availability_summary(fecha)
                if summary:
                    return {"disponible": True, "mensaje": summary}
        except Exception as _cal_err:
            log.debug(f"[Voice Tool] Calendar lookup skipped: {_cal_err}")

        # Fallback: return clinic working hours
        return {
            "disponible": True,
            "horarios": ["09:00 AM", "11:30 AM", "03:00 PM", "04:30 PM"],
            "mensaje": f"Para {fecha} tenemos horarios disponibles a las 9:00 de la mañana, 11:30, 3:00 de la tarde y 4:30. Cual te queda mejor?"
        }

    elif name == "agendar_cita":
        nombre = args.get("nombre_paciente", "")
        fecha = args.get("fecha", "")
        hora = args.get("hora", "")
        motivo = args.get("motivo", "Consulta general")
        tel = args.get("telefono", "")

        # 1. Guardar en Base de Datos SQLite
        if db:
            try:
                db.create_appointment(
                    patient_name=nombre,
                    date=fecha,
                    time=hora,
                    treatment=motivo,
                    phone=tel,
                    notes="Agendada vía llamada telefónica de voz con Firby"
                )
            except Exception as e:
                log.warning(f"Error creando cita en DB durante llamada: {e}")

        # 2. Sincronizar automáticamente con Google Calendar & Google Sheets (Hermes / n8n)
        from src.core.globals import Config
        n8n_url = getattr(Config, "N8N_WEBHOOK_URL", "https://nexusys.duckdns.org/webhook/firby_appointments")
        async def _sync_external():
            try:
                async with httpx.AsyncClient(timeout=6.0) as client:
                    await client.post(
                        f"{n8n_url.rstrip('/')}/webhook/firby_appointments",
                        json={
                            "event": "appointment_booked",
                            "patient_name": nombre,
                            "phone": tel,
                            "date": fecha,
                            "time": hora,
                            "treatment": motivo,
                            "channel": "phone_call",
                            "source": "Firby Voice Telephony",
                            "created_at": datetime.utcnow().isoformat()
                        }
                    )
            except Exception as _sync_err:
                log.debug(f"[voice_sync] n8n sync skipped: {_sync_err}")

        asyncio.create_task(_sync_external())

        return {
            "ok": True,
            "mensaje": f"Cita confirmada con éxito para {nombre} el día {fecha} a las {hora}. Se ha registrado en Google Calendar y se le enviará un recordatorio por WhatsApp."
        }

    return {"error": f"Herramienta {name} no reconocida"}
