# -*- coding: utf-8 -*-
"""Core data models extracted from ``src.core.globals``.

Contains Enums, dataclasses and lightweight value objects used across
the Firby codebase.  Re-exported from ``globals.py`` for backward
compatibility.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Any, Dict, List, Optional, Tuple


# ═══════════════════════════════════════════════════════════════════════════════
# TIPOS Y ESTRUCTURAS DE DATOS
# ═══════════════════════════════════════════════════════════════════════════════

class IntentType(Enum):
    """Tipos de intención detectados."""
    GREETING = auto()
    APPOINTMENT_REQUEST = auto()
    APPOINTMENT_CANCEL = auto()
    APPOINTMENT_RESCHEDULE = auto()
    PRICE_INQUIRY = auto()
    SERVICE_INFO = auto()
    LOCATION_INQUIRY = auto()
    HOURS_INQUIRY = auto()
    COMPLAINT = auto()
    COMPLIMENT = auto()
    EMERGENCY = auto()
    GENERAL_QUESTION = auto()
    CHITCHAT = auto()
    CONFIRMATION = auto()
    DENIAL = auto()
    UNCLEAR = auto()

class SentimentType(Enum):
    """Niveles de sentimiento."""
    VERY_NEGATIVE = -2
    NEGATIVE = -1
    NEUTRAL = 0
    POSITIVE = 1
    VERY_POSITIVE = 2

class UrgencyLevel(Enum):
    """Niveles de urgencia."""
    CRITICAL = 5
    HIGH = 4
    MEDIUM = 3
    LOW = 2
    NONE = 1

@dataclass
class MessageAnalysis:
    """Análisis completo de un mensaje."""
    raw_text: str
    cleaned_text: str
    intent: IntentType
    intent_confidence: float
    secondary_intents: List[Tuple[IntentType, float]]
    sentiment: SentimentType
    sentiment_score: float
    urgency: UrgencyLevel
    entities: Dict[str, Any]
    keywords: List[str]
    language: str
    is_question: bool
    requires_action: bool
    requires_search: bool
    emotional_state: str
    context_references: List[str]
    closing_score: float = 0.0      # 0-1: prob de cierre
    lead_temperature: str = "cold"  # cold/warm/hot/boiling

@dataclass
class ConversationState:
    """Estado de una conversación."""
    chat_id: str
    phase: str  # greeting, info_gathering, appointment, closing, etc.
    collected_data: Dict[str, Any]
    pending_questions: List[str]
    last_intent: Optional[IntentType]
    turn_count: int
    satisfaction_score: float
    escalation_needed: bool
    notes: List[str]

@dataclass
class MemoryItem:
    """Item de memoria semántica."""
    id: str
    chat_id: str
    content: str
    embedding: Optional[List[float]]
    category: str
    importance: float
    created_at: datetime
    accessed_count: int
    last_accessed: datetime
    metadata: Dict[str, Any]

@dataclass
class Task:
    """Tarea autónoma."""
    id: str
    type: str
    priority: int
    status: str  # pending, running, completed, failed
    data: Dict[str, Any]
    created_at: datetime
    scheduled_for: Optional[datetime]
    completed_at: Optional[datetime]
    result: Optional[Any]
    retries: int

@dataclass
class MCPPlugin:
    """Plugin MCP (Model Context Protocol)."""
    id: str
    name: str
    description: str
    version: str
    enabled: bool
    config: Dict[str, Any]
    capabilities: List[str]
    endpoints: Dict[str, str]
    health_status: str
    last_check: datetime

@dataclass
class PersonalityProfile:
    """
    Perfil de personalidad de Firby.
    
    Arquetipos disponibles (se aplican con apply_archetype()):
      amigable   — Cercana, tuteo, colombiana real. Default.
      profesional — Usted, cálida pero formal. Clínicas, consultorios.
      luxury     — Elegante, exclusiva, premium. Alto estrato.
      directa    — Mínimo de palabras, máximo de acción. Sin adornos.
      energica   — Entusiasta, positiva, impulsa. Gimnasios, academia.
      empatica   — Escucha profunda, valida antes de proponer. Psicólogos.
      experta    — Técnica, precisa, confiable. Médicos, abogados.
      juvenil    — Informal extrema, cercana a millenials/GenZ. Tattoo, moda.
    """
    name: str = "Firby"
    role: str = "asesora"
    archetype: str = "amigable"   # identificador del arquetipo activo
    tone: str = "natural colombiana"
    formality_level: float = 0.4   # 0=muy informal, 1=muy formal
    warmth_level: float = 0.75     # 0=distante, 1=muy cálida
    humor_level: float = 0.15      # 0=seria, 1=muy humorística
    verbosity: float = 0.35        # 0=muy concisa, 1=muy elaborada
    emoji_usage: float = 0.0       # siempre 0 — nunca emojis

    # Patrones de lenguaje calibrados por arquetipo
    greetings: List[str] = field(default_factory=lambda: [
        "hola", "hola qué tal", "buenas"
    ])
    closings: List[str] = field(default_factory=lambda: [
        "cualquier cosa me escribes", "estoy por aquí", "con gusto"
    ])
    affirmations: List[str] = field(default_factory=lambda: [
        "claro", "sí claro", "dale", "listo"
    ])
    transitions: List[str] = field(default_factory=lambda: [
        "mira", "te cuento", "a ver"
    ])
    forbidden_words: List[str] = field(default_factory=list)
    custom_phrases: Dict[str, str] = field(default_factory=dict)
    situation_responses: Dict[str, str] = field(default_factory=dict)

    # ── Instrucción de tono que se inyecta en el prompt ──────────────────────
    tone_instruction: str = ""
