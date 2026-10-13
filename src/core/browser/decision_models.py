# -*- coding: utf-8 -*-
"""
Firby Browser Decision Engine Models
====================================
Contratos tipados para el motor de decisiones rápidas (System 1)
inspirado en la arquitectura de browser-use/jev-ultrafast y NandhaKishorM/laya.
Prohíbe la generación de código arbitrario y restringe las operaciones a un espacio finito.
"""
from __future__ import annotations

import time
import uuid
from enum import Enum
from typing import Dict, Any, List, Optional, Union
from pydantic import BaseModel, Field


class BrowserOperation(str, Enum):
    """Acciones atómicas permitidas en el navegador (espacio finito indexado)."""
    CLICK = "CLICK"
    TYPE_TEXT = "TYPE_TEXT"
    SELECT = "SELECT"
    SCROLL_SLOW = "SCROLL_SLOW"
    SCROLL_UP = "SCROLL_UP"
    SCROLL_DOWN = "SCROLL_DOWN"
    HIGHLIGHT = "HIGHLIGHT"
    STRIKE_TEXT = "STRIKE_TEXT"
    WAIT = "WAIT"
    DONE = "DONE"
    BLOCKED = "BLOCKED"


class ObservedElement(BaseModel):
    """Elemento interactivo observado y numerado en el DOM."""
    index: int = Field(..., description="Índice numérico asignado [1], [2], [3]...")
    tag: str = Field(..., description="Etiqueta HTML (button, input, a, select, etc.)")
    role: Optional[str] = Field(None, description="Rol ARIA del elemento")
    text: str = Field("", description="Texto visible, placeholder o aria-label")
    element_type: Optional[str] = Field(None, description="Tipo de input si aplica")
    selector: Optional[str] = Field(None, description="Selector CSS o data-firby-index")
    href: Optional[str] = Field(None, description="Enlace de destino si es un tag <a>")
    value: Optional[str] = Field(None, description="Valor actual del campo")
    is_interactive: bool = Field(True, description="Si es clickeable o editable")

    def to_display_string(self) -> str:
        """Formato compacto para el estado de decisión: [1] <button text='Comenzar'>"""
        details = []
        if self.text:
            clean_text = self.text.replace("\n", " ").strip()[:80]
            details.append(f"text='{clean_text}'")
        if self.element_type:
            details.append(f"type='{self.element_type}'")
        if self.role and self.role != self.tag:
            details.append(f"role='{self.role}'")
        if self.value:
            details.append(f"value='{self.value[:40]}'")
        details_str = (" " + " ".join(details)) if details else ""
        return f"[{self.index}] <{self.tag}{details_str}>"


class DecisionRequest(BaseModel):
    """Petición enviada al Decision Engine (compatible con /v1/systemone)."""
    goal: str = Field(..., description="Objetivo específico de la interacción")
    current_url: str = Field(..., description="URL actual de la página")
    elements: List[ObservedElement] = Field(default_factory=list, description="Tabla de elementos observados")
    history: List[Dict[str, Any]] = Field(default_factory=list, description="Historial reciente de micro-acciones")
    state_fingerprint: Optional[str] = Field(None, description="Hash/huella del estado del DOM para evitar stale page")


class DecisionAnswer(BaseModel):
    """Decisión estructurada devuelta por el Decision Engine."""
    operation: BrowserOperation = Field(..., description="Operación atómica elegida")
    target: Optional[int] = Field(None, description="Índice del elemento objetivo [1..N]")
    target_selector: Optional[str] = Field(None, description="Selector resuelto (data-firby-index)")
    text_to_type: Optional[str] = Field(None, description="Texto a escribir si operation == TYPE_TEXT")
    select_value: Optional[str] = Field(None, description="Opción a seleccionar si operation == SELECT")
    scroll_target: Optional[Union[int, str]] = Field(None, description="Elemento hacia donde scrollear lentamente")
    strike_keyword: Optional[str] = Field(None, description="Palabra clave a tachar o enmarcar si aplica")
    confidence: float = Field(1.0, description="Nivel de certidumbre (0.0 a 1.0)")
    latency_ms: float = Field(0.0, description="Tiempo de inferencia en milisegundos")
    requires_human_escalation: bool = Field(False, description="Si la confianza es baja o el estado es BLOCKED")
    reasoning_summary: Optional[str] = Field(None, description="Resumen breve de la micro-decisión (1 línea)")


class DecisionResponse(BaseModel):
    """Respuesta completa compatible con el protocolo wire de Jev / Laya."""
    model: str = Field("firby-decision-systemone-v1")
    id: str = Field(default_factory=lambda: f"dec_{uuid.uuid4().hex[:10]}")
    answers: Dict[str, Any] = Field(default_factory=dict)
    decision: DecisionAnswer
    usage: Dict[str, int] = Field(default_factory=lambda: {"input_tokens": 0, "output_tokens": 0})
    created_at: str = Field(default_factory=lambda: time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
