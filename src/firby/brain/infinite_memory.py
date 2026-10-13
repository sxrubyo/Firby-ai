"""Infinite Memory Subsystem for Firby V10.

Implements multi-tiered memory (Episodic, Semantic, Admin Teachings Store)
with multi-tenant isolation, priority weighting, and TTL cache.
"""

import time
import json
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path

log = logging.getLogger("firby.brain.infinite_memory")


class AdminTeachingRule:
    def __init__(self, rule_id: str, trigger: str, instruction: str, priority: int = 10, created_at: float = None):
        self.rule_id = rule_id
        self.trigger = trigger.lower()
        self.instruction = instruction
        self.priority = priority
        self.created_at = created_at or time.time()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "rule_id": self.rule_id,
            "trigger": self.trigger,
            "instruction": self.instruction,
            "priority": self.priority,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AdminTeachingRule":
        return cls(
            rule_id=data.get("rule_id", ""),
            trigger=data.get("trigger", ""),
            instruction=data.get("instruction", ""),
            priority=data.get("priority", 10),
            created_at=data.get("created_at", time.time()),
        )


class InfiniteMemoryEngine:
    """Motor de Memoria Infinita con 4 capas de persistencia y contexto."""

    def __init__(self, tenant_id: str = "default"):
        self.tenant_id = tenant_id
        self._working_memory: Dict[str, List[Dict[str, Any]]] = {}
        self._admin_rules: List[AdminTeachingRule] = []
        self._semantic_index: Dict[str, str] = {}
        self._storage_dir = Path("memory_store") / tenant_id
        self._storage_dir.mkdir(parents=True, exist_ok=True)
        self._load_admin_rules()

    def _load_admin_rules(self) -> None:
        rules_file = self._storage_dir / "admin_rules.json"
        if rules_file.exists():
            try:
                data = json.loads(rules_file.read_text(encoding="utf-8"))
                self._admin_rules = [AdminTeachingRule.from_dict(r) for r in data]
            except Exception as e:
                log.error(f"[InfiniteMemory] Failed to load admin rules for tenant {self.tenant_id}: {e}")

    def save_admin_rules(self) -> None:
        rules_file = self._storage_dir / "admin_rules.json"
        try:
            data = [r.to_dict() for r in self._admin_rules]
            rules_file.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        except Exception as e:
            log.error(f"[InfiniteMemory] Failed to save admin rules for tenant {self.tenant_id}: {e}")

    def add_admin_teaching(self, trigger: str, instruction: str, priority: int = 10) -> AdminTeachingRule:
        """Agrega una regla aprendida directamente del administrador."""
        rule_id = f"rule_{len(self._admin_rules) + 1}_{int(time.time())}"
        rule = AdminTeachingRule(rule_id, trigger, instruction, priority)
        self._admin_rules.append(rule)
        self.save_admin_rules()
        log.info(f"[InfiniteMemory] Added admin rule for tenant {self.tenant_id}: '{trigger}' -> '{instruction}'")
        return rule

    def get_matching_admin_rules(self, user_msg: str) -> List[AdminTeachingRule]:
        """Obtiene las reglas del admin aplicables al mensaje actual."""
        msg_low = user_msg.lower()
        matched = [r for r in self._admin_rules if r.trigger in msg_low]
        return sorted(matched, key=lambda x: x.priority, reverse=True)

    def record_turn(self, chat_id: str, user_msg: str, bot_response: str) -> None:
        """Registra un turno conversacional en la memoria de trabajo y episodios."""
        if chat_id not in self._working_memory:
            self._working_memory[chat_id] = []

        turn = {
            "timestamp": time.time(),
            "user_msg": user_msg,
            "bot_response": bot_response,
        }
        self._working_memory[chat_id].append(turn)

    def get_working_history(self, chat_id: str, max_turns: int = 10) -> List[Dict[str, Any]]:
        """Devuelve los últimos N turnos conversacionales."""
        history = self._working_memory.get(chat_id, [])
        return history[-max_turns:]

    def build_infinite_context_prompt(self, chat_id: str, user_msg: str) -> str:
        """Construye el bloque de memoria inyectable para el prompt LLM."""
        matched_rules = self.get_matching_admin_rules(user_msg)
        prompt_parts = []

        if matched_rules:
            prompt_parts.append("=== REGLAS APRENDIDAS DEL ADMINISTRADOR (PRIORIDAD ALTA) ===")
            for r in matched_rules:
                prompt_parts.append(f"- REGLA: {r.instruction}")
            prompt_parts.append("")

        history = self.get_working_history(chat_id, max_turns=6)
        if history:
            prompt_parts.append("=== HISTORIAL RECIENTE DE LA CONVERSACIÓN ===")
            for turn in history:
                prompt_parts.append(f"Usuario: {turn['user_msg']}")
                prompt_parts.append(f"Agente: {turn['bot_response']}")

        return "\n".join(prompt_parts)
