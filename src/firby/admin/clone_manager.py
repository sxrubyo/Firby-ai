# -*- coding: utf-8 -*-
"""Administrador de clonación de instancias en caliente para recepcionistas virtuales."""
from __future__ import annotations
import os
import re
import json
import shutil
import secrets
import sqlite3
import logging
import asyncio
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional

log = logging.getLogger("firby.admin.clone_manager")

BASE_DIR = "/home/ubuntu/firby"
INSTANCES_DIR = "/home/ubuntu/firby/instances"

def get_next_port() -> int:
    """Busca el puerto más alto configurado en las instancias y suma 1."""
    highest_port = 8003  # Base/default
    try:
        if os.path.exists(INSTANCES_DIR):
            for item in os.listdir(INSTANCES_DIR):
                json_path = os.path.join(INSTANCES_DIR, item, "instance.json")
                if os.path.exists(json_path):
                    try:
                        with open(json_path, "r", encoding="utf-8") as f:
                            data = json.load(f)
                            port = int(data.get("port", 0))
                            if port > highest_port:
                                highest_port = port
                    except Exception:
                        pass
    except Exception as e:
        log.warning(f"Error calculando puerto: {e}")
    return highest_port + 1

async def clone_instance_programmatic(source_slug: str, dest_name: str, tg_token: Optional[str] = None) -> Dict[str, Any]:
    """
    Clona una instancia de recepcionista en caliente.
    1. Copia el runtime y BD.
    2. Limpia tablas de transacciones.
    3. Registra en PM2 y guarda.
    """
    dest_name_clean = dest_name.strip()
    dest_slug = re.sub(r'[^a-z0-9]', '-', dest_name_clean.lower())
    dest_slug = re.sub(r'-+', '-', dest_slug).strip('-')
    
    if not dest_slug:
        return {"ok": False, "error": "El nombre de la recepcionista no es válido."}
        
    source_dir = os.path.join(INSTANCES_DIR, source_slug)
    dest_dir = os.path.join(INSTANCES_DIR, dest_slug)
    
    if os.path.exists(dest_dir):
        return {"ok": False, "error": f"La recepcionista '{dest_name_clean}' (instancia: {dest_slug}) ya existe."}
        
    port = get_next_port()
    log.info(f"[clone_manager] Iniciando clonación {source_slug} -> {dest_slug} en puerto {port}")
    
    try:
        # Crear directorios
        os.makedirs(dest_dir, exist_ok=True)
        os.makedirs(os.path.join(dest_dir, "logs"), exist_ok=True)
        
        # Copiar archivos (excluyendo logs, sesiones antiguas y DBs directas)
        ignore_patterns = shutil.ignore_patterns("logs", "*.log", "sessions", "*.pid", "firby.db", "vectors.db", "__pycache__")
        for item in os.listdir(source_dir):
            s_path = os.path.join(source_dir, item)
            d_path = os.path.join(dest_dir, item)
            if os.path.isdir(s_path):
                if item not in ("logs", "sessions", "__pycache__"):
                    shutil.copytree(s_path, d_path, ignore=ignore_patterns)
            else:
                if not item.endswith((".log", ".db", ".pid")):
                    shutil.copy2(s_path, d_path)
                    
        # Copiar y limpiar la base de datos SQLite
        src_db = os.path.join(source_dir, "firby.db")
        dest_db = os.path.join(dest_dir, "firby.db")
        if os.path.exists(src_db):
            shutil.copy2(src_db, dest_db)
            # Limpiar datos transaccionales para el nuevo clon
            conn = sqlite3.connect(dest_db)
            try:
                conn.execute("DELETE FROM conversations;")
                conn.execute("DELETE FROM appointments;")
                conn.execute("DELETE FROM patients;")
                conn.execute("DELETE FROM admin_instructions;")
                
                # Actualizar el nombre de la clínica/agente en la tabla clinic
                cursor = conn.execute("SELECT persona_config FROM clinic WHERE id=1")
                row = cursor.fetchone()
                if row and row[0]:
                    try:
                        persona = json.loads(row[0])
                        persona["name"] = dest_name_clean
                        conn.execute("UPDATE clinic SET name=?, persona_config=? WHERE id=1", 
                                     (dest_name_clean, json.dumps(persona, ensure_ascii=False)))
                    except Exception:
                        conn.execute("UPDATE clinic SET name=? WHERE id=1", (dest_name_clean,))
                else:
                    conn.execute("UPDATE clinic SET name=? WHERE id=1", (dest_name_clean,))
                conn.commit()
            except Exception as dbe:
                log.error(f"[clone_manager] Error limpiando tablas en BD clonada: {dbe}")
            finally:
                conn.close()
                
        # Leer .env origen y construir nuevo .env
        src_env_path = os.path.join(source_dir, ".env")
        dest_env_path = os.path.join(dest_dir, ".env")
        env_vars = {}
        if os.path.exists(src_env_path):
            with open(src_env_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and "=" in line and not line.startswith("#"):
                        k, v = line.split("=", 1)
                        env_vars[k.strip()] = v.strip()
                        
        # Sobrescribir variables de la nueva instancia
        env_vars["PORT"] = str(port)
        env_vars["INSTANCE_ID"] = dest_slug
        env_vars["TELEGRAM_TOKEN"] = tg_token or ""
        env_vars["MASTER_API_KEY"] = secrets.token_hex(12)
        env_vars["WEBHOOK_SECRET"] = f"firby_{dest_slug}_{secrets.token_hex(6)}"
        env_vars["DB_PATH"] = dest_db
        env_vars["VECTOR_DB_PATH"] = os.path.join(dest_dir, "vectors.db")
        env_vars["WHATSAPP_BRIDGE_URL"] = ""  # Limpiar WhatsApp para evitar colisiones hasta que se vincule un número
        
        # Guardar .env
        with open(dest_env_path, "w", encoding="utf-8") as f:
            f.write(f"# Env generado para clon: {dest_name_clean}\n")
            for k, v in env_vars.items():
                f.write(f"{k}={v}\n")
                
        # Crear instance.json
        instance_json_path = os.path.join(dest_dir, "instance.json")
        with open(instance_json_path, "w", encoding="utf-8") as f:
            json.dump({
                "name": dest_slug,
                "label": dest_name_clean,
                "port": port,
                "cloned_from": source_slug,
                "created_at": sqlite3.connect(":memory:").execute("SELECT datetime('now')").fetchone()[0] + "Z"
            }, f, indent=2, ensure_ascii=False)
            
        # Registrar y arrancar en PM2
        pm2_name = f"firby-{dest_slug}"
        log.info(f"[clone_manager] Registrando en PM2: {pm2_name}")
        
        # Eliminar si existe previo
        subprocess.run(["pm2", "delete", pm2_name], capture_output=True)
        
        # Iniciar servicio nuevo
        run_script = os.path.join(dest_dir, "run.sh")
        start_cmd = [
            "pm2", "start", run_script,
            "--name", pm2_name,
            "--cwd", dest_dir
        ]
        
        proc = subprocess.run(start_cmd, capture_output=True, text=True)
        if proc.returncode != 0:
            log.error(f"[clone_manager] Error arrancando PM2: {proc.stderr}")
            return {"ok": False, "error": f"No se pudo arrancar la nueva recepcionista en PM2: {proc.stderr}"}
            
        # Guardar PM2
        subprocess.run(["pm2", "save"], capture_output=True)
        
        # Registrar Webhook en Telegram si hay token
        webhook_registered = False
        if tg_token:
            base_url = env_vars.get("BASE_URL")
            if base_url:
                webhook_url = f"{base_url}/webhook/{env_vars['WEBHOOK_SECRET']}?bot={dest_slug}"
                set_url = f"https://api.telegram.org/bot{tg_token}/setWebhook?url={webhook_url}"
                try:
                    # Hacemos la llamada HTTP de manera asíncrona
                    import httpx
                    async with httpx.AsyncClient(timeout=8.0) as client:
                        resp = await client.post(set_url)
                        if resp.status_code == 200 and resp.json().get("ok"):
                            webhook_registered = True
                except Exception as _wh_err:
                    log.warning(f"[clone_manager] Error registrando webhook en Telegram: {_wh_err}")
                    
        return {
            "ok": True,
            "name": dest_name_clean,
            "slug": dest_slug,
            "port": port,
            "webhook_registered": webhook_registered,
            "webhook_secret": env_vars["WEBHOOK_SECRET"]
        }
        
    except Exception as e:
        log.error(f"[clone_manager] Error general clonando instancia: {e}", exc_info=True)
        return {"ok": False, "error": f"Error técnico durante la clonación: {str(e)}"}
