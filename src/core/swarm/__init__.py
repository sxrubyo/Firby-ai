# -*- coding: utf-8 -*-
"""
Firby Multi-Agent Swarm Package
===============================
"""

from src.core.swarm.types import SwarmResult, AgentMessage, MessageType, AgentDomain
from src.core.swarm.registry import swarm_registry, SwarmAgent
from src.core.swarm.message_bus import message_bus
from src.core.swarm.engine import swarm_engine, SwarmEngine
from src.core.swarm.agents import build_default_swarm_agents, create_autonomous_worker_agents

# Registrar flota de agentes predeterminados en el registro central
for agent in build_default_swarm_agents():
    swarm_registry.register(agent, persist_db=True)

for agent in create_autonomous_worker_agents():
    swarm_registry.register(agent, persist_db=True)

__all__ = [
    "swarm_engine",
    "swarm_registry",
    "message_bus",
    "SwarmAgent",
    "SwarmResult",
    "AgentMessage",
    "MessageType",
    "AgentDomain"
]
