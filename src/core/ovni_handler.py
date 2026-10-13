"""
ovni_handler.py — Handler exclusivo para el agente técnico OVNI.

OVNI no es una instancia de Firby ni un bot de recepcionista.
Es el centro de operaciones del ecosistema: crea instancias, diagnostica,
orquesta agentes, y atiende SOLO al administrador (Santiago o un dev autorizado).

Características:
- Solo el admin puede interactuar. Desconocidos reciben silencio.
- Usa LLM con system prompt técnico cargado desde ovni.yaml
- Tiene acceso al estado de todas las instancias del sistema
- Puede ejecutar acciones: listar instancias, revisar logs, activar/desactivar demo
- Sin frases de recepcionista. Sin "Hola soy Firby". Nunca.
"""
from __future__ import annotations

import json
import logging
import os
import re
import subprocess
import time
from typing import Any, Dict, List, Optional, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    pass

log = logging.getLogger("firby.ovni")

# ─── Persona de OVNI ─────────────────────────────────────────────────────────

OVNI_SYSTEM_PROMPT = """\
Eres Dumi, la mano derecha técnica de Santiago. Sos el que orquesta todo el ecosistema Firby.

CAPACIDADES:
- Tenés acceso completo a la API de n8n. Cuando Santiago te pida algo relacionado, usá el formato:
  [CMD:N8N:METHOD:endpoint:body_json]
  Ej: [CMD:N8N:GET:/api/v1/workflows:]
  Ej: [CMD:N8N:PATCH:/api/v1/workflows/ID:{{"active": true}}]

- Podés activar/desactivar demo en instancias:
  [CMD:DEMO:nombre-instancia:ON]  o  [CMD:DEMO:nombre-instancia:OFF]

- Podés reiniciar procesos PM2:
  [CMD:RESTART:nombre-proceso]

- Podés ejecutar comandos de consola:
  [CMD:SHELL:comando]

- Podés orquestar tareas de desarrollo con Codex:
  [CMD:CODEX:instrucción]

- Si tu respuesta es muy larga, separala en partes con ||| para que llegue como mensajes separados.

REGLAS:
- Solo hablás con Santiago o devs autorizados.
- NUNCA te presentes como "copiloto inteligente" ni repitas frases hechas. Soná natural, como un colega.
- Si algo del sistema necesita atención, decilo sin que te lo pidan.
- NO uses lenguaje de recepcionista ni call center.

ESTADO DEL SISTEMA:
{system_state}

HISTORIAL:
{history_txt}
"""

OVNI_FIRST_TURN = "Dumi acá. ¿Qué necesitás?"


# ─── Lectura del estado del sistema ──────────────────────────────────────────

def _get_system_state() -> str:
    """Genera un resumen del estado de todas las instancias."""
    lines = []
    try:
        result = subprocess.run(
            ["pm2", "jlist"], capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            processes = json.loads(result.stdout)
            for proc in processes:
                name = proc.get("name", "?")
                status = proc.get("pm2_env", {}).get("status", "?")
                restarts = proc.get("pm2_env", {}).get("restart_time", 0)
                memory = proc.get("monit", {}).get("memory", 0)
                mem_mb = round(memory / 1024 / 1024, 1) if memory else 0
                lines.append(f"• {name}: {status} | reintentos={restarts} | mem={mem_mb}MB")
    except Exception as e:
        lines.append(f"(no pude leer pm2: {e})")

    # Instancias registradas
    try:
        registry_path = "/home/ubuntu/firby/instances.registry.json"
        if os.path.exists(registry_path):
            registry = json.loads(open(registry_path).read())
            if isinstance(registry, list):
                instance_names = [i.get("name", "?") for i in registry]
                lines.append(f"Instancias registradas: {', '.join(instance_names)}")
    except Exception:
        pass

    return "\n".join(lines) if lines else "(sin datos de sistema)"


def _build_history_txt(history: List[Dict]) -> str:
    if not history:
        return "(sin historial)"
    lines = []
    for h in history[-6:]:
        role = "Admin" if h.get("role") == "user" else "Ovni"
        content = str(h.get("content", ""))[:300]
        lines.append(f"{role}: {content}")
    return "\n".join(lines)


# ─── Detección de comandos rápidos ───────────────────────────────────────────

def _find_instance_dir(name: str) -> Optional[Tuple[str, str, str]]:
    """
    Busca una instancia que coincida con 'name' en instances/ o agents/.
    Devuelve Tuple (tipo, ruta_absoluta, nombre_carpeta) o None.
    Soporta búsqueda por tokens/palabras clave parciales.
    """
    name_clean = name.strip().lower().replace("firby-", "")
    # Separar en palabras clave individuales
    search_tokens = [t for t in re.split(r"[-\s_]", name_clean) if t]
    if not search_tokens:
        return None
    
    # Directorios base
    base_dirs = {
        "instance": "/home/ubuntu/firby/instances",
        "agent": "/home/ubuntu/firby/agents"
    }
    
    candidates = []
    for kind, base in base_dirs.items():
        if not os.path.exists(base):
            continue
        for folder in os.listdir(base):
            if folder == "_template":
                continue
            folder_path = os.path.join(base, folder)
            if not os.path.isdir(folder_path):
                continue
            
            folder_lower = folder.lower()
            # Match exacto
            if folder_lower == name_clean:
                return (kind, folder_path, folder)
            
            # Match si todos los tokens buscados existen en el nombre del directorio
            if all(token in folder_lower for token in search_tokens):
                candidates.append((kind, folder_path, folder))
                
    if candidates:
        # Ordenar por el que tenga la longitud más parecida al término de búsqueda
        candidates.sort(key=lambda x: abs(len(x[2]) - len(name_clean)))
        return candidates[0]
        
    return None


def _execute_demo_toggle(instance_name: str, is_on: bool) -> str:
    resolved = _find_instance_dir(instance_name)
    if not resolved:
        return f"❌ No encontré ninguna instancia o agente que coincida con '{instance_name}'."
        
    kind, path, folder = resolved
    db_val = "true" if is_on else "false"
    action_word = "activado" if is_on else "desactivado"
    
    # Actualizar .env
    env_path = os.path.join(path, ".env")
    env_updated = False
    if os.path.exists(env_path):
        try:
            env_content = open(env_path, "r", encoding="utf-8").read()
            if "DEMO_MODE=" in env_content:
                new_content = re.sub(r"DEMO_MODE=(true|false|True|False)", f"DEMO_MODE={db_val}", env_content)
            else:
                new_content = env_content + f"\nDEMO_MODE={db_val}\n"
            open(env_path, "w", encoding="utf-8").write(new_content)
            env_updated = True
        except Exception as e:
            log.error(f"[Ovni] Error actualizando .env de {folder}: {e}")
            
    # Actualizar base de datos sqlite si existe firby.db
    db_path = os.path.join(path, "firby.db")
    db_updated = False
    if os.path.exists(db_path):
        try:
            import sqlite3
            conn = sqlite3.connect(db_path, timeout=10)
            c = conn.cursor()
            c.execute("CREATE TABLE IF NOT EXISTS system_config (key TEXT PRIMARY KEY, value TEXT, updated_at TEXT)")
            c.execute("INSERT OR REPLACE INTO system_config (key, value, updated_at) VALUES ('demo_mode', ?, datetime('now'))", (db_val,))
            conn.commit()
            conn.close()
            db_updated = True
        except Exception as e:
            log.error(f"[Ovni] Error actualizando DB de {folder}: {e}")
            
    # Reiniciar vía PM2
    pm2_name = f"firby-{folder}"
    if folder == "ovni":
        pm2_name = "firby-ovni"
    elif folder == "firby" or (kind == "agent" and folder == "default"):
        pm2_name = "firby"
        
    pm2_restarted = False
    try:
        res = subprocess.run(["pm2", "restart", pm2_name, "--update-env"], capture_output=True, text=True, timeout=10)
        if res.returncode == 0:
            pm2_restarted = True
        else:
            res_list = subprocess.run(["pm2", "jlist"], capture_output=True, text=True, timeout=5)
            if res_list.returncode == 0:
                import json
                pm2_jobs = json.loads(res_list.stdout)
                for job in pm2_jobs:
                    if folder in job.get("name", ""):
                        res_retry = subprocess.run(["pm2", "restart", job.get("name"), "--update-env"], capture_output=True, text=True, timeout=10)
                        if res_retry.returncode == 0:
                            pm2_name = job.get("name")
                            pm2_restarted = True
                            break
    except Exception as e:
        log.error(f"[Ovni] Error al reiniciar PM2 para {folder}: {e}")
        
    details = []
    if env_updated:
        details.append(".env actualizado")
    if db_updated:
        details.append("DB actualizada")
    if pm2_restarted:
        details.append(f"proceso PM2 `{pm2_name}` reiniciado")
    else:
        details.append(f"⚠️ no se pudo reiniciar PM2 `{pm2_name}` (hazlo manualmente con 'reinicia {pm2_name}')")
        
    return f"✅ Modo demo {action_word} para la instancia *{folder}*." + " ||| " + ", ".join(details)


def _execute_restart(instance_name: str) -> str:
    resolved = _find_instance_dir(instance_name)
    if not resolved:
        pm2_name = instance_name
    else:
        kind, path, folder = resolved
        pm2_name = f"firby-{folder}"
        if folder == "ovni":
            pm2_name = "firby-ovni"
        elif folder == "firby" or (kind == "agent" and folder == "default"):
            pm2_name = "firby"

    try:
        result = subprocess.run(
            ["pm2", "restart", pm2_name, "--update-env"],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            return f"✅ Instancia `{pm2_name}` reiniciada correctamente."
        else:
            return f"❌ Error al reiniciar `{pm2_name}`: {result.stderr[:200]}"
    except Exception as e:
        return f"❌ Error al reiniciar `{pm2_name}`: {e}"


def _queue_shell_task(command: str, chat_id: str, platform: str = "whatsapp") -> str:
    try:
        from src.firby.core.tasks import task_manager
        task_id = task_manager.schedule_task(
            task_type="shell_run",
            data={
                "command": command,
                "chat_id": chat_id,
                "platform": platform
            }
        )
        return f"🚀 *Tarea de consola encolada con éxito (ID: `{task_id}`)*.\nEjecutando: `{command}`\nTe avisaré en este chat tan pronto termine."
    except Exception as e:
        log.error(f"[Ovni] Error encolando tarea shell: {e}")
        return f"❌ Error al encolar tarea de consola: {e}"


def _queue_codex_task(prompt: str, chat_id: str, platform: str = "whatsapp") -> str:
    try:
        from src.firby.core.tasks import task_manager
        task_id = task_manager.schedule_task(
            task_type="codex_run",
            data={
                "prompt": prompt,
                "chat_id": chat_id,
                "platform": platform
            }
        )
        return f"🤖 *Tarea de desarrollo/Codex encolada con éxito (ID: `{task_id}`)*.\nInstrucción: *{prompt}*\nTe avisaré en este chat tan pronto termine."
    except Exception as e:
        log.error(f"[Ovni] Error encolando tarea Codex: {e}")
        return f"❌ Error al encolar tarea Codex: {e}"




def _execute_n8n(method: str, endpoint: str, body_str: str = "") -> str:
    """Ejecuta una llamada a la API de n8n."""
    import httpx
    n8n_url = os.environ.get("N8N_WEBHOOK_URL", "http://localhost:5678")
    api_key = os.environ.get("N8N_API_KEY", "")
    
    # Si el endpoint ya comienza con /, lo usamos directo
    # Si no, asumimos que es un path de API
    url = n8n_url.rstrip("/") + "/" + endpoint.lstrip("/")
    
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["X-N8N-API-KEY"] = api_key
    
    # Parsear body si viene como string JSON
    body = None
    if body_str and body_str.strip():
        try:
            body = json.loads(body_str.strip())
        except json.JSONDecodeError:
            return f"❌ Error: el body no es JSON válido: {body_str[:100]}"
    
    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.request(
                method.upper(),
                url,
                headers=headers,
                json=body,
            )
            # Intentar parsear como JSON
            try:
                result = response.json()
                # Formatear para mostrar bonito
                formatted = json.dumps(result, indent=2, ensure_ascii=False)
                return f"✅ N8N {method.upper()} {endpoint}\n\n```json\n{formatted[:1500]}\n```"
            except Exception:
                text = response.text[:1000]
                return f"✅ N8N {method.upper()} {endpoint}\n\n```\n{text}\n```"
    except Exception as e:
        return f"❌ Error llamando a n8n: {e}"



def _detect_quick_command(text: str, chat_id: str = "", platform: str = "whatsapp") -> Optional[List[str]]:
    """
    Intercepta comandos técnicos comunes antes de ir al LLM.
    Devuelve lista de bubbles o None si no hay comando.
    """
    from src.core.globals import db
    t = text.strip().lower()

    if t in ("/status", "status", "estado", "qué pasa", "que pasa"):
        state = _get_system_state()
        return [f"Estado del sistema:\n{state}"]

    if t in ("/help", "help", "ayuda", "qué puedes hacer", "que puedes hacer"):
        return [
            "Comandos disponibles:",
            "/status — estado de todos los procesos\n"
            "demo <instancia> on|off — activar/desactivar demo\n"
            "logs <instancia> — últimas 20 líneas de log\n"
            "reinicia <instancia> — reiniciar proceso PM2\n"
            "instancias — listar instancias registradas\n"
            "nueva instancia — iniciar flujo de creación\n"
            "/shell <comando> o run <comando> — ejecutar comando de consola en segundo plano\n"
            "/codex <tarea> o codex <tarea> — ejecutar tarea de desarrollo con Codex en segundo plano\n"
            "/tasks — ver últimas tareas registradas en segundo plano\n"
            "/task <id_parcial> [status|cancel] — ver detalles o cancelar una tarea"
        ]

    # Listar tareas en segundo plano
    if t in ("/tasks", "tasks", "tareas", "ver tareas"):
        if db:
            try:
                with db._conn() as c:
                    rows = c.execute("SELECT id, type, status, created_at FROM tasks ORDER BY created_at DESC LIMIT 5").fetchall()
                if not rows:
                    return ["No hay tareas registradas en el sistema."]
                reply = ["📋 *Últimas tareas en el sistema:*"]
                for r in rows:
                    reply.append(f"• ID: `{r['id'][:8]}...` | Tipo: *{r['type']}* | Estado: *{r['status']}* ({r['created_at']})")
                return ["\n".join(reply)]
            except Exception as e:
                return [f"Error leyendo tareas: {e}"]
        return ["Base de datos no disponible."]

    # Ver detalle de tarea o cancelarla
    task_details_match = re.match(r"^/task\s+([a-zA-Z0-9_-]+)(?:\s+(status|kill|cancel))?$", t)
    if task_details_match:
        task_id_partial = task_details_match.group(1).strip()
        action = task_details_match.group(2) or "status"
        action = "cancel" if action in ("kill", "cancel") else "status"
        
        if db:
            try:
                with db._conn() as c:
                    row = c.execute("SELECT * FROM tasks WHERE id LIKE ?", (f"{task_id_partial}%",)).fetchone()
                if not row:
                    return [f"❌ No encontré ninguna tarea que comience con `{task_id_partial}`."]
                
                full_id = row["id"]
                if action == "cancel":
                    from src.firby.core.tasks import task_manager
                    task_manager.cancel_task(full_id)
                    return [f"✅ Tarea `{full_id[:8]}...` cancelada con éxito."]
                
                info = [
                    f"📋 *Detalles de Tarea:* `{row['id']}`",
                    f"- *Tipo:* {row['type']}",
                    f"- *Estado:* {row['status']}",
                    f"- *Creada:* {row['created_at']}",
                    f"- *Iniciada:* {row['started_at'] or 'N/A'}",
                    f"- *Completada:* {row['completed_at'] or 'N/A'}"
                ]
                if row["error"]:
                    info.append(f"- ⚠️ *Error:* {row['error']}")
                if row["result"]:
                    try:
                        import json
                        res_val = json.loads(row["result"])
                        if isinstance(res_val, dict) and "error" in res_val:
                            info.append(f"- ⚠️ *Error de ejecución:* {res_val['error']}")
                    except Exception:
                        pass
                    info.append(f"- *Resultado:* `{str(row['result'])[:300]}...`")
                return ["\n".join(info)]
            except Exception as e:
                return [f"Error al procesar tarea: {e}"]

    # Comando shell / terminal rápido
    for prefix in ("/shell ", "run ", "exec ", "cmd "):
        if text.strip().lower().startswith(prefix):
            cmd = text.strip()[len(prefix):].strip()
            if cmd:
                res = _queue_shell_task(cmd, chat_id=chat_id, platform=platform)
                return [res]

    # Comando codex rápido
    for prefix in ("/codex ", "codex "):
        if text.strip().lower().startswith(prefix):
            prompt = text.strip()[len(prefix):].strip()
            if prompt:
                res = _queue_codex_task(prompt, chat_id=chat_id, platform=platform)
                return [res]

    # Comando demo <instancia> on|off estricto (CLI)
    demo_cli_match = re.match(r"^demo\s+([a-zA-Z0-9_-]+)\s+(on|off)$", t)
    if demo_cli_match:
        inst = demo_cli_match.group(1).strip()
        is_on = demo_cli_match.group(2) == "on"
        res = _execute_demo_toggle(inst, is_on)
        return [b.strip() for b in res.split("|||") if b.strip()]

    # Reinicio de instancia estricto (CLI)
    restart_match = re.match(r"^reinicia?\s+([a-zA-Z0-9_-]+)$", t)
    if restart_match:
        inst = restart_match.group(1).strip()
        res = _execute_restart(inst)
        return [res]

    # Logs de instancia estricto (CLI)
    logs_match = re.match(r"^logs?\s+([a-zA-Z0-9_-]+)$", t)
    if logs_match:
        inst = logs_match.group(1).strip()
        try:
            log_path = f"/home/ubuntu/firby/instances/{inst}/logs/firby.log"
            if not os.path.exists(log_path):
                log_path = f"/home/ubuntu/firby/agents/{inst}/logs/firby.log"
            if os.path.exists(log_path):
                result = subprocess.run(
                    ["tail", "-n", "20", log_path],
                    capture_output=True, text=True, timeout=5
                )
                return [f"Últimas líneas de {inst}:\n```\n{result.stdout[-800:]}\n```"]
            else:
                return [f"No encontré logs de '{inst}'"]
        except Exception as e:
            return [f"Error leyendo logs: {e}"]

    return None


# ─── Handler principal ───────────────────────────────────────────────────────

class OvniHandler:
    """
    Handler exclusivo para el agente Ovni.
    Solo acepta mensajes del admin registrado.
    Usa LLM con identidad técnica de Ovni.
    """

    def __init__(self, firby_instance):
        self.firby = firby_instance

    async def handle(
        self,
        chat_id: str,
        text: str,
        clinic: Dict,
        admin_ids: List[str],
        history: List[Dict],
        is_audio: bool = False,
        attachments: Optional[List] = None,
    ) -> List[str]:
        """
        Procesa un mensaje para OVNI.
        Solo el admin puede interactuar. Desconocidos → silencio.
        """
        from firby import llm_engine

        # ── Solo admin puede escribir a OVNI ──────────────────────────────
        # Normalizar comparación: chat_id puede venir como "6908159885" o 6908159885
        _chat_str = str(chat_id).strip()
        _admin_strs = {str(a).strip() for a in admin_ids}
        # Tambien consultar tabla local de admins
        try:
            import sqlite3 as _sqlite3
            _local_conn = _sqlite3.connect("/home/ubuntu/firby/agents/ovni/firby.db", timeout=3)
            _local_admins = {r[0] for r in _local_conn.execute("SELECT chat_id FROM admins").fetchall()}
            _local_conn.close()
            _admin_strs |= _local_admins
        except Exception:
            pass
        log.info(f"[Ovni] Mensaje de {_chat_str} | admins={_admin_strs}")
        if _chat_str not in _admin_strs:
            log.info(f"[Ovni] {_chat_str} no es admin — silencio")
            return []  # Silencio total

        # ── Primer turno ──────────────────────────────────────────────────
        is_first = not any(h.get("role") == "assistant" for h in history)
        if is_first and not text.strip():
            return [OVNI_FIRST_TURN]

        # ── Comandos rápidos (sin LLM) ────────────────────────────────────
        quick = _detect_quick_command(text, chat_id=chat_id)
        if quick:
            return quick

        # ── LLM con identidad de OVNI ─────────────────────────────────────
        if not llm_engine:
            return ["LLM no disponible — revisa los logs del sistema"]

        system_state = _get_system_state()
        history_txt = _build_history_txt(history)

        system_prompt = OVNI_SYSTEM_PROMPT.format(
            system_state=system_state,
            history_txt=history_txt,
        )

        messages = [
            {"role": "system", "content": system_prompt},
        ]

        # Si es primer turno, agregar instrucción de saludo técnico
        if is_first:
            messages.append({
                "role": "system",
                "content": (
                    f"El admin acaba de escribirte. "
                f"Responde natural, sin presentarte. "
                f"Máximo 10 palabras."
                )
            })

        # Historial de conversación
        for h in history[-8:]:
            messages.append({"role": h["role"], "content": h["content"][:400]})
        messages.append({"role": "user", "content": text})

        try:
            raw, _ = await llm_engine.complete(
                messages,
                model_tier="fast",
                temperature=0.7,
                max_tokens=500,
                use_cache=False,
            )
        except Exception as e:
            log.error(f"[Ovni] LLM error: {e}")
            return [f"Error LLM: {e}"]

        if not raw:
            return []  # LLM sin respuesta → silencio

        # ── Post-process: eliminar frases de recepcionista e identidad equivocada ────────────────
        raw = re.sub(r"(?i)\bfirby\b", "Dumi", raw)
        
        FORBIDDEN = (
            "recepcionista virtual", "recepcionista ejecutiva", "asesora de servicio",
            "servicio al cliente", "en qué puedo ayudar", "en qué te puedo ayudar",
            "con mucho gusto", "fue un placer", "soy tu asistente", "tu asistente virtual",
            "recepcionista de"
        )
        raw_lower = raw.lower()
        for f in FORBIDDEN:
            if f in raw_lower:
                log.warning(f"[Ovni] LLM generó frase prohibida: '{f}' — sanitizando respuesta")
                raw = "Ovni. Ejecución de comando técnica completada."
                break

        # Buscar comandos estructurados: [CMD:DEMO:instance:ON/OFF] o [CMD:RESTART:instance]
        cmd_matches = re.findall(r"\[CMD:(DEMO|RESTART):([^:\]]+)(?::(ON|OFF))?\]", raw)
        # Buscar comandos estructurados generales (SHELL, CODEX)
        gen_matches = re.findall(r"\[CMD:(SHELL|CODEX|N8N):([\s\S]+?)\]", raw)
        
        # Eliminar las etiquetas del texto de respuesta para no mostrarlas en bruto al usuario
        raw_clean = raw
        raw_clean = re.sub(r"\[CMD:(DEMO|RESTART):([^:\]]+)(?::(ON|OFF))?\]", "", raw_clean)
        raw_clean = re.sub(r"\[CMD:(SHELL|CODEX|N8N):([\s\S]+?)\]", "", raw_clean)
        raw_clean = raw_clean.strip()

        # Separar en burbujas por |||
        bubbles = [b.strip() for b in raw_clean.split("|||") if b.strip()]
        if not bubbles and raw_clean:
            bubbles = [raw_clean]

        # Ejecutar los comandos y añadir burbujas de estado
        for cmd_type, inst, option in cmd_matches:
            inst = inst.strip()
            if cmd_type == "DEMO":
                is_on = option == "ON"
                status_msg = _execute_demo_toggle(inst, is_on)
                # La respuesta de _execute_demo_toggle puede contener ||| para separar burbujas
                for sub_bubble in status_msg.split("|||"):
                    if sub_bubble.strip():
                        bubbles.append(sub_bubble.strip())
            elif cmd_type == "RESTART":
                status_msg = _execute_restart(inst)
                bubbles.append(status_msg)

        # Ejecutar comandos generales
        for cmd_type, payload in gen_matches:
            payload = payload.strip()
            if cmd_type == "SHELL":
                status_msg = _queue_shell_task(payload, chat_id=chat_id, platform="whatsapp")
                bubbles.append(status_msg)
            elif cmd_type == "CODEX":
                status_msg = _queue_codex_task(payload, chat_id=chat_id, platform="whatsapp")
                bubbles.append(status_msg)
            elif cmd_type == "N8N":
                # Parse method:endpoint:body from payload
                parts = payload.split(":", 2)
                method = parts[0].strip() if len(parts) > 0 else "GET"
                endpoint = parts[1].strip() if len(parts) > 1 else ""
                body_str = parts[2].strip() if len(parts) > 2 else ""
                status_msg = _execute_n8n(method, endpoint, body_str)
                bubbles.append(status_msg)

        return bubbles if bubbles else [raw.strip()]
