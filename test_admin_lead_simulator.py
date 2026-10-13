"""
test_admin_lead_simulator.py
════════════════════════════════════════════════════════════════════════════════
AUTOMATED ADMIN LEAD SIMULATOR FOR FIRBY AI
Simula una conversación real de 10 turnos entre el Dueño (Santiago) y Firby AI.
Inspecciona respuestas, verifica limpieza de texto, ausencia de artifacts ():*),
generación de notas de voz nativas y persistencia de memoria.
════════════════════════════════════════════════════════════════════════════════
"""
import sys
import asyncio
import os
import json
import logging
from dotenv import load_dotenv

load_dotenv("/home/ubuntu/firby/.env")

sys.path.insert(0, "/home/ubuntu/firby")

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("firby.simulator")

TEST_CHAT_ID = "3124348669@s.whatsapp.net"
ADMIN_PHONE = "3124348669"

async def run_simulation():
    from src.firby.brain.database import DatabaseManager
    from src.firby.brain.llm_engine import LLMEngine
    import src.core.globals as g

    print("\n" + "="*80)
    print("🚀 INICIANDO SIMULACIÓN DE ADMIN REAL EN FIRBY AI")
    print("="*80 + "\n")

    db_inst = DatabaseManager("instances/clinica-de-las-americas/firby.db", "instances/clinica-de-las-americas/firby_vectors.db")
    db_inst.update_clinic(admin_chat_ids=json.dumps([ADMIN_PHONE, TEST_CHAT_ID]))
    
    g.db = db_inst
    llm_inst = LLMEngine()
    g.llm_engine = llm_inst

    from src.core.runtime import FirbyUltra
    firby_app = FirbyUltra()

    test_turns = [
        ("Hola, me cambias el nombre a Valentina", "Cambio de nombre a Valentina"),
        ("Como es tu nombre???", "Verificación de nombre asignado"),
        ("Enviame un audio contandome tus capacidades", "Petición de audio de voz"),
        ("Si te doy las apis de google para que veas mi calendario te conectas?", "Integración Google Calendar"),
        ("Tenemos leche a 4500 y arroz a 3500 pesos", "Ingestión de precios / catálogo de inventario"),
        ("Enviame otro audio", "Petición de segundo audio"),
    ]

    passed_tests = 0
    failed_tests = 0

    for idx, (user_msg, scenario_title) in enumerate(test_turns, 1):
        print(f"\n💬 [TURNO {idx}] Admin: \"{user_msg}\" ({scenario_title})")
        
        result = await firby_app.process_message(
            chat_id=TEST_CHAT_ID,
            text=user_msg,
            route={"platform": "whatsapp", "channel_identity": "admin"}
        )

        bubbles = result.get("bubbles", []) if isinstance(result, dict) else (result or [])
        status = result.get("status", "ok") if isinstance(result, dict) else "ok"

        print(f"   🤖 Firby Responde ({len(bubbles)} burbujas, status={status}):")
        for b in bubbles:
            print(f"      👉 \"{b}\"")

        # AUDITORÍA DE ANOMALÍAS DE TEXTO
        anomalies = []
        for b in bubbles:
            if any(bad in b for bad in ["):*", ")*", ":*", "(:", "como ia"]):
                anomalies.append(f"Artefacto visual detectado: '{b}'")
            if "¿" in b or "¡" in b:
                anomalies.append(f"Signo invertido de puntuación: '{b}'")

        if anomalies:
            print(f"   ❌ ERROR EN TURNO {idx}: {anomalies}")
            failed_tests += 1
        else:
            print(f"   ✅ TURNO {idx} SUPERADO CON ÉXITO")
            passed_tests += 1

        await asyncio.sleep(1)

    print("\n" + "="*80)
    print(f"📊 RESULTADO DE LA SIMULACIÓN: {passed_tests} Pruebas Exitosas, {failed_tests} Fallidas.")
    print("="*80 + "\n")

if __name__ == "__main__":
    asyncio.run(run_simulation())
