# -*- coding: utf-8 -*-
"""
Firby 2.0 Autonomous Multi-Agent API Router (FastAPI).
Exposes endpoints for high-level goal execution, task DAG monitoring,
interactive browser/sandbox actions, human approval gates,
Langfuse-style tracing telemetry, and DeerFlow-style checkpoint management.
"""
from __future__ import annotations

import logging
import uuid
from typing import Dict, Any, Optional

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field

from src.core.agent.autonomous_loop import AutonomousAgent
from src.core.governance.budget_guard import BudgetLimits
from src.core.planner.task_graph import TaskStatus
from src.core.telemetry import global_tracer

logger = logging.getLogger("firby.autonomous_routes")
router = APIRouter(prefix="/api/v2/agent", tags=["Autonomous Agent 2.0"])

# In-memory store of active agent sessions
ACTIVE_AGENT_SESSIONS: Dict[str, AutonomousAgent] = {}


class GoalRequest(BaseModel):
    goal: str = Field(..., description="High-level natural language goal")
    max_steps: Optional[int] = Field(30, description="Max execution steps")
    max_duration_seconds: Optional[float] = Field(300.0, description="Max execution duration in seconds")


class ApprovalRequestBody(BaseModel):
    session_id: str
    task_id: str
    action: str = Field("approve", description="'approve' or 'reject'")
    reason: Optional[str] = None


@router.get("/capabilities")
async def get_agent_capabilities():
    """Returns the catalog of active tools and subsystem capabilities."""
    return {
        "status": "online",
        "version": "2.0.0",
        "capabilities": {
            "sandbox_execution": {
                "engine": "E2B-isolated-runner",
                "languages": ["python", "bash", "javascript"],
                "features": ["environment_scrubbing", "timeout_enforcement", "traceback_parsing", "artifact_tracking"],
            },
            "internet_research": {
                "engine": "Agent-Reach",
                "backends": ["Exa Semantic MCP", "Jina Reader Markdown", "GitHub API"],
                "zero_fee_routing": True,
            },
            "browser_automation": {
                "engine": "Playwright Headless Chromium",
                "features": ["aria_accessibility_tree", "numerical_dom_indexing", "click", "fill_forms", "extract_text", "screenshots"],
            },
            "autonomous_loop": {
                "pattern": "SWE-agent-loop",
                "features": ["goal_dag_decomposition", "test_verification", "traceback_diagnosis", "iterative_self_repair"],
            },
            "observability": {
                "pattern": "Langfuse-tracing",
                "features": ["hierarchical_spans", "millisecond_latency", "token_telemetry", "sqlite_persistence"],
            },
            "task_continuity": {
                "pattern": "DeerFlow-checkpoints",
                "features": ["bounded_task_notebooks", "sqlite_checkpoints", "state_recovery"],
            },
            "governance": {
                "pattern": "Paperclip-governance & OpenAI-Guardrails",
                "features": ["step_limits", "budget_enforcement", "pre_flight_tool_guardrails", "human_approval_gates"],
            },
            "verification_evidence": {
                "pattern": "Hermes-evidence-engine",
                "features": ["test_pass_validation", "artifact_existence_checks", "syntax_verification_evidence"],
            },
        },
    }


@router.post("/goal")
async def submit_goal(req: GoalRequest):
    """Submits a high-level goal, generates a Task DAG, and initializes an agent session."""
    session_id = f"sess_{uuid.uuid4().hex[:12]}"
    limits = BudgetLimits(
        max_steps=req.max_steps or 30,
        max_duration_seconds=req.max_duration_seconds or 300.0,
    )
    agent = AutonomousAgent(budget_limits=limits, session_id=session_id)
    graph = agent.plan_goal(req.goal)

    ACTIVE_AGENT_SESSIONS[session_id] = agent

    return {
        "ok": True,
        "session_id": session_id,
        "goal": req.goal,
        "tasks_planned": len(graph.tasks),
        "graph": graph.to_dict(),
        "budget": agent.budget.get_summary(),
    }


@router.post("/run")
async def execute_agent_session(session_id: str):
    """Executes the agent session until completion or human approval gate."""
    agent = ACTIVE_AGENT_SESSIONS.get(session_id)
    if not agent or not agent.current_graph:
        raise HTTPException(status_code=404, detail="Agent session or plan not found")

    result = agent.run_until_complete(goal=agent.current_graph.goal, graph=agent.current_graph)
    return {
        "ok": True,
        "session_id": session_id,
        "result": result,
    }


@router.get("/status/{session_id}")
async def get_session_status(session_id: str):
    """Returns the current state of tasks, execution log, and artifacts."""
    agent = ACTIVE_AGENT_SESSIONS.get(session_id)
    if not agent or not agent.current_graph:
        raise HTTPException(status_code=404, detail="Session not found")

    return {
        "ok": True,
        "session_id": session_id,
        "goal": agent.current_graph.goal,
        "is_complete": agent.current_graph.is_complete(),
        "has_failed": agent.current_graph.has_failed(),
        "graph": agent.current_graph.to_dict(),
        "budget": agent.budget.get_summary(),
        "notebook": agent.notebook.to_dict(),
        "artifacts": agent.workspace.list_files(),
        "evidence": [e.to_dict() for e in agent.evidence_collector.evidence_ledger],
        "execution_log": agent.execution_log,
    }


@router.post("/approve")
async def approve_task(body: ApprovalRequestBody):
    """Approves or rejects a task held at a human approval gate."""
    agent = ACTIVE_AGENT_SESSIONS.get(body.session_id)
    if not agent or not agent.current_graph:
        raise HTTPException(status_code=404, detail="Session not found")

    if body.task_id not in agent.current_graph.tasks:
        raise HTTPException(status_code=404, detail="Task ID not found in plan")

    task = agent.current_graph.tasks[body.task_id]
    if body.action == "approve":
        success = agent.current_graph.approve_task(body.task_id)
        return {"ok": success, "task_id": body.task_id, "new_status": task.status.value}
    else:
        task.status = TaskStatus.FAILED
        task.error = body.reason or "Rejected by human operator"
        return {"ok": True, "task_id": body.task_id, "new_status": task.status.value}


# ── Observability & Telemetry Endpoints (Langfuse) ───────────────────────────

@router.get("/traces")
async def list_recent_traces(limit: int = 20):
    """Lists recent execution traces with duration and token summaries."""
    traces = global_tracer.list_recent_traces(limit=limit)
    return {"ok": True, "count": len(traces), "traces": traces}


@router.get("/trace/{trace_id}")
async def get_trace_details(trace_id: str):
    """Returns detailed trace telemetry including all nested spans."""
    trace_data = global_tracer.get_trace(trace_id)
    if not trace_data:
        raise HTTPException(status_code=404, detail=f"Trace {trace_id} not found")
    return {"ok": True, "trace": trace_data}


# ── Workflow Continuity & Checkpoints Endpoints (DeerFlow) ───────────────────

@router.get("/checkpoints/{session_id}")
async def get_session_checkpoints(session_id: str):
    """Returns checkpoint history for an agent session."""
    agent = ACTIVE_AGENT_SESSIONS.get(session_id)
    if agent:
        checkpoints = agent.checkpoint_manager.list_checkpoints_for_session(session_id)
    else:
        from src.core.planner.checkpoint import WorkflowCheckpointManager
        checkpoints = WorkflowCheckpointManager().list_checkpoints_for_session(session_id)
    return {"ok": True, "session_id": session_id, "checkpoints": checkpoints}
