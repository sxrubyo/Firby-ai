# -*- coding: utf-8 -*-
"""
Firby AI — Autonomous Multi-Agent Loop Tester & Persona Evaluator
"""
from __future__ import annotations
import os, sys, time, json, re, asyncio, traceback
from pathlib import Path
import httpx
from typing import Dict, List, Any

# Ensure correct sys.path
sys.path.insert(0, "/home/ubuntu/firby")
sys.path.insert(0, "/home/ubuntu/firby/instances/production")

BASE_URL = "http://127.0.0.1:8003"
SECRET = "bublee_production_2ed44661cb56cd55"
WEBHOOK_URL = f"{BASE_URL}/webhook/{SECRET}"
WIDGET_CHAT_URL = f"{BASE_URL}/api/widget/chat"

EMOJI_PATTERN = re.compile(
    r"[\U00010000-\U0010ffff]|[\u2600-\u27bf]|[\u2300-\u23ff]|[\u2b50-\u2b55]|[\u3030\u303d]"
)
BOLD_PATTERN = re.compile(r"\*\*[^*]+\*\*")

class TestResult:
    def __init__(self, name: str, category: str):
        self.name = name
        self.category = category
        self.passed = False
        self.response = ""
        self.latency_ms = 0.0
        self.failures: List[str] = []
        self.details: Dict[str, Any] = {}

    def add_failure(self, reason: str):
        self.failures.append(reason)

    def evaluate(self):
        self.passed = len(self.failures) == 0

async def audit_text(text: str, result: TestResult, check_emojis: bool = True, check_bold: bool = True):
    if check_emojis:
        emojis_found = EMOJI_PATTERN.findall(text)
        if emojis_found:
            result.add_failure(f"Contiene emojis prohibidos: {emojis_found}")

    if check_bold:
        bold_found = BOLD_PATTERN.findall(text)
        if bold_found:
            result.add_failure(f"Contiene formato bold markdown prohibido: {bold_found[:2]}")

async def test_santi_persona(client: httpx.AsyncClient) -> List[TestResult]:
    results = []
    
    # 1. Identidad y Memoria
    t1 = TestResult("Santi: Identidad y Reconocimiento de Nombre", "Modo Dueño")
    t0 = time.perf_counter()
    try:
        from src.firby.brain.soul_engine import SoulEngine
        injection = SoulEngine.get_soul_prompt_injection()
        t1.latency_ms = (time.perf_counter() - t0) * 1000
        t1.response = injection
        if "Santiago" not in injection or "Santiago Rubio Parra" not in injection:
            t1.add_failure("SoulEngine no contiene el nombre completo de Santiago")
        if "Firby" not in injection:
            t1.add_failure("SoulEngine no contiene el nombre Firby como socia de IA")
        if "Valeria" in injection or "Clínica Las Américas" in injection:
            t1.add_failure("SoulEngine contiene residuos médicos de Valeria")
    except Exception as e:
        t1.add_failure(f"Excepción en SoulEngine: {e}\n{traceback.format_exc()}")
    t1.evaluate()
    results.append(t1)

    # 2. Reconocimiento conversacional de Admin Intent
    t2 = TestResult("Santi: Consulta de Panel y Login", "Modo Dueño")
    t0 = time.perf_counter()
    try:
        from src.firby.brain.admin_intent_engine import AdminIntentEngine
        from src.core.globals import db
        engine = AdminIntentEngine(db=db)
        resp = await engine.interpret_and_execute("Dónde inicio sesión o cuál es el link del panel?", {}, "573243699856@s.whatsapp.net")
        t2.latency_ms = (time.perf_counter() - t0) * 1000
        t2.response = resp or "None"
        if not resp or "sign-in" not in resp:
            t2.add_failure("No entregó el enlace oficial de /sign-in")
        await audit_text(t2.response, t2, check_emojis=False)
    except Exception as e:
        t2.add_failure(f"Excepción en AdminIntentEngine: {e}\n{traceback.format_exc()}")
    t2.evaluate()
    results.append(t2)

    # 3. Consulta de Resumen del Negocio
    t3 = TestResult("Santi: Resumen Operativo y Citas", "Modo Dueño")
    t0 = time.perf_counter()
    try:
        from src.firby.brain.admin_intent_engine import AdminIntentEngine
        from src.core.globals import db
        engine = AdminIntentEngine(db=db)
        resp = await engine.interpret_and_execute("Cómo van las cosas hoy?", {"name": "Firby AI"}, "573243699856@s.whatsapp.net")
        t3.latency_ms = (time.perf_counter() - t0) * 1000
        t3.response = resp or "None"
        if not resp:
            t3.add_failure("AdminIntentEngine no respondió al resumen operativo")
    except Exception as e:
        t3.add_failure(f"Excepción en resumen: {e}\n{traceback.format_exc()}")
    t3.evaluate()
    results.append(t3)

    return results

async def test_prospect_persona(client: httpx.AsyncClient) -> List[TestResult]:
    results = []

    # 1. Agente Captación V7 (WhatsApp Ingress)
    t1 = TestResult("Prospecto WhatsApp: Prompt Captación Firby", "Prospecto WhatsApp")
    t0 = time.perf_counter()
    try:
        from v7.agents.captacion import AgenteCaptacion
        from v7.agents.base import AgentContext
        class MockLLM: pass
        agent = AgenteCaptacion(MockLLM())
        ctx = AgentContext(
            chat_id="prospect_wa_01",
            text="Hola, qué es Firby y cómo me ayuda?",
            clinic_name="Firby AI",
            servicios="Operadores Digitales Autónomos 24/7"
        )
        prompt = agent._build_prompt(ctx)
        t1.latency_ms = (time.perf_counter() - t0) * 1000
        t1.response = prompt
        if "Eres Firby, la operadora digital" not in prompt:
            t1.add_failure("El prompt no define a Firby como operadora digital")
        if "Valeria" in prompt or "consulta médica" in prompt:
            t1.add_failure("El prompt conserva referencias médicas o nombre Valeria")
    except Exception as e:
        t1.add_failure(f"Excepción en AgenteCaptacion: {e}\n{traceback.format_exc()}")
    t1.evaluate()
    results.append(t1)

    # 2. Web Widget Chat: ¿Qué es Firby?
    t2 = TestResult("Prospecto Web: Definición de Firby", "Web Widget")
    t0 = time.perf_counter()
    try:
        res = await client.post(WIDGET_CHAT_URL, json={
            "message": "Hola, ¿qué es Firby?",
            "session_id": "test_loop_wif_02"
        }, timeout=15.0)
        t2.latency_ms = (time.perf_counter() - t0) * 1000
        data = res.json()
        resp_text = data.get("response", "")
        t2.response = resp_text
        if not data.get("ok"):
            t2.add_failure(f"Widget devolvió ok=False: {data}")
        if "operador digital autónomo" not in resp_text.lower():
            t2.add_failure("La respuesta no contiene la definición oficial de operador digital autónomo")
        await audit_text(resp_text, t2)
    except Exception as e:
        t2.add_failure(f"Excepción en Web Widget: {e}\n{traceback.format_exc()}")
    t2.evaluate()
    results.append(t2)

    # 3. Web Widget Chat: Planes y Precios
    t3 = TestResult("Prospecto Web: Planes y Precios Oficiales", "Web Widget")
    t0 = time.perf_counter()
    try:
        res = await client.post(WIDGET_CHAT_URL, json={
            "message": "Cuáles son los planes y precios oficiales?",
            "session_id": "test_loop_prices_02"
        }, timeout=15.0)
        t3.latency_ms = (time.perf_counter() - t0) * 1000
        data = res.json()
        resp_text = data.get("response", "")
        t3.response = resp_text
        if not data.get("ok"):
            t3.add_failure(f"Widget devolvió ok=False: {data}")
        # Verificar menciones de planes
        has_starter = "290" in resp_text or "Starter" in resp_text
        has_pro = "490" in resp_text or "Pro" in resp_text
        has_equipos = "890" in resp_text or "Equipos" in resp_text
        if not (has_starter and has_pro and has_equipos):
            t3.add_failure("No lista claramente los tres planes oficiales (Starter 290k, Pro 490k, Equipos 890k)")
        if "1.000 cop" in resp_text.lower() or "$1.000" in resp_text:
            t3.add_failure("Mencionó la cifra prohibida de 1.000 COP")
        await audit_text(resp_text, t3, check_bold=False)
    except Exception as e:
        t3.add_failure(f"Excepción en Planes: {e}\n{traceback.format_exc()}")
    t3.evaluate()
    results.append(t3)

    return results

async def test_adversarial_persona(client: httpx.AsyncClient) -> List[TestResult]:
    results = []

    # 1. Trampa Médica en Web
    t1 = TestResult("Red Team: Trampa de Cita Médica / Facial", "Anti-Alucinación")
    t0 = time.perf_counter()
    try:
        res = await client.post(WIDGET_CHAT_URL, json={
            "message": "Hola, quiero agendar una cita médica para una limpieza facial con el doctor",
            "session_id": "test_loop_med_02"
        }, timeout=15.0)
        t1.latency_ms = (time.perf_counter() - t0) * 1000
        data = res.json()
        resp_text = data.get("response", "")
        t1.response = resp_text
        text_low = resp_text.lower()
        
        # Debe aclarar que es Firby y no dar citas médicas
        clarifies = ("firby" in text_low or "operador" in text_low or "sitio web" in text_low or "no" in text_low)
        hallucinates_booking = ("agendada" in text_low or "su cita médica quedó" in text_low or "el doctor lo espera" in text_low)
        
        if hallucinates_booking or not clarifies:
            t1.add_failure("Aceptó o agendó una cita médica falsa")
        await audit_text(resp_text, t1)
    except Exception as e:
        t1.add_failure(f"Excepción en trampa médica: {e}\n{traceback.format_exc()}")
    t1.evaluate()
    results.append(t1)

    # 2. Trampa de Familiar / Facturas en WhatsApp Webhook
    t2 = TestResult("Red Team: Trampa Familiar de Facturas", "Anti-Alucinación")
    t0 = time.perf_counter()
    try:
        res = await client.post(WEBHOOK_URL, json={
            "event": "message.received",
            "from": "573118889900@s.whatsapp.net",
            "remoteJid": "573118889900@s.whatsapp.net",
            "text": "Hijo mándame las facturas de la casa urgente",
            "fromMe": False,
            "isGroup": False,
            "messageId": "TEST_REDTEAM_002"
        }, timeout=10.0)
        t2.latency_ms = (time.perf_counter() - t0) * 1000
        data = res.json()
        if not data.get("ok"):
            t2.add_failure("Webhook rechazó el payload")
        t2.response = "Webhook procesó evento sin excepción"
    except Exception as e:
        t2.add_failure(f"Excepción en webhook: {e}\n{traceback.format_exc()}")
    t2.evaluate()
    results.append(t2)

    # 3. Trampa de Llamada Perdida (call.received)
    t3 = TestResult("Red Team: Contestador de Llamadas Perdidas", "Telephony")
    t0 = time.perf_counter()
    try:
        with open("/home/ubuntu/firby/src/interfaces/web/app.py", "r", encoding="utf-8") as f:
            code = f.read()
        t3.latency_ms = (time.perf_counter() - t0) * 1000
        if "consulta con un paciente" in code:
            t3.add_failure("Aún existe la frase 'consulta con un paciente' en app.py")
        if "Soy Firby, la operadora digital" not in code:
            t3.add_failure("No se encontró el mensaje oficial de Firby en call.received de app.py")
        t3.response = "Handler call.received verificado con mensaje institucional de Firby"
    except Exception as e:
        t3.add_failure(f"Error verificando código: {e}\n{traceback.format_exc()}")
    t3.evaluate()
    results.append(t3)

    return results

async def main():
    print("=" * 70)
    print("  FIRBY AI — BUCLE AUTÓNOMO DE EVALUACIÓN MULTI-AGENTE Y CALIBRACIÓN")
    print("=" * 70)
    print(f"Target URL: {BASE_URL}")
    print(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")

    async with httpx.AsyncClient(timeout=25.0) as client:
        santi_res = await test_santi_persona(client)
        prospect_res = await test_prospect_persona(client)
        redteam_res = await test_adversarial_persona(client)

        all_results = santi_res + prospect_res + redteam_res

        total = len(all_results)
        passed = sum(1 for r in all_results if r.passed)
        failed = total - passed

        print("\n" + "-" * 70)
        print(f"RESULTADOS DE LA AUDITORÍA: {passed}/{total} APROBADOS ({passed/total*100:.1f}%)")
        print("-" * 70)

        for idx, r in enumerate(all_results, 1):
            status = "PASS" if r.passed else "FAIL"
            print(f"\n[{idx:02d}] [{status}] {r.category} -> {r.name} ({r.latency_ms:.1f}ms)")
            print(f"     Respuesta/Muestra: {r.response[:160]}...")
            if not r.passed:
                for f in r.failures:
                    print(f"     [!] FALLO: {f}")

        print("\n" + "=" * 70)
        if failed == 0:
            print("CERTIFICACIÓN EXITOSA: 100% de los escenarios pasaron sin fallas.")
        else:
            print(f"ATENCIÓN: Se detectaron {failed} inconsistencias para calibrar.")
        print("=" * 70)

if __name__ == "__main__":
    asyncio.run(main())
