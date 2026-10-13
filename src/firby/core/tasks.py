# -*- coding: utf-8 -*-
"""TaskManager for executing autonomous background tasks."""
from __future__ import annotations

import asyncio
import logging
import uuid
from datetime import datetime
from typing import Dict, Any, Callable

from src.firby.core.proxy import GlobalProxy
from src.firby.core.models import Task

log = logging.getLogger("firby.tasks")

db = GlobalProxy("db")
mcp_manager = GlobalProxy("mcp_manager")
_parse_admin_ids = GlobalProxy("_parse_admin_ids")


class TaskManager:
    """Gestor de tareas autónomas."""

    def __init__(self):
        self._running = False
        self._task_handlers: Dict[str, Callable] = {}
        self._register_default_handlers()

    def _register_default_handlers(self):
        self._task_handlers["reminder"] = self._handle_reminder
        self._task_handlers["self_improve"] = self._handle_self_improve
        self._task_handlers["daily_report"] = self._handle_daily_report
        self._task_handlers["shell_run"] = self._handle_shell_run
        self._task_handlers["codex_run"] = self._handle_codex_run

    async def start(self):
        self._running = True
        # Reset stuck running tasks to pending on startup
        try:
            if db:
                with db._conn() as c:
                    c.execute("UPDATE tasks SET status='pending' WHERE status='running'")
                    # Prevent self_improve flood: keep only 1 pending, delete the rest
                    c.execute("""
                        DELETE FROM tasks WHERE type='self_improve' AND status='pending'
                        AND id NOT IN (
                            SELECT id FROM tasks WHERE type='self_improve' AND status='pending'
                            ORDER BY created_at DESC LIMIT 1
                        )
                    """)
                    # Also purge old completed self_improve tasks (keep last 10)
                    c.execute("""
                        DELETE FROM tasks WHERE type='self_improve' AND status='completed'
                        AND id NOT IN (
                            SELECT id FROM tasks WHERE type='self_improve' AND status='completed'
                            ORDER BY created_at DESC LIMIT 10
                        )
                    """)
        except Exception as e:
            log.warning(f"[task] Failed to reset stuck tasks: {e}")
            
        asyncio.create_task(self._run_loop())

    async def _run_loop(self):
        while self._running:
            try:
                if db:
                    pending = db.get_pending_tasks(limit=5)
                    for task in pending:
                        if task.status == "pending":
                            asyncio.create_task(self.execute_task_by_id(task.id))
            except Exception as e:
                log.error(f"[task] Error in run loop: {e}")
            await asyncio.sleep(15)

    def _get_task_by_id(self, task_id: str) -> Optional[Task]:
        if not db:
            return None
        import json
        with db._conn() as c:
            row = c.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
        if not row:
            return None
        return Task(
            id=row["id"],
            type=row["type"],
            priority=row["priority"],
            status=row["status"],
            data=json.loads(row["data"] or "{}"),
            created_at=datetime.fromisoformat(row["created_at"]),
            scheduled_for=datetime.fromisoformat(row["scheduled_for"]) if row["scheduled_for"] else None,
            completed_at=datetime.fromisoformat(row["completed_at"]) if row["completed_at"] else None,
            result=json.loads(row["result"]) if row["result"] else None,
            retries=row["retries"]
        )

    async def execute_task_by_id(self, task_id: str):
        task = self._get_task_by_id(task_id)
        if not task or task.status not in ("pending", "running"):
            return
        
        if db:
            db.update_task(task_id, status="running", started_at=datetime.now())
            
        task.status = "running"
        handler = self._task_handlers.get(task.type)
        if handler:
            try:
                log.info(f"[task] Starting background execution for task {task_id} (type: {task.type})")
                result = await handler(task)
                if db:
                    db.update_task(task_id, status="completed", result=result, completed_at=datetime.now())
            except Exception as e:
                log.error(f"[task] Task {task_id} execution failed: {e}", exc_info=True)
                if db:
                    db.update_task(task_id, status="failed", error=str(e), completed_at=datetime.now())
        else:
            log.warning(f"[task] No handler found for task type: {task.type}")
            if db:
                db.update_task(task_id, status="failed", error=f"No handler for type: {task.type}", completed_at=datetime.now())

    async def _send_notification_to_chat(self, chat_id: str, message: str, platform: str = "whatsapp"):
        try:
            import httpx
            from src.firby.core.proxy import GlobalProxy
            Config = GlobalProxy("Config")
            
            resolved_platform = platform
            if "telegram:" in chat_id or (chat_id.isdigit() and len(chat_id) < 15):
                resolved_platform = "telegram"
                
            clean_chat_id = chat_id.replace("telegram:", "")
            
            if resolved_platform == "telegram":
                if Config.TELEGRAM_TOKEN:
                    async with httpx.AsyncClient(timeout=15.0) as client:
                        await client.post(
                            f"https://api.telegram.org/bot{Config.TELEGRAM_TOKEN}/sendMessage",
                            json={"chat_id": clean_chat_id, "text": message, "parse_mode": "Markdown"}
                        )
                else:
                    log.warning("[task] Telegram token not configured, cannot send notification")
            else:
                if Config.WHATSAPP_BRIDGE_URL:
                    target_id = clean_chat_id
                    if "@lid" in target_id:
                        target_id = target_id.replace("@lid", "@s.whatsapp.net")
                    elif "@s.whatsapp.net" not in target_id and "@g.us" not in target_id:
                        target_id = f"{target_id}@s.whatsapp.net"
                        
                    async with httpx.AsyncClient(timeout=15.0) as client:
                        r = await client.post(
                            f"{Config.WHATSAPP_BRIDGE_URL}/send",
                            json={"to": target_id, "message": message}
                        )
                        if r.status_code >= 400:
                            log.error(f"[task] WhatsApp send failed ({r.status_code}): {r.text[:200]}")
                else:
                    log.warning("[task] WHATSAPP_BRIDGE_URL not configured, cannot send notification")
        except Exception as e:
            log.error(f"[task] _send_notification_to_chat error: {e}")

    async def _handle_reminder(self, task: "Task") -> Dict[str, Any]:
        try:
            chat_id = task.data.get("chat_id", "")
            message = task.data.get("message", "")
            if chat_id and message:
                await mcp_manager.execute(
                    "notifications_v1", "send_notification",
                    {"chat_id": chat_id, "message": message}
                )
            return {"status": "sent", "chat_id": chat_id}
        except Exception as e:
            log.warning(f"[task] reminder failed: {e}")
            return {"status": "failed", "error": str(e)}

    async def _handle_self_improve(self, task: "Task") -> Dict[str, Any]:
        try:
            from pathlib import Path
            try:
                from src.firby.brain.firby_skill_engine import FirbySkillEngine
            except ImportError:
                from firby_skill_engine import FirbySkillEngine

            skills_dir = Path("/home/ubuntu/firby/skills")
            engine = FirbySkillEngine(skills_dir)
            skills = engine.list_skills()
            log.info(f"[task] self_improve executed cleanly. Total skills in system: {len(skills)}")
            return {"status": "ok", "total_skills": len(skills)}
        except Exception as e:
            log.warning(f"[task] self_improve failed: {e}")
            return {"status": "failed", "error": str(e)}

    async def _handle_daily_report(self, task: "Task") -> Dict[str, Any]:
        try:
            await self._send_daily_report()
            return {"status": "ok"}
        except Exception as e:
            log.warning(f"[task] daily_report failed: {e}")
            return {"status": "failed"}

    async def _handle_shell_run(self, task: "Task") -> Dict[str, Any]:
        command = task.data.get("command", "")
        chat_id = task.data.get("chat_id", "")
        platform = task.data.get("platform", "whatsapp")
        
        if not command:
            return {"status": "error", "error": "No command provided"}
            
        import os
        cwd = "/home/ubuntu/firby"
        if not os.path.exists(cwd):
            cwd = os.getcwd()
            
        try:
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=cwd
            )
            stdout_bytes, stderr_bytes = await process.communicate()
            
            out = stdout_bytes.decode("utf-8", errors="replace").strip()
            err = stderr_bytes.decode("utf-8", errors="replace").strip()
            code = process.returncode
            
            reply = []
            reply.append(f"📋 *Resultado de Tarea (ID: `{task.id}`)*")
            reply.append(f"Comando: `{command}`")
            if out:
                reply.append(f"💻 *Console Output (code={code}):*\n```\n{out[-1500:]}\n```")
            if err:
                reply.append(f"⚠️ *Error Output:*\n```\n{err[-1000:]}\n```")
            if not out and not err:
                reply.append(f"✅ Comando ejecutado con código {code} (sin salida).")
                
            full_msg = "\n".join(reply)
            
            if chat_id:
                await self._send_notification_to_chat(chat_id, full_msg, platform)
                
            return {"status": "ok", "code": code, "stdout_len": len(out), "stderr_len": len(err)}
        except Exception as e:
            log.error(f"[task] shell_run exception: {e}")
            error_msg = f"❌ *Error en Tarea (ID: `{task.id}`)*\nFalló al ejecutar `{command}`: {e}"
            if chat_id:
                await self._send_notification_to_chat(chat_id, error_msg, platform)
            raise e

    async def _handle_codex_run(self, task: "Task") -> Dict[str, Any]:
        prompt = task.data.get("prompt", "")
        chat_id = task.data.get("chat_id", "")
        platform = task.data.get("platform", "whatsapp")
        
        if not prompt:
            return {"status": "error", "error": "No prompt provided"}
            
        import os
        import tempfile
        cwd = "/home/ubuntu/firby"
        if not os.path.exists(cwd):
            cwd = os.getcwd()
            
        with tempfile.NamedTemporaryFile("r+", encoding="utf-8", delete=False) as handle:
            output_path = handle.name
            
        try:
            command_list = [
                "/home/ubuntu/.nvm/versions/node/v24.15.0/bin/codex",
                "exec",
                "--skip-git-repo-check",
                "--full-auto",
                "--sandbox", "danger-full-access",
                "--color", "never",
                "-C", cwd,
                "-o", output_path,
                prompt
            ]
            
            process = await asyncio.create_subprocess_exec(
                *command_list,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout_bytes, stderr_bytes = await process.communicate()
            
            out = stdout_bytes.decode("utf-8", errors="replace").strip()
            err = stderr_bytes.decode("utf-8", errors="replace").strip()
            code = process.returncode
            
            content = ""
            if os.path.exists(output_path):
                content = open(output_path, encoding="utf-8").read().strip()
                os.unlink(output_path)
                
            reply = []
            reply.append(f"🤖 *Resultado de Codex (Tarea ID: `{task.id}`)*")
            reply.append(f"Instrucción: *{prompt}*")
            if content:
                reply.append(f"\n{content}")
            else:
                if out:
                    reply.append(f"Output de Codex:\n```\n{out[-1500:]}\n```")
                if err:
                    reply.append(f"Error de Codex:\n```\n{err[-1000:]}\n```")
                if not out and not err:
                    reply.append("✅ Codex ejecutó la tarea con éxito (sin salida).")
                    
            full_msg = "\n".join(reply)
            
            if chat_id:
                await self._send_notification_to_chat(chat_id, full_msg, platform)
                
            return {"status": "ok", "code": code, "output_len": len(content)}
        except Exception as e:
            log.error(f"[task] codex_run exception: {e}")
            error_msg = f"❌ *Error en Codex (ID: `{task.id}`)*\nFalló al ejecutar: {e}"
            if chat_id:
                await self._send_notification_to_chat(chat_id, error_msg, platform)
            raise e

    async def _send_daily_report(self):
        try:
            if db:
                admin_ids = _parse_admin_ids(db.get_clinic().get("admin_chat_ids", []))
                today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
                stats = db.get_conversation_stats(since=today_start)
                msg = f"*Reporte diario Firby*\n\nConversaciones: {stats.get('conversations', 0)}\nMensajes: {stats.get('messages', 0)}"
                for aid in admin_ids:
                    await mcp_manager.execute("notifications_v1", "send_notification", {"chat_id": aid, "message": msg})
        except Exception:
            pass

    def schedule_task(self, task_type: str, data: Dict[str, Any],
                      scheduled_for: datetime = None, priority: int = 5) -> str:
        task_obj = Task(
            id=str(uuid.uuid4()),
            type=task_type,
            priority=priority,
            status="pending",
            data=data,
            created_at=datetime.now(),
            scheduled_for=scheduled_for,
            completed_at=None,
            result=None,
            retries=0
        )
        if db:
            db.create_task(task_obj)
        
        # Immediate background execution trigger
        if self._running and (not scheduled_for or scheduled_for <= datetime.now()):
            asyncio.create_task(self.execute_task_by_id(task_obj.id))
            
        return task_obj.id

    def cancel_task(self, task_id: str):
        if db:
            db.update_task(task_id, status="cancelled", completed_at=datetime.now())

task_manager = TaskManager()

async def init_task_manager():
    await task_manager.start()
