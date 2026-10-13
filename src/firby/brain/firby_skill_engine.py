#!/usr/bin/env python3
"""
Firby Procedural Skill Engine (Hermes Architecture Port)

Brings Hermes Agent's autonomous skill generation, curation, and execution
to Firby AI, replacing the broken self_improve task flood.

Features:
1. Procedural Skills formatted as SKILL.md with YAML frontmatter + markdown instructions.
2. Skill Curation & Validation: Guard scanner to prevent malicious code/prompt injections.
3. Auto-synthesis: Automatically extracts successful sales/closing patterns into reusable skills.
4. Skill Registry & Execution: Matches incoming user turns against relevant skills.
"""

import json
import logging
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

SKILL_TEMPLATE = """---
name: {name}
description: {description}
version: 1.0.0
category: {category}
tags: [{tags}]
---

# {title}

## Trigger Conditions
{triggers}

## Procedural Strategy
{strategy}

## Examples
{examples}
"""


class SkillGuard:
    """Validates skills for path traversal, code injection, and security threats."""

    FORBIDDEN_KEYWORDS = [
        "os.system",
        "subprocess.Popen",
        "eval(",
        "exec(",
        "__import__",
        "rm -rf",
        "DROP TABLE",
        "DELETE FROM",
    ]

    @classmethod
    def validate_skill(cls, name: str, content: str) -> Optional[str]:
        # Path safety check
        if "/" in name or "\\" in name or ".." in name:
            return "Invalid skill name: Path traversal characters not allowed."

        # Content safety check
        for kw in cls.FORBIDDEN_KEYWORDS:
            if kw in content:
                return f"Blocked: Skill contains forbidden keyword or code execution pattern '{kw}'."

        return None


class FirbySkillEngine:
    """
    Manages procedural skills stored on disk under instances/<instance>/skills/ or ~/.firby/skills/.
    """

    def __init__(self, skills_dir: Path):
        self.skills_dir = Path(skills_dir)
        self.skills_dir.mkdir(parents=True, exist_ok=True)

    def create_skill(
        self,
        name: str,
        description: str,
        category: str,
        triggers: List[str],
        strategy: str,
        examples: List[str],
        tags: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Creates a new skill file after security validation."""
        clean_name = re.sub(r"[^\w\-]", "_", name.lower().strip())
        
        tags_str = ", ".join(f'"{t}"' for t in (tags or ["sales", "auto-generated"]))
        triggers_str = "\n".join(f"- {t}" for t in triggers)
        examples_str = "\n".join(f"- {e}" for e in examples)

        content = SKILL_TEMPLATE.format(
            name=clean_name,
            description=description,
            category=category,
            tags=tags_str,
            title=name.replace("_", " ").title(),
            triggers=triggers_str,
            strategy=strategy,
            examples=examples_str,
        )

        error = SkillGuard.validate_skill(clean_name, content)
        if error:
            return {"success": False, "error": error}

        skill_folder = self.skills_dir / clean_name
        skill_folder.mkdir(parents=True, exist_ok=True)
        skill_file = skill_folder / "SKILL.md"

        try:
            skill_file.write_text(content, encoding="utf-8")
            return {"success": True, "path": str(skill_file), "name": clean_name}
        except Exception as e:
            return {"success": False, "error": f"Failed to write skill file: {e}"}

    def list_skills(self) -> List[Dict[str, Any]]:
        """Lists all registered skills with their metadata."""
        skills = []
        if not self.skills_dir.exists():
            return skills

        for skill_folder in self.skills_dir.iterdir():
            if skill_folder.is_dir():
                skill_file = skill_folder / "SKILL.md"
                if skill_file.exists():
                    try:
                        raw = skill_file.read_text(encoding="utf-8")
                        metadata = self._parse_frontmatter(raw)
                        skills.append({
                            "name": skill_folder.name,
                            "path": str(skill_file),
                            "metadata": metadata
                        })
                    except Exception as e:
                        logger.error(f"Error reading skill {skill_file}: {e}")
        return skills

    def _parse_frontmatter(self, content: str) -> Dict[str, str]:
        metadata = {}
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                yaml_block = parts[1]
                for line in yaml_block.strip().split("\n"):
                    if ":" in line:
                        k, v = line.split(":", 1)
                        metadata[k.strip()] = v.strip().strip('"').strip("'")
        return metadata

    def find_matching_skills(self, user_message: str) -> List[str]:
        """Finds skills whose triggers, description, or content match the incoming message."""
        matched = []
        user_lower = user_message.lower()

        for skill in self.list_skills():
            name = skill["name"]
            meta = skill["metadata"]
            desc = meta.get("description", "").lower()
            
            # Check description keywords
            if any(term in user_lower for term in desc.split() if len(term) > 3):
                matched.append(name)
                continue

            # Check SKILL.md file content for triggers
            skill_file = Path(skill["path"])
            if skill_file.exists():
                try:
                    content_lower = skill_file.read_text(encoding="utf-8").lower()
                    if name.replace("_", " ") in user_lower:
                        matched.append(name)
                    elif "trigger" in content_lower:
                        for line in content_lower.split("\n"):
                            stripped = line.strip()
                            if stripped.startswith("- ") and len(stripped) > 3:
                                trigger_phrase = stripped[2:].strip()
                                if trigger_phrase in user_lower or any(word in user_lower for word in trigger_phrase.split() if len(word) >= 4):
                                    matched.append(name)
                                    break
                except Exception:
                    pass
        return list(set(matched))

    def synthesize_skill_from_conversation(self, chat_history: List[Dict[str, str]], outcome: str) -> Dict[str, Any]:
        """
        Extracts a procedural skill from a successful high-converting conversation (Hermes Trajectory Synthesis).
        """
        if outcome != "conversion_success" or len(chat_history) < 4:
            return {"success": False, "reason": "Insufficient turns or non-converting conversation"}

        # Extract user objections and successful closing response
        user_inputs = [m["content"] for m in chat_history if m.get("role") == "user"]
        assistant_responses = [m["content"] for m in chat_history if m.get("role") == "assistant"]

        if not user_inputs or not assistant_responses:
            return {"success": False, "reason": "Missing conversation roles"}

        trigger_summary = f"Objections raised: {user_inputs[-2] if len(user_inputs) > 1 else user_inputs[0]}"
        strategy_summary = f"Successful response technique: {assistant_responses[-1][:200]}..."

        skill_name = f"auto_closer_{int(time.time())}"
        return self.create_skill(
            name=skill_name,
            description="Auto-synthesized closing technique from successful lead interaction",
            category="sales_closing",
            triggers=[trigger_summary],
            strategy=strategy_summary,
            examples=[assistant_responses[-1]],
            tags=["auto-learned", "conversion"]
        )
