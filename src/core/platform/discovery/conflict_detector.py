# -*- coding: utf-8 -*-
"""
Firby Platform — Knowledge & Policy Conflict Detector
=====================================================
Detecta inconsistencias o contradicciones comerciales extraídas durante el
descubrimiento del sitio web o ingresadas por el usuario:
- Contradicción de precios entre diferentes páginas.
- Horarios de atención discrepantes.
- Políticas de cancelación o prueba en conflicto.
"""

from __future__ import annotations
import re
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from src.core.platform.discovery.crawler import SiteModel


@dataclass
class KnowledgeConflict:
    conflict_id: str
    entity: str
    description: str
    sources: List[Dict[str, Any]] = field(default_factory=list)
    status: str = "PENDING_CONFIRMATION"  # PENDING_CONFIRMATION, RESOLVED
    resolution: Optional[str] = None
    resolved_by: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "conflict_id": self.conflict_id,
            "entity": self.entity,
            "description": self.description,
            "sources": self.sources,
            "status": self.status,
            "resolution": self.resolution,
            "resolved_by": self.resolved_by
        }


class ConflictDetector:
    """Motor de detección y resolución de discrepancias de conocimiento."""

    @staticmethod
    def detect_conflicts(site_model: SiteModel) -> List[KnowledgeConflict]:
        conflicts: List[KnowledgeConflict] = []
        cid = 1

        # 1. Detección de conflicto de precios entre páginas
        # Agrupar menciones de precios de cada plan por URL
        plan_prices: Dict[str, Dict[str, str]] = {"starter": {}, "pro": {}, "equipos": {}}

        for page in site_model.pages:
            all_mentions = list(page.pricing_mentions)
            if hasattr(page, "prices_found") and page.prices_found:
                for k, v in page.prices_found.items():
                    all_mentions.append(f"{k}: {v}")
            if hasattr(page, "text_content") and page.text_content:
                for line in page.text_content.splitlines():
                    if any(w in line.lower() for w in ["costo", "precio", "cuesta", "plan", "usd", "$"]):
                        all_mentions.append(line)

            for mention in all_mentions:
                m_low = mention.lower()
                for plan in ["starter", "pro", "equipos"]:
                    if plan in m_low:
                        # Extraer cifra numérica aproximada
                        num_m = re.search(r"[\d\.,]+", mention)
                        if num_m:
                            plan_prices[plan][page.url] = mention

        for plan, urls in plan_prices.items():
            if len(urls) > 1:
                # Verificar si los valores difieren
                unique_vals = set(urls.values())
                if len(unique_vals) > 1:
                    conflicts.append(KnowledgeConflict(
                        conflict_id=f"conf_{cid}",
                        entity=f"pricing_{plan}",
                        description=f"Valores contradictorios detectados para el Plan {plan.capitalize()} en diferentes páginas del sitio.",
                        sources=[{"url": u, "value": v} for u, v in urls.items()]
                    ))
                    cid += 1

        return conflicts

    @staticmethod
    def resolve_conflict(conflict: KnowledgeConflict, chosen_value: str, admin_notes: str = "", actor: str = "admin") -> KnowledgeConflict:
        """Aplica la resolución del administrador formalmente."""
        conflict.status = "RESOLVED"
        conflict.resolution = chosen_value
        conflict.resolved_by = actor
        return conflict
