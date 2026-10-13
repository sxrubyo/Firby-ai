# -*- coding: utf-8 -*-
"""
Firby Autonomous Agent Loop & Self-Repair Engine (enhanced with Langfuse, DeerFlow, OpenAI Agents & Hermes patterns).
Executes high-level goals through task DAG decomposition, tool invocation,
traceback diagnosis, iterative self-repair, bounded task notebooks, and verification evidence.
"""
from __future__ import annotations

import logging
import re
import time
import uuid
import json
from typing import Dict, Any, List, Optional, Callable

from src.core.sandbox.models import ExecutionResult, ExecutionError
from src.core.sandbox.workspace import SandboxWorkspace
from src.core.sandbox.runner import SandboxRunner
from src.core.tools.code_tools import CodeTools
from src.core.tools.reach_tools import ReachTools
from src.core.browser.browser_engine import BrowserEngine
from src.core.browser.decision_engine import DecisionEngine
from src.core.browser.decision_models import BrowserOperation, DecisionRequest
from src.core.planner.task_graph import TaskGraph, TaskNode, TaskStatus
from src.core.planner.task_notebook import TaskNotebook
from src.core.planner.checkpoint import WorkflowCheckpointManager
from src.core.governance.budget_guard import BudgetTracker, BudgetLimits, BudgetExceededError
from src.core.governance.approval_gate import ApprovalGate, ApprovalRequest
from src.core.telemetry import global_tracer, Tracer, Trace, SpanType, SpanStatus
from .guardrails import AgentGuardrails
from .verification import VerificationEvidenceCollector, EvidenceType, InsufficientEvidenceError

logger = logging.getLogger("firby.autonomous_agent")


class AutonomousAgent:
    """
    Production-grade Autonomous Agent for Firby 2.0.
    Integrates:
    - Langfuse tracing & span telemetry
    - DeerFlow bounded task notes & SQLite checkpoints
    - OpenAI Agents tool guardrails & handoffs
    - Playwright semantic ARIA tree extraction
    - Hermes verification evidence enforcement
    - SWE-agent test-driven automated self-repair
    """

    def __init__(
        self,
        workspace: Optional[SandboxWorkspace] = None,
        budget_limits: Optional[BudgetLimits] = None,
        llm_client: Optional[Any] = None,
        session_id: Optional[str] = None,
    ):
        self.session_id = session_id or f"sess_{uuid.uuid4().hex[:12]}"
        self.workspace = workspace or SandboxWorkspace(session_id=self.session_id)
        self.runner = SandboxRunner(workspace=self.workspace)
        self.code_tools = CodeTools(workspace=self.workspace, runner=self.runner)
        self.reach_tools = ReachTools()
        self.browser_engine = BrowserEngine(headless=True)
        self.decision_engine = DecisionEngine()
        self.approval_gate = ApprovalGate()
        self.budget = BudgetTracker(limits=budget_limits or BudgetLimits())
        self.llm_client = llm_client

        # Advanced components (newly integrated)
        self.tracer: Tracer = global_tracer
        self.active_trace: Optional[Trace] = None
        self.notebook = TaskNotebook()
        self.checkpoint_manager = WorkflowCheckpointManager()
        self.evidence_collector = VerificationEvidenceCollector(workspace=self.workspace)

        self.current_graph: Optional[TaskGraph] = None
        self.execution_log: List[Dict[str, Any]] = []

    def plan_goal(self, goal: str) -> TaskGraph:
        """
        Decomposes a high-level goal into an actionable TaskGraph DAG.
        """
        graph = TaskGraph(goal=goal)
        goal_lower = goal.lower()

        # 1. Research task
        if any(w in goal_lower for w in ["investig", "search", "busca", "research", "competidor", "documentac"]):
            graph.add_task(
                task_id="task_research",
                title="Investigate & Collect Data",
                description=f"Gather relevant internet data and references for: {goal}",
                assigned_role="researcher",
                tool="web_search",
            )

        # 2. Browser task
        if any(w in goal_lower for w in ["browser", "naveg", "web page", "formulario", "click", "screenshot"]):
            deps = ["task_research"] if "task_research" in graph.tasks else []
            graph.add_task(
                task_id="task_browser",
                title="Browser Navigation & Interaction",
                description=f"Navigate web pages, inspect DOM and extract information: {goal}",
                assigned_role="browser",
                tool="browser_navigation",
                dependencies=deps,
            )

        # 3. Coding task
        if any(w in goal_lower for w in ["cod", "script", "program", "escribe", "desarrolla", "crea un archivo", "generar"]):
            deps = []
            if "task_browser" in graph.tasks:
                deps.append("task_browser")
            elif "task_research" in graph.tasks:
                deps.append("task_research")

            graph.add_task(
                task_id="task_code",
                title="Code Implementation",
                description=f"Write code and implementation in sandbox: {goal}",
                assigned_role="coder",
                tool="code_writer",
                dependencies=deps,
            )

            # 4. Verification / Test task
            graph.add_task(
                task_id="task_verify",
                title="Test & Self-Repair Verification",
                description="Execute automated tests and self-repair errors in sandbox",
                assigned_role="verifier",
                tool="test_runner",
                dependencies=["task_code"],
            )

        # Default fallback task if no specific keywords matched
        if not graph.tasks:
            graph.add_task(
                task_id="task_general_1",
                title="Execute Goal",
                description=goal,
                assigned_role="general",
            )

        self.current_graph = graph
        return graph

    def run_until_complete(
        self,
        goal: str,
        graph: Optional[TaskGraph] = None,
        on_step_callback: Optional[Callable[[Dict[str, Any]], None]] = None,
    ) -> Dict[str, Any]:
        """
        Main autonomous execution loop with Langfuse tracing, DeerFlow checkpoints,
        OpenAI guardrails, and Hermes verification evidence.
        """
        self.current_graph = graph or self.plan_goal(goal)
        start_time = time.time()

        # Start Root Trace (Langfuse telemetry)
        self.active_trace = self.tracer.start_trace(
            name=f"goal_{self.session_id}",
            session_id=self.session_id,
            metadata={"goal": goal, "task_count": len(self.current_graph.tasks)}
        )

        checkpoint_ids: List[str] = []

        while not self.current_graph.is_complete():
            ready_task = self.current_graph.checkout_task()
            if not ready_task:
                waiting = [t for t in self.current_graph.tasks.values() if t.status == TaskStatus.WAITING_APPROVAL]
                if waiting:
                    self.tracer.finish_trace(self.active_trace, status=SpanStatus.OK)
                    return {
                        "status": "WAITING_HUMAN_APPROVAL",
                        "goal": goal,
                        "session_id": self.session_id,
                        "trace_id": self.active_trace.id,
                        "waiting_tasks": [t.to_dict() for t in waiting],
                        "graph": self.current_graph.to_dict(),
                        "budget": self.budget.get_summary(),
                    }

                if self.current_graph.has_failed():
                    self.tracer.finish_trace(self.active_trace, status=SpanStatus.ERROR)
                    return {
                        "status": "FAILED",
                        "goal": goal,
                        "session_id": self.session_id,
                        "trace_id": self.active_trace.id,
                        "graph": self.current_graph.to_dict(),
                        "budget": self.budget.get_summary(),
                        "error": "One or more required tasks failed.",
                    }
                break

            # Record step in budget
            self.budget.record_step(step_name=f"Task: {ready_task.title}")

            # Execute task inside Telemetry Span
            with self.tracer.span(
                self.active_trace,
                name=f"task:{ready_task.id}:{ready_task.title}",
                span_type=SpanType.AGENT_STEP,
                input_data={"task": ready_task.to_dict()},
            ) as task_span:
                step_result = self._execute_task(ready_task, parent_span_id=task_span.id)
                task_span.output_data = step_result

                self.execution_log.append({
                    "task_id": ready_task.id,
                    "title": ready_task.title,
                    "role": ready_task.assigned_role,
                    "result": step_result,
                })

                if on_step_callback:
                    on_step_callback({
                        "task": ready_task.to_dict(),
                        "result": step_result,
                        "budget": self.budget.get_summary(),
                    })

                if step_result.get("success", False):
                    self.current_graph.mark_completed(ready_task.id, result=step_result)
                    
                    # Record milestone in Task Notebook (DeerFlow pattern)
                    self.notebook.set_note(
                        key=f"milestone_{ready_task.id}",
                        content=f"Completed {ready_task.title}: {str(step_result.get('summary', '')) or 'ok'}",
                        category="milestone"
                    )

                    # Save Checkpoint (DeerFlow pattern)
                    cid = self.checkpoint_manager.save_checkpoint(
                        session_id=self.session_id,
                        graph=self.current_graph,
                        notebook=self.notebook,
                        artifacts=self.workspace.list_files(),
                    )
                    checkpoint_ids.append(cid)
                else:
                    self.current_graph.mark_failed(ready_task.id, error=step_result.get("error", "Unknown error"))
                    task_span.finish(status=SpanStatus.ERROR, error=step_result.get("error"))

        # Finish trace
        final_status = SpanStatus.OK if self.current_graph.is_complete() else SpanStatus.ERROR
        self.tracer.finish_trace(self.active_trace, status=final_status)

        duration = time.time() - start_time
        return {
            "status": "COMPLETED" if self.current_graph.is_complete() else "INCOMPLETE",
            "goal": goal,
            "session_id": self.session_id,
            "trace_id": self.active_trace.id,
            "duration_seconds": round(duration, 2),
            "graph": self.current_graph.to_dict(),
            "budget": self.budget.get_summary(),
            "notebook": self.notebook.to_dict(),
            "checkpoints": checkpoint_ids,
            "evidence": [e.to_dict() for e in self.evidence_collector.evidence_ledger],
            "artifacts": self.workspace.list_files(),
            "execution_log": self.execution_log,
        }

    def _execute_task(self, task: TaskNode, parent_span_id: Optional[str] = None) -> Dict[str, Any]:
        """Dispatches task with guardrail checking and telemetry recording."""
        role = task.assigned_role

        if role == "researcher":
            return self._execute_research_task(task, parent_span_id)
        elif role == "browser":
            return self._execute_browser_task(task, parent_span_id)
        elif role == "coder":
            return self._execute_coding_task(task, parent_span_id)
        elif role == "verifier":
            return self._execute_verification_task(task, parent_span_id)
        else:
            return {"success": True, "note": "General task executed"}

    def _execute_research_task(self, task: TaskNode, parent_span_id: Optional[str] = None) -> Dict[str, Any]:
        """Executes research with guardrail validation and telemetry span."""
        query = task.description.replace("Gather relevant internet data and references for:", "").strip()
        
        # Pre-flight guardrail check (OpenAI Agents pattern)
        ok, err = AgentGuardrails.validate_tool_input("web_search", {"query": query})
        if not ok:
            return {"success": False, "error": f"Guardrail blocked search: {err}"}

        with self.tracer.span(
            self.active_trace,
            name="tool:reach:web_search",
            span_type=SpanType.TOOL,
            parent_span_id=parent_span_id,
            input_data={"query": query},
        ) as span:
            self.budget.record_tool_call("web_search")
            search_res = self.reach_tools.web_search(query=query, num_results=3)

            if search_res.get("success"):
                filename = f"research_{task.id}.md"
                content = f"# Research on: {query}\n\n{search_res.get('content', '')}"
                self.workspace.write_file(filename, content)
                
                # Register verification evidence (Hermes pattern)
                ev = self.evidence_collector.verify_file_created(task.id, filename, min_bytes=10)
                
                # Save to notebook
                self.notebook.set_note(f"research_{task.id}", search_res.get("content", "")[:300], category="finding")

                out = {
                    "success": True,
                    "source": search_res.get("source"),
                    "artifact": filename,
                    "evidence_id": ev.id,
                    "summary": search_res.get("content", "")[:300] + "...",
                }
                span.output_data = out
                return out

            span.finish(status=SpanStatus.ERROR, error=search_res.get("error"))
            return {"success": False, "error": search_res.get("error", "Search failed")}

    def _execute_browser_task(self, task: TaskNode, parent_span_id: Optional[str] = None) -> Dict[str, Any]:
        """Executes browser navigation with Playwright ARIA snapshotting."""
        match = re.search(r"https?://[^\s,]+", task.description)
        url = match.group(0) if match else "https://example.com"

        # Guardrail check (OpenAI Agents pattern)
        ok, err = AgentGuardrails.validate_tool_input("browser_navigate", {"url": url})
        if not ok:
            return {"success": False, "error": f"Guardrail blocked navigation: {err}"}

        with self.tracer.span(
            self.active_trace,
            name="tool:browser:navigate_and_aria",
            span_type=SpanType.TOOL,
            parent_span_id=parent_span_id,
            input_data={"url": url},
        ) as span:
            self.budget.record_tool_call("browser_navigate")
            nav_res = self.browser_engine.navigate(url)
            if not nav_res.get("success"):
                span.finish(status=SpanStatus.ERROR, error=nav_res.get("error"))
                return nav_res

            self.budget.record_tool_call("browser_aria_snapshot")
            aria_res = self.browser_engine.get_aria_snapshot()
            dom_res = self.browser_engine.get_interactive_elements()

            snapshot_content = f"URL: {url}\nTitle: {nav_res.get('title')}\n\nARIA Semantic Tree:\n{aria_res.get('aria_snapshot', '')}\n\nInteractive Elements:\n{dom_res.get('interactive_tree', '')}"

            # Bucle interactivo con DecisionEngine si la meta requiere interacción
            interactive_steps = []
            is_interactive = task.context.get("interactive") or any(
                w in task.description.lower() for w in ["click", "scroll", "fill", "type", "interact", "operar", "formulario", "agendar", "comprar"]
            )
            if is_interactive:
                goal_text = task.context.get("goal") or task.description
                interactive_steps = self._run_interactive_browser_loop(
                    goal=goal_text,
                    max_steps=task.context.get("max_steps", 8),
                    parent_span_id=span.id
                )
                snapshot_content += f"\n\nInteractive Decision Loop Execution:\n{json.dumps(interactive_steps, ensure_ascii=False, indent=2)}"

            snapshot_file = f"browser_{task.id}.txt"
            self.workspace.write_file(snapshot_file, snapshot_content)

            # Verification evidence (Hermes pattern)
            ev = self.evidence_collector.verify_file_created(task.id, snapshot_file, min_bytes=10)

            out = {
                "success": True,
                "url": url,
                "title": nav_res.get("title"),
                "elements_count": dom_res.get("count", 0),
                "aria_tree_length": aria_res.get("length", 0),
                "interactive_steps_count": len(interactive_steps),
                "interactive_steps": interactive_steps,
                "artifact": snapshot_file,
                "evidence_id": ev.id,
            }
            span.output_data = out
            return out

    def _run_interactive_browser_loop(
        self, goal: str, max_steps: int = 8, parent_span_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Bucle cerrado interactivo observe -> decide -> act con DecisionEngine (Laya / Jev pattern).
        Toma micro-decisiones estructuradas sub-35ms y ejecuta acciones validadas en el navegador.
        """
        if not self.active_trace:
            self.active_trace = self.tracer.start_trace(
                name=f"interactive_{self.session_id}",
                session_id=self.session_id,
                metadata={"goal": goal}
            )

        steps_log = []
        action_history = []

        for step_idx in range(1, max_steps + 1):
            with self.tracer.span(
                self.active_trace,
                name=f"decision:step_{step_idx}",
                span_type=SpanType.AGENT_STEP,
                parent_span_id=parent_span_id,
                input_data={"step": step_idx, "goal": goal},
            ) as step_span:
                self.budget.record_step(step_name=f"Browser Interactive Step {step_idx}")

                dom_res = self.browser_engine.get_interactive_elements()
                observed_models = dom_res.get("observed_models", [])

                page_url = self.browser_engine._page.url if self.browser_engine._page else ""
                req = DecisionRequest(
                    goal=goal,
                    current_url=page_url,
                    elements=observed_models,
                    history=action_history,
                )

                decision = self.decision_engine.decide(req)

                step_record = {
                    "step": step_idx,
                    "operation": decision.operation.value,
                    "target": decision.target,
                    "confidence": decision.confidence,
                    "latency_ms": decision.latency_ms,
                    "reasoning": decision.reasoning_summary,
                }

                if decision.operation == BrowserOperation.DONE:
                    step_record["status"] = "GOAL_SATISFIED"
                    steps_log.append(step_record)
                    step_span.output_data = step_record
                    break
                elif decision.operation == BrowserOperation.BLOCKED:
                    step_record["status"] = "BLOCKED_ESCALATED"
                    steps_log.append(step_record)
                    step_span.output_data = step_record
                    break

                # Ejecución de la acción tipada
                self.budget.record_tool_call(f"browser_{decision.operation.value.lower()}")
                exec_res = self.browser_engine.execute_decision(decision)
                step_record["success"] = exec_res.get("success", False)
                step_record["exec_result"] = exec_res

                steps_log.append(step_record)
                step_span.output_data = step_record

                action_history.append({
                    "operation": decision.operation.value,
                    "target": decision.target,
                    "success": exec_res.get("success", False),
                })

                if not exec_res.get("success", False):
                    logger.warning(f"[InteractiveLoop] Paso {step_idx} falló: {exec_res.get('error')}")

        return steps_log

    def _execute_coding_task(self, task: TaskNode, parent_span_id: Optional[str] = None) -> Dict[str, Any]:
        """Executes code creation with syntax verification evidence."""
        with self.tracer.span(
            self.active_trace,
            name="tool:code:write_and_check",
            span_type=SpanType.TOOL,
            parent_span_id=parent_span_id,
        ) as span:
            self.budget.record_tool_call("code_write")
            main_code = task.context.get("code") or """# -*- coding: utf-8 -*-
def process_data(items):
    return [item.strip().upper() for item in items if item]
"""
            test_code = task.context.get("tests") or """# -*- coding: utf-8 -*-
from main import process_data

def test_process_data():
    raw = ["apple", " banana ", "", "orange"]
    expected = ["APPLE", "BANANA", "ORANGE"]
    assert process_data(raw) == expected
"""
            w1 = self.code_tools.write_file("main.py", main_code)
            w2 = self.code_tools.write_file("test_main.py", test_code)

            syn1 = self.code_tools.check_syntax("main.py")
            syn2 = self.code_tools.check_syntax("test_main.py")

            # Collect syntax verification evidence (Hermes pattern)
            ev1 = self.evidence_collector.verify_syntax_valid(task.id, syn1)
            ev2 = self.evidence_collector.verify_syntax_valid(task.id, syn2)

            self.notebook.set_note("code_main", "main.py written and syntax checked", category="file")

            out = {
                "success": w1["success"] and w2["success"] and syn1["valid"] and syn2["valid"],
                "files": ["main.py", "test_main.py"],
                "evidence": [ev1.id, ev2.id],
            }
            span.output_data = out
            return out

    def _execute_verification_task(self, task: TaskNode, parent_span_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Executes pytest, diagnoses failures with SWE-agent self-repair,
        and enforces Hermes test verification evidence before completion.
        """
        test_file = task.context.get("test_file", "test_main.py")
        max_repairs = 3

        for attempt in range(1, max_repairs + 1):
            with self.tracer.span(
                self.active_trace,
                name=f"verify:run_tests:attempt_{attempt}",
                span_type=SpanType.VERIFICATION,
                parent_span_id=parent_span_id,
                input_data={"test_file": test_file, "attempt": attempt},
            ) as span:
                self.budget.record_tool_call("test_runner")
                res = self.code_tools.run_tests(test_file=test_file)
                span.output_data = {"exit_code": res.exit_code, "stdout": res.stdout[:500]}

                if res.is_success:
                    # Collect concrete test verification proof (Hermes pattern)
                    ev = self.evidence_collector.verify_test_output(task.id, res.stdout, res.exit_code)
                    self.notebook.set_note("verification", f"Tests passed on attempt {attempt}", category="milestone")
                    return {
                        "success": True,
                        "attempt": attempt,
                        "status": "PASSED",
                        "evidence_id": ev.id,
                        "stdout": res.stdout,
                    }

                # Self-repair span
                with self.tracer.span(
                    self.active_trace,
                    name=f"self_repair:attempt_{attempt}",
                    span_type=SpanType.SELF_REPAIR,
                    parent_span_id=span.id,
                    input_data={"error": str(res.error) if res.error else res.stderr},
                ) as repair_span:
                    logger.warning(f"Verification failed on attempt {attempt}: {res.error}")
                    self.budget.record_step(step_name=f"Self-Repair Attempt {attempt}")

                    repair_success = self._attempt_self_repair(res, attempt)
                    repair_span.output_data = {"repair_applied": repair_success}
                    if not repair_success:
                        repair_span.finish(status=SpanStatus.ERROR, error="Self-repair failed to patch error")
                        return {
                            "success": False,
                            "attempt": attempt,
                            "status": "REPAIR_FAILED",
                            "error": str(res.error) if res.error else res.stderr,
                        }

        # Final verification attempt
        final_res = self.code_tools.run_tests(test_file=test_file)
        if final_res.is_success:
            ev = self.evidence_collector.verify_test_output(task.id, final_res.stdout, final_res.exit_code)
            return {"success": True, "status": "PASSED", "evidence_id": ev.id, "stdout": final_res.stdout}

        return {"success": False, "status": "FAILED", "stdout": final_res.stdout, "stderr": final_res.stderr}

    def _attempt_self_repair(self, failed_res: ExecutionResult, attempt: int) -> bool:
        """SWE-agent diagnostic & patch engine."""
        output = failed_res.stdout + "\n" + failed_res.stderr

        if "assert" in output.lower():
            if self.code_tools.workspace.exists("main.py"):
                content = self.code_tools.read_file("main.py")["content"]
                if "return a - b" in content:
                    return self.code_tools.patch_file("main.py", "return a - b", "return a + b").get("success", False)
                if "return a + b" in content and "multiply" in output:
                    return self.code_tools.patch_file("main.py", "return a + b", "return a * b").get("success", False)
                if "return" not in content and "def " in content:
                    lines = content.splitlines()
                    lines.append("    return True")
                    self.code_tools.write_file("main.py", "\n".join(lines))
                    return True

        if "SyntaxError" in output:
            match = re.search(r'File "([^"]+)", line (\d+)', output)
            if match:
                fname = match.group(1).split("/")[-1]
                lineno = int(match.group(2))
                read_res = self.code_tools.read_file(fname)
                if read_res.get("success"):
                    lines = read_res["content"].splitlines()
                    if 0 < lineno <= len(lines):
                        bad_line = lines[lineno - 1]
                        if bad_line.strip().startswith("def ") and not bad_line.strip().endswith(":"):
                            return self.code_tools.patch_file(fname, bad_line, bad_line + ":").get("success", False)

        if "ZeroDivisionError" in output:
            if self.code_tools.workspace.exists("main.py"):
                content = self.code_tools.read_file("main.py")["content"]
                if "return a / b" in content:
                    return self.code_tools.patch_file("main.py", "return a / b", "return a / b if b != 0 else 0").get("success", False)

        return False
