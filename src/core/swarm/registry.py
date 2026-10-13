# -*- coding: utf-8 -*-
"""
Firby Swarm Agent Registry
==========================
Catálogo centralizado de agentes autónomos y workers.
Diseñado para escalar a cientos de agentes interactivos y especializados por tenant.
Permite búsqueda por capacidad (capabilities), aislamiento multi-tenant y registro dinámico en SQLite.
"""

from __future__ import annotations
import json
import logging
import sqlite3
from typing import Dict, Any, List, Optional, Callable
from src.core.swarm.types import AgentMetadata, AgentDomain

log = logging.getLogger("firby.swarm.registry")


class SwarmAgent:
    """Instancia ejecutable de un agente dentro de la red."""

    def __init__(
        self,
        id: str,
        name: str,
        system_prompt: str,
        domain: AgentDomain = AgentDomain.CORE,
        description: str = "",
        capabilities: Optional[List[str]] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        tool_handlers: Optional[Dict[str, Callable]] = None,
        allowed_handoffs: Optional[List[str]] = None,
        is_conversational: bool = True,
        org_id: Optional[str] = None
    ):
        self.id = id
        self.name = name
        self.system_prompt = system_prompt
        self.domain = domain
        self.description = description
        self.capabilities = capabilities or []
        self.tools = tools or []
        self.tool_handlers = tool_handlers or {}
        self.allowed_handoffs = allowed_handoffs or ["*"]
        self.is_conversational = is_conversational
        self.org_id = org_id

    def add_tool(self, tool_def: Dict[str, Any], handler: Callable):
        self.tools.append(tool_def)
        self.tool_handlers[tool_def["function"]["name"]] = handler

    def to_metadata(self) -> AgentMetadata:
        return AgentMetadata(
            id=self.id,
            name=self.name,
            domain=self.domain,
            description=self.description,
            capabilities=self.capabilities,
            system_prompt=self.system_prompt,
            tools=[t["function"]["name"] for t in self.tools if "function" in t],
            allowed_handoffs=self.allowed_handoffs,
            is_conversational=self.is_conversational,
            org_id=self.org_id
        )


class SwarmRegistry:
    """Registro unificado capaz de gestionar cientos de micro-agentes."""

    def __init__(self, db_path: str = "/home/ubuntu/firby/firby_ultra.db"):
        self.db_path = db_path
        self._agents: Dict[str, SwarmAgent] = {}
        self._capability_index: Dict[str, List[str]] = {}
        self._init_db()

    def _init_db(self):
        try:
            with sqlite3.connect(self.db_path, timeout=5.0) as conn:
                cur = conn.cursor()
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS swarm_agent_registry (
                        id TEXT PRIMARY KEY,
                        name TEXT NOT NULL,
                        domain TEXT NOT NULL,
                        description TEXT,
                        capabilities JSON,
                        system_prompt TEXT,
                        allowed_handoffs JSON,
                        is_conversational INTEGER DEFAULT 1,
                        org_id TEXT,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                        updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                cur.execute("""
                    CREATE INDEX IF NOT EXISTS idx_swarm_agent_org 
                    ON swarm_agent_registry(org_id)
                """)
                conn.commit()
        except Exception as e:
            log.error(f"[SwarmRegistry] Error inicializando base de datos: {e}")

    def register(self, agent: SwarmAgent, persist_db: bool = False):
        """Registra un agente en memoria e indexa sus capacidades."""
        self._agents[agent.id] = agent
        for cap in agent.capabilities:
            cap_norm = cap.lower().strip()
            if cap_norm not in self._capability_index:
                self._capability_index[cap_norm] = []
            if agent.id not in self._capability_index[cap_norm]:
                self._capability_index[cap_norm].append(agent.id)

        if persist_db:
            self._persist_agent_db(agent)

        log.info(f"[SwarmRegistry] Agente registrado: {agent.id} ({agent.name})")

    def _persist_agent_db(self, agent: SwarmAgent):
        try:
            with sqlite3.connect(self.db_path, timeout=3.0) as conn:
                cur = conn.cursor()
                cur.execute("""
                    INSERT INTO swarm_agent_registry (id, name, domain, description, capabilities, system_prompt, allowed_handoffs, is_conversational, org_id, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
                    ON CONFLICT(id) DO UPDATE SET
                        name = excluded.name,
                        domain = excluded.domain,
                        description = excluded.description,
                        capabilities = excluded.capabilities,
                        system_prompt = excluded.system_prompt,
                        allowed_handoffs = excluded.allowed_handoffs,
                        is_conversational = excluded.is_conversational,
                        org_id = excluded.org_id,
                        updated_at = datetime('now')
                """, (
                    agent.id,
                    agent.name,
                    agent.domain.value if isinstance(agent.domain, AgentDomain) else str(agent.domain),
                    agent.description,
                    json.dumps(agent.capabilities, ensure_ascii=False),
                    agent.system_prompt,
                    json.dumps(agent.allowed_handoffs, ensure_ascii=False),
                    1 if agent.is_conversational else 0,
                    agent.org_id
                ))
                conn.commit()
        except Exception as e:
            log.warning(f"[SwarmRegistry] Error persistiendo agente {agent.id} en DB: {e}")

    def get(self, agent_id: str) -> Optional[SwarmAgent]:
        return self._agents.get(agent_id)

    def find_by_capability(self, capability: str, org_id: Optional[str] = None) -> List[SwarmAgent]:
        """Encuentra agentes coincidentes con una capacidad, respetando el tenant."""
        cap_norm = capability.lower().strip()
        matched_ids = self._capability_index.get(cap_norm, [])
        results = []
        for aid in matched_ids:
            ag = self.get(aid)
            if ag:
                if org_id is None or ag.org_id is None or ag.org_id == org_id:
                    results.append(ag)
        return results

    def list_all(self, org_id: Optional[str] = None) -> List[SwarmAgent]:
        """Lista todos los agentes disponibles para la organización dada."""
        if org_id is None or org_id in ("firby_landing", "firby", ""):
            return [a for a in self._agents.values() if a.org_id is None]
        return [a for a in self._agents.values() if a.org_id is None or a.org_id == org_id]

    def count(self) -> int:
        return len(self._agents)


# Singleton
swarm_registry = SwarmRegistry()
