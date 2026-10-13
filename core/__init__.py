"""
firby/core/ — Clean public API for Firby v9.0.

Exports the main engine components without requiring direct firby.py imports.
This module bridges the legacy monolith (firby.py) with the new modular architecture.
"""
from firby_memory_engine import memory_engine, FirbyMemoryEngine
from firby_uncertainty import uncertainty_detector, UncertaintyDetector
from firby_voice import voice, FirbyVoice
from firby_nova_proxy import NovaLLMProxy
from src.interfaces.web.admin_api import router as admin_router
from firby_cron import init_scheduler, shutdown_scheduler

__all__ = [
    "memory_engine",
    "FirbyMemoryEngine",
    "uncertainty_detector",
    "UncertaintyDetector",
    "voice",
    "FirbyVoice",
    "NovaLLMProxy",
    "admin_router",
    "init_scheduler",
    "shutdown_scheduler",
]
