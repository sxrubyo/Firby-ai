#!/usr/bin/env python3
"""
Firby Context Variables & Concurrent Session Isolation (Hermes Architecture Port)

Uses Python's `contextvars` stdlib module to isolate chat, tenant, and instance state
across concurrent asyncio tasks in FastAPI/Uvicorn, preventing race conditions when
multiple WhatsApp patients talk simultaneously.
"""

import contextvars
from typing import Any, Dict, Optional

# Context Variables for concurrent safety
_SESSION_CHAT_ID: contextvars.ContextVar[str] = contextvars.ContextVar("session_chat_id", default="")
_SESSION_INSTANCE_ID: contextvars.ContextVar[str] = contextvars.ContextVar("session_instance_id", default="firby")
_SESSION_PLATFORM: contextvars.ContextVar[str] = contextvars.ContextVar("session_platform", default="whatsapp")
_SESSION_PATIENT_NAME: contextvars.ContextVar[str] = contextvars.ContextVar("session_patient_name", default="")


def set_request_context(chat_id: str, instance_id: str = "firby", platform: str = "whatsapp", patient_name: str = "") -> list:
    """Sets context variables for the active asyncio task and returns reset tokens."""
    t1 = _SESSION_CHAT_ID.set(chat_id)
    t2 = _SESSION_INSTANCE_ID.set(instance_id)
    t3 = _SESSION_PLATFORM.set(platform)
    t4 = _SESSION_PATIENT_NAME.set(patient_name)
    return [(_SESSION_CHAT_ID, t1), (_SESSION_INSTANCE_ID, t2), (_SESSION_PLATFORM, t3), (_SESSION_PATIENT_NAME, t4)]


def reset_request_context(tokens: list):
    """Resets context variables using returned tokens to clean up after request finishes."""
    for var, token in reversed(tokens):
        var.reset(token)


def get_current_chat_id() -> str:
    return _SESSION_CHAT_ID.get()


def get_current_instance_id() -> str:
    return _SESSION_INSTANCE_ID.get()


def get_current_platform() -> str:
    return _SESSION_PLATFORM.get()


def get_current_patient_name() -> str:
    return _SESSION_PATIENT_NAME.get()
