#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
firby_redteam.py — Autonomous AI vs AI Red-Teaming & Lead Simulation Engine.
Simulates real potential clients (AI Lead) interacting dynamically with Firby (AI Target Agent)
to discover edge-case flaws, robotic phrases, infinite loops, and conversion issues.
"""
from __future__ import annotations

import asyncio
import json
import logging
import os
import re
import sys
import time
from typing import Dict, List, Optional, Tuple, Any

log = logging.getLogger("firby.redteam")
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")

# Ensure proper imports from firby environment
sys.path.insert(0, "/home/ubuntu/firby")

# ANSI Terminal Styling
RESET = "\033[0m"
BOLD = "\033[1m"
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
MAGENTA = "\033[95m"
CYAN = "\033[96m"
WHITE = "\033[97m"

# ── 1. PERSONAS Y ESCENARIOS RED-TEAM ─────────────────────────────────────────

REDTEAM_PERSONAS: Dict[str, Dict[str, Any]] = {
    "esceptico_miedoso": {
        "name": "Cliente Escéptico (Miedo a Botox / Tratamientos)",
        "sector": "estetica",
        "business_name": "Clínica Estética Deluxe",
        "system_prompt": (
            "Eres Sofía, una mujer de 32 años en Medellín. Quieres hacerte un tratamiento facial/botox "
            "pero tienes mucho miedo de quedar cara de muñeca o con expresiones congeladas. "
            "Respóndele a la asesora comercial de WhatsApp de forma muy natural, con dudas reales, "
            "haciendo preguntas específicas sobre precios, seguridad, dolor y si la persona es real o un bot. "
            "Usa lenguaje colombianizado de WhatsApp (tutea, usa expresión de duda, minúsculas, sin puntuación formal). "
            "Responde máximo en 1 o 2 oraciones cortas."
        ),
        "initial_msg": "hola buenas, quería preguntar por botox pero la verdad me da mucho miedo quedar cara congelada",
        "goals": ["saber precio", "verificar si es bot", "pedir audio explicativo"],
        "max_turns": 6,
    },
    "objecion_precio_audio": {
        "name": "Cliente de Objeción de Precio + Solicitud de Audio",
        "sector": "salud_estetica",
        "business_name": "Clínica de las Américas",
        "system_prompt": (
            "Eres Santiago, un empresario colombiano que busca servicios de estética o salud. "
            "Quieres saber rápidamente precios y qué pueden hacer por tu negocio. "
            "Pide de forma explícita que te respondan por NOTA DE VOZ o AUDIO. "
            "Prueba si la respuesta por audio responde a tu pregunta o si vuelve a repetir frases en bucle. "
            "Escribe como alguien ocupado, directo y exigente por WhatsApp."
        ),
        "initial_msg": "Holaa, qué precios manejan y podrías enviarme un audio explicando qué harían en mi negocio?",
        "goals": ["respuesta de precios", "nota de voz real", "explicación clara sin discursos robóticos"],
        "max_turns": 5,
    },
    "ingles_spanglish": {
        "name": "Cliente Expat / Spanglish (Inglés + Audio en Inglés)",
        "sector": "salud",
        "business_name": "Clínica de las Américas",
        "system_prompt": (
            "You are Mark, an expat living in Medellín who speaks mostly English with a bit of Spanish. "
            "You want to know about consultation fees and medical procedures. "
            "You also ask the assistant to send you a voice note explaining services in English ('otro en inglés'). "
            "Be natural, short, conversational, like a real WhatsApp user."
        ),
        "initial_msg": "Hi there! I need information about medical consultation fees. Could you send me an audio in English?",
        "goals": ["english response", "english voice note", "clear pricing"],
        "max_turns": 5,
    },
    "reset_and_loop_probe": {
        "name": "Red-Team Probe (Comandos de Reset + Bucle de Confirmación)",
        "sector": "estetica",
        "business_name": "Clínica de las Américas",
        "system_prompt": (
            "Eres un evaluador probando la resiliencia del sistema de IA. "
            "Primero dices 'reset' o 'reiniciar', y luego inmediatamente haces una pregunta de negocio concreta. "
            "Verifica que el agente NO responda con plantillas fijas de 'demo reseteada' o 'borrón y cuenta nueva', "
            "sino con una respuesta 100% fluida del LLM. Luego pide un audio sobre precios."
        ),
        "initial_msg": "reset",
        "followup_triggers": ["me gustaría saber qué precios manejan para atención 24/7 y si me envías un audio"],
        "goals": ["no fallback strings", "no robotic template notices", "llm reset response"],
        "max_turns": 4,
    },
    "paciente_urgente": {
        "name": "Paciente de Urgencia Dental / Médica",
        "sector": "dental",
        "business_name": "Clínica Odontológica Especializada",
        "system_prompt": (
            "Eres Carlos, un paciente con un dolor de muela insoportable desde anoche. "
            "Necesitas una cita urgente para hoy mismo. "
            "Estás desesperado y quieres respuesta inmediata sobre disponibilidad de agendamiento. "
            "Si la IA te sale con discursos largos o respuestas frías, dile que necesitas solución ya."
        ),
        "initial_msg": "hola me dolió una muela horrible toda la noche, tienen cita urgente para hoy mismo???",
        "goals": ["agendamiento urgente", "empatía y rapidez", "sin rodeos"],
        "max_turns": 5,
    },
}


# ── 2. AUDITOR DE RESPUESTAS (RED-TEAM EVALUATOR) ─────────────────────────────

ROBOT_CLICHES = [
    r"como (IA|inteligencia artificial|(?:asistente|asesora)\s+virtual|bot)",
    r"no (tengo|tenemos) (la )?capacidad",
    r"está fuera de mi (alcance|capacidades)",
    r"no (puedo|podemos) (procesar|entender)",
    r"estoy aquí para (servirte|atenderte)",
    r"no dudes en",
    r"estaré encantad[ao] de",
    r"será un placer",
    r"⏰ tu sesión de demo ha expirado",
    r"✅ listo, demo reseteada",
    r"borrón y cuenta nueva",
    r"en un segundito te mando un audio",
    r"te mando un audio contándote",
    r"qué te gustaría que te dijera en el audio",
    r"cuál es el nombre de tu negocio para que el audio sea más personalizado",
    r"entrando en personaje",
    r"a partir de este momento actúo como",
    r"voy a actuar como",
]


class RedTeamAuditor:
    """Audita respuestas del agente en tiempo real buscando fallas."""

    @staticmethod
    def audit_turn(turn_idx: int, lead_msg: str, firby_bubbles: List[str], history: List[Dict]) -> Dict[str, Any]:
        full_text = " ||| ".join(firby_bubbles)
        low_text = full_text.lower()
        failures = []
        warnings = []
        scores = {"humanness": 1.0, "relevance": 1.0, "naturalness": 1.0}

        # 1. Clichés robóticos o plantillas prohibidas
        for pat in ROBOT_CLICHES:
            if re.search(pat, low_text, re.IGNORECASE):
                failures.append(f"Patrón robótico/fallback detectado: '{pat}' en respuesta: '{full_text[:80]}...'")
                scores["humanness"] -= 0.35

        # 2. Exceso de exclamaciones
        excl_count = full_text.count("!")
        if excl_count > 2:
            warnings.append(f"Exceso de signos de exclamación ({excl_count}): suena artificial")
            scores["naturalness"] -= 0.15

        # 3. Metas / Romper personaje en respuestas de inicio
        meta_phrases = ["estoy en personaje", "entra en personaje", "voy a actuar como la recepcionista", "en personaje"]
        for mp in meta_phrases:
            if mp in low_text:
                failures.append(f"Ruptura de personaje / Frase meta detectada: '{mp}'")
                scores["naturalness"] -= 0.30

        # 4. Incongruencia con la pregunta del cliente (Lead preguntó X y Firby no dijo nada de X)
        lead_low = lead_msg.lower()
        if ("precio" in lead_low or "cuanto" in lead_low or "cuesta" in lead_low) and not any(w in low_text for w in ("precio", "valor", "costo", "cuesta", "tarifa", "inversión", "depende", "valoración", "$")):
            warnings.append("El cliente preguntó por precios/costos y Firby no abordó el tema de costos o valoración.")
            scores["relevance"] -= 0.25

        if ("audio" in lead_low or "voz" in lead_low) and any(mp in low_text for mp in ("te mando un audio", "en un segundito te mando", "cuál es el nombre de tu negocio")):
            failures.append("Promesa vacía de audio / Plantilla estática sobre pedir el nombre del negocio.")
            scores["relevance"] -= 0.30

        # 5. Detección de bucles (Firby repite exactamente la misma frase que en turnos anteriores)
        for prev in history:
            if prev.get("role") == "assistant":
                prev_text = prev.get("content", "").lower()
                if full_text.strip().lower() == prev_text.strip() and len(full_text) > 20:
                    failures.append(f"BUCLE REPETITIVO: Firby repitió la misma respuesta previa exactamente.")
                    scores["naturalness"] -= 0.50

        final_score = round(max(0.0, (scores["humanness"] * 0.4 + scores["relevance"] * 0.3 + scores["naturalness"] * 0.3) * 100), 1)

        return {
            "turn": turn_idx,
            "lead": lead_msg,
            "firby": firby_bubbles,
            "full_text": full_text,
            "failures": failures,
            "warnings": warnings,
            "score": final_score,
        }


# ── 3. SIMULADOR IA VS IA (RED-TEAM ENGINE) ───────────────────────────────────

class RedTeamEngine:
    """Orquesta la conversación interactiva entre la IA Lead y la IA Firby."""

    def __init__(self):
        self.auditor = RedTeamAuditor()

    async def _generate_lead_reply(self, persona: Dict, history: List[Dict]) -> str:
        """Usa el LLM del motor para simular el siguiente mensaje hiper-realista del Lead."""
        from firby import llm_engine, init_llm, Config
        import src.core.globals as globals_module

        engine = getattr(globals_module, "llm_engine", None) or llm_engine
        if not engine:
            try:
                init_llm()
                engine = getattr(globals_module, "llm_engine", None) or llm_engine
            except Exception as e:
                log.warning(f"[redteam] init_llm error: {e}")

        sys_prompt = persona["system_prompt"]
        conv_formatted = "\n".join([f"{m['role'].upper()}: {m['content']}" for m in history[-6:]])

        prompt = (
            f"{sys_prompt}\n\n"
            f"HISTORIAL DE CONVERSACIÓN HASTA AHORA:\n{conv_formatted}\n\n"
            f"TAREA: Genera el siguiente mensaje del cliente por WhatsApp. "
            f"Mantente totalmente en personaje. Si el agente ya respondió tu duda, avanza en la conversación o pregunta el siguiente paso. "
            f"Escribe SÓLO el texto del mensaje, súper natural, como un usuario real en Colombia. Máximo 2 oraciones."
        )

        try:
            if engine:
                msgs = [{"role": "system", "content": sys_prompt}, {"role": "user", "content": prompt}]
                res, _ = await engine.complete(msgs, temperature=0.82, max_tokens=120)
                if res and isinstance(res, str):
                    lead_reply = res.strip().strip('"')
                    lead_reply = re.sub(r"^(SOFÍA|SANTIAGO|MARK|CARLOS|CLIENTE|LEAD):\s*", "", lead_reply, flags=re.I)
                    return lead_reply
        except Exception as e:
            log.warning(f"[redteam] Lead LLM error: {e}")

        return "entendido, pero cuánto me cuesta y cómo agendamos?"

    async def run_scenario(self, persona_key: str, persona: Dict, mode: str = "demo") -> Dict[str, Any]:
        from firby import FirbyUltra, FirbyDemo, init_llm, init_database

        try:
            init_database()
            init_llm()
        except Exception:
            pass

        firby_inst = FirbyUltra()
        await firby_inst.initialize()
        demo_handler = getattr(firby_inst, "demo_mgr", None) or FirbyDemo(firby_inst)
        chat_id = f"redteam_{mode}_{persona_key}_{int(time.time())}"
        clinic_context = {
            "name": persona.get("business_name", "Clínica de las Américas"),
            "sector": persona.get("sector", "estetica"),
            "city": "Medellín",
            "services": ["Botox facial", "Ácido Hialurónico", "Consultas de valoración", "Tratamientos estéticos"],
            "schedule": "Lunes a Viernes 8:00 AM - 6:00 PM | Sábados 8:00 AM - 12:00 PM",
            "setup_done": True,
        }

        history: List[Dict[str, str]] = []
        turns_log: List[Dict[str, Any]] = []
        all_failures: List[str] = []
        all_warnings: List[str] = []
        total_score = 0.0

        print(f"\n{BOLD}{CYAN}═══════════════════════════════════════════════════════════════════════{RESET}")
        print(f"{BOLD}{WHITE} 🚀 INICIANDO PRUEBA RED-TEAM ({mode.upper()}): {YELLOW}{persona['name']}{RESET}")
        print(f"{CYAN} Negocio: {WHITE}{clinic_context['name']} {RESET}")
        print(f"{CYAN}═══════════════════════════════════════════════════════════════════════{RESET}\n")

        current_lead_msg = persona["initial_msg"]
        max_turns = persona.get("max_turns", 5)

        for turn_idx in range(1, max_turns + 1):
            print(f"{BOLD}{BLUE}[Turno {turn_idx}/{max_turns}] {MAGENTA}🗣️ LEAD (IA):{RESET} {WHITE}{current_lead_msg}{RESET}")

            # 1. Firby responde (Demo o Producción)
            t0 = time.time()
            try:
                if mode == "production":
                    from src.core.globals import Config
                    old_demo = Config.DEMO_MODE
                    Config.DEMO_MODE = False
                    try:
                        firby_bubbles = await firby_inst.process_message(chat_id, current_lead_msg, is_simulation=True)
                    finally:
                        Config.DEMO_MODE = old_demo
                else:
                    firby_bubbles = await demo_handler.handle(chat_id, current_lead_msg, clinic_context)
            except Exception as e:
                firby_bubbles = [f"Error de ejecución: {e}"]
                all_failures.append(f"Excepción en turno {turn_idx}: {e}")

            elapsed = round((time.time() - t0) * 1000, 1)

            if isinstance(firby_bubbles, str):
                firby_bubbles = [firby_bubbles]

            # Imprimir respuesta de Firby
            print(f" {GREEN}🤖 FIRBY ({elapsed}ms):{RESET}")
            for b in firby_bubbles:
                print(f"   💬 {b}")

            # Update history
            history.append({"role": "user", "content": current_lead_msg})
            full_firby_resp = " ||| ".join(firby_bubbles)
            history.append({"role": "assistant", "content": full_firby_resp})

            # 2. Auditar turno
            turn_audit = self.auditor.audit_turn(turn_idx, current_lead_msg, firby_bubbles, history[:-2])
            turns_log.append(turn_audit)
            total_score += turn_audit["score"]

            if turn_audit["failures"]:
                for f in turn_audit["failures"]:
                    print(f"   {RED}✘ FAIL:{RESET} {f}")
                    all_failures.append(f"Turno {turn_idx}: {f}")

            if turn_audit["warnings"]:
                for w in turn_audit["warnings"]:
                    print(f"   {YELLOW}⚠ WARN:{RESET} {w}")
                    all_warnings.append(f"Turno {turn_idx}: {w}")

            print(f"   {CYAN}📊 Score Turno: {WHITE}{turn_audit['score']}%{RESET}\n")

            # Check if simulation reached natural conclusion
            if any(term in full_firby_resp.lower() for term in ("agendada", "confirmada tu cita", "nos vemos el", "te esperamos")):
                print(f"{BOLD}{GREEN}✨ Conversación convertida exitosamente con agendamiento/cierre en turno {turn_idx}!{RESET}\n")
                break

            # 3. AI Lead generates next reply
            if turn_idx < max_turns:
                current_lead_msg = await self._generate_lead_reply(persona, history)
                await asyncio.sleep(0.5)

        avg_score = round(total_score / len(turns_log), 1) if turns_log else 0.0
        status_badge = f"{GREEN}PASSED (100% OK){RESET}" if not all_failures else f"{RED}FAILED ({len(all_failures)} fallos){RESET}"

        summary = {
            "persona_key": persona_key,
            "persona_name": persona["name"],
            "total_turns": len(turns_log),
            "score": avg_score,
            "failures": all_failures,
            "warnings": all_warnings,
            "turns": turns_log,
        }

        print(f"{BOLD}{CYAN}-----------------------------------------------------------------------{RESET}")
        print(f"{BOLD}RESULTADO FINAL PRUEBA ({mode.upper()}): {status_badge} | Score Calidad: {YELLOW}{avg_score}%{RESET}")
        print(f"{BOLD}{CYAN}-----------------------------------------------------------------------{RESET}\n")

        return summary

    async def run_all(self, mode: str = "demo") -> List[Dict[str, Any]]:
        results = []
        for pkey, pdata in REDTEAM_PERSONAS.items():
            res = await self.run_scenario(pkey, pdata, mode=mode)
            results.append(res)
        return results


# ── 4. CLI RUNNER ENTRYPOINT ──────────────────────────────────────────────────

async def main():
    import argparse
    parser = argparse.ArgumentParser(description="Firby AI vs AI Red-Team Engine")
    parser.add_argument("--scenario", type=str, help="Escenario específico a probar")
    parser.add_argument("--mode", type=str, default="demo", choices=["demo", "production"], help="Modo a evaluar: demo o production")
    parser.add_argument("--all", action="store_true", help="Ejecutar todos los escenarios de prueba Red-Team")
    args = parser.parse_args()

    engine = RedTeamEngine()

    if args.scenario:
        if args.scenario not in REDTEAM_PERSONAS:
            print(f"{RED}Escenario '{args.scenario}' no encontrado. Disponibles: {list(REDTEAM_PERSONAS.keys())}{RESET}")
            sys.exit(1)
        await engine.run_scenario(args.scenario, REDTEAM_PERSONAS[args.scenario], mode=args.mode)
    else:
        # Default: run all scenarios
        print(f"{BOLD}{GREEN}🔥 Ejecutando Suite Completa de Red-Teaming IA vs IA ({len(REDTEAM_PERSONAS)} escenarios en modo {args.mode.upper()})...{RESET}\n")
        all_res = await engine.run_all(mode=args.mode)


        total_scenarios = len(all_res)
        failed_scenarios = [r for r in all_res if r["failures"]]
        avg_overall_score = round(sum(r["score"] for r in all_res) / total_scenarios, 1) if total_scenarios else 0.0

        print(f"\n{BOLD}{MAGENTA}======================================================================={RESET}")
        print(f"{BOLD}{WHITE} 📊 RESUMEN EJECUTIVO RED-TEAM AUDIT{RESET}")
        print(f"{BOLD}{MAGENTA}======================================================================={RESET}")
        print(f" • Escenarios Evaluados: {WHITE}{total_scenarios}{RESET}")
        print(f" • Escenarios Limpios (100% OK): {GREEN}{total_scenarios - len(failed_scenarios)}{RESET}")
        print(f" • Escenarios con Fallos: {RED}{len(failed_scenarios)}{RESET}")
        print(f" • Promedio de Calidad Global: {YELLOW}{avg_overall_score}%{RESET}")
        print(f"{BOLD}{MAGENTA}======================================================================={RESET}\n")


if __name__ == "__main__":
    asyncio.run(main())
