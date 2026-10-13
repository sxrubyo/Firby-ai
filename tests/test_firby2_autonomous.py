# -*- coding: utf-8 -*-
"""
Firby 2.0 Autonomous Multi-Agent Comprehensive Test Suite.
Verifies Sandbox isolation, CodeTools, ReachTools, BrowserEngine,
TaskGraph DAG, Governance limits, and SWE-agent autonomous self-repair.
"""
import os
import pytest
from pathlib import Path

from src.core.sandbox import SandboxRunner, SandboxWorkspace, PathTraversalError
from src.core.tools.code_tools import CodeTools
from src.core.tools.reach_tools import ReachTools
from src.core.browser import BrowserEngine
from src.core.planner import TaskGraph, TaskStatus
from src.core.governance import BudgetTracker, BudgetLimits, BudgetExceededError, ApprovalGate
from src.core.agent import AutonomousAgent
from fastapi.testclient import TestClient
from src.interfaces.web.app import app


class TestFirby2AutonomousPlatform:
    """Master test suite for Firby 2.0 Autonomous Architecture."""

    def test_sandbox_isolation_and_secret_scrubbing(self):
        """Ensures secrets on the host machine are scrubbed from the sandbox environment."""
        workspace = SandboxWorkspace()
        runner = SandboxRunner(workspace=workspace)

        os.environ["OPENAI_API_KEY"] = "sk-fake-secret-key-that-must-be-scrubbed"
        os.environ["DATABASE_URL"] = "postgresql://user:pass@host/db"

        result = runner.run_python_code("""
import os
print("KEY:", os.environ.get("OPENAI_API_KEY", "CLEAN"))
print("DB:", os.environ.get("DATABASE_URL", "CLEAN"))
""")
        assert result.is_success, f"Execution failed: {result.stderr}"
        assert "KEY: CLEAN" in result.stdout
        assert "DB: CLEAN" in result.stdout
        workspace.cleanup()

    def test_sandbox_traceback_diagnostics(self):
        """Ensures runtime exceptions are parsed into structured ExecutionError objects."""
        workspace = SandboxWorkspace()
        runner = SandboxRunner(workspace=workspace)

        result = runner.run_python_code("""
def divide(a, b):
    return a / b
divide(10, 0)
""")
        assert not result.is_success
        assert result.error is not None
        assert result.error.name == "ZeroDivisionError"
        assert "division by zero" in result.error.value
        assert "Traceback" in result.error.traceback
        workspace.cleanup()

    def test_sandbox_path_traversal_protection(self):
        """Ensures scripts and operations cannot escape the sandbox boundary."""
        workspace = SandboxWorkspace()
        with pytest.raises(PathTraversalError):
            workspace.resolve_safe_path("../../../etc/passwd")
        with pytest.raises(PathTraversalError):
            workspace.resolve_safe_path("/etc/passwd")
        workspace.cleanup()

    def test_code_tools_read_write_patch(self):
        """Verifies file creation, line-slice reading, and surgical patching."""
        tools = CodeTools()
        w = tools.write_file("module.py", "def greet():\n    return 'hello world'\n")
        assert w["success"] is True

        r = tools.read_file("module.py", start_line=1, end_line=1)
        assert "def greet():" in r["content"]

        p = tools.patch_file("module.py", "hello world", "firby 2.0")
        assert p["success"] is True

        updated = tools.read_file("module.py")
        assert "firby 2.0" in updated["content"]
        tools.workspace.cleanup()

    def test_reach_tools_search_and_fetch(self):
        """Verifies internet search and web page extraction with fallbacks."""
        reach = ReachTools()
        search_res = reach.web_search("Python pytest testing framework", num_results=2)
        assert search_res.get("success") is True
        assert len(search_res.get("content", "")) > 10

        fetch_res = reach.fetch_web_page("https://example.com")
        assert fetch_res.get("success") is True
        assert "Example Domain" in fetch_res.get("content", "")

    def test_browser_engine_dom_indexing_and_text(self):
        """Verifies Playwright headless browser navigation and element indexing [1], [2]."""
        with BrowserEngine(headless=True) as engine:
            nav = engine.navigate("https://example.com")
            assert nav["success"] is True

            elems = engine.get_interactive_elements()
            assert elems["success"] is True
            assert elems["count"] >= 1
            assert "[1]" in elems["interactive_tree"]

            txt = engine.extract_text()
            assert txt["success"] is True
            assert "Example Domain" in txt["content"]

    def test_task_graph_dag_lifecycle(self):
        """Verifies DAG dependencies, cycle prevention, and atomic checkout."""
        dag = TaskGraph("Build and test feature")
        t1 = dag.add_task("Step 1", "Initial setup")
        t2 = dag.add_task("Step 2", "Implementation", dependencies=[t1.id])

        # Step 2 cannot be checked out before Step 1
        ready = dag.get_ready_tasks()
        assert len(ready) == 1
        assert ready[0].id == t1.id

        # Checkout Step 1
        co = dag.checkout_task()
        assert co.id == t1.id
        assert co.status == TaskStatus.IN_PROGRESS

        # Complete Step 1
        dag.mark_completed(t1.id, result="Setup done")

        # Now Step 2 must be ready
        ready2 = dag.get_ready_tasks()
        assert len(ready2) == 1
        assert ready2[0].id == t2.id

        # Complete Step 2
        dag.mark_completed(t2.id, result="Implemented")
        assert dag.is_complete() is True

    def test_governance_limits_and_risk_gating(self):
        """Verifies step budget guard and dangerous action approval gates."""
        tracker = BudgetTracker(limits=BudgetLimits(max_steps=2))
        tracker.record_step("step 1")
        tracker.record_step("step 2")
        with pytest.raises(BudgetExceededError):
            tracker.record_step("step 3")

        gate = ApprovalGate()
        assert gate.requires_approval("command", "rm -rf /") is True
        assert gate.requires_approval("command", "git push origin main --force") is True
        assert gate.requires_approval("command", "curl http://localhost:8003") is True
        assert gate.requires_approval("command", "echo hello") is False

    def test_autonomous_swe_self_repair_loop(self):
        """
        Full SWE-agent feedback loop test:
        Injects a failing calculation into main.py, executes pytest,
        diagnoses the AssertionError, applies the repair patch,
        and verifies that tests pass autonomously.
        """
        agent = AutonomousAgent()
        graph = agent.plan_goal("Generar script y verificar tests con self-repair")

        # Injected bug in task_code
        task_code = graph.tasks["task_code"]
        task_code.context = {
            "code": """# -*- coding: utf-8 -*-
def multiply(a, b):
    return a + b  # Bug: adding instead of multiplying
""",
            "tests": """# -*- coding: utf-8 -*-
from main import multiply

def test_multiply():
    assert multiply(3, 4) == 12
"""
        }

        # Custom repair patch for multiplication
        def custom_repair(failed_res, attempt):
            content = agent.workspace.read_file("main.py")
            if "return a + b" in content:
                agent.code_tools.patch_file("main.py", "return a + b", "return a * b")
                return True
            return False

        agent._attempt_self_repair = custom_repair

        exec_res = agent.run_until_complete("Generar script y verificar tests con self-repair", graph=graph)
        assert exec_res["status"] == "COMPLETED", f"Autonomous run failed: {exec_res}"
        
        # Verify patched code in workspace
        final_code = agent.workspace.read_file("main.py")
        assert "return a * b" in final_code
        agent.workspace.cleanup()

    def test_autonomous_api_endpoints(self):
        """Verifies FastAPI REST endpoints for the autonomous agent."""
        client = TestClient(app)

        # 1. Capabilities
        cap_res = client.get("/api/v2/agent/capabilities")
        assert cap_res.status_code == 200
        cap_data = cap_res.json()
        assert cap_data["status"] == "online"
        assert "sandbox_execution" in cap_data["capabilities"]
        assert "browser_automation" in cap_data["capabilities"]

        # 2. Submit Goal
        goal_payload = {"goal": "Investigar y escribir script de procesamiento de texto"}
        goal_res = client.post("/api/v2/agent/goal", json=goal_payload)
        assert goal_res.status_code == 200
        goal_data = goal_res.json()
        assert goal_data["ok"] is True
        session_id = goal_data["session_id"]
        assert goal_data["tasks_planned"] >= 2

        # 3. Status
        status_res = client.get(f"/api/v2/agent/status/{session_id}")
        assert status_res.status_code == 200
        status_data = status_res.json()
        assert status_data["ok"] is True
        assert status_data["goal"] == goal_payload["goal"]

    def test_langfuse_style_tracing_and_spans(self):
        """Verifies hierarchical tracing, duration measurement, and SQLite persistence."""
        from src.core.telemetry import global_tracer, SpanType
        trace = global_tracer.start_trace("eval_run", session_id="sess_eval_10")
        with global_tracer.span(trace, "step_parent", span_type=SpanType.AGENT_STEP) as sp_parent:
            sp_parent.usage.total_tokens = 250
            with global_tracer.span(trace, "child_tool", span_type=SpanType.TOOL, parent_span_id=sp_parent.id) as sp_child:
                sp_child.finish(output_data={"status": "ok"})
        global_tracer.finish_trace(trace)

        retrieved = global_tracer.get_trace(trace.id)
        assert retrieved is not None
        assert retrieved["span_count"] == 2
        assert retrieved["total_tokens"] == 250
        assert retrieved["status"] == "ok"

    def test_deerflow_task_notebook_and_checkpoints(self):
        """Verifies bounded task notes and SQLite workflow checkpoint save/restore."""
        from src.core.planner import TaskGraph, TaskNotebook, WorkflowCheckpointManager
        nb = TaskNotebook(max_notes=4)
        nb.set_note("lead_info", "Extracted 3 prospective clients", category="finding")
        nb.set_note("script_path", "main.py", category="file")

        mgr = WorkflowCheckpointManager()
        graph = TaskGraph("Research and outreach")
        t1 = graph.add_task("Collect", "Find prospects")
        graph.mark_completed(t1.id, result="Found 3")

        cid = mgr.save_checkpoint("sess_df_1", graph, notebook=nb, artifacts=["main.py"])
        assert cid.startswith("chk_")

        restored = mgr.restore_checkpoint(cid)
        assert restored is not None
        assert restored["goal"] == "Research and outreach"
        assert restored["notebook"].get_note("lead_info") == "Extracted 3 prospective clients"

    def test_openai_agents_tool_guardrails_and_handoffs(self):
        """Verifies pre-flight tool input validation and typed agent handoffs."""
        from src.core.agent import AgentGuardrails, HandoffRouter
        # Guardrail check
        ok, err = AgentGuardrails.validate_tool_input("run_command", {"command": "rm -rf /var"})
        assert ok is False
        assert "destruction" in err

        ok2, _ = AgentGuardrails.validate_tool_input("run_command", {"command": "python -m pytest"})
        assert ok2 is True

        # Handoff check
        router = HandoffRouter()
        h = router.execute_handoff("landing.concierge", "booking.coordinator", "User wants an appointment")
        assert h.from_agent == "landing.concierge"
        assert h.to_agent == "booking.coordinator"

    def test_playwright_aria_semantic_snapshots(self):
        """Verifies Playwright ARIA accessibility tree extraction for token reduction."""
        with BrowserEngine(headless=True) as engine:
            engine.navigate("https://example.com")
            res = engine.get_aria_snapshot()
            assert res["success"] is True
            assert "Example Domain" in res["aria_snapshot"]
            assert "link" in res["aria_snapshot"]
            # ARIA tree is concise (less than 600 chars) vs. raw HTML (thousands of chars)
            assert res["length"] < 600

    def test_hermes_verification_evidence_collector(self):
        """Verifies that tasks enforce concrete proof before completion."""
        from src.core.agent import VerificationEvidenceCollector, InsufficientEvidenceError
        from src.core.sandbox import SandboxWorkspace

        ws = SandboxWorkspace()
        collector = VerificationEvidenceCollector(workspace=ws)

        # File creation proof
        ws.write_file("output.json", '{"status": "ok"}')
        ev_file = collector.verify_file_created("task_1", "output.json")
        assert ev_file.proof.startswith("File output.json verified")

        # Test output proof
        ev_test = collector.verify_test_output("task_2", "=== 5 passed in 0.2s ===", exit_code=0)
        assert "5 passed" in ev_test.proof

        # Negative test: failed test must raise InsufficientEvidenceError
        with pytest.raises(InsufficientEvidenceError):
            collector.verify_test_output("task_3", "=== 1 failed in 0.1s ===", exit_code=1)

        ws.cleanup()

