#!/usr/bin/env python3
"""
Firby Natural Language WhatsApp Reminders Engine (Hermes Architecture Port)

Allows patients, leads, and admins to schedule WhatsApp reminders using
natural time expressions or structured durations ("30m", "2h", "1d", "every 1d", ISO timestamps).

Key Features:
1. Schedule parser supporting relative durations, ISO timestamps, and recurring intervals.
2. Threat scanner validating reminder prompt text against injection attacks.
3. Seamless integration with SQLite `tasks` table for automated background dispatch.
"""

import json
import logging
import re
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

logger = logging.getLogger(__name__)

# Threat scanner for reminder prompts
REMINDER_THREAT_PATTERNS = [
    r"ignore\s+(?:\w+\s+)*(previous|all|above|prior)\s+(?:\w+\s+)*instructions",
    r"system prompt override",
    r"cat\s+[^\n]*(\.env|credentials)",
    r"curl\s+[^\n]*https?://",
    r"rm\s+-rf",
]


def scan_reminder_prompt(prompt: str) -> Optional[str]:
    """Validates reminder prompt text against security threat patterns."""
    for pattern in REMINDER_THREAT_PATTERNS:
        if re.search(pattern, prompt, re.IGNORECASE):
            return f"Blocked: Reminder prompt matched security threat pattern ({pattern})"
    return None


def parse_duration(s: str) -> int:
    """Parses duration string like '30m', '2h', '1d' into total minutes."""
    match = re.match(r"^(\d+)([mhd])$", s.strip().lower())
    if not match:
        raise ValueError(f"Invalid duration: '{s}'. Use format like '30m', '2h', or '1d'")
    value = int(match.group(1))
    unit = match.group(2)
    multipliers = {"m": 1, "h": 60, "d": 1440}
    return value * multipliers[unit]


def parse_schedule_expression(expression: str) -> Dict[str, Any]:
    """
    Parses a schedule string into structured format.
    Supports:
      - '30m', '2h', '1d' → relative duration
      - 'every 1d', 'every 2h' → recurring interval
      - '2026-07-25T15:00:00' → ISO timestamp
    """
    expr = expression.strip()
    expr_lower = expr.lower()

    if expr_lower.startswith("every "):
        duration_str = expr[6:].strip()
        minutes = parse_duration(duration_str)
        return {"kind": "recurring", "minutes": minutes, "display": f"every {minutes}m"}

    # Relative duration: 30m, 2h, 1d
    if re.match(r"^\d+[mhd]$", expr_lower):
        minutes = parse_duration(expr_lower)
        target_dt = datetime.now() + timedelta(minutes=minutes)
        return {
            "kind": "once",
            "minutes": minutes,
            "target_iso": target_dt.isoformat(),
            "target_epoch": target_dt.timestamp(),
            "display": f"in {minutes} minutes"
        }

    # ISO timestamp
    if "T" in expr or re.match(r"^\d{4}-\d{2}-\d{2}", expr):
        try:
            target_dt = datetime.fromisoformat(expr.replace("Z", "+00:00"))
            return {
                "kind": "once",
                "target_iso": target_dt.isoformat(),
                "target_epoch": target_dt.timestamp(),
                "display": f"at {target_dt.strftime('%Y-%m-%d %H:%M')}"
            }
        except Exception as e:
            raise ValueError(f"Invalid ISO timestamp '{expr}': {e}")

    raise ValueError(f"Unrecognized schedule expression: '{expr}'")


class FirbyReminderEngine:
    """Manages WhatsApp reminders backed by SQLite tasks table."""

    def __init__(self, db_manager: Any):
        self.db = db_manager

    def schedule_reminder(
        self,
        chat_id: str,
        reminder_text: str,
        schedule_expr: str,
        platform: str = "whatsapp"
    ) -> Dict[str, Any]:
        """Schedules a new WhatsApp reminder task."""
        # 1. Threat Scan
        threat_err = scan_reminder_prompt(reminder_text)
        if threat_err:
            return {"success": False, "error": threat_err}

        # 2. Parse Schedule Expression
        try:
            sched = parse_schedule_expression(schedule_expr)
        except Exception as e:
            return {"success": False, "error": f"Schedule parse error: {e}"}

        # 3. Schedule into DB tasks table
        task_id = f"rem_{int(time.time())}_{chat_id[-4:] if len(chat_id) >= 4 else '0000'}"
        scheduled_for = sched.get("target_iso", datetime.now().isoformat())

        task_data = json.dumps({
            "chat_id": chat_id,
            "message": reminder_text,
            "platform": platform,
            "schedule": sched
        }, ensure_ascii=False)

        try:
            with self.db._conn() as conn:
                conn.execute(
                    """
                    INSERT INTO tasks (id, type, priority, status, data, scheduled_for)
                    VALUES (?, 'reminder', 5, 'pending', ?, ?)
                    """,
                    (task_id, task_data, scheduled_for)
                )
            return {
                "success": True,
                "task_id": task_id,
                "scheduled_for": scheduled_for,
                "display": sched["display"],
                "reminder_text": reminder_text
            }
        except Exception as e:
            return {"success": False, "error": f"DB task insertion failed: {e}"}
