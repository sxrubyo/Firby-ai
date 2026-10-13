#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Firby WhatsApp Identity & Capabilities Automated Evaluator
=========================================================
Audits external prospect conversations and admin owner interactions on WhatsApp.
Checks:
1. Zero emojis
2. Zero markdown bold (**...**)
3. Zero medical/dental hallucinations ("en consulta con un paciente", "doctora", etc.)
4. Zero "socia" to external prospects (only for Santi)
5. Comprehensive Firby AI capabilities:
   - 24/7 autonomous operator on website
   - 100% customizable widget (icon, name, 20+ designs, 1 script installation)
   - Total owner governance (prompt, roles, Google Calendar, full APIs)
   - Screen action (scrolling and navigating across the website)
   - Official sign-up link (https://firbyai.lat/sign-up) with 7-day free trial (cancel in 1 click)
   - Official pricing ($290.000 Starter, $490.000 Pro, $890.000 Equipos)
6. Voice synthesis quality (no Bubli, no stutter, no ehh fillers)
7. Owner recognition for Santiago (3124348669)
"""

import os
import sys
import asyncio
import re

# Configure environment
os.environ["FIRBY_V7_ENABLED"] = "true"
os.environ["INSTANCE_ID"] = "production"
os.environ["DB_PATH"] = "/home/ubuntu/firby/instances/production/bublee.db"
sys.path.insert(0, "/home/ubuntu/firby/instances/production")
sys.path.insert(0, "/home/ubuntu/firby")

import src.core.globals as g
g.init_database()
g.init_llm()
db = g.db
llm_engine = g.llm_engine

from v7.orchestrator import FirbyOrchestrator
from firby_voice import inject_human_disfluencies, should_send_voice
from firby import FirbyUltra

EMOJI_PATTERN = re.compile(
    "[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF"
    "\U00002500-\U00002BEF\U00002702-\U000027B0\U0001F900-\U0001F9FF\U0001FA00-\U0001FAFF"
    "\u2600-\u26FF\u2700-\u27BF]+"
)

async def evaluate_suite():
    print("=" * 80)
    print("FIRBY WHATSAPP SUITE EVALUATION — EXTERNAL PROSPECTS & OWNER AUDIT")
    print("=" * 80)

    orch = FirbyOrchestrator(llm_engine, db)
    clinic = db.get_clinic()
    
    external_test_cases = [
        {
            "id": "1. Identidad y Qué es Firby",
            "query": "Hola! Qué es Firby y qué hace?",
            "must_include": ["operador", "web"],
            "must_not_include": ["socia", "consulta con un paciente", "doctora", "clínica", "1.000"],
        },
        {
            "id": "2. Widget y Personalización",
            "query": "Cómo se instala el widget en mi página web y se puede cambiar el diseño?",
            "must_include": ["código", "script", "personaliz"],
            "must_not_include": ["socia", "consulta", "1.000"],
        },
        {
            "id": "3. Control Total del Dueño",
            "query": "Qué control tengo yo como dueño del negocio sobre el agente?",
            "must_include": ["prompt", "control"],
            "must_not_include": ["socia", "consulta", "1.000"],
        },
        {
            "id": "4. Acción Real en Pantalla",
            "query": "De verdad se mueve por la web o es solo un chatbot de texto?",
            "must_include": ["mueve", "scroll", "pantalla", "sección"],
            "must_not_include": ["socia", "consulta", "1.000"],
        },
        {
            "id": "5. Precios y Enlace de Registro",
            "query": "Cuánto cuesta el servicio y dónde puedo crear mi cuenta para probarlo?",
            "must_include": ["290.000", "490.000", "890.000", "https://firbyai.lat/sign-up", "7 días"],
            "must_not_include": ["1.000", "socia", "consulta"],
        },
        {
            "id": "6. Manejo de Objeción de Alucinación",
            "query": "Me da miedo que invente información o alucine con mis clientes.",
            "must_include": ["control", "política", "autoriz"],
            "must_not_include": ["socia", "consulta", "1.000"],
        },
        {
            "id": "7. Solicitud de Demostración",
            "query": "Quiero agendar una demo técnica en vivo o probar el sistema.",
            "must_include": ["https://firbyai.lat", "demo"],
            "must_not_include": ["socia", "consulta con un paciente", "1.000"],
        },
    ]

    total_tests = len(external_test_cases) + 2  # + voice test + admin test
    passed_tests = 0
    external_chat_id = "573001234567@s.whatsapp.net"

    print("\n--- AUDITANDO ESCENARIOS DE PROSPECTO EXTERNO ---")
    for tc in external_test_cases:
        t_id = tc["id"]
        q = tc["query"]
        print(f"\n[TEST: {t_id}]")
        print(f"Pregunta: \"{q}\"")

        bubbles = await orch.process(
            chat_id=external_chat_id,
            text=q,
            clinic=clinic,
            patient={},
            history=[]
        )
        
        full_text = " ".join(bubbles)
        print(f"Burbujas devueltas ({len(bubbles)}):")
        for i, b in enumerate(bubbles, 1):
            print(f"  [{i}] {b}")

        # Verification rules
        checks_passed = True
        failures = []

        # 1. Zero emojis
        if EMOJI_PATTERN.search(full_text):
            checks_passed = False
            failures.append("Contiene emojis prohibidos")

        # 2. Zero bold markdown
        if "**" in full_text:
            checks_passed = False
            failures.append("Contiene asteriscos bold (**)")

        # 3. Must not include forbidden terms
        for term in tc["must_not_include"]:
            if term.lower() in full_text.lower():
                checks_passed = False
                failures.append(f"Contiene término prohibido: '{term}'")

        # 4. Must include expected terms (at least some)
        matches = [term for term in tc["must_include"] if term.lower() in full_text.lower()]
        if not matches:
            checks_passed = False
            failures.append(f"No incluyó ninguno de los términos requeridos: {tc['must_include']}")

        # 5. Bubble count between 1 and 3
        if not (1 <= len(bubbles) <= 3):
            checks_passed = False
            failures.append(f"Número de burbujas fuera de rango: {len(bubbles)}")

        if checks_passed:
            print(f"VEREDICTO: PASÓ (Términos validados: {matches})")
            passed_tests += 1
        else:
            print(f"VEREDICTO: FALLÓ -> {failures}")

    # TEST 8: Voice Engine Check
    print("\n[TEST: 8. Síntesis y Fonética de Voz]")
    raw_sample = "Hola! Firby cuenta con un widget 100% personalizable en más de 20 diseños para tu sitio web."
    refined_sample = inject_human_disfluencies(raw_sample, user_text="hola qué es firby")
    print(f"Texto procesado para ElevenLabs: \"{refined_sample}\"")
    
    voice_ok = True
    v_failures = []
    if "Bubli" in refined_sample:
        voice_ok = False
        v_failures.append("Contiene 'Bubli' en lugar de 'Firby'")
    if "ehh" in refined_sample.lower():
        voice_ok = False
        v_failures.append("Contiene muletilla 'ehh'")
    if "hola... hola" in refined_sample.lower() or "te cuento, hola" in refined_sample.lower():
        voice_ok = False
        v_failures.append("Doble saludo o tartamudeo detectado")

    if voice_ok:
        print("VEREDICTO: PASÓ (Voz limpia, natural y sin tartamudeo)")
        passed_tests += 1
    else:
        print(f"VEREDICTO: FALLÓ -> {v_failures}")

    # TEST 9: Admin Recognition (Santi)
    print("\n[TEST: 9. Reconocimiento de Modo Dueño para Santiago (3124348669)]")
    ultra = FirbyUltra()
    await ultra.initialize()
    santi_chat_id = "573124348669@s.whatsapp.net"
    santi_bubbles = await ultra.process_message(santi_chat_id, "Hola Firby, cómo vamos con el lanzamiento?")
    santi_text = " ".join(santi_bubbles)
    print(f"Respuesta a Santi ({len(santi_bubbles)} burbujas):")
    for i, b in enumerate(santi_bubbles, 1):
        print(f"  [{i}] {b}")

    admin_ok = True
    if "Santi" not in santi_text and "Santiago" not in santi_text:
        admin_ok = False
        print("Fallo: No reconoció a Santi por su nombre")

    if admin_ok:
        print("VEREDICTO: PASÓ (Reconoció a Santi como dueño)")
        passed_tests += 1
    else:
        print("VEREDICTO: FALLÓ")

    print("\n" + "=" * 80)
    print(f"RESULTADO FINAL: {passed_tests}/{total_tests} PRUEBAS APROBADAS ({passed_tests/total_tests*100:.0f}%)")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(evaluate_suite())
