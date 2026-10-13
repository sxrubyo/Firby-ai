# -*- coding: utf-8 -*-
"""
Firby AI — Workspace Teaching & Behavioral Alignment Engine
==========================================================
Permite al dueño del negocio enseñar, alinear y configurar a su agente en el Workspace
a través de lenguaje natural y ejemplos guiados, sin re-entrenar modelos de fondo:

KNOWLEDGE + INSTRUCTIONS + EXAMPLES + POLICIES + TOOLS + PERMISSIONS + EVALUATION

Convierte expresiones como:
"Cuando un cliente pregunte por cambios de reserva, primero verifica la política de cambios"
en una regla estructurada (StructuredRule) persistente que el runtime aplica de inmediato.
"""

from __future__ import annotations
import re
import time
import uuid
import logging
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Tuple

from src.core.operator.business_config import (
    get_business_config, register_business_config,
    StructuredRule, BehaviorExample, BusinessConfig
)

log = logging.getLogger("firby.operator.teaching")


@dataclass
class TeachingResult:
    """Resultado del procesamiento de una instrucción de enseñanza en el Workspace."""
    ok: bool
    action_taken: str  # rule_added, policy_updated, tool_permission_updated, example_added, knowledge_added
    summary: str
    structured_data: Dict[str, Any] = field(default_factory=dict)
    feedback_for_owner: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ok": self.ok,
            "action_taken": self.action_taken,
            "summary": self.summary,
            "structured_data": self.structured_data,
            "feedback_for_owner": self.feedback_for_owner
        }


class WorkspaceTeachingEngine:
    """
    Motor que interpreta las instrucciones operativas del propietario y las traduce
    a especificaciones ejecutables en el BusinessConfig.
    """

    @classmethod
    def teach(cls, tenant_id: str, instruction: str, example_response: str = "") -> TeachingResult:
        """
        Procesa una instrucción del propietario para alinear o configurar el comportamiento del agente.
        """
        text = (instruction or "").strip()
        if not text:
            return TeachingResult(
                ok=False,
                action_taken="none",
                summary="Instrucción vacía",
                feedback_for_owner="Por favor escribe una indicación o regla para el agente."
            )

        config = get_business_config(tenant_id)
        rule_id = f"rule_{uuid.uuid4().hex[:8]}"
        created_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

        # 1. CASO: Habilitar o Deshabilitar Herramienta
        tool_action_match = cls._detect_tool_permission_instruction(text)
        if tool_action_match:
            tool_name, enable_status, reason = tool_action_match
            config.update_tool_permission(tool_name, enabled=enable_status, disabled_message=reason)
            config.save_to_db()
            action_desc = "habilitada" if enable_status else "deshabilitada"
            return TeachingResult(
                ok=True,
                action_taken="tool_permission_updated",
                summary=f"Herramienta '{tool_name}' {action_desc}",
                structured_data={"tool_name": tool_name, "enabled": enable_status, "reason": reason},
                feedback_for_owner=f"He actualizado los permisos: la herramienta '{tool_name}' ha sido {action_desc}."
            )

        # 2. CASO: Regla Condicional de Negocio ("Cuando X... haz Y")
        cond_match = cls._detect_conditional_rule(text)
        if cond_match:
            trigger_cond, directive = cond_match
            new_rule = StructuredRule(
                id=rule_id,
                category="policy",
                trigger_condition=trigger_cond,
                directive=directive,
                created_at=created_at
            )
            config.add_structured_rule(new_rule)
            
            # Si el usuario además dio un ejemplo de respuesta
            if example_response:
                config.add_behavior_example(BehaviorExample(
                    user_query=trigger_cond,
                    assistant_response=example_response,
                    rationale=directive
                ))

            config.save_to_db()
            return TeachingResult(
                ok=True,
                action_taken="rule_added",
                summary=f"Regla operativa agregada: Cuando {trigger_cond} -> {directive}",
                structured_data=new_rule.to_dict(),
                feedback_for_owner=(
                    f"Entendido. He incorporado la siguiente regla operativa:\n"
                    f"- Condición: Cuando {trigger_cond}\n"
                    f"- Directiva: {directive}"
                )
            )

        # 3. CASO: Actualización de Horarios
        if any(w in text.lower() for w in ["horario", "abrimos", "cerramos", "días de atención", "lunes a"]):
            config.official_info.operating_hours = text
            config.save_to_db()
            return TeachingResult(
                ok=True,
                action_taken="policy_updated",
                summary="Horarios oficiales actualizados",
                structured_data={"operating_hours": text},
                feedback_for_owner=f"He registrado el nuevo horario de atención oficial: {text}"
            )

        # 4. CASO: Actualización de Tono o Identidad
        if any(w in text.lower() for w in ["tono", "habla como", "sé más", "responde de forma", "estilo"]):
            config.identity.tone_and_voice = text
            config.save_to_db()
            return TeachingResult(
                ok=True,
                action_taken="policy_updated",
                summary="Tono de voz actualizado",
                structured_data={"tone_and_voice": text},
                feedback_for_owner=f"He ajustado el tono conversacional del operador a: {text}"
            )

        # 5. CASO GENERAL: Regla de Comportamiento o Conocimiento
        general_rule = StructuredRule(
            id=rule_id,
            category="behavior",
            trigger_condition="consultas relacionadas",
            directive=text,
            created_at=created_at
        )
        config.add_structured_rule(general_rule)
        config.save_to_db()

        return TeachingResult(
            ok=True,
            action_taken="rule_added",
            summary=f"Directriz general registrada: {text[:60]}...",
            structured_data=general_rule.to_dict(),
            feedback_for_owner=f"He aprendido la nueva directriz operativa: '{text}'. La aplicaré en las próximas conversaciones."
        )

    @staticmethod
    def _detect_conditional_rule(text: str) -> Optional[Tuple[str, str]]:
        """Detecta patrones del tipo 'Cuando [condición], [acción]' o 'Si [condición], entonces [acción]'."""
        patterns = [
            r'^(?:cuando|si|al)\s+(?:un\s+|el\s+)?(?:cliente|usuario|visitante)?\s*(.*?)[,;]\s*(?:primero\s+)?(.*)$',
            r'^cuando\s+(.*?)\s+(?:debes|tienes que|procede a|verifica|haz)\s+(.*)$',
            r'^si\s+(.*?)\s+entonces\s+(.*)$'
        ]
        for p in patterns:
            m = re.match(p, text, re.IGNORECASE)
            if m:
                trigger = m.group(1).strip()
                directive = m.group(2).strip()
                return trigger, directive
        return None

    @staticmethod
    def _detect_tool_permission_instruction(text: str) -> Optional[Tuple[str, bool, str]]:
        """Detecta instrucciones para habilitar/deshabilitar herramientas como agendamiento."""
        t = text.lower()
        if "deshabilita" in t or "desactivar" in t or "no permitas" in t or "bloquea" in t:
            if "cita" in t or "reserva" in t or "agendamiento" in t or "agenda" in t:
                return "book_appointment", False, "El agendamiento directo está temporalmente deshabilitado por la dirección."
            if "navegar" in t or "navegacion" in t:
                return "navigate_web", False, "La navegación guiada está desactivada."

        if "habilita" in t or "activar" in t or "permite" in t:
            if "cita" in t or "reserva" in t or "agendamiento" in t or "agenda" in t:
                return "book_appointment", True, ""
            if "navegar" in t or "navegacion" in t:
                return "navigate_web", True, ""

        return None
