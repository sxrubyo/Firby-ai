# -*- coding: utf-8 -*-
"""Conversation Intelligence and HyperHuman Engine."""
from __future__ import annotations

import asyncio
import json
import logging
import random
import re
import time
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Tuple

from src.firby.brain.filters import AntiRobotFilter
from src.firby.core.config import Config
from src.firby.core.proxy import GlobalProxy

log = logging.getLogger("firby.intelligence")

# Lazy dynamic attributes to prevent circular imports
db = GlobalProxy("db")
llm_engine = GlobalProxy("llm_engine")
_V9_AVAILABLE = GlobalProxy("_V9_AVAILABLE")
normalize_model_arg = GlobalProxy("normalize_model_arg")
v9_enhance_anti_robot_filter = GlobalProxy("v9_enhance_anti_robot_filter")
init_v9_systems_ref = GlobalProxy("init_v9_systems")
PERSONALITY_ARCHETYPES = GlobalProxy("PERSONALITY_ARCHETYPES")
SKILL_DEFINITIONS = GlobalProxy("SKILL_DEFINITIONS")
V9_PERSONALITY_ARCHETYPES = GlobalProxy("V9_PERSONALITY_ARCHETYPES")
V9_SKILL_DEFINITIONS = GlobalProxy("V9_SKILL_DEFINITIONS")
_parse_admin_ids = GlobalProxy("_parse_admin_ids")

# Global instances (init_v8_systems will initialize/set these, or they can be set globally)
anti_robot_filter: Optional[AntiRobotFilter] = None
conversation_intelligence: Optional[ConversationIntelligence] = None
hyper_human_engine: Optional[HyperHumanEngine] = None
smart_variety: Optional[SmartVariety] = None
conversion_funnel: Optional[ConversionFunnelTracker] = None
multilingual_handler: Optional[MultilingualHandler] = None
persona_evolution: Optional[PersonaEvolution] = None
model_manager: Optional[ModelManager] = None


class ConversationIntelligence:
    """
    Rastreador de estado conversacional por chat_id.
    
    Sabe en qué etapa está cada conversación:
    DISCOVERY → PAIN_EXPLORED → SOLUTION_PRESENTED → COMMITMENT → BOOKED
    
    Esta información se inyecta al prompt para que Firby sepa
    exactamente qué hacer en el siguiente mensaje.
    """

    STAGES = {
        "COLD":               "Cliente nuevo, sin contexto.",
        "DISCOVERY":          "Firby preguntando qué le molesta / qué busca.",
        "PAIN_EXPLORED":      "El cliente compartió su problema real.",
        "SOLUTION_MATCH":     "Firby conectó dolor con solución específica.",
        "OBJECTION_ACTIVE":   "Cliente con objeción activa (precio, miedo, tiempo).",
        "MICRO_COMMITMENT":   "Cliente está considerando la valoración/cita.",
        "BOOKED":             "Cita agendada, confirmación pendiente.",
        "CONFIRMED":          "Cita confirmada por el cliente.",
        "LOST":               "Cliente se fue (sin responder 48h+).",
        "REACTIVATED":        "Cliente inactivo que volvió.",
    }

    EMOTIONAL_STATES = {
        "CURIOUS":      "Interesado, explorando opciones.",
        "ANXIOUS":      "Nervioso, dudas de seguridad o resultado.",
        "SKEPTICAL":    "Desconfiado, ha tenido malas experiencias.",
        "EXCITED":      "Emocionado, listo para decidir.",
        "FRUSTRATED":   "Frustrado por algo que pasó antes.",
        "PRICE_SHOCKED": "Reaccionó mal al precio.",
        "UNDECIDED":    "Tiene la intención pero no el momentum.",
        "NEUTRAL":      "Sin señales emocionales claras.",
    }

    def __init__(self):
        # Almacena estado por chat_id
        # {chat_id: {"stage": str, "emotion": str, "turn": int,
        #            "last_update": float, "signals": list}}
        self._states: Dict[str, Dict] = {}

    def get_state(self, chat_id: str) -> Dict:
        """Retorna el estado actual de la conversación."""
        return self._states.get(chat_id, {
            "stage":   "COLD",
            "emotion": "NEUTRAL",
            "turn":    0,
            "signals": [],
            "commitment_score": 0.0,
            "last_objection": "",
        })

    def update(self, chat_id: str, user_text: str, bot_response: str,
               analysis: Any) -> Dict:
        """
        Actualiza el estado basado en lo que dijo el usuario y respondió Firby.
        Retorna el nuevo estado.
        """
        state = self.get_state(chat_id)
        text_lower = user_text.lower()
        turn = state.get("turn", 0) + 1
        state["turn"] = turn

        # ── Detectar etapa ──────────────────────────────────────────────────────
        # Señales de avance
        PAIN_SIGNALS = [
            "me molesta", "me preocupa", "me incomoda", "ya se me nota",
            "quiero mejorar", "llevo tiempo", "desde hace", "ya me cansé",
            "se me marcan", "siento que", "me veo", "ya no me gusta",
            "quiero hacerme", "necesito", "busco"
        ]
        OBJECTION_SIGNALS = [
            "está caro", "es muy caro", "no tengo plata", "lo voy a pensar",
            "déjame pensarlo", "me da miedo", "qué tal si", "y si quedo",
            "lo consulto", "no sé si", "cuánto tiempo de recuperación",
            "tengo mucho trabajo", "no tengo tiempo", "ya fui a otro lado"
        ]
        COMMITMENT_SIGNALS = [
            "qué día", "cuándo pueden", "me interesa la valoración",
            "me agendas", "cómo agendo", "este jueves", "este viernes",
            "la semana que viene", "puedo ir el", "sí quiero"
        ]
        BOOKED_SIGNALS = [
            "perfecto, ahí estaré", "confirmado", "listo nos vemos",
            "anotado", "ya quedé agendada", "ya quedé"
        ]

        # Actualizar etapa según señales
        if state["stage"] == "COLD" or state["stage"] == "REACTIVATED":
            state["stage"] = "DISCOVERY"

        if any(s in text_lower for s in PAIN_SIGNALS) and state["stage"] in ("DISCOVERY", "COLD"):
            state["stage"] = "PAIN_EXPLORED"

        if state["stage"] == "PAIN_EXPLORED" and turn >= 3:
            state["stage"] = "SOLUTION_MATCH"

        if any(s in text_lower for s in OBJECTION_SIGNALS):
            state["stage"] = "OBJECTION_ACTIVE"
            state["last_objection"] = user_text[:100]

        if any(s in text_lower for s in COMMITMENT_SIGNALS):
            state["stage"] = "MICRO_COMMITMENT"

        if any(s in text_lower for s in BOOKED_SIGNALS):
            state["stage"] = "BOOKED"

        # ── Detectar emoción ────────────────────────────────────────────────────
        if any(w in text_lower for w in ["miedo", "me da miedo", "me preocupa que quede", "qué tal si quedo"]):
            state["emotion"] = "ANXIOUS"
        elif any(w in text_lower for w in ["ya fui", "quedé mal", "otra clínica me hizo", "no funciona"]):
            state["emotion"] = "SKEPTICAL"
        elif any(w in text_lower for w in ["emocionada", "qué bueno", "súper", "me alegra", "por fin"]):
            state["emotion"] = "EXCITED"
        elif any(w in text_lower for w in ["está caro", "costoso", "muy caro", "no tengo"]):
            state["emotion"] = "PRICE_SHOCKED"
        elif any(w in text_lower for w in ["lo pienso", "lo consulto", "después te escribo"]):
            state["emotion"] = "UNDECIDED"
        elif any(w in text_lower for w in ["frustrad", "molest", "qué fastidio", "llevaba"]):
            state["emotion"] = "FRUSTRATED"
        elif any(w in text_lower for w in ["me interesa", "cuánto", "qué incluye", "cuándo"]):
            state["emotion"] = "CURIOUS"

        # ── Score de compromiso (0-1) ───────────────────────────────────────────
        commitment = state.get("commitment_score", 0.0)
        commitment += 0.05 * min(turn, 10)  # cada turno suma un poco
        if state["stage"] in ("MICRO_COMMITMENT", "BOOKED", "CONFIRMED"):
            commitment = min(1.0, commitment + 0.3)
        if state["stage"] == "OBJECTION_ACTIVE":
            commitment = max(0.1, commitment - 0.1)
        state["commitment_score"] = round(min(1.0, commitment), 2)

        state["last_update"] = time.time()
        self._states[chat_id] = state
        return state

    # V8.1 — Señales universales por sector
    SECTOR_PAIN_SIGNALS = {
        "dental": [
            "me duele", "dolor", "me está molestando", "se me cayó",
            "caries", "sensibilidad", "fractura", "muela del juicio",
            "me sangra", "inflamado", "absceso"
        ],
        "veterinaria": [
            "no come", "está decaído", "vomitó", "diarrea", "cojea",
            "tiene algo en", "no se mueve bien", "está raro", "no bebe",
            "tiene fiebre", "está llorando", "no para de rascarse"
        ],
        "restaurante": [
            "cumpleaños", "aniversario", "propuesta", "celebración",
            "quiero sorprender", "evento especial", "graduación"
        ],
        "gimnasio": [
            "llevo tiempo sin", "quiero bajar", "quiero subir", "me cansé",
            "me recomendaron", "quiero empezar", "necesito moverme más",
            "estoy muy sedentario", "doctor me dijo"
        ],
        "psicologo": [
            "ansiedad", "depresión", "estrés", "no puedo dormir",
            "relación", "me siento", "llevo tiempo así", "necesito hablar",
            "me recomendaron", "problemas con", "no sé cómo manejar"
        ],
        "abogado": [
            "me demandaron", "me despidieron", "accidente", "deuda",
            "divorcio", "herencia", "me amenazaron", "robo", "estafa",
            "contrato", "problema con", "me estafaron"
        ],
    }

    SECTOR_OBJECTION_SIGNALS = {
        "dental": [
            "está caro", "le tengo miedo", "me da miedo", "voy a pensar",
            "no tengo tiempo", "se me va a notar", "es que no fui en años"
        ],
        "veterinaria": [
            "está caro", "espero a ver", "voy a esperarlo un poco",
            "no es urgente", "se ve bien"
        ],
        "restaurante": [
            "está caro", "hay descuento", "qué incluye exactamente",
            "tienen menú más económico"
        ],
        "gimnasio": [
            "está caro", "no tengo tiempo", "empiezo el lunes", "voy a pensarlo",
            "primero bajo un poco de peso", "no sé si pueda ir seguido"
        ],
        "psicologo": [
            "está caro", "no creo en eso", "no soy de los que van al psicólogo",
            "ya lo intenté", "puedo solo", "mi familia no va a entender"
        ],
        "tattoo": [
            "está caro", "lo voy a pensar", "voy a seguir buscando",
            "vi uno más barato", "todavía no sé bien qué quiero"
        ],
    }

    def get_sector_signals(self, sector: str) -> dict:
        """Retorna señales de dolor y objeción para el sector."""
        return {
            "pain": self.SECTOR_PAIN_SIGNALS.get(sector, [
                "me molesta", "problema", "necesito", "busco", "quiero"
            ]),
            "objection": self.SECTOR_OBJECTION_SIGNALS.get(sector, [
                "está caro", "lo pienso", "me da miedo", "no tengo tiempo"
            ])
        }

    def update_with_sector(self, chat_id: str, user_text: str,
                            bot_response: str, analysis: Any,
                            sector: str = "") -> dict:
        """
        V8.1 — Actualiza el estado con señales específicas por sector.
        """
        state = self.get_state(chat_id)
        text_lower = user_text.lower()
        turn = state.get("turn", 0) + 1
        state["turn"] = turn

        signals = self.get_sector_signals(sector)
        pain_signals = signals["pain"] + [
            "me molesta", "me preocupa", "quiero mejorar", "necesito",
            "llevo tiempo", "desde hace", "busco", "quiero hacerme"
        ]
        objection_signals = signals["objection"] + [
            "está caro", "lo voy a pensar", "déjame pensarlo",
            "me da miedo", "no tengo tiempo"
        ]
        commitment_signals = [
            "qué día", "cuándo pueden", "me interesa", "me agendas",
            "cómo agendo", "esta semana", "puedo ir", "sí quiero",
            "cuánto de anticipo", "cómo pago"
        ]
        booked_signals = [
            "confirmado", "listo", "anotado", "ya quedé",
            "perfecto ahí estaré", "ya lo agendé"
        ]

        # Actualizar etapa
        if state["stage"] in ("COLD", "REACTIVATED"):
            state["stage"] = "DISCOVERY"

        if any(s in text_lower for s in pain_signals) and state["stage"] in ("DISCOVERY", "COLD"):
            state["stage"] = "PAIN_EXPLORED"

        if state["stage"] == "PAIN_EXPLORED" and turn >= 3:
            state["stage"] = "SOLUTION_MATCH"

        if any(s in text_lower for s in objection_signals):
            state["stage"] = "OBJECTION_ACTIVE"
            state["last_objection"] = user_text[:100]

        if any(s in text_lower for s in commitment_signals):
            state["stage"] = "MICRO_COMMITMENT"

        if any(s in text_lower for s in booked_signals):
            state["stage"] = "BOOKED"

        # Detectar emoción
        if any(w in text_lower for w in ["miedo", "me da miedo", "qué tal si quedo", "me preocupa"]):
            state["emotion"] = "ANXIOUS"
        elif any(w in text_lower for w in ["ya fui", "quedé mal", "no funciona", "no sirvió"]):
            state["emotion"] = "SKEPTICAL"
        elif any(w in text_lower for w in ["emocionad", "qué bueno", "súper", "por fin", "me alegra"]):
            state["emotion"] = "EXCITED"
        elif any(w in text_lower for w in ["está caro", "costoso", "muy caro", "no tengo"]):
            state["emotion"] = "PRICE_SHOCKED"
        elif any(w in text_lower for w in ["lo pienso", "lo consulto", "después", "voy a ver"]):
            state["emotion"] = "UNDECIDED"
        elif any(w in text_lower for w in ["frustrad", "molest", "fastidio", "llevaba tiempo"]):
            state["emotion"] = "FRUSTRATED"
        elif any(w in text_lower for w in ["me interesa", "cuánto", "qué incluye", "cuándo"]):
            state["emotion"] = "CURIOUS"

        # Score de compromiso
        commitment = state.get("commitment_score", 0.0)
        commitment += 0.05 * min(turn, 10)
        if state["stage"] in ("MICRO_COMMITMENT", "BOOKED", "CONFIRMED"):
            commitment = min(1.0, commitment + 0.3)
        if state["stage"] == "OBJECTION_ACTIVE":
            commitment = max(0.1, commitment - 0.1)
        state["commitment_score"] = round(min(1.0, commitment), 2)

        state["last_update"] = time.time()
        state["sector"] = sector
        self._states[chat_id] = state
        return state

    def get_prompt_context(self, chat_id: str) -> str:
        """
        Retorna un bloque de texto para inyectar al sistema prompt.
        Le dice a Firby exactamente en qué punto está la conversación
        y qué debe hacer en el próximo mensaje.
        """
        state = self.get_state(chat_id)
        stage      = state["stage"]
        emotion    = state["emotion"]
        turn       = state["turn"]
        commitment = state["commitment_score"]
        objection  = state.get("last_objection", "")

        # Instrucción específica por etapa
        stage_instructions = {
            "COLD": "Primera interacción. Saludo natural, pregunta abierta sobre qué busca.",
            "DISCOVERY": "Estás descubriendo qué le molesta. NO ofrezcas soluciones aún. Pregunta UNA cosa.",
            "PAIN_EXPLORED": "Ya conoces el dolor. Profundiza un poco más antes de conectar con solución.",
            "SOLUTION_MATCH": "Conecta el dolor que describió con UNA solución específica. Luego propón la valoración.",
            "OBJECTION_ACTIVE": f"Hay una objeción activa: '{objection[:60]}'. Valida primero, LUEGO maneja con la técnica de transferencia al especialista.",
            "MICRO_COMMITMENT": "El cliente está considerando. Propón UN día concreto. No des opciones múltiples.",
            "BOOKED": "Cita agendada. Confirma, da instrucciones simples de qué llevar/esperar.",
            "CONFIRMED": "Confirmado. Cierre natural. Recuérdales el día/hora brevemente.",
            "LOST": "El cliente volvió después de estar inactivo. Saluda como si nada, no menciones el tiempo.",
            "REACTIVATED": "Cliente reactivado. Tono natural de continuación, no de 'oye cuánto tiempo'.",
        }

        emotion_instructions = {
            "ANXIOUS":       "PRIORIDAD: validar el miedo ANTES de cualquier información. 'ese miedo es muy normal aquí'",
            "SKEPTICAL":     "PRIORIDAD: reconocer la mala experiencia. 'ay qué pena, eso no debería pasar' — luego diferenciar.",
            "EXCITED":       "Match su energía. Cierra hacia fecha concreta rápido, está listo.",
            "PRICE_SHOCKED": "No defiendas el precio de frente. 'sí, los buenos no son baratos' — luego habla de valor.",
            "UNDECIDED":     "Descubre QUÉ le frena: '¿qué sería lo que más te detiene, el precio, el resultado o el proceso?'",
            "FRUSTRATED":    "Valida PRIMERO: 'entiendo, eso es frustrante' — NUNCA expliques o justifiques de entrada.",
            "CURIOUS":       "Aprovecha el interés. Responde directo, luego mueve un paso hacia la valoración.",
            "NEUTRAL":       "Tono natural. Descubre su estado emocional con UNA pregunta cálida.",
        }

        # Entregar contexto como una sola frase orientativa — no como lista de instrucciones
        # Menos estructura → el LLM la sigue sin sonar a que está siguiendo una lista
        stage_note = stage_instructions.get(stage, "Continúa naturalmente.")
        emotion_note = emotion_instructions.get(emotion, "") if emotion != "NEUTRAL" else ""

        hint_parts = [stage_note]
        if emotion_note:
            hint_parts.append(emotion_note)

        return " ".join(hint_parts)


class HyperHumanEngine:
    """
    Motor de validación de humanidad.
    
    Antes de enviar cualquier respuesta, la evalúa y si es muy robótica,
    la regenera con instrucciones más precisas.
    
    En V8.0 esto resuelve el problema principal: Firby se sentía
    como un chatbot corporativo; escribe natural y directo.
    """

    def __init__(self, anti_robot: AntiRobotFilter):
        self.filter = anti_robot
        self._retry_count: Dict[str, int] = {}  # chat_id → retries this turn

    def validate(self, response: str, chat_id: str = "") -> Tuple[bool, float, str]:
        """
        Valida si la respuesta es suficientemente humana.
        Retorna (is_valid, score, reason).
        """
        score = self.filter.score_humanness(response)
        threshold = Config.V8_QUALITY_THRESHOLD

        if score >= threshold:
            return True, score, "ok"

        # Identificar por qué falló
        reasons = []
        text_lower = response.lower()

        for phrase in self.filter.FORBIDDEN_EXACT:
            if phrase in text_lower:
                reasons.append(f"frase_bot:'{phrase[:30]}'")
                break

        if len(response.split()) > 50:
            reasons.append("muy_larga")

        if not reasons:
            reasons.append("score_bajo")

        return False, score, ",".join(reasons)

    def get_retry_prompt_injection(self, original_response: str,
                                   reason: str, archetype: str) -> str:
        """
        Genera instrucciones de corrección para la regeneración.
        Se inyectan al prompt de retry.
        """
        lines = [
            f"\n\n⚠️ CORRECCIÓN NECESARIA:",
            f"Tu respuesta anterior fue demasiado robótica. Razón: {reason}",
            f"Respuesta anterior: '{original_response[:80]}...'",
            f"",
            "REGLAS DE CORRECCIÓN:"
        ]

        if "muy_larga" in reason:
            lines.append("→ Máximo 20 palabras en total. Si necesitas más, usa |||")
        if "frase_bot" in reason:
            lines.append("→ Elimina TODA frase de call center. Di lo mismo en palabras simples.")

        lines.extend([
            "→ Natural y directo por WhatsApp — no como chatbot corporativo",
            "→ Una oración directa. Sin introducción. Sin cierre formal.",
            f"→ Arquetipo activo: {archetype}. Usa su vocabulario.",
            "",
            "Escribe de nuevo, más corto y natural:"
        ])

        return "\n".join(lines)


class SmartVariety:
    """
    Evita que Firby repita el mismo patrón de apertura/cierre en cada conversación.
    
    Problema V7: Firby siempre empezaba con "hola qué tal"
    y cerraba con "cuándo puedes". Predecible = robótico.
    
    SmartVariety rastraea los últimos N aperturas y cierres por chat_id
    y fuerza variación natural.
    """

    # Aperturas colombianas reales para diferentes contextos
    OPENINGS_GREETING = [
        "hola", "hola qué más", "buenas", "hola buenas", "hey",
        "hola qué tal", "buenas qué más", "hola!", "qué más",
    ]
    OPENINGS_FOLLOWUP = [
        "", "", "",  # (vacío = sin apertura, responde directo — lo más natural)
        "oye", "mira", "oye mira", "a ver",
    ]
    OPENINGS_AFTER_SILENCE = [
        "hola de nuevo", "hola", "oye", "buenas",
    ]

    # Cierres naturales (propuesta de siguiente paso)
    CLOSINGS_APPOINTMENT = [
        "esta semana tienes el jueves, te queda bien",
        "tengo espacio el jueves en la tarde, te funciona",
        "esta semana hay espacio, cuándo puedes venir",
        "qué día te queda mejor esta semana",
        "el jueves hay espacio, ese día puedes",
        "tenemos cupo esta semana, cuándo te cuadra",
    ]
    CLOSINGS_SOFT = [
        "cualquier cosa me cuentas",
        "estoy por acá",
        "me escribes si tienes más preguntas",
        "si quieres más info me avisas",
    ]
    CLOSINGS_COMMITMENT = [
        "te agendo la valoración, es gratis, cuándo puedes",
        "valoración gratis con la doctora, esta semana puedes",
        "te la agendo ahora mismo, cuándo tienes 20 minutos",
    ]

    def __init__(self):
        # Historial de aperturas y cierres por chat_id
        self._history: Dict[str, Dict[str, list]] = {}

    # V8.1 — Aperturas y cierres específicos por sector
    SECTOR_OPENINGS = {
        "dental": [
            "hola", "buenas", "hola buenas",
            "cuéntame", "buenas tardes",
        ],
        "veterinaria": [
            "hola", "hola buenas", "buenas",
            "cómo están", "cuéntame",
        ],
        "restaurante": [
            "hola", "buenas", "hola buenas",
            "cuéntame", "buenas tardes",
        ],
        "gimnasio": [
            "hola", "hola qué más", "buenas",
            "hola", "qué más",
        ],
        "belleza": [
            "hola", "hola qué más", "hola buenas",
            "buenas", "hola",
        ],
        "tattoo": [
            "hola", "buenas", "hey",
            "qué más", "hola",
        ],
        "psicologo": [
            "hola", "hola qué tal", "buenas",
            "cuéntame", "buenas",
        ],
        "abogado": [
            "buenos días", "buenas tardes", "buenas",
            "cuénteme", "buenos días",
        ],
        "medico": [
            "buenas", "buenas tardes", "buenos días",
            "hola buenas", "buenas",
        ],
    }

    SECTOR_CLOSINGS_APPOINTMENT = {
        "dental": [
            "cuándo puedes venir",
            "esta semana hay espacio, qué día te queda",
            "el doctor tiene turno el jueves, puedes",
            "esta semana tenemos cita, cuándo puedes",
        ],
        "veterinaria": [
            "cuándo pueden traerlo",
            "esta tarde hay espacio, puedes venir",
            "el doctor tiene turno hoy, qué hora te queda",
            "cuándo lo traes",
        ],
        "restaurante": [
            "qué hora les queda mejor",
            "a las 7 o a las 8, cuál les queda",
            "a qué hora les pongo la mesa",
            "a qué hora los esperamos",
        ],
        "gimnasio": [
            "cuándo puedes venir",
            "esta semana hay cupo, cuándo te queda",
            "puedes venir mañana a conocer",
            "arranquemos esta semana, cuándo tienes",
        ],
        "tattoo": [
            "cuándo puedes venir",
            "esta semana tengo el miércoles y el viernes",
            "mándame el diseño y coordinamos fecha",
            "cuándo quieres agendar",
        ],
    }

    def get_sector_opening(self, sector: str = "") -> str:
        """Retorna apertura apropiada para el sector."""
        pool = self.SECTOR_OPENINGS.get(sector, self.OPENINGS_GREETING)
        return pool[hash(str(time.time())) % len(pool)]

    def get_sector_closing(self, sector: str = "", context: str = "appointment") -> str:
        """Retorna cierre apropiado para el sector."""
        if context == "appointment":
            pool = self.SECTOR_CLOSINGS_APPOINTMENT.get(sector, self.CLOSINGS_APPOINTMENT)
        else:
            pool = self.CLOSINGS_SOFT
        return pool[hash(str(time.time())) % len(pool)]

    def get_opening(self, chat_id: str, context: str = "greeting") -> str:
        """Retorna una apertura que no se ha usado recientemente."""
        pool = {
            "greeting":        self.OPENINGS_GREETING,
            "followup":        self.OPENINGS_FOLLOWUP,
            "after_silence":   self.OPENINGS_AFTER_SILENCE,
        }.get(context, self.OPENINGS_GREETING)

        used = self._history.get(chat_id, {}).get("openings", [])
        available = [o for o in pool if o not in used[-3:]]
        if not available:
            available = pool

        choice = random.choice(available)
        self._track(chat_id, "openings", choice)
        return choice

    def get_closing(self, chat_id: str, style: str = "soft") -> str:
        """Retorna un cierre que no se ha usado recientemente."""
        pool = {
            "appointment": self.CLOSINGS_APPOINTMENT,
            "soft":        self.CLOSINGS_SOFT,
            "commitment":  self.CLOSINGS_COMMITMENT,
        }.get(style, self.CLOSINGS_SOFT)

        used = self._history.get(chat_id, {}).get("closings", [])
        available = [c for c in pool if c not in used[-3:]]
        if not available:
            available = pool

        choice = random.choice(available)
        self._track(chat_id, "closings", choice)
        return choice

    def get_variety_instruction(self, chat_id: str) -> str:
        """
        Contexto de variedad — fraseado como dato, no como orden.
        Research: el modelo respeta más "ya usé X" que "no uses X".
        """
        history = self._history.get(chat_id, {})
        last_openings = [o for o in history.get("openings", [])[-3:] if o]
        last_closings  = [c for c in history.get("closings", [])[-2:]  if c]

        lines = []
        if last_openings:
            used = ", ".join(f'"{o}"' for o in last_openings)
            lines.append(f"en esta conversación ya abriste con {used} — varía")
        if last_closings:
            used = ", ".join(f'"{c}"' for o in last_closings)
            lines.append(f"ya cerraste con {used} — usa algo diferente")

        return "\n".join(lines)

    def _track(self, chat_id: str, category: str, value: str):
        if chat_id not in self._history:
            self._history[chat_id] = {}
        if category not in self._history[chat_id]:
            self._history[chat_id][category] = []
        self._history[chat_id][category].append(value)
        # Mantener solo últimas 10
        self._history[chat_id][category] = self._history[chat_id][category][-10:]


class ConversionFunnelTracker:
    """
    Rastreador de embudo de conversión.
    
    Sabe cuántos leads hay en cada etapa y qué tan efectiva es Firby
    en mover leads de una etapa a la siguiente.
    
    Se usa para el reporte /pipeline del admin y para entrenar
    la auto-mejora de Firby.
    """

    FUNNEL_STAGES = [
        "cold", "discovery", "pain_explored",
        "solution_match", "objection_active",
        "micro_commitment", "booked", "confirmed"
    ]

    def __init__(self):
        self._events: list = []  # Lista de eventos para análisis

    def record(self, chat_id: str, from_stage: str, to_stage: str,
               triggered_by: str = ""):
        """Registra una transición de etapa."""
        self._events.append({
            "chat_id":     chat_id,
            "from":        from_stage,
            "to":          to_stage,
            "triggered":   triggered_by,
            "ts":          time.time(),
        })
        # También persistir en DB si está disponible
        try:
            if db:
                db.remember(
                    f"funnel_{chat_id}",
                    json.dumps({"stage": to_stage, "ts": datetime.now().isoformat()}),
                    category="funnel"
                )
        except Exception:
            pass

    def get_pipeline_summary(self) -> Dict[str, int]:
        """Retorna conteo de leads por etapa (último mes)."""
        summary = {s: 0 for s in self.FUNNEL_STAGES}
        try:
            if db:
                memories = db.recall_all(category="funnel")
                for key, value in memories.items():
                    try:
                        data = json.loads(value)
                        stage = data.get("stage", "cold").lower()
                        if stage in summary:
                            summary[stage] += 1
                    except Exception:
                        pass
        except Exception:
            pass
        return summary

    def get_conversion_rate(self) -> Dict[str, float]:
        """Calcula tasa de conversión entre etapas."""
        rates = {}
        cutoff = time.time() - (30 * 24 * 3600)  # últimos 30 días
        recent = [e for e in self._events if e["ts"] > cutoff]

        stage_counts: Dict[str, int] = {}
        for e in recent:
            stage_counts[e["from"]] = stage_counts.get(e["from"], 0) + 1

        stage_successes: Dict[str, int] = {}
        for e in recent:
            idx_from = self.FUNNEL_STAGES.index(e["from"]) if e["from"] in self.FUNNEL_STAGES else -1
            idx_to   = self.FUNNEL_STAGES.index(e["to"])   if e["to"]   in self.FUNNEL_STAGES else -1
            if idx_to > idx_from >= 0:
                stage_successes[e["from"]] = stage_successes.get(e["from"], 0) + 1

        for stage in self.FUNNEL_STAGES:
            total   = stage_counts.get(stage, 0)
            success = stage_successes.get(stage, 0)
            rates[stage] = round(success / total, 2) if total > 0 else 0.0

        return rates

    def format_pipeline_report(self) -> str:
        """Genera texto del reporte de pipeline para el admin."""
        summary = self.get_pipeline_summary()
        rates   = self.get_conversion_rate()

        lines = ["Pipeline de leads:"]
        stage_names = {
            "cold":             "🧊 Fríos",
            "discovery":        "🔍 Descubrimiento",
            "pain_explored":    "💬 Dolor explorado",
            "solution_match":   "✅ Solución presentada",
            "objection_active": "🚧 Con objeción",
            "micro_commitment": "🎯 Casi listos",
            "booked":           "📅 Agendados",
            "confirmed":        "✔️  Confirmados",
        }
        for stage in self.FUNNEL_STAGES:
            count = summary.get(stage, 0)
            rate  = rates.get(stage, 0.0)
            name  = stage_names.get(stage, stage)
            rate_str = f" → {int(rate*100)}% avanzan" if rate > 0 else ""
            lines.append(f"  {name}: {count} leads{rate_str}")

        total = sum(summary.values())
        booked = summary.get("booked", 0) + summary.get("confirmed", 0)
        global_rate = round(booked / total * 100, 1) if total > 0 else 0
        lines.append(f"\nConversión global: {global_rate}% ({booked}/{total})")
        return "\n".join(lines)


class MultilingualHandler:
    """
    Maneja inglés, español y portugués de forma transparente.
    
    Detecta el idioma del cliente y ajusta Firby automáticamente.
    No solo traduce — adapta el tono completo al contexto cultural.
    """

    LANGUAGE_PROFILES = {
        "en": {
            "name": "English",
            "tone_note": "Client is writing in English. Respond entirely in English. Use a natural, warm tone. Avoid sounding like a bot. Use casual American/Latin phrasing. If the user uses slang, mirror it subtly.",
            "greetings": ["hey", "hi", "hello", "hi there", "how's it going?"],
            "closings": ["let me know", "happy to help", "have a great day"],
            "yes_words": ["yes", "yep", "sure", "ok", "okay", "sounds good", "perfect"],
        },
        "es": {
            "name": "Español",
            "tone_note": "Cliente en español. Mantén el trato cálido y humano. Evita sonar como un call center. Usa frases cortas y directas.",
            "greetings": ["hola", "buenas", "qué tal?", "hola!", "un gusto"],
            "closings": ["quedo atenta", "cualquier duda me dices", "un saludo"],
            "yes_words": ["sí", "si", "dale", "claro", "ok", "perfecto"],
        },
        "pt": {
            "name": "Português",
            "tone_note": "Cliente em português. Responda em português brasileiro (PT-BR). Use um tom amigável e casual. Evite formalidades excessivas. Sinta-se como uma pessoa real no WhatsApp.",
            "greetings": ["oi", "olá", "tudo bem?", "bom dia", "boa tarde"],
            "closings": ["estou aqui se precisar", "qualquer coisa me chama", "um abraço"],
            "yes_words": ["sim", "ok", "claro", "com certeza", "perfeito"],
        },
    }

    def detect(self, text: str) -> str:
        """Detecta idioma con heurísticas y fallback al LLM si es necesario."""
        text_lower = text.lower().strip()
        if not text_lower: return "es"

        words = set(re.findall(r"\b\w+\b", text_lower))

        EN_INDICATORS = ["the ", "and ", "with ", "you ", "what ", "how ", "hello", "thanks", "please", "can i", "i want", "i need", "do you", "is it", "are you", "how much", "when can", "today", "tomorrow", "appointment"]
        PT_INDICATORS = ["você", "boa ", "obrigad", "tudo bem", "gostaria", "preciso", "pode", "tem ", "qual ", "quero", "agendar", "horário", "amanhã", "obrigado", "obrigada"]
        ES_INDICATORS = ["hola", "buenas", "qué", "cómo", "cuándo", "gracias", "tengo", "quiero", "necesito", "cuánto", "pueden", "cita", "horario", "mañana", "ayer", "hacer", "podemos", "haces", "hacerla", "hey", "heyy"]

        en_score = sum(1 for i in EN_INDICATORS if (i in text_lower if " " in i else i in words))
        pt_score = sum(1 for i in PT_INDICATORS if (i in text_lower if " " in i else i in words))
        es_score = sum(1 for i in ES_INDICATORS if (i in text_lower if " " in i else i in words))

        # Saludos cortos tipo "hey", "heyy", "hi", "ok" en contexto latino se quedan en español
        if len(words) <= 3 and not any(k in text_lower for k in ["english", "speak", "translate", "how much", "appointment"]):
            return "es"

        if en_score > es_score and en_score > pt_score:
            return "en"
        if pt_score > es_score and pt_score > en_score:
            return "pt"
        return "es"

    def get_tone_instruction(self, lang: str) -> str:
        profile = self.LANGUAGE_PROFILES.get(lang, self.LANGUAGE_PROFILES["es"])
        return profile["tone_note"]

    def get_tone_injection(self, lang: str) -> str:
        """Retorna instrucción de idioma para el system prompt."""
        profile = self.LANGUAGE_PROFILES.get(lang, self.LANGUAGE_PROFILES["es"])
        return profile.get("tone_note", "")


class PersonaEvolution:
    """
    Aprende el estilo de escritura de cada cliente y adapta Firby.
    
    Si el cliente escribe muy corto → Firby responde corto.
    Si escribe formal → Firby ajusta formalidad.
    Si usa emojis → Firby puede usarlos.
    Si escribe en inglés → Firby responde en inglés.
    
    Esta adaptación hace que la conversación se sientan personalizada,
    no genérica.
    """

    def __init__(self):
        self._profiles: Dict[str, Dict] = {}  # chat_id → style profile

    def learn(self, chat_id: str, messages: List[Dict]):
        """Analiza los mensajes del usuario y actualiza su perfil."""
        user_msgs = [m["content"] for m in messages if m["role"] == "user"]
        if not user_msgs:
            return

        # Calcular métricas de estilo
        avg_len    = sum(len(m.split()) for m in user_msgs) / len(user_msgs)
        emoji_use  = sum(1 for m in user_msgs
                        if re.search(r'[\U0001F600-\U0001F64F]', m)) / len(user_msgs)
        formal_words = ["usted", "señor", "señora", "estimado", "buenos días"]
        formality  = sum(1 for m in user_msgs
                        for w in formal_words if w in m.lower()) / len(user_msgs)

        profile = {
            "avg_msg_len":   round(avg_len, 1),
            "emoji_rate":    round(emoji_use, 2),
            "formality":     round(formality, 2),
            "msg_count":     len(user_msgs),
            "updated_at":    time.time(),
        }
        self._profiles[chat_id] = profile

    def get_adaptation_note(self, chat_id: str) -> str:
        """Retorna nota de adaptación para el system prompt."""
        profile = self._profiles.get(chat_id)
        if not profile or profile.get("msg_count", 0) < 3:
            return ""

        notes = []
        avg_len = profile.get("avg_msg_len", 10)
        emoji_rate = profile.get("emoji_rate", 0)
        formality = profile.get("formality", 0)

        if avg_len < 5:
            notes.append("Cliente escribe muy corto. Responde aún más corto que lo normal.")
        elif avg_len > 25:
            notes.append("Cliente escribe largo. Puedes ser un poco más elaborada.")

        if emoji_rate > 0.5:
            notes.append("Cliente usa muchos emojis. Puedes usar 1 emoji por burbuja si es natural.")

        if formality > 0.3:
            notes.append("Cliente usa lenguaje formal. Sube levemente tu formalidad.")

        if not notes:
            return ""

        return "ADAPTACIÓN A ESTE CLIENTE:\n" + "\n".join(f"  • {n}" for n in notes)


class ModelManager:
    """
    Gestor de modelos LLM en tiempo real.
    
    Permite al admin cambiar el modelo sin reiniciar.
    Guarda la configuración en DB para que persista.
    
    V8 — el admin puede hacer:
      /modelo                     → ver modelo actual y opciones
      /modelo claude-sonnet        → cambiar a Claude Sonnet
      /modelo gemini-flash         → cambiar a Gemini Flash
      /modelo llama-70b            → cambiar a Llama 70B
      /modelo reset               → volver al modelo del .env
    """

    def __init__(self):
        self._current_overrides: Dict[str, str] = {}  # tier → model_id

    def apply_override(self, tier: str, model_id: str):
        """Aplica un override de modelo en memoria."""
        self._current_overrides[tier] = model_id

    def clear_overrides(self):
        """Limpia todos los overrides (vuelve al .env)."""
        self._current_overrides.clear()

    def get_effective_models(self) -> Dict[str, str]:
        """Retorna el mapa tier → model_id efectivo (con overrides)."""
        base = dict(Config.LLM_MODELS)
        base.update(self._current_overrides)
        return base

    def get_current_model_display(self) -> str:
        """Retorna string formateado con el modelo actual."""
        effective = self.get_effective_models()
        overrides = self._current_overrides

        lines = ["Modelos activos:"]
        for tier, model in effective.items():
            override_mark = " ← cambiado" if tier in overrides else " (por defecto)"
            lines.append(f"  {tier}: {model}{override_mark}")
        return "\n".join(lines)

    def get_catalog_display(self) -> str:
        """Retorna el catálogo de modelos disponibles para mostrar al admin."""
        lines = ["Modelos disponibles para cambiar:\n"]
        current_fast = self.get_effective_models().get("fast", "")

        for key, (model_id, tier, desc) in Config.V8_MODEL_CATALOG.items():
            active = " ← ACTIVO" if model_id == current_fast else ""
            lines.append(f"  /modelo {key} — {desc}{active}")

        lines.append("\nTambién puedes escribir el ID completo:")
        lines.append("  /modelo anthropic/claude-sonnet-4")
        lines.append("\nPara volver al modelo original:")
        lines.append("  /modelo reset")
        return "\n".join(lines)

    def set_model_from_command(self, arg: str) -> Tuple[bool, str]:
        """
        Procesa el argumento de /modelo y aplica el cambio.
        Retorna (success, mensaje).
        """
        arg = normalize_model_arg(arg)

        if arg == "reset":
            self.clear_overrides()
            if db:
                db.remember("v8_model_override", "", "config")
            return True, "Modelos restaurados a los valores del .env."

        # Buscar en catálogo por alias
        if arg in Config.V8_MODEL_CATALOG:
            model_id, tier, desc = Config.V8_MODEL_CATALOG[arg]
            self.apply_override(tier, model_id)
            self.apply_override("fast", model_id)  # fast también
            if tier == "reasoning":
                self.apply_override("reasoning", model_id)
            # Persistir
            if db:
                db.remember("v8_model_override",
                             json.dumps({"tier": tier, "model": model_id, "alias": arg}),
                             "config")
            # También aplicar en llm_engine si está disponible
            self._push_to_engine(tier, model_id)
            return True, f"Modelo cambiado a: {model_id}\n{desc}"

        # Buscar por ID completo (ej: "anthropic/claude-opus-4")
        if "/" in arg:
            model_id = arg
            # Determinar tier por heurística
            tier = "fast"
            if any(x in arg for x in ["opus", "pro", "gpt-4o ", "mistral-large"]):
                tier = "reasoning"
            elif any(x in arg for x in ["lite", "mini", "8b", "flash-lite"]):
                tier = "lite"
            self.apply_override("fast", model_id)
            self.apply_override(tier, model_id)
            self._push_to_engine(tier, model_id)
            if db:
                db.remember("v8_model_override",
                             json.dumps({"tier": tier, "model": model_id}),
                             "config")
            return True, f"Modelo cambiado a: {model_id}"

        return False, (f"No reconozco '{arg}'. Escribe /modelo para ver opciones.")

    def _push_to_engine(self, tier: str, model_id: str):
        """
        Empuja el override al LLM engine en memoria.
        """
        try:
            if not llm_engine:
                return
            applied_to = []
            for provider in llm_engine.providers:
                if not hasattr(provider, "MDLS"):
                    continue
                # Solo OpenRouter puede usar model_ids externos
                if provider.name == "openrouter":
                    provider.MDLS[tier]   = model_id
                    provider.MDLS["fast"] = model_id
                    if tier == "reasoning":
                        provider.MDLS["reasoning"] = model_id
                    applied_to.append(provider.name)
            if applied_to:
                log.info(f"[model_manager] override aplicado en: {applied_to} → {model_id}")
            else:
                log.info(f"[model_manager] override guardado en config, OpenRouter no disponible — usando cascada nativa")
        except Exception as e:
            log.warning(f"[model_manager] _push_to_engine error: {e}")

    def restore_from_db(self):
        """Restaura overrides guardados en DB al arrancar."""
        try:
            if not db:
                return

            # GOD MODE: Revisar tabla system_config primero
            try:
                with db._conn() as c:
                    active_id_row = c.execute("SELECT value FROM system_config WHERE key='active_model'").fetchone()
                    if active_id_row:
                        active_id = active_id_row[0]
                        # Buscar detalles del modelo
                        model_row = c.execute("SELECT * FROM models WHERE id=? AND is_active=1", (active_id,)).fetchone()
                        if model_row:
                            provider = model_row['provider']  # ej: "anthropic"
                            model_id = model_row['model_id']  # ej: "claude-3-opus-20240229"
                            
                            log.info(f"[GOD MODE] Activando modelo dinámico: {active_id} ({provider}/{model_id})")
                            
                            # Aplicar a todos los tiers por simplicidad en God Mode
                            self.apply_override("reasoning", f"{provider}/{model_id}")
                            self.apply_override("fast", f"{provider}/{model_id}")
                            self.apply_override("lite", f"{provider}/{model_id}")
                            self._push_to_engine("fast", f"{provider}/{model_id}")
                            return
            except Exception as e:
                log.warning(f"[GOD MODE] Error leyendo config dinámica: {e}")

            # Fallback legacy
            raw = db.recall("v8_model_override")
            if not raw:
                return
            data = json.loads(raw)
            if data.get("model"):
                tier     = data.get("tier", "fast")
                model_id = data["model"]
                self.apply_override(tier, model_id)
                self.apply_override("fast", model_id)
                self._push_to_engine(tier, model_id)
                log.info(f"[model_manager] modelo restaurado desde DB: {model_id}")
        except Exception as e:
            log.warning(f"[model_manager] error restaurando modelo: {e}")


def init_v8_systems():
    """
    Inicializa todos los sistemas core de V8.0.
    Cada sistema es independiente — un fallo no para al resto.
    """
    import src.core.globals as g

    _ok = 0

    try:
        g.anti_robot_filter = AntiRobotFilter(level=Config.V8_FILTER_LEVEL)
        global anti_robot_filter
        anti_robot_filter = g.anti_robot_filter
        _ok += 1
    except Exception as _e:
        log.warning(f"[v8] AntiRobotFilter: {_e}")

    try:
        g.conversation_intelligence = ConversationIntelligence()
        global conversation_intelligence
        conversation_intelligence = g.conversation_intelligence
        _ok += 1
    except Exception as _e:
        log.warning(f"[v8] ConversationIntelligence: {_e}")

    try:
        g.hyper_human_engine = HyperHumanEngine(g.anti_robot_filter) if g.anti_robot_filter else None
        global hyper_human_engine
        hyper_human_engine = g.hyper_human_engine
        if g.hyper_human_engine:
            _ok += 1
    except Exception as _e:
        log.warning(f"[v8] HyperHumanEngine: {_e}")

    try:
        g.smart_variety = SmartVariety()
        global smart_variety
        smart_variety = g.smart_variety
        _ok += 1
    except Exception as _e:
        log.warning(f"[v8] SmartVariety: {_e}")

    try:
        g.conversion_funnel = ConversionFunnelTracker()
        global conversion_funnel
        conversion_funnel = g.conversion_funnel
        _ok += 1
    except Exception as _e:
        log.warning(f"[v8] ConversionFunnelTracker: {_e}")

    try:
        g.multilingual_handler = MultilingualHandler()
        global multilingual_handler
        multilingual_handler = g.multilingual_handler
        _ok += 1
    except Exception as _e:
        log.warning(f"[v8] MultilingualHandler: {_e}")

    try:
        g.persona_evolution = PersonaEvolution()
        global persona_evolution
        persona_evolution = g.persona_evolution
        _ok += 1
    except Exception as _e:
        log.warning(f"[v8] PersonaEvolution: {_e}")

    try:
        g.model_manager = ModelManager()
        g.model_manager.restore_from_db()
        global model_manager
        model_manager = g.model_manager
        _ok += 1
    except Exception as _e:
        log.warning(f"[v8] ModelManager: {_e}")

    log.info(f"═══ V8.0 CORE SYSTEMS: {_ok}/8 OK ═══")
    log.info(f"  AntiRobotFilter: {'OK' if g.anti_robot_filter else 'FAILED'}")
    log.info(f"  ModelManager:    {'OK' if g.model_manager else 'FAILED'}")

    # V9 HUMANIZATION — Inicializar sistemas de humanización
    if g._V9_AVAILABLE:
        try:
            init_v9_systems_ref()
            # Parchar arquetipos y skills con V9
            g.PERSONALITY_ARCHETYPES.update(g.V9_PERSONALITY_ARCHETYPES)
            g.SKILL_DEFINITIONS.update(g.V9_SKILL_DEFINITIONS)
            # Mejorar AntiRobotFilter con patrones V9
            if g.anti_robot_filter:
                v9_enhance_anti_robot_filter(g.anti_robot_filter)
            log.info("═══ V9 HUMANIZATION: OK ═══")
        except Exception as _v9_e:
            log.warning(f"V9 init parcial: {_v9_e}")
