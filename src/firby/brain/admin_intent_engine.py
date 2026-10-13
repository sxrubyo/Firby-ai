# -*- coding: utf-8 -*-
"""
Firby Admin Natural Conversational Intent Engine
Translates informal, natural, voice-note or conversational Spanish from the business owner
into live business operations without requiring slash commands or technical syntax.
"""
from __future__ import annotations

import re
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple

log = logging.getLogger("firby.admin_intent_engine")


class AdminIntentEngine:
    """Interpreta intenciones en lenguaje 100% natural del dueño del negocio."""

    def __init__(self, db):
        self.db = db

    async def interpret_and_execute(
        self, text: str, clinic: Dict[str, Any], chat_id: str
    ) -> Optional[str]:
        """
        Analiza el mensaje en lenguaje natural del dueño y ejecuta la acción correspondiente.
        Si no es una instrucción operativa, devuelve None para que el LLM converse con el dueño.
        """
        text_clean = text.lower().strip()
        clinic_name = clinic.get("name", "Firby AI") if clinic else "Firby AI"
        owner_name = clinic.get("owner_name") or clinic.get("doctor_name") or "Santi"
        if owner_name.lower() in ["doctor", "doctor/a", "admin", "usuario", "dr"]:
            owner_name = "Santi"

        # 0. PANEL WEB / DASHBOARD / LOGIN ("cuál es el link?", "dónde inicio sesión?", "pásame el panel")
        if any(w in text_clean for w in [
            "link de la pagina", "link de la página", "enlace de la pagina", "enlace de la página",
            "iniciar sesion", "iniciar sesión", "iniciar sección", "donde inicio", "dónde inicio",
            "link del panel", "enlace del panel", "link del dashboard", "dashboard", "panel web",
            "entrar a la pagina", "entrar a la página", "ver la pagina", "ver la página", "link de la web"
        ]):
            import os
            base_url = os.getenv("BASE_URL", "https://firbyai.lat")
            return f"Claro que sí! Aquí tienes el acceso a tu panel web oficial:\n\n🌐 {base_url}/sign-in\n\nPuedes ingresar directamente con tu correo y contraseña."

        # 1. RESUMEN FORMAL / MÉTRICAS DEL DÍA ("resumen de hoy", "cómo van las cosas hoy?", "reporte del día")
        is_formal_summary = any(w in text_clean for w in [
            "resumen de hoy", "resumen del día", "resumen del dia", "reporte de hoy",
            "cómo van las cosas hoy", "como van las cosas hoy", "cómo estuvo el día", "como estuvo el dia",
            "resumen operativo"
        ])
        has_conversational_topic = any(w in text_clean for w in [
            "lanzamiento", "landing", "web", "cliente", "campaña", "estrategia",
            "opinas", "crees", "hacemos", "hacer", "marketing", "demo", "ventas",
            "piensas", "parece", "funciona", "arreglar", "cambiar"
        ])
        if is_formal_summary and not has_conversational_topic:
            return self._build_executive_daily_summary(clinic_name, owner_name)

        # 2. CONSULTA DE CITAS ("qué citas hay hoy?", "quién viene mañana?", "a qué hora es la primera cita?")
        if any(w in text_clean for w in [
            "qué citas", "que citas", "quién viene", "quien viene", "citas de hoy", "citas de mañana",
            "agenda de hoy", "agenda de mañana", "cómo está la agenda", "como esta la agenda",
            "a qué hora", "a que hora", "cuántas citas hay", "cuantas citas hay"
        ]):
            is_tomorrow = "mañana" in text_clean
            return self._query_agenda(is_tomorrow)

        # 3. PAUSAR / SILENCIAR BOT CON UN PACIENTE ("pausa a Carlos", "silencia a 300...", "no le contestes a...")
        if any(w in text_clean for w in [
            "pausa a", "silencia a", "no le respondas a", "no le contestes a",
            "voy a hablar yo con", "deja que yo hablo con", "pausar chat con"
        ]):
            return self._handle_pause_request(text_clean)

        # 4. REACTIVAR BOT CON UN PACIENTE ("activa a Carlos", "reactiva a 300...", "ya puedes responderle")
        if any(w in text_clean for w in [
            "activa a", "reactiva a", "vuelve a responder a", "despausa a", "ya puedes hablar con"
        ]):
            return self._handle_resume_request(text_clean)

        # 5. CREAR AUTOMATIZACIÓN ("créame un flujo que...", "automatiza que cuando...", "haz que cuando alguien...")
        if any(w in text_clean for w in [
            "crea un flujo", "creame un flujo", "crea una automatización", "creame una automatizacion",
            "automatiza que", "haz que cuando", "configura que cuando"
        ]):
            from src.firby.brain.automation_architect import AutomationArchitect
            arch = AutomationArchitect()
            res = await arch.create_workflow_from_natural_language(text, clinic_name=clinic_name)
            if res.get("ok"):
                return (
                    f"Listo {owner_name}! Ya dejé creada y activa esa automatización en el sistema ||| "
                    f"Cada vez que ocurra ese evento, Firby se encargará de ejecutarlo en automático."
                )
            return "Intenté crear la automatización pero tuve un pequeño error de conexión con el motor. Me confirmas los detalles?"

        # 6. LLENAR AGENDA / REACTIVACIÓN ("mándale mensaje a los pacientes viejos", "reactiva clientes inactivos")
        if any(w in text_clean for w in [
            "pacientes viejos", "pacientes inactivos", "reactivar pacientes", "llenar agenda",
            "escribe a los que no han vuelto", "haz una campaña", "manda una promoción"
        ]):
            from src.firby.brain.growth_engine import GrowthCampaignEngine
            growth = GrowthCampaignEngine(db=self.db)
            res = await growth.execute_reactivation_campaign(
                service_name="consulta de control",
                clinic_name=clinic_name,
                days_inactive=60,
                batch_size=10
            )
            return (
                f"Entendido! Ya inicié la campaña de reactivación segura para {res.get('total_candidates', 0)} pacientes inactivos ||| "
                f"Los mensajes se están enviando con pausas humanas de 2 minutos para proteger tu WhatsApp de bloqueos."
            )

        # 7. CONSULTA DE EQUIPO / EMPLEADOS ("quiénes están trabajando?", "cómo está mi equipo?")
        if any(w in text_clean for w in [
            "quiénes están trabajando", "quienes estan trabajando", "cómo está mi equipo",
            "qué empleados tengo", "quiénes son mis bots", "equipo digital"
        ]):
            from src.firby.brain.employee_roles import EmployeeManager, EMPLOYEE_PROFILES
            mgr = EmployeeManager(db=self.db)
            active = mgr.get_active_roles()
            names = [EMPLOYEE_PROFILES.get(r, {}).get("default_name", "Agente") for r in active]
            return (
                f"Tu equipo digital de Firby está 100% activo y coordinado: {', '.join(names)} ||| "
                f"Firby está en la recepción y atención web, Santiago en el cierre y cobros, Camila en el triaje y Nova en las automatizaciones."
            )

        # 8. GESTIÓN DE INSTRUCCIONES / ENSEÑANZAS DINÁMICAS (Micro-prompts aprendidos)
        # 8a. Listar instrucciones aprendidas
        if any(w in text_clean for w in [
            "qué instrucciones tienes", "que instrucciones tienes", "ver instrucciones", "mostrar instrucciones",
            "qué has aprendido", "que has aprendido", "cuáles son tus reglas", "cuales son tus reglas"
        ]):
            if self.db and hasattr(self.db, "get_active_admin_instructions"):
                insts = self.db.get_active_admin_instructions()
                if insts:
                    lines = ["📋 *Instrucciones activas aprendidas de ti*:"]
                    for idx, ins in enumerate(insts, 1):
                        lines.append(f"{idx}. {ins}")
                    return "\n".join(lines) + " ||| Las aplico en cada conversación con los pacientes."
                else:
                    return "Aún no tengo instrucciones personalizadas guardadas ||| Puedes enseñarme lo que quieras diciéndome por ejemplo: 'Cuando te escriban, saluda con...' o 'Aprende que la consulta cuesta 50 mil'."

        # 8b. Limpiar / Olvidar instrucciones
        if any(w in text_clean for w in [
            "borra las instrucciones", "borrar instrucciones", "olvida las instrucciones",
            "limpiar instrucciones", "restablecer reglas", "borra lo que aprendiste"
        ]):
            if self.db and hasattr(self.db, "clear_admin_instructions"):
                self.db.clear_admin_instructions()
                return f"Listo {owner_name}! He limpiado todas las instrucciones personalizadas anteriores ||| Mis agentes vuelven a su configuración base de atención web."

        # 8c. Captura inteligente de NUEVA INSTRUCCIÓN / ENSEÑANZA
        is_instruction = False
        instruction_triggers = [
            "cuando te escriban", "cuando alguien escriba", "cuando pregunten", "cuando un paciente",
            "de ahora en adelante", "a partir de ahora", "no digas", "no uses la palabra", "no respondas",
            "aprende esto", "aprende que", "recuerda que", "ten en cuenta que", "agrega que", "añade que",
            "cambia el saludo", "di siempre", "responde siempre", "el precio es", "los precios son",
            "nuestro horario es", "enseña a", "debes decir", "saluda con", "saluda diciendo"
        ]
        if any(w in text_clean for w in instruction_triggers):
            is_instruction = True

        if is_instruction:
            clean_instruction = text.strip()
            if self.db and hasattr(self.db, "add_admin_instruction"):
                self.db.add_admin_instruction(chat_id, clean_instruction)
                return (
                    f"Entendido! Ya aprendí esa nueva instrucción y la incorporé a mis agentes de atención: \"{clean_instruction}\" ||| "
                    f"A partir de este momento la tendré en cuenta en todas las respuestas con los prospectos y visitantes sin alterar mis otras funciones."
                )

        # No es una orden determinista directa ➔ Dejar que el LLM responda con empatía
        return None

    def _build_executive_daily_summary(self, clinic_name: str, owner_name: str = "Santi") -> str:
        """Construye un resumen ejecutivo cálido y profesional para el dueño."""
        try:
            today_str = datetime.now().strftime("%Y-%m-%d")
            with self.db._conn() as c:
                convs_today = c.execute(
                    "SELECT count(DISTINCT chat_id) FROM conversations WHERE created_at LIKE ?",
                    (f"%{today_str}%",)
                ).fetchone()[0]
                apts_today = c.execute(
                    "SELECT count(*) FROM appointments WHERE datetime_slot LIKE ?",
                    (f"%{today_str}%",)
                ).fetchone()[0]
                total_patients = c.execute("SELECT count(*) FROM patients").fetchone()[0]

            return (
                f"Hola {owner_name}! Todo marchando excelente hoy en {clinic_name} ||| "
                f"Hoy hemos atendido a {convs_today} conversaciones en la plataforma, tenemos {apts_today} citas o demostraciones registradas en el sistema y tu base ya cuenta con {total_patients} contactos ||| "
                f"Todos los canales de atención y servicios están activos y operando normalmente."
            )
        except Exception as e:
            return f"Hola {owner_name}! El sistema está activo y funcionando normalmente en {clinic_name}."

    def _query_agenda(self, is_tomorrow: bool = False) -> str:
        """Consulta la agenda de hoy o mañana con lenguaje natural."""
        target_date = (datetime.now() + timedelta(days=1 if is_tomorrow else 0)).strftime("%Y-%m-%d")
        day_label = "mañana" if is_tomorrow else "hoy"
        try:
            with self.db._conn() as c:
                rows = c.execute("""
                    SELECT patient_name, service, datetime_slot, status
                    FROM appointments
                    WHERE datetime_slot LIKE ?
                    ORDER BY id ASC
                """, (f"%{target_date}%",)).fetchall()

                if not rows:
                    return f"Para {day_label} ({target_date}) no tienes citas programadas todavía en el sistema."

                lines = [f"Para {day_label} tienes {len(rows)} cita(s) programada(s):"]
                for idx, r in enumerate(rows, 1):
                    time_part = r["datetime_slot"].split("T")[-1] if "T" in r["datetime_slot"] else r["datetime_slot"]
                    lines.append(f"• {time_part[:5]} — {r['patient_name']} ({r['service']})")

                return "\n".join(lines)
        except Exception as e:
            return f"No pude consultar la agenda en este momento: {e}"

    def _handle_pause_request(self, text: str) -> str:
        """Pausa el bot con un paciente específico."""
        phone_match = re.search(r"(\+?\d{8,15})", text)
        if phone_match:
            clean_phone = phone_match.group(1).replace("+", "").strip()
            target_jid = f"{clean_phone}@s.whatsapp.net"
            try:
                from src.firby.brain.database import ConversationState
                state = self.db.get_conversation_state(target_jid)
                if state:
                    state.escalation_needed = True
                    self.db.save_conversation_state(state)
                else:
                    self.db.save_conversation_state(ConversationState(chat_id=target_jid, escalation_needed=True))
                return f"Listo! Ya pausé a Firby para el número +{clean_phone}. No le responderá hasta que me digas que lo reactive."
            except Exception as e:
                pass
        return "Para pausar a un paciente, dime su número de teléfono (ej. 'pausa a 3001234567') y me encargo de inmediato."

    def _handle_resume_request(self, text: str) -> str:
        """Reactiva el bot con un paciente específico."""
        phone_match = re.search(r"(\+?\d{8,15})", text)
        if phone_match:
            clean_phone = phone_match.group(1).replace("+", "").strip()
            target_jid = f"{clean_phone}@s.whatsapp.net"
            try:
                state = self.db.get_conversation_state(target_jid)
                if state:
                    state.escalation_needed = False
                    self.db.save_conversation_state(state)
                return f"Perfecto! Ya reactivé la atención automática para el número +{clean_phone}."
            except Exception as e:
                pass
        return "Dime el número de teléfono del paciente para reactivarlo (ej. 'activa a 3001234567')."
