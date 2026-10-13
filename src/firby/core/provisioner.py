# -*- coding: utf-8 -*-
"""
Firby Multi-Tenant Instance Provisioner
Creates isolated "habitaciones separadas" for each client upon registration with dedicated SQLite database, port allocation, and zero-drift code symlinking.
"""
from __future__ import annotations

import os
import re
import json
import secrets
import logging
import sqlite3
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

log = logging.getLogger("firby.provisioner")

BASE_DIR = Path("/home/ubuntu/firby")
INSTANCES_DIR = BASE_DIR / "instances"


def slugify(text: str) -> str:
    """Generates a clean URL and filesystem safe slug from business name."""
    s = text.lower().strip()
    s = re.sub(r"[áàäâ]", "a", s)
    s = re.sub(r"[éèëê]", "e", s)
    s = re.sub(r"[íìïî]", "i", s)
    s = re.sub(r"[óòöô]", "o", s)
    s = re.sub(r"[úùüû]", "u", s)
    s = re.sub(r"[ñ]", "n", s)
    s = re.sub(r"[^a-z0-9]+", "-", s)
    s = s.strip("-")
    return s or "instance"


def get_allocated_ports() -> Dict[str, int]:
    """Scans all instances and root to identify allocated ports."""
    ports = {"base": 8000}
    
    # Check base .env
    base_env = BASE_DIR / ".env"
    if base_env.exists():
        for line in base_env.read_text(encoding="utf-8", errors="ignore").splitlines():
            if line.strip().startswith("PORT="):
                try:
                    ports["base"] = int(line.split("=", 1)[1].strip())
                except Exception:
                    pass

    if INSTANCES_DIR.exists():
        for item in INSTANCES_DIR.iterdir():
            if item.is_dir() and (item / ".env").exists():
                for line in (item / ".env").read_text(encoding="utf-8", errors="ignore").splitlines():
                    if line.strip().startswith("PORT="):
                        try:
                            ports[item.name] = int(line.split("=", 1)[1].strip())
                        except Exception:
                            pass
    return ports


def get_next_available_port(start_port: int = 8010) -> int:
    """Finds the next unassigned port for new tenant instances."""
    used_ports = set(get_allocated_ports().values())
    # Reserve known system ports
    used_ports.update({5678, 8000, 8001, 8002, 8003, 8004, 8005, 8006, 8007, 8008, 9001})
    
    candidate = start_port
    while candidate in used_ports:
        candidate += 1
    return candidate


def provision_tenant_instance(
    business_name: str,
    email: str,
    phone: str,
    password_hash: str,
    name: str = "",
    sector: str = "salud",
    website: str = "",
    assistant_name: str = "Firby",
    tone: str = "humana_calida",
    start_pm2: bool = False,
) -> Dict[str, Any]:
    """
    Provisions a completely isolated tenant environment:
    1. Generates unique instance slug and directory in /home/ubuntu/firby/instances/{slug}/
    2. Zero-drift symlinks to shared src/ engine
    3. Initializes dedicated SQLite database with fresh schema
    4. Seeds clinic profile, admin user, and dev accounts
    5. Writes instance .env and instance.json metadata
    6. Registers in master database registry
    """
    INSTANCES_DIR.mkdir(parents=True, exist_ok=True)
    
    # 1. Generate unique slug
    base_slug = slugify(business_name)
    slug = base_slug
    counter = 2
    while (INSTANCES_DIR / slug).exists():
        slug = f"{base_slug}-{counter}"
        counter += 1
        
    instance_dir = INSTANCES_DIR / slug
    instance_dir.mkdir(parents=True, exist_ok=True)
    
    # 2. Setup zero-drift symlink for src directory
    src_target = BASE_DIR / "src"
    src_link = instance_dir / "src"
    if not src_link.exists():
        try:
            os.symlink(src_target, src_link, target_is_directory=True)
        except Exception as _sym_err:
            log.warning(f"Could not symlink src: {_sym_err}, copying instead")
            import shutil
            shutil.copytree(src_target, src_link, dirs_exist_ok=True)

    # 3. Determine Port & Secrets
    port = get_next_available_port()
    webhook_secret = f"firby_{slug}_{secrets.token_hex(8)}"
    master_key = secrets.token_hex(32)
    db_path = str(instance_dir / "firby.db")
    vectors_db_path = str(instance_dir / "vectors.db")
    
    # 4. Write isolated .env
    base_env_content = {}
    root_env_path = BASE_DIR / ".env"
    if root_env_path.exists():
        for line in root_env_path.read_text(encoding="utf-8", errors="ignore").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                base_env_content[k.strip()] = v.strip().strip("'").strip('"')

    env_lines = [
        f"# ═══════════════════════════════════════════════════════",
        f"# FIRBY TENANT INSTANCE: {business_name} ({slug})",
        f"# Created at: {datetime.utcnow().isoformat()}",
        f"# ═══════════════════════════════════════════════════════",
        f"PORT={port}",
        f"HOST=0.0.0.0",
        f"INSTANCE_ID={slug}",
        f"CLINIC_NAME=\"{business_name}\"",
        f"SECTOR={sector}",
        f"PLATFORM=whatsapp",
        f"BASE_URL=https://firbyai.lat",
        f"WHATSAPP_BRIDGE_URL=http://127.0.0.1:8002",
        f"WEBHOOK_SECRET={webhook_secret}",
        f"MASTER_API_KEY={master_key}",
        f"DB_PATH={db_path}",
        f"VECTOR_DB_PATH={vectors_db_path}",
        f"DEMO_MODE=true",
        f"DEMO_SESSION_TTL=1800",
        f"GREETING_ONLY_IDLE_SECONDS=20",
        f"BUFFER_WAIT_MIN=1",
        f"BUFFER_WAIT_MAX=3",
        "",
        "# LLM Providers",
        f"GEMINI_API_KEY={base_env_content.get('GEMINI_API_KEY', '')}",
        f"GEMINI_API_KEY_2={base_env_content.get('GEMINI_API_KEY_2', '')}",
        f"GEMINI_API_KEY_3={base_env_content.get('GEMINI_API_KEY_3', '')}",
        f"GEMINI_API_KEY_4={base_env_content.get('GEMINI_API_KEY_4', '')}",
        f"GEMINI_API_KEY_5={base_env_content.get('GEMINI_API_KEY_5', '')}",
        f"LLM_REASONING={base_env_content.get('LLM_REASONING', 'google/gemini-3.6-flash')}",
        f"LLM_FAST={base_env_content.get('LLM_FAST', 'google/gemini-3.5-flash')}",
        f"LLM_LITE={base_env_content.get('LLM_LITE', 'google/gemini-3.5-flash-lite')}",
        f"GROQ_API_KEY={base_env_content.get('GROQ_API_KEY', '')}",
        f"SERP_API_KEY={base_env_content.get('SERP_API_KEY', '')}",
        f"APIFY_API_KEY={base_env_content.get('APIFY_API_KEY', '')}",
        f"ELEVENLABS_API_KEY={base_env_content.get('ELEVENLABS_API_KEY', '')}",
    ]
    
    (instance_dir / ".env").write_text("\n".join(env_lines), encoding="utf-8")

    # 5. Initialize Dedicated SQLite Database & Seed Data
    from src.firby.brain.database import Database
    instance_db = Database(db_path=db_path, vector_db_path=vectors_db_path)
    
    try:
        instance_db.update_clinic(
            name=business_name,
            phone=phone,
            email=email,
            sector=sector,
            website=website,
            assistant_name=assistant_name,
            setup_done=1,
            onboarding_done=1,
        )
    except Exception as e:
        log.warning(f"Error seeding clinic in instance {slug}: {e}")

    try:
        with instance_db._conn() as c:
            c.execute("""
                INSERT OR REPLACE INTO admins (chat_id, email, password_hash, name, role, is_active)
                VALUES (?, ?, ?, ?, 'owner', 1)
            """, (email, email, password_hash, name or business_name))
    except Exception as e:
        log.warning(f"Error seeding admin in instance {slug}: {e}")

    try:
        instance_db.create_dev_account(email, password_hash)
    except Exception as e:
        log.warning(f"Error seeding dev account in instance {slug}: {e}")

    # 6. Write instance metadata JSON
    meta = {
        "slug": slug,
        "name": business_name,
        "email": email,
        "phone": phone,
        "sector": sector,
        "port": port,
        "webhook_secret": webhook_secret,
        "master_key": master_key,
        "created_at": datetime.utcnow().isoformat(),
        "is_active": True,
    }
    (instance_dir / "instance.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")

    # 7. Synchronize master databases
    for p in [BASE_DIR / "firby_ultra.db", BASE_DIR / "firby.db"]:
        if p.exists():
            try:
                with sqlite3.connect(str(p)) as conn:
                    conn.execute("CREATE TABLE IF NOT EXISTS dev_accounts (id INTEGER PRIMARY KEY AUTOINCREMENT, email TEXT UNIQUE NOT NULL, password_hash TEXT NOT NULL, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
                    conn.execute("INSERT INTO dev_accounts (email, password_hash) VALUES (?, ?) ON CONFLICT(email) DO UPDATE SET password_hash=excluded.password_hash", (email, password_hash))
                    
                    conn.execute("CREATE TABLE IF NOT EXISTS tenant_instances (id INTEGER PRIMARY KEY AUTOINCREMENT, slug TEXT UNIQUE NOT NULL, name TEXT, email TEXT, port INTEGER, dir_path TEXT, created_at TEXT)")
                    conn.execute("INSERT INTO tenant_instances (slug, name, email, port, dir_path, created_at) VALUES (?, ?, ?, ?, ?, ?) ON CONFLICT(slug) DO UPDATE SET port=excluded.port, email=excluded.email", (slug, business_name, email, port, str(instance_dir), datetime.utcnow().isoformat()))
                    conn.commit()
            except Exception as _sync_err:
                log.warning(f"Error syncing master database registry: {_sync_err}")

    # 8. Start PM2 process if requested
    pm2_name = f"firby-{slug}"
    if start_pm2:
        try:
            app_script = str(BASE_DIR / "src" / "interfaces" / "web" / "app.py")
            cmd = [
                "pm2", "start", app_script,
                "--name", pm2_name,
                "--cwd", str(instance_dir),
                "--interpreter", "python3",
                "--", "--port", str(port)
            ]
            subprocess.run(cmd, capture_output=True, timeout=15)
            log.info(f"PM2 process {pm2_name} started on port {port}")
        except Exception as _pm2_err:
            log.error(f"Error starting PM2 process for {slug}: {_pm2_err}")

    log.info(f"Successfully provisioned isolated tenant {slug} on port {port} at {instance_dir}")
    return {
        "ok": True,
        "slug": slug,
        "port": port,
        "instance_dir": str(instance_dir),
        "db_path": db_path,
        "master_key": master_key,
        "webhook_secret": webhook_secret,
        "pm2_name": pm2_name,
    }
