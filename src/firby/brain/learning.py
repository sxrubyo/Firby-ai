"""firby_learning.py — Real-time 3-layer learning engine."""
from __future__ import annotations

import hashlib
import json
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

log = logging.getLogger("firby.learning")

POSITIVE_SIGNALS = [
    "gracias", "perfecto", "listo", "genial", "excelente", "dale", "ok perfecto",
    "thanks", "great", "perfect", "awesome",
    "te agradezco", "muy amable", "me queda claro", "entendido",
]
NEGATIVE_SIGNALS = [
    "no entiendo", "eso no es", "no me sirve", "otra vez", "repite",
    "eso ya lo dije", "ya te dije", "no es eso", "equivocad",
]


class RealTimeLearningEngine:
    """3-layer learning: per-turn, per-session, admin-corrected."""

    def __init__(self, base_dir: str = "memory_store"):
        self._base = Path(base_dir)
        self._teachings_dir = Path("teachings")
        self._teachings_dir.mkdir(exist_ok=True)

    def _instance_dir(self, instance_id: str) -> Path:
        d = self._base / instance_id / "learning"
        d.mkdir(parents=True, exist_ok=True)
        return d

    async def learn_from_turn(self, instance_id: str, user_msg: str,
                              bot_response: str, user_reply: str = ""):
        idir = self._instance_dir(instance_id)
        if user_reply and any(s in user_reply.lower() for s in POSITIVE_SIGNALS):
            await self._reinforce_pattern(idir, bot_response, user_msg)
        if user_reply and any(s in user_reply.lower() for s in NEGATIVE_SIGNALS):
            await self._flag_failed_response(idir, bot_response, user_msg, user_reply)

    async def _reinforce_pattern(self, idir: Path, response: str, trigger: str):
        file = idir / "reinforced.jsonl"
        entry = {"ts": datetime.now().isoformat(), "trigger": trigger[:200], "response": response[:300]}
        with open(file, "a") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    async def _flag_failed_response(self, idir: Path, response: str,
                                    user_msg: str, user_reply: str):
        file = idir / "failures.jsonl"
        entry = {
            "ts": datetime.now().isoformat(),
            "user_msg": user_msg[:200],
            "bot_response": response[:300],
            "user_complaint": user_reply[:200],
        }
        with open(file, "a") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        log.info(f"[learning] flagged failed response for {idir.parent.name}")

    async def learn_from_session(self, instance_id: str, messages: List[Dict],
                                 outcome: str = "unknown"):
        idir = self._instance_dir(instance_id)
        file = idir / "sessions.jsonl"
        entry = {
            "ts": datetime.now().isoformat(),
            "outcome": outcome,
            "turns": len(messages),
            "summary": self._summarize_session(messages),
        }
        with open(file, "a") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        if outcome == "booked":
            await self._save_successful_flow(idir, messages)
        elif outcome == "abandoned":
            await self._save_dropout_point(idir, messages)

    async def _save_successful_flow(self, idir: Path, messages: List[Dict]):
        file = idir / "successful_flows.jsonl"
        flow = [{"role": m["role"], "content": m["content"][:150]} for m in messages[-8:]]
        with open(file, "a") as f:
            f.write(json.dumps({"ts": datetime.now().isoformat(), "flow": flow}, ensure_ascii=False) + "\n")

    async def _save_dropout_point(self, idir: Path, messages: List[Dict]):
        file = idir / "dropouts.jsonl"
        last_bot = ""
        for m in reversed(messages):
            if m.get("role") == "assistant":
                last_bot = m["content"][:200]
                break
        with open(file, "a") as f:
            f.write(json.dumps({"ts": datetime.now().isoformat(), "last_bot_msg": last_bot}, ensure_ascii=False) + "\n")

    def _summarize_session(self, messages: List[Dict]) -> str:
        user_msgs = [m["content"] for m in messages if m.get("role") == "user"]
        return " | ".join(msg[:50] for msg in user_msgs[:5]) if user_msgs else "empty"

    async def learn_from_admin(self, instance_id: str, question: str, answer: str,
                               admin_id: str = "") -> str:
        teachings_file = self._teachings_dir / f"{instance_id}.jsonl"
        entry = {
            "ts": datetime.now().isoformat(),
            "question": question,
            "answer": answer,
            "taught_by": admin_id,
            "question_hash": hashlib.md5(question.lower().strip().encode(), usedforsecurity=False).hexdigest()[:12],
        }
        with open(teachings_file, "a") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

        try:
            faq_file = self._base / instance_id / "semantic" / "faqs.json"
            faq_file.parent.mkdir(parents=True, exist_ok=True)
            faqs = json.loads(faq_file.read_text()) if faq_file.exists() else {}
            faqs[entry["question_hash"]] = {
                "question": question,
                "answer": answer,
                "frequency": faqs.get(entry["question_hash"], {}).get("frequency", 0) + 1,
                "source": "admin_taught",
                "last_asked": datetime.now().isoformat(),
            }
            faq_file.write_text(json.dumps(faqs, ensure_ascii=False, indent=2))
        except Exception as e:
            log.warning(f"[learning] FAQ update failed: {e}")

        log.info(f"[learning] admin taught: '{question[:50]}' → '{answer[:50]}'")
        return f"✅ Aprendido. Ya sé responder: '{question[:50]}...'"

    async def get_teachings(self, instance_id: str, limit: int = 50) -> List[Dict]:
        teachings_file = self._teachings_dir / f"{instance_id}.jsonl"
        if not teachings_file.exists():
            return []
        teachings = []
        for line in open(teachings_file):
            try:
                teachings.append(json.loads(line))
            except Exception:
                continue
        return teachings[-limit:]

    def build_teachings_prompt(self, teachings: List[Dict]) -> str:
        if not teachings:
            return ""
        lines = ["INFORMACIÓN APRENDIDA (verificada por admin):"]
        for t in teachings:
            lines.append(f"- Pregunta: {t['question']}\n  Respuesta: {t['answer']}")
        return "\n".join(lines)

    def get_learning_context(self, instance_id: str, query: str = "") -> str:
        """
        Retorna el contexto de aprendizaje acumulado (patrones reforzados, intervenciones
        del admin y errores a evitar) formateado para inyectarse directamente en el prompt del LLM.
        """
        try:
            idir = self._instance_dir(instance_id)
            query_lower = query.lower() if query else ""
            reinforced_matches = []
            failure_matches = []

            # 1. Consultar patrones reforzados (reinforced.jsonl)
            reinf_file = idir / "reinforced.jsonl"
            if reinf_file.exists():
                lines = reinf_file.read_text().splitlines()[-20:]
                for line in reversed(lines):
                    if not line.strip(): continue
                    try:
                        data = json.loads(line)
                        trig = data.get("trigger", "").lower()
                        resp = data.get("response", "")
                        if not query_lower or any(w in trig for w in query_lower.split() if len(w) > 3):
                            reinforced_matches.append(f"• Pregunta: \"{data.get('trigger','')}\" ➔ Respuesta Aprobada: \"{resp}\"")
                            if len(reinforced_matches) >= 3: break
                    except Exception: pass

            # 2. Consultar errores a evitar (failures.jsonl)
            fail_file = idir / "failures.jsonl"
            if fail_file.exists():
                lines = fail_file.read_text().splitlines()[-15:]
                for line in reversed(lines):
                    if not line.strip(): continue
                    try:
                        data = json.loads(line)
                        bot_resp = data.get("bot_response", "")
                        complaint = data.get("user_complaint", "")
                        failure_matches.append(f"• EVITAR decir \"{bot_resp[:120]}\" (Motivo: {complaint})")
                        if len(failure_matches) >= 2: break
                    except Exception: pass

            # 3. Consultar enseñanzas del admin en enseñanzas directas (teachings/)
            teachings_file = Path("instances") / instance_id / "teachings.json"
            if not teachings_file.exists():
                teachings_file = self._teachings_dir / f"{instance_id}.json"

            admin_teachings = []
            if teachings_file.exists():
                try:
                    tdata = json.loads(teachings_file.read_text())
                    if isinstance(tdata, list):
                        for item in tdata[-5:]:
                            admin_teachings.append(f"• Regla Enseñada por el Dueño: {item}")
                    elif isinstance(tdata, dict):
                        for k, v in list(tdata.items())[-5:]:
                            admin_teachings.append(f"• Regla '{k}': {v}")
                except Exception: pass

            # Construir bloque de contexto
            sections = []
            if admin_teachings:
                sections.append("🎓 [REGLAS Y ENSEÑANZAS DEL ADMINISTRADOR / DUEÑO]:\n" + "\n".join(admin_teachings))
            if reinforced_matches:
                sections.append("🌟 [PATRONES Y EJEMPLOS DE RESPUESTA EXITOSOS]:\n" + "\n".join(reinforced_matches))
            if failure_matches:
                sections.append("⚠️ [ERRORES Y CORRECCIONES DE CONVERSACIONES PASADAS A EVITAR]:\n" + "\n".join(failure_matches))

            return "\n\n".join(sections) if sections else ""
        except Exception as e:
            log.warning(f"[learning] Error generating learning context: {e}")
            return ""


learning_engine = RealTimeLearningEngine()
