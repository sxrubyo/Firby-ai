# -*- coding: utf-8 -*-
"""
Firby Multi-Agent Swarm Engine
==============================
Motor orquestador de agentes autónomos y red multi-agente escalable.
Coordina transferencias (handoffs), ejecución de herramientas, trazabilidad en SQLite
y comunicación a través del SwarmMessageBus.
"""

from __future__ import annotations
import json
import logging
import sqlite3
import re
import time
from typing import Dict, Any, List, Optional, Callable, Tuple
from src.core.swarm.types import SwarmResult, AgentMessage, MessageType
from src.core.swarm.registry import SwarmAgent, swarm_registry
from src.core.swarm.message_bus import message_bus

log = logging.getLogger("firby.swarm.engine")


class SwarmEngine:
    """Orquestador de enjambre agéntico para Firby."""

    def __init__(self, db_path: str = "/home/ubuntu/firby/firby_ultra.db"):
        self.db_path = db_path
        self.registry = swarm_registry
        self.bus = message_bus

    def register_agent(self, agent: SwarmAgent, persist_db: bool = False):
        self.registry.register(agent, persist_db=persist_db)

    def get_agent(self, agent_id: str) -> Optional[SwarmAgent]:
        return self.registry.get(agent_id)

    def load_active_agent_id(self, chat_id: str, default_id: str) -> str:
        """Carga el ID del agente que estaba atendiendo la conversación."""
        try:
            with sqlite3.connect(self.db_path, timeout=3.0) as conn:
                cur = conn.cursor()
                row = cur.execute("SELECT state FROM conversation_states WHERE chat_id = ?", (chat_id,)).fetchone()
                if row and row[0]:
                    state = json.loads(row[0])
                    return state.get("active_agent_id", default_id)
        except Exception:
            pass
        return default_id

    def save_active_agent_id(self, chat_id: str, agent_id: str, context: Dict[str, Any]):
        """Persiste el agente activo en conversation_states."""
        try:
            with sqlite3.connect(self.db_path, timeout=3.0) as conn:
                cur = conn.cursor()
                row = cur.execute("SELECT state FROM conversation_states WHERE chat_id = ?", (chat_id,)).fetchone()
                state = {}
                if row and row[0]:
                    try:
                        state = json.loads(row[0])
                    except Exception:
                        state = {}
                state["active_agent_id"] = agent_id
                state["context"] = context
                state["updated_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
                cur.execute(
                    """
                    INSERT INTO conversation_states (chat_id, state, updated_at)
                    VALUES (?, ?, datetime('now'))
                    ON CONFLICT(chat_id) DO UPDATE SET
                        state = excluded.state,
                        updated_at = datetime('now')
                    """,
                    (chat_id, json.dumps(state, ensure_ascii=False))
                )
                conn.commit()
        except Exception as e:
            log.error(f"[SwarmEngine] Error guardando estado de agente activo: {e}")

    def _strip_emojis(self, text: str) -> str:
        """Elimina emojis garantizando la regla de CERO emojis."""
        emoji_pattern = re.compile(r"[\U00010000-\U0010ffff\u2600-\u27bf\u2b50\u231a-\u23f3\u2190-\u21ff]")
        return emoji_pattern.sub("", text).strip()

    def _parse_agent_output(self, raw_text: str) -> Tuple[List[str], Optional[Dict[str, Any]], Optional[Dict[str, Any]], List[str], Optional[str], Optional[Dict[str, Any]]]:
        """Extrae burbujas, navegación, tarjetas interactivas, handoffs y acciones."""
        ui_action = None
        action_card = None
        chips = []
        handoff_target = None
        booking_action = None

        # 1. Handoff: [HANDOFF:target_agent_id:reason]
        handoff_match = re.search(r'\[HANDOFF:([a-zA-Z0-9_\.\-]+)(?::([^\]]*))?\]', raw_text)
        if handoff_match:
            handoff_target = handoff_match.group(1).strip()
            raw_text = raw_text.replace(handoff_match.group(0), "")

        # 2. Navegación estructurada de interfaz
        ui_sec_match = re.search(r'\[UI:NAVIGATE_TO_SECTION:(#[a-zA-Z0-9_-]+)\]', raw_text)
        if ui_sec_match:
            ui_action = {"type": "navigate_to_section", "target": ui_sec_match.group(1), "route": ui_sec_match.group(1)}
            raw_text = raw_text.replace(ui_sec_match.group(0), "")

        ui_nav_match = re.search(r'\[UI:NAVIGATE_TO:([a-zA-Z0-9_\-/#]+)\]', raw_text)
        if ui_nav_match:
            ui_action = {"type": "navigate_to", "target": ui_nav_match.group(1), "route": ui_nav_match.group(1)}
            raw_text = raw_text.replace(ui_nav_match.group(0), "")

        ui_hl_match = re.search(r'\[UI:HIGHLIGHT:([a-zA-Z0-9_\-\.#]+)\]', raw_text)
        if ui_hl_match:
            ui_action = {"type": "highlight", "target": ui_hl_match.group(1), "route": ui_hl_match.group(1)}
            raw_text = raw_text.replace(ui_hl_match.group(0), "")

        # Compatibilidad con comando legacy [CMD:NAV:#seccion]
        nav_match = re.search(r'\[CMD:NAV:(#[a-zA-Z0-9_-]+)\]', raw_text)
        if nav_match and not ui_action:
            ui_action = {"type": "navigate_to_section", "target": nav_match.group(1), "route": nav_match.group(1)}
            raw_text = raw_text.replace(nav_match.group(0), "")
        elif nav_match:
            raw_text = raw_text.replace(nav_match.group(0), "")

        # 3. Chips de respuesta rápida: [CHIPS: Opción 1 | Opción 2]
        chips_match = re.search(r'\[CHIPS:(.*?)\]', raw_text)
        if chips_match:
            raw_chips = chips_match.group(1).split("|")
            clean_chips = [self._strip_emojis(c).strip() for c in raw_chips if len(c.strip()) > 1]
            if clean_chips:
                chips = clean_chips
            raw_text = raw_text.replace(chips_match.group(0), "")

        # 4. Google Auth Card
        auth_match = re.search(r'\[ACTION:GOOGLE_AUTH:(.*?):(.*?)\]', raw_text)
        if auth_match:
            action_card = {
                "type": "google_auth",
                "label": self._strip_emojis(auth_match.group(1)).strip() or "Iniciar prueba con Google",
                "url": auth_match.group(2).strip() or "/auth/google"
            }
            raw_text = raw_text.replace(auth_match.group(0), "")

        # 5. Botón genérico (ej: WhatsApp del dueño)
        btn_match = re.search(r'\[ACTION:BUTTON:(.*?):(.*?)\]', raw_text)
        if btn_match:
            action_card = {
                "type": "button",
                "label": self._strip_emojis(btn_match.group(1)).strip(),
                "url": btn_match.group(2).strip()
            }
            raw_text = raw_text.replace(btn_match.group(0), "")

        # 6. Agendamiento real de cita
        book_match = re.search(r'\[ACTION:BOOK_APPOINTMENT:(.*?):(.*?):(.*?):(.*?)(?::(.*?))?\]', raw_text)
        if book_match:
            booking_action = {
                "name": book_match.group(1).strip(),
                "phone": book_match.group(2).strip(),
                "service": book_match.group(3).strip(),
                "datetime": book_match.group(4).strip(),
                "notes": book_match.group(5).strip() if book_match.group(5) else ""
            }
            raw_text = raw_text.replace(book_match.group(0), "")

        # 7. Burbujas limpias (delimitadas por ||| o párrafos)
        if "|||" in raw_text:
            parts = [p.strip() for p in raw_text.split("|||") if p.strip()]
        else:
            # Si el modelo devolvió párrafos dobles, separarlos en hasta 2 burbujas
            parts = [p.strip() for p in raw_text.split("\n\n") if p.strip()]

        clean_bubbles = []
        for p in parts:
            p_clean = re.sub(r'\[(CHIPS|CMD|ACTION|HANDOFF|UI):[^\]]*\]?', '', p).strip()
            p_clean = self._strip_emojis(p_clean)
            if p_clean:
                clean_bubbles.append(p_clean)

        return clean_bubbles, ui_action, action_card, chips, handoff_target, booking_action

    def _resolve_target_agent(self, target_identifier: str) -> Optional[SwarmAgent]:
        """Resuelve un agente por id directo o por nombre clásico."""
        agent = self.registry.get(target_identifier)
        if agent:
            return agent
        # Buscar por nombre o alias (ej: 'PricingAdvisorAgent' -> 'landing.pricing')
        for ag in self.registry._agents.values():
            if ag.name.lower() == target_identifier.lower() or ag.id.lower() == target_identifier.lower():
                return ag
        return None

    async def run(
        self,
        user_message: str,
        chat_id: str,
        org_id: str,
        history: List[Dict[str, str]],
        llm_caller: Callable[[str, List[Dict[str, str]], str], Any]
    ) -> SwarmResult:
        """Ejecuta el flujo multi-agente con resolución de handoffs y comunicación en el bus."""
        is_landing = org_id in ("firby_landing", "firby", "firby_default", "")
        default_agent_id = "landing.concierge" if is_landing else "booking.coordinator"

        active_agent_id = self.load_active_agent_id(chat_id, default_agent_id)
        current_agent = self.get_agent(active_agent_id) or self.get_agent(default_agent_id)
        if not current_agent:
            # Fallback seguro al primer agente disponible
            all_agents = self.registry.list_all(org_id)
            current_agent = all_agents[0] if all_agents else list(self.registry._agents.values())[0]

        handoff_history = []
        inter_agent_messages = []
        max_hops = 2
        hop = 0

        final_bubbles = []
        final_ui_action = None
        final_action_card = None
        final_chips = []

        while hop < max_hops:
            hop += 1
            log.info(f"[SwarmEngine] Hop {hop}: Agente activo '{current_agent.id}' ({current_agent.name})")

            # Ejecutar LLM con el system prompt del agente actual
            raw_llm_response = await llm_caller(current_agent.system_prompt, history, user_message)
            bubbles, ui_action, action_card, chips, handoff_target, booking_action = self._parse_agent_output(raw_llm_response)

            if ui_action:
                final_ui_action = ui_action
            if action_card:
                final_action_card = action_card
            if chips:
                final_chips = chips

            # Ejecución atómica de reserva si el agente emitió BOOK_APPOINTMENT
            if booking_action:
                from src.core.enterprise_tools import enterprise_tool_registry
                tool_res = await enterprise_tool_registry.execute(
                    "book_appointment",
                    {
                        "patient_name": booking_action["name"],
                        "patient_phone": booking_action["phone"],
                        "service": booking_action["service"],
                        "datetime_slot": booking_action["datetime"],
                        "notes": booking_action["notes"]
                    },
                    context={"chat_id": chat_id, "org_id": org_id}
                )
                if tool_res.get("success"):
                    apt_id = tool_res["result"].get("appointment_id")
                    confirmation = f"Cita confirmada en el sistema (Reserva #{apt_id}). Te esperamos."
                    bubbles.append(confirmation)
                    final_chips = ["Ver detalles de la cita", "Ubicación de la sede", "Preguntas frecuentes"]

            # Si el agente emitió un HANDOFF a otro especialista
            if handoff_target:
                next_agent = self._resolve_target_agent(handoff_target)
                if next_agent and next_agent.id != current_agent.id:
                    log.info(f"[SwarmEngine] Handoff ejecutado: {current_agent.id} -> {next_agent.id}")
                    handoff_event = f"{current_agent.id} -> {next_agent.id}"
                    handoff_history.append(handoff_event)

                    # Publicar en el SwarmMessageBus
                    msg = AgentMessage(
                        sender_id=current_agent.id,
                        recipient_id=next_agent.id,
                        conversation_id=chat_id,
                        org_id=org_id,
                        message_type=MessageType.HANDOFF,
                        payload={"reason": handoff_target, "user_message": user_message}
                    )
                    await self.bus.publish(msg)
                    inter_agent_messages.append(msg.to_dict())

                    current_agent = next_agent
                    # Continuar el ciclo para que el especialista dé la respuesta final
                    continue

            # Respuesta definitiva de este agente
            final_bubbles = bubbles
            break

        # Chips contextuales por defecto si no hubo específicos
        if not final_chips:
            if current_agent.id == "landing.pricing":
                final_chips = ["Ver planes y precios", "Activar 7 días gratis", "Hablar con el equipo"]
            elif current_agent.id == "landing.setup":
                final_chips = ["WordPress", "Shopify", "Web a medida"]
            elif current_agent.id == "booking.coordinator":
                final_chips = ["En la mañana", "En la tarde", "Ver otros días"]
            else:
                final_chips = ["Ver cómo funciona", "Ver planes y precios", "Hablar con el equipo"]

        # Persistir el nuevo agente activo
        self.save_active_agent_id(chat_id, current_agent.id, {
            "hops": hop,
            "handoffs": handoff_history,
            "domain": current_agent.domain.value
        })

        response_text = "\n".join(final_bubbles) if final_bubbles else "Entendido."

        return SwarmResult(
            response=response_text,
            bubbles=final_bubbles or ["Entendido."],
            chips=final_chips,
            ui_action=final_ui_action,
            action_card=final_action_card,
            active_agent=current_agent.id,
            handoff_history=handoff_history,
            inter_agent_messages=inter_agent_messages
        )


# Singleton
swarm_engine = SwarmEngine()
