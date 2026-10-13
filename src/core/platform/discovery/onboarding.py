# -*- coding: utf-8 -*-
"""
Firby Platform — First-Time Installation & Onboarding Engine
===========================================================
Implementa la experiencia de instalación autónoma de Firby como producto:
1. Conectar sitio web -> Crawling y descubrimiento controlado.
2. Detección de inconsistencias y conflictos.
3. Entrevista dinámica de administración (identifica qué falta).
4. Generación estructurada de AgentManifest.
5. Simulación y Publish Gate pre-publicación.
6. Publicación atómica y generación del snippet de instalación en 1 línea.
"""

from __future__ import annotations
import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional

from src.core.platform.models import Tenant, AgentInstance, AgentManifest, TenantStatus, AgentStatus
from src.core.platform.discovery.crawler import ControlledSiteCrawler, SiteModel
from src.core.platform.discovery.conflict_detector import ConflictDetector, KnowledgeConflict
from src.core.platform.manager import control_plane
from src.core.platform.store import platform_store


@dataclass
class OnboardingSession:
    session_id: str
    website_url: str
    business_name: str
    tenant_id: str
    agent_id: str
    public_id: str
    status: str = "DISCOVERING"  # DISCOVERING, CONFLICTS_DETECTED, INTERVIEW_PENDING, READY_TO_PUBLISH, PUBLISHED
    site_model: Optional[SiteModel] = None
    conflicts: List[KnowledgeConflict] = field(default_factory=list)
    pending_questions: List[str] = field(default_factory=list)
    admin_answers: Dict[str, str] = field(default_factory=dict)
    draft_manifest: Optional[AgentManifest] = None
    published_version: Optional[int] = None
    embed_snippet: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "website_url": self.website_url,
            "business_name": self.business_name,
            "tenant_id": self.tenant_id,
            "agent_id": self.agent_id,
            "public_id": self.public_id,
            "status": self.status,
            "site_pages_count": self.site_model.page_count if self.site_model else 0,
            "conflicts_count": len(self.conflicts),
            "pending_questions": self.pending_questions,
            "published_version": self.published_version,
            "embed_snippet": self.embed_snippet
        }


class OnboardingEngine:
    """Motor que orquesta el ciclo de vida de la primera instalación de Firby."""

    def __init__(self):
        self._sessions: Dict[str, OnboardingSession] = {}

    def start_installation(
        self,
        website_url: str,
        business_name: Optional[str] = None,
        fetcher_func=None
    ) -> OnboardingSession:
        """Inicia el proceso de descubrimiento e instalación para un nuevo sitio web."""
        session_id = f"inst_{uuid.uuid4().hex[:12]}"
        clean_url = website_url.strip()
        name = (business_name or "Nuevo Negocio").strip()

        # Generar IDs normalizados
        safe_slug = "".join(c if c.isalnum() else "_" for c in name.lower()).strip("_")[:16] or "biz"
        tenant_id = f"tenant_{safe_slug}_{session_id[:6]}"
        agent_id = f"agent_{safe_slug}_{session_id[:6]}"
        public_id = f"agt_{safe_slug}_{session_id[:6]}"

        session = OnboardingSession(
            session_id=session_id,
            website_url=clean_url,
            business_name=name,
            tenant_id=tenant_id,
            agent_id=agent_id,
            public_id=public_id,
            status="DISCOVERING"
        )
        self._sessions[session_id] = session

        # 1. Ejecutar descubrimiento controlado
        crawler = ControlledSiteCrawler(base_url=clean_url, depth_limit=2, page_budget=15)
        site_model = crawler.crawl_site(fetcher_func=fetcher_func)
        session.site_model = site_model

        if site_model.business_name and not business_name:
            session.business_name = site_model.business_name

        # 2. Detección de conflictos comerciales
        conflicts = ConflictDetector.detect_conflicts(site_model)
        session.conflicts = conflicts

        # 3. Formulación de preguntas de la entrevista inicial (lo que falta)
        questions = []
        if not site_model.prices:
            questions.append("¿Cuáles son los planes y precios oficiales de tus servicios?")
        if not site_model.contacts.get("phones"):
            questions.append("¿Cuál es el número de WhatsApp corporativo para notificaciones al dueño?")
        questions.append("¿Cuáles son tus políticas de cancelación y devolución?")
        session.pending_questions = questions

        if conflicts:
            session.status = "CONFLICTS_DETECTED"
        elif questions:
            session.status = "INTERVIEW_PENDING"
        else:
            session.status = "READY_TO_PUBLISH"

        return session

    def answer_interview_question(
        self,
        session_id: str,
        question: str,
        answer: str
    ) -> OnboardingSession:
        """Registra respuestas de la entrevista y remueve la pregunta pendiente."""
        session = self._sessions.get(session_id)
        if not session:
            raise ValueError("Sesión de instalación no encontrada")

        session.admin_answers[question] = answer
        if question in session.pending_questions:
            session.pending_questions.remove(question)

        if not session.pending_questions and not [c for c in session.conflicts if c.status != "RESOLVED"]:
            session.status = "READY_TO_PUBLISH"

        return session

    def answer_interview(self, session_id: str, answers: Dict[str, str]) -> Optional[OnboardingSession]:
        """Acepta un diccionario de respuestas para la entrevista."""
        session = self._sessions.get(session_id)
        if not session:
            return None
        for q, a in answers.items():
            session.admin_answers[q] = a
            matched = [pq for pq in session.pending_questions if pq.lower() in q.lower() or q.lower() in pq.lower()]
            for m in matched:
                if m in session.pending_questions:
                    session.pending_questions.remove(m)
        session.pending_questions.clear()
        session.status = "READY_TO_PUBLISH"
        return session

    start_onboarding = start_installation

    def generate_draft_manifest(self, session_id: str) -> AgentManifest:
        """Compila el manifiesto formal a partir del modelo del sitio y las respuestas."""
        session = self._sessions.get(session_id)
        if not session:
            raise ValueError("Sesión de instalación no encontrada")

        sm = session.site_model
        manifest = AgentManifest(
            agent_id=session.agent_id,
            tenant_id=session.tenant_id,
            version=1,
            published_by="onboarding",
            business_name=session.business_name,
            business_summary=sm.summary if sm else f"Operador oficial para {session.website_url}",
            website_url=session.website_url,
            enabled_capabilities=[
                "navigate_web",
                "web_navigation",
                "highlight_ui",
                "query_business_knowledge",
                "escalate_to_human"
            ],
            metadata={
                "target_audience": "Clientes y visitantes web",
                "official_voice": "Profesional, directo, empático y sin lenguaje artificial",
                "navigation_sections": [
                    {"id": "inicio", "target": "#hero", "label": "Inicio", "description": "Portada principal"}
                ],
                "commercial_terms": {
                    "plans": sm.prices if (sm and sm.prices) else {"estandar": "Consultar valoración"},
                    "free_trial_days": 7,
                    "cancellation_policy": session.admin_answers.get("¿Cuáles son tus políticas de cancelación y devolución?", "Cancela en 1 clic")
                }
            }
        )

        session.draft_manifest = manifest
        return manifest

    def complete_and_publish(self, session_id: str, actor: str = "admin") -> Tuple[bool, str, Optional[OnboardingSession]]:
        """
        Ejecuta el Publish Gate:
        Crea el Tenant, el AgentInstance, valida la configuración y publica la versión 1.
        """
        session = self._sessions.get(session_id)
        if not session:
            return False, "Sesión no encontrada", None

        # 1. Compilar manifiesto si aún no se generó
        if not session.draft_manifest:
            self.generate_draft_manifest(session_id)

        try:
            from src.core.operator.business_config import (
                BusinessConfig, BusinessIdentity, OfficialInfo, BusinessPolicy,
                ToolPermission, NavigationResource, ConnectedIntegrations
            )

            # 2. Registrar Tenant en Control Plane si no existe
            tenant = control_plane.get_tenant(session.tenant_id)
            if not tenant:
                tenant = control_plane.create_tenant(
                    tenant_id=session.tenant_id,
                    name=session.business_name,
                    metadata={"source": "onboarding"}
                )

            # 3. Registrar AgentInstance si no existe
            agent = control_plane.get_agent(session.tenant_id, session.agent_id)
            if not agent:
                agent = control_plane.create_agent(
                    tenant_id=session.tenant_id,
                    agent_id=session.agent_id,
                    name=f"Operador {session.business_name}",
                    public_id=session.public_id
                )

            # 4. Crear y almacenar BusinessConfig verificada
            domain_name = session.website_url.replace("https://", "").replace("http://", "").split("/")[0]
            identity = BusinessIdentity(
                name=session.business_name,
                legal_name=session.business_name,
                industry="Servicios",
                description=session.draft_manifest.business_summary if session.draft_manifest else f"Operador para {session.business_name}",
                website_url=session.website_url,
                tone_and_voice="profesional, directo y empático"
            )
            official_info = OfficialInfo(
                locations=[],
                contact_email=f"contacto@{domain_name}",
                executive_phone="",
                operating_hours="Lunes a Viernes 8:00 AM - 6:00 PM",
                team_overview=""
            )
            nav_res = [
                NavigationResource(id="inicio", target="#hero", label="Inicio", description="Portada principal")
            ]
            tools = {
                "web_navigation": ToolPermission(name="web_navigation", enabled=True),
                "highlight_ui": ToolPermission(name="highlight_ui", enabled=True),
                "query_business_knowledge": ToolPermission(name="query_business_knowledge", enabled=True),
                "escalate_to_human": ToolPermission(name="escalate_to_human", enabled=True),
                "check_availability": ToolPermission(name="check_availability", enabled=False),
                "book_appointment": ToolPermission(name="book_appointment", enabled=False),
                "capture_lead": ToolPermission(name="capture_lead", enabled=True)
            }
            config = BusinessConfig(
                tenant_id=session.tenant_id,
                identity=identity,
                official_info=official_info,
                navigation_resources=nav_res,
                tool_permissions=tools,
                connected_integrations=ConnectedIntegrations(whatsapp_owner=True, database_sync=True)
            )
            control_plane.save_agent_config(session.tenant_id, session.agent_id, config)

            # 5. Publicar versión 1 a través del publish gate
            manifest = control_plane.publish_agent(session.tenant_id, session.agent_id, published_by=actor)

            session.published_version = manifest.version
            session.status = "PUBLISHED"

            # 6. Generar snippet de instalación en 1 línea
            session.embed_snippet = (
                f'<script src="https://firbyai.com/firby.js"></script>\n'
                f'<script>\n'
                f'  Firby.init({{\n'
                f'    agent: "{session.public_id}"\n'
                f'  }});\n'
                f'</script>'
            )

            return True, "Instalación completada y agente publicado exitosamente", session

        except Exception as e:
            return False, f"Error en publish gate: {str(e)}", session


# Instancia única del motor de onboarding
onboarding_engine = OnboardingEngine()
