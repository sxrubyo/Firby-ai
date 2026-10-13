# -*- coding: utf-8 -*-
"""
Firby Task Notebook (inspired by DeerFlow task_continuity & task_note).
Maintains a clean, bounded working memory of facts, file locations, and milestone notes
across long-running agent workflows without bloating the LLM context window.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional


@dataclass
class TaskNote:
    key: str
    content: str
    category: str = "general"     # "finding" | "file" | "todo" | "credential" | "general"
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "key": self.key,
            "content": self.content,
            "category": self.category,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


class TaskNotebook:
    """
    Bounded scratchpad for an agent's long-running workflow.
    Prevents token context explosion by capping active notes to max_notes
    and max_chars_per_note (inspired by DeerFlow).
    """

    def __init__(self, max_notes: int = 12, max_chars_per_note: int = 1000):
        self.max_notes = max_notes
        self.max_chars_per_note = max_chars_per_note
        self.notes: Dict[str, TaskNote] = {}

    def set_note(self, key: str, content: str, category: str = "general") -> bool:
        """Saves or updates a named note."""
        trimmed = content.strip()[:self.max_chars_per_note]
        if key in self.notes:
            note = self.notes[key]
            note.content = trimmed
            note.category = category
            note.updated_at = time.time()
            return True

        if len(self.notes) >= self.max_notes:
            # Drop oldest note to maintain bound (FIFO eviction)
            oldest_key = min(self.notes.keys(), key=lambda k: self.notes[k].updated_at)
            del self.notes[oldest_key]

        self.notes[key] = TaskNote(
            key=key,
            content=trimmed,
            category=category,
        )
        return True

    def get_note(self, key: str) -> Optional[str]:
        """Retrieves a note by key."""
        note = self.notes.get(key)
        return note.content if note else None

    def delete_note(self, key: str) -> bool:
        """Deletes a note."""
        if key in self.notes:
            del self.notes[key]
            return True
        return False

    def search_notes(self, query: str) -> List[Dict[str, Any]]:
        """Lexical search over saved notes."""
        q_lower = query.lower()
        results = []
        for note in self.notes.values():
            if q_lower in note.key.lower() or q_lower in note.content.lower():
                results.append(note.to_dict())
        return results

    def render_context_summary(self) -> str:
        """Renders a concise, bulleted markdown representation for system context injection."""
        if not self.notes:
            return "No task notes recorded."
        lines = ["### Active Task Notebook:"]
        for k, note in self.notes.items():
            lines.append(f"- **{k}** ({note.category}): {note.content}")
        return "\n".join(lines)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "max_notes": self.max_notes,
            "count": len(self.notes),
            "notes": {k: n.to_dict() for k, n in self.notes.items()},
        }
