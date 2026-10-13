# -*- coding: utf-8 -*-
"""
Firby Platform — Scoped Knowledge Engine
========================================
Gestiona la definición, versionado y recuperación de conocimiento scoped por:
1. TENANT_ID: Aislamiento absoluto entre clientes.
2. AGENT_ID: Partición entre agentes del mismo tenant (e.g. Agente Web vs Agente WhatsApp).
3. SCOPE: 'public' (visible a visitantes web) vs 'private'/'internal' (solo políticas internas).
4. METADATA: Fuente oficial, versión y prioridad de grounding.
"""

from __future__ import annotations
import re
import uuid
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

from src.core.platform.models import KnowledgeItem
from src.core.platform.store import platform_store, PlatformStore
from src.core.operator.business_config import BusinessConfig

log = logging.getLogger("firby.platform.knowledge")


class TenantKnowledgeEngine:
    """Motor de indexación y búsqueda de conocimiento particionado."""

    def __init__(self, store: Optional[PlatformStore] = None):
        self.store = store or platform_store

    def add_document(
        self,
        tenant_id: str,
        agent_id: str,
        title: str,
        content: str,
        source: str = "manual",
        scope: str = "public",
        priority: int = 0,
        doc_id: Optional[str] = None
    ) -> KnowledgeItem:
        """Registra un nuevo fragmento de conocimiento scoped a un tenant y agente."""
        doc = KnowledgeItem(
            doc_id=doc_id or f"kb_{uuid.uuid4().hex[:12]}",
            tenant_id=tenant_id,
            agent_id=agent_id,
            title=title,
            content=content,
            source=source,
            version=1,
            scope=scope,
            priority=priority,
            status="active",
            created_at=datetime.now(timezone.utc).isoformat(),
            updated_at=datetime.now(timezone.utc).isoformat()
        )
        self.store.save_knowledge_item(doc)
        return doc

    def query_knowledge(
        self,
        tenant_id: str,
        agent_id: str = "*",
        query_text: str = "",
        limit: int = 3,
        scope: str = "public"
    ) -> List[KnowledgeItem]:
        """
        Recupera los documentos relevantes garantizando aislamiento server-side.
        Si tenant_id no coincide, SQLite nunca retornará el registro.
        """
        all_items = self.store.get_knowledge_items(tenant_id=tenant_id, agent_id=agent_id, scope=scope)
        if not query_text:
            return all_items[:limit]

        # Ranking léxico ponderado por palabras clave y prioridad
        keywords = [k.lower().strip() for k in re.split(r'\W+', query_text) if len(k) >= 3]
        scored_items = []
        for item in all_items:
            match_score = 0
            text_corpus = f"{item.title} {item.content}".lower()
            for kw in keywords:
                if kw in item.title.lower():
                    match_score += 10
                if kw in text_corpus:
                    match_score += 5
            if match_score > 0 or not keywords:
                total_score = match_score + (item.priority * 2)
                scored_items.append((total_score, item))

        scored_items.sort(key=lambda x: x[0], reverse=True)
        return [item for _, item in scored_items[:limit]]

    def sync_business_config(self, tenant_id: str, agent_id: str, config: BusinessConfig):
        """Sincroniza e indexa la configuración declarativa de negocio en la base de conocimiento."""
        # 1. Información oficial y horarios
        if config.official_info.operating_hours:
            self.add_document(
                tenant_id=tenant_id,
                agent_id=agent_id,
                title="Horarios de Atención y Ubicación",
                content=f"Horarios: {config.official_info.operating_hours}. Ubicación: {', '.join(config.official_info.locations)}.",
                source="business_config.official_info",
                scope="public",
                priority=10,
                doc_id=f"kb_{tenant_id}_{agent_id}_hours"
            )

        # 2. Servicios
        for s in config.services:
            price_txt = f"${s.price_cop:,} COP" if s.price_cop else "A cotizar"
            self.add_document(
                tenant_id=tenant_id,
                agent_id=agent_id,
                title=f"Servicio: {s.name}",
                content=f"{s.description}. Duración aproximada: {s.duration_minutes} min. Precio: {price_txt}.",
                source="business_config.services",
                scope="public",
                priority=8,
                doc_id=f"kb_{tenant_id}_{agent_id}_svc_{s.id}"
            )

        # 3. Políticas
        self.add_document(
            tenant_id=tenant_id,
            agent_id=agent_id,
            title="Políticas Comerciales y Cancelación",
            content=f"Agendamiento: {config.policies.booking_policy}. Cancelación: {config.policies.cancellation_policy}.",
            source="business_config.policies",
            scope="public",
            priority=7,
            doc_id=f"kb_{tenant_id}_{agent_id}_policies"
        )


tenant_knowledge_engine = TenantKnowledgeEngine()
