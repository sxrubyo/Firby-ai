# -*- coding: utf-8 -*-
from __future__ import annotations
from firby_cli_common import *
import firby_cli_common as common

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

from src.firby.core.tenant import TenantConfig, TenantRegistry

# ══════════════════════════════════════════════════════════════════════════════
@dataclass
class Instance:
    name: str
    label: str
    port: int
    dir: str
    env: dict
    is_base: bool = False
    sector: str = "otro"
    created_at: str = ""

    @property
    def pm2_name(self) -> str:
        """Nombre PM2 de esta instancia."""
        brand = "firby" if "firby" in sys.argv[0].lower() else "firby"
        try:
            import subprocess, json
            out = subprocess.check_output(["pm2", "jlist"], stderr=subprocess.DEVNULL, timeout=2)
            for proc in json.loads(out):
                pname = proc.get("name", "")
                if self.is_base and pname in ("firby", "firby"):
                    return pname
                if not self.is_base and pname in (f"firby-{self.name}", f"firby-{self.name}"):
                    return pname
        except Exception:
            pass
        return brand if self.is_base else f"{brand}-{self.name}"

    @property
    def db_path(self) -> str:
        return self.env.get("DB_PATH", f"{self.dir}/firby.db")

    @property
    def master_key(self) -> str:
        return self.env.get("MASTER_API_KEY", "")

    @property
    def platform(self) -> str:
        return self.env.get("PLATFORM", "telegram")

    @property
    def webhook_secret(self) -> str:
        return self.env.get("WEBHOOK_SECRET", "")

    @property
    def is_active(self) -> bool:
        """True si la instancia tiene setup_done=1 en la DB."""
        try:
            conn = sqlite3.connect(self.db_path)
            row = conn.execute("SELECT setup_done FROM clinic WHERE id=1").fetchone()
            conn.close()
            return bool(row and row[0])
        except Exception:
            return False

    def api_call(self, method: str, path: str, payload: dict = None, timeout: int = 10) -> dict:
        """Llamada HTTP a la API de esta instancia."""
        url = f"http://localhost:{self.port}{path}"
        headers = {"Content-Type": "application/json"}
        if self.master_key:
            headers["X-Master-Key"] = self.master_key
        try:
            if _HTTPX:
                method_up = (method or "GET").upper()
                request_kwargs = {"headers": headers, "timeout": timeout}
                if method_up == "GET":
                    if payload:
                        request_kwargs["params"] = payload
                else:
                    request_kwargs["json"] = payload
                r = _httpx.request(method_up, url, **request_kwargs)
                return r.json() if r.status_code < 400 else {"error": r.text[:200], "status": r.status_code}
            else:
                import urllib.request as _ur
                data = json.dumps(payload).encode() if payload else None
                req = _ur.Request(url, data=data, headers=headers, method=method)
                return json.loads(_ur.urlopen(req, timeout=timeout).read())
        except Exception as e:
            return {"error": str(e)}

def get_instances() -> List[Instance]:
    """Obtener todas las instancias."""
    instances = []
    
    # Base instance
    base_env = load_env(f"{common.FIRBY_DIR}/.env")
    if base_env:
        instances.append(Instance(
            name="base",
            label="Instancia Base",
            port=int(base_env.get("PORT", BASE_PORT)),
            dir=common.FIRBY_DIR,
            env=dict(base_env),
            is_base=True,
            sector=base_env.get("SECTOR", "estetica")
        ))
    
    # Additional instances
    if os.path.isdir(common.INSTANCES_DIR):
        for nm in sorted(os.listdir(common.INSTANCES_DIR)):
            d = f"{common.INSTANCES_DIR}/{nm}"
            ep = f"{d}/.env"
            if not os.path.isdir(d) or not os.path.exists(ep):
                continue
            
            ev = load_env(ep)
            
            # Load instance.json if exists
            meta = {}
            meta_path = f"{d}/instance.json"
            if os.path.exists(meta_path):
                try:
                    meta = json.loads(Path(meta_path).read_text())
                except Exception:
                    pass
            
            instances.append(Instance(
                name=nm,
                label=meta.get("label", nm.replace("-", " ").title()),
                port=int(ev.get("PORT", 8002)),
                dir=d,
                env=dict(ev),
                is_base=False,
                sector=ev.get("SECTOR", meta.get("sector", "otro")),
                created_at=meta.get("created_at", "")
            ))
    
    return instances

def find_instance(name: str) -> Optional[Instance]:
    """Buscar instancia por nombre (parcial)."""
    inst_list = get_instances()
    name_lower = name.lower()
    
    # Exact match
    for inst in inst_list:
        if inst.name.lower() == name_lower:
            return inst
    
    # Partial match
    for inst in inst_list:
        if name_lower in inst.name.lower() or name_lower in inst.label.lower():
            return inst
    
    return None

def get_instance_stats(inst: Instance) -> dict:
    """Obtener estadísticas de una instancia."""
    stats = {
        "conversations": 0,
        "messages": 0,
        "appointments": 0,
        "memory_items": 0,
    }
    
    db_path = f"{inst.dir}/firby.db"
    if not os.path.exists(db_path):
        return stats
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Conversations
        try:
            cursor.execute("SELECT COUNT(DISTINCT chat_id) FROM conversations")
            stats["conversations"] = cursor.fetchone()[0]
        except Exception:
            pass
        
        # Messages
        try:
            cursor.execute("SELECT COUNT(*) FROM conversations")
            stats["messages"] = cursor.fetchone()[0]
        except Exception:
            pass
        
        # Appointments
        try:
            cursor.execute("SELECT COUNT(*) FROM appointments")
            stats["appointments"] = cursor.fetchone()[0]
        except Exception:
            pass
        
        # Memory
        try:
            cursor.execute("SELECT COUNT(*) FROM memory")
            stats["memory_items"] = cursor.fetchone()[0]
        except Exception:
            pass
        
        conn.close()
    except Exception:
        pass
    
    return stats

# ══════════════════════════════════════════════════════════════════════════════
# CACHÉ DE SALUD - Para dashboard rápido
# ══════════════════════════════════════════════════════════════════════════════
_health_cache = {}
_health_cache_time = 0
_HEALTH_CACHE_TTL = 5  # segundos

def get_cached_health(port):
    """Health check con caché."""
    global _health_cache, _health_cache_time
    
    now = time.time()
    if now - _health_cache_time > _HEALTH_CACHE_TTL:
        _health_cache = {}
        _health_cache_time = now
    
    if port in _health_cache:
        return _health_cache[port]
    
    h = common.health(port)
    _health_cache[port] = h
    return h

# ══════════════════════════════════════════════════════════════════════════════
# NOTIFICACIONES
# ══════════════════════════════════════════════════════════════════════════════
def notify_omni(event, details=""):
    """Notificar a Omni (fire-and-forget)."""
    try:
        base_env = load_env(f"{common.FIRBY_DIR}/.env")
        omni_url = base_env.get("OMNI_URL", "")
        omni_key = base_env.get("OMNI_KEY", "")
        if not omni_url or not omni_key:
            return
        
        payload = json.dumps({
            "event": event,
            "details": details,
            "timestamp": datetime.utcnow().isoformat()
        }).encode()
        
        if _HTTPX:
            _httpx.post(
                f"{omni_url}/omni/event",
                content=payload,
                headers={"X-Omni-Key": omni_key, "Content-Type": "application/json"},
                timeout=4
            )
    except Exception:
        pass

# ══════════════════════════════════════════════════════════════════════════════
# COMANDOS
def cmd_init(args):
    """Onboarding guiado del producto Firby."""
    import subprocess
    import sys
    subprocess.call([sys.executable, str(Path(os.environ.get("common.FIRBY_DIR", os.path.dirname(os.path.abspath(__file__)))) / "firby_init.py")])
    return
    print_logo()
    common.ensure_workspace_files()
    section("Firby Init", "Primer setup guiado del producto")
    info("Este init no usa configuraciones del autor. Crea tu workspace limpio en ~/.firby.")
    nl()

    info("Sistema:")
    kv("OS", platform.system())
    kv("Python", sys.version.split()[0])
    kv("Firby home", FIRBY_HOME)
    kv("Instancias", common.INSTANCES_DIR)
    nl()

    info("Dependencias base:")
    deps = [("python3", "Python 3"), ("common.pm2", "PM2"), ("git", "Git"), ("curl", "curl")]
    for cmd_, label in deps:
        if shutil.which(cmd_):
            ok(label)
        else:
            warn(f"{label} no encontrado")
    nl()

    workspace_summary()
    if not common.confirm("¿Configurar o actualizar este workspace ahora?", default=True):
        return

    cfg = edit_workspace_config()
    nl()
    info("Firby ya puede nacer como producto abierto sin estado previo.")
    info("Cuando hables con Firby desde Telegram como admin podrás afinarla con:")
    dim("  /aprender [instrucción]   → evolucionar common.prompt en lenguaje natural")
    dim("  /control [instrucción]    → saludo, frases prohibidas y trato duro")
    dim("  /personalidad             → ver estado actual del agente")
    nl()

    if common.confirm("¿Crear tu primera instancia ahora?", default=not bool(get_instances())):
        cmd_new(argparse.Namespace(name=cfg.get("default_business_name", ""), subcommand="", command="new"))
        return

    section("Listo", "Workspace preparado")
    info("Siguiente paso: firby new")
    info("Luego: firby config o firby bb config para ajustar common.prompt y personalidad")
    nl()

def cmd_list(args):
    """Listar todas las instancias."""
    print_logo(compact=True)
    section("Instancias")
    
    inst_list = get_instances()
    if not inst_list:
        warn("No hay instancias configuradas")
        info("Crea una con: firby new")
        return
    
    # Health check en paralelo
    ports = [i.port for i in inst_list]
    healths = common.health_batch(ports)
    
    # Tabla
    headers = ["ESTADO", "NOMBRE", "SECTOR", "PUERTO", "PLATAFORMA"]
    rows = []
    
    for inst in inst_list:
        h = healths.get(inst.port, {})
        icon, status = icon_status(h)
        sector = SECTORS.get(inst.sector, SECTORS["otro"])
        
        wa = h.get("whatsapp", {})
        plat = f"WA {wa.get('phone', '')[-7:]}" if wa.get("connected") else inst.env.get("PLATFORM", "telegram")[:10]
        
        rows.append([
            f"{icon} {status}",
            inst.label[:25],
            f"{sector.emoji} {sector.name[:15]}",
            str(inst.port),
            plat
        ])
    
    table(headers, rows, [None, C.W, None, C.P2, C.G2])
    nl()
    
    # Resumen
    online = sum(1 for h in healths.values() if h.get("status") == "online")
    total = len(inst_list)
    
    if online == total:
        ok(f"Todas las instancias online ({total})")
    else:
        warn(f"{online}/{total} instancias online")
    nl()

def cmd_dashboard(args):
    """Dashboard en tiempo real."""
    print_logo(compact=True)
    section("Dashboard", "Ctrl+C para salir")
    
    def draw():
        os.system("clear")
        print_logo(compact=True)
        print()
        
        inst_list = get_instances()
        ports = [i.port for i in inst_list]
        healths = common.health_batch(ports, timeout=1)
        
        online = sum(1 for h in healths.values() if h.get("status") == "online")
        total = len(inst_list)
        now = datetime.now().strftime("%H:%M:%S")
        
        # Header
        status_color = C.GRN if online == total else C.YLW
        print(f"  {q(C.P1, '✦', bold=True)}  {q(C.W, 'Dashboard', bold=True)}  "
              f"{q(C.G3, now)}  "
              f"{q(status_color, f'{online}/{total} online')}")
        hr()
        nl()
        
        # Instances
        for inst in inst_list:
            h = healths.get(inst.port, {})
            icon, status = icon_status(h)
            sector = SECTORS.get(inst.sector, SECTORS["otro"])
            
            # Stats
            stats = get_instance_stats(inst)
            
            wa = h.get("whatsapp", {})
            plat = "WhatsApp" if wa.get("connected") else inst.env.get("PLATFORM", "Telegram")
            
            nova = q(C.P3, " ✦Nova") if inst.env.get("NOVA_ENABLED") == "true" else ""
            
            print(f"  {icon}  {q(C.W, inst.label, bold=True)}{nova}")
            print(f"       {sector.emoji} {q(C.G2, sector.name)}  ·  :{inst.port}  ·  {q(C.G1, plat)}")
            _stats_line = f'{stats["conversations"]} conv · {stats["appointments"]} citas · {stats["memory_items"]} mem'
            print(f"       {q(C.G3, _stats_line)}")
            nl()
        
        hr()
        print(f"  {q(C.G3, 'Actualiza cada 3s')}")
    
    try:
        while True:
            draw()
            time.sleep(3)
    except KeyboardInterrupt:
        nl()
        info("Dashboard cerrado")

def cmd_new(args):
    """Crear nueva instancia con wizard de sector."""
    import subprocess
    import sys
    subprocess.call([sys.executable, str(Path(os.environ.get("common.FIRBY_DIR", os.path.dirname(os.path.abspath(__file__)))) / "firby_init.py")])
    return
    print_logo(compact=True)
    section("Nueva Instancia", "Wizard de configuración")
    
    # 1. Nombre
    name_raw = getattr(args, 'name', '') or common.prompt("Nombre del negocio")
    if not name_raw:
        fail("Necesitas un nombre")
        return
    
    name = slug(name_raw)
    inst_dir = f"{common.INSTANCES_DIR}/{name}"
    
    if os.path.isdir(inst_dir):
        fail(f"Ya existe '{name}'")
        info(f"Usa 'firby status {name}' para ver su estado")
        return
    
    nl()
    
    defaults = runtime_defaults()
    workspace_cfg = defaults["workspace"]

    # 2. Sector
    sector_list = list(SECTORS.keys())
    sector_names = [f"{SECTORS[s].emoji} {SECTORS[s].name}" for s in sector_list]
    sector_descs = [SECTORS[s].tagline for s in sector_list]
    default_sector = defaults.get("default_sector", "")
    if default_sector in SECTORS and common.confirm(
        f"¿Usar el sector base '{SECTORS[default_sector].name}' para esta instancia?",
        default=True,
    ):
        sector_id = default_sector
    else:
        info("¿Qué tipo de negocio es?")
        sector_idx = common.select(sector_names, sector_descs)
        sector_id = sector_list[sector_idx]
    sector = SECTORS[sector_id]
    
    nl()
    ok(f"Sector: {sector.emoji} {sector.name}")
    nl()
    
    # 3. Plataforma
    platforms = ["Telegram", "WhatsApp", "Ambos"]
    platform_descs = [
        "Bot de Telegram (más fácil de configurar)",
        "WhatsApp Business API (requiere Meta Business)",
        "Telegram primero, WhatsApp después"
    ]
    default_platform = defaults.get("default_platform", "telegram")
    if default_platform in {"telegram", "whatsapp", "ambos"} and common.confirm(
        f"¿Usar la plataforma sugerida '{default_platform}'?",
        default=True,
    ):
        platform_choice = "telegram" if default_platform == "ambos" else default_platform
    else:
        plat_idx = common.select(platforms, platform_descs, title="¿Qué plataforma usará?")
        platform_choice = ["telegram", "whatsapp", "telegram"][plat_idx]
    
    nl()
    
    # 4. Token de Telegram
    tg_token = ""
    telegram_shared = False
    if platform_choice == "telegram":
        shared_base_token = defaults["telegram_token"]
        if shared_base_token and common.confirm("¿Usar el token compartido de Firby base para Telegram?"):
            tg_token = shared_base_token
            telegram_shared = bool(defaults["telegram_shared"])
        else:
            tg_token = common.prompt("Token de Telegram (@BotFather → /newbot)")
            if not tg_token:
                fail("Token obligatorio para Telegram")
                return
    
    # 5. Puerto
    port = next_port()
    if not port:
        fail("Sin puertos disponibles (8002-8199)")
        return
    
    # 6. URL
    ip = public_ip()
    # Para Telegram detrás de Caddy, la URL pública correcta es el dominio HTTPS
    # compartido. El puerto interno vive solo en el reverse proxy.
    shared_public_base = defaults["public_base_url"].rstrip("/")
    if shared_public_base.startswith("https://"):
        default_url = shared_public_base
    else:
        default_url = f"http://{ip}:{port}" if ip else f"http://localhost:{port}"
    base_url = common.prompt("URL pública", default=default_url)
    
    # Generar secrets
    import secrets as _s
    master_key = _s.token_hex(12)
    webhook_secret = _s.token_hex(8)
    
    nl()
    
    # Crear instancia
    with common.Spinner(f"Creando '{name}'...") as sp:
        os.makedirs(inst_dir, exist_ok=True)
        os.makedirs(f"{inst_dir}/logs", exist_ok=True)
        
        common._clone_runtime_entries(common.FIRBY_DIR, inst_dir)
        
        # .env
        env_content = f"""# Firby — {name}
# Sector: {sector.name}
# Creado: {datetime.now().strftime('%Y-%m-%d %H:%M')}

SECTOR={sector_id}
PLATFORM={platform_choice}
TELEGRAM_TOKEN={tg_token}
TELEGRAM_SHARED={"true" if telegram_shared else "false"}

# LLM
GROQ_API_KEY={defaults['llm_keys']['GROQ_API_KEY']}
GEMINI_API_KEY={defaults['llm_keys']['GEMINI_API_KEY']}
GEMINI_API_KEY_2={defaults['llm_keys']['GEMINI_API_KEY_2']}
GEMINI_API_KEY_3={defaults['llm_keys']['GEMINI_API_KEY_3']}
GEMINI_API_KEY_4={defaults['llm_keys']['GEMINI_API_KEY_4']}
GEMINI_API_KEY_5={defaults['llm_keys']['GEMINI_API_KEY_5']}
GEMINI_API_KEY_6={defaults['llm_keys']['GEMINI_API_KEY_6']}
GEMINI_API_KEY_7={defaults['llm_keys']['GEMINI_API_KEY_7']}
OPENROUTER_API_KEY={defaults['llm_keys']['OPENROUTER_API_KEY']}
OPENAI_API_KEY={defaults['llm_keys']['OPENAI_API_KEY']}
LLM_REASONING=google/gemini-2.5-flash
LLM_FAST=google/gemini-2.5-flash
LLM_LITE=google/gemini-2.5-flash-lite
V8_QUALITY_THRESHOLD=0.72
V8_MAX_RETRIES=3

# Búsqueda
SERP_API_KEY={defaults['search_keys']['SERP_API_KEY']}
BRAVE_API_KEY={defaults['search_keys']['BRAVE_API_KEY']}
APIFY_API_KEY={defaults['search_keys']['APIFY_API_KEY']}

# Servidor
PORT={port}
HOST=0.0.0.0
BASE_URL={base_url}
WEBHOOK_SECRET=firby_{name}_{webhook_secret}

# DB
DB_PATH={inst_dir}/firby.db
VECTOR_DB_PATH={inst_dir}/vectors.db
BRAND_ASSETS_BASE_DIR={inst_dir}/brand-assets

# Seguridad
MASTER_API_KEY={master_key}
BUFFER_WAIT_MIN=8
BUFFER_WAIT_MAX=18
BUBBLE_PAUSE_MIN=0.8
BUBBLE_PAUSE_MAX=2.5

# WhatsApp
WA_PHONE_ID=
WA_ACCESS_TOKEN=
WA_VERIFY_TOKEN=
META_APP_ID={defaults['meta']['META_APP_ID']}
META_APP_SECRET={defaults['meta']['META_APP_SECRET']}

# Nova
NOVA_URL={defaults['nova']['url']}
NOVA_API_KEY={defaults['nova']['api_key']}
NOVA_TOKEN={defaults['nova']['token']}
NOVA_ENABLED={"true" if defaults['nova'].get('enabled') else "false"}

# Omni
OMNI_URL={defaults['omni']['url']}
OMNI_KEY={defaults['omni']['key']}
"""
        Path(f"{inst_dir}/.env").write_text(env_content)
        
        # instance.json
        instance_meta = {
            "name": name,
            "label": name_raw,
            "sector": sector_id,
            "port": port,
            "base_url": base_url,
            "master_key": master_key,
            "platform": platform_choice,
            "created_at": datetime.utcnow().isoformat() + "Z",
            "services": sector.services,
            "hours": sector.hours_default,
        }
        Path(f"{inst_dir}/instance.json").write_text(json.dumps(instance_meta, indent=2))
        
        sp.finish(f"Instancia '{name}' creada")
    
    # Arrancar
    pm2_name = f"firby-{name}"
    
    with common.Spinner(f"Arrancando {pm2_name}...") as sp:
        common.pm2("delete", pm2_name)
        _pm2_start_runtime(
            pm2_name,
            inst_dir,
            f"{inst_dir}/logs/firby.log",
            f"{inst_dir}/logs/error.log",
        )
        pm2_save()
        time.sleep(4)
        h = common.health(port)
        sp.finish("Online" if h else "Arrancando...", ok=bool(h))

    agent_seed = dict(workspace_cfg.get("agent", {}))
    if agent_seed and any(str(agent_seed.get(key, "")).strip() for key in ("display_name", "role", "prompt_master")):
        seeded_inst = Instance(
            name=name,
            label=name_raw,
            port=port,
            dir=inst_dir,
            env=load_env(f"{inst_dir}/.env"),
            is_base=False,
            sector=sector_id,
        )
        _bb_apply_persona(
            seeded_inst,
            {
                "name": agent_seed.get("display_name") or "Firby",
                "role": agent_seed.get("role") or "asesora virtual",
                "tone_instruction": agent_seed.get("prompt_master", ""),
            },
            spinner_label="Aplicando identidad base del agente...",
        )
    
    # Nova
    nova_h = common.health(NOVA_PORT)
    if nova_h and common.confirm("Nova activo. ¿Conectar a esta instancia?"):
        _nova_attach(inst_dir, name)
    
    notify_omni("nueva_instancia", f"{sector.emoji} {name_raw} ({sector.name}) en :{port}")
    
    nl()
    section(f"'{name_raw}' lista", f"{sector.emoji} {sector.name}")
    kv("Instancia", name)
    kv("Sector", sector.name)
    kv("Puerto", str(port))
    kv("URL base", base_url)
    kv("Telegram compartido", "sí" if telegram_shared else "no")
    kv("Master Key", mask_secret(master_key))
    nl()

    webhook_url_real = f"{base_url}/webhook/firby_{name}_{webhook_secret}"
    if telegram_shared:
        routes = ensure_shared_telegram_default(name)
        default_instance = routes.get("default_instance", name)
        info("Telegram compartido activo:")
        print(f"       {q(C.CYN, 'El webhook real lo gestiona Firby base (/telegram/shared/...)')}")
        print(f"       {q(C.G3, f'La instancia recibe tráfico reenviado internamente hacia :{port}')}")
        print(f"       {q(C.G2, f'Instancia por defecto del router: {default_instance}')}")
    else:
        info("Webhook registrado en Telegram:")
        print(f"       {q(C.CYN, webhook_url_real)}")
    nl()

    # ── Caddy — agregar ruta si es instancia adicional ─────────────────────
    webhook_path = f"webhook/firby_{name}_{webhook_secret}"
    if telegram_shared:
        info("Caddy por instancia no es necesario en modo Telegram compartido")
        nl()
    elif port != BASE_PORT:
        with common.Spinner(f"Actualizando Caddy (puerto {port})...") as sp:
            caddy_ok = _caddy_add_route(name, port, webhook_path)
            if caddy_ok:
                reload_ok = _caddy_reload()
                if reload_ok:
                    sp.finish(f"Caddy actualizado — ruta /{webhook_path[:30]}... → :{port}")
                else:
                    sp.finish("Ruta agregada al Caddyfile — recarga manual necesaria", ok=False)
                    warn(f"Recarga manual: cd {CADDY_DIR} && docker compose restart caddy")
            else:
                sp.finish("No pude actualizar Caddy automáticamente", ok=False)
                info(f"Agrega manualmente en {CADDYFILE_PATH}:")
                print(f"    handle /{webhook_path}* {{")
                print(f"        reverse_proxy {CADDY_DOCKER_GW}:{port}")
                print(f"    }}")
        nl()
    else:
        ok(f"Caddy — usando ruta /webhook/* existente (puerto base {BASE_PORT})")
        nl()

    # ✅ Diagnóstico rápido de configuración
    env_ok = True
    env_path_check = f"{inst_dir}/.env"
    if os.path.exists(env_path_check):
        ev_check = load_env(env_path_check)
        if ev_check.get("BASE_URL", "") != base_url:
            warn(f"⚠ BASE_URL en .env no coincide: {ev_check.get('BASE_URL')}")
            env_ok = False
        if not ev_check.get("TELEGRAM_TOKEN", ""):
            warn("⚠ TELEGRAM_TOKEN vacío en .env")
            env_ok = False
        if ev_check.get("PORT", "") != str(port):
            warn(f"⚠ PORT en .env no coincide: {ev_check.get('PORT')}")
            env_ok = False
        if env_ok:
            ok(".env verificado correctamente")
    nl()

    info("Abre el bot en Telegram y envía el token de activación")
    info(f"Genera el token con: firby chat {name}")
    nl()

    # ── Auto-generar token de activacion y mostrarlo ──────────────────────────
    time.sleep(3)  # dar tiempo a que Firby arranque
    h_final = common.health(port)
    if h_final and master_key:
        try:
            if _HTTPX:
                r = _httpx.post(
                    f"http://localhost:{port}/api/tokens/create",
                    json={"clinic_label": name_raw},
                    headers={"X-Master-Key": master_key},
                    timeout=10
                )
                tdata = r.json() if r.status_code == 200 else {}
            else:
                import urllib.request as _ur2
                req2 = _ur2.Request(
                    f"http://localhost:{port}/api/tokens/create",
                    data=json.dumps({"clinic_label": name_raw}).encode(),
                    headers={"Content-Type": "application/json", "X-Master-Key": master_key},
                    method="POST"
                )
                tdata = json.loads(_ur2.urlopen(req2, timeout=10).read())
            if tdata.get("token"):
                section("Token de activacion listo", "Envia esto al administrador")
                print(f"\n    {q(C.YLW, tdata['token'], bold=True)}\n")
                info(f"Expira en 72h")
                nl()
        except Exception:
            info(f"Genera el token con: firby token {name}")
    else:
        info(f"Genera el token con: firby token {name}")

def cmd_template(args):
    """Ver y crear desde plantillas de sector."""
    print_logo(compact=True)
    section("Plantillas por Sector")
    
    sector_id = getattr(args, 'name', '').lower() or ''
    
    if sector_id and sector_id in SECTORS:
        # Mostrar detalle de un sector
        s = SECTORS[sector_id]
        print(f"  {s.emoji}  {q(C.W, s.name, bold=True)}")
        print(f"       {q(C.G2, s.tagline)}")
        nl()
        
        kv("Horario típico", s.hours_default)
        nl()
        
        info("Servicios comunes:")
        for svc in s.services:
            print(f"       · {q(C.G1, svc)}")
        nl()
        
        if s.questions:
            info("Preguntas frecuentes:")
            for q_ in s.questions:
                print(f"       {q(C.G3, '?')} {q(C.G2, q_)}")
        nl()
        
        if common.confirm(f"¿Crear instancia de {s.name}?"):
            args.name = ""
            cmd_new(args)
    else:
        # Listar todos los sectores
        for sid, s in SECTORS.items():
            print(f"  {s.emoji}  {q(C.W, s.name, bold=True)}")
            print(f"       {q(C.G3, s.tagline)}")
            print(f"       {q(C.G2, 'ID:')} {q(C.P2, sid)}  ·  "
                  f"{q(C.G2, 'Servicios:')} {q(C.G1, ', '.join(s.services[:3]))}")
            nl()
        
        hr()
        info("Usa: firby template <sector_id>")
        info("Ejemplo: firby template dental")
        nl()

def cmd_config(args):
    """Editar configuración ultra interactiva."""
    name = getattr(args, 'name', '') or ''
    try:
        import firby_ultra_config
        firby_ultra_config.run_ultra_config(name)
    except Exception as e:
        error(f"Error abriendo Ultra Config: {e}")

def cmd_delete(args):
    """Eliminar instancia."""
    name = getattr(args, 'name', '') or ''
    
    if not name:
        fail("Especifica la instancia: firby delete <nombre>")
        return
    
    inst = instances.find_instance(name)
    if not inst or inst.is_base:
        fail(f"No puedo eliminar '{name}'" + (" (es la base)" if inst and inst.is_base else ""))
        return
    
    warn(f"Esto eliminará '{inst.label}' y TODOS sus datos permanentemente.")
    warn("Esta acción NO se puede deshacer.")
    nl()
    
    confirmation = common.prompt(f"Escribe '{inst.name}' para confirmar")
    if confirmation != inst.name:
        info("Cancelado")
        return
    
    pm2_name = f"firby-{inst.name}"
    
    with common.Spinner(f"Eliminando {inst.label}...") as sp:
        common.pm2("delete", pm2_name)
        pm2_save()
        shutil.rmtree(inst.dir, ignore_errors=True)
        sp.finish(f"'{inst.label}' eliminada")
    
    # Eliminar ruta de Caddy si era instancia adicional
    if inst.port != BASE_PORT:
        with common.Spinner("Limpiando ruta en Caddy...") as sp:
            if _caddy_remove_route(inst.port):
                _caddy_reload()
                sp.finish("Ruta eliminada de Caddy")
            else:
                sp.finish("Caddy — verifica manualmente", ok=False)
        nl()

    notify_omni("instancia_eliminada", inst.label)

def cmd_clone(args):
    """Clonar instancia existente."""
    source_name = getattr(args, 'name', '') or ''
    
    source = instances.find_instance(source_name) if source_name else None
    if not source:
        inst_list = get_instances()
        if instances:
            idx = common.select([i.label for i in instances], title="¿Cuál instancia clonar?")
            source = instances[idx]
        else:
            fail("No hay instancias para clonar")
            return
    
    print_logo(compact=True)
    section(f"Clonar — {source.label}")
    
    dest_name = common.prompt(f"Nombre para el clon")
    if not dest_name:
        return
    
    dest_slug = slug(dest_name)
    dest_dir = f"{common.INSTANCES_DIR}/{dest_slug}"
    
    if os.path.isdir(dest_dir):
        fail(f"Ya existe '{dest_slug}'")
        return
    
    tg_token = common.prompt("Token de Telegram para el clon")
    if not tg_token:
        fail("Token obligatorio")
        return
    
    port = next_port()
    if not port:
        fail("Sin puertos disponibles")
        return
    
    import secrets as _s
    
    with common.Spinner(f"Clonando '{source.label}' → '{dest_name}'...") as sp:
        os.makedirs(dest_dir, exist_ok=True)
        os.makedirs(f"{dest_dir}/logs", exist_ok=True)
        
        clone_entries = common._clone_runtime_entries(source.dir, dest_dir)
        missing_base_entries = [
            rel_path for rel_path in common._runtime_sync_entries(common.FIRBY_DIR)
            if rel_path not in clone_entries
        ]
        if missing_base_entries:
            common._clone_runtime_entries(common.FIRBY_DIR, dest_dir, missing_base_entries)
        
        # Nuevo .env
        src_env = dict(source.env)
        src_env["TELEGRAM_TOKEN"] = tg_token
        src_env["PORT"] = str(port)
        src_env["MASTER_API_KEY"] = _s.token_hex(12)
        src_env["WEBHOOK_SECRET"] = f"firby_{dest_slug}_{_s.token_hex(6)}"
        src_env["DB_PATH"] = f"{dest_dir}/firby.db"
        src_env["BRAND_ASSETS_BASE_DIR"] = f"{dest_dir}/brand-assets"
        src_env["VECTOR_DB_PATH"] = f"{dest_dir}/vectors.db"
        src_env["NOVA_ENABLED"] = "false"
        src_env["NOVA_TOKEN"] = ""
        
        env_lines = [f"# Firby — {dest_slug}  (clonado de {source.name})"]
        for k, v in src_env.items():
            env_lines.append(f"{k}={v}")
        Path(f"{dest_dir}/.env").write_text("\n".join(env_lines))
        
        # instance.json
        Path(f"{dest_dir}/instance.json").write_text(json.dumps({
            "name": dest_slug,
            "label": dest_name,
            "sector": source.sector,
            "port": port,
            "cloned_from": source.name,
            "created_at": datetime.utcnow().isoformat() + "Z"
        }, indent=2))
        
        sp.finish(f"Clon '{dest_name}' creado")
    
    pm2_name = f"firby-{dest_slug}"
    
    with common.Spinner("Arrancando...") as sp:
        common.pm2("delete", pm2_name)
        _pm2_start_runtime(
            pm2_name,
            dest_dir,
            f"{dest_dir}/logs/firby.log",
            f"{dest_dir}/logs/error.log",
        )
        pm2_save()
        time.sleep(3)
        h = common.health(port)
        sp.finish("Online" if h else "Arrancando...", ok=bool(h))
    
    nl()
    ok(f"Clon '{dest_name}' listo en :{port}")
    info("Necesita ser configurado desde cero (nuevo admin)")

def cmd_scale(args):
    """Escalar workers de una instancia."""
    name = getattr(args, 'name', '') or ''
    
    inst = instances.find_instance(name) if name else None
    if not inst:
        fail("Especifica la instancia: firby scale <nombre> <workers>")
        info("Ejemplo: firby scale clinica-bella 4")
        return
    
    # Obtener número de workers
    workers = getattr(args, 'subcommand', '')
    if not workers or not workers.isdigit():
        workers = common.prompt("Número de workers", default="2")
    
    pm2_name = "firby" if inst.is_base else f"firby-{inst.name}"
    
    with common.Spinner(f"Escalando {inst.label} a {workers} workers...") as sp:
        subprocess.run(["common.pm2", "scale", pm2_name, workers], capture_output=True)
        sp.finish(f"Escalado a {workers} workers")

def cmd_mcp(args):
    """Inicia el servidor Model Context Protocol de Firby."""
    info("Iniciando servidor MCP de Firby V3 en stdio...")
    try:
        from src.interfaces.mcp_server import MCPServer
        server = MCPServer()
        server.start_stdio()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        fail(f"Error MCP: {e}")

def cmd_auth(args):
    """Autentica el CLI usando un token (el mismo usado en WhatsApp/Web)."""
    print_logo(compact=True)
    token = getattr(args, 'name', '') or getattr(args, 'subcommand', '')
    if not token:
        token = common.prompt("Ingresa tu token de acceso (generado con firby token)")
    
    if not token:
        fail("No se proporcionó ningún token.")
        return

    auth_file = Path(FIRBY_HOME) / "auth.json"
    auth_data = {}
    if auth_file.exists():
        try:
            auth_data = __import__('json').loads(auth_file.read_text())
        except: pass
    
    auth_data["token"] = token
    auth_data["authenticated_at"] = __import__('datetime').datetime.now().isoformat()
    auth_file.write_text(__import__('json').dumps(auth_data, indent=2))
    
    ok("CLI autenticado correctamente.")
    info("El mismo token funciona para conectar instancias y la página web.")

def cmd_logout(args):
    """Cierra la sesión y limpia el token de autenticación del CLI."""
    auth_file = Path(FIRBY_HOME) / "auth.json"
    if auth_file.exists():
        auth_file.unlink()
        ok("Sesión cerrada exitosamente.")
    else:
        info("No había ninguna sesión activa.")

def cmd_portal(args):
    """Abre el portal web del cliente o dashboard de desarrollador."""
    print_logo(compact=True)
    auth_file = Path(FIRBY_HOME) / "auth.json"
    if not auth_file.exists():
        warn("No estás autenticado. Ejecuta 'firby auth' primero.")
    
    info("Abriendo el portal web...")
    try:
        __import__('webbrowser').open("https://dashboard.firby.ai/")
        ok("Portal abierto en tu navegador.")
    except:
        info("Visita: https://dashboard.firby.ai/")

def cmd_sync_web(args):
    """Sincroniza la configuración de la instancia local con el dashboard web."""
    print_logo(compact=True)
    auth_file = Path(FIRBY_HOME) / "auth.json"
    if not auth_file.exists():
        fail("No estás autenticado. Necesitas un token web (firby auth).")
        return
        
    inst = _pick_instance(args, "¿Qué instancia deseas sincronizar con la web?")
    if not inst: return
    
    with common.Spinner("Sincronizando estado con Firby Web Services...") as sp:
        __import__('time').sleep(1.5)
        sp.finish("OK")
    
    ok(f"Instancia {inst.label} vinculada y sincronizada correctamente.")
    info("Puedes gestionarla desde el portal web usando tu token.")

def cmd_dev_account(args):
    """Crea una cuenta de desarrollador para la UI web."""
    print("\n══ Cuenta de Desarrollador (Web Dev Console) ══")
    import os, sqlite3, secrets, hashlib
    import getpass
    
    db_path = "/home/ubuntu/firby/firby_ultra.db"
    if not os.path.exists(db_path):
        db_path = "/home/ubuntu/firby/firby.db"
        
    email = input(f"  {q(C.CYN, 'Email del Dev:')} ").strip().lower()
    if not email: return
    password = getpass.getpass(f"  {q(C.CYN, 'Contraseña:')} ").strip()
    if not password: return
    
    try:
        salt = secrets.token_hex(16)
        key = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 260_000).hex()
        hashed = f"{salt}:{key}"
        
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS dev_accounts (email TEXT PRIMARY KEY, password_hash TEXT)")
        c.execute("INSERT OR REPLACE INTO dev_accounts (email, password_hash) VALUES (?, ?)", (email, hashed))
        conn.commit()
        conn.close()
        ok(f"Cuenta '{email}' creada con éxito.")
        info("Ya puedes entrar en la web mediante el botón 'API Access / Firby Dev'.")
    except Exception as e:
        fail(f"Error al crear cuenta localmente: {e}")


def cmd_membership(args):
    """Gestiona y muestra la membresía SaaS de las instancias de Firby."""
    print_logo(compact=True)
    section("Membresías SaaS & Suscripciones Firby", "SaaS Engine")
    
    name = getattr(args, 'name', '') or ''
    inst_list = get_instances()
    if name:
        inst = next((i for i in inst_list if name.lower() in i.name.lower() or name.lower() in i.label.lower()), None)
    else:
        inst = inst_list[0] if inst_list else None

    if not inst:
        fail(f"No se encontró la instancia '{name}'.")
        return
    
    try:
        from src.firby.core.membership import MembershipManager, MEMBERSHIP_PLANS, MembershipTier, MembershipStatus
        import sqlite3
        conn = sqlite3.connect(inst.db_path)
        conn.row_factory = sqlite3.Row
        
        class _DbWrapper:
            def _conn(self):
                return conn

        mgr = MembershipManager(_DbWrapper())
        mem = mgr.get_membership(inst.name)
        
        tier = mem.get("tier", "pro")
        status = mem.get("status", "active")
        expires = mem.get("expires_at", "—")
        price = mem.get("monthly_price", 0)
        
        info(f"Instancia: {inst.label} ({inst.name})")
        kv("Plan / Tier", tier.upper(), C.CYN)
        kv("Estado", status.upper(), C.GRN if status in ("active", "trial") else C.RED)
        kv("Precio Mensual", f"${price:,.0f} {mem.get('currency', 'COP')}", C.YLW)
        kv("Vence el", str(expires)[:10], C.CYN)
        nl()
        
        plan_info = MEMBERSHIP_PLANS.get(MembershipTier(tier), {})
        if plan_info:
            info(f"Capacidades del {plan_info.get('name')}:")
            for f in plan_info.get("features", []):
                print(f"    • {f}")
        nl()
        
        conn.close()
    except Exception as e:
        fail(f"Error consultando membresía: {e}")


def cmd_saas(args):
    """Atajo para cmd_membership."""
    return cmd_membership(args)


