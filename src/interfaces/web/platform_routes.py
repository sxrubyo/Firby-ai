# -*- coding: utf-8 -*-
"""
Firby Platform — Web & REST Interface Routes
============================================
Expone los endpoints del Control Plane y del Data Plane multi-tenant:
1. PUBLIC API (WIDGET RUNTIME):
   - GET  /public/agents/{public_id}/bootstrap : Bootstrap público seguro sin secretos.
   - POST /public/agents/{public_id}/chat      : Endpoint de chat seguro con session pinning.
   - POST /public/agents/{public_id}/observe   : Observación de interfaz (protocolo de 2 fases).
   - GET  /firby.js                            : SDK de instalación en 1 línea.
2. CONTROL PLANE API (WORKSPACE DASHBOARD):
   - GET/POST /api/platform/tenants
   - GET/POST /api/platform/tenants/{tenant_id}/agents
   - GET      /api/platform/agents/{agent_id}/manifest
   - GET      /api/platform/agents/{agent_id}/versions
   - POST     /api/platform/agents/{agent_id}/validate
   - POST     /api/platform/agents/{agent_id}/publish
   - POST     /api/platform/agents/{agent_id}/rollback
   - GET      /api/platform/audit-logs
   - GET/POST /api/platform/agents/{agent_id}/knowledge
"""

from __future__ import annotations
import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional

from fastapi import APIRouter, Request, Response, HTTPException
from fastapi.responses import JSONResponse, FileResponse

from src.core.platform.models import TenantStatus, AgentStatus
from src.core.platform.store import platform_store
from src.core.platform.manager import control_plane
from src.core.platform.session import widget_session_manager
from src.core.platform.bootstrap import public_bootstrap_service
from src.core.platform.knowledge import tenant_knowledge_engine
from src.core.platform.migration import resolve_tenant_agent_pair
from src.core.platform.control import agent_control, RunControlState
from src.core.platform.discovery import onboarding_engine, self_inspector

log = logging.getLogger("firby.platform.routes")

router = APIRouter(tags=["Firby Multi-Tenant Platform"])

FIRBY_JS_PATH = Path(__file__).resolve().parents[0] / "static" / "firby.js"


# ═════════════════════════════════════════════════════════════════════════════
# 1. PUBLIC AGENT RUNTIME & EMBED (ZERO SECRETS)
# ═════════════════════════════════════════════════════════════════════════════

@router.get("/firby.js")
async def get_firby_embed_script():
    """Sirve el archivo SDK javascript de instalación en una línea."""
    if FIRBY_JS_PATH.exists():
        return FileResponse(
            FIRBY_JS_PATH,
            media_type="application/javascript",
            headers={"Cache-Control": "public, max-age=300"}
        )
    raise HTTPException(status_code=404, detail="firby.js not found")


@router.get("/public/agents/{public_id}/bootstrap")
async def public_agent_bootstrap(public_id: str, request: Request, session_token: Optional[str] = None):
    """
    Bootstrap seguro del agente para el widget web.
    Resuelve la identidad del negocio y entrega únicamente metadatos públicos autorizados.
    """
    client_ip = request.client.host if request.client else ""
    client_meta = {
        "ip": client_ip,
        "user_agent": request.headers.get("user-agent", "")
    }

    res = public_bootstrap_service.bootstrap_agent(
        public_id=public_id,
        session_token=session_token,
        client_metadata=client_meta
    )
    if not res.get("ok"):
        return JSONResponse(res, status_code=404 if "no encontrado" in str(res.get("error")) else 400)
    return JSONResponse(res)


@router.post("/public/agents/{public_id}/chat")
async def public_agent_chat(public_id: str, request: Request):
    """
    Endpoint de mensajería con el agente público con Tenant Pinning forzado en backend.
    """
    try:
        data = await request.json()
    except Exception:
        return JSONResponse({"ok": False, "error": "Formato JSON inválido."}, status_code=400)

    message = (data.get("message") or "").strip()
    session_token = data.get("session_token")
    run_id = (data.get("run_id") or "").strip()
    observation = data.get("observation")

    if not message and not observation:
        return JSONResponse({"ok": False, "error": "Mensaje u observación requeridos."}, status_code=400)

    client_ip = request.client.host if request.client else ""
    client_meta = {
        "ip": client_ip,
        "user_agent": request.headers.get("user-agent", "")
    }

    # 1. Vincular sesión de forma estricta (Tenant Pinning)
    token, tenant_id, agent_id, conv_id = widget_session_manager.validate_and_bind(
        session_token=session_token,
        public_id=public_id,
        client_metadata=client_meta
    )

    from src.core.widget_operator import widget_operator

    # 2. Manejo de observación de dos fases
    if observation and run_id:
        try:
            obs_res = await widget_operator.handle_observation(
                run_id=run_id,
                observation=observation,
                user_id=conv_id,
                org_id=tenant_id,
                agent_id=agent_id
            )
            obs_res["session_token"] = token
            return JSONResponse(obs_res)
        except Exception as e:
            log.error(f"[PublicChat] Error procesando observación: {e}", exc_info=True)
            return JSONResponse({"ok": False, "error": str(e)}, status_code=500)

    # 3. Manejo de mensaje conversacional regular
    web_context = data.get("web_context") or {
        "current_url": "/",
        "page_title": "Firby"
    }
    if run_id and "run_id" not in web_context:
        web_context["run_id"] = run_id

    try:
        chat_res = await widget_operator.handle_message(
            message=message,
            user_id=conv_id,
            org_id=tenant_id,
            web_context=web_context,
            agent_id=agent_id
        )
        chat_res["session_token"] = token
        return JSONResponse(chat_res)
    except Exception as e:
        log.error(f"[PublicChat] Error procesando mensaje: {e}", exc_info=True)
        return JSONResponse({"ok": False, "error": f"Error interno: {str(e)[:200]}"}, status_code=500)


@router.post("/public/agents/{public_id}/observe")
async def public_agent_observe(public_id: str, request: Request):
    """Reporte de observaciones de interfaz para el agente público."""
    try:
        data = await request.json()
    except Exception:
        return JSONResponse({"ok": False, "error": "Formato JSON inválido."}, status_code=400)

    run_id = (data.get("run_id") or "").strip()
    observation = data.get("observation") or data
    session_token = data.get("session_token")

    token, tenant_id, agent_id, conv_id = widget_session_manager.validate_and_bind(
        session_token=session_token,
        public_id=public_id
    )

    from src.core.widget_operator import widget_operator
    res = await widget_operator.handle_observation(
        run_id=run_id,
        observation=observation,
        user_id=conv_id,
        org_id=tenant_id,
        agent_id=agent_id
    )
    res["session_token"] = token
    return JSONResponse(res)


# ═════════════════════════════════════════════════════════════════════════════
# 2. CONTROL PLANE API (WORKSPACE / ADMINISTRACIÓN)
# ═════════════════════════════════════════════════════════════════════════════

@router.get("/api/platform/tenants")
async def list_tenants():
    """Lista todos los tenants registrados."""
    tenants = control_plane.list_tenants()
    return {"ok": True, "tenants": [t.to_dict() for t in tenants]}


@router.post("/api/platform/tenants")
async def create_tenant(request: Request):
    """Crea un nuevo tenant en la plataforma."""
    data = await request.json()
    tid = data.get("tenant_id")
    name = data.get("name")
    if not tid or not name:
        return JSONResponse({"ok": False, "error": "tenant_id y name son requeridos."}, status_code=400)
    tenant = control_plane.create_tenant(tid, name, metadata=data.get("metadata"))
    return {"ok": True, "tenant": tenant.to_dict()}


@router.get("/api/platform/tenants/{tenant_id}/agents")
async def list_agents(tenant_id: str):
    """Lista todos los agentes de un tenant."""
    agents = control_plane.list_agents(tenant_id)
    return {"ok": True, "agents": [a.to_dict() for a in agents]}


@router.post("/api/platform/tenants/{tenant_id}/agents")
async def create_agent(tenant_id: str, request: Request):
    """Crea una nueva instancia de agente en un tenant."""
    data = await request.json()
    aid = data.get("agent_id")
    name = data.get("name")
    if not aid or not name:
        return JSONResponse({"ok": False, "error": "agent_id y name son requeridos."}, status_code=400)

    try:
        agent = control_plane.create_agent(
            tenant_id=tenant_id,
            agent_id=aid,
            name=name,
            public_id=data.get("public_id"),
            allowed_channels=data.get("allowed_channels"),
            metadata=data.get("metadata")
        )
        return {"ok": True, "agent": agent.to_dict()}
    except ValueError as e:
        return JSONResponse({"ok": False, "error": str(e)}, status_code=400)


@router.get("/api/platform/agents/{agent_id}/manifest")
async def get_agent_manifest(agent_id: str, tenant_id: Optional[str] = None):
    """Obtiene el AgentManifest de la versión actualmente publicada."""
    tid = tenant_id or "tenant_demo"
    manifest = control_plane.get_published_manifest(tid, agent_id)
    if not manifest:
        return JSONResponse({"ok": False, "error": "No hay manifiesto publicado para este agente."}, status_code=404)
    return {"ok": True, "manifest": manifest.to_dict()}


@router.get("/api/platform/agents/{agent_id}/versions")
async def list_agent_versions(agent_id: str, tenant_id: Optional[str] = None):
    """Lista el historial de versiones publicadas para rollback."""
    tid = tenant_id or "tenant_demo"
    versions = platform_store.list_agent_versions(tid, agent_id)
    return {"ok": True, "versions": [v.to_dict() for v in versions]}


@router.post("/api/platform/agents/{agent_id}/validate")
async def validate_agent(agent_id: str, request: Request):
    """Valida la consistencia de un agente antes de permitir su publicación."""
    data = await request.json()
    tid = data.get("tenant_id") or "tenant_demo"
    res = control_plane.validate_agent_for_publish(tid, agent_id)
    return {"ok": True, "validation": {"valid": res.valid, "errors": res.errors, "warnings": res.warnings}}


@router.post("/api/platform/agents/{agent_id}/publish")
async def publish_agent(agent_id: str, request: Request):
    """Publica una nueva versión inmutable del agente."""
    data = await request.json()
    tid = data.get("tenant_id") or "tenant_demo"
    published_by = data.get("published_by") or "admin"

    try:
        manifest = control_plane.publish_agent(tid, agent_id, published_by=published_by)
        return {"ok": True, "manifest": manifest.to_dict()}
    except ValueError as e:
        return JSONResponse({"ok": False, "error": str(e)}, status_code=400)


@router.post("/api/platform/agents/{agent_id}/rollback")
async def rollback_agent(agent_id: str, request: Request):
    """Restaura una versión previa del agente."""
    data = await request.json()
    tid = data.get("tenant_id") or "tenant_demo"
    target_version = data.get("version")
    if not target_version:
        return JSONResponse({"ok": False, "error": "version es requerido para rollback."}, status_code=400)

    try:
        manifest = control_plane.rollback_agent(tid, agent_id, target_version=int(target_version))
        return {"ok": True, "manifest": manifest.to_dict()}
    except ValueError as e:
        return JSONResponse({"ok": False, "error": str(e)}, status_code=400)


@router.get("/api/platform/audit-logs")
async def get_audit_logs(tenant_id: Optional[str] = None, agent_id: Optional[str] = None, limit: int = 50):
    """Consulta los registros de auditoría."""
    tid = tenant_id or "tenant_demo"
    events = control_plane.get_audit_log(tid, agent_id, limit=limit)
    return {"ok": True, "events": [e.to_dict() for e in events]}


# ═════════════════════════════════════════════════════════════════════════════
# 3. VERIFIABLE AGENT CONTROL & RUN LIFECYCLE API
# ═════════════════════════════════════════════════════════════════════════════

@router.get("/api/platform/agents/{agent_id}/capabilities")
async def get_agent_capability_matrix(agent_id: str, tenant_id: Optional[str] = None):
    """Retorna la matriz verificable de capacidades para una instancia de agente."""
    tid = tenant_id or "tenant_demo"
    matrix = agent_control.get_capability_matrix(tid, agent_id)
    return {"ok": True, "tenant_id": tid, "agent_id": agent_id, "capabilities": [c.to_dict() for c in matrix]}


@router.get("/api/platform/runs/{run_id}")
async def get_agent_run_status(run_id: str):
    """Consulta el estado y registro auditable de un turno de ejecución."""
    run = agent_control.get_run(run_id)
    if not run:
        return JSONResponse({"ok": False, "error": "Run no encontrado."}, status_code=404)
    return {"ok": True, "run": run.to_dict()}


@router.post("/api/platform/runs/{run_id}/pause")
async def pause_agent_run(run_id: str, request: Request):
    """Pausa la ejecución de un turno en curso."""
    data = await request.json() if request.headers.get("content-type") == "application/json" else {}
    actor = data.get("actor", "admin")
    ok = agent_control.pause_run(run_id, actor=actor)
    return {"ok": ok}


@router.post("/api/platform/runs/{run_id}/resume")
async def resume_agent_run(run_id: str, request: Request):
    """Reanuda la ejecución de un turno pausado."""
    data = await request.json() if request.headers.get("content-type") == "application/json" else {}
    actor = data.get("actor", "admin")
    ok = agent_control.resume_run(run_id, actor=actor)
    return {"ok": ok}


@router.post("/api/platform/runs/{run_id}/cancel")
async def cancel_agent_run(run_id: str, request: Request):
    """Cancela limpiamente la ejecución de un turno."""
    data = await request.json() if request.headers.get("content-type") == "application/json" else {}
    reason = data.get("reason", "cancelled_by_admin")
    actor = data.get("actor", "admin")
    ok = agent_control.cancel_run(run_id, reason=reason, actor=actor)
    return {"ok": ok}


@router.post("/api/platform/runs/{run_id}/approve")
async def approve_agent_action(run_id: str, request: Request):
    """Aprueba una acción en espera de supervisión humana (HITL)."""
    data = await request.json() if request.headers.get("content-type") == "application/json" else {}
    actor = data.get("actor", "admin")
    ok, action = agent_control.approve_action(run_id, actor=actor)
    return {"ok": ok, "action": action}


@router.post("/api/platform/runs/{run_id}/deny")
async def deny_agent_action(run_id: str, request: Request):
    """Rechaza una acción en espera de supervisión humana."""
    data = await request.json() if request.headers.get("content-type") == "application/json" else {}
    reason = data.get("reason", "denied_by_admin")
    actor = data.get("actor", "admin")
    ok = agent_control.deny_action(run_id, reason=reason, actor=actor)
    return {"ok": ok}


# ═════════════════════════════════════════════════════════════════════════════
# 4. SELF-INSPECTION & SYSTEM DIAGNOSTIC API
# ═════════════════════════════════════════════════════════════════════════════

@router.get("/api/platform/self-inspection")
async def platform_self_inspection():
    """Diagnóstico e introspección factual del sistema Firby sin alucinaciones."""
    report = self_inspector.inspect()
    return {"ok": True, "report": report.to_dict()}


# ═════════════════════════════════════════════════════════════════════════════
# 5. FIRST-TIME INSTALLATION & ONBOARDING API
# ═════════════════════════════════════════════════════════════════════════════

@router.post("/api/platform/onboarding/start")
async def start_onboarding(request: Request):
    """Inicia el proceso de instalación y descubrimiento autónomo de un sitio web."""
    data = await request.json()
    url = data.get("website_url")
    name = data.get("business_name")
    if not url or not name:
        return JSONResponse({"ok": False, "error": "website_url y business_name son requeridos."}, status_code=400)

    session = onboarding_engine.start_onboarding(url, name)
    return {"ok": True, "session": session.to_dict()}


@router.get("/api/platform/onboarding/{session_id}")
async def get_onboarding_status(session_id: str):
    """Consulta el estado actual del proceso de instalación."""
    session = onboarding_engine.get_session(session_id)
    if not session:
        return JSONResponse({"ok": False, "error": "Sesión de instalación no encontrada."}, status_code=404)
    return {"ok": True, "session": session.to_dict()}


@router.post("/api/platform/onboarding/{session_id}/answer")
async def answer_onboarding_questions(session_id: str, request: Request):
    """Registra respuestas a las preguntas de la entrevista dinámica de onboarding."""
    data = await request.json()
    answers = data.get("answers", {})
    session = onboarding_engine.answer_interview(session_id, answers)
    if not session:
        return JSONResponse({"ok": False, "error": "Sesión de instalación no encontrada."}, status_code=404)
    return {"ok": True, "session": session.to_dict()}


@router.post("/api/platform/onboarding/{session_id}/publish")
async def publish_onboarded_agent(session_id: str, request: Request):
    """Ejecuta el Publish Gate y finaliza la instalación de Firby para el sitio web."""
    data = await request.json() if request.headers.get("content-type") == "application/json" else {}
    actor = data.get("actor", "admin")
    ok, msg, session = onboarding_engine.complete_and_publish(session_id, actor=actor)
    if not ok:
        return JSONResponse({"ok": False, "error": msg}, status_code=400)
    return {"ok": True, "message": msg, "session": session.to_dict() if session else None}

