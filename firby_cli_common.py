#!/usr/bin/env python3
"""
firby — CLI v8.0 Enterprise

Sistema de recepcionista IA multi-sector.

Sectores soportados:
  • Clínicas estéticas      • Dentales           • Veterinarias
  • Restaurantes            • Hoteles            • Gimnasios
  • Salones de belleza      • Spas               • Consultorios médicos
  • Psicólogos              • Abogados           • Inmobiliarias
  • Talleres mecánicos      • Academias          • Nutricionistas
  • Fisioterapia            • Fotografía         • Coworkings

Comandos:
  firby install           Instalar CLI globalmente (hazlo primero)
  firby init              Primer setup guiado del producto
  firby new               Crear instancia para un cliente (wizard)
  firby list              Ver todas las instancias
  firby dashboard         Panel en tiempo real
  firby chat [n]          Generar tokens, probar bot, ver webhook
  firby sync              Clonar runtime compartido actualizado a todos los clientes
  firby sync-check        Vista previa de qué archivos se sincronizarían (dry-run)
  firby sync-manifest     Ver / editar el manifiesto de archivos sincronizables
  firby fix [n]           Reparar instancias con bug de --cwd (bot no responde)
  firby status [n]        Estado detallado
  firby health            Health check rápido de todas
  firby logs [n]          Logs en tiempo real
  firby restart [n]       Reiniciar (o 'all')
  firby webhooks [n]      Ver/reconfigurar webhook de Telegram
  firby mcp               Inicia el servidor Model Context Protocols [n]
  firby config [n]        Hub de configuración o edición de instancia
  firby guide             Guía completa de operación
  firby doctor            Diagnóstico del sistema
  firby upgrade           Actualizar + propagar a todos los clientes
  firby metrics [n]       Métricas de uso
  firby stats [n]         Estadísticas de conversaciones
  firby export [n]        Exportar a JSON/CSV
  firby import [file]     Importar configuración
  firby test [n]          Probar respuestas
  firby stop [n]          Detener
  firby delete [n]        Eliminar
  firby clone [n]         Clonar instancia
  firby reset [n]         Resetear sesión
  firby backup [n]        Crear snapshot
  firby restore [file]    Restaurar snapshot
  firby scale [n] [num]   Escalar workers
  firby audit             Auditoría de seguridad
  firby benchmark         Test de rendimiento
  firby secure            Guía de seguridad
  firby rotate-keys       Rotar secrets
  firby billing           Uso de APIs y costos
  firby omni [sub]        Monitoreo central
  firby nova [sub]        Motor Nova
  firby gateway [n]       Gateway automático de skills y reglas
  firby control [n]       Control duro del admin sobre frases, saludo y trato

V8.0 — NUEVOS COMANDOS:
  firby modelo [n]        Cambiar modelo LLM en caliente (sin reiniciar)
  firby simular [n]       Simular 10 conversaciones — detecta frases de bot
  firby v8 [n]            Estado de los 15 sistemas V8
  firby quality [n]       Score de humanidad de últimas respuestas
  firby briefing [n]      Briefing diario: leads calientes + acción recomendada
  firby cost [n]          Estimación de costo mensual del LLM
  firby latency [n]       Test de latencia HTTP + LLM
  firby diff [n1] [n2]    Comparar configuración entre instancias
  firby watchdog          Monitor continuo con auto-restart inteligente
  firby warmup [n]        Precalentar LLM antes de lanzar
  firby campana [n]       Campañas de seguimiento y reactivación
  firby env-check [n]     Verificar .env contra mejores prácticas V8
  firby rollforward [n]   Aplicar firby.py a instancias
  firby dashboard-v8      Dashboard enriquecido con métricas V8

LOG ENGINE — Análisis inteligente de errores:
  firby logs [n]           Stream en vivo con colores + alerta de errores
  firby logs [n] --scan    Escanear logs: detecta errores con diagnóstico
  firby logs [n] --fix     Detectar errores + aplicar fixes automáticos
  firby logs [n] --errors  Mostrar solo líneas de error
  firby logfix [n]         Atajo: logs --fix
  firby logscan [n]        Atajo: logs --scan
"""

import sys, os, json, time, subprocess, threading, shutil, hashlib, signal, ast, tempfile
import platform, re, argparse, tarfile, sqlite3, csv
from pathlib import Path
from datetime import datetime, timedelta
from functools import lru_cache
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor, as_completed

from firby_cli_bb import (
    BBContext,
    bb_apply_persona as _bb_apply_persona_impl,
    bb_load_persona as _bb_load_persona_impl,
    bb_persona_defaults as _bb_persona_defaults_impl,
    bb_personality_catalog as _bb_personality_catalog_impl,
    bb_prompt_block as _bb_prompt_block_impl,
    bb_read_persona_db as _bb_read_persona_db_impl,
    bb_score_prompt as _bb_score_prompt_impl,
    bb_show_agent_summary as _bb_show_agent_summary_impl,
    bb_write_persona_db as _bb_write_persona_db_impl,
    cmd_bb as _cmd_bb_impl,
    cmd_bb_config as _cmd_bb_config_impl,
)

try:
    from firby_i18n import get_i18n, set_language, SUPPORTED_LANGUAGES, LANGUAGE_MENU, detect_user_language
    _I18N = get_i18n()
except ImportError:
    class FakeI18n:
        def t(self, key, category="ui"): return key
        def ui(self, key): return key
        def bot(self, key): return key
        def demo(self, key): return key
        def admin(self, key): return key
        def set_lang(self, lang): pass
        @property
        def current_lang(self): return "es"
        @property
        def available_languages(self): return {"es": "Español"}
    _I18N = FakeI18n()

def t(key, category="ui"): return _I18N.t(key, category)

def mask_secret(value: str, visible: int = 4) -> str:
    raw = str(value or "")
    if not raw:
        return "—"
    if len(raw) <= visible * 2:
        return "•" * len(raw)
    return f"{raw[:visible]}…{raw[-visible:]}"

# ══════════════════════════════════════════════════════════════════════════════
# READLINE + AUTOCOMPLETADO
# ══════════════════════════════════════════════════════════════════════════════
COMMANDS = [
    "init", "new", "list", "dashboard", "status", "health", "metrics", "stats",
    "logs", "config", "template", "export", "import", "test", "restart", "stop",
    "delete", "clone", "reset", "backup", "restore", "scale", "doctor", "audit",
    "benchmark", "secure", "rotate-keys", "upgrade", "billing", "chat", "omni", "nova",
    "sync", "sincronizar", "sync-check", "synccheck", "sync-manifest", "manifest",
    "base",
    "fix", "reparar", "install", "guide",
    "pair", "pairing",
    "token", "tokens", "activar", "bridge", "whatsapp", "wa", "info",
    # V8.0 — nuevos comandos
    "modelo", "simular", "simulate", "v8", "quality", "humanness",
    "briefing", "campana", "campaign", "diff", "compare",
    "cost", "costos", "latency", "latencia",
    "env-check", "warmup", "watchdog", "rollforward", "watch", "live", "diagnose", "obs", "skills", "skill", "aprender", "desaprender", "entrenar", "simular-cliente", "skills", "skill", "aprender", "desaprender", "entrenar", "trainer", "simular-cliente", "cliente", "gateway", "control",
    # i18n — multilingual
    "language", "idioma", "lang", "locale",
    "demo",
]

try:
    import readline
    HIST = Path.home() / ".firby" / "history"
    HIST.parent.mkdir(exist_ok=True)
    if HIST.exists():
        readline.read_history_file(str(HIST))
    readline.set_history_length(1000)
    
    def _completer(text, state):
        opts = [c for c in COMMANDS if c.startswith(text.lower())]
        return opts[state] if state < len(opts) else None
    
    readline.set_completer(_completer)
    readline.parse_and_bind("tab: complete")
    
    import atexit
    atexit.register(readline.write_history_file, str(HIST))
except Exception:
    pass

# ══════════════════════════════════════════════════════════════════════════════
# HTTP CLIENT
# ══════════════════════════════════════════════════════════════════════════════
try:
    import httpx as _httpx
    _HTTPX = True
except ImportError:
    import urllib.request
    _HTTPX = False

# ══════════════════════════════════════════════════════════════════════════════
# CONFIGURACIÓN
# ══════════════════════════════════════════════════════════════════════════════
def _default_instances_dir() -> str:
    env_value = os.getenv("INSTANCES_DIR", "").strip()
    candidates: List[Path] = []
    if env_value:
        candidates.append(Path(env_value).expanduser())
    home = Path.home()
    candidates.extend(
        [
            home / ".firby" / "instances",
            home / ".firby/instances",
            home / "firby/instances",
        ]
    )
    for candidate in candidates:
        if candidate.exists():
            return str(candidate)
    return str(candidates[0])


def build_portable_run_script(instance_dir: str) -> str:
    instance_path = Path(instance_dir)
    return f"""#!/usr/bin/env bash
set -euo pipefail

INSTANCE_DIR="{instance_path}"
cd "$INSTANCE_DIR"

if [ -x "$INSTANCE_DIR/.venv/bin/python" ]; then
  exec "$INSTANCE_DIR/.venv/bin/python" firby.py
fi

if [ -x "$HOME/.firby/runtime/bin/python" ]; then
  exec "$HOME/.firby/runtime/bin/python" "$INSTANCE_DIR/firby.py"
fi

if command -v python3 >/dev/null 2>&1; then
  exec python3 "$INSTANCE_DIR/firby.py"
fi

exec python "$INSTANCE_DIR/firby.py"
"""


def write_portable_run_script(instance_dir: str) -> Path:
    run_path = Path(instance_dir) / "run.sh"
    run_path.write_text(build_portable_run_script(instance_dir), encoding="utf-8")
    run_path.chmod(0o755)
    return run_path


def build_pm2_start_command(instance_dir: str, pm2_name: str, log_dir: str) -> List[str]:
    run_path = write_portable_run_script(instance_dir)
    return [
        "pm2",
        "start",
        str(run_path),
        "--name",
        pm2_name,
        "--cwd",
        str(instance_dir),
        "--restart-delay",
        "3000",
        "--max-restarts",
        "10",
        "--log",
        str(Path(log_dir) / "firby.log"),
        "--error",
        str(Path(log_dir) / "error.log"),
    ]


VERSION = "9.8.0"
FIRBY_HOME = os.getenv("FIRBY_HOME", str(Path.home() / ".firby"))
FIRBY_DIR = os.getenv("FIRBY_DIR", str(Path(__file__).resolve().parent))
INSTANCES_DIR = _default_instances_dir()
NOVA_DIR = os.getenv("NOVA_DIR", "/home/ubuntu/nova-os")
BACKUP_DIR = Path(os.getenv("FIRBY_BACKUPS", Path.home() / "firby-backups"))
CACHE_DIR = Path(FIRBY_HOME) / "cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

OMNI_PORT = int(os.getenv("OMNI_PORT", "9001"))
NOVA_PORT = int(os.getenv("NOVA_PORT", "9002"))
BASE_PORT, MAX_PORT = 8001, 8199

# Caddy — proxy reverso que maneja SSL y enrutamiento
# IMPORTANTE: el Caddyfile vive SIEMPRE en xus-https, nunca en la carpeta de Firby.
# CADDY_DIR se ignora a propósito para evitar que un .env de instancia lo pise.
CADDY_DIR      = "/home/ubuntu/xus-https"
CADDYFILE_PATH = "/home/ubuntu/xus-https/Caddyfile"
CADDY_DOCKER_GW = os.getenv("CADDY_DOCKER_GW", "172.28.0.1")  # gateway Docker→host
SHARED_TELEGRAM_ROUTES = Path(
    os.getenv("FIRBY_SHARED_TELEGRAM_ROUTES", f"{FIRBY_HOME}/shared_telegram_routes.json")
)
WORKSPACE_CONFIG_PATH = Path(os.getenv("FIRBY_WORKSPACE_CONFIG", f"{FIRBY_HOME}/config.json"))

# ── SYNC ENGINE v2 — 2026-05 — auto-detección + manifiesto persistente ────────
#
# Arquitectura de tres capas:
#   1. SYNC_RUNTIME_FILES   — lista fija (siempre se sincronizan)
#   2. SYNC_RUNTIME_DIRS    — directorios fijos (siempre se sincronizan)
#   3. Auto-detección       — cualquier .py nuevo en la base que no esté excluido
#   4. Manifiesto           — ~/.firby/sync_manifest.json (lista extra del usuario)
#
# El manifiesto permite añadir/quitar archivos sin tocar el código.
# ──────────────────────────────────────────────────────────────────────────────

SYNC_RUNTIME_FILES = [
    "firby.py",
    "run.sh",
    "firby_doctor.py",
    "firby_runtime_ops.py",
    "firby_ultra_config.py",
    "src/core/globals.py",
    "src/core/runtime.py",
    "src/interfaces/web/app.py",
    "src/core/admin_engines.py",
    "src/core/production_monitor.py",
    "src/interfaces/web/demo_handler.py",
    "firby_config.py",
    "firby_router.py",
    "firby_utils.py",
    "firby_brain_v10.py",
    "firby_domino.py",
    "firby_memory_engine.py",
    "firby_uncertainty.py",
    "firby_voice.py",
    "firby_voice_engine.py",
    "firby_nova_proxy.py",
    "firby_cron.py",
    "firby_learning.py",
    "firby_commands.py",
    "firby_admin_api.py",
    "firby_session.py",
    "firby_generator.py",
    "firby_audio.py",
    "firby_i18n.py",
    "firby_send_guard.py",
    "firby_nuke_robot_phrases.py",
    "firby_pitch_upgrade.py",
    "firby_memory.py",
    "search.py",
    "knowledge_base.py",
    "brand_assets.py",
    "nova_bridge.py",
    "smart_handoff.py",
    "requirements.txt",
    ".env.example",
]

SYNC_RUNTIME_DIRS = [
    "v7",
    "firby_core",
    "firby_agents",
    "firby_skills",
    "firby_integrations",
    "personas",
    "templates",
    "core",
    "nova",
]

# Archivos que NUNCA se auto-detectan (aunque estén en la raíz base)
_SYNC_EXCLUDE_NAMES: set = {
    # CLI — no se distribuye a las instancias
    "firby_cli.py",
    "firby_cli_bb.py",
    "firby_tui.py",
    # Bases de datos
    "firby.db",
    "firby_ultra.db",
    "firby_x-bussines.db",
    "data.db",
    # Configs de entorno
    ".env",
    ".env.bak",
    # Tooling
    "package.json",
    "install.sh",
    "start.sh",
    "verify_conversation_impl.py",
    "firby_pairing.py",
    "firby_patch.py",
    "firby_sync_fix.py",   # helper temporal de fixes, no es runtime
}

# Sufijos que NUNCA se auto-detectan
_SYNC_EXCLUDE_SUFFIXES: tuple = (
    ".bak", ".log", ".patch", ".db", ".db-shm", ".db-wal",
    ".pyc", ".pyo", ".pre_merge_v9_backup",
)

# Ruta del manifiesto persistente
_SYNC_MANIFEST_PATH = Path(FIRBY_HOME) / "sync_manifest.json"


def _load_sync_manifest() -> dict:
    """Carga el manifiesto desde ~/.firby/sync_manifest.json."""
    default = {"include": [], "exclude": [], "version": 1}
    if not _SYNC_MANIFEST_PATH.exists():
        return default
    try:
        data = json.loads(_SYNC_MANIFEST_PATH.read_text(encoding="utf-8"))
        return {**default, **data}
    except Exception:
        return default


def _save_sync_manifest(manifest: dict) -> None:
    """Guarda el manifiesto."""
    _SYNC_MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    _SYNC_MANIFEST_PATH.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8"
    )


def _autodetect_sync_files(source_root: str) -> List[str]:
    """
    Detecta automáticamente archivos .py en source_root que NO están
    en la lista fija, NO están excluidos y SÍ existen.
    Retorna lista de nombres relativos ordenada.
    """
    root = Path(source_root)
    fixed = set(SYNC_RUNTIME_FILES)
    manifest = _load_sync_manifest()
    extra_exclude = set(manifest.get("exclude", []))
    found = []
    for py_file in sorted(root.glob("*.py")):
        rel = py_file.name
        if rel in fixed:
            continue
        if rel in _SYNC_EXCLUDE_NAMES:
            continue
        if rel in extra_exclude:
            continue
        if any(rel.endswith(s) for s in _SYNC_EXCLUDE_SUFFIXES):
            continue
        found.append(rel)
    # Archivos extra del manifiesto (include manual)
    for extra in manifest.get("include", []):
        if extra not in found and (root / extra).exists():
            found.append(extra)
    return found


def _runtime_sync_entries(source_root: str) -> List[str]:
    """
    Devuelve la lista completa de entradas a sincronizar:
      • archivos y directorios fijos
      • archivos .py auto-detectados en la raíz base
    """
    root = Path(source_root)
    entries: List[str] = []
    seen: set = set()

    # Capa 1 — lista fija
    for rel_path in [*SYNC_RUNTIME_FILES, *SYNC_RUNTIME_DIRS]:
        if (root / rel_path).exists() and rel_path not in seen:
            entries.append(rel_path)
            seen.add(rel_path)

    # Capa 2 — auto-detección de nuevos .py
    for rel in _autodetect_sync_files(source_root):
        if rel not in seen:
            entries.append(rel)
            seen.add(rel)

    return entries


def _remove_runtime_target(path: Path) -> None:
    if not path.exists() and not path.is_symlink():
        return
    if path.is_dir() and not path.is_symlink():
        shutil.rmtree(path)
    else:
        path.unlink()


def _clone_runtime_entries(source_root: str, dest_root: str, entries: Optional[List[str]] = None) -> List[str]:
    src_root = Path(source_root)
    dst_root = Path(dest_root)
    copied: List[str] = []
    for rel_path in entries or _runtime_sync_entries(source_root):
        src = src_root / rel_path
        dst = dst_root / rel_path
        if not src.exists():
            continue
        if rel_path == "run.sh" and dst.exists():
            continue
        dst.parent.mkdir(parents=True, exist_ok=True)
        if src.is_dir():
            _remove_runtime_target(dst)
            shutil.copytree(src, dst)
        else:
            if dst.exists() or dst.is_symlink():
                _remove_runtime_target(dst)
            shutil.copy2(src, dst)
        copied.append(rel_path)
    return copied

# ══════════════════════════════════════════════════════════════════════════════
# SECTORES - La clave para escalar Firby
# ══════════════════════════════════════════════════════════════════════════════
@dataclass
class Sector:
    id: str
    name: str
    emoji: str
    tagline: str
    services: List[str]
    hours_default: str
    questions: List[str]
    keywords: List[str]
    color: str

SECTORS: Dict[str, Sector] = {
    "estetica": Sector(
        id="estetica", name="Clínica Estética", emoji="💉",
        tagline="Transforma belleza en citas",
        services=["Botox", "Rellenos", "Láser", "Peeling", "Mesoterapia"],
        hours_default="09:00-19:00",
        questions=["¿Qué tratamientos ofrecen?", "¿Precio del botox?", "¿Tienen promociones?"],
        keywords=["botox", "relleno", "arrugas", "rejuvenecimiento", "lifting"],
        color="183"
    ),
    "dental": Sector(
        id="dental", name="Clínica Dental", emoji="🦷",
        tagline="Sonrisas que agendan solas",
        services=["Limpieza", "Blanqueamiento", "Ortodoncia", "Implantes", "Endodoncia"],
        hours_default="08:00-18:00",
        questions=["¿Hacen urgencias?", "¿Precio de limpieza?", "¿Aceptan seguro?"],
        keywords=["diente", "muela", "dolor", "caries", "brackets"],
        color="117"
    ),
    "veterinaria": Sector(
        id="veterinaria", name="Veterinaria", emoji="🐾",
        tagline="Cuidando a quien no puede llamar",
        services=["Consulta", "Vacunación", "Cirugía", "Peluquería", "Urgencias"],
        hours_default="08:00-20:00",
        questions=["¿Atienden urgencias 24h?", "¿Precio de consulta?", "¿Tienen pensión?"],
        keywords=["perro", "gato", "mascota", "vacuna", "enfermo"],
        color="114"
    ),
    "restaurante": Sector(
        id="restaurante", name="Restaurante", emoji="🍽️",
        tagline="Mesas llenas, cocina feliz",
        services=["Reservas", "Eventos", "Catering", "Menú del día", "Delivery"],
        hours_default="12:00-23:00",
        questions=["¿Tienen terraza?", "¿Menú vegetariano?", "¿Reserva para grupos?"],
        keywords=["reserva", "mesa", "cena", "almuerzo", "grupo"],
        color="221"
    ),
    "hotel": Sector(
        id="hotel", name="Hotel / Hospedaje", emoji="🏨",
        tagline="Reservas mientras duermes",
        services=["Habitaciones", "Suites", "Desayuno", "Spa", "Eventos"],
        hours_default="24h",
        questions=["¿Precio por noche?", "¿Incluye desayuno?", "¿Admiten mascotas?"],
        keywords=["habitación", "reserva", "noche", "disponibilidad", "check-in"],
        color="179"
    ),
    "gimnasio": Sector(
        id="gimnasio", name="Gimnasio / Fitness", emoji="💪",
        tagline="Membresías que se venden solas",
        services=["Membresía", "Personal trainer", "Clases grupales", "Nutrición"],
        hours_default="06:00-22:00",
        questions=["¿Precio mensual?", "¿Tienen piscina?", "¿Clases incluidas?"],
        keywords=["inscripción", "clase", "horario", "entrenador", "precio"],
        color="203"
    ),
    "belleza": Sector(
        id="belleza", name="Salón de Belleza", emoji="💇",
        tagline="Cada cita, una transformación",
        services=["Corte", "Color", "Manicure", "Pedicure", "Tratamientos capilares"],
        hours_default="09:00-20:00",
        questions=["¿Precio de mechas?", "¿Atienden sin cita?", "¿Tienen parking?"],
        keywords=["corte", "tinte", "uñas", "peinado", "cita"],
        color="177"
    ),
    "spa": Sector(
        id="spa", name="Spa / Wellness", emoji="🧖",
        tagline="Relax automatizado",
        services=["Masajes", "Faciales", "Circuito spa", "Aromaterapia", "Parejas"],
        hours_default="10:00-21:00",
        questions=["¿Paquetes para parejas?", "¿Duración del circuito?", "¿Promociones?"],
        keywords=["masaje", "relajación", "facial", "spa", "pareja"],
        color="141"
    ),
    "medico": Sector(
        id="medico", name="Consultorio Médico", emoji="🩺",
        tagline="Citas sin espera telefónica",
        services=["Consulta general", "Especialidades", "Estudios", "Certificados"],
        hours_default="08:00-17:00",
        questions=["¿Atienden mi seguro?", "¿Cuánto dura la cita?", "¿Necesito ayuno?"],
        keywords=["cita", "doctor", "consulta", "seguro", "estudios"],
        color="117"
    ),
    "psicologo": Sector(
        id="psicologo", name="Psicología / Terapia", emoji="🧠",
        tagline="El primer paso, más fácil",
        services=["Terapia individual", "Parejas", "Familiar", "Online", "Evaluaciones"],
        hours_default="09:00-20:00",
        questions=["¿Primera cita gratis?", "¿Terapia online?", "¿Cuánto dura la sesión?"],
        keywords=["terapia", "ansiedad", "sesión", "psicólogo", "ayuda"],
        color="135"
    ),
    "abogado": Sector(
        id="abogado", name="Despacho Legal", emoji="⚖️",
        tagline="Consultas que llegan solas",
        services=["Consulta inicial", "Divorcios", "Laboral", "Mercantil", "Penal"],
        hours_default="09:00-18:00",
        questions=["¿Primera consulta gratis?", "¿Manejan mi caso?", "¿Cuánto cobran?"],
        keywords=["abogado", "demanda", "divorcio", "consulta", "legal"],
        color="99"
    ),
    "inmobiliaria": Sector(
        id="inmobiliaria", name="Inmobiliaria", emoji="🏠",
        tagline="Visitas que se agendan solas",
        services=["Venta", "Renta", "Avalúos", "Administración", "Asesoría"],
        hours_default="09:00-19:00",
        questions=["¿Propiedades en X zona?", "¿Aceptan crédito?", "¿Puedo agendar visita?"],
        keywords=["casa", "departamento", "renta", "comprar", "visita"],
        color="179"
    ),
    "taller": Sector(
        id="taller", name="Taller Mecánico", emoji="🔧",
        tagline="Citas de servicio sin llamadas",
        services=["Servicio", "Diagnóstico", "Frenos", "Alineación", "Hojalatería"],
        hours_default="08:00-18:00",
        questions=["¿Cuánto tarda el servicio?", "¿Tienen refacciones?", "¿Precio aproximado?"],
        keywords=["carro", "coche", "servicio", "frenos", "ruido"],
        color="208"
    ),
    "academia": Sector(
        id="academia", name="Academia / Escuela", emoji="📚",
        tagline="Inscripciones automáticas",
        services=["Inscripción", "Cursos", "Clases particulares", "Certificaciones"],
        hours_default="08:00-20:00",
        questions=["¿Horarios disponibles?", "¿Precio del curso?", "¿Tienen becas?"],
        keywords=["curso", "clase", "inscripción", "horario", "nivel"],
        color="221"
    ),
    "nutricion": Sector(
        id="nutricion", name="Nutricionista", emoji="🥗",
        tagline="Consultas que transforman",
        services=["Consulta", "Plan alimenticio", "Seguimiento", "Estudios"],
        hours_default="08:00-18:00",
        questions=["¿Primera cita incluye plan?", "¿Consulta online?", "¿Cuánto dura?"],
        keywords=["dieta", "peso", "nutrición", "plan", "consulta"],
        color="114"
    ),
    "fisioterapia": Sector(
        id="fisioterapia", name="Fisioterapia", emoji="🦴",
        tagline="Rehabilitación sin esperas",
        services=["Evaluación", "Rehabilitación", "Masaje terapéutico", "Electroterapia"],
        hours_default="07:00-19:00",
        questions=["¿Cuántas sesiones necesito?", "¿Aceptan seguro?", "¿Precio por sesión?"],
        keywords=["dolor", "lesión", "rehabilitación", "sesión", "terapia"],
        color="117"
    ),
    "fotografia": Sector(
        id="fotografia", name="Fotografía / Estudio", emoji="📸",
        tagline="Sesiones que se agendan solas",
        services=["Sesión retrato", "Eventos", "Producto", "Bodas", "Books"],
        hours_default="10:00-19:00",
        questions=["¿Precio de sesión?", "¿Incluye edición?", "¿Cuántas fotos entrega?"],
        keywords=["sesión", "fotos", "boda", "retrato", "evento"],
        color="183"
    ),
    "coworking": Sector(
        id="coworking", name="Coworking", emoji="🏢",
        tagline="Espacios que se rentan solos",
        services=["Hot desk", "Oficina privada", "Sala de juntas", "Domicilio fiscal"],
        hours_default="08:00-20:00",
        questions=["¿Precio mensual?", "¿Incluye internet?", "¿Tienen estacionamiento?"],
        keywords=["oficina", "espacio", "escritorio", "renta", "sala"],
        color="141"
    ),
    "tattoo": Sector(
        id="tattoo", name="Estudio de Tatuaje", emoji="🎨",
        tagline="Arte que se agenda",
        services=["Tatuaje", "Cover up", "Piercing", "Diseño personalizado"],
        hours_default="12:00-21:00",
        questions=["¿Precio por hora?", "¿Cómo agendar?", "¿Tienen portafolio?"],
        keywords=["tatuaje", "diseño", "cita", "piercing", "cover"],
        color="99"
    ),
    "otro": Sector(
        id="otro", name="Otro / Personalizado", emoji="⚙️",
        tagline="Adaptable a cualquier negocio",
        services=["Personalizado"],
        hours_default="09:00-18:00",
        questions=[],
        keywords=[],
        color="248"
    ),
}

# ══════════════════════════════════════════════════════════════════════════════
# SISTEMA DE COLORES
# ══════════════════════════════════════════════════════════════════════════════
def _tty(): 
    return sys.stdout.isatty() or bool(os.getenv("FORCE_COLOR"))

def _e(c): 
    return f"\033[{c}m" if _tty() else ""

class C:
    R = _e("0")
    BOLD = _e("1")
    DIM = _e("2")
    ITALIC = _e("3")
    
    # Paleta principal - Morado y Rosa consistentes
    P1 = _e("38;2;139;92;246")   # Morado #8B5CF6
    P2 = _e("38;2;236;72;153")   # Rosa #EC4899
    P3 = _e("38;5;135")   # Púrpura medio
    P4 = _e("38;5;99")    # Púrpura profundo
    P5 = _e("38;5;57")    # Púrpura oscuro
    
    # Neutros
    W = _e("38;5;15")     # Blanco puro
    G0 = _e("38;5;252")   # Casi blanco
    G1 = _e("38;5;248")   # Gris claro
    G2 = _e("38;5;244")   # Gris medio
    G3 = _e("38;5;240")   # Gris oscuro
    G4 = _e("38;5;236")   # Gris muy oscuro
    
    # Semánticos
    GRN = _e("38;5;114")  # Verde
    RED = _e("38;5;203")  # Rojo
    YLW = _e("38;5;221")  # Amarillo
    CYN = _e("38;5;117")  # Cyan
    AMB = _e("38;5;179")  # Amber
    
    # Backgrounds
    BG_P = _e("48;5;57")
    BG_G = _e("48;5;236")

def q(color, text, bold=False):
    """Quick format."""
    return f"{C.BOLD if bold else ''}{color}{text}{C.R}"

def sector_color(sector_id: str) -> str:
    """Obtener color según sector."""
    s = SECTORS.get(sector_id, SECTORS["otro"])
    return _e(f"38;5;{s.color}")

# ══════════════════════════════════════════════════════════════════════════════
# LOGO ESTÁTICO CON PAC-MAN (ya comió parte del texto)
# ══════════════════════════════════════════════════════════════════════════════
def _get_terminal_width() -> int:
    try:
        return shutil.get_terminal_size().columns
    except Exception:
        return 80

def print_logo(compact=False, sector=None):
    brand_cmd = "firby" if "firby" in sys.argv[0].lower() else "firby"
    if compact:
        print()
        print(f"  {q(C.P1, '✦', bold=True)}  "
              f"{q(C.W, brand_cmd, bold=True)}  "
              f"{q(C.P2, f'v{VERSION}')}")
        print()
        return

    import subprocess
    from pathlib import Path
    
    logo_path = Path(os.environ.get("FIRBY_DIR", os.path.dirname(os.path.abspath(__file__)))) / "brand-assets" / "firby-logo.png"
    if logo_path.exists():
        try:
            # -c 256 for true colors, --symbols block
            result = subprocess.run(
                ["chafa", "--symbols", "block", "-c", "256", "--size", "50x25", str(logo_path)],
                capture_output=True, text=True, check=True
            )
            print()
            for line in result.stdout.splitlines():
                print("  " + line)
            print()
            return
        except:
            pass

    try:
        from src.firby.channels.logo_art import LOGO_ART_LINES
    except ImportError:
        try:
            from firby.channels.logo_art import LOGO_ART_LINES
        except ImportError:
            LOGO_ART_LINES = ["Firby"]

    C_BLUE = _e("38;2;59;130;246")
    
    sector_str = "Instance Manager"
    if sector:
        sector_str = f"Sector: {sector.capitalize()}"

    text_lines = [
        "",
        "",
        f"  {C.P1}{C.BOLD}Firby CLI {VERSION}{C.R}",
        f"  {C.P2}Autonomous Dynamic Receptionist{C.R}",
        f"  {C_BLUE}Target:{C.R} {C.W}Local Environment{C.R}",
        f"  {C_BLUE}Node:{C.R} {C.G1}{sector_str}{C.R}",
        f"  {C_BLUE}Status:{C.R} {C.G1}System Ready{C.R}",
        f"  {C_BLUE}~{C.R}"
    ]
    
    print()
    print(f"  {C.G4}{'─' * 100}{C.R}")
    print()
    max_len = max(len(LOGO_ART_LINES), len(text_lines))
    for i in range(max_len):
        left = LOGO_ART_LINES[i] if i < len(LOGO_ART_LINES) else " " * 18
        right = text_lines[i] if i < len(text_lines) else ""
        print(f"      {left}        {right}")
    print()
    print(f"  {C.G4}{'─' * 100}{C.R}")
    print()

def ok(m):    print(f"  {q(C.GRN, '✓')}  {q(C.W, _I18N.ui('success') + ': ' + str(m))}")
def fail(m):  print(f"  {q(C.RED, '✕')}  {q(C.W, _I18N.ui('error') + ': ' + str(m))}")
def warn(m):  print(f"  {q(C.YLW, '!')}  {q(C.G1, _I18N.ui('warning') + ': ' + str(m))}")
def info(m):  print(f"  {q(C.P2, '·')}  {q(C.G1, str(m))}")
def dim(m):   print(f"       {q(C.G3, m)}")
def nl():     print()
def hr():     print(f"  {q(C.G4, '─' * 54)}")

def section(title, sub="", icon="■"):
    """Sección con título."""
    print()
    print(f"  {q(C.P1, icon, bold=True)}  {q(C.W, title, bold=True)}")
    if sub:
        print(f"       {q(C.G2, sub)}")
    print()

def kv(key, val, color=None):
    """Key-value pair."""
    c = color or C.P2
    print(f"  {q(C.G2, f'{key:<20}')}  {q(c, str(val))}")

def box(title, content_lines, width=50):
    """Caja con borde."""
    print(f"  ┌{'─' * (width - 2)}┐")
    print(f"  │ {q(C.W, title.center(width - 4), bold=True)} │")
    print(f"  ├{'─' * (width - 2)}┤")
    for line in content_lines:
        padding = width - 4 - len(line.replace('\033[', '').split('m')[-1] if '\033[' in line else line)
        print(f"  │ {line}{' ' * max(0, padding)} │")
    print(f"  └{'─' * (width - 2)}┘")

def table(headers, rows, colors=None):
    """Tabla formateada."""
    if not rows:
        return
    
    _ansi_re = re.compile(r'\033\[[0-9;]*m')
    
    def _vis_len(s):
        return len(_ansi_re.sub('', str(s)))
    
    # Calcular anchos
    widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            if i < len(widths):
                widths[i] = max(widths[i], _vis_len(cell))
    
    # Header
    header_line = "  "
    for i, h in enumerate(headers):
        header_line += f"{q(C.G2, h.ljust(widths[i]))}  "
    print(header_line)
    print(f"  {q(C.G4, '─' * (sum(widths) + len(widths) * 2))}")
    
    # Rows
    for row in rows:
        line = "  "
        for i, cell in enumerate(row):
            c = colors[i] if colors and i < len(colors) else C.G1
            padding = widths[i] - _vis_len(cell)
            line += f"{q(c, str(cell))}{' ' * padding}  "
        print(line)

def progress_bar(current, total, width=30, label=""):
    """Barra de progreso estática."""
    pct = current / total if total > 0 else 0
    filled = int(width * pct)
    bar = f"{'█' * filled}{'░' * (width - filled)}"
    pct_str = f"{pct * 100:.0f}%"
    print(f"  {q(C.P2, bar)} {q(C.W, pct_str)} {q(C.G3, label)}")

def prompt(label, default="", secret=False):
    """Input con estilo."""
    d = f" [{default}]" if default else ""
    try:
        import getpass
        v = input(f"\n  {q(C.P2, '▸')}  {label}{q(C.G3, d)}  ") if secret else input(f"\n  {q(C.P2, '▸')}  {label}{q(C.G3, d)}  ")
    except (EOFError, KeyboardInterrupt):
        print()
        return default
    return v.strip() or default

def confirm(label, default=True):
    """Confirmación S/N."""
    d = "S/n" if default else "s/N"
    try:
        v = input(f"\n  {q(C.P2, '▸')}  {label} [{d}]  ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        print()
        return default
    return (v in ("s", "si", "sí", "y", "yes")) if v else default

def select(opts, descs=None, title="", icons=None):
    """Selector de opciones."""
    if title:
        print(f"\n  {q(C.G2, title)}")
    
    for i, o in enumerate(opts):
        num = q(C.P2, f"{i + 1}.", bold=True)
        icon = f"{icons[i]} " if icons and i < len(icons) else ""
        desc = f"  {q(C.G3, descs[i])}" if descs and i < len(descs) else ""
        print(f"    {num}  {icon}{q(C.W, o)}{desc}")
    
    while True:
        sys.stdout.write(f"\n  {q(C.P2, '→')}  ")
        sys.stdout.flush()
        try:
            v = input("").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return 0
        if v.isdigit() and 1 <= int(v) <= len(opts):
            return int(v) - 1
        warn("Escribe el número de la opción")

def multi_select(opts, descs=None, title=""):
    """Selector múltiple."""
    if title:
        print(f"\n  {q(C.G2, title)}")
    
    for i, o in enumerate(opts):
        num = q(C.P2, f"{i + 1}.", bold=True)
        desc = f"  {q(C.G3, descs[i])}" if descs and i < len(descs) else ""
        print(f"    {num}  {q(C.W, o)}{desc}")
    
    print(f"\n  {q(C.G3, 'Escribe números separados por coma (ej: 1,3,5) o todo')}")
    
    sys.stdout.write(f"\n  {q(C.P2, '→')}  ")
    sys.stdout.flush()
    try:
        v = input("").strip().lower()
    except (EOFError, KeyboardInterrupt):
        print()
        return []
    
    if v in ("todo", "all", "*"):
        return list(range(len(opts)))
    
    result = []
    for part in v.split(","):
        part = part.strip()
        if part.isdigit() and 1 <= int(part) <= len(opts):
            result.append(int(part) - 1)
    return result

# ══════════════════════════════════════════════════════════════════════════════
# SPINNER SIMPLE (para operaciones largas)
# ══════════════════════════════════════════════════════════════════════════════
class Spinner:
    """Spinner minimalista para operaciones largas."""
    
    FRAMES = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    
    def __init__(self, msg):
        self.msg = msg
        self._stop = threading.Event()
        self._thread = None
    
    def __enter__(self):
        self.start()
        return self
    
    def __exit__(self, *args):
        self.stop()
    
    def start(self):
        def _run():
            i = 0
            while not self._stop.is_set():
                frame = q(C.P2, self.FRAMES[i % len(self.FRAMES)], bold=True)
                sys.stdout.write(f"\r  {frame}  {q(C.G1, self.msg)}")
                sys.stdout.flush()
                time.sleep(0.1)
                i += 1
        
        self._thread = threading.Thread(target=_run, daemon=True)
        self._thread.start()
    
    def update(self, msg):
        self.msg = msg
    
    def stop(self, msg=None, success=True, ok=None):
        # ok= es alias de success= para compatibilidad
        if ok is not None:
            success = ok
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=0.2)

        icon = q(C.GRN, "✓") if success else q(C.RED, "✗")
        final_msg = msg or self.msg
        # Pad a 70 chars para limpiar cualquier basura del spinner anterior
        padded = f"{final_msg:<70}"
        sys.stdout.write(f"\r  {icon}  {q(C.W, padded)}\n")
        sys.stdout.flush()
    
    def finish(self, msg=None, ok=True):
        self.stop(msg, ok=ok)

# ══════════════════════════════════════════════════════════════════════════════
# HELPERS - Utilidades optimizadas
# ══════════════════════════════════════════════════════════════════════════════
@lru_cache(maxsize=32)
def load_env(path):
    """Cargar .env con caché."""
    env = {}
    try:
        p = Path(path)
        if not p.exists():
            return env
        for line in p.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, _, v = line.partition('=')
                env[k.strip()] = v.strip().strip('"').strip("'")
    except Exception:
        pass
    return env

def save_env(path, env_dict):
    """Guardar .env."""
    lines = []
    for k, v in env_dict.items():
        if '\n' in str(v):
            v = f'"{v}"'
        lines.append(f"{k}={v}")
    Path(path).write_text("\n".join(lines))
    load_env.cache_clear()

def update_env_key(path, key, val):
    """Actualizar una clave específica con quoting seguro para bash."""
    try:
        val_str = str(val)
        if (" " in val_str or "\n" in val_str or "$" in val_str) and not (
            (val_str.startswith("'") and val_str.endswith("'"))
            or (val_str.startswith('"') and val_str.endswith('"'))
        ):
            val_str = f"'{val_str}'"

        c = Path(path).read_text() if Path(path).exists() else ""
        if re.search(rf"^{key}=", c, re.MULTILINE):
            c = re.sub(rf"^{key}=.*$", f"{key}={val_str}", c, flags=re.MULTILINE)
        else:
            c += f"\n{key}={val_str}"
        Path(path).write_text(c)
        load_env.cache_clear()
    except Exception as e:
        warn(f".env no actualizado: {e}")


def workspace_defaults() -> Dict[str, Any]:
    return {
        "owner_name": "",
        "default_business_name": "",
        "default_sector": "",
        "default_platform": "telegram",
        "public_base_url": "",
        "telegram_token": "",
        "telegram_shared": False,
        "llm_keys": {
            "GROQ_API_KEY": "",
            "GEMINI_API_KEY": "",
            "GEMINI_API_KEY_2": "",
            "GEMINI_API_KEY_3": "",
            "GEMINI_API_KEY_4": "",
            "GEMINI_API_KEY_5": "",
            "GEMINI_API_KEY_6": "",
            "GEMINI_API_KEY_7": "",
            "OPENROUTER_API_KEY": "",
            "OPENAI_API_KEY": "",
        },
        "search_keys": {
            "SERP_API_KEY": "",
            "BRAVE_API_KEY": "",
            "APIFY_API_KEY": "",
        },
        "meta": {
            "META_APP_ID": "",
            "META_APP_SECRET": "",
        },
        "nova": {
            "url": f"http://localhost:{NOVA_PORT}",
            "api_key": "",
            "token": "",
            "enabled": False,
        },
        "omni": {
            "url": f"http://localhost:{OMNI_PORT}",
            "key": "",
        },
        "agent": {
            "display_name": "Firby",
            "role": "asesora virtual",
            "prompt_master": "",
        },
    }


def ensure_workspace_files() -> None:
    Path(FIRBY_HOME).mkdir(parents=True, exist_ok=True)
    Path(INSTANCES_DIR).mkdir(parents=True, exist_ok=True)
    if not WORKSPACE_CONFIG_PATH.exists():
        WORKSPACE_CONFIG_PATH.write_text(
            json.dumps(workspace_defaults(), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
    if not SHARED_TELEGRAM_ROUTES.exists():
        save_shared_telegram_routes({"default_instance": "", "routes": {}})


def load_workspace_config() -> Dict[str, Any]:
    defaults = workspace_defaults()
    if not WORKSPACE_CONFIG_PATH.exists():
        return defaults
    try:
        payload = json.loads(WORKSPACE_CONFIG_PATH.read_text(encoding="utf-8"))
    except Exception:
        return defaults
    if not isinstance(payload, dict):
        return defaults
    merged = json.loads(json.dumps(defaults))
    for key, value in payload.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key].update(value)
        else:
            merged[key] = value
    return merged


def save_workspace_config(data: Dict[str, Any]) -> None:
    ensure_workspace_files()
    WORKSPACE_CONFIG_PATH.write_text(
        json.dumps(data, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def workspace_is_configured() -> bool:
    config = load_workspace_config()
    return bool(
        str(config.get("default_business_name", "")).strip()
        or str(config.get("owner_name", "")).strip()
        or str(config.get("telegram_token", "")).strip()
        or any(str(v).strip() for v in config.get("llm_keys", {}).values())
    )


def runtime_defaults() -> Dict[str, Any]:
    config = load_workspace_config()
    legacy_env = load_env(f"{FIRBY_DIR}/.env")
    llm_keys = dict(config.get("llm_keys", {}))
    search_keys = dict(config.get("search_keys", {}))
    meta = dict(config.get("meta", {}))
    nova_cfg = dict(config.get("nova", {}))
    omni_cfg = dict(config.get("omni", {}))

    for key in llm_keys:
        llm_keys[key] = llm_keys.get(key) or legacy_env.get(key, "")
    for key in search_keys:
        search_keys[key] = search_keys.get(key) or legacy_env.get(key, "")
    for key in meta:
        meta[key] = meta.get(key) or legacy_env.get(key, "")

    nova_cfg["url"] = nova_cfg.get("url") or legacy_env.get("NOVA_URL", f"http://localhost:{NOVA_PORT}")
    nova_cfg["api_key"] = nova_cfg.get("api_key") or legacy_env.get("NOVA_API_KEY", "")
    nova_cfg["token"] = nova_cfg.get("token") or legacy_env.get("NOVA_TOKEN", "")
    if "NOVA_ENABLED" in legacy_env and not nova_cfg.get("enabled"):
        nova_cfg["enabled"] = legacy_env.get("NOVA_ENABLED", "false").lower() == "true"

    omni_cfg["url"] = omni_cfg.get("url") or legacy_env.get("OMNI_URL", f"http://localhost:{OMNI_PORT}")
    omni_cfg["key"] = omni_cfg.get("key") or legacy_env.get("OMNI_KEY", "")

    return {
        "workspace": config,
        "llm_keys": llm_keys,
        "search_keys": search_keys,
        "meta": meta,
        "nova": nova_cfg,
        "omni": omni_cfg,
        "public_base_url": str(config.get("public_base_url", "")).strip() or legacy_env.get("BASE_URL", "").strip(),
        "telegram_token": str(config.get("telegram_token", "")).strip() or legacy_env.get("TELEGRAM_TOKEN", "").strip(),
        "telegram_shared": bool(config.get("telegram_shared", False)),
        "default_platform": str(config.get("default_platform", "telegram")).strip() or "telegram",
        "default_business_name": str(config.get("default_business_name", "")).strip(),
        "default_sector": str(config.get("default_sector", "")).strip(),
    }


def load_shared_telegram_routes() -> Dict[str, Any]:
    default = {"default_instance": "", "routes": {}}
    if not SHARED_TELEGRAM_ROUTES.exists():
        return default
    try:
        data = json.loads(SHARED_TELEGRAM_ROUTES.read_text())
        if not isinstance(data, dict):
            return default
        if not isinstance(data.get("routes"), dict):
            data["routes"] = {}
        data.setdefault("default_instance", "")
        return data
    except Exception:
        return default


def save_shared_telegram_routes(data: Dict[str, Any]):
    SHARED_TELEGRAM_ROUTES.parent.mkdir(parents=True, exist_ok=True)
    SHARED_TELEGRAM_ROUTES.write_text(json.dumps(data, indent=2, ensure_ascii=False))


def ensure_shared_telegram_default(instance_name: str) -> Dict[str, Any]:
    routes = load_shared_telegram_routes()
    routes.setdefault("routes", {})
    if not routes.get("default_instance"):
        routes["default_instance"] = instance_name
        save_shared_telegram_routes(routes)
    return routes


def workspace_summary(config: Optional[Dict[str, Any]] = None) -> None:
    cfg = config or load_workspace_config()
    llm_active = [key for key, value in cfg.get("llm_keys", {}).items() if str(value).strip()]
    search_active = [key for key, value in cfg.get("search_keys", {}).items() if str(value).strip()]
    section("Workspace Firby", "Producto limpio y configurable")
    kv("Owner", cfg.get("owner_name", "") or "—")
    kv("Negocio por defecto", cfg.get("default_business_name", "") or "—")
    kv("Sector sugerido", cfg.get("default_sector", "") or "—")
    kv("Plataforma sugerida", cfg.get("default_platform", "telegram") or "telegram")
    kv("Base URL", cfg.get("public_base_url", "") or "—")
    kv("Telegram compartido", "sí" if cfg.get("telegram_shared") else "no")
    kv("Token Telegram", "configurado" if cfg.get("telegram_token") else "vacío")
    kv("LLM keys", ", ".join(llm_active) if llm_active else "ninguna")
    kv("Search keys", ", ".join(search_active) if search_active else "ninguna")
    kv("Agente", cfg.get("agent", {}).get("display_name", "Firby"))
    nl()


def edit_workspace_config() -> Dict[str, Any]:
    ensure_workspace_files()
    cfg = load_workspace_config()

    owner_name = prompt("Nombre del dueño o admin", default=cfg.get("owner_name", ""))
    business_name = prompt("Nombre del negocio por defecto", default=cfg.get("default_business_name", ""))
    sector_keys = list(SECTORS.keys())
    suggested_sector = str(cfg.get("default_sector", "") or "").strip()
    if confirm("¿Definir un sector por defecto para nuevas instancias?", default=bool(suggested_sector)):
        sector_labels = [f"{SECTORS[key].emoji} {SECTORS[key].name}" for key in sector_keys]
        sector_descs = [SECTORS[key].tagline for key in sector_keys]
        sector_idx = select(sector_labels, descs=sector_descs, title="Sector sugerido para nuevas instancias")
        cfg["default_sector"] = sector_keys[sector_idx]

    platform_options = ["telegram", "whatsapp", "ambos"]
    platform_descs = [
        "Empieza por Telegram con setup más simple.",
        "Prepara WhatsApp Business como canal principal.",
        "Deja todo listo para Telegram y WhatsApp.",
    ]
    platform_idx = select(
        ["Telegram", "WhatsApp", "Ambos"],
        descs=platform_descs,
        title="Canal sugerido para nuevas instancias",
    )
    cfg["default_platform"] = platform_options[platform_idx]

    public_base_url = prompt("Base URL pública por defecto", default=cfg.get("public_base_url", ""))
    telegram_token = prompt(
        "Token compartido de Telegram (opcional)",
        default=cfg.get("telegram_token", ""),
        secret=bool(cfg.get("telegram_token")),
    )
    telegram_shared = confirm("¿Usar router compartido de Telegram por defecto?", default=bool(cfg.get("telegram_shared")))

    llm_labels = [
        ("GROQ_API_KEY", "Groq"),
        ("GEMINI_API_KEY", "Gemini"),
        ("OPENROUTER_API_KEY", "OpenRouter"),
        ("OPENAI_API_KEY", "OpenAI"),
    ]
    if confirm("¿Configurar API keys LLM ahora?", default=any(cfg.get("llm_keys", {}).values())):
        for key, label in llm_labels:
            current = cfg["llm_keys"].get(key, "")
            cfg["llm_keys"][key] = prompt(f"{label} API key", default=current, secret=bool(current))

    if confirm("¿Configurar claves de búsqueda ahora?", default=any(cfg.get("search_keys", {}).values())):
        for key, label in [("BRAVE_API_KEY", "Brave Search"), ("SERP_API_KEY", "SerpAPI"), ("APIFY_API_KEY", "Apify")]:
            current = cfg["search_keys"].get(key, "")
            cfg["search_keys"][key] = prompt(f"{label} API key", default=current, secret=bool(current))

    cfg["owner_name"] = owner_name.strip()
    cfg["default_business_name"] = business_name.strip()
    cfg["public_base_url"] = public_base_url.strip()
    cfg["telegram_token"] = telegram_token.strip()
    cfg["telegram_shared"] = telegram_shared

    agent_cfg = dict(cfg.get("agent", {}))
    agent_cfg["display_name"] = prompt("Nombre base del agente", default=agent_cfg.get("display_name", "Firby")).strip() or "Firby"
    agent_cfg["role"] = prompt("Rol base del agente", default=agent_cfg.get("role", "asesora virtual")).strip() or "asesora virtual"
    agent_cfg["prompt_master"] = prompt(
        "Prompt maestro base (opcional)",
        default=agent_cfg.get("prompt_master", ""),
    ).strip()
    cfg["agent"] = agent_cfg

    save_workspace_config(cfg)
    ok(f"Workspace guardado en {WORKSPACE_CONFIG_PATH}")
    return cfg

def slug(name):
    """Convertir nombre a slug."""
    n = name.lower().strip()
    for a, b in [("á", "a"), ("é", "e"), ("í", "i"), ("ó", "o"), ("ú", "u"), ("ñ", "n")]:
        n = n.replace(a, b)
    return re.sub(r'[^a-z0-9]+', '-', n).strip('-')

def next_port():
    """Encontrar siguiente puerto disponible — evita puertos usados por instancias existentes."""
    import socket
    # Collect all ports already assigned to existing instances
    used_ports: Set[int] = {BASE_PORT}
    try:
        for inst in get_instances():
            used_ports.add(inst.port)
    except Exception:
        pass

    # También detectar puertos realmente en uso (socket bind fallará igual,
    # pero esto ayuda a filtrar rápido sin probar cada uno)
    for p in range(BASE_PORT + 1, MAX_PORT + 1):
        if p in used_ports:
            continue
        with socket.socket() as s:
            try:
                s.bind(("0.0.0.0", p))
                return p
            except OSError:
                pass
    return None

def health(port: int, timeout: float = 5) -> Dict:
    """Health check rápido."""
    url = f"http://localhost:{port}/health"
    try:
        if _HTTPX:
            r = _httpx.get(url, timeout=timeout)
            return r.json() if r.status_code == 200 else {}
        else:
            return json.loads(urllib.request.urlopen(url, timeout=timeout).read())
    except Exception:
        return {}

def _health_with_retry(port: int, max_retries: int = 5, delay: float = 1.5) -> Dict:
    """Health check con retry y backoff exponencial — para después de restart."""
    for attempt in range(max_retries):
        h = health(port, timeout=3)
        if h and h.get("status") == "online":
            return h
        wait = delay * (1.5 ** attempt)
        time.sleep(wait)
    return health(port, timeout=5)

def health_batch(ports, timeout=2):
    """Health check en paralelo."""
    results = {}
    with ThreadPoolExecutor(max_workers=20) as ex:
        futures = {ex.submit(health, p, timeout): p for p in ports}
        for f in as_completed(futures):
            port = futures[f]
            try:
                results[port] = f.result()
            except Exception:
                results[port] = {}
    return results

def pm2(cmd, name=""):
    """Ejecutar comando PM2."""
    args = ["pm2", cmd]
    if name:
        args.append(name)
    if cmd == "restart":
        args.append("--update-env")
    return subprocess.run(args, capture_output=True).returncode == 0

def pm2_save():
    subprocess.run(["pm2", "save"], capture_output=True)

def pm2_list():
    """Obtener lista de procesos PM2."""
    try:
        r = subprocess.run(["pm2", "jlist"], capture_output=True, text=True)
        if r.returncode == 0:
            return json.loads(r.stdout)
    except Exception:
        pass
    return []


def _pm2_start_runtime(pm2_name: str, inst_dir: str, log_path: str, error_path: str) -> subprocess.CompletedProcess:
    """Arrancar Firby siempre a través de run.sh para respetar VENV/runtime real."""
    run_script = Path(inst_dir) / "run.sh"
    if not run_script.exists():
        raise FileNotFoundError(f"run.sh no existe en {inst_dir}")
    try:
        run_script.chmod(run_script.stat().st_mode | 0o111)
    except Exception:
        pass
    return subprocess.run(
        [
            "pm2", "start", str(run_script),
            "--name", pm2_name,
            "--cwd", inst_dir,
            "--restart-delay", "3000",
            "--max-restarts", "10",
            "--log", str(log_path),
            "--error", str(error_path),
        ],
        capture_output=True,
        text=True,
    )

def public_ip():
    """Obtener IP pública."""
    try:
        if _HTTPX:
            return _httpx.get("https://api.ipify.org", timeout=5).text.strip()
        return urllib.request.urlopen("https://api.ipify.org", timeout=5).read().decode().strip()
    except Exception:
        return ""

def icon_status(h):
    """Icono de estado."""
    if not h:
        return q(C.RED, "●"), "offline"
    return (q(C.GRN, "●"), "online") if h.get("status") == "online" else (q(C.RED, "●"), "offline")

# ══════════════════════════════════════════════════════════════════════════════
# INSTANCIAS - Gestión centralizada
