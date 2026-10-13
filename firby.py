# -*- coding: utf-8 -*-
"""Firby AI - Monolithic Bootstrap Facade."""
from __future__ import annotations

import sys
import os
import logging

log = logging.getLogger("firby.facade")

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Force full reload of submodules for dynamic test environments to maintain perfect isolation
if __name__ != "__main__":
    for k in list(sys.modules.keys()):
        if k.startswith("src.core") or k.startswith("src.interfaces"):
            del sys.modules[k]

# 1. Import all globals dynamically
import src.core.globals as globals_module
globals_module.__facade_name__ = __name__
for name in dir(globals_module):
    if not name.startswith("__"):
        globals()[name] = getattr(globals_module, name)

# 2. Import all runtime attributes dynamically
import src.core.runtime as runtime_module
runtime_module.__facade_name__ = __name__
for name in dir(runtime_module):
    if not name.startswith("__"):
        globals()[name] = getattr(runtime_module, name)

# 3. Import all web app attributes dynamically
import src.interfaces.web.app as app_module
app_module.__facade_name__ = __name__
for name in dir(app_module):
    if not name.startswith("__"):
        globals()[name] = getattr(app_module, name)

# 4. Define firby global instance and initialization helpers
firby: FirbyUltra = None
ADMIN_PENDING_CONFIRMATIONS: Dict[str, Dict] = {}
db = None
llm_engine = None
anti_robot_filter = None
conversation_simulator = None
response_variation = None
hallucination_guard = None
owner_style_controller = None
auth_engine = None
mcp_manager = None
prompt_evolver = None
trainer_gateway = None
v8_build_quality_system_prompt_addon = None
trainer_get_system_prompt_addon = None
task_manager = None
class FacadeProxy:
    def __init__(self, name):
        self.name = name
    def __call__(self, *args, **kwargs):
        import src.core.globals as g
        func = getattr(g, self.name, None)
        if func:
            return func(*args, **kwargs)
        return args[0] if args else ""

v8_process_response = FacadeProxy("v8_process_response")
v8_process_agentic_intent = FacadeProxy("v8_process_agentic_intent")

async def init_firby():
    """Inicializa Firby Ultra."""
    global firby
    firby = FirbyUltra()
    await firby.initialize()
    
    import src.core.globals as g
    global db, llm_engine, auth_engine, mcp_manager, v8_process_response
    db = g.db
    llm_engine = g.llm_engine
    auth_engine = getattr(g, "auth_engine", None)
    mcp_manager = getattr(g, "mcp_manager", None)
    v8_process_response = getattr(g, "v8_process_response", None)

    # ── brain_v10: anti-frustracion / anti-loop / anti-plantilla ──────────────
    # NOTA: este parche estaba escrito en firby_brain_v10.py pero no se estaba
    # invocando desde ningun lado visible (ni aqui, ni en runtime.py hasta donde
    # pude revisar). Sin esta llamada, todo el trabajo de detectar frustracion,
    # romper loops de preguntas repetidas y validar calidad de respuesta queda
    # escrito pero INACTIVO. auto_patch() busca el objeto `generator` expuesto
    # a nivel de modulo (via los imports dinamicos de arriba); si no lo encuentra
    # ahi, se intenta como atributo de la instancia `firby` o de `globals_module`
    # como respaldo. Si ninguno existe, queda una advertencia clara en el log
    # en vez de fallar en silencio o tumbar el arranque.
    try:
        from firby_brain_v10 import patch_llm_first, init_brain, auto_patch
        init_brain()
        patched = auto_patch()
        if not patched:
            fallback_generator = (
                getattr(firby, "generator", None)
                or getattr(g, "generator", None)
            )
            if fallback_generator is not None:
                patched = patch_llm_first(fallback_generator)
        if patched:
            log.info("[firby] brain_v10 activo (anti-frustracion / anti-loop / anti-plantilla)")
        else:
            log.warning(
                "[firby] brain_v10 NO se pudo activar: no se encontro un objeto "
                "'generator' (ni a nivel de modulo, ni en firby.generator, ni en "
                "globals.generator). Revisar src/core/runtime.py — deberia exponer "
                "una instancia de ResponseGenerator con metodos generate() y "
                "_normalize_first_patient_turn()."
            )
    except ImportError:
        log.info("[firby] firby_brain_v10 no esta presente — se omite el parche")
    except Exception as e:
        log.error(f"[firby] error activando brain_v10: {e}", exc_info=True)


# 5. CLI entrypoint
if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", "8001"))
    host = os.getenv("HOST", "0.0.0.0")
    
    print("""
    ╔══════════════════════════════════════════════════════════════════╗
    ║                                                                  ║
    ║   ███████╗██╗██████╗ ██████╗ ██╗   ██╗                          ║
    ║   ██╔════╝██║██╔══██╗██╔══██╗╚██╗ ██╔╝                          ║
    ║   █████╗  ██║██████╔╝██████╔╝ ╚████╔╝                           ║
    ║   ██╔══╝  ██║██╔══██╗██╔══██╗  ╚██╔╝                            ║
    ║   ██║     ██║██║  ██║██████╔╝   ██║                             ║
    ║   ╚═╝     ╚═╝╚═╝  ╚═╝╚═════╝    ╚═╝                             ║
    ║                                                                  ║
    ║                      F I R B Y   A I                             ║
    ║                                                                  ║
    ║            Plataforma Autonoma de Recepcion y Citas              ║
    ║                                                                  ║
    ╠══════════════════════════════════════════════════════════════════╣
    ║  • Web Widget 2D — Atencion y citas en tiempo real               ║
    ║  • WhatsApp Ejecutivo — Canal privado con el dueno (+57 324...)  ║
    ║  • Google Calendar Sync — Disponibilidad y reservas reales       ║
    ║  • Lienzo de Automatizacion — Integracion nativa con n8n         ║
    ║  • Memoria FTS5 — Retencion e inteligencia contextual            ║
    ║  • Multi-Tenant SaaS — Personalizacion dinamica por cliente      ║
    ╚══════════════════════════════════════════════════════════════════╝
    """)
    
    uvicorn.run(
        "firby:app",
        host=host,
        port=port,
        reload=False,
        log_level="info"
    )
