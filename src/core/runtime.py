# -*- coding: utf-8 -*-
"""Firby runtime execution layer."""
from __future__ import annotations

import asyncio
import os
import json
import random
import re
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple
import httpx
from src.firby.utils.helpers import _parse_admin_ids

import src.core.globals as globals_module
from src.core.globals import (
    AdminLearningEngine, AudioHandler, BrandAssetStore, FirbyAdmin, FirbyDemo,
    FirbyProduction, Config, ConversationEngine, GeneratorManager, MessageAnalysis,
    PersonaRegistry, ReasoningEngine, ResponseGenerator, SelfImprovementEngine,
    SessionManager, SimulationEngine, UrgencyLevel, WebSearchEngine, WhatsAppConnector,
    _AUDIO_HANDLER_AVAILABLE, _BRAND_ASSETS_AVAILABLE, _FIRBY_CORE_AVAILABLE,
    _GENERATOR_MANAGER_AVAILABLE, _KB_AVAILABLE, _NOVA_AVAILABLE, _SESSION_MANAGER_AVAILABLE,
    _buffer_key, _detect_wa_credentials, _is_greeting_only, _load_instance_metadata,
    _normalize_conv_text, _route_platform, analyzer, anti_robot_filter, auth_engine,
    db, ensure_minimum_business_state, extract_model_request_from_text,
    generate_activation_token, get_client, init_auth, init_calendar, init_database,
    init_llm, init_mcp, init_nova, init_task_manager, init_v8_systems, llm_engine,
    log, mcp_manager, notify_omni, now_col, owner_style_controller, setup_firby_agent,
    task_manager
)


from src.firby.admin.dashboard import AdminCommandsMixin
class FirbyUltra(AdminCommandsMixin):
    """Orquestador principal de Firby Ultra V7.0."""

    def __init__(self):
        self.db = db
        self.analyzer = analyzer
        self.search = WebSearchEngine()
        self.reasoning: ReasoningEngine = None
        self.generator: ResponseGenerator = None
        self.self_improvement = None
        self.admin_learning: AdminLearningEngine = None
        self.simulator: SimulationEngine = None
        # ── Atributos base (antes de managers que los usan) ──────────────────────
        self._demo_sessions: Dict[str, float] = {}
        self._emoji_chats_off: set = set()
        
        from src.core.message_sender import MessageSender
        self._sender = MessageSender(Config, db, self._demo_sessions, self._emoji_chats_off)

        # ── Demo: trucos progresivos y comandos del modo demo ─────────────────
        self._DEMO_TRICKS_ORDER = [
            ("/objecion",  "ver cómo manejo objeciones en vivo"),
            ("/cita",      "ver cómo agendo una cita completa"),
            ("/luxury",    "activar personalidad premium"),
            ("/empatica",  "cambiar a modo empático y de escucha"),
            ("/stats",     "ver el impacto en números reales"),
            ("/prueba",    "lanzarme el mensaje más difícil que tengas"),
            ("/cierre",    "ver cómo cierro una venta"),
            ("/directa",   "activar modo al grano sin rodeos"),
            ("/menu",      "ver modo bot con emojis y menú numerado"),
            ("/2am",       "verme responder a las 2 de la madrugada"),
        ]

        # Gestores de áreas separadas (v9)
        self.demo_mgr = FirbyDemo(self)
        self.admin_mgr = FirbyAdmin(self)
        self.production_mgr = FirbyProduction(self)
        self._conversation_engine = None

        # V7.0 — orquestador de agentes especializados
        self._orchestrator = None   # se inicializa en initialize() cuando llm_engine existe

        self._pending_buffers: Dict[str, Dict] = {}
        self._admin_pending: Dict[str, Dict] = {}
        self._last_reviewed_chat: Optional[str] = None
        self._availability_pending_patient: Optional[str] = None

        if _SESSION_MANAGER_AVAILABLE:
            self._session_mgr = SessionManager(self._demo_sessions, self._emoji_chats_off)
        if _AUDIO_HANDLER_AVAILABLE:
            self._audio_handler = AudioHandler()
        if _GENERATOR_MANAGER_AVAILABLE:
            self._generator_mgr = GeneratorManager(llm_engine, None)

    async def _mark_read_action(self, chat_id: str, route: Optional[Dict[str, Any]] = None):
        """
        Marca visto el mensaje en WhatsApp enviando chulos azules en el momento natural.
        """
        await self._sender._mark_read_action(chat_id, route)

    def _remember_route(self, chat_id: str, route: Optional[Dict[str, Any]] = None):
        self._sender._remember_route(chat_id, route)

    def _resolve_route(self, chat_id: str, route: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return self._sender._resolve_route(chat_id, route)

    def _brand_store(self, clinic: Dict[str, Any]) -> Optional["BrandAssetStore"]:
        if not _BRAND_ASSETS_AVAILABLE:
            return None
        clinic_name = clinic.get("name") or clinic.get("tagline") or Config.SECTOR or "firby"
        brand_key = clinic_name
        try:
            remembered_slug = (db.recall("instance_slug") or "").strip() if db else ""
            meta = _load_instance_metadata()
            meta_slug = str(meta.get("name") or "").strip() if isinstance(meta, dict) else ""
            brand_key = remembered_slug or meta_slug or clinic_name
        except Exception:
            brand_key = clinic_name
        try:
            return BrandAssetStore(Config.BRAND_ASSETS_BASE_DIR, brand_key)
        except Exception as e:
            log.warning(f"[brand] no pude abrir el vault: {e}")
            return None
    
    async def initialize(self):
        """Inicializa todos los componentes."""
        init_database()
        init_llm()
        init_auth()
        # admin_learning/simulator/reasoning/generator se instancian más abajo,
        # después de restaurar credenciales de WhatsApp y business_bootstrap
        # (antes se creaban también acá, se descartaban sin usar, y se volvían
        # a crear más abajo — duplicado innecesario).
        init_calendar()
        await init_mcp()
        try:
            await init_task_manager()
        except NameError:
            log.warning("[startup] init_task_manager no disponible — saltando")
        except Exception as _tm_err:
            log.warning(f"[startup] init_task_manager error: {_tm_err}")

        # Nova governance bridge
        if _NOVA_AVAILABLE and Config.NOVA_ENABLED:
            nova_guard = init_nova()
            # Verificar si Nova está activo
            client = get_client()
            if client:
                nova_alive = await client.health_check()
                if nova_alive:
                    log.info("[nova] conectado y activo")
                    # Auto-crear agente si no hay token configurado
                    if not Config.NOVA_TOKEN:
                        clinic = db.get_clinic()
                        token_id = await setup_firby_agent(
                            client, clinic.get("name", "Clinica"),
                            "Firby"
                        )
                        if token_id:
                            log.info(f"[nova] agente creado automáticamente: {token_id[:16]}...")
                else:
                    log.warning("[nova] server no disponible — modo degradado")

        # Restaurar credenciales WhatsApp desde DB (si fueron configuradas antes)
        try:
            clinic = db.get_clinic()
            wa_phone_id    = clinic.get("wa_phone_id", "")
            wa_access_token = clinic.get("wa_access_token", "")
            wa_verify_token = clinic.get("wa_verify_token", "")
            if wa_phone_id and wa_access_token:
                WhatsAppConnector.apply_to_config(
                    wa_phone_id, wa_access_token, wa_verify_token
                )
                log.info(f"[wa] credenciales restauradas desde DB: {wa_phone_id[:8]}...")
        except Exception as e:
            log.warning(f"[wa] no se pudieron restaurar credenciales: {e}")

        try:
            ensure_minimum_business_state()
        except Exception as exc:
            log.warning(f"[business_bootstrap] error: {exc}")

        # NOTA: antes estas 4 líneas se ejecutaban DOS VECES seguidas dentro
        # de este mismo initialize() — se creaban admin_learning/simulator/
        # reasoning/generator, se descartaban sin usar, y se volvían a crear
        # unas líneas más abajo. Se dejó solo la segunda tanda (que además
        # agrega self_improvement) para no instanciar objetos al pedo.
        self.admin_learning   = AdminLearningEngine(db)
        self.simulator        = SimulationEngine(self)
        self.reasoning        = ReasoningEngine(llm_engine)
        self.generator        = ResponseGenerator(llm_engine, learning_engine=self.admin_learning)
        self.self_improvement = None
        try:
            self.self_improvement = SelfImprovementEngine(llm_engine)
        except (NameError, AttributeError):
            log.warning("[startup] SelfImprovementEngine no disponible")

        if Config.FIRBY_CORE_ENABLED and _FIRBY_CORE_AVAILABLE:
            try:
                self._conversation_registry = PersonaRegistry(Config.FIRBY_CORE_PERSONAS_DIR)
                self._conversation_engine = ConversationEngine(self._conversation_registry)
                log.info("[firby_core] conversation core OK")
            except Exception as _mcore_err:
                self._conversation_registry = None
                self._conversation_engine = None
                log.warning(f"[firby_core] no se pudo activar el core nuevo: {_mcore_err}")
        else:
            self._conversation_registry = None
            self._conversation_engine = None
            log.info("[firby_core] desactivado o no disponible")

        # V8.0 — inicializar sistemas de humanidad real
        # CRÍTICO: envuelto en try/except para que un fallo en V8
        # NUNCA crashee el bot principal
        try:
            init_v8_systems()
            log.info("[v8] core OK")
        except Exception as _ev8:
            log.warning(f"[v8] init_v8_systems falló — V8 degradado: {_ev8}")
        try:
            init_v8_extended_systems()
            log.info("[v8] extended OK")
        except Exception as _ev8ext:
            log.warning(f"[v8] init_v8_extended falló: {_ev8ext}")
        # _patch_admin_dispatcher se llama SOLO en lifespan

        # V7.0 — activable por flag para rollout seguro
        v7_enabled = os.getenv("FIRBY_V7_ENABLED", "true").lower() in ("1", "true", "yes", "on")
        if v7_enabled:
            try:
                from v7.orchestrator import FirbyOrchestrator
                self._orchestrator = FirbyOrchestrator(llm_engine, db)
                log.info("[v7] orquestador activado por FIRBY_V7_ENABLED")
            except Exception as _v7_init:
                self._orchestrator = None
                log.warning(f"[v7] no se pudo activar el orquestador, fallback a generator: {_v7_init}")
        else:
            self._orchestrator = None
            log.info("[v7] orquestador desactivado — usando generator clásico")

        # Programar auto-mejora periódica
        task_manager.schedule_task(
            "self_improve",
            {},
            scheduled_for=datetime.now() + timedelta(hours=1)
        )

        log.info("═══ FIRBY V9.6.1 INICIALIZADA ═══")
        asyncio.create_task(self._schedule_daily_report())
    
    async def _schedule_daily_report(self):
        """Programa el reporte diario a las 8am."""
        while True:
            try:
                now = now_col()
                # Calcular segundos hasta las 8am del día siguiente
                next_8am = now.replace(hour=8, minute=0, second=0, microsecond=0)
                if now.hour >= 8:
                    next_8am = next_8am + timedelta(days=1)
                wait_seconds = (next_8am - now).total_seconds()
                await asyncio.sleep(wait_seconds)

                # Programar el reporte
                if task_manager:
                    task_manager.schedule_task(
                        task_type="report",
                        data={"type": "daily"},
                        scheduled_for=datetime.now(),
                        priority=5
                    )
                log.info("[daily_report] programado")
            except Exception as e:
                log.error(f"[daily_report] {e}")
                await asyncio.sleep(3600)

    async def _notify_hot_lead(self, clinic: Dict, message: str):
        """Notifica al admin cuando un lead tiene closing_score >= 75%."""
        try:
            admin_ids = _parse_admin_ids(clinic.get("admin_chat_ids", []))
            for admin_id in admin_ids[:2]:
                await self._send_message(admin_id, message)
        except Exception as e:
            log.warning(f"[hot_lead] {e}")

    def _build_conversation_core_clinic(self, clinic: Dict[str, Any], channel: str = "") -> Dict[str, Any]:
        core_clinic = dict(clinic or {})
        sector = _normalize_conv_text(str(core_clinic.get("sector") or Config.SECTOR or ""))
        channel_norm = _normalize_conv_text(channel or core_clinic.get("channel") or Config.PLATFORM or "")
        if sector == "estetica" and not core_clinic.get("persona_key"):
            core_clinic["persona_key"] = "estetica_whatsapp"
        if channel_norm:
            core_clinic["channel"] = channel_norm
        return core_clinic

    def _try_conversation_core(
        self,
        *,
        clinic: Dict[str, Any],
        user_msg: str,
        history: Optional[List[Dict[str, Any]]] = None,
        is_admin: bool = False,
        channel: str = "",
    ) -> Optional[List[str]]:
        if not Config.FIRBY_CORE_ENABLED or not self._conversation_engine:
            return None
        try:
            core_clinic = self._build_conversation_core_clinic(clinic, channel)
            result = self._conversation_engine.handle(
                clinic=core_clinic,
                user_msg=user_msg,
                history=history or [],
                is_admin=is_admin,
                channel=channel,
            )
            if result.handled and result.bubbles:
                return [bubble.strip() for bubble in result.bubbles if str(bubble).strip()]
        except Exception as exc:
            log.warning(f"[firby_core] fallo en handle(): {exc}")
        return None

    def _llm_runtime_available(self) -> bool:
        """Indica si Firby tiene un runtime LLM utilizable para priorizarlo sobre fallbacks."""
        try:
            if llm_engine:
                return True
        except Exception:
            pass
        try:
            generator = getattr(self, "generator", None)
            if generator and getattr(generator, "llm", None):
                return True
        except Exception:
            pass
        provider_keys = (
            getattr(Config, "GEMINI_API_KEY", ""),
            getattr(Config, "GEMINI_API_KEY_2", ""),
            getattr(Config, "GEMINI_API_KEY_3", ""),
            getattr(Config, "OPENROUTER_API_KEY", ""),
            getattr(Config, "GROQ_API_KEY", ""),
        )
        return any(bool(key) for key in provider_keys)

    def _handle_patient_meta_question(
        self,
        clinic: Dict,
        chat_id: str = "",
        user_msg: str = "",
        history: Optional[List[Dict[str, Any]]] = None,
    ) -> List[str]:
        clinic_name = clinic.get("name", "la clínica")
        services = clinic.get("services", [])
        channel = ""
        if chat_id:
            try:
                channel = str(self._resolve_route(chat_id).get("platform") or "")
            except Exception:
                channel = ""
        core_bubbles = self._try_conversation_core(
            clinic=clinic,
            user_msg=user_msg or "",
            history=history or [],
            is_admin=False,
            channel=channel,
        )
        if core_bubbles:
            return core_bubbles
        normalized_user = _normalize_conv_text(user_msg or "")
        prior_identity = any(
            any(marker in _normalize_conv_text(str(msg.get("content") or "")) for marker in (
                "recepcionista virtual",
                "asesora virtual",
                "soy firby",
                "trabaja por tu negocio",
                "trabajo por este canal",
            ))
            for msg in (history or [])
            if msg.get("role") == "assistant"
        )
        p_cfg = clinic.get("persona_config", {})
        if isinstance(p_cfg, str):
            try: p_cfg = json.loads(p_cfg)
            except Exception: p_cfg = {}
        agent_name = p_cfg.get("name") or "Firby"

        if prior_identity:
            if any(marker in normalized_user for marker in ("eres una ia", "eres ia", "eres una persona", "persona real", "eres un bot", "eres bot")):
                return [
                    f"Sigo siendo {agent_name}, la asesora comercial de {clinic_name}",
                    "Soy la asistente hecha para orientar, responder y ayudarte a avanzar sin que todo dependa de una persona pegada al chat",
                ]
            if any(marker in normalized_user for marker in ("quién eres", "quien eres", "qué eres", "que eres")):
                return [
                    f"Holaa! Hablas con {agent_name} de {clinic_name}, qué rico saludarte!",
                    "Te respondo en tiempo real 24/7 con toda la información sobre nuestros tratamientos, precios y citas",
                ]
        try:
            personality = self.generator._get_default_personality(clinic)
        except Exception:
            personality = None
        if personality:
            return self.generator._build_identity_probe_bubbles(clinic, personality, user_msg or "")
        if owner_style_controller:
            fallback = owner_style_controller.get_fallback_template(
                is_admin=False,
                chat_id=chat_id,
                clinic=clinic,
            )
            if fallback:
                return [part.strip() for part in fallback.split("|||") if part.strip()]
        services_text = ", ".join(services[:2]) if services else "citas e información"
        return [
            f"Holaa! Hablas con Firby de {clinic_name}, qué gusto saludarte!",
            f"Te puedo ayudar con información de {services_text}, precios y agendamiento",
        ]

    def _build_demo_patient_clinic(self, clinic: Dict[str, Any]) -> Dict[str, Any]:
        demo_clinic = dict(clinic or {})
        clinic_name = str(demo_clinic.get("name") or "").strip()
        sector = str(demo_clinic.get("sector") or "").strip().lower()
        env_sector = str(Config.SECTOR or Config.DEMO_SECTOR or "").strip().lower()
        configured_demo_name = str(Config.DEMO_BUSINESS_NAME or "").strip()
        normalized_demo_name = _normalize_conv_text(configured_demo_name)
        if normalized_demo_name in {"clinica demo", "clínica demo", "demo", "nova"}:
            configured_demo_name = ""

        # FIX: En modo demo para leads nuevos (sin negocio conocido), NO mostrar nombre de negocio
        # Solo usar DEMO_BUSINESS_NAME si es un negocio real configurado, no "demo" genérico
        if Config.DEMO_MODE and configured_demo_name and normalized_demo_name not in {"clinica demo", "clínica demo", "demo", "nova"}:
            demo_clinic["name"] = configured_demo_name
        elif clinic_name.lower() == "nova":
            demo_clinic["name"] = "la clínica"
        elif not clinic_name.strip():
            # En demo mode para leads nuevos, usar "tu clínica" en vez de nombre específico
            demo_clinic["name"] = "la clínica"

        if not sector or sector == "otro":
            demo_clinic["sector"] = env_sector or "estetica"

        if not demo_clinic.get("platform"):
            demo_clinic["platform"] = str(Config.PLATFORM or "").strip().lower()
        return demo_clinic

    def _demo_should_use_patient_chat_path(self, user_msg: str) -> bool:
        normalized = _normalize_conv_text(user_msg or "")
        if not normalized:
            return False

        token_set = set(re.findall(r"[a-z0-9áéíóúüñ]+", normalized))

        def _has_marker(marker: str) -> bool:
            marker_norm = _normalize_conv_text(marker or "")
            if not marker_norm:
                return False
            if " " in marker_norm:
                return marker_norm in normalized
            return marker_norm in token_set

        owner_exceptions = (
            "config", "demo", "prueba", "probar", "entrenar", "enseñar",
            "cómo funcionas", "como funcionas", "qué haces", "que haces",
            "quiero una demo", "quiero demo", "hagamos una demo", "simulacion",
            "simulación", "modo demo", "tengo un negocio", "tengo una empresa",
            "what is this", "what do you do", "who are you", "english only",
            "i don't talk spanish", "i dont talk spanish", "i don't understand", "i dont understand",
            "me mandaron", "me enviaron", "me pasaron", "me recomendaron",
            "no se que es", "no sé qué es", "que es esto", "qué es esto",
            "como funciona esto", "cómo funciona esto", "para que sirve", "para qué sirve",
            "me dijeron que", "alguien me dijo", "me lo recomendaron",
        )
        if any(_has_marker(exc) for exc in owner_exceptions):
            return False

        if any(_has_marker(marker) for marker in ("5 x 4", "5x4", "capital de francia", "capital de")):
            return False
        if any(
            _has_marker(marker)
            for marker in (
                "cuanto es",
                "cuánto es",
                "quien te hizo",
                "quién te hizo",
                "para que",
                "para qué",
                "aceptas audios",
                "aceptas pdf",
            )
        ):
            return False

        # Keywords de cliente/lead (mensaje de alguien preguntando como cliente)
        client_intent_markers = (
            # Servicios
            "botox", "relleno", "rellenos", "laser", "láser", "facial",
            "tratamiento", "tratamientos", "procedimiento", "procedimientos",
            "cita", "agenda", "agendar", "disponibilidad", "valoracion", "valoración",
            "consulta", "sesion", "sesión", "toxina", "hifu", "prp", "hidrafacial",
            # Precios
            "precio", "costo", "cuánto", "cuanto", "tarifa",
            # Ubicación/horario
            "horario", "hora", "abierta", "abierto", "cerrado", "ubicación", "dirección",
            # Agendamiento
            "reservar", "reserva", "mañana", "hoy", "viernes", "lunes", "sábado",
            "tarde", "noche", "pronto", "primavera", "urgencia", "emergencia",
            # generic lead
            "quiero", "necesito", "busco", "me interesa", "información",
            "saber", "acerca", "sobre", "qué tienen", "que tienen", "servicios",
        )
        if any(_has_marker(token) for token in client_intent_markers):
            return True

        if any(_has_marker(marker) for marker in ("cuanto es", "cuánto es", "cuanto cuestas", "cuánto cuestas", "cuanto vale", "cuánto vale", "que es", "qué es")):
            if not any(_has_marker(token) for token in client_intent_markers):
                return False

        owner_demo_markers = (
            "hola",
            "hola buenas",
            "buenas",
            "buenas tardes",
            "buenos dias",
            "buenos días",
            "buenas noches",
            "hey",
            "holi",
            "quien eres",
            "quién eres",
            "que eres",
            "qué eres",
            "que haces",
            "qué haces",
            "como funcionas",
            "cómo funcionas",
            "como trabajas",
            "cómo trabajas",
            "para que",
            "para qué",
            "por que",
            "por qué",
            "quien te hizo",
            "quién te hizo",
            "como te hicieron",
            "cómo te hicieron",
            "aceptas audios",
            # Prospect B2B markers (solo para pregunta de precio, NO para cambiar el flujo de demo)
            "cuanto cuestas",
            "cuánto cuestas",
            "cuanto cobras",
            "cuánto cobras",
            "cuanto vale",
            "cuánto vale",
            "me mandaron",
            "me pasaron",
            "aceptas audio",
            "aceptas pdf",
            "lees pdf",
            "lees archivos",
            "me mandaron tu numero",
            "me mandaron tu número",
            "me pasaron tu numero",
            "me pasaron tu número",
            "quiero probarte",
            "me gustaria probarte",
            "me gustaría probarte",
            "quiero una demo",
            "quiero demo",
            "tengo un negocio",
            "tengo una empresa",
            "me lo recomendaron",
            "me dijeron que te escribiera",
            "me dejaron probarte",
            "me pasaron este numero",
            "me pasaron este número",
            "para mi negocio",
            "para mi empresa",
            "what is this",
            "what do you do",
            "who are you",
            "english only",
            "i don't talk spanish",
            "i dont talk spanish",
            "i don't understand",
            "i dont understand",
        )
        if any(_has_marker(marker) for marker in owner_demo_markers):
            return False

        patient_like_markers = (
            "botox",
            "relleno",
            "rellenos",
            "laser",
            "láser",
            "cita",
            "agenda",
            "agendar",
            "disponibilidad",
            "precio",
            "cuanto",
            "cuánto",
            "valor",
            "tratamiento",
            "procedimiento",
            "consulta",
            "quiero informacion",
            "quiero información",
            "quiero una cita",
            "me quiero valorar",
            "valoracion",
            "valoración",
            "me interesa el botox",
            "me interesa botox",
            "me interesa el tratamiento",
            "me interesa el procedimiento",
            "quiero info sobre",
            "quiero saber del tratamiento",
            "quiero reservar",
            "quiero una reserva",
            "quiero apartar",
            "me duele",
            "me preocupa",
            "me mandaron por botox",
        )
        return any(_has_marker(marker) for marker in patient_like_markers)

    def _handle_patient_off_topic(self, clinic: Dict, chat_id: str = "", user_msg: str = "") -> List[str]:
        """Maneja mensajes fuera de tema con respuestas variadas según el tipo de off-topic."""
        if owner_style_controller:
            fallback = owner_style_controller.get_fallback_template(
                is_admin=False,
                chat_id=chat_id,
                clinic=clinic,
            )
            if fallback:
                return [part.strip() for part in fallback.split("|||") if part.strip()]

        services = clinic.get("services", [])
        focus = ", ".join(services[:2]) if services else "servicios, horarios o citas"
        normalized = (user_msg or "").lower()

        # Respuestas diferenciadas según el tipo de off-topic
        if any(t in normalized for t in ["película", "pelicula", "movie", "cine", "serie", "netflix"]):
            return [
                "eso ya se sale de lo que manejo por acá",
                f"si quieres, te ayudo con {focus} o agendamos una cita"
            ]

        if any(t in normalized for t in ["clima", "tiempo", "lluvia", "calor", "frío", "frio"]):
            return [
                "el clima no lo manejo desde este chat",
                f"pero si necesitas {focus} o información de citas, ahí sí te ayudo"
            ]

        if any(t in normalized for t in ["comida", "restaurante", "almuerzo", "cena", "desayuno"]):
            return [
                "eso de comida no lo manejo por aquí",
                f"te puedo ayudar con {focus} si quieres"
            ]

        if any(t in normalized for t in ["música", "musica", "canción", "cancion", "artista", "banda"]):
            return [
                "la música no es algo que maneje desde acá",
                f"pero para {focus} o citas, ahí sí te oriento"
            ]

        if any(t in normalized for t in ["bitcoin", "crypto", "cripto", "trading", "crypto"]):
            return [
                "eso de criptos no lo manejo por este canal",
                f"si quieres información de {focus}, ahí te ayudo"
            ]

        if any(t in normalized for t in ["fútbol", "futbol", "messi", "deporte", "partido"]):
            return [
                "el deporte no es algo que maneje desde aquí",
                f"pero si es por {focus} o citas, te ayudo con gusto"
            ]

        # Fallback genérico con variación
        variants = [
            ["eso se sale un poco de lo que manejo por acá", f"si quieres, te ayudo con {focus} o con una cita"],
            ["eso no lo manejo desde este chat", f"pero para {focus} o información de citas, ahí sí te ayudo"],
            ["eso ya es por fuera de lo que hago acá", f"si necesitas {focus}, te ayudo sin problema"],
        ]
        import hashlib
        idx = int(hashlib.md5(normalized.encode()).hexdigest()[:2], 16) % len(variants)
        return variants[idx]

    async def _download_telegram_binary(self, file_id: str) -> Tuple[bytes, str]:
        async with httpx.AsyncClient(timeout=20.0) as client:
            r = await client.get(
                f"https://api.telegram.org/bot{Config.TELEGRAM_TOKEN}/getFile",
                params={"file_id": file_id},
            )
            data = r.json()
            file_path = data.get("result", {}).get("file_path", "")
            if not file_path:
                raise RuntimeError("Telegram no devolvió file_path")
            dl = await client.get(
                f"https://api.telegram.org/file/bot{Config.TELEGRAM_TOKEN}/{file_path}"
            )
            dl.raise_for_status()
            return dl.content, Path(file_path).name or "telegram_asset.bin"

    async def _download_whatsapp_cloud_binary(self, media_id: str) -> Tuple[bytes, str, str]:
        async with httpx.AsyncClient(timeout=20.0) as client:
            meta = await client.get(
                f"https://graph.facebook.com/v20.0/{media_id}",
                headers={"Authorization": f"Bearer {Config.WA_ACCESS_TOKEN}"},
            )
            meta.raise_for_status()
            payload = meta.json() if meta.content else {}
            media_url = payload.get("url", "")
            if not media_url:
                raise RuntimeError("WhatsApp Cloud no devolvió URL del media")
            dl = await client.get(
                media_url,
                headers={"Authorization": f"Bearer {Config.WA_ACCESS_TOKEN}"},
            )
            dl.raise_for_status()
            filename = payload.get("id", media_id)
            mime_type = payload.get("mime_type", "application/octet-stream")
            return dl.content, filename, mime_type

    async def _process_patient_message(self, chat_id: str, text: str, clinic: dict, history: list, conv_state: dict, is_audio: bool = False, attachments: list = None) -> list:
        # Build dynamic search context via FTS5, Curated Memory Snapshot, and Skill Engine
        computed_search_context = ""
        try:
            if db:
                fts_matches = db.search_fts_messages(text, limit=4)
                if fts_matches:
                    snippets = [f"- [{m['role']}]: {m['content'][:120]}" for m in fts_matches]
                    computed_search_context += "[MEMORIA HISTÓRICA FTS5]:\n" + "\n".join(snippets) + "\n"
                if hasattr(db, "curated_memories") and db.curated_memories:
                    snapshot = db.curated_memories.get_snapshot()
                    if snapshot:
                        computed_search_context += "\n" + snapshot

            # Procedural Skill Engine matching
            from pathlib import Path
            try:
                from src.firby.brain.firby_skill_engine import FirbySkillEngine
            except ImportError:
                from firby_skill_engine import FirbySkillEngine

            instance_dir = getattr(self, "_instance_dir", "/home/ubuntu/firby")
            skill_engine = FirbySkillEngine(Path(instance_dir) / "skills")
            matched_skills = skill_engine.find_matching_skills(text)
            if matched_skills:
                computed_search_context += f"\n[SKILLS RELEVANTE ACTIVA: {', '.join(matched_skills)}]\n"
        except Exception as _ctx_err:
            log.warning(f"[FTS5/Skills] Error computing search_context: {_ctx_err}")

        if self._orchestrator is not None:
            try:
                bubbles = await self._orchestrator.process(
                    chat_id=chat_id,
                    text=text,
                    clinic=clinic,
                    patient=conv_state or {},
                    history=history,
                    search_context=computed_search_context,
                    kb_context='',
                    calendar_info='',
                )
                if bubbles is not None:
                    return bubbles
            except Exception as e:
                log.warning(f'[v7] orchestrator fallo, usando fallback: {e}')
        if self.production_mgr:
            return await self.production_mgr.handle(chat_id, text, clinic, history, conv_state, attachments=attachments)
        return []
    async def process_message(self, chat_id: str, text: str,
                             is_audio: bool = False,
                             attachments: Optional[List[Dict[str, Any]]] = None,
                             route: Optional[Dict[str, Any]] = None,
                             is_simulation: bool = False) -> List[str]:
        """Procesa un mensaje delegando a los gestores especializados."""
        start_time = time.time()
        attachments = attachments or []
        self._remember_route(chat_id, route)
        
        try:
            clinic = db.get_clinic()
            admin_ids = _parse_admin_ids(clinic.get("admin_chat_ids", []))
            chat_id_clean = chat_id.split("@")[0].replace("+", "").strip()
            admin_ids_clean = {aid.split("@")[0].replace("+", "").strip() for aid in admin_ids}

            is_admin = (
                chat_id in admin_ids or 
                chat_id_clean in admin_ids_clean or 
                db.get_admin(chat_id) is not None or
                db.get_admin(chat_id_clean) is not None or
                chat_id_clean in ["573124348669", "3124348669"]
            )

            # En modo simulación, tratamos al admin como un paciente real
            effective_is_admin = is_admin and not is_simulation


            # 1. Auth check (ignorar en simulación)
            if not is_simulation and auth_engine and auth_engine.is_auth_message(chat_id, text):
                result = await auth_engine.process(chat_id, text)
                if result: return result

            # 1.5. Slash commands (works in all modes)
            if text.strip().startswith("/"):
                try:
                    from src.firby.admin.commands import get_command_handler
                    _cmd_h = get_command_handler(getattr(self, "_instance_id", "default"))
                    _cmd_result = await _cmd_h.handle(chat_id, text.strip(), is_admin=False, clinic=clinic, db=db)
                    if _cmd_result:
                        return _cmd_result
                except Exception:
                    pass

            # ── Interceptación para OVNI ───────────────────────────────────────
            _pk = os.getenv("PERSONA_KEY", "").strip().lower()
            if _pk == "ovni":
                log.info(f"[Router] OVNI handler activado para {chat_id}")
                try:
                    from src.core.ovni_handler import OvniHandler
                    ovni_h = OvniHandler(self)
                    history = db.get_history(chat_id)
                    return await ovni_h.handle(
                        chat_id=chat_id,
                        text=text,
                        clinic=clinic,
                        admin_ids=admin_ids,
                        history=history,
                        is_audio=is_audio,
                        attachments=attachments
                    )
                except Exception as _oe:
                    log.error(f"[Router] error cargando OvniHandler: {_oe}", exc_info=True)

            # --- CLASIFICACIÓN Y RUTEO ---
            if Config.DEMO_MODE:
                log.info(f"[Router] Ruteando mensaje de {chat_id} a Modo Demo (DEMO_MODE=True)")
                return await self._handle_demo_message(chat_id, text, clinic, attachments)
            
            # Modo producción: localizar admin e identificar si es nueva instancia o ya configurada
            is_setup_done = bool(clinic.get("setup_done"))
            log.info(f"[Router] Modo Producción Activo. Instancia: {'Configurada' if is_setup_done else 'Nueva Instancia (Falta Setup)'}")
            
            if effective_is_admin:
                log.info(f"[Router] Admin detectado ({chat_id}). Ruteando a Panel Admin.")
                return await self._handle_admin_message(chat_id, text, clinic, is_audio=is_audio, attachments=attachments)
            
            if not is_setup_done:
                # 🔑 Verificar si el mensaje entrante es un Token de Activación válido (TOKN_xxx)
                raw_token = text.strip().upper()
                token_info = None
                if db:
                    try:
                        with db._conn() as _c:
                            _row = _c.execute("SELECT * FROM activation_tokens WHERE UPPER(token)=? AND is_active=1", (raw_token,)).fetchone()
                            if _row:
                                token_info = dict(_row)
                    except Exception as _te:
                        log.warning(f"[token_auth] Error checking token: {_te}")

                if token_info:
                    log.info(f"[Router] Token de activación VÁLIDO aceptado para {chat_id}: {raw_token}")
                    admin_ids = _parse_admin_ids(clinic.get("admin_chat_ids", []))
                    admin_ids = list(admin_ids) if isinstance(admin_ids, list) else []
                    clean_id = chat_id.split("@")[0].replace("+", "").strip()
                    if chat_id not in admin_ids:
                        admin_ids.append(chat_id)
                    if clean_id not in admin_ids:
                        admin_ids.append(clean_id)
                    db.update_clinic(admin_chat_ids=json.dumps(admin_ids))

                    try:
                        with db._conn() as _c:
                            _c.execute("UPDATE activation_tokens SET used_at=datetime('now'), used_by_chat_id=? WHERE UPPER(token)=?", (chat_id, raw_token))
                    except Exception:
                        pass

                    try:
                        db.save_admin(chat_id, role="owner")
                    except Exception:
                        pass

                    return await self._handle_setup(chat_id, text, clinic)

                # Si NO es un token y la instancia no ha sido activada, solicitar token de activación
                log.info(f"[Router] Remitente {chat_id} escribió a instancia sin activar. Solicitando token de activación.")
                return [
                    "Hola! Esta instancia de Firby aún no ha sido activada.",
                    "Por favor ingresa tu token de activación para comenzar a configurarla."
                ]

            # Ruteo normal para paciente en producción
            log.info(f"[Router] Remitente {chat_id} clasificado como Paciente. Ruteando a flujo de producción.")
            conv_state = db.get_conversation_state(chat_id)
            if conv_state and conv_state.escalation_needed and not effective_is_admin:
                # Si el paciente está pidiendo explícitamente hablar con un humano, no lo silenciamos
                # para que el production monitor le responda con el mensaje de transferencia y alerte al admin.
                human_signals = ["hablar con humano", "hablar con una persona", "hablar con alguien",
                                 "quiero hablar con", "pasame con", "pásame con", "un humano",
                                 "una persona real", "talk to a human", "real person", "hablar con un humano",
                                 "asesor humano", "atencion humana", "atención humana", "humano", "asesor",
                                 "atención", "atencion", "contacto", "hablar con alguien"]
                wants_human = any(s in text.lower() for s in human_signals)
                if not wants_human:
                    log.info(f"[mute] Bot is muted for chat_id={chat_id} (escalation_needed=True)")
                    return []
                
            history = db.get_history(chat_id)
            try:
                from pathlib import Path
                try:
                    from src.firby.brain.firby_session_lineage import SessionLineageEngine
                except ImportError:
                    from firby_session_lineage import SessionLineageEngine

                db_path = getattr(db, "db_path", "/home/ubuntu/firby/firby.db")
                lineage = SessionLineageEngine(Path(db_path))
                active_history, lineage_summary = lineage.build_lineage_context(chat_id, history, max_active_turns=12)
                history = active_history
            except Exception as _lin_err:
                log.warning(f"[SessionLineage] Error: {_lin_err}")

            return await self._process_patient_message(chat_id, text, clinic, history, conv_state, is_audio=is_audio, attachments=attachments)

        except Exception as e:
            log.error(f"Error processing message from {chat_id}: {e}", exc_info=True)
            db.record_metric("error", "message_processing", 1, {"error": str(e)})

            try:
                from src.firby.utils.helpers import handle_ai_failure
                await handle_ai_failure(
                    chat_id=chat_id,
                    last_message=text,
                    error=e,
                    send_fn=self._send_message
                )
            except Exception as e_fail:
                log.error(f"[handle_ai_failure] Failed executing error routine: {e_fail}")

            return []
    async def _handle_demo_message(self, chat_id: str, text: str,
                                    clinic: Dict,
                                    attachments: Optional[List[Dict[str, Any]]] = None) -> List[str]:
        from src.interfaces.web.demo_handler import handle_demo_message
        return await handle_demo_message(self, chat_id, text, clinic, attachments)

    async def _handle_admin_message(self, chat_id: str, text: str, clinic: Dict,
                                   is_audio: bool = False,
                                   attachments: Optional[List[Dict[str, Any]]] = None) -> List[str]:
        # 1. Ingest assets if there are attachments
        if attachments:
            assets_res = await self._admin_ingest_assets(chat_id, text, attachments, clinic)
            if assets_res:
                return assets_res

        # 1a. Natural Conversational Intent Engine (El dueño habla 100% natural)
        try:
            from src.firby.brain.admin_intent_engine import AdminIntentEngine
            intent_engine = AdminIntentEngine(db=db)
            intent_res = await intent_engine.interpret_and_execute(text, clinic, chat_id)
            if intent_res:
                return [intent_res]
        except Exception as _ie_err:
            log.warning(f"[admin_intent] Error evaluating intent: {_ie_err}")
        
        # 1b. Check proactive outbound command (e.g. "háblale a +573001234567 Hola...", "/escribir 3001234567 ...")
        try:
            from src.firby.admin.outreach import AdminOutreachEngine
            from src.firby.channels.outreach_router import OmnichannelOutreachRouter
            
            outreach_engine = AdminOutreachEngine(tenant_id=clinic.get("tenant_id", "default"))
            parsed = outreach_engine.parse_escribir_command(text)
            if parsed:
                router = OmnichannelOutreachRouter(tenant_id=clinic.get("tenant_id", "default"))
                res = await router.dispatch_admin_outreach(
                    raw_recipient=parsed["recipient"],
                    message=parsed["message"],
                    send_fn=self._send_message,
                    preferred_channel="whatsapp",
                    admin_id=chat_id,
                )
                if res.get("success"):
                    return [f"📲 Mensaje proactivo enviado a {parsed['recipient']}:\n\"{parsed['message']}\""]
                else:
                    return [f"⚠️ No se pudo enviar el mensaje a {parsed['recipient']}. Revisa la conexión de WhatsApp."]
        except Exception as _oe:
            log.warning(f"[outbound] Error parsing outbound command: {_oe}")

        # 1c. Admin Controls (Pausa, Activar, Citas, Métricas) — soporta comandos / y lenguaje natural
        try:
            text_lower = text.lower().strip()
            import re
            
            # Detect phone number in text if present
            phone_match = re.search(r"(\+?\d{8,15})", text_lower)
            target_phone = phone_match.group(1) if phone_match else ""

            # PAUSA / SILENCIAR
            is_pause = any(k in text_lower for k in ("/pausa", "/silenciar", "pausa a", "silencia a", "silenciar a", "no le respondas a", "voy a hablar yo con"))
            if is_pause and target_phone:
                if db:
                    clean_jid = target_phone.replace("+", "").strip()
                    if not clean_jid.endswith("@s.whatsapp.net") and not "@" in clean_jid:
                        clean_jid += "@s.whatsapp.net"
                    state = db.get_conversation_state(clean_jid)
                    if state:
                        state.escalation_needed = True
                        db.save_conversation_state(state)
                    else:
                        from src.firby.brain.database import ConversationState
                        db.save_conversation_state(ConversationState(chat_id=clean_jid, escalation_needed=True))
                    return [f"⏸️ Bot pausado para el cliente {target_phone}. Firby no le responderá hasta que lo reactives con '/activar {target_phone}' o diciéndome 'reactiva a {target_phone}'."]

            # REACTIVAR / RESUME
            is_resume = any(k in text_lower for k in ("/activar", "/resume", "/despausar", "activa a", "reactiva a", "vuelve a responder a", "despausa a"))
            if is_resume and target_phone:
                if db:
                    clean_jid = target_phone.replace("+", "").strip()
                    if not clean_jid.endswith("@s.whatsapp.net") and not "@" in clean_jid:
                        clean_jid += "@s.whatsapp.net"
                    state = db.get_conversation_state(clean_jid)
                    if state:
                        state.escalation_needed = False
                        db.save_conversation_state(state)
                    return [f"▶️ Bot reactivado para el cliente {target_phone}. Firby volverá a responderle de forma automática."]

            # LISTAR CITAS DE HOY
            is_citas = any(k in text_lower for k in ("/citas", "/agenda", "citas de hoy", "qué citas hay hoy", "cuántas citas", "ver citas"))
            if is_citas:
                if db:
                    import datetime
                    today_str = datetime.datetime.now().strftime("%Y-%m-%d")
                    with db._conn() as c:
                        rows = c.execute("SELECT patient_name, service, datetime_slot, status FROM appointments WHERE datetime_slot LIKE ? ORDER BY id DESC LIMIT 10", (f"%{today_str}%",)).fetchall()
                        if rows:
                            lines = [f"📅 *Citas registradas para hoy ({today_str})*:"]
                            for idx, r in enumerate(rows, 1):
                                lines.append(f"{idx}. {r['datetime_slot']} — {r['patient_name']} ({r['service']}) [{r['status']}]")
                            return ["\n".join(lines)]
                        else:
                            return [f"📅 No hay citas registradas en la base de datos para el día de hoy ({today_str})."]

            # CREAR AUTOMATIZACIÓN EN N8N
            is_auto = any(k in text_lower for k in ("/automatizar", "/auto", "crea una automatización", "crear automatizacion", "crea un flujo", "automatiza que"))
            if is_auto:
                try:
                    from src.firby.brain.automation_architect import AutomationArchitect
                    arch = AutomationArchitect()
                    clinic_name = clinic.get("name", "Clínica")
                    res = await arch.create_workflow_from_natural_language(text, clinic_name=clinic_name)
                    if res.get("ok"):
                        return [
                            f"⚡ *Automatización Creada y Activa en n8n*:\n\n"
                            f"• *Nombre*: {res['name']}\n"
                            f"• *ID*: `{res['workflow_id']}`\n"
                            f"• *Estado*: 🟢 En Vivo\n\n"
                            f"Cada vez que ocurra el evento, se ejecutarán las acciones automáticamente."
                        ]
                    else:
                        return [f"⚠️ No se pudo crear la automatización: {res.get('error', 'Error de conexión con n8n')}"]
                except Exception as _auto_err:
                    log.error(f"[admin_auto] Error: {_auto_err}")

            # LANZAR CAMPAÑA DE REACTIVACIÓN / GROWTH
            is_growth = any(k in text_lower for k in ("/reactivar", "/growth", "reactivar pacientes", "campaña de reactivacion", "campana de reactivacion", "llenar agenda"))
            if is_growth:
                try:
                    from src.firby.brain.growth_engine import GrowthCampaignEngine
                    growth = GrowthCampaignEngine(db=db)
                    clinic_name = clinic.get("name", "la clínica")
                    res = await growth.execute_reactivation_campaign(
                        service_name="consulta de control",
                        clinic_name=clinic_name,
                        days_inactive=60,
                        batch_size=10
                    )
                    return [
                        f"📢 *Campaña de Reactivación Iniciada*:\n\n"
                        f"• Pacientes Candidatos: {res.get('total_candidates', 0)}\n"
                        f"• Mensajes Despachados: {res.get('sent_count', 0)}\n"
                        f"• Modo de Seguridad: 🛡️ Pausas anti-baneo de 2 min entre contactos activadas."
                    ]
                except Exception as _gr_err:
                    log.error(f"[admin_growth] Error: {_gr_err}")

            # GESTIÓN DE EMPLEADOS DIGITALES / ROLES
            is_roles = any(k in text_lower for k in ("/roles", "/empleados", "ver empleados", "quiénes trabajan", "equipo digital"))
            if is_roles:
                try:
                    from src.firby.brain.employee_roles import EmployeeManager, EMPLOYEE_PROFILES
                    mgr = EmployeeManager(db=db)
                    active = mgr.get_active_roles()
                    lines = ["👥 *Equipo de Empleados Digitales de tu Negocio*:\n"]
                    for r in active:
                        p = EMPLOYEE_PROFILES.get(r, {})
                        lines.append(f"• *{p.get('default_name')}* ({p.get('title')}): {p.get('description')}")
                    lines.append("\nTodos los agentes operan de forma coordinada con la misma base de datos.")
                    return ["\n".join(lines)]
                except Exception as _rol_err:
                    log.error(f"[admin_roles] Error: {_rol_err}")

        except Exception as _admin_cmd_err:
            log.warning(f"[admin_cmd] Error processing admin command: {_admin_cmd_err}")

        # 2. Delegate to _handle_admin_or_setup
        return await self._handle_admin_or_setup(chat_id, text, clinic)



    async def _handle_admin_or_setup(self, chat_id: str, text: str,
                                     clinic: Dict) -> List[str]:
        """Maneja modo admin o setup. Nunca lanza excepcion al exterior."""
        from src.firby.utils.helpers import _parse_admin_ids
        try:
            # Setup inicial — SOLO si el chat_id ya fue autenticado como admin
            # Protege contra pacientes que lleguen antes de que el admin configure
            if not clinic.get("setup_done"):
                admin_ids = _parse_admin_ids(clinic.get("admin_chat_ids", []))

                # ¿Este chat_id fue autenticado via token de activacion?
                is_authenticated_admin = (
                    chat_id in admin_ids or
                    db.get_admin(chat_id) is not None
                )

                if is_authenticated_admin:
                    return await self._handle_setup(chat_id, text, clinic)
                else:
                    # 🔑 Verificar si el usuario ingresó un Token de Activación válido (TOKN_xxx)
                    raw_token = text.strip()
                    token_info = None
                    if db:
                        try:
                            with db._conn() as _c:
                                _row = _c.execute("SELECT * FROM activation_tokens WHERE token=? AND is_active=1", (raw_token,)).fetchone()
                                if _row:
                                    token_info = dict(_row)
                        except Exception:
                            pass

                    if token_info:
                        log.info(f"[Setup] Token de activación válido aceptado para {chat_id}: {raw_token}")
                        admin_ids = list(admin_ids) if isinstance(admin_ids, list) else []
                        if chat_id not in admin_ids:
                            admin_ids.append(chat_id)
                            db.update_clinic(admin_chat_ids=json.dumps(admin_ids))
                        
                        try:
                            with db._conn() as _c:
                                _c.execute("UPDATE activation_tokens SET used_at=datetime('now'), used_by_chat_id=? WHERE token=?", (chat_id, raw_token))
                        except Exception:
                            pass

                        try:
                            db.save_admin(chat_id, role="owner")
                        except Exception:
                            pass

                        return await self._handle_setup(chat_id, text, clinic)

                    # Verificar si el texto ingresado es el MASTER_API_KEY
                    import os as _os
                    master_key = _os.environ.get("MASTER_API_KEY", "")
                    if master_key and text.strip() == master_key:
                        log.info(f"[Setup] MASTER_API_KEY válido para {chat_id} — activando instancia")
                        admin_ids = list(admin_ids) if isinstance(admin_ids, list) else []
                        if chat_id not in admin_ids:
                            admin_ids.append(chat_id)
                            db.update_clinic(admin_chat_ids=json.dumps(admin_ids))
                        return await self._handle_setup(chat_id, text, clinic)
                    
                    # Paciente / Cliente — auto-activar instancia y atender amablemente
                    log.info(f"[Setup] Atendiendo a cliente/paciente {chat_id} — auto-activando canal de atención.")
                    db.update_clinic(setup_done=1, setup_step="idle")
                    clinic = db.get_clinic()
                    history = db.get_history(chat_id)
                    conv_state = db.get_conversation_state(chat_id)
                    return await self._process_patient_message(chat_id, text, clinic, history, conv_state, is_audio=is_audio, attachments=attachments)

            # Comandos slash
            cmd = text.lower().strip()

            natural_model_arg = extract_model_request_from_text(cmd)
            if natural_model_arg:
                return await self._admin_set_model(natural_model_arg, clinic)

            if cmd == "/citas":
                return await self._admin_show_appointments()
            elif cmd == "/config":
                return await self._admin_show_config(clinic)
            elif cmd == "/metricas":
                return await self._admin_show_metrics()
            elif cmd == "/setup":
                return await self._restart_setup(chat_id)
            elif cmd == "/plugins":
                return await self._admin_show_plugins()
            elif cmd == "/personalidad":
                return await self._admin_show_personality(clinic)
            elif cmd == "/control":
                return await _admin_control_status(chat_id)
            elif cmd.startswith("/control "):
                return await _admin_control_apply(chat_id, text)
            elif cmd == "/addadmin":
                if auth_engine:
                    return await auth_engine.create_invite(chat_id)
                return ["Sistema de invitaciones no disponible."]
            elif cmd == "/admins":
                return await self._admin_show_admins()
            elif cmd == "/login":
                db.set_auth_session(chat_id, flow="login", step="email", temp_data={})
                return ["Tu correo electronico de admin?"]
            elif cmd == "/logout":
                if auth_engine:
                    return auth_engine._logout(chat_id)
                return ["Sesion cerrada."]
            elif cmd == "/kb":
                return await self._admin_kb_status()
            elif cmd == "/simular":
                if self.simulator:
                    return self.simulator.start(chat_id)
                return ["El motor de simulación no está disponible."]
            elif cmd == "/kb borrar":
                return await self._admin_kb_clear()
            elif cmd == "/brand":
                return await self._admin_brand_status(clinic)
            # Handler de confirmación de mensajes pendientes
            text_lower = text.lower().strip()
            if text_lower in ("confirmar", "confirmar sí", "confirmar si", "si", "sí", "ok", "si, confirmar"):
                return await self._handle_admin_confirm(chat_id, text)
            elif text_lower in ("cancelar", "no", "cancela"):
                return await self._handle_admin_cancel(chat_id, text)
            
            elif cmd == "/sector":
                return await self._admin_show_sector()
            elif cmd.startswith("/sector "):
                new_sector = cmd.split("/sector ", 1)[1].strip().lower()
                return await self._admin_set_sector(new_sector)

            # ── Calendario ────────────────────────────────────────────────
            elif cmd == "/agenda":
                return await self._admin_agenda_status()
            elif cmd.startswith("/calendly "):
                link = cmd.split("/calendly ", 1)[1].strip()
                if link.startswith("http"):
                    # Guardar en Config y en DB
                    Config.CALENDLY_LINK = link
                    if calendar_bridge:
                        calendar_bridge._calendly_link = link
                    db.update_clinic(calendly_link=link)
                    return [
                        f"Calendly guardado.",
                        f"Cuando un paciente pregunte por horarios, le comparto ese link directamente."
                    ]
                return ["Formato: /calendly https://calendly.com/tu-link"]

            # ── WhatsApp ──────────────────────────────────────────────────
            elif cmd == "/whatsapp":
                return await self._admin_whatsapp_guide(clinic)

            # ── Telegram V10 ──────────────────────────────────────────────
            elif cmd == "/telegram":
                buf = clinic.get("setup_buffer", {})
                if isinstance(buf, str):
                    try: buf = json.loads(buf) if buf else {}
                    except Exception: buf = {}
                buf["omni_flow"] = "telegram_waiting_token"
                db.update_clinic(setup_buffer=json.dumps(buf, ensure_ascii=False))
                return [
                    "🤖 *Conexión de Telegram*",
                    "1. Ve a @BotFather en Telegram y crea un bot con `/newbot` (o selecciona uno existente).",
                    "2. Copia el *HTTP API Token* que te proporciona @BotFather.",
                    "3. Pégalo directamente en este chat en cualquier momento.",
                    "Escribe 'cancelar' si deseas interrumpir este proceso."
                ]

            # ── Slack V10 ─────────────────────────────────────────────────
            elif cmd == "/slack":
                buf = clinic.get("setup_buffer", {})
                if isinstance(buf, str):
                    try: buf = json.loads(buf) if buf else {}
                    except Exception: buf = {}
                buf["omni_flow"] = "slack_waiting_token"
                db.update_clinic(setup_buffer=json.dumps(buf, ensure_ascii=False))
                return [
                    "💬 *Conexión de Slack*",
                    "1. Crea una App en `api.slack.com/apps` desde cero o desde un manifiesto.",
                    "2. Ve a *OAuth & Permissions*, agrega el scope `chat:write` a los Bot Token Scopes.",
                    "3. Instala la app en tu Workspace para generar el *Bot User OAuth Token* (empieza con `xoxb-`).",
                    "4. Copia ese token y pégalo directamente en este chat.",
                    "Escribe 'cancelar' si deseas interrumpir este proceso."
                ]

            # ── WhatsApp Cloud API secundario ─────────────────────────────
            elif cmd == "/whatsapp2":
                buf = clinic.get("setup_buffer", {})
                if isinstance(buf, str):
                    try: buf = json.loads(buf) if buf else {}
                    except Exception: buf = {}
                buf["omni_flow"] = "wa2_waiting_phone_id"
                db.update_clinic(setup_buffer=json.dumps(buf, ensure_ascii=False))
                return [
                    "📱 *Conectar un segundo número de WhatsApp Cloud API*",
                    "Necesito dos datos de tu App de Meta for Developers:",
                    "1️⃣ *Phone Number ID* — lo encuentras en: Meta for Developers → Tu App → WhatsApp → API Setup → 'Phone number ID'.",
                    "Empieza por ahí: pégame el *Phone Number ID* (es un número de 15+ dígitos).",
                    "Escribe 'cancelar' si deseas interrumpir este proceso."
                ]

            # ── Gmail Connection ──────────────────────────────────────────
            elif cmd == "/gmail":
                buf = clinic.get("setup_buffer", {})
                if isinstance(buf, str):
                    try: buf = json.loads(buf) if buf else {}
                    except Exception: buf = {}
                buf["omni_flow"] = "gmail_waiting_credentials"
                db.update_clinic(setup_buffer=json.dumps(buf, ensure_ascii=False))
                return [
                    "📧 *Conexión de Gmail*",
                    "Puedo conectarme a tu cuenta de Gmail para gestionar notificaciones y correos.",
                    "Para iniciar la vinculación, necesito que me envíes tu *Google API Key* o *Client Secret*.",
                    "Por favor, pega el token o credencial directamente en este chat (o escribe 'cancelar' para salir)."
                ]



            # ── Nova governance ───────────────────────────────────────────
            elif cmd == "/nova":
                return await self._admin_nova_status()
            elif cmd == "/nova ledger":
                return await self._admin_nova_ledger()
            elif cmd.startswith("/nova regla "):
                rule_text = cmd.split("/nova regla ", 1)[1].strip()
                return await self._admin_nova_add_rule(rule_text, clinic)

            # ── V6.0 — Nuevos comandos ────────────────────────────────────
            elif cmd == "/pipeline":
                return await self._admin_pipeline()
            elif cmd == "/perdidos":
                return await self._admin_lost_analysis()
            elif cmd == "/coach":
                return await self._admin_sales_coach()
            elif cmd == "/estilo":
                return await self._admin_clone_style(chat_id)
            elif cmd == "/reactivar":
                return await self._admin_reactivate_dormant()
            elif cmd == "/seguimiento":
                return await self._admin_configure_followup(clinic)
            elif cmd == "/preconsulta":
                return await self._admin_preconsult_config(clinic)
            elif cmd.startswith("/broadcast "):
                msg_text = cmd.split("/broadcast ", 1)[1].strip()
                return await self._admin_broadcast(msg_text)
            elif cmd == "/instagram":
                return await self._admin_instagram_guide()
            elif cmd == "/pagos":
                return await self._admin_payments_guide()
            elif cmd == "/reporte":
                return await self._admin_trigger_report()

            # ── V8.0 — Modelo en caliente ─────────────────────────────────
            elif cmd == "/modelo":
                return await self._admin_show_model(clinic)
            elif cmd.startswith("/modelo "):
                arg = cmd.split("/modelo ", 1)[1].strip()
                return await self._admin_set_model(arg, clinic)
            elif cmd == "/v8":
                return await self._admin_v8_status()
            elif cmd == "/v8 reset":
                # Desbloquear todos los providers manualmente
                if llm_engine:
                    for p in llm_engine.providers:
                        llm_engine._failures[p.name] = 0
                        llm_engine._blocked_until[p.name] = 0
                    return ["todos los providers LLM desbloqueados", "usa /v8 para ver el estado"]
                return ["LLMEngine no disponible"]
            elif cmd == "/filtro":
                return await self._admin_show_filter_status()
            elif cmd.startswith("/filtro "):
                level_str = cmd.split("/filtro ", 1)[1].strip()
                return await self._admin_set_filter_level(level_str)

            # ── Conversaciones y feedback ──────────────────────────────────
            elif cmd == "/chats":
                return await self._admin_show_chats()
            elif cmd.startswith("/chat "):
                # /chat 1234567890  → ver conversación de ese chat_id
                patient_id = cmd.split("/chat ", 1)[1].strip()
                return await self._admin_show_patient_chat(patient_id)
            elif cmd == "/reglas":
                return await self._admin_show_trust_rules()
            elif cmd.startswith("/borrar regla "):
                rule_id_str = cmd.split("/borrar regla ", 1)[1].strip()
                if rule_id_str.isdigit():
                    db.delete_trust_rule(int(rule_id_str))
                    return ["Regla eliminada."]
                return ["Formato: /borrar regla [número]"]

            # ── Activacion y tokens ───────────────────────────────────────
            elif cmd == "/token" or cmd.startswith("/token "):
                label = cmd.split("/token", 1)[1].strip() if " " in cmd else ""
                if not label:
                    label = clinic.get("name") or "Mi Negocio"
                new_token = generate_activation_token(label)
                expires_at = (datetime.now() + timedelta(hours=Config.TOKEN_EXPIRY_HOURS)).isoformat()
                saved = db.create_activation_token(new_token, label, expires_at)
                if saved:
                    return [
                        f"Token generado para: {label}",
                        f"{new_token}",
                        f"Expira en {Config.TOKEN_EXPIRY_HOURS}h. Enviaselo al administrador."
                    ]
                return ["No pude generar el token. Intenta de nuevo."]

            elif cmd == "/activar":
                clinic_name = clinic.get("name") or ""
                if not clinic_name:
                    db.update_clinic(setup_step="idle")
                    return ["Para activar primero dime el nombre de tu negocio."]
                db.update_clinic(setup_done=1)
                admin_ids = _parse_admin_ids(clinic.get("admin_chat_ids", []))
                if chat_id not in admin_ids:
                    admin_ids.append(chat_id)
                    db.update_clinic(admin_chat_ids=json.dumps(admin_ids))
                return [
                    f"Instancia activada.",
                    f"Negocio: {clinic_name}",
                    "Ya puedo atender pacientes. Escribe /config para ver la configuracion."
                ]

            elif cmd == "/bridge":
                # Estado del WhatsApp bridge
                if not Config.WHATSAPP_BRIDGE_URL:
                    return ["WHATSAPP_BRIDGE_URL no configurada."]
                try:
                    async with httpx.AsyncClient(timeout=5.0) as hx:
                        r = await hx.get(f"{Config.WHATSAPP_BRIDGE_URL}/status")
                        data = r.json()
                    status = data.get("status", "?")
                    phone = data.get("phoneNumber", "no vinculado")
                    return [
                        f"Bridge WhatsApp: {status}",
                        f"Numero: {phone}",
                        f"Puerto: {Config.WHATSAPP_BRIDGE_URL}"
                    ]
                except Exception as e:
                    return [f"Bridge no responde: {e}"]

            elif cmd.startswith("/"):
                return [
                    "Comandos disponibles:\n\n"
                    "Atención:\n"
                    "/citas — citas pendientes\n"
                    "/chats — conversaciones de pacientes\n"
                    "/chat [id] — conversación completa\n"
                    "/reglas — reglas aprendidas\n"
                    "/broadcast [msg] — mensaje masivo\n\n"
                    "Configuración:\n"
                    "/config — configuración completa\n"
                    "/sector — ver/cambiar sector\n"
                    "/brand — vault de marca y documentos\n"
                    "/personalidad — ajustar personalidad\n"
                    "/control — control duro de frases, saludo y trato\n"
                    "/gateway — gateway automático de skills/reglas\n"
                    "/whatsapp — guía para configurar WhatsApp principal\n"
                    "/whatsapp2 — conectar un segundo número de WhatsApp Cloud API\n"
                    "/telegram — conectar un bot de Telegram\n"
                    "/slack — conectar un espacio de Slack\n"
                    "/gmail — conectar tu cuenta de Gmail\n"
                    "/bridge — estado del bridge WhatsApp\n"
                    "/agenda — calendario\n"
                    "/nova — gobernanza\n"
                    "/metricas — métricas\n\n"
                    "V8.0 — Modelo & Calidad:\n"
                    "/modelo — ver modelo activo y cambiarlo\n"
                    "/modelo [alias] — cambiar modelo (ej: claude-sonnet, gemini-flash)\n"
                    "/modelo reset — volver al modelo del .env\n"
                    "/v8 — estado de los sistemas V8\n"
                    "/filtro [1|2|3] — nivel del filtro anti-robot\n\n"
                    "Activación:\n"
                    "/activar — activar esta instancia\n"
                    "/token [nombre] — generar código de activación\n\n"
                    "Inteligencia:\n"
                    "/pipeline — leads por temperatura\n"
                    "/perdidos — análisis de abandono\n"
                    "/coach — feedback de ventas\n"
                    "/reactivar — reactivar inactivos\n"
                    "/reporte — reporte inmediato\n\n"
                    "O escribe en lenguaje natural."
                ]

            # ── Feedback sobre conversación revisada ──────────────────────
            feedback_result = await self._process_admin_feedback(chat_id, text, clinic)
            if feedback_result is not None:
                return feedback_result

            # ── Flujo activo de configuración Omnicanal V10 ────────────────
            try:
                from src.firby.channels.onboarding import handle_omnichannel_setup_flow
                omni_result = await handle_omnichannel_setup_flow(self, chat_id, text, clinic)
                if omni_result is not None:
                    return omni_result
            except Exception as _oee:
                log.error(f"[Router] Error in omnichannel setup flow: {_oee}", exc_info=True)

            # ── Flujo activo de configuración WhatsApp ─────────────────────
            wa_result = await self._handle_whatsapp_setup_flow(chat_id, text, clinic)
            if wa_result is not None:
                return wa_result

            # Lenguaje natural
            return await self._admin_natural_command(chat_id, text, clinic)

        except Exception as e:
            log.error(f"Admin handler error: {e}", exc_info=True)
            return ["algo salió mal, intenta de nuevo"]
    
    async def _handle_setup(self, chat_id: str, text: str, clinic: Dict) -> List[str]:
        """
        Setup inteligente con autodiscovery.
        Cuando el admin escribe el nombre, buscamos la clinica en Google
        y pre-llenamos todo. Si se encuentra, solo confirman. Si no, 5 pasos rapidos.
        """
        import re
        import json
        import os

        _db = getattr(self, "db", None) or db
        setup_step   = clinic.get("setup_step", "idle")
        setup_buffer = clinic.get("setup_buffer", {})
        if isinstance(setup_buffer, str):
            setup_buffer = json.loads(setup_buffer) if setup_buffer else {}

        step_names = ["name", "tagline", "services", "schedule", "phone", "pricing"]

        # 🟢 Detección de Saludos / Reanudación Proactiva
        text_clean_g = text.lower().strip().replace("¿", "").replace("?", "").replace("¡", "").replace("!", "").strip()
        is_greeting_only = text_clean_g in [
            "hola", "holaa", "holaaa", "buenas", "buenos dias", "buenos días",
            "buenas tardes", "buenas noches", "que mas", "qué más", "quiubo",
            "hey", "alo", "aló"
        ]
        owner_name = (
            setup_buffer.get("owner_name") or
            (_db.get_admin(chat_id).get("name", "").split()[0].title() if (_db and _db.get_admin(chat_id)) else "Santiago")
        )
        if isinstance(owner_name, str) and owner_name:
            owner_name = owner_name.split()[0].title()

        if is_greeting_only and setup_step != "idle":
            if setup_step == "confirm_discovered":
                discovered = setup_buffer.get("discovered", {})
                clinic_name = (discovered.get("name") or setup_buffer.get("name") or "tu empresa").strip()
                return [
                    f"Hola {owner_name}! Qué bueno saludarte de nuevo. Te parece si continuamos desde donde lo dejamos?",
                    f"Te había mostrado los datos encontrados de *{clinic_name}* para confirmar si todo está correcto o si deseas cambiar algo."
                ]
            elif setup_step == "persona_name":
                clinic_name = clinic.get("name") or setup_buffer.get("name") or "tu empresa"
                return [
                    f"Hola {owner_name}! Qué bueno verte de nuevo. Te parece si continuamos donde íbamos?",
                    "Estábamos eligiendo el nombre para tu recepcionista en WhatsApp. Cómo te gustaría que me llame? (Puedes dejarme como Firby, o asignarme el nombre que prefieras)."
                ]
            elif setup_step == "training_materials":
                p_name = clinic.get("assistant_name") or setup_buffer.get("persona_name") or "Firby"
                c_name = clinic.get("name") or "tu empresa"
                return [
                    f"Hola {owner_name}! Qué gusto saludarte. Continuamos con el entrenamiento de *{p_name}* para *{c_name}*?",
                    "Puedes enviarme por aquí listas de precios, folletos o casos especiales, o escribir 'activar' cuando quieras abrir la atención al público."
                ]
            elif setup_step == "name":
                return [
                    f"Hola {owner_name}! Qué gusto saludarte de nuevo. Te parece si continuamos con la configuración?",
                    "Cuéntame: cómo se llama tu empresa o clínica?"
                ]

        # ── Inicio ─────────────────────────────────────────────────────────────
        if setup_step == "idle":
            owner_name = ""
            try:
                rec = _db.get_admin(chat_id) if _db else None
                if rec and rec.get("name") and rec["name"] not in ("", "Admin"):
                    owner_name = rec["name"].split()[0].title()
            except Exception:
                pass
            setup_buf = {"owner_name": owner_name} if owner_name else {}
            if _db:
                _db.update_clinic(setup_step="name", setup_buffer=json.dumps(setup_buf) if setup_buf else "{}")
            if owner_name:
                return [
                    f"Hola {owner_name}! Qué gusto saludarte, mi nombre es Firby.",
                    "Oficialmente soy tu nueva socia de Inteligencia Artificial para el negocio.",
                    "Para comenzar a configurarme, cuéntame: cómo se llama tu empresa o clínica?"
                ]
            else:
                return [
                    "Hola! Qué gusto saludarte, mi nombre es Firby.",
                    "Oficialmente soy tu nueva socia de Inteligencia Artificial para el negocio... pero antes de ponernos la bata y atender pacientes, vamos a configurarme!",
                    "Primero cuéntame: cómo te llamas y cómo se llama tu clínica o empresa?"
                ]

        # ── Confirmar datos descubiertos en web (Universal LLM Brain) ───────────
        if setup_step == "confirm_discovered":
            discovered = setup_buffer.get("discovered", {})
            clinic_name = (discovered.get("name") or setup_buffer.get("name") or "tu empresa").strip()
            web_url = discovered.get("website_url") or discovered.get("url") or ""
            owner_name = (setup_buffer.get("owner_name") or "Santiago").split()[0].title()
            svcs_current = list(discovered.get("services", []))

            # 🟢 Clasificador y Razonador Universal LLM
            prompt_reasoning = f"""Eres el cerebro conversacional de Firby en la configuración inicial de WhatsApp con tu dueño ({owner_name}).
Le mostraste los datos públicos encontrados en Google de su negocio ({clinic_name}):
- Servicios: {", ".join(svcs_current) if svcs_current else 'Servicios médicos/especializados'}
- Horario: {discovered.get("schedule_text", "No especificado")}
- Teléfono: {discovered.get("phone", "No especificado")}
- Dirección: {discovered.get("address", "No especificada")}
- Web: {web_url or 'No disponible'}

EL DUEÑO RESPONDIÓ: "{text}"

INSTRUCCIONES DE CLASIFICACIÓN:
Determina la intención del dueño en una de estas categorías:
1. "CONFIRM":
   - El dueño aprueba la información (incluso con modismos latinos/paisas como: sí, dale, perfecto, de una, hágale, todo melo, firme, listo, ok, correcto, etc.).
   - O confirma y añade/corrige datos (ej: "sí pero agrega diseño de sonrisa", "cambia el teléfono", "el horario es 24h").
   - O el dueño va un paso adelante y asigna directamente el nombre del bot (ej: "ponle Mateo", "llámate Sofía", "deja Firby").

2. "REJECT":
   - Dice que esa NO es su empresa/clínica o que los datos están completamente equivocados.

3. "QUESTION":
   - Hace una pregunta o duda ("cómo supiste?", "de dónde salió eso?", "puedo cambiarlo luego?", etc.).

4. "OTHER":
   - Saludo o comentario no relacionado.

RESPONDE ÚNICAMENTE UN JSON CON ESTA ESTRUCTURA EXACTA:
{{
  "intent": "CONFIRM" | "REJECT" | "QUESTION" | "OTHER",
  "data_updates": {{
    "added_services": ["servicios nuevos si mencionó"],
    "removed_services": ["servicios a quitar si mencionó"],
    "schedule_text": "nuevo horario o vacio",
    "phone": "nuevo telefono o vacio",
    "address": "nueva direccion o vacio",
    "assigned_persona": "nombre de recepcionista si lo ordenó directamente, o vacio"
  }},
  "response_bubbles": [
    "Burbuja 1 cálida, profesional y humana.",
    "Burbuja 2 con la siguiente pregunta o indicación clara."
  ]
}}

REGLAS PARA LAS BURBUJAS DE RESPUESTA:
- CERO signos '¿' ni '¡'. Español latinoamericano natural, cálido y profesional.
- Si intent == "CONFIRM":
    - Si asignó nombre directo, agradece, confirma los datos y el nombre asignado, y pasa a invitarlo a entrenar o decir 'activar'.
    - Si NO asignó nombre, agradece, confirma que guardaste la información (mencionando cambios si los hubo), y pregúntale: "qué nombre te gustaría que use yo como tu recepcionista en WhatsApp? (Puedes dejarme como Firby, o asignarme el nombre que prefieras)".
- Si intent == "REJECT":
    - Discúlpate con amabilidad y pídele que te escriba el nombre exacto de su empresa para investigarla de nuevo.
- Si intent == "QUESTION":
    - Responde su pregunta con calidez y transparencia (ej: explicando que investigaste en Google para ahorrarle tiempo) y pídele que te indique si los datos están bien para continuar.
- Si intent == "OTHER":
    - Responde cordialmente y guíalo a confirmar los datos.
SOLO JSON."""

            try:
                from src.core.globals import llm_engine
                _llm = getattr(getattr(self, "generator", None), "llm", None) or llm_engine
                if _llm:
                    res_r, _ = await _llm.complete(
                        [{"role": "user", "content": prompt_reasoning}],
                        model_tier="fast",
                        temperature=0.2,
                        max_tokens=450,
                        use_cache=False
                    )
                    clean_r = res_r.strip().replace("```json", "").replace("```", "").strip()
                    data_r = json.loads(clean_r)
                    intent = data_r.get("intent", "CONFIRM")
                    updates = data_r.get("data_updates", {})
                    bubbles = data_r.get("response_bubbles", [])
                    bubbles = [b.strip().replace("¿", "").replace("¡", "") for b in bubbles if b.strip()]

                    if intent == "CONFIRM":
                        # Aplicar actualizaciones de datos
                        if updates.get("added_services"):
                            for s in updates["added_services"]:
                                if s not in svcs_current:
                                    svcs_current.append(s)
                        if updates.get("removed_services"):
                            svcs_current = [s for s in svcs_current if s not in updates["removed_services"]]
                        
                        final_sched = updates.get("schedule_text") or discovered.get("schedule_text", "")
                        final_phone = updates.get("phone") or discovered.get("phone", "")
                        final_addr  = updates.get("address") or discovered.get("address", "")
                        assigned_p  = updates.get("assigned_persona", "").strip()

                        setup_buffer["discovered"] = {
                            **discovered,
                            "services": svcs_current,
                            "schedule_text": final_sched,
                            "phone": final_phone,
                            "address": final_addr
                        }

                        if assigned_p:
                            setup_buffer["persona_name"] = assigned_p.title()
                            if _db:
                                _db.update_clinic(
                                    name=clinic_name,
                                    tagline=discovered.get("tagline", ""),
                                    services=svcs_current,
                                    schedule={"texto": final_sched},
                                    phone=final_phone,
                                    address=final_addr,
                                    agent_name=assigned_p.title(),
                                    assistant_name=assigned_p.title(),
                                    setup_step="training_materials",
                                    setup_buffer=setup_buffer
                                )
                        else:
                            if _db:
                                _db.update_clinic(
                                    name=clinic_name,
                                    tagline=discovered.get("tagline", ""),
                                    services=svcs_current,
                                    schedule={"texto": final_sched},
                                    phone=final_phone,
                                    address=final_addr,
                                    setup_step="persona_name",
                                    setup_buffer=setup_buffer
                                )

                        try:
                            from src.firby.brain.soul_engine import SoulEngine
                            SoulEngine.sync_soul(
                                clinic_data={"name": clinic_name, "services": svcs_current, "schedule_text": final_sched, "phone": final_phone, "address": final_addr},
                                assistant_name=assigned_p.title() if assigned_p else None
                            )
                        except Exception as _sse:
                            log.warning(f"[setup_soul] error: {_sse}")

                        if bubbles and len(bubbles) >= 1:
                            return bubbles

                    elif intent == "REJECT":
                        if _db:
                            _db.update_clinic(
                                setup_step="name",
                                setup_buffer={"owner_name": owner_name}
                            )
                        if bubbles and len(bubbles) >= 1:
                            return bubbles
                        return [
                            "Entendido, disculpa la confusión.",
                            "Por favor escribe el nombre exacto de tu clínica o empresa para investigarla de nuevo."
                        ]

                    elif intent in ("QUESTION", "OTHER"):
                        if bubbles and len(bubbles) >= 1:
                            return bubbles

            except Exception as _e_reason:
                log.warning(f"[confirm_discovered_llm] error: {_e_reason}")

            # Fallback seguro si falla LLM
            if _db:
                _db.update_clinic(
                    name=clinic_name,
                    tagline=discovered.get("tagline", ""),
                    services=svcs_current,
                    schedule=discovered.get("schedule", {}),
                    phone=discovered.get("phone", ""),
                    address=discovered.get("address", ""),
                    setup_step="persona_name",
                    setup_buffer=setup_buffer
                )
            return [
                f"Excelente, {owner_name}! Ya guardé toda la información de *{clinic_name}*.",
                "Ahora cuéntame: qué nombre te gustaría que use yo como tu recepcionista para responderle a tus clientes en WhatsApp? (Puedes dejarme como Firby, o asignarme el nombre que prefieras)."
            ]

        # ── Personalización de Nombre y Espejismo Psicológico (100% LLM) ─────────────
        if setup_step == "persona_name":
            clinic_name = clinic.get("name") or setup_buffer.get("name", "tu clínica")
            owner_name = (setup_buffer.get("owner_name") or "").split()[0].title()
            text_clean = text.lower().strip()

            # Detectar confusión o preguntas en persona_name
            is_question_or_confused = any(q in text_clean for q in [
                "como asi", "cómo así", "no entendi", "no entendí", "que es", "qué es",
                "a que te refieres", "a qué te refieres", "por que", "por qué", "?"
            ])
            if is_question_or_confused and not any(w in text_clean for w in ["llamate", "llámate", "nombre", "firby", "sofia", "como yo"]):
                return [
                    f"Me refiero al nombre con el que me presentaré ante tus clientes cuando te escriban por WhatsApp.",
                    f"Por ejemplo: 'Hola! Te habla Firby de {clinic_name}'.",
                    "Qué nombre prefieres que use?"
                ]

            # Extracción inteligente del nombre asignado via LLM
            persona_name = "Firby"
            try:
                from src.core.globals import llm_engine
                _llm = getattr(getattr(self, "generator", None), "llm", None) or llm_engine

                extract_prompt = f"""El usuario fue preguntado qué nombre quiere asignarle a su recepcionista de WhatsApp (ej: 'Firby', 'Andrea', 'Santiago', etc.).
Mensaje del usuario: "{text}"
Nombre del dueño: "{owner_name}"

Responde ÚNICAMENTE un JSON:
{{
  "assistant_name": "Nombre asignado (si dijo 'como yo' o 'mi nombre', usa '{owner_name or 'Santiago'}'. Si dijo 'el que quieras' o 'dejalo asi', usa 'Firby')",
  "gender": "masculino|femenino|neutro"
}}"""
                if _llm:
                    res_p, _ = await _llm.complete(
                        [{"role": "user", "content": extract_prompt}],
                        model_tier="fast", temperature=0.1, max_tokens=100, use_cache=False
                    )
                    clean_p = res_p.strip().replace("```json", "").replace("```", "").strip()
                    data_p = json.loads(clean_p)
                    extracted_name = str(data_p.get("assistant_name", "Firby")).strip()
                    if extracted_name and len(extracted_name) < 40:
                        persona_name = extracted_name.title()

                setup_buffer["persona_name"] = persona_name

                db.update_clinic(
                    agent_name=persona_name,
                    assistant_name=persona_name,
                    setup_step="training_materials",
                    setup_buffer=setup_buffer
                )
                try:
                    from src.firby.brain.soul_engine import SoulEngine
                    SoulEngine.sync_soul(assistant_name=persona_name)
                except Exception:
                    pass

                return [
                    f"De una! Desde este momento atenderé como *{persona_name}* en *{clinic_name}*.",
                    "Para entrenarme con tus precios y casos especiales, puedes enviarme por aquí listas de precios, folletos o escribir ejemplos como 'la consulta cuesta 50 mil'.",
                    "Mantendré el agente BLOQUEADO para clientes externos hasta que pruebes mis respuestas y me des la orden escribiendo 'activar'."
                ]
            except Exception as _pe_err:
                log.warning(f"[persona_name_llm] error: {_pe_err}")

            # Fallback limpio si falla LLM
            if "como yo" in text.lower() or "mi nombre" in text.lower():
                persona_name = owner_name or "Santiago"

            db.update_clinic(
                agent_name=persona_name,
                assistant_name=persona_name,
                setup_step="training_materials",
                setup_buffer=setup_buffer
            )
            try:
                from src.firby.brain.soul_engine import SoulEngine
                SoulEngine.sync_soul(assistant_name=persona_name)
            except Exception:
                pass
            return [
                f"De una! Desde este momento atenderé como *{persona_name}* en *{clinic_name}*.",
                "Para entrenarme con tus precios y casos especiales, puedes enviarme por aquí listas de precios, folletos o escribir ejemplos como 'la consulta cuesta 50 mil'.",
                "Mantendré el agente BLOQUEADO para clientes externos hasta que pruebes mis respuestas y me des la orden escribiendo 'activar'."
            ]

        # ── Fase de Entrenamiento y Materiales (100% LLM) ──────────────────────
        if setup_step == "training_materials":
            text_low = text.lower().strip()
            if text_low in ["activar", "listo", "despegar", "iniciar", "empezar", "/activar"]:
                db.update_clinic(
                    setup_done=1,
                    setup_step="idle",
                    setup_buffer={}
                )
                persona_name = clinic.get("assistant_name") or setup_buffer.get("persona_name") or "Firby"
                clinic_name = clinic.get("name") or "tu empresa"
                return [
                    f"🚀 AGENTE DESBLOQUEADO Y 100% ACTIVO PARA EL PÚBLICO!",
                    f"Me llamo *{persona_name}* y desde este milisegundo estoy atendiendo el WhatsApp de *{clinic_name}* con tu estilo y tus materiales aprendidos.",
                    "Puedes monitorearme en tiempo real desde este chat. Escribe /config o /citas para ver tus controles de administración."
                ]
            else:
                # 🟢 Detectar si solicitó cambiar de nombre durante el entrenamiento
                is_name_change_request = any(kw in text_low for w in [
                    "cambia", "cambiar", "llamate", "llámate", "ahora te llamas", 
                    "prefiero", "te vas a llamar", "ahora seras", "ahora serás"
                ] for kw in [w] if kw in text_low and any(nk in text_low for nk in ["nombre", "llame", "llamas", "llamarte", "seras", "serás"]))
                
                if is_name_change_request:
                    try:
                        from src.core.globals import llm_engine
                        _llm = getattr(getattr(self, "generator", None), "llm", None) or llm_engine
                        if _llm:
                            res_n, _ = await _llm.complete(
                                [{"role": "user", "content": f"Extrae UNICAMENTE el nuevo nombre asignado de esta frase: '{text}'. Si no hay un nombre claro, responde 'Firby'. SOLO JSON: {{\"new_name\": \"...\"}}"}],
                                model_tier="fast", temperature=0.1, max_tokens=50, use_cache=False
                            )
                            clean_n = res_n.strip().replace("```json", "").replace("```", "").strip()
                            data_n = json.loads(clean_n)
                            new_name = str(data_n.get("new_name", "Firby")).strip().title()
                            if new_name and len(new_name) < 40 and new_name != "Firby":
                                db.update_clinic(assistant_name=new_name)
                                setup_buffer["persona_name"] = new_name
                    except Exception as _ne_err:
                        log.warning(f"[name_change] error: {_ne_err}")

                # 🔑 Interceptar credenciales de Google OAuth (Estilo Hermes Tool Ingestion)
                google_oauth_status_note = ""
                if ("client_id" in text or "installed" in text or "web" in text) and "client_secret" in text:
                    try:
                        import json as _j_creds
                        from pathlib import Path
                        
                        raw_json_str = text
                        json_match = re.search(r"\{.*\}", text, re.DOTALL)
                        if json_match:
                            raw_json_str = json_match.group(0)

                        creds_data = _j_creds.loads(raw_json_str)
                        creds = creds_data.get("installed") or creds_data.get("web") or creds_data
                        c_id = creds.get("client_id", "")
                        c_sec = creds.get("client_secret", "")
                        r_tok = creds_data.get("refresh_token") or creds.get("refresh_token") or ""

                        if c_id and c_sec:
                            vault_dir = Path("integrations/vault/default")
                            vault_dir.mkdir(parents=True, exist_ok=True)
                            (vault_dir / "google_credentials.json").write_text(raw_json_str)
                            
                            os.environ["GOOGLE_CLIENT_ID"] = c_id
                            os.environ["GOOGLE_CLIENT_SECRET"] = c_sec
                            if r_tok:
                                os.environ["GOOGLE_REFRESH_TOKEN"] = r_tok

                            env_path = Path(".env")
                            if env_path.exists():
                                env_text = env_path.read_text()
                                if "GOOGLE_CLIENT_ID" not in env_text:
                                    env_text += f"\nGOOGLE_CLIENT_ID={c_id}\nGOOGLE_CLIENT_SECRET={c_sec}\n"
                                    if r_tok:
                                        env_text += f"GOOGLE_REFRESH_TOKEN={r_tok}\n"
                                    env_path.write_text(env_text)

                            if db:
                                db.save_core_memory("google_oauth_creds", json.dumps({"client_id": c_id, "has_secret": True, "has_refresh_token": bool(r_tok)}), category="system")

                            google_oauth_status_note = "[EVENTO DE SISTEMA: El dueño acaba de enviar las credenciales de Google OAuth. Las credenciales fueron procesadas y guardadas exitosamente en la bóveda. Confírmale a tu dueño que las credenciales quedaron recibidas e integradas con calidez y naturalidad]."
                    except Exception as _cred_err:
                        log.warning(f"[admin_google_creds] Error guardando credenciales: {_cred_err}")

                # 📊 Interceptar Google Sheets URL (Estilo Hermes)
                try:
                    from src.firby.brain.hermes_api_engine import hermes_api_engine
                    sheet_result = await hermes_api_engine.process_incoming_sheet(text, db)
                    if sheet_result is not None:
                        return sheet_result
                except Exception as _sheet_err:
                    log.warning(f"[hermes_sheet] error: {_sheet_err}")

                # Ingestar productos, precios o entrenamiento dado por el admin
                if db:
                    try:
                        import secrets
                        db.save_core_memory(f"admin_rule_{secrets.token_hex(4)}", text.strip(), category="learned")
                        
                        # 🛒 Extracción de Productos y Precios para Inventario (Tienda de barrio, restaurante, etc.)
                        try:
                            from src.core.globals import llm_engine
                            _llm_p = getattr(getattr(self, "generator", None), "llm", None) or llm_engine
                            if _llm_p:
                                p_prompt = f"""Extrae productos, ítems de inventario o servicios con sus precios a partir de este mensaje: "{text}".
Responde ÚNICAMENTE un JSON: {{"Producto": "$Precio"}}. Si no hay precios o productos, responde {{}}. SOLO JSON."""
                                p_res, _ = await _llm_p.complete([{"role": "user", "content": p_prompt}], model_tier="fast", temperature=0.1, max_tokens=150, use_cache=False)
                                clean_pr = p_res.strip().replace("```json", "").replace("```", "").strip()
                                parsed_pr = json.loads(clean_pr)
                                if isinstance(parsed_pr, dict) and parsed_pr:
                                    current_clinic = db.get_clinic()
                                    curr_pricing = current_clinic.get("pricing", {})
                                    if isinstance(curr_pricing, str):
                                        try: curr_pricing = json.loads(curr_pricing)
                                        except Exception: curr_pricing = {}
                                    curr_pricing.update(parsed_pr)

                                    curr_services = current_clinic.get("services", [])
                                    if isinstance(curr_services, str):
                                        try: curr_services = json.loads(curr_services)
                                        except Exception: curr_services = [s.strip() for s in curr_services.split(",") if s.strip()]
                                    if not isinstance(curr_services, list):
                                        curr_services = []

                                    for k, v in parsed_pr.items():
                                        item_str = f"{k}: {v}"
                                        if item_str not in curr_services:
                                            curr_services.append(item_str)

                                    db.update_clinic(pricing=json.dumps(curr_pricing), services=json.dumps(curr_services))
                                    db.save_core_memory("pricing_catalog", json.dumps(curr_pricing), category="clinic")
                                    log.info(f"[inventory] Updated pricing catalog with {len(parsed_pr)} items: {parsed_pr}")
                        except Exception as _pr_err:
                            log.warning(f"[inventory_extract] error: {_pr_err}")

                    except Exception:
                        pass

                persona_name = db.get_clinic().get("assistant_name") or setup_buffer.get("persona_name") or "Firby"
                clinic_name = clinic.get("name") or "tu empresa"

                # Generar respuesta de aprendizaje 100% por LLM (con Espejismo de Emojis y Capacidades Reales)
                try:
                    from src.core.globals import llm_engine
                    _llm = getattr(getattr(self, "generator", None), "llm", None) or llm_engine
                    if _llm:
                        has_emojis = any(ord(char) > 0x1F300 for char in text)
                        emoji_rule = "REGLA DE EMOJIS: El dueño NO usó emojis en su mensaje. Queda TOTALMENTE PROHIBIDO usar emojis en tu respuesta. Cero emojis." if not has_emojis else "REGLA DE EMOJIS: Puedes usar 1 o 2 emojis cálidos."

                        sys_tr = f"""Eres {persona_name}, la mano derecha de IA para {clinic_name}. Estás conversando en vivo por WhatsApp con tu dueño/administrador.

{emoji_rule}

SITIO WEB DE ADMINISTRACIÓN / DASHBOARD:
- Si pregunta dónde ver su panel, configurar su cuenta o ver analíticas, la URL de sign-in es: https://firbyai.lat/sign-in

TUS SUPERPODERES Y CAPACIDADES REALES:
1. Google Calendar / Google APIs: Si te habla de conectar las APIs de Google o su calendario, respóndele con entusiasmo que SÍ te conectas a su Google Calendar en vivo para ver la disponibilidad en tiempo real del especialista antes de agendar citas.
2. Audios de Voz Ultra-Realista: Puedes enviar notas de voz de WhatsApp con acento natural cuando lo requiera.
3. Ingestión de PDFs e Imágenes: Lees catálogos, listas de precios y documentos en tiempo real.
4. Smart Handoff: Le notificas al dueño de inmediato al celular si un cliente requiere atención humana directa.

REGLAS DE ESTILO (WhatsApp Colombiano / Paisa ultra-humano):
1. Responde de forma CORTA, FRESCAS y CERCANA.
2. Separa tus pensamientos en 2 o 3 burbujas usando '|||'.
3. NUNCA uses parrafadas largas ni lenguaje de libro formal.
4. NUNCA uses signos invertidos ('¿' o '¡'). Solo usa '?' y '!' al final de frase.
5. Si te hace una pregunta o te habla de una integración, respóndele la duda de forma inteligente sin decir que fue una 'instrucción aprendida'. Recuérdale de forma fluida que cuando quiera empezar con el público en WhatsApp solo debe escribir 'activar'.
6. SOLICITUDES DE AUDIO / NOTA DE VOZ: Si el usuario te pide un audio ("enviame un audio", "enviame otro audio"), NUNCA respondas con meta-promesas como "ya te grabo" o "en un segundito te envío un audio". En lugar de eso, respóndele DIRECTAMENTE la información o lo que necesite habladoramente. Tu respuesta será sintetizada como nota de voz nativa de WhatsApp.

EJEMPLO DE INTERACCIÓN:
- Usuario: "si te doy las apis de google para que veas mi calendario te conectas para que veas que disponibilidad tiene el doctor cuando quieras agendar?"
  Respuesta: Obvio que sí! Con las APIs de Google Calendar me conecto directo a tu agenda en vivo y reviso disponibilidad en tiempo real antes de agendar a cualquier paciente. ||| Pásame las credenciales OAuth o el enlace y lo dejamos listo de una. ||| Cuando estés listo para abrir el bot al público me escribes 'activar'!
"""
                        if google_oauth_status_note:
                            sys_tr += f"\n\n{google_oauth_status_note}"

                        res_tr, _ = await _llm.complete(
                            [
                                {"role": "system", "content": sys_tr},
                                {"role": "user", "content": text}
                            ],
                            model_tier="fast", temperature=0.4, max_tokens=250, use_cache=False
                        )
                        if res_tr and res_tr.strip():
                            return [b.strip() for b in res_tr.split("|||") if b.strip()]
                except Exception as _tr_err:
                    log.warning(f"[training_materials_llm] error: {_tr_err}")

                return [
                    "Anotado y aprendido! Lo sumé a mi memoria de trabajo. 🧠",
                    "Escribe 'activar' cuando estés listo para desatascarme y responderle a tus clientes externos."
                ]

        if setup_step not in step_names:
            db.update_clinic(setup_step="idle", setup_buffer={})
            return ["Algo salió mal. Escribe /setup para comenzar de nuevo."]

        idx = step_names.index(setup_step)

        # ── Procesar respuesta ─────────────────────────────────────────────────
        if setup_step == "services":
            raw_svcs = [s.strip() for s in text.split(",") if s.strip()]
            # Validar: si parece una URL, un comando, o una sola frase larga -> rechazar
            is_garbage = (
                len(raw_svcs) == 1 and (
                    len(raw_svcs[0]) > 50 or
                    any(kw in raw_svcs[0].lower() for kw in [
                        "google", "busca", "http", "www", ".com", "facebook",
                        "instagram", "busqueda", "encuentra"
                    ])
                )
            )
            if is_garbage:
                return [
                    "Eso no parece una lista de servicios.",
                    "Escríbelos separados por coma:\nEj: Botox, Rellenos, Limpieza facial, Laser CO2, Radiofrecuencia"
                ]
            setup_buffer["services"] = [s.title() for s in raw_svcs]
        elif setup_step == "tagline":
            setup_buffer["tagline"] = "" if text.lower().strip() in ["no", "n", "-", "ninguno"] else text.strip()
        elif setup_step == "schedule":
            setup_buffer["schedule"] = {"General": text.strip()}
        elif setup_step == "pricing":
            # Parsear precios libres: "Botox: 350.000, Rellenos: 500.000" o texto libre
            pricing_dict = {}
            text_low_p = text.lower().strip()
            if text_low_p not in ["no", "n", "-", "ninguno", "despues", "luego"]:
                for line in re.split(r'[,\n;]+', text):
                    line = line.strip()
                    if ':' in line:
                        parts = line.split(':', 1)
                        svc = parts[0].strip()
                        price = parts[1].strip()
                        if svc and price:
                            pricing_dict[svc] = price
                    elif '-' in line:
                        parts = line.split('-', 1)
                        svc = parts[0].strip()
                        price = parts[1].strip()
                        if svc and price:
                            pricing_dict[svc] = price
            setup_buffer["pricing"] = pricing_dict
        else:
            setup_buffer[setup_step] = text.strip()

        # ── Si acaba de darnos el nombre, buscar en Google ─────────────────────
        if setup_step == "name":
            text_clean = text.lower().strip()
            
            # Detectar confusión o dudas (ej. "cómo así?", "no entendí", "a qué te refieres?", "qué negocio?")
            is_confused = any(q in text_clean for q in [
                "como asi", "cómo así", "no entendi", "no entendí", "que es", "qué es",
                "a que te refieres", "a qué te refieres", "por que", "por qué", "?"
            ])
            if is_confused and not any(w in text_clean for w in ["clinica", "clínica", "empresa", "odontologia", "odontología", "doctor", "consultorio", "restaurante", "tienda", "centro", "salud"]):
                o_name = (setup_buffer.get("owner_name") or "").split()[0].title()
                greeting_o = f", {o_name}" if o_name else ""
                return [
                    f"Me refiero al nombre de tu empresa, clínica o consultorio{greeting_o} (por ejemplo: 'Clínica Las Américas', 'Consultorio Dr. Rubio', 'Odontología San Lucas').",
                    "Con el nombre investigo tus servicios y horarios en internet para configurarme automáticamente. Cómo se llama tu negocio?"
                ]

            # 🟢 Extracción Limpia por Regex + LLM de Nombre de Empresa y Nombre de Admin
            c_name, o_name = "", ""
            
            # Regex Parser de alta precisión
            m_clinic = re.search(r"(?:clinica|clínica|empresa|negocio)\s+(?:se\s+llama\s+)?([A-Za-z0-9\sáéíóúÁÉÍÓÚñÑ]{3,50})", text, re.I)
            m_owner = re.search(r"(?:mi\s+nombre\s+es|soy|me\s+llamo)\s+([A-Za-z0-9\sáéíóúÁÉÍÓÚñÑ]{2,30})", text, re.I)
            
            if m_clinic:
                c_name = m_clinic.group(1).strip()
            if m_owner:
                o_name = m_owner.group(1).split(",")[0].strip().split()[0].title()

            # LLM Parser para frases complejas
            if not c_name or not o_name:
                try:
                    from src.core.globals import llm_engine
                    _llm = getattr(getattr(self, "generator", None), "llm", None) or llm_engine
                    prompt_ext = f"""Extrae limpiamente el NOMBRE DE LA EMPRESA O CLINICA y el NOMBRE DEL DUENO/ADMINISTRADOR a partir de este mensaje:

MENSAJE DEL USUARIO: "{text}"

Responde UNICAMENTE un JSON valido con esta estructura exacta:
{{
  "clinic_name": "Nombre oficial limpio de la empresa o clinica",
  "owner_name": "Nombre de pila del dueno o administrador si aparece"
}}

Si no aparece el nombre del dueno, usa "". SOLO JSON."""

                    if _llm:
                        res_ext, _ = await _llm.complete(
                            [{"role": "user", "content": prompt_ext}],
                            model_tier="fast",
                            temperature=0.1,
                            max_tokens=150,
                            use_cache=False
                        )
                        clean_json = res_ext.strip().replace("```json", "").replace("```", "").strip()
                        data_ext = json.loads(clean_json)
                        if not c_name and data_ext.get("clinic_name"):
                            c_name = str(data_ext.get("clinic_name", "")).strip()
                        if not o_name and data_ext.get("owner_name"):
                            o_name = str(data_ext.get("owner_name", "")).strip().split()[0].title()
                except Exception as _ex_err:
                    log.warning(f"[setup_name] error extracting via LLM: {_ex_err}")

            clinic_name = c_name if (c_name and len(c_name) < 60) else text.strip()
            if len(clinic_name) > 60:
                clinic_name = clinic_name.split(",")[-1].strip()

            if o_name:
                setup_buffer["owner_name"] = o_name

            discovered  = await self._discover_clinic_from_web(clinic_name)

            if discovered and discovered.get("confidence", 0) >= 0.5:
                # Guardamos todo en buffer
                official_name = (discovered.get("name") or clinic_name).strip()
                setup_buffer["discovered"] = discovered
                web_url = discovered.get("website_url") or discovered.get("url") or ""
                svcs  = ", ".join(discovered.get("services", [])) or "Servicios médicos/especializados"
                phone = discovered.get("phone", "")
                sched = discovered.get("schedule_text", "")
                addr  = discovered.get("address", "")

                db.update_clinic(
                    setup_step="confirm_discovered",
                    setup_buffer=setup_buffer
                )

                curr_o = (setup_buffer.get("owner_name") or o_name or "").split()[0].title()

                # 🟢 Presentación 100% Generada por LLM (Humana, Cálida y con Link)
                pres_prompt = f"""Eres Firby, una socia de inteligencia artificial para negocios.
Estás hablando con tu dueño ({curr_o or 'Santiago'}).
Acabas de buscar en Google la información pública de su empresa ({official_name}) para ahorrarle tiempo.

DATOS ENCONTRADOS EN INTERNET:
- Empresa: {official_name}
- Web / Enlace: {web_url or 'No especificado'}
- Servicios: {svcs}
- Horario: {sched or 'Consultar'}
- Teléfono: {phone or 'No especificado'}
- Dirección / Sedes: {addr or 'No especificada'}

INSTRUCCIONES:
1. Saluda con entusiasmo y por su primer nombre ({curr_o or 'Santiago'}).
2. Cuéntale con calidez que encontraste la información de su negocio en internet para aprender de una vez.
3. Presenta los datos clave (servicios, horario, sedes/dirección y el enlace web si existe) de forma clara, visual y estética.
4. Pregúntale si los datos son correctos o si le gustaría ajustar/agregar algo más antes de continuar (para continuar solo debe decir 'sí').
5. CERO signos '¿' ni '¡'. Habla como un profesional en Medellín / Colombia.
6. Divide la respuesta en 2 o 3 burbujas usando '|||' como separador."""

                try:
                    from src.core.globals import llm_engine
                    _llm = getattr(getattr(self, "generator", None), "llm", None) or llm_engine
                    if _llm:
                        res_pres, _ = await _llm.complete(
                            [{"role": "user", "content": pres_prompt}],
                            model_tier="fast",
                            temperature=0.3,
                            max_tokens=400,
                            use_cache=False
                        )
                        clean_pres = res_pres.strip()
                        if clean_pres:
                            bubbles = [b.strip() for b in clean_pres.split("|||") if b.strip()]
                            if len(bubbles) >= 2:
                                return bubbles
                except Exception as _e_pres:
                    log.warning(f"[setup_pres_llm] error: {_e_pres}")

                # Fallback de seguridad
                greeting_owner = f", {curr_o}" if curr_o else ""
                summary_parts = [f"• *Servicios*: {svcs}"]
                if sched:
                    summary_parts.append(f"• *Horario*: {sched}")
                if addr:
                    summary_parts.append(f"• *Dirección*: {addr}")
                if phone:
                    summary_parts.append(f"• *Teléfono*: {phone}")
                if web_url:
                    summary_parts.append(f"• *Web*: {web_url}")
                summary = "\n".join(summary_parts)

                return [
                    f"Genial{greeting_owner}! Estuve investigando en segundo plano y encontré la información de *{official_name}* en internet.",
                    f"Esto fue lo principal que rescaté:\n\n{summary}",
                    "Confirmas que esta información es correcta o te gustaría cambiar algo? Dime 'sí' para continuar."
                ]
            else:
                # No encontre nada, seguir con setup normal
                db.update_clinic(
                    setup_step=step_names[1],
                    setup_buffer=setup_buffer
                )
                return self._setup_next_bubbles("name", text.strip(), "tagline", setup_buffer)

        # ── Siguiente paso normal ──────────────────────────────────────────────
        if idx + 1 < len(step_names):
            next_step = step_names[idx + 1]
            db.update_clinic(setup_step=next_step, setup_buffer=setup_buffer)
            return self._setup_next_bubbles(setup_step, text.strip(), next_step, setup_buffer)

        # ── Pasar a personalización de nombre de recepcionista ──────────────────
        db.update_clinic(
            name=setup_buffer.get("name", "Mi Clínica"),
            tagline=setup_buffer.get("tagline", ""),
            services=setup_buffer.get("services", []),
            schedule=setup_buffer.get("schedule", {}),
            phone=setup_buffer.get("phone", ""),
            pricing=setup_buffer.get("pricing", {}),
            setup_step="persona_name",
            setup_buffer=setup_buffer
        )
        owner_name = setup_buffer.get("owner_name", "")
        greeting_o = f", {owner_name}" if owner_name else ""
        return [
            f"Listo{greeting_o}! Ya guardé toda la información de tu negocio.",
            "Ahora cuéntame: qué nombre te gustaría que use yo como tu recepcionista para responderle a tus clientes en WhatsApp? (Puedes dejarme como Firby, o asignarme el nombre que prefieras)."
        ]

        # Guardar identidad en memoria permanente
        db.remember("clinic_name",     name,                               "identity")
        db.remember("clinic_services", ", ".join(setup_buffer.get("services", [])), "clinic")
        db.remember("clinic_phone",    setup_buffer.get("phone", ""),     "clinic")
        db.remember("platform",        Config.PLATFORM,                    "identity")
        db.remember("setup_completed", "true",                             "identity")

        # Notificar a Omni que esta instancia quedó configurada
        asyncio.create_task(asyncio.to_thread(
            notify_omni, "setup_completado",
            f"Nueva instancia configurada: {name} (sector: {Config.SECTOR})", name
        ))

        # Guía de siguiente paso — WhatsApp si aún no está conectado
        whatsapp_connected = db.recall("whatsapp_connected") == "true"

        if whatsapp_connected:
            next_step = (
                "\n\nYa tienes WhatsApp conectado. Listo para recibir pacientes."
            )
        else:
            next_step = (
                "\n\nSiguiente paso — conectar WhatsApp:\n"
                "Pégame aquí tu Phone Number ID y Access Token de Meta Business.\n"
                "Formato:\n"
                "  WA_PHONE_ID: 123456789012345\n"
                "  WA_TOKEN: EAAxxxxx...\n\n"
                "Si aun no los tienes, escribe /whatsapp y te explico cómo obtenerlos."
            )

        kb_invite = (
            "\n\nTambién puedes enviarme un documento con toda la info de tu clinica "
            "(precios detallados, protocolos, FAQs) y lo aprendo todo de una vez."
        ) if _KB_AVAILABLE else ""

        return [
            f"¡Listo! Soy {name}.{pricing_note}",
            f"Servicios: {svcs}.{next_step}{kb_invite}",
            "Estoy aquí cuando llegue tu primer paciente. Cuéntame más sobre cómo te gusta que les hable y yo aprendo.",
        ]

    async def _discover_clinic_from_web(self, clinic_name: str, city: str = "Medellin") -> Dict:
        """
        Busca la clinica en Google y extrae info estructurada via LLM.
        V9 Upgrade: Timeout robusto y protección contra cuelgues.
        """
        try:
            # ── Paso 1: Búsqueda Web con Timeout ──────────────────────────────
            search_query = f"{clinic_name} {city} servicios precios horario telefono"
            log.info(f"[autodiscovery] buscando: {search_query}")

            try:
                # Timeout de 15s para la búsqueda
                snippets = await asyncio.wait_for(
                    self.search.search(search_query, context=""),
                    timeout=15.0
                )
            except asyncio.TimeoutError:
                log.warning(f"[autodiscovery] búsqueda expiró para {clinic_name}")
                return {}
            except Exception as se:
                log.warning(f"[autodiscovery] error en búsqueda: {se}")
                return {}

            if not snippets:
                log.info(f"[autodiscovery] no se encontro info de {clinic_name}")
                return {}

            # Usar LLM para extraer datos estructurados
            extraction_prompt = f"""Extrae informacion estructurada de esta empresa o clinica a partir de los snippets de busqueda de Google.

NOMBRE BUSCADO: {clinic_name}
CIUDAD: {city}

SNIPPETS DE BUSQUEDA:
{snippets[:1400]}

Extrae y retorna SOLO un JSON valido con esta estructura exacta:
{{
  "name": "nombre oficial exacto de la clinica o empresa",
  "tagline": "descripcion corta o slogan si hay",
  "website_url": "url o enlace web oficial si aparece (o vacio si no)",
  "services": ["servicio 1", "servicio 2", ...],
  "schedule": {{"Lunes a Viernes": "9am-6pm", "Sabados": "9am-2pm"}},
  "schedule_text": "texto resumido del horario",
  "phone": "telefono de contacto si aparece",
  "address": "direccion fisica o sedes si aparece",
  "confidence": 0.0
}}

confidence: 0.0 si no encontraste nada relevante, 0.5 si encontraste algo, 0.9 si encontraste la clinica real con datos.
Si un campo no aplica o no se encontro, usa "" o []. Solo JSON, sin texto extra."""

            try:
                # Timeout de 20s para el LLM
                _llm = getattr(getattr(self, "generator", None), "llm", None) or llm_engine
                response, _ = await asyncio.wait_for(
                    _llm.complete(
                        [{"role": "user", "content": extraction_prompt}],
                        model_tier="fast",
                        temperature=0.1,
                        max_tokens=600,
                        use_cache=False
                    ),
                    timeout=20.0
                )
            except asyncio.TimeoutError:
                log.warning(f"[autodiscovery] LLM expiró para {clinic_name}")
                return {}

            # Limpiar y parsear
            clean = response.strip()
            clean = re.sub(r'^```json\s*', '', clean)
            clean = re.sub(r'\s*```$', '', clean)

            data = json.loads(clean)
            log.info(f"[autodiscovery] encontrado con confidence={data.get('confidence', 0)}: {data.get('name', '')} | web={data.get('website_url', '')}")
            return data

        except Exception as e:
            log.warning(f"[autodiscovery] error critico: {e}")
            return {}

    def _setup_next_bubbles(self, completed_step: str, value: str,
                            next_step: str, buffer: Dict) -> List[str]:
        """Genera transicion natural entre pasos. Acuse breve + pregunta."""
        ack = self._setup_ack(completed_step, value, buffer)

        questions = {
            "tagline":  "Tienes un slogan o descripcion corta? Si no, escribe 'no'.",
            "services": "Que servicios ofreces?\nEscribelos separados por coma. Ej: Botox, Rellenos, Limpieza facial",
            "schedule": "Cual es el horario de atencion?\nEj: Lunes a viernes 9am-6pm, Sabados 9am-2pm",
            "phone":    "Y el telefono de la clinica?",
            "pricing":  "Tienes precios para tus servicios? (opcionales, ayudan a informar mejor al paciente)\n\nFormato: Servicio: precio\nEj: Botox: 350.000, Rellenos: 500.000\n\nSi no, escribe 'no'.",
        }

        question = questions.get(next_step, "")

        if ack and question:
            return [ack, question]
        if question:
            return [question]
        return [ack] if ack else ["Siguiente."]

    def _setup_ack(self, step: str, value: str, buffer: Dict) -> str:
        """Acuse corto y natural. Maximo 1 oracion."""
        if step == "name":
            clean = value.strip().title() if value else "Listo"
            return f"{clean}, perfecto."
        elif step == "tagline":
            low = value.lower().strip()
            if not value or low in ["no", "n", "-", "ninguno", "ninguna"]:
                return "Sin slogan, bien."
            return "Guardado."
        elif step == "services":
            n = len(buffer.get("services", []))
            s = "servicio" if n == 1 else "servicios"
            return f"{n} {s} registrados."
        elif step == "schedule":
            return "Horario guardado."
        elif step == "phone":
            return "Telefono guardado."
        elif step == "pricing":
            low = value.lower().strip()
            if not value or low in ["no", "n", "-", "ninguno"]:
                return "Sin precios por ahora, bien."
            return "Precios guardados."
        return ""




    async def _handle_emergency(self, chat_id: str, text: str,
                                analysis: MessageAnalysis, clinic: Dict) -> List[str]:
        """Maneja emergencias."""
        
        # Notificar a admins
        admin_ids = _parse_admin_ids(clinic.get("admin_chat_ids", []))
        
        for admin_id in admin_ids:
            await mcp_manager.execute(
                "notifications_v1",
                "send_notification",
                {
                    "chat_id": admin_id,
                    "message": f"⚠️ EMERGENCIA detectada:\n\n{text[:200]}\n\nChat: {chat_id}"
                }
            )
        
        phone = clinic.get("phone", "")
        
        return [
            "Entiendo que es urgente.",
            f"Te recomiendo llamar directamente al teléfono: {phone}" if phone else "Por favor contacta a la clínica directamente.",
            "Un profesional te atenderá de inmediato."
        ]
    
    def _extract_actions(self, response: str, chat_id: str, 
                        clinic: Dict) -> Tuple[str, List[Dict]]:
        """Extrae y procesa acciones del response."""
        actions = []
        clean = response
        
        # Extraer nombre del paciente
        if "NOMBRE:" in clean:
            parts = clean.split("NOMBRE:", 1)
            clean = parts[0].strip()
            try:
                raw = parts[1].strip().split("\n")[0]
                data = json.loads(raw)
                if data.get("name"):
                    db.update_patient(chat_id, name=data["name"])
                    actions.append({"type": "name_extracted", "name": data["name"]})
            except Exception:
                pass
        
        # Extraer cita
        if "CITA:" in clean:
            parts = clean.split("CITA:", 1)
            clean = parts[0].strip()
            try:
                raw = parts[1].strip().split("\n")[0]
                data = json.loads(raw)
                apt_id = db.save_appointment(chat_id, data)
                actions.append({"type": "appointment_created", "id": apt_id, "data": data})
                
                # Notificar admin
                admin_ids = _parse_admin_ids(clinic.get("admin_chat_ids", []))
                
                for admin_id in admin_ids:
                    asyncio.create_task(self._notify_admin_appointment(admin_id, data))
                
                # Procesar Pasarela de Pagos (Stripe / Bold)
                from src.core.globals import payment_bridge, calendar_bridge
                deposit = payment_bridge.get_deposit_amount(data.get("service", ""))
                
                if deposit > 0:
                    db.update_appointment(apt_id, status="pendiente_pago")
                    
                    async def _process_payment_flow():
                        try:
                            pay_url = await payment_bridge.create_payment_link(
                                appointment_id=apt_id,
                                service=data.get("service", ""),
                                amount=deposit,
                                chat_id=chat_id
                            )
                            if pay_url:
                                db.update_appointment(apt_id, notes=f"{data.get('notes', '')}\n[Link de Pago]: {pay_url}".strip())
                                # Enviar link de pago al paciente
                                formatted_msg = (
                                    f"Para confirmar tu cita de {data.get('service', '')}, "
                                    f"por favor realiza el pago del abono de {deposit:,} COP ingresando a este enlace: {pay_url}"
                                )
                                await self._send_message(chat_id, formatted_msg)
                        except Exception as _pay_err:
                            log.error(f"[payments] Error procesando flujo de pago: {_pay_err}")
                            
                    asyncio.create_task(_process_payment_flow())

                # Sincronizar con Google Calendar si está configurado
                if calendar_bridge and calendar_bridge.has_google_calendar():
                    async def _sync_to_gcal():
                        try:
                            p_name = data.get("patient_name") or "Paciente"
                            p_phone = data.get("patient_phone") or chat_id.split("@")[0]
                            svc = data.get("service") or "Servicio"
                            dt_slot = data.get("datetime_slot")
                            
                            notes_field = data.get("notes", "")
                            if deposit > 0:
                                notes_field = f"[PENDIENTE DE PAGO - Abono: {deposit:,} COP]\n{notes_field}".strip()
                                
                            if dt_slot:
                                evt_id = await calendar_bridge.create_event(
                                    patient_name=p_name,
                                    phone=p_phone,
                                    service=svc,
                                    date_time=dt_slot,
                                    notes=notes_field
                                )
                                if evt_id:
                                    db.update_appointment(apt_id, google_event_id=evt_id)
                                    log.info(f"[calendar] Cita {apt_id} vinculada exitosamente con evento Google {evt_id}")
                        except Exception as _sync_err:
                            log.warning(f"[calendar] Error sincronizando cita con Google Calendar: {_sync_err}")
                    asyncio.create_task(_sync_to_gcal())

                # Programar recordatorio
                if data.get("datetime_slot"):
                    try:
                        apt_time = datetime.fromisoformat(data["datetime_slot"])
                        reminder_time = apt_time - timedelta(hours=24)
                        if reminder_time > datetime.now():
                            task_manager.schedule_task(
                                "reminder",
                                {
                                    "chat_id": chat_id,
                                    "message": f"Recordatorio: Mañana tienes cita para {data.get('service', 'tu servicio')} a las {apt_time.strftime('%H:%M')}.",
                                    "appointment_id": apt_id
                                },
                                scheduled_for=reminder_time
                            )
                    except Exception:
                        pass
            except Exception as e:
                log.warning(f"Appointment extraction error: {e}")
        
        return clean, actions
    
    async def _notify_admin_appointment(self, admin_id: str, data: Dict):
        """Notifica al admin de nueva cita."""
        nombre = data.get("patient_name", "Paciente")
        msg = (
            f"*Nueva cita agendada*\n\n"
            f"Paciente: {nombre}\n"
            f"Servicio: {data.get('service', '-')}\n"
            f"Fecha/hora: {data.get('datetime_slot', '-')}\n"
            f"Teléfono: {data.get('patient_phone', '-')}"
        )
        
        await mcp_manager.execute(
            "notifications_v1",
            "send_notification",
            {"chat_id": admin_id, "message": msg}
        )
    
    def _split_bubbles(self, text: str, chat_id: str = "",
                       archetype: str = "amigable") -> List[str]:
        """
        Divide respuesta en burbujas separadas.
        """
        import random as _rnd
        import re

        def clean(s: str) -> str:
            s = s.replace('¿', '').replace('¡', '').strip()
            import re as _re2
            s = _re2.sub(r'!{2,}', '!', s)
            s = _re2.sub(r'\s*\|{1,2}\s*$', '', s)
            s = _re2.sub(r'\s+\|{1,2}\s+', ' ', s)
            s = s.replace('.!', '.').replace('!.', '.')
            if anti_robot_filter:
                s = anti_robot_filter.process(s, archetype)
            return s
        
        def dedupe_greetings(raw_bubbles: List[str]) -> List[str]:
            if not raw_bubbles:
                return raw_bubbles
            greeting_words = {"hola", "holaa", "buenas", "buenos días", "buenas tardes", "buenas noches", "hey", "heyy", "holi", "hi", "hello"}
            res = []
            seen_greeting = False
            for b in raw_bubbles:
                if not b or not b.strip():
                    continue
                norm_b = re.sub(r'[^\w\s]', '', b.lower()).strip()
                words = norm_b.split()
                if words and all(w in greeting_words for w in words):
                    if seen_greeting:
                        continue
                    seen_greeting = True
                    res.append(f"{words[0].capitalize()}!")
                else:
                    if words and any(w in greeting_words for w in words[:2]):
                        seen_greeting = True
                    res.append(b)
            return res or raw_bubbles

        def _subsplit_long_bubble(b: str, max_chars: int = 125) -> List[str]:
            b = b.strip()
            if len(b) <= max_chars:
                return [b] if b else []
            
            # 1. Intentar dividir por oraciones (puntos, interrogaciones, exclamaciones)
            sentences = re.split(r'(?<=[.!?])\s+(?=[A-ZÁÉÍÓÚÜÑA-Za-z])', b)
            sentences = [s.strip() for s in sentences if s.strip()]
            if len(sentences) >= 2:
                result = []
                curr = ''
                for s in sentences:
                    if not curr:
                        curr = s
                    elif len(curr) + len(s) + 1 <= max_chars:
                        curr += ' ' + s
                    else:
                        result.append(curr)
                        curr = s
                if curr:
                    result.append(curr)
                return result

            # 2. Si es una sola oración larga, buscar conectores naturales
            connectors = r',\s+(?=y\b|pero\b|así que\b|entonces\b|para que\b|me cuentas\b|cuéntame\b|además\b|te parece\b|por ejemplo\b)'
            clauses = re.split(connectors, b, flags=re.IGNORECASE)
            clauses = [c.strip() for c in clauses if c.strip()]
            if len(clauses) >= 2:
                result = []
                curr = ''
                for c in clauses:
                    if not curr:
                        curr = c
                    elif len(curr) + len(c) + 1 <= max_chars:
                        curr += ', ' + c
                    else:
                        result.append(curr)
                        curr = c
                if curr:
                    result.append(curr)
                return result

            return [b]

        if re.search(r'\|{2,}|\|\s*\|\s*\|', text):
            raw_parts = [clean(p) for p in re.split(r'\s*\|{2,}\s*|\s*\|\s*\|\s*\|\s*', text) if p.strip()]
            parts = []
            for p in raw_parts:
                if p and re.search(r'\w', p) and len(p.strip()) > 2:
                    if len(p) > 125:
                        parts.extend(_subsplit_long_bubble(p, max_chars=125))
                    else:
                        parts.append(p)
            return dedupe_greetings(parts[:12])

        clean_text = clean(text)
        if len(clean_text) <= 45:
            return dedupe_greetings([clean_text]) if clean_text and re.search(r'\w', clean_text) else []

        # 1. Separar por saltos de línea explícitos si existen
        raw_lines = [clean(l) for l in re.split(r'\n+', text) if l.strip()]
        if len(raw_lines) >= 2:
            expanded = []
            for l in raw_lines:
                expanded.extend(_subsplit_long_bubble(l, max_chars=125))
            return dedupe_greetings(expanded[:6])

        # 2. Separar por oraciones gramaticales
        sentences = re.split(r'(?<=[.!?])\s+(?=[A-ZÁÉÍÓÚÜÑA-Za-z¿¡])', text)
        sentences = [clean(s) for s in sentences if s.strip() and re.search(r'\w', s)]

        if len(sentences) <= 1:
            return dedupe_greetings(_subsplit_long_bubble(clean_text, max_chars=125))

        # 3. Separación natural: Saludo / Cuerpo / Pregunta final
        greetings_starts = ("hola", "holaa", "buenas", "buenos", "hey", "claro", "de una", "con gusto", "por supuesto", "listo", "perfecto")
        first_is_greeting = any(sentences[0].lower().startswith(g) for g in greetings_starts)

        raw_bubbles = []
        if len(sentences) == 2:
            raw_bubbles = [sentences[0], sentences[1]]
        elif len(sentences) == 3:
            if first_is_greeting:
                raw_bubbles = [sentences[0], sentences[1], sentences[2]]
            else:
                raw_bubbles = [f"{sentences[0]} {sentences[1]}", sentences[2]]
        else:
            if first_is_greeting:
                b1 = sentences[0]
                b2 = " ".join(sentences[1:-1])
                b3 = sentences[-1]
                raw_bubbles = [b1, b2, b3]
            else:
                mid = len(sentences) // 2
                b1 = " ".join(sentences[:mid])
                b2 = " ".join(sentences[mid:])
                raw_bubbles = [b1, b2]

        final_bubbles = []
        for b in raw_bubbles:
            if len(b) > 125:
                final_bubbles.extend(_subsplit_long_bubble(b, max_chars=125))
            else:
                final_bubbles.append(b)

        return dedupe_greetings(final_bubbles)
    
    # ─── Admin Commands ─────────────────────────────────────────────────────────
    
    async def _process_admin_feedback(self, chat_id: str, text: str,
                                      clinic: Dict) -> Optional[List[str]]:
        """
        Detecta si el admin está:
        A) Dando feedback sobre una conversación revisada
        B) Respondiendo a la pregunta de disponibilidad que Firby le hizo
        C) Usando el puente — enviando un mensaje directo a un paciente activo
        """
        text_low = text.lower().strip()

        # ── C. PUENTE — admin envía mensaje directo a un paciente ────────────────
        # Patrones detectados:
        #   "envíale: hola, ¿cómo estás?"
        #   "mándale este mensaje: ya podemos atenderte"
        #   "dile a este cliente: confirmada la cita"
        #   "escríbele: te esperamos el martes"
        BRIDGE_PATTERNS = [
            "envíale:", "enviale:", "envíale ", "envialessto",
            "mándale:", "mandale:", "mándale este mensaje:",
            "dile:", "dile a este cliente:", "dile que:",
            "escríbele:", "escribele:", "escríbele este:",
            "envía:", "envia:", "manda:", "pásale:", "pasale:",
            "respóndele:", "respondele:", "contéstale:", "contestale:",
        ]
        reviewed = getattr(self, '_last_reviewed_chat', None)

        _bridge_prefix = next(
            (p for p in BRIDGE_PATTERNS if text_low.startswith(p.lower())),
            None
        )
        # También detectar patrón "envíale [mensaje]" sin dos puntos
        if not _bridge_prefix:
            for p in ["envíale ", "enviále ", "mándale ", "mandale ", "dile ", "escríbele "]:
                if text_low.startswith(p):
                    _bridge_prefix = p
                    break

        if _bridge_prefix and reviewed:
            # Extraer el mensaje que va al paciente
            raw_bridge_msg = text[len(_bridge_prefix):].strip().strip('"').strip("'").strip()

            if raw_bridge_msg:
                try:
                    # Obtener nombre del paciente para el log
                    patient_name = ""
                    try:
                        with db._conn() as c:
                            row = c.execute("SELECT name FROM patients WHERE chat_id=?",
                                            (reviewed,)).fetchone()
                            if row:
                                patient_name = row["name"] or ""
                    except Exception:
                        pass

                    # Enviar el mensaje como si fuera Firby (no el admin)
                    await self._send_message(reviewed, raw_bridge_msg)

                    # Guardarlo en el historial como si Firby lo hubiera dicho
                    db.save_message(reviewed, "assistant", raw_bridge_msg)

                    name_str = patient_name or f"cliente {reviewed[-6:]}"
                    log.info(f"[bridge] admin→{reviewed}: {raw_bridge_msg[:60]}")
                    return [
                        f"Listo, le mandé eso a {name_str}",
                        "Mensaje enviado: " + raw_bridge_msg[:120] + ("..." if len(raw_bridge_msg) > 120 else ""),
                        "Quedó guardado en el historial como si lo hubiera dicho Firby"
                    ]

                except Exception as e:
                    log.error(f"[bridge] error: {e}")
                    return [f"No pude enviar el mensaje: {e}"]
            else:
                return [
                    "No entendí el mensaje a enviar",
                    "Formato: envíale: tu mensaje aquí"
                ]

        elif _bridge_prefix and not reviewed:
            return [
                "Primero abre una conversación con /chat [id]",
                "Así sé a qué cliente enviarle el mensaje"
            ]

        # ── B. Respuesta de disponibilidad del admin ──────────────────────────
        # Firby le preguntó al admin su disponibilidad; él responde
        AVAILABILITY_RESPONSE_SIGNALS = [
            "lunes", "martes", "miercoles", "miércoles", "jueves", "viernes",
            "sabado", "sábado", "esta semana", "proxima", "próxima",
            "manana", "mañana", "hoy", "pm", "am", "9am", "10am", "11am",
            "disponible", "libre", "puedo", "tengo espacio",
        ]
        is_availability_response = sum(
            1 for s in AVAILABILITY_RESPONSE_SIGNALS if s in text_low
        ) >= 2 and len(text) > 10

        if is_availability_response:
            # Verificar si hay un paciente esperando respuesta de disponibilidad
            pending_patient = getattr(self, '_availability_pending_patient', None)
            if pending_patient:
                # Retransmitir la disponibilidad al paciente
                patient_name = ""
                try:
                    with db._conn() as c:
                        row = c.execute("SELECT name FROM patients WHERE chat_id=?",
                                        (pending_patient,)).fetchone()
                        if row:
                            patient_name = row["name"] or ""
                except Exception:
                    pass

                patient_greeting = f"Hola{f' {patient_name}' if patient_name else ''}! "
                patient_msg = f"{patient_greeting}Ya me confirmaron. {text}"

                try:
                    await self._send_message(pending_patient, patient_msg)
                    self._availability_pending_patient = None
                    return [
                        f"Listo, le acabo de confirmar la disponibilidad al paciente."
                    ]
                except Exception as e:
                    log.warning(f"[calendar] error retransmitiendo: {e}")

        # ── A. Instrucción directa del admin (sin conversación activa) ──────────
        # El admin puede decir "no le digas X", "siempre di Y", "cuando pregunten
        # por precio diles que..." en cualquier momento y se guarda como regla.
        text_low = text.lower().strip()

        DIRECT_RULE_SIGNALS = [
            "no le digas", "no digas", "nunca digas", "nunca le digas",
            "siempre di", "siempre dile", "siempre que", "cuando pregunten",
            "cuando el cliente", "cuando la cliente", "cuando alguien",
            "en vez de decir", "en lugar de", "mejor di", "mejor dile",
            "desde ahora", "de ahora en adelante", "para los clientes",
            "a los pacientes", "no menciones", "evita decir", "evita mencionar",
            "quiero que digas", "quiero que le digas", "diles que",
            "respóndeles", "respondeles", "si te preguntan por",
        ]
        is_direct_rule = any(s in text_low for s in DIRECT_RULE_SIGNALS) and len(text) > 15

        if is_direct_rule and not reviewed:
            # Regla directa — guardar sin contexto de conversación
            try:
                extraction_prompt = f"""El dueño de un negocio está dando una instrucción directa a su asistente virtual Firby sobre cómo debe comportarse con los clientes.

INSTRUCCIÓN DEL DUEÑO:
"{text}"

Extrae una regla clara y accionable de esta instrucción.
Responde SOLO con JSON válido, sin texto adicional:
{{
  "rule": "la regla en lenguaje claro y directo, como una instrucción para Firby",
  "example_bad": "cómo NO responder (si se puede inferir del contexto)",
  "example_good": "cómo SÍ responder (si se puede inferir del contexto)",
  "category": "tone|product|closing|objection|flow|general",
  "feedback_type": "instruction",
  "save_as_playbook": true,
  "trigger_text": "cuándo aplica esta instrucción, en lenguaje simple",
  "response_example": "ejemplo exacto de respuesta o secuencia de burbujas usando ||| si aplica",
  "bubble_count": 1
}}

Categorías:
- tone: cómo hablar, palabras a usar o evitar
- product: info sobre servicios o precios
- closing: cómo y cuándo cerrar hacia la cita
- objection: manejo de objeciones
- flow: orden de la conversación
- general: todo lo demás

Usa save_as_playbook=true SOLO si el dueño está enseñando un patrón reusable tipo:
- "si te saludan..."
- "cuando pregunten por..."
- "al inicio responde..."
- "primero di X y luego Y"

Si el dueño dio una forma concreta de responder, trigger_text y response_example son obligatorios.
Si menciona dos mensajes, response_example debe usar ||| entre burbujas."""

                raw, _ = await asyncio.wait_for(
                    llm_engine.complete(
                        [{"role": "user", "content": extraction_prompt}],
                        model_tier="fast", temperature=0.1, max_tokens=250, use_cache=False
                    ),
                    timeout=10.0
                )

                import re as _re
                m = _re.search(r'\{[\s\S]+\}', raw.strip())
                if m:
                    parsed       = json.loads(m.group(0))
                    rule         = parsed.get("rule", "")
                    example_bad  = parsed.get("example_bad", "")
                    example_good = parsed.get("example_good", "")
                    category     = parsed.get("category", "general")
                    save_as_playbook = bool(parsed.get("save_as_playbook"))
                    trigger_text = (parsed.get("trigger_text", "") or "").strip()
                    response_example = (parsed.get("response_example", "") or "").strip()
                    bubble_count = int(parsed.get("bubble_count", 1) or 1)

                    if rule:
                        rule_id = db.save_trust_rule(
                            category=category, rule=rule,
                            example_bad=example_bad, example_good=example_good,
                            weight=2.5,
                        )
                        playbook_id = 0
                        if db and save_as_playbook and trigger_text and response_example:
                            playbook_id = db.save_behavior_playbook(
                                trigger_text=trigger_text,
                                response_example=response_example,
                                category=category,
                                instruction=rule,
                                bubble_count=bubble_count,
                                weight=3.0,
                            )
                        cat_labels = {
                            "objection":"Objeciones","tone":"Tono","closing":"Cierre",
                            "product":"Servicios","flow":"Flujo","general":"General"
                        }
                        ejemplo_line = (f'\nEjemplo correcto: "{example_good}"' if example_good else "")
                        playbook_line = (
                            f'\nPlaybook #{playbook_id}: si pasa "{trigger_text}", responde parecido a "{response_example}"'
                            if playbook_id else ""
                        )
                        return [
                            "Entendido, lo guardo ahora mismo",
                            f'Carpeta de confianza #{rule_id} [{cat_labels.get(category,"General")}]:\n"{rule}"' + ejemplo_line,
                            "Aplico esto en todas las conversaciones desde ya. Ver todas las reglas: /reglas" + playbook_line
                        ]
            except Exception as e:
                log.warning(f"[trust_rule] Error procesando instrucción directa: {e}")
            return None

        # ── B. Feedback sobre conversación revisada ───────────────────────────
        if not reviewed:
            return None

        # Detectar si el texto es feedback (no un comando ni saludo)
        FEEDBACK_SIGNALS = [
            "debió", "deberia", "debería", "tendría", "tenia que", "faltó",
            "falto", "muy bien", "estuvo bien", "estuvo mal", "mal manejado",
            "bien manejado", "mejor si", "en vez de", "en lugar de",
            "cuando el paciente", "cuando la paciente", "hubiera",
            "le faltó", "pudo haber", "hay que", "siempre que",
            "nunca", "siempre", "próxima vez", "la próxima",
        ]
        is_feedback = any(s in text_low for s in FEEDBACK_SIGNALS)

        if not is_feedback and len(text) < 40:
            return None
        if not is_feedback and not any(
            kw in text_low for kw in ["precio", "cita", "objecion", "respuesta",
                                       "firby", "paciente", "cliente", "cerrar",
                                       "agendar", "tono", "dijo", "respondio", "respondió"]
        ):
            return None

        # Obtener el contexto de la conversación revisada
        context_msgs = db.get_patient_conversation(reviewed, limit=20)
        context_str = "\n".join(
            f"{m['role']}: {m['content'][:100]}"
            for m in context_msgs[-10:]
        )

        # Usar LLM para extraer la regla aprendida
        try:
            extraction_prompt = f"""El dueño de una clínica estética está dando feedback sobre cómo su asistente virtual Firby manejó una conversación.

CONVERSACIÓN REVISADA (fragmento):
{context_str}

FEEDBACK DEL DUEÑO:
"{text}"

Extrae la regla de comunicación aprendida y devuelve SOLO este JSON:
{{
  "category": "objection|tone|closing|product|flow|general",
  "rule": "regla clara en una oración, tercera persona",
  "example_bad": "ejemplo de lo que NO hacer (opcional, máx 60 chars)",
  "example_good": "ejemplo de lo que SÍ hacer (opcional, máx 60 chars)",
  "feedback_type": "correction|praise|instruction"
}}

Ejemplos de categorías:
- objection: manejo de "es caro", "lo pienso", "no sé si sirva"
- tone: cómo hablar, qué palabras usar o evitar
- closing: cómo y cuándo agendar la valoración
- product: información sobre tratamientos específicos
- flow: orden de la conversación, cuándo preguntar qué
- general: todo lo demás"""

            raw, _ = await asyncio.wait_for(
                llm_engine.complete(
                    [{"role": "user", "content": extraction_prompt}],
                    model_tier="fast",
                    temperature=0.2,
                    max_tokens=300,
                    use_cache=False
                ),
                timeout=10.0
            )

            raw = raw.strip()
            json_str = None
            import re as _re
            m = _re.search(r'\{[\s\S]+\}', raw)
            if m:
                json_str = m.group(0)

            if not json_str:
                raise ValueError("No JSON found")

            parsed = json.loads(json_str)
            category     = parsed.get("category", "general")
            rule         = parsed.get("rule", "")
            example_bad  = parsed.get("example_bad", "")
            example_good = parsed.get("example_good", "")
            fb_type      = parsed.get("feedback_type", "instruction")

            if not rule:
                raise ValueError("Empty rule")

            # Guardar en trust_folder
            trust_weight = 2.0 if fb_type == "praise" else 3.0
            rule_id = db.save_trust_rule(
                category=category,
                rule=rule,
                example_bad=example_bad,
                example_good=example_good,
                weight=trust_weight,
            )

            # Guardar el feedback también
            db.save_feedback(
                patient_chat_id=reviewed,
                feedback_text=text,
                feedback_type=fb_type,
                context=context_str,
                admin_chat_id=chat_id
            )

            # Limpiar la conversación bajo revisión
            self._last_reviewed_chat = None

            cat_labels = {
                "objection": "Objeciones", "tone": "Tono", "closing": "Cierre",
                "product": "Tratamientos", "flow": "Flujo", "general": "General"
            }
            cat_label = cat_labels.get(category, "General")

            if fb_type == "praise":
                return [
                    f"Gracias, guardado como referencia de lo que funciona bien.",
                    f"Carpeta de confianza #{rule_id} [{cat_label}]:\n\"{rule}\""
                ]
            else:
                return [
                    f"Entendido. Lo aprendo ahora mismo.",
                    f"Carpeta de confianza #{rule_id} [{cat_label}]:\n\"{rule}\""
                    + (f"\nEjemplo: \"{example_good}\"" if example_good else ""),
                    "Desde ahora aplico esto en cada conversación. Para ver todo lo aprendido: /reglas"
                ]

        except Exception as e:
            log.warning(f"[feedback] Error extrayendo regla: {e}")
            # Guardar el feedback en crudo aunque no se extrajo la regla
            try:
                db.save_feedback(
                    patient_chat_id=reviewed,
                    feedback_text=text,
                    feedback_type="instruction",
                    context="",
                    admin_chat_id=chat_id
                )
                self._last_reviewed_chat = None
            except Exception:
                pass
            return [
                "Guardé tu feedback, aunque no pude procesarlo automáticamente.",
                "Puedes ver todo el feedback con /reglas y editarlo desde ahí."
            ]

    async def _restart_setup(self, chat_id: str) -> List[str]:
        """Reinicia el setup."""
        db.update_clinic(
            setup_done=0,
            setup_step="idle",
            setup_buffer={}
        )
        return await self._handle_setup(chat_id, "", db.get_clinic())
    

    # ══════════════════════════════════════════════════════════════════════════
    # V6.0 — COMANDOS NUEVOS
    # ══════════════════════════════════════════════════════════════════════════

    def _validate_services(self, raw: list) -> List[str]:
        """
        Valida que una lista de strings sean nombres de servicios reales.
        Filtra frases, oraciones, textos personales y garbage.
        """
        if not raw or not isinstance(raw, list):
            return []

        # Palabras que indican que NO es un servicio
        NOT_SERVICE_SIGNALS = {
            "puedes", "puede", "podrias", "llama", "llamame", "soy", "mi",
            "busca", "google", "facebook", "instagram", "http", "www",
            "necesito", "quiero", "tengo", "favor", "gracias", "por"
        }
        # Categorías de servicios estéticos válidas
        AESTHETIC_HINTS = {
            "botox", "relleno", "laser", "peeling", "facial", "corporal",
            "limpieza", "hilo", "dermapen", "radiofrecuencia", "lipolisis",
            "cavitacion", "mesoterapia", "presoterapia", "depilacion",
            "microblading", "micropigmentacion", "prp", "hifu", "toxina",
            "bichectomia", "rinoplastia", "ojeras", "vitamina", "hydrafacial",
            "masaje", "drenaje", "plasma", "nutricion", "acne", "manchas",
            "cicatriz", "poro", "colágeno", "colageno", "elastina",
        }

        valid = []
        for item in raw:
            item = str(item).strip()
            if not item or len(item) < 2:
                continue
            if len(item) > 60:
                continue  # demasiado largo para ser un nombre de servicio
            item_low = item.lower()
            # Rechazar si contiene señales de NO servicio
            if any(sig in item_low for sig in NOT_SERVICE_SIGNALS):
                log.info(f"[validate_services] rechazado: '{item}'")
                continue
            # Rechazar si parece una oración (tiene verbo conjugado al inicio)
            words = item_low.split()
            if len(words) > 6:
                continue
            valid.append(item.title())

        return valid

    def _is_synthetic_chat_id(self, chat_id: str) -> bool:
        value = (chat_id or "").strip().lower()
        if not value:
            return True
        synthetic_prefixes = (
            "qa_", "test_", "cli_", "api", "debug_", "tmp_", "sim_",
            "admin_test_", "qa-", "test-", "prod_", "audit_", "probe_",
            "admin_probe_", "prod_audit_", "owner-demo-", "wa_style_probe_",
            "tone_probe_", "prompt_probe_", "style_probe_", "owner-debug",
        )
        if value.startswith(synthetic_prefixes):
            return True
        synthetic_tokens = ("probe", "debug", "synthetic")
        if any(token in value for token in synthetic_tokens):
            return True
        if "@" not in value and not value.isdigit():
            if any(ch.isalpha() for ch in value) and ("_" in value or "-" in value):
                return True
        if value in {"status@broadcast"} or value.endswith("@newsletter"):
            return True
        return False

    def _apply_admin_output_pipeline(self, reply_text: str, chat_id: str, clinic: Dict, user_msg: str = "") -> str:
        """Aplica el plano de control del admin sobre las respuestas internas."""
        current = (reply_text or "").strip()
        if not current:
            return ""

        current = re.sub(r'\s*—\s*', ' ', current)
        current = re.sub(r'\s+', ' ', current).strip()
        current = re.sub(r'\s*\|\|\|\s*', ' ||| ', current)

        first_turn = True
        try:
            history = db.get_history(chat_id, limit=8) if db else []
            first_turn = not any((m.get("role") == "assistant") for m in (history or []))
        except Exception:
            pass

        if owner_style_controller:
            current = owner_style_controller.enforce_output(
                current,
                is_admin=True,
                first_turn=first_turn,
                chat_id=chat_id,
                clinic=clinic,
                user_msg=user_msg,
            )

        bubbles = [part.strip() for part in re.split(r'\s*\|\|\|\s*', current or "") if part.strip()]
        normalized: List[str] = []
        for bubble in bubbles:
            if bubble and bubble[0].islower():
                bubble = bubble[0].upper() + bubble[1:]
            normalized.append(bubble)
        current = " ||| ".join(normalized) if normalized else current

        return current or "Entendido."

    async def _handle_whatsapp_setup_flow(self, chat_id: str, text: str,
                                           clinic: Dict) -> Optional[List[str]]:
        """
        Maneja el flujo conversacional de configuración de WhatsApp.
        Se activa cuando hay un wa_flow activo en setup_buffer.
        Retorna burbujas si está manejando el flujo, None si no aplica.
        """
        buf = clinic.get("setup_buffer", {})
        if isinstance(buf, str):
            try: buf = json.loads(buf) if buf else {}
            except Exception: buf = {}

        wa_flow = buf.get("wa_flow", "")
        if not wa_flow:
            return None

        text_low = text.lower().strip()

        # ── Paso 1: preguntamos tipo (nuevo o existente) ──────────────────────
        if wa_flow == "asking_type":
            is_existing = any(w in text_low for w in [
                "1", "tengo", "tengo uno", "existente", "ya tengo",
                "tengo numero", "tengo el", "mio", "mío", "si tengo"
            ])
            is_new = any(w in text_low for w in [
                "2", "nuevo", "quiero uno", "no tengo", "necesito",
                "sin numero", "quiero nuevo"
            ])

            if is_new:
                # Flujo nuevo número — escalar a Omni/Santiago
                buf["wa_flow"] = "new_number_requested"
                db.update_clinic(setup_buffer=buf)

                # Notificar a Santiago via Firby Omni
                asyncio.create_task(
                    self._notify_omni(
                        event="new_whatsapp_number_requested",
                        clinic_name=clinic.get("name", ""),
                        chat_id=chat_id,
                        details=f"El admin de {clinic.get('name','')} necesita un número nuevo de WhatsApp."
                    )
                )
                return [
                    "Perfecto. Para conseguirte un número nuevo de WhatsApp Business "
                    "necesito coordinarlo.",
                    "Ya le avisé a nuestro equipo. Te contactarán en menos de 24 horas "
                    "para activar tu número. Mientras tanto puedo seguir funcionando por "
                    "Telegram."
                ]

            elif is_existing:
                buf["wa_flow"] = "guide_step_1"
                db.update_clinic(setup_buffer=buf)
                return await self._wa_guide_step(1, clinic)

            else:
                return [
                    "No entendí bien. Tienes ya un número de WhatsApp Business (1) "
                    "o quieres uno nuevo (2)?"
                ]

        # ── Pasos del guía para número existente ──────────────────────────────
        if wa_flow.startswith("guide_step_"):
            step = int(wa_flow.split("_")[-1])

            # Detectar si pegaron credenciales en cualquier paso
            wa_creds = _detect_wa_credentials(text)
            if wa_creds:
                buf["wa_flow"] = ""
                db.update_clinic(setup_buffer=buf)
                return await self._admin_connect_whatsapp(
                    chat_id, wa_creds["phone_id"], wa_creds["token"], clinic
                )

            # Confirmar que van avanzando
            CONTINUE_SIGNALS = [
                "listo", "ok", "ya", "hecho", "sí", "si", "dale",
                "siguiente", "continua", "next", "ya lo hice", "ya está"
            ]
            if any(s in text_low for s in CONTINUE_SIGNALS) or len(text_low) < 25:
                next_step = step + 1
                if next_step > 6:
                    # Ya deberían tener las credenciales
                    buf["wa_flow"] = "waiting_credentials"
                    db.update_clinic(setup_buffer=buf)
                    return [
                        "Ahora pégame los dos datos que copiaste:",
                        "WA_PHONE_ID: (el número largo de 15 dígitos)\n"
                        "WA_TOKEN: EAAxxxxx... (el token de acceso)"
                    ]
                buf["wa_flow"] = f"guide_step_{next_step}"
                db.update_clinic(setup_buffer=buf)
                return await self._wa_guide_step(next_step, clinic)

            # Pregunta o confusión — buscar en web para ayudar
            if len(text) > 20:
                search_hint = await self._wa_search_help(text)
                return [search_hint or "Cuéntame qué ves en tu pantalla y te ayudo."]

            return await self._wa_guide_step(step, clinic)

        if wa_flow == "waiting_credentials":
            wa_creds = _detect_wa_credentials(text)
            if wa_creds:
                buf["wa_flow"] = ""
                db.update_clinic(setup_buffer=buf)
                return await self._admin_connect_whatsapp(
                    chat_id, wa_creds["phone_id"], wa_creds["token"], clinic
                )
            return [
                "Aún no veo las credenciales. Necesito los dos datos:",
                "WA_PHONE_ID: [número de 15 dígitos]\n"
                "WA_TOKEN: EAAxxxxx..."
            ]

        return None

    async def _wa_guide_step(self, step: int, clinic: Dict) -> List[str]:
        """
        Guía paso a paso para conectar WhatsApp Business.
        Lenguaje 100% humano — sin jerga técnica.
        """
        clinic_name = clinic.get("name", "tu clínica")

        steps = {
            1: [
                "Primero abre este link en tu computador (no en el celular):",
                "developers.facebook.com/apps\n\n"
                "Si no tienes cuenta, créala con el mismo correo de tu Facebook Business. "
                "Cuando estés adentro, dime 'listo'."
            ],
            2: [
                "Haz clic en 'Crear app' (botón verde arriba a la derecha).",
                "Te va a preguntar el tipo de app. Selecciona 'Business' y sigue. "
                "Ponle el nombre que quieras, por ejemplo 'WhatsApp Clínica'. "
                "Cuando termines de crearla, dime 'listo'."
            ],
            3: [
                "Dentro de tu nueva app, busca el producto 'WhatsApp' en la lista "
                "y haz clic en 'Configurar'.",
                "Te va a pedir que conectes una cuenta de WhatsApp Business. "
                "Si no tienes una, te la crea Meta automáticamente. Acepta. "
                "Cuando lo hayas hecho, dime 'listo'."
            ],
            4: [
                "Ahora estás en el panel de WhatsApp. Busca la sección "
                "'Configuración de la API' o 'API Setup'.",
                "Ahí verás un número de prueba de Meta. Más abajo hay un campo "
                "que dice 'Número de teléfono' — ahí agrega tu número de "
                f"{clinic_name}. Cuando lo hayas agregado, dime 'listo'."
            ],
            5: [
                "En esa misma pantalla vas a ver dos datos importantes.",
                "Cópialos y guárdalos en un bloc de notas:\n\n"
                "1. Phone Number ID — un número largo de 15 dígitos\n"
                "2. Token de acceso — empieza con 'EAA...'\n\n"
                "Para el token, busca la opción de generar un token permanente "
                "(no temporal). Cuando los tengas, dime 'listo'."
            ],
            6: [
                "Perfecto, ya casi.",
                "Pégame aquí los dos datos que copiaste así:\n\n"
                "WA_PHONE_ID: [el número de 15 dígitos]\n"
                "WA_TOKEN: EAAxxxxx...\n\n"
                "Yo me encargo del resto."
            ]
        }

        return steps.get(step, steps[6])

    async def _wa_search_help(self, question: str) -> str:
        """
        Busca en web para responder una duda específica del flujo de WhatsApp.
        """
        try:
            query = f"Meta WhatsApp Business API setup {question[:60]} 2024"
            result = await self.search.search(query)
            if result:
                # Simplificar el resultado para el admin
                try:
                    prompt = (
                        f"El admin de una clínica está configurando WhatsApp Business API "
                        f"y tiene esta duda: '{question}'\n\n"
                        f"Esto encontré en internet:\n{result[:600]}\n\n"
                        f"Explícale en máximo 2 oraciones, en lenguaje simple, sin jerga técnica."
                    )
                    answer, _ = await asyncio.wait_for(
                        llm_engine.complete(
                            [{"role": "user", "content": prompt}],
                            model_tier="fast", temperature=0.3, max_tokens=150,
                            use_cache=False
                        ),
                        timeout=8.0
                    )
                    return answer.strip()
                except Exception:
                    return result[:200]
        except Exception:
            pass
        return ""

    async def _notify_omni(self, event: str, clinic_name: str,
                           chat_id: str, details: str):
        """
        Envía una notificación a Firby Omni (instancia de Santiago).
        Usa httpx async si está disponible, cae a la función sync como fallback.
        """
        omni_url = os.getenv("OMNI_URL", "")
        omni_key = os.getenv("OMNI_KEY", "")
        if not omni_url or not omni_key:
            # Fallback: notificar directo al chat de Santiago
            santiago_chat = os.getenv("SANTIAGO_CHAT_ID", "")
            if santiago_chat:
                msg = f"Evento [{event}] en {clinic_name}: {details}"
                try:
                    await self._send_message(santiago_chat, msg)
                except Exception:
                    pass
            return
        try:
            async with httpx.AsyncClient(timeout=5.0) as c:
                await c.post(f"{omni_url}/omni/event",
                    headers={"X-Omni-Key": omni_key, "Content-Type": "application/json"},
                    json={
                        "event":      event,
                        "clinic":     clinic_name,
                        "chat_id":    chat_id,
                        "details":    details,
                        "severity":   "info" if event not in ("queja_paciente", "error_procesamiento") else "warning",
                        "timestamp":  datetime.now().isoformat()
                    })
        except Exception as e:
            log.debug(f"[omni] notify silenced: {e}")

    def _try_local_persona_change(self, text_low: str, persona: Dict,
                                  clinic: Dict) -> Optional[List[str]]:
        """
        Detecta cambios de personalidad simples SIN necesitar el LLM.
        Retorna lista de burbujas si se pudo resolver localmente, None si no.
        """
        changes = {}
        msgs = []

        # Calidez
        if re.search(r'(mas|m[aá]s|m[aá]ximo|sube|aumenta|100|alta?)\s*(calidez|c[aá]lid[ao]|cariñ|warm)', text_low):
            val = 1.0 if "100" in text_low or "maximo" in text_low or "máximo" in text_low else 0.9
            changes.setdefault("persona_config", {})["warmth_level"] = val
            msgs.append(f"Calidez: {int(val*100)}%")
        elif re.search(r'(menos|baja|reduce|minimal?)\s*(calidez|cariñ)', text_low):
            changes.setdefault("persona_config", {})["warmth_level"] = 0.4
            msgs.append("Calidez: 40%")

        # Formalidad
        if re.search(r'(mas|m[aá]s|muy|sube)\s*(formal|profesional)', text_low):
            val = 0.9 if "muy" in text_low else 0.8
            changes.setdefault("persona_config", {})["formality_level"] = val
            msgs.append(f"Formalidad: {int(val*100)}%")
        elif re.search(r'(menos|baja|poco|informal|relajad)', text_low):
            changes.setdefault("persona_config", {})["formality_level"] = 0.25
            msgs.append("Formalidad: 25%")

        # Cambio de nombre del agente
        m = re.search(r'(?:cambia|llama(?:la|se)?|nombre)[^\w]+(a|como)\s+([A-Z][a-z]+)', text_low, re.IGNORECASE)
        if not m:
            m = re.search(r'(?:se llame|se llama|nombre es|nombre a)\s+([A-Z][a-z]+)', text_low, re.IGNORECASE)
            if m:
                nuevo_nombre = m.group(1).strip().title()
                changes.setdefault("persona_config", {})["name"] = nuevo_nombre
                msgs.append(f"Nombre cambiado a {nuevo_nombre}")
        elif m:
            nuevo_nombre = m.group(2).strip().title()
            changes.setdefault("persona_config", {})["name"] = nuevo_nombre
            msgs.append(f"Nombre cambiado a {nuevo_nombre}")

        if not changes:
            return None  # No se pudo resolver localmente

        # Aplicar cambios
        changes = self._apply_persona_merge(changes, clinic)
        db.update_clinic(**changes)

        persona_new = changes.get("persona_config", {})
        agent_name = clinic.get("assistant_name") or persona_new.get("name") or persona.get("name") or "Valentina"
        if agent_name.lower() in ("firby", "lucia", "lucía"):
            agent_name = clinic.get("assistant_name") or "Valentina"
        summary = ". ".join(msgs)
        return [
            f"Listo. {summary}.",
            f"{agent_name} ya tiene la nueva configuracion."
        ]

    def _apply_persona_merge(self, changes: Dict, clinic: Dict) -> Dict:
        """Merge inteligente de persona_config con el existente."""
        if "persona_config" not in changes:
            return changes

        existing = clinic.get("persona_config", {})
        if isinstance(existing, str):
            try:
                existing = json.loads(existing) if existing else {}
            except Exception:
                existing = {}

        new_persona = dict(existing)
        new_persona.update(changes["persona_config"])
        changes["persona_config"] = new_persona
        return changes

    def _changes_summary(self, changes: Dict, clinic: Dict) -> str:
        """Genera confirmacion legible de los cambios aplicados."""
        parts = []

        for key, value in changes.items():
            if key == "persona_config":
                for pkey, pval in value.items():
                    if pkey == "name":
                        parts.append(f"Nombre cambiado a {pval}")
                    elif pkey == "formality_level":
                        pct = int(float(pval) * 100)
                        parts.append(f"Formalidad: {pct}%")
                    elif pkey == "warmth_level":
                        pct = int(float(pval) * 100)
                        parts.append(f"Calidez: {pct}%")
                    elif pkey == "tone":
                        parts.append(f"Tono: {pval}")
                    elif pkey == "forbidden_words":
                        parts.append(f"Palabras prohibidas: {', '.join(pval)}")
                    else:
                        parts.append(f"{pkey}: {pval}")
            elif key == "services":
                parts.append(f"Servicios actualizados ({len(value)} en total)")
            elif key == "phone":
                parts.append(f"Telefono: {value}")
            elif key == "name":
                parts.append(f"Nombre clinica: {value}")
            elif key == "schedule":
                parts.append("Horario actualizado")
            elif key == "address":
                parts.append(f"Direccion: {value}")
            else:
                parts.append(f"{key} actualizado")

        if parts:
            return "Listo. " + ". ".join(parts) + "."
        return "Cambios aplicados."

    
    # ─── Buffer Management ──────────────────────────────────────────────────────
    
    # ─── Busqueda Inteligente ────────────────────────────────────────────────────

    async def _smart_search(self, text: str, analysis: "MessageAnalysis",
                            clinic: Dict) -> str:
        """
        Construye la query de busqueda segun intencion y entidades extraidas.
        Busca diferente segun lo que el paciente este preguntando.
        """
        clinic_name = clinic.get("name", "")
        services    = clinic.get("services", [])
        intent      = analysis.intent
        entities    = analysis.entities
        keywords    = analysis.keywords

        # ── Precio de servicio especifico ─────────────────────────────────────
        if intent.name in ("PRICE_INQUIRY", "SERVICE_INFO"):
            # Si menciona servicios conocidos, incluirlos en la query
            mentioned_services = [
                s for s in services
                if any(kw in s.lower() for kw in keywords[:5])
            ]
            service_term = mentioned_services[0] if mentioned_services else " ".join(keywords[:2])
            query = f"{service_term} precio costo Medellin clinica estetica"

        # ── Pregunta sobre horario o ubicacion ────────────────────────────────
        elif intent.name in ("HOURS_INQUIRY", "LOCATION_INQUIRY"):
            query = f"{clinic_name} {intent.name.lower().replace('_inquiry', '')} Medellin"

        # ── Pregunta general con keywords claros ──────────────────────────────
        elif keywords:
            query = f"{' '.join(keywords[:3])} clinica estetica Colombia"

        # ── Fallback: buscar el texto completo ────────────────────────────────
        else:
            query = f"{text[:80]} clinica estetica Medellin"

        log.info(f"[search] intent={intent.name} query={query!r}")
        return await self.search.search(query, context=clinic_name)

    # ─── Buffer Inteligente ──────────────────────────────────────────────────────
    
    def _calc_smart_wait(self, chat_id: str, text: str) -> float:
        """
        Calcula tiempo de espera inteligente. No es random fijo.
        Analiza el contexto real para decidir cuanto esperar.

        Logica:
          - Setup flow (respondiendo preguntas directas) (3-8s)
          - Mensaje muy corto (si/no/ok/dato puntual)    (3-10s)
          - Respuesta corta (1 dato, una oracion)        (5-15s)
          - Mensaje normal (1-2 oraciones)               (9-22s)
          - Mensaje largo (parrafo, varias preguntas)    (16-40s)
          - Si Firby acaba de preguntar algo (-40%) del tiempo base
        
        Maximo absoluto: 55s
        """
        text = text.strip()
        chars = len(text)
        
        # ── Leer contexto de la BD ─────────────────────────────────────────────
        try:
            clinic = db.get_clinic()
            is_setup = not clinic.get("setup_done")
            history = db.get_history(chat_id, limit=3)
            
            # Demo mode: siempre rápido para no perder al prospecto
            if Config.DEMO_MODE:
                if chars <= 12:
                    return round(random.uniform(2.0, 4.5), 1)
                elif chars <= 60:
                    return round(random.uniform(3.0, 7.0), 1)
                else:
                    return round(random.uniform(5.0, 10.0), 1)

            # Setup: siempre rapido — el usuario responde preguntas directas cortas
            if is_setup:
                if chars < 60:
                    return round(random.uniform(3.0, 7.0), 1)
                return round(random.uniform(5.0, 11.0), 1)
            
            if not history and _is_greeting_only(text):
                cfg_idle = getattr(Config, "GREETING_ONLY_IDLE_SECONDS", 3.5)
                if cfg_idle > 10.0:
                    return float(cfg_idle)
                return round(random.uniform(2.5, 4.5), 1)

            # Ver si Firby acaba de hacer una pregunta al usuario
            last_bot = next(
                (m for m in reversed(history) if m["role"] == "assistant"), None
            )
            bot_asked = False
            if last_bot:
                bot_content = last_bot.get("content", "").lower()
                # Pregunta directa: tiene "?" o palabras tipicas de solicitud de dato
                bot_asked = "?" in bot_content or any(
                    w in bot_content for w in [
                        "cual", "como", "cuando", "tienes", "nombre", "telefono",
                        "servicio", "fecha", "hora", "confirmas", "dime"
                    ]
                )
        except Exception:
            is_setup = False
            bot_asked = False
            history = []
        
        # ── Rango base segun longitud del texto ───────────────────────────────
        # Muy corto: "si", "no", "ok", "dale", numero, nombre
        if chars <= 12:
            lo, hi = 3.0, 9.0
        # Corto: dato simple, respuesta directa
        elif chars <= 40:
            lo, hi = 5.0, 14.0
        # Oracion normal
        elif chars <= 100:
            lo, hi = 9.0, 22.0
        # Parrafo
        elif chars <= 220:
            lo, hi = 16.0, 35.0
        # Mensaje largo con varias preguntas/contexto
        else:
            lo, hi = 22.0, 50.0
        
        # Si el usuario terminó de preguntar con '?' -> responder con delay natural (3.5s - 5.5s)
        user_asked = text.strip().endswith("?") or "?" in text
        if user_asked and not is_setup:
            lo = round(random.uniform(3.0, 4.5), 1)
            hi = round(random.uniform(5.0, 6.5), 1)
        elif bot_asked:
            lo = max(3.0, lo * 0.55)
            hi = max(8.0, hi * 0.60)
        
        # Nunca superar 55s
        hi = min(hi, 55.0)
        
        return round(random.uniform(lo, hi), 1)
    
    async def enqueue_message(
        self,
        chat_id: str,
        text: str,
        urgent: bool = False,
        message_id: str = "",
        route: Optional[Dict[str, Any]] = None,
        attachments: Optional[List[Dict[str, Any]]] = None,
    ):
        """Encola mensaje con buffer inteligente basado en contexto real."""
        attachments = attachments or []

        # ── Audio Transcription Failure Guard (Fix #81) ──────────────────────
        t_clean = text.strip()
        if t_clean in ["[no pude escuchar, puedes escribirlo?]", "[no se pudo transcribir el audio]"] or t_clean.startswith("[no pude escuchar"):
            await self._send_bubbles(chat_id, ["Recibí tu nota de voz pero no se escuchó claramente. ¿Podrías escribir tu consulta por acá? 🙏"], message_id=message_id, route=route, user_text=t_clean)
            return

        # ── Commands: process inline (no buffer needed for slash commands)
        text_cmd = text.strip().lower()
        first_token = text_cmd.split()[0] if text_cmd.startswith("/") else ""
        known_cmds = {
            "/config", "/citas", "/simular", "/ayuda", "/help", "/estado",
            "/directa", "/menu", "/2am", "/reset", "/salir", "/reanudar",
            "/pausar", "/token", "/vincular-agenda", "/telegram", "/slack",
            "/gmail", "/whatsapp2", "/modo", "/training"
        }
        if first_token in known_cmds:
            try:
                from src.firby.admin.commands import get_command_handler
                instance_id = getattr(self, "_instance_id", "default")
                clinic = db.get_clinic()
                admin_ids = _parse_admin_ids(clinic.get("admin_chat_ids", []))
                is_admin = (chat_id in admin_ids or db.get_admin(chat_id) is not None)
                cmd_handler = get_command_handler(instance_id)
                result = await cmd_handler.handle(chat_id, text.strip(), is_admin=is_admin, clinic=clinic, db=db)
                if result:
                    await self._send_bubbles(chat_id, result, message_id="", route=route, user_text=text.strip())
                    return
            except Exception as e:
                log.warning(f"[command] error: {e}")
            # If command not recognized, let it pass to process_message as normal text
            pass

        # ── MODO SIMULACIÓN ──────────────────────────────────────────────────
        if self.simulator and self.simulator.is_simulating(chat_id):
            bubbles = await self.simulator.handle_step(chat_id, text)
            if bubbles:
                await self._send_bubbles(chat_id, bubbles, message_id=message_id, route=route, user_text=text.strip())
            return

        route = self._resolve_route(chat_id, route)
        platform = _route_platform(route)
        key = _buffer_key(chat_id, route)
        is_wa = platform == "whatsapp" and bool(Config.WHATSAPP_BRIDGE_URL)

        # ── Fire /read con delay natural — tarea completamente independiente ──────
        # Separada del buffer para que nunca interfiera con el flush.
        # read_delay simula el tiempo que tarda una persona en leer antes de marcar azul.
        if is_wa and message_id:
            chars = len(text.strip())
            is_demo = Config.DEMO_MODE
            if   chars <= 8:   rd_lo, rd_hi = 0.8, 2.0
            elif chars <= 30:  rd_lo, rd_hi = 1.2, 3.5
            elif chars <= 80:  rd_lo, rd_hi = 2.5, 6.0
            elif chars <= 200: rd_lo, rd_hi = 4.0, 10.0
            else:              rd_lo, rd_hi = 6.0, 15.0
            if is_demo:
                rd_lo *= 0.35; rd_hi *= 0.35
            read_delay = round(random.uniform(rd_lo, rd_hi), 1)

            async def _fire_read(mid: str, delay: float):
                await asyncio.sleep(delay)
                try:
                    async with httpx.AsyncClient(timeout=4.0) as hx:
                        await hx.post(
                            f"{Config.WHATSAPP_BRIDGE_URL}/read",
                            json={"to": chat_id, "messageId": mid}
                        )
                except Exception:
                    pass

            asyncio.create_task(_fire_read(message_id, read_delay))

        if urgent:
            log.info(f"Urgente [{chat_id[:8]}]: bypass buffer")
            if key in self._pending_buffers:
                task = self._pending_buffers[key].get("task")
                if task and not task.done():
                    task.cancel()
                prev_entry = self._pending_buffers.pop(key, {})
                prev = " ".join(prev_entry.get("messages", []))
                attachments = prev_entry.get("attachments", []) + attachments
                combined = (prev + " " + text).strip() if prev else text
            else:
                combined = text
            bubbles = await self.process_message(chat_id, combined, attachments=attachments, route=route)
            await self._send_bubbles(chat_id, bubbles, message_id="", route=route, user_text=combined)  # read ya disparado arriba
            return

        # Buffer normal — lógica original intacta
        if key in self._pending_buffers:
            task = self._pending_buffers[key].get("task")
            if task and not task.done():
                task.cancel()
            if text:
                self._pending_buffers[key]["messages"].append(text)
            self._pending_buffers[key]["attachments"].extend(attachments)
        else:
            self._pending_buffers[key] = {
                "chat_id": chat_id,
                "messages": [text] if text else [],
                "attachments": list(attachments),
                "task": None,
                "message_id": message_id,
                "route": route,
            }

        wait_seed = text or " ".join(att.get("filename", "") for att in attachments) or "archivo"
        wait = self._calc_smart_wait(chat_id, wait_seed)

        async def delayed():
            await asyncio.sleep(wait)
            await self._flush_buffer(key)

        task = asyncio.create_task(delayed())
        self._pending_buffers[key]["task"] = task

        n = len(self._pending_buffers[key]["messages"])
        log.info(f"buffer [{platform}:{chat_id[:8]}] msg #{n}, flush en {wait:.1f}s")
    
    async def _flush_buffer(self, key: str):
        """Vacía el buffer y procesa mensajes."""
        entry = self._pending_buffers.pop(key, None)
        if not entry:
            return

        chat_id = entry.get("chat_id", "")
        route = entry.get("route") or self._resolve_route(chat_id)
        combined   = " ".join(entry.get("messages", []))
        message_id = entry.get("message_id", "")
        attachments = entry.get("attachments", [])
        log.info(f"flush [{key}] {len(entry.get('messages', []))} msgs")

        try:
            bubbles = await self.process_message(chat_id, combined, attachments=attachments, route=route)
            if bubbles:
                await self._send_bubbles(chat_id, bubbles, message_id=message_id, route=route, user_text=combined)
        except Exception as e:
            log.error(f"Flush error for {chat_id}: {e}", exc_info=True)
            try:
                from src.firby.utils.helpers import handle_ai_failure
                await handle_ai_failure(
                    chat_id=chat_id,
                    last_message=combined,
                    error=e,
                    send_fn=self._send_message
                )
            except Exception as e_fail:
                log.error(f"[handle_ai_failure] Failed executing error routine: {e_fail}")
    
    async def _send_bubbles(
        self,
        chat_id: str,
        bubbles: List[str],
        message_id: str = "",
        route: Optional[Dict[str, Any]] = None,
        user_text: str = "",
    ):
        """Envía burbujas con typing proporcional y pausas naturales."""
        await self._sender._send_bubbles(chat_id, bubbles, message_id, route, user_text)

    async def _send_library_media(
        self, chat_id: str, asset_id: str, route: Optional[Dict[str, Any]] = None
    ):
        """
        Resolve a [MEDIA:asset_id] tag to a real file and send it
        via the appropriate platform API (sendPhoto, sendVoice, sendDocument).
        """
        await self._sender._send_library_media(chat_id, asset_id, route)

    async def _typing_action(
        self,
        chat_id: str,
        text: str = "",
        message_id: str = "",
        route: Optional[Dict[str, Any]] = None,
    ):
        """
        Indica escribiendo... proporcional al texto que va a enviar.
        En WhatsApp Bridge también marca como leído si hay message_id.
        """
        await self._sender._typing_action(chat_id, text, message_id, route)

    async def _recording_action(
        self,
        chat_id: str,
        duration_ms: int = 4000,
        route: Optional[Dict[str, Any]] = None,
    ):
        """
        Indica grabando audio... en WhatsApp/Evolution/Telegram/Bridge.
        """
        await self._sender._recording_action(chat_id, duration_ms, route)

    def sanitize_outgoing(self, text: Optional[str]) -> Optional[str]:
        """
        Sanitiza TODO mensaje saliente antes de enviarlo.
        Previene JSON bleed, debug messages y respuestas vacías.
        """
        return self._sender.sanitize_outgoing(text)

    async def _send_audio(self, chat_id: str, audio_path: str, route: Optional[Dict[str, Any]] = None):
        """Send audio file as voice note via WhatsApp bridge."""
        if getattr(self, "_sender", None):
            await self._sender._send_audio(chat_id, audio_path, route)

    async def _send_message(self, chat_id: str, text: str, route: Optional[Dict[str, Any]] = None):
        """
        Envia mensaje al paciente/admin segun la plataforma configurada.
        Plataformas soportadas: telegram | whatsapp_cloud | evolution | whatsapp
        """
        await self._sender._send_message(chat_id, text, route)

    def _strip_emojis(self, text: str) -> str:
        """Elimina todos los emojis."""
        return self._sender._strip_emojis(text)

    async def transcribe_audio(self, file_id: str, platform: str = "telegram",
                               wa_media_id: str = None) -> str:
        """Delega transcripción a AudioHandler si está disponible."""
        if _AUDIO_HANDLER_AVAILABLE and hasattr(self, "_audio_handler"):
            return await self._audio_handler.transcribe_audio(file_id, platform, wa_media_id)
        return "[no pude escuchar, puedes escribirlo?]"
    
    def is_urgent(self, text: str) -> bool:
        """Detecta si el mensaje es urgente."""
        analysis = self.analyzer.analyze(text)
        return analysis.urgency in [UrgencyLevel.CRITICAL, UrgencyLevel.HIGH]

    def _analysis_to_dict(self, analysis: MessageAnalysis) -> Dict:
        """Convierte MessageAnalysis a dict JSON-serializable (enums -> strings)."""
        try:
            return {
                "intent": analysis.intent.name,
                "intent_confidence": analysis.intent_confidence,
                "secondary_intents": [(i.name, s) for i, s in (analysis.secondary_intents or [])],
                "sentiment": analysis.sentiment.name,
                "sentiment_score": analysis.sentiment_score,
                "urgency": analysis.urgency.name,
                "emotional_state": analysis.emotional_state,
                "is_question": analysis.is_question,
                "requires_action": analysis.requires_action,
                "requires_search": analysis.requires_search,
                "entities": analysis.entities,
                "keywords": analysis.keywords,
                "language":       analysis.language,
                "closing_score":  getattr(analysis, "closing_score", 0.0),
                "lead_temperature": getattr(analysis, "lead_temperature", "cold"),
            }
        except Exception:
            return {}
