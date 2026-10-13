# -*- coding: utf-8 -*-
import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from src.firby.admin.dashboard import AdminCommandsMixin
from src.core.ovni_handler import _detect_quick_command
from src.firby.core.tasks import task_manager

class DummyRuntime(AdminCommandsMixin):
    def __init__(self):
        self._admin_pending = {}
        self.admin_learning = MagicMock()
        self.simulator = MagicMock()

@pytest.mark.anyio
async def test_admin_shell_exec_action():
    runtime = DummyRuntime()
    clinic = {"name": "Mi Negocio", "setup_buffer": "{}"}
    result_dict = {"reply": ""}

    mock_db = MagicMock()
    mock_task_id = "test-task-123"
    
    with patch("src.firby.admin.dashboard.db", mock_db), \
         patch("src.firby.core.tasks.task_manager.schedule_task", return_value=mock_task_id) as mock_schedule:
         
        ok = await runtime._admin_apply_action(
            action="shell_exec",
            data={"command": "echo 'Antigravity Shell Test'"},
            clinic=clinic,
            chat_id="admin_1",
            result_dict=result_dict
        )
        assert ok is True
        assert mock_task_id in result_dict["reply"]
        assert "echo 'Antigravity Shell Test'" in result_dict["reply"]
        mock_schedule.assert_called_once_with(
            task_type="shell_run",
            data={
                "command": "echo 'Antigravity Shell Test'",
                "chat_id": "admin_1",
                "platform": "whatsapp"
            }
        )

@pytest.mark.anyio
async def test_ovni_quick_commands_enqueue():
    mock_task_id = "test-ovni-task-999"
    
    with patch("src.firby.core.tasks.task_manager.schedule_task", return_value=mock_task_id) as mock_schedule:
        quick_res = _detect_quick_command("run echo 'Quick Run Test'", chat_id="admin_2")
        assert quick_res is not None
        assert len(quick_res) == 1
        assert mock_task_id in quick_res[0]
        assert "echo 'Quick Run Test'" in quick_res[0]
        mock_schedule.assert_called_once_with(
            task_type="shell_run",
            data={
                "command": "echo 'Quick Run Test'",
                "chat_id": "admin_2",
                "platform": "whatsapp"
            }
        )

@pytest.mark.anyio
async def test_task_manager_shell_run_handler():
    from src.firby.core.models import Task
    from datetime import datetime
    
    task = Task(
        id="task-xxx",
        type="shell_run",
        priority=5,
        status="pending",
        data={"command": "echo 'Handler execution'", "chat_id": "admin_3", "platform": "whatsapp"},
        created_at=datetime.now(),
        scheduled_for=None,
        completed_at=None,
        result=None,
        retries=0
    )
    
    # Mock subprocess communication
    mock_process = AsyncMock()
    mock_process.communicate.return_value = (b"Handler execution\n", b"")
    mock_process.returncode = 0
    
    with patch("asyncio.create_subprocess_shell", return_value=mock_process) as mock_create_sub, \
         patch.object(task_manager, "_send_notification_to_chat", new_callable=AsyncMock) as mock_notify:
         
        res = await task_manager._handle_shell_run(task)
        assert res["status"] == "ok"
        assert res["code"] == 0
        
        mock_create_sub.assert_called_once()
        mock_notify.assert_called_once()
        assert "Handler execution" in mock_notify.call_args[0][1]
