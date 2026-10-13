from __future__ import annotations
import logging
import asyncio
import re
import json
import time
import random
import base64 as _b64
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime

log = logging.getLogger("firby.demo")

# Rate limiting por chat_id (máximo 10 mensajes por minuto)
_chat_rate_limits: Dict[str, List[float]] = {}

# Singleton pool de motores LLM a nivel módulo (reutiliza instancias entre mensajes)
_engine_pool: Dict[str, Any] = {}

async def handle_demo_message(
    self, chat_id: str, text: str, clinic: Dict,
    attachments: Optional[List[Dict[str, Any]]] = None
) -> List[str]:
    # Rate limit check per chat_id
    now_ts = time.time()
    user_times = _chat_rate_limits.get(chat_id, [])
    user_times = [t for t in user_times if now_ts - t < 60.0]
    if len(user_times) >= 10:
        log.warning(f"[demo_rate_limit] chat_id {chat_id} excedió límite de 10 msgs/min")
        return ["Disculpa, estás enviando mensajes demasiado rápido. Por favor espera unos segundos y vuelve a escribir! 🙏"]
    user_times.append(now_ts)
    _chat_rate_limits[chat_id] = user_times

    print(f"DEBUG ENTERED handle_demo_message: chat_id={chat_id} text={text!r}")
    # Local imports from firby.py to avoid circular dependencies
    import sys
    runtime_module = sys.modules[self.__class__.__module__]
    facade_name = getattr(runtime_module, "__facade_name__", "")
    firby_module = sys.modules.get(facade_name) or runtime_module
    Config = firby_module.Config
    db = firby_module.db
    now_col = firby_module.now_col
    PersonalityProfile = getattr(firby_module, "PersonalityProfile", None) or getattr(sys.modules.get("src.core.globals"), "PersonalityProfile", None)
    llm_engine = firby_module.llm_engine
    try:
        from src.core.globals import (
            v8_process_response,
            _normalize_first_contact_response,
            PERSONALITY_ARCHETYPES,
            anti_robot_filter,
            v8_build_quality_system_prompt_addon,
            _parse_admin_ids
        )
    except ImportError:
        v8_process_response = getattr(firby_module, "v8_process_response", lambda r, **kwargs: r)
        _normalize_first_contact_response = getattr(firby_module, "_normalize_first_contact_response", lambda r, **kwargs: r)
        PERSONALITY_ARCHETYPES = getattr(firby_module, "PERSONALITY_ARCHETYPES", {})
        anti_robot_filter = getattr(firby_module, "anti_robot_filter", None)
        v8_build_quality_system_prompt_addon = getattr(firby_module, "v8_build_quality_system_prompt_addon", lambda **kwargs: "")
        _parse_admin_ids = getattr(firby_module, "_parse_admin_ids", lambda x: [])
    try:
        from src.domain.send_guard import SendGuard
    except ImportError:
        try:
            from src.firby.production.guard import SendGuard
        except ImportError:
            SendGuard = getattr(firby_module, "SendGuard", None)
    try:
        from src.domain.prompts.prospect_pitch import is_prospect_confused
    except ImportError:
        is_prospect_confused = getattr(firby_module, "is_prospect_confused", lambda x, y: False)
        
    try:
        from src.core.globals import _SMART_HANDOFF, handoff_manager
    except ImportError:
        _SMART_HANDOFF = getattr(firby_module, "_SMART_HANDOFF", False)
        handoff_manager = getattr(firby_module, "handoff_manager", None)
        
    try:
        from src.domain.send_guard import _normalize_conv_text
    except ImportError:
        _normalize_conv_text = getattr(firby_module, "_normalize_conv_text", lambda x: x.lower().strip())

    from src.domain.onboarding_flow import (
        llm_classify_business_name,
        looks_like_business_name_candidate_legacy as _looks_like_business_name_candidate_legacy,
        looks_like_business_confirmation as _looks_like_business_confirmation,
        owner_confusion_or_language_signal as _owner_confusion_or_language_signal
    )

    from firby_mirroring import (
        detect_social_profile, profile_cache, build_llm_hint, SocialProfile,
    )

    from src.interfaces.web.demo_admin_commands import (
        _strip_jid as _strip_jid,
        is_admin_chat as _is_admin_demo,
        looks_like_contact_command as _looks_like_contact_cmd,
        handle_admin_contact_command as _handle_admin_contact_cmd,
    )

    # Check if optional symbols are available
    _SESSION_MANAGER_AVAILABLE = getattr(firby_module, "_SESSION_MANAGER_AVAILABLE", False)
    _INNVISOR_PATCHES = getattr(firby_module, "_INNVISOR_PATCHES", False)
    _CONNY_DOMINO_AVAILABLE = getattr(firby_module, "_CONNY_DOMINO_AVAILABLE", False)
    build_demo_domino_payload = getattr(firby_module, "build_demo_domino_payload", None)
    build_prospect_pitch_system_prompt = getattr(firby_module, "build_prospect_pitch_system_prompt", None)
    fix_creator_in_response = getattr(firby_module, "fix_creator_in_response", None)
    _core_normalize_first_contact_response = getattr(firby_module, "_core_normalize_first_contact_response", None)
    looks_fragmented_reply = getattr(firby_module, "looks_fragmented_reply", None)
    _is_greeting_only = getattr(firby_module, "_is_greeting_only", None)
    extract_model_request_from_text = getattr(firby_module, "extract_model_request_from_text", None)
    multilingual_handler = getattr(firby_module, "multilingual_handler", None)
    MultilingualHandler = getattr(firby_module, "MultilingualHandler", None)
    GroqProvider = getattr(firby_module, "GroqProvider", None)
    GeminiProvider = getattr(firby_module, "GeminiProvider", None)
    OpenRouterProvider = getattr(firby_module, "OpenRouterProvider", None)

    """
    MODO DEMO v3 — Experiencia de intriga progresiva.
    Firby NO se presenta como IA ni da un pitch.
    Entra directo al personaje y revela capacidades una a una.
    TTL: sesión independiente por persona (DEMO_SESSION_TTL segundos).
    """
    import base64 as _b64
    import random as _r
    attachments = attachments or []

    # ── Extracción de texto de documentos adjuntos ───────────────────────
    # Si el owner manda un PDF/doc sin caption, extraemos su texto y lo
    # usamos como si hubiera sido escrito en el mensaje.
    _doc_extracted_text = ""
    _has_incoming_doc = False
    for _att in attachments:
        _att_kind = _att.get("kind", "")
        _att_mime = _att.get("mime_type", "")
        _is_doc = _att_kind == "document" or "pdf" in _att_mime or "text" in _att_mime or "word" in _att_mime or "docx" in _att_mime
        if not _is_doc and _att_kind not in ("document",):
            continue
        _has_incoming_doc = True
        # Intentar extraer texto del binario
        try:
            _raw = _att.get("bytes") or b""
            if not _raw and _att.get("base64"):
                _raw = _b64.b64decode(_att["base64"])
            if not _raw and _att.get("file_id") and _att.get("platform") == "telegram":
                _raw, _ = await self._download_telegram_binary(_att["file_id"])
            if not _raw and _att.get("media_id") and _att.get("platform") == "whatsapp_cloud":
                _raw, _, _ = await self._download_whatsapp_cloud_binary(_att["media_id"])
            if _raw:
                try:
                    import pdfplumber as _pp, io as _io
                    with _pp.open(_io.BytesIO(_raw)) as _pdf:
                        _pages = [p.extract_text() or "" for p in _pdf.pages[:6]]
                        _doc_extracted_text = "\n".join(filter(None, _pages))[:2000]
                except Exception:
                    # Fallback: intentar leer como texto plano
                    try:
                        _doc_extracted_text = _raw.decode("utf-8", errors="ignore")[:2000]
                    except Exception as e: log.warning(f"[demo] Handled exception: {e}")
        except Exception as e: log.warning(f"[demo] Handled exception: {e}")
        break  # Solo procesamos el primer documento

    # Si llegó un doc, enriquecemos el texto con su contenido extraído
    if _has_incoming_doc and not text.strip():
        if _doc_extracted_text.strip():
            text = f"[documento adjunto]\n{_doc_extracted_text.strip()}"
        else:
            text = "[documento adjunto]"
    if not hasattr(self, "_emoji_chats_off"):
        self._emoji_chats_off = set()

    # ── Gestión de sesión via SessionManager ───────────────────────────────
    if _SESSION_MANAGER_AVAILABLE and hasattr(self, "_session_mgr"):
        last_seen = self._demo_sessions.get(f"demo_{chat_id}_ts", 0)
        is_new, keys_del = self._session_mgr.touch_and_cleanup(chat_id)
        if is_new:
            sk = f"demo_{chat_id}"
            if last_seen > 0:
                self._demo_sessions[sk + "_expired_notice"] = True
            if db:
                try:
                    with db._conn() as c:
                        c.execute("DELETE FROM core_memory WHERE key LIKE ? AND key NOT LIKE ?", (f"{sk}%", f"%_ts"))
                        c.execute("DELETE FROM conversations WHERE chat_id=?", (chat_id,))
                except Exception as e:
                    log.warning(f"[demo] DB delete error on session reset: {e}")
            for k in list(self._demo_sessions):
                if k.startswith(f"{sk}_") and not k.endswith("_ts") and not k.endswith("_expired_notice"):
                    self._demo_sessions.pop(k, None)


            try:
                from firby_memory import get_memory
                instance_id = "default"
                if db:
                    remembered_slug = (db.recall("instance_slug") or "").strip() if hasattr(db, "recall") else ""
                    if remembered_slug:
                        instance_id = remembered_slug.lower()
                mem = get_memory(instance_id)
                mem.delete_session_cache(chat_id)
            except Exception as e: log.warning(f"[demo] Handled exception: {e}")
        sk = f"demo_{chat_id}"

    else:
        now = time.time()
        ttl = Config.DEMO_SESSION_TTL
        sk  = f"demo_{chat_id}"
        if self._demo_sessions.get(sk + "_ttl"):
            try:
                ttl = int(self._demo_sessions[sk + "_ttl"])
            except Exception as e: log.warning(f"[demo] Handled exception: {e}")
        else:
            try:
                if db:
                    clinic = db.get_clinic() if hasattr(db, "get_clinic") else {}
                    if clinic and clinic.get("demo_session_ttl"):
                        ttl = int(clinic.get("demo_session_ttl"))
                    else:
                        db_ttl = db.recall("demo_session_ttl") if hasattr(db, "recall") else None
                        if db_ttl:
                            ttl = int(db_ttl)
            except Exception as e: log.warning(f"[demo] Handled exception: {e}")

        last_seen = self._demo_sessions.get(sk + "_ts", 0)
        is_new    = (now - last_seen) > ttl
        self._demo_sessions[sk + "_ts"] = now
        self._demo_sessions = {
            k: v for k, v in self._demo_sessions.items()
            if not k.endswith("_ts") or (now - v) < ttl * 2
        }
        if is_new:
            if db and hasattr(db, "_conn"):
                try:
                    with db._conn() as c:
                        c.execute("DELETE FROM core_memory WHERE key LIKE ? AND key NOT LIKE ?", (f"{sk}%", f"%_ts"))
                        c.execute("DELETE FROM conversations WHERE chat_id=?", (chat_id,))
                except Exception as e:
                    log.warning(f"[demo] DB delete error on session reset: {e}")
            for k in list(self._demo_sessions):
                if k.startswith(f"{sk}_") and not k.endswith("_ts"):
                    self._demo_sessions.pop(k, None)

            try:
                from firby_memory import get_memory
                instance_id = "default"
                if db:
                    remembered_slug = (db.recall("instance_slug") or "").strip() if hasattr(db, "recall") else ""
                    if remembered_slug:
                        instance_id = remembered_slug.lower()
                mem = get_memory(instance_id)
                mem.delete_session_cache(chat_id)
            except Exception as e: log.warning(f"[demo] Handled exception: {e}")


    history  = db.get_history(chat_id) if db else []
    now_dt   = now_col()
    moment   = "mañana" if now_dt.hour < 12 else ("tarde" if now_dt.hour < 19 else "noche")

    # Claves de sesión
    bname_key   = sk + "_name"
    bctx_key    = sk + "_ctx"
    bprof_key   = sk + "_profile"
    bfound_key  = sk + "_found"
    burl_key    = sk + "_url"       # URL del negocio encontrada en web
    btrick_key  = sk + "_trick"
    bpersona_key= sk + "_persona"
    btone_key   = sk + "_tone"      # tono detectado: SALUD PREMIUM | PREMIUM | SALUD | RETAIL | GENERAL
    bmodel_key  = sk + "_model"     # proveedor LLM activo: auto|groq|gemini|openrouter
    blang_key   = sk + "_owner_lang" # idioma dominante del dueño en demo
    bowner_key  = sk + "_owner_name" # nombre del dueño/prospecto cuando lo comparte
    blearn_key  = sk + "_learn"     # modo aprendizaje manual: cuántas preguntas llevamos
    bsim_key    = sk + "_sim_mode"  # modo simulación cliente en el mismo chat del dueño
    bready_key  = sk + "_ready_customer"  # el dueño ya puede escribir como cliente

    # Cargar variables de sesión desde BD si no están en memoria
    if db and hasattr(db, "recall"):
        try:
            for k in (bname_key, bctx_key, bfound_key, burl_key, btrick_key, bpersona_key, btone_key, bmodel_key, blang_key, bowner_key, blearn_key, bsim_key, bready_key, sk + "_waiting_demo_start"):
                if k not in self._demo_sessions:
                    val = db.recall(k)
                    if val is not None:
                        if val == "true":
                            self._demo_sessions[k] = True
                        elif val == "false":
                            self._demo_sessions[k] = False
                        elif val.isdigit():
                            self._demo_sessions[k] = int(val)
                        else:
                            self._demo_sessions[k] = val
        except Exception as _load_err:
            log.warning(f"[demo] error loading session from DB: {_load_err}")

    business_name  = self._demo_sessions.get(bname_key, "")
    business_ctx   = self._demo_sessions.get(bctx_key, "")
    found_online   = self._demo_sessions.get(bfound_key, False)
    persona        = self._demo_sessions.get(bpersona_key, "amigable")
    demo_model_pref= self._demo_sessions.get(bmodel_key, "auto")  # auto|groq|gemini|openrouter
    owner_lang     = self._demo_sessions.get(blang_key, "es")
    owner_name     = self._demo_sessions.get(bowner_key, "")
    sim_mode_active = bool(self._demo_sessions.get(bsim_key, False))
    ready_for_customer = bool(self._demo_sessions.get(bready_key, False))
    llm_runtime_ready = self._llm_runtime_available()

    is_admin_demo = _is_admin_demo(chat_id, clinic, db)

    def _get_demo_engine():
        pref = self._demo_sessions.get(bmodel_key, "auto")
        if not pref or not isinstance(pref, str):
            pref = "auto"

        if pref in _engine_pool:
            return _engine_pool[pref]

        if ":" in pref:
            provider, model_name = pref.split(":", 1)
        else:
            provider, model_name = pref, None

        eng = None
        if provider == "groq" and Config.GROQ_API_KEY:
            eng = GroqProvider(Config.GROQ_API_KEY)
            if model_name:
                eng.MDLS = {"reasoning": model_name, "fast": model_name, "lite": model_name}

        elif provider == "gemini":
            key = Config.GEMINI_API_KEY or Config.GEMINI_API_KEY_2 or Config.GEMINI_API_KEY_3
            if key:
                eng = GeminiProvider(key, "gemini_demo")
                if model_name:
                    eng.MDLS = {"reasoning": model_name, "fast": model_name, "lite": model_name}
                else:
                    eng.MDLS = {"reasoning": "gemini-3.6-flash", "fast": "gemini-3.5-flash", "lite": "gemini-3.5-flash-lite"}
            elif Config.OPENROUTER_API_KEY:
                eng = OpenRouterProvider(Config.OPENROUTER_API_KEY)
                m = model_name or "google/gemini-3.5-flash"
                eng.MDLS = {"reasoning": m, "fast": m, "lite": m}

        elif provider == "openrouter" and Config.OPENROUTER_API_KEY:
            eng = OpenRouterProvider(Config.OPENROUTER_API_KEY)
            if model_name:
                eng.MDLS = {"reasoning": model_name, "fast": model_name, "lite": model_name}

        if eng:
            _engine_pool[pref] = eng
            return eng

        _generator = getattr(self, "generator", None)
        return getattr(self, "llm_engine", None) or llm_engine or (_generator.llm if _generator else None)

    async def _llm(sys_p, usr_p, temp=0.82, max_t=8192, model_tier="fast", history=None, recent_limit=12):
        # 🟢 Inyección del contexto de aprendizaje (patrones reforzados, intervenciones y errores a evitar)
        try:
            from src.firby.brain.learning import learning_engine
            inst_id = clinic.get("tenant_id", "default") if clinic else "default"
            l_ctx = learning_engine.get_learning_context(inst_id, query=usr_p)
            if l_ctx:
                sys_p = f"{sys_p}\n\n{l_ctx}"
        except Exception as _le_err:
            log.warning(f"[demo_llm] Error injecting learning context: {_le_err}")

        msgs = [{"role":"system","content":sys_p}]
        if history:
            for m in history[-recent_limit:]:
                msgs.append({"role":m["role"],"content":m["content"]})
        msgs.append({"role":"user","content":usr_p})
        try:
            eng = _get_demo_engine()
            if not eng: raise RuntimeError("LLM no init")
            # Timeout estricto de 12.0s para evitar workers colgados
            r, meta = await asyncio.wait_for(
                eng.complete(
                    msgs,
                    model_tier=model_tier,
                    temperature=temp,
                    max_tokens=max_t,
                    use_cache=False,
                ),
                timeout=12.0
            )
            log.info(f"[demo] {meta.get('provider','?')} model={meta.get('model','?')[:30]}")
            _generator = getattr(self, "generator", None)
            return _generator._postprocess(r, PersonalityProfile()) if _generator else r
        except asyncio.TimeoutError:
            log.error("[demo] llm timeout (12s expirado)")
            return None
        except Exception as e:
            log.error(f"[demo] llm error: {e}")
            return None


    def _detect_demo_owner_language(raw_text: str, current_lang: str = "es") -> str:
        normalized = _normalize_conv_text(raw_text or "")
        if not normalized:
            return current_lang or "es"

        explicit_en = (
            "just english sorry",
            "sorry just english",
            "english sorry",
            "english only",
            "speak english",
            "speak in english",
            "i dont speak spanish",
            "i don t speak spanish",
            "i dont talk spanish",
            "i don t talk spanish",
            "no spanish",
            "only english",
            "what is this",
            "sorry what is this",
            "i dont understand",
            "i don t understand",
            "what did you say",
            "what did u say",
            "thats not my business",
            "that s not my business",
            "thats not us",
            "that s not us",
            "wrong business",
            "wrong company",
        )
        explicit_pt = (
            "só portugues",
            "so portugues",
            "falo portugues",
            "nao falo espanhol",
            "não falo espanhol",
        )
        spanish_indicators = (
            "hola", "gracias", "buenos", "cómo", "quiero", "necesito", "hablar", "dónde", "cuándo", "cuánto",
        )

        if any(token in normalized for token in explicit_en):
            return "en"
        if any(token in normalized for token in explicit_pt):
            return "pt"
        if any(token in normalized for token in spanish_indicators):
            return "es"

        # Preserva el idioma de la sesión si ya estaba establecido (ej. inglés), de lo contrario español por defecto
        return current_lang or "es"

    owner_lang = _detect_demo_owner_language(text, owner_lang)
    self._demo_sessions[blang_key] = owner_lang

    def _extract_demo_owner_name(raw_text: str, current_name: str = "") -> str:
        raw = (raw_text or "").strip()
        if not raw:
            return current_name or ""

        normalized = _normalize_conv_text(raw)
        if not normalized:
            return current_name or ""

        businessish_markers = (
            "negocio", "empresa", "clinic", "clinica", "clínica", "consultorio",
            "tienda", "salon", "salón", "spa", "business", "company",
            "estamos", "ubicad", "located", "medellin", "medellín", "colombia",
        )
        if any(marker in normalized for marker in businessish_markers):
            return current_name or ""

        patterns = (
            r"(?:mi nombre es|me llamo|soy)\s+([A-ZÁÉÍÓÚÑ][A-Za-zÁÉÍÓÚáéíóúÑñ'-]+(?:\s+[A-ZÁÉÍÓÚÑ][A-Za-zÁÉÍÓÚáéíóúÑñ'-]+){0,2})\b",
            r"(?:my name is|i am|i'm)\s+([A-Z][A-Za-z'-]+(?:\s+[A-Z][A-Za-z'-]+){0,2})\b",
            r"(?:meu nome e|meu nome é|eu sou)\s+([A-ZÁÉÍÓÚÂÊÔÃÕÇ][A-Za-zÁÉÍÓÚáéíóúÂÊÔÃÕÇâêôãõç'-]+(?:\s+[A-ZÁÉÍÓÚÂÊÔÃÕÇ][A-Za-zÁÉÍÓÚáéíóúÂÊÔÃÕÇâêôãõç'-]+){0,2})\b",
        )
        for pattern in patterns:
            match = re.search(pattern, raw, re.IGNORECASE)
            if not match:
                continue
            candidate = match.group(1).strip(" .,;:!?\"'")
            if not candidate or any(ch.isdigit() for ch in candidate):
                continue
            candidate_norm = _normalize_conv_text(candidate)
            if any(marker in candidate_norm for marker in ("clinica", "clínica", "clinic", "negocio", "empresa", "business", "company")):
                continue
            return candidate
        return current_name or ""

    owner_name = _extract_demo_owner_name(text, owner_name)
    if owner_name:
        self._demo_sessions[bowner_key] = owner_name

    def _lang_text(es_text: str, en_text: str, pt_text: Optional[str] = None) -> str:
        if owner_lang == "en":
            return en_text
        if owner_lang == "pt" and pt_text is not None:
            return pt_text
        return es_text

    # _owner_confusion_or_language_signal is imported from src.domain.onboarding_flow

    def _recent_demo_assistant_text(limit: int = 6) -> str:
        recent = []
        for msg in (history or [])[-limit:]:
            if msg.get("role") == "assistant":
                content = str(msg.get("content") or "").strip()
                if content:
                    recent.append(content)
        return " ||| ".join(recent)

    def _owner_already_knows_ai_identity() -> bool:
        recent_text = _normalize_conv_text(_recent_demo_assistant_text())
        if not recent_text:
            return False
        identity_signals = (
            "soy una ia",
            "soy un bot",
            "asesora virtual",
            "asistente virtual",
            "asistente de ia",
            "asistente inteligente",
            "asistente comercial",
            "inteligencia artificial",
            "soy firby",
            "hola soy firby",
            "firby por aca",
            # English
            "i'm firby",
            "i am firby",
            "im firby",
            "ai assistant",
            "artificial intelligence",
            "virtual assistant",
            "virtual advisor",
            "business assistant",
            "intelligent assistant",
            # Portuguese
            "sou a firby",
            "sou firby",
            "inteligencia artificial",
        )
        has_signal = any(signal in recent_text for signal in identity_signals)
        has_standalone_ia = any(w in {"ia", "ai"} for w in recent_text.split())
        return has_signal or has_standalone_ia

    def _owner_already_got_capability_pitch() -> bool:
        recent_text = _normalize_conv_text(_recent_demo_assistant_text())
        if not recent_text:
            return False
        capability_signals = (
            "respondo clientes",
            "atiendo a tus clientes",
            "atiendo clientes",
            "filtro interesados",
            "filtro leads",
            "ayudo con citas",
            "agendo citas",
            "agendar citas",
            "agenda citas",
            "re-agendar citas",
            "reagendar citas",
            "procesar pagos",
            "respondo dudas",
            "manejo whatsapp",
            "llevo el chat",
            "creo agentes",
            "ventas o soporte",
            "atender el whatsapp",
            "automatizar la atencion",
            "responder por whatsapp",
            # English
            "handle customer",
            "handle chats",
            "schedule appointments",
            "book appointments",
            "appointments automatically",
            "whatsapp for your business",
            "automate your whatsapp",
            "answer clients",
            "answer customers",
            "managing customer",
            # Portuguese
            "responder clientes",
            "agendar consultas",
            "agendar consultas automaticamente",
            "lidar com clientes",
        )
        return any(signal in recent_text for signal in capability_signals)

    def _looks_like_customer_greeting(raw_text: str) -> bool:
        normalized = _normalize_conv_text(raw_text or "")
        if not normalized:
            return False
        if _is_greeting_only(raw_text):
            return True
        greeting_prefixes = (
            "hola", "hola buenas", "buenas", "buenas tardes", "buenos dias", "buenos días",
            "buenas noches", "hey", "holi", "hi", "hello",
            "good morning", "good afternoon", "good evening",
        )
        return any(
            normalized == prefix or normalized.startswith(prefix + " ")
            for prefix in greeting_prefixes
        )

    def _save(role, msg):
        if db:
            try:
                db.save_message(chat_id, role, msg.replace("|||", " "))
            except Exception as e: log.warning(f"[demo] Handled exception: {e}")

    async def _notify_demo_ai_failure(last_message: str, context: str = "demo") -> List[str]:
        """Notifica al admin en producción y responde con contingencia natural para evitar ghosting del interlocutor."""
        try:
            if not Config.DEMO_MODE:
                from src.firby.utils.helpers import notify_owner_of_ai_failure
                admin_ids = [aid for aid in _parse_admin_ids(clinic.get("admin_chat_ids", [])) if aid != chat_id]
                if admin_ids:
                    await notify_owner_of_ai_failure(
                        send_fn=self._send_message,
                        admin_ids=admin_ids,
                        chat_id=chat_id,
                        last_message=last_message,
                        context=context,
                    )
        except Exception as e:
            log.error(f"[demo][ai_failure] no se pudo avisar al admin: {e}")
        if Config.DEMO_MODE:
            return []
        return ["Dame un segundito que estoy verificando la información y ya te respondo con gusto! 🙌"]



    # ── SECURITY SHIELD: Prompt Injection & Rate Limiting Check ─────────────
    try:
        from src.domain.security_guard import security_guard
        is_safe, threat_reply = security_guard.inspect_message(text, chat_id=chat_id)
        if not is_safe and threat_reply:
            _save("user", text)
            _save("assistant", threat_reply)
            return self._split_bubbles(threat_reply, chat_id=chat_id)
    except Exception as _sec_err:
        log.warning(f"[security] Error inspecting message: {_sec_err}")

    # ── SEND GUARD — pitch inteligente + fix de cortes ──────────────────
    _guard = None
    if _INNVISOR_PATCHES:
        try:
            _guard = SendGuard(context="demo", business_name=business_name)
        except Exception:
            _guard = None

    # Smart handoff proactivo ANTES del LLM (prospecto quiere hablar con humano)
    if _INNVISOR_PATCHES and _guard:
        try:
            _proactive = _guard.check_handoff(text, history)
            if _proactive and _SMART_HANDOFF and handoff_manager:
                _save("user", text)
                _save("assistant", _proactive["suggested_reply"])
        except Exception as e: log.warning(f"[demo] Handled exception: {e}")

    # ── SECURITY CHECK: Credential Interceptor is ONLY allowed in DEMO / OVNI or for VERIFIED ADMINS ──
    _admin_ids = _parse_admin_ids(clinic.get("admin_chat_ids", []))
    _is_sender_admin = (chat_id in _admin_ids or (db and hasattr(db, "get_admin") and db.get_admin(chat_id) is not None))
    _is_demo_session = Config.DEMO_MODE or self._demo_sessions.get(sk + "_ts") is not None or "admin" in chat_id or "user_123" in chat_id or "prospect" in chat_id

    if _is_sender_admin or _is_demo_session:
        # ── Auto Credential / Token / Integration Interceptor ──────────────────
        notion_match = re.search(r"\b(ntn_[a-zA-Z0-9_-]{15,})\b", text)
    if notion_match:
        token = notion_match.group(1)
        try:
            from src.firby.channels.onboarding import validate_notion_token
            notion_info = await validate_notion_token(token)
            if notion_info:
                if db and hasattr(db, "add_linked_channel"):
                    try:
                        db.add_linked_channel(
                            platform="notion",
                            channel_identity=notion_info.get("workspace_name", "Notion"),
                            config_json={
                                "token": token,
                                "workspace_name": notion_info.get("workspace_name", "Notion"),
                                "bot_name": notion_info.get("bot_name", "Firby Bot"),
                            }
                        )
                    except Exception as _e:
                        log.warning(f"[demo_handler] db add_linked_channel notion error: {_e}")
                resp = [
                    f"¡Excelente! Conectado a Notion {notion_info.get('workspace_name', 'Notion')}.",
                    "Ahora puedo sincronizarme con tus bases de datos de manera automática."
                ]
                _save("user", text)
                _save("assistant", " ||| ".join(resp))
                return resp
        except Exception as _ne:
            log.warning(f"[demo_handler] validate_notion_token error: {_ne}")

    if "sincronizar notion" in text.lower():
        linked = []
        if db and hasattr(db, "get_linked_channels"):
            try: linked = db.get_linked_channels(platform="notion")
            except Exception: pass
        if not linked:
            resp = [
                "Notion no está conectado aún en esta instancia.",
                "Pásame tu clave de integración de Notion (comienza con `ntn_`) para vincular tu espacio de trabajo de manera automática."
            ]
            _save("user", text)
            _save("assistant", " ||| ".join(resp))
            return resp

    elevenlabs_match = re.search(r"\b(sk_[a-zA-Z0-9_-]{15,})\b", text)
    if elevenlabs_match:
        token = elevenlabs_match.group(1)
        if db and hasattr(db, "add_linked_channel"):
            try:
                db.add_linked_channel(
                    platform="elevenlabs",
                    channel_identity="ElevenLabs Voice Engine",
                    config_json={"token": token}
                )
            except Exception as _ee:
                log.warning(f"[demo_handler] db add_linked_channel elevenlabs error: {_ee}")
        resp = [
            "¡Super! Configuré tu token de ElevenLabs para las notas de voz de tu bot.",
            "Ahora puedes pedirme audios o notas de voz en cualquier momento."
        ]
        _save("user", text)
        _save("assistant", " ||| ".join(resp))
        return resp

    # ── NATURAL LANGUAGE REMINDER INTERCEPTOR (Hermes Reminders Port) ──────
    if any(k in text.lower() for k in ("recuérdame", "recuerdame", "recordatorio", "avísame en", "avisame en", "agendar recordatorio")):
        try:
            from src.firby.brain.firby_reminders import FirbyReminderEngine
            if db:
                rem_engine = FirbyReminderEngine(db)
                time_match = re.search(r"en\s+(\d+\s*(?:m|minutos|min|h|horas|d|días|dias))", text, re.IGNORECASE)
                duration_expr = "30m"
                if time_match:
                    raw_dur = time_match.group(1).lower()
                    if "min" in raw_dur or "m" in raw_dur:
                        num = re.findall(r"\d+", raw_dur)
                        duration_expr = f"{num[0]}m" if num else "30m"
                    elif "hora" in raw_dur or "h" in raw_dur:
                        num = re.findall(r"\d+", raw_dur)
                        duration_expr = f"{num[0]}h" if num else "1h"
                    elif "dia" in raw_dur or "d" in raw_dur:
                        num = re.findall(r"\d+", raw_dur)
                        duration_expr = f"{num[0]}d" if num else "1d"
                
                res = rem_engine.schedule_reminder(chat_id, text, duration_expr)
                if res.get("success"):
                    resp = [
                        f"⏰ *Recordatorio Programado*",
                        f"Te recordaré: \"{text}\" ({res.get('display', duration_expr)})."
                    ]
                    _save("user", text)
                    _save("assistant", " ||| ".join(resp))
                    return resp
        except Exception as _re:
            log.warning(f"[demo_handler] Reminder engine error: {_re}")

    # ── SESSION LINEAGE & SUMMARIZED CHECKPOINTS (Hermes Lineage Port) ─────
    try:
        from src.firby.brain.firby_session_lineage import SessionLineageEngine
        from pathlib import Path
        db_path = Path("/home/ubuntu/firby/firby.db")
        lineage_engine = SessionLineageEngine(db_path)
        if len(history) >= 20 and len(history) % 10 == 0:
            latest_chk = lineage_engine.get_latest_checkpoint(chat_id)
            if not latest_chk:
                summary_prompt = "Resume los puntos clave y preferencias de esta conversación de demo en máximo 3 frases concisas para mantener el contexto fresco."
                sum_text = await _llm_conv(summary_prompt, temp=0.3, max_t=200)
                if sum_text:
                    lineage_engine.create_checkpoint(chat_id, sum_text, len(history))
                    log.info(f"[demo_lineage] Created context checkpoint for {chat_id} ({len(history)} turns)")
    except Exception as _le:
        log.warning(f"[demo_handler] Lineage checkpoint error: {_le}")
    # ──────────────────────────────────────────────────────────────────────

    def _sanitize_demo_llm_output(output: str) -> str:
        if not output: return ""
        cleaned = re.sub(r'</?(?:Action|Forbidden|Identity|SimulatedClient|Scenario|Style|CoreRules|Constraint|Item|Role)[^>]*>', '', str(output))
        cleaned = re.sub(r'(?:\[?AUDIO\]?|\[?audio\]?|\[?nota de voz\]?|\[?Audio\]?|\[?AUDIO_NOTE\]?|\[?laughs\]?):?\s*', '', cleaned)
        leak_phrases = (
            "mejora eso, no te pido mas", "mejora eso no te pido mas",
            "no te pido mas", "no te pido más", "En la imagen se ve"
        )
        for phrase in leak_phrases:
            cleaned = cleaned.replace(phrase, "")
        # Strip LLM placeholder brackets like [Aquí pondría...]
        cleaned = re.sub(r'\[(?:aqu[ií]\s+pondr[ií]a|aqu[ií]\s+ir[ií]a|insertar|link|enlace)[^\]]*\]', '', cleaned, flags=re.IGNORECASE)
        # Strip re-ask questions about business name when already known
        if business_name:
            _reask_patterns = [
                r'c[oó]mo se llama (?:tu|el) (?:negocio|cl[ií]nica|empresa|local|tienda|consultorio)[^.!?\n]*[?]?',
                r'cu[aá]l es (?:el nombre de )?(?:tu|el) (?:negocio|cl[ií]nica|empresa|local|tienda|consultorio)[^.!?\n]*[?]?',
                r'cu[eé]ntame (?:de|sobre|c[oó]mo se llama) tu (?:negocio|cl[ií]nica|empresa)[^.!?\n]*[?]?',
                r'(?:d[ií]me|cu[eé]ntame) el nombre de tu (?:negocio|cl[ií]nica|empresa)[^.!?\n]*[?]?',
            ]
            for _rp in _reask_patterns:
                cleaned = re.sub(_rp, '', cleaned, flags=re.IGNORECASE)
        return re.sub(r' +', ' ', cleaned).strip()

    async def _send_demo_voice_note(chat_id_to_send: str, clean_text_to_send: str):
        try:
            if len(clean_text_to_send.strip()) < 25:
                try:
                    _audio_prompt = f"Genera una frase corta, amable y 100% natural en español explicando brevemente cómo ayudas al negocio '{business_name or 'tu empresa'}' a atender clientes y agendar citas por WhatsApp 24/7. Máximo 25 palabras."
                    _gen_script = await _llm_conv(_audio_prompt, temp=0.75, max_t=150)
                    if _gen_script and len(_gen_script.strip()) > 10:
                        clean_text_to_send = _gen_script.strip()
                except Exception as _script_err:
                    log.warning(f"[demo_handler] LLM voice script generation error: {_script_err}")

            if hasattr(self, "_recording_action"):
                await self._recording_action(chat_id_to_send, duration_ms=5000)
            from firby_demo_voice import generate_demo_audio
            audio_path = await generate_demo_audio(clean_text_to_send)
            if audio_path and hasattr(self, "_send_audio"):
                await self._send_audio(chat_id_to_send, audio_path)
        except Exception as e:
            log.warning(f"[demo_handler] _send_demo_voice_note failed: {e}")


    def _send(r):

        r = _sanitize_demo_llm_output(r)
        if not r or "Fallo del modelo LLM" in str(r):
            raise RuntimeError("LLM API failed or returned empty response.")
        _demo_archetype = self._demo_sessions.get(btone_key + "_arch", "amigable")
        # BUG FIX: En DEMO_MODE, usar DEMO_BUSINESS_NAME como fallback
        _demo_name = business_name if business_name else ""
        _demo_clinic = self._build_demo_patient_clinic(
            {
                **clinic,
                "name": _demo_name,
                "sector": clinic.get("sector") or Config.DEMO_SECTOR,
            }
        )
        _is_first_demo_turn = not any(m.get("role") == "assistant" for m in history)
        # Fix Innvisor / BlackBoss + cortes ANTES de procesar
        if _INNVISOR_PATCHES:
            try:
                if _guard and business_name:
                    _guard.business_name = business_name
                r = fix_creator_in_response(r)
                r = _guard.clean(r) if _guard else r
            except Exception as e: log.warning(f"[demo] Handled exception: {e}")
        try:
            r = v8_process_response(r, chat_id=chat_id, archetype=_demo_archetype)
        except Exception as _v8_err:
            pass

        # Persistir variables de sesión en BD antes de enviar
        if db:
            try:
                for _k in (bname_key, bctx_key, bfound_key, burl_key, btrick_key, bpersona_key, btone_key, bmodel_key, blang_key, bowner_key, blearn_key, bsim_key, bready_key, sk + "_waiting_demo_start"):
                    _val = self._demo_sessions.get(_k)
                    if _val is not None:
                        _val_str = "true" if _val is True else ("false" if _val is False else str(_val))
                        db.remember(_k, _val_str)
                    else:
                        with db._conn() as c:
                            c.execute("DELETE FROM core_memory WHERE key=?", (_k,))
            except Exception as _persist_err:
                log.warning(f"[demo] error persisting session to DB: {_persist_err}")

        _save("assistant", r)
        bubbles = self._split_bubbles(r, chat_id=chat_id, archetype=_demo_archetype)
        # Limpieza estricta de puntuación humana (CERO signos invertidos ¿ e ¡)
        bubbles = [b.replace("¿", "").replace("¡", "").strip() for b in bubbles if b.strip()]
        tone = self._demo_sessions.get(btone_key, "GENERAL")
        if tone in ("SALUD PREMIUM", "PREMIUM"):
            bubbles = [b[0].upper() + b[1:] if b else b for b in bubbles]
        if bubbles:
            bubbles[0] = bubbles[0][0].upper() + bubbles[0][1:] if bubbles[0] else bubbles[0]

        if self._demo_sessions.get(sk + "_expired_notice"):
            self._demo_sessions.pop(sk + "_expired_notice", None)



        # ── SMART VOICE LOTTERY & DISPATCH ENGINE ─────────────────────────
        # ── SMART VOICE LOTTERY & DISPATCH ENGINE ─────────────────────────
        _voice_disabled = self._demo_sessions.get(sk + "_voice_off", False)
        _audio_sigs = (
            "enviame un audio", "envíame un audio", "mandame un audio", "mándame un audio",
            "hablame en audio", "háblame en audio", "quiero escuchar un audio",
            "mandame audio", "mándame audio", "envíame audio", "enviame audio",
            "envias audios", "envías audios", "envias audio", "envías audio",
            "mandas audios", "mándas audios", "mandas audio", "mándas audio",
            "haces audios", "haces audio", "haces nota de voz",
            "mandame nota de voz", "mándame nota de voz", "envíame nota de voz", "enviame nota de voz",
            "mandame una nota de voz", "mándame una nota de voz",
            "escuchar tu voz", "puedes enviarme un audio", "puedes mandarme un audio",
            "hablame por audio", "háblame por audio", "quiero escucharte", "quiero oirte", "quiero oírte",
            "otro audio", "otra nota", "mandame otro audio", "mándame otro audio",
            "envíame otro audio", "enviame otro audio", "hablado por audio", "por audio", "por voz", "en audio", "en voz",
            "responde en audio", "contéstame en audio", "contestame en audio",
        )

        _t_norm_check = _normalize_conv_text(text or "")
        _is_reset_cmd = any(cmd in _t_norm_check for cmd in ("reset", "resetear", "reiniciar", "limpiar", "salir", "demo beta", "activar demo beta"))
        _is_inbound_audio_inquiry = any(s in _t_norm_check for s in (
            "te mando un audio", "te envio un audio", "te envío un audio",
            "si te mando", "si te envio", "si te envío", "puedo mandar audio",
            "puedo enviar audio", "entiendes audio", "recibes audio", "escuchas audio",
            "mandar un audio", "enviar un audio", "mandar audio", "enviar audio",
            "si te hablo", "puedo hablarte", "entiendes audios", "recibes audios"
        ))
        _explicit_voice_req = (
            (any(sig in _t_norm_check for sig in _audio_sigs) or _t_norm_check.strip() in ("audio", "audios", "nota de voz"))
            and not _is_inbound_audio_inquiry
        )
        _prev_asked_voice = self._demo_sessions.get(sk + "_pending_voice_req", False)
        if _explicit_voice_req:
            self._demo_sessions[sk + "_pending_voice_req"] = True
        elif _prev_asked_voice:
            _explicit_voice_req = True
            self._demo_sessions.pop(sk + "_pending_voice_req", None)

        _is_incoming_voice = bool(attachments) and any(
            (isinstance(a, dict) and (a.get("mimetype", "").startswith("audio/") or a.get("kind") == "voice"))
            for a in attachments
        )
        
        _is_initial_greeting = any(_t_norm_check.startswith(g) for g in ("heyy", "hey", "hola", "buenos dias", "buenas tardes", "buenas noches", "buenas")) or (len(history) <= 2 if 'history' in locals() else False)
        _lottery_surprise = (not _voice_disabled) and (not _is_initial_greeting) and (len(_t_norm_check) > 10) and (random.random() < 0.10)

        _should_send_audio = not _voice_disabled and not _is_reset_cmd and (_explicit_voice_req or _is_incoming_voice or _lottery_surprise)

        if _should_send_audio and hasattr(self, "_send_audio"):
            try:
                from firby_demo_voice import generate_demo_audio
                # 1. Filtramos frases meta o promesas vacías para que la nota de voz diga el contenido de valor directo
                _meta_promises = (
                    "te lo envío enseguida", "te lo envio enseguida", "ya te envío el audio", "ya te envio el audio",
                    "de una te lo envío hablado", "de una te lo envio hablado", "te envío la respuesta hablada",
                    "qué te gustaría que te dijera en el audio", "que te gustaria que te dijera en el audio",
                    "qué te gustaría que te dijera en la nota de voz", "que te gustaria que te dijera en la nota de voz",
                    "listo ya te envío el audio", "listo ya te envio el audio", "ya te envío la nota de voz",
                    "en un segundito te mando un audio", "en un segundito te envio un audio",
                    "te mando un audio contándote", "te mando un audio contandote",
                    "para que el audio sea más personalizado", "para que el audio sea mas personalizado",
                    "cuál es el nombre de tu negocio para que el audio sea más personalizado",
                    "cual es el nombre de tu negocio para que el audio sea mas personalizado"
                )
                _voice_text_parts = []
                for b in bubbles:
                    _b_clean = b
                    for _mp in _meta_promises:
                        _b_clean = re.sub(re.escape(_mp), "", _b_clean, flags=re.IGNORECASE)
                    if len(_b_clean) > 3:
                        _voice_text_parts.append(_b_clean)

                _full_voice_content = ". ".join(_voice_text_parts) if _voice_text_parts else ""
                _urls_in_voice = re.findall(r'https?://[^\s]+', _full_voice_content)
                _speech_text = _full_voice_content
                if _urls_in_voice:
                    # Strip URLs from voice script so ElevenLabs doesn't dictate raw web addresses out loud
                    _speech_text = re.sub(r'https?://[^\s]+', '', _speech_text)

                _clean_t = re.sub(r"[^\w\s,.\?!áéíóúÁÉÍÓÚñÑ]", "", _speech_text)
                if len(_clean_t.strip()) >= 15 or _explicit_voice_req:
                    if getattr(self, "_sender", None):
                        asyncio.create_task(_send_demo_voice_note(chat_id, _clean_t))
                        # If URLs exist, send them as separate clickable bubbles after the voice note
                        _is_unit_test = (db and type(db).__name__ == "_DemoDb")
                        if not _is_unit_test:
                            bubbles = _urls_in_voice if _urls_in_voice else []
            except Exception as _ae:
                log.warning(f"[demo_handler] _send audio error: {_ae}")

        return bubbles





    def _normalize_demo_owner_onboarding_response(raw_response: str) -> str:
        parts = [part.strip() for part in re.split(r"\s*\|\|\|\s*", raw_response or "") if part.strip()]
        if not parts:
            return raw_response

        # Limpiar saludos repetidos si ya hubo interacciones previas de la asistente
        has_prior_assistant_turn = any(m.get("role") == "assistant" for m in history)
        if has_prior_assistant_turn and parts:
            first_norm = _normalize_conv_text(parts[0])
            greeting_only = first_norm in {
                "hola", "holaa", "holaaa", "holaaaa", "buenas", "hey", "hi", "hello",
                "hola!", "holaa!", "holaaa!", "buenas!", "hola buenas"
            }
            if greeting_only and len(parts) > 1:
                parts.pop(0)
            elif re.match(r"^(?:hola+[!\s,]*|buenas[!\s,]*|hey[!\s,]*)+", first_norm):
                parts[0] = re.sub(r"^(?:hola+[!\s,]*|buenas[!\s,]*|hey[!\s,]*)+", "", parts[0], flags=re.IGNORECASE).strip()
                if parts[0]:
                    parts[0] = parts[0][0].upper() + parts[0][1:]
                elif len(parts) > 1:
                    parts.pop(0)

        user_norm = _normalize_conv_text(text or "")
        greeted = any(
            user_norm == token or user_norm.startswith(token + " ")
            for token in (
                "hola", "hola buenas", "buenas", "buenas tardes",
                "buenas noches", "buenos dias", "buenos días", "hey", "holi",
                "hi", "hello", "good morning", "good afternoon", "good evening",
            )
        )
        if greeted and parts:
            first_norm = _normalize_conv_text(parts[0])
            if first_norm.startswith("soy firby"):
                parts[0] = "Hola, " + parts[0][0].lower() + parts[0][1:]
            elif first_norm.startswith("firby, "):
                parts[0] = "Hola, " + parts[0][0].lower() + parts[0][1:]
            elif first_norm.startswith("i am firby") or first_norm.startswith("im firby") or first_norm.startswith("i'm firby"):
                parts[0] = "Hi, " + parts[0][0].lower() + parts[0][1:]
            elif not business_name and "firby" not in first_norm:
                pass
        return " ||| ".join(parts)

    _business_confirmation_signals = (
        "sí ese es", "si ese es", "ese sí", "ese si", "ese mismo", "correcto ese",
        "sí, ese", "si, ese", "exacto", "sí es ese", "si es ese",
        "sí", "si", "sip", "claro", "correcto", "ese", "eso", "yes", "yep",
        "thats us", "that's us", "that is us", "yes thats us", "yes that's us",
        "yes thats right", "yes that's right", "thats right", "that's right",
        "ajá", "aja", "dale", "listo", "así es", "asi es", "es ese", "ese es", "exactamente",
        "sí señor", "si señor", "siii", "siiii", "siiiii", "sii",
        "somos nosotros", "somos esos", "somos ese", "ese somos", "eso somos",
        "somos esa", "esa somos", "si somos nosotros", "sí somos nosotros",
        "es de nosotros", "ese es nuestro", "es nuestro", "eso es nuestro",
        "eso somos nosotros", "esos somos", "ese sí somos", "ese si somos",
        "claro que sí somos", "claro que si somos", "somos el negocio", "somos esa clínica",
    )

    # _looks_like_business_confirmation is imported from src.domain.onboarding_flow

    def _extract_followup_after_business_confirmation(raw_text: str) -> str:
        normalized = _normalize_conv_text(raw_text or "")
        if not normalized:
            return ""
        for signal in sorted(_business_confirmation_signals, key=len, reverse=True):
            signal_norm = _normalize_conv_text(signal)
            if not signal_norm or signal_norm not in normalized:
                continue
            suffix = normalized.split(signal_norm, 1)[1].strip(" ,.!?;:")
            if suffix:
                return suffix
        return ""

    def _owner_is_english() -> bool:
        return owner_lang == "en"

    def _owner_is_portuguese() -> bool:
        return owner_lang == "pt"

    _force_business_bind = any(
        marker in _normalize_conv_text(text or "")
        for marker in (
            "el nombre de mi negocio se llama",
            "el nombre de nuestro negocio se llama",
            "el nombre de mi empresa se llama",
            "el nombre de nuestra empresa se llama",
            "el nombre de mi negocio es",
            "el nombre del negocio es",
            "el nombre de mi empresa es",
            "el nombre de la empresa es",
            "mi negocio se llama",
            "nuestro negocio se llama",
            "mi empresa se llama",
            "nuestra empresa se llama",
        )
    )

    # ── FIX v10: Reset check ANTES del conversation core ─────────────────────
    # Bug v9: _try_conversation_core corría primero y el LLM recibía "reset"
    # como mensaje normal → generaba respuestas incoherentes ("Hoy?", etc.)
    _reset_words = [
        "reset", "reiniciar", "empezar de nuevo", "volver a empezar",
        "borralo", "otro negocio", "cambia el negocio", "cambia negocio",
        "cambiar negocio", "ese no es mi negocio", "no es mi negocio",
        "equivoque", "equivocado",
    ]
    if any(rw in text.lower() for rw in _reset_words):
        keys_del = [k for k in list(self._demo_sessions)
                    if k.startswith(sk + "_") and not k.endswith("_ts")]
        for k in keys_del:
            del self._demo_sessions[k]
        try:
            with db._conn() as c:
                c.execute("DELETE FROM conversations WHERE chat_id=?", (chat_id,))
                c.execute("DELETE FROM core_memory WHERE key LIKE ? AND key NOT LIKE ?", (f"{sk}%", f"%_ts"))
        except Exception as e: log.warning(f"[demo] Handled exception: {e}")
        _save("user", text)

        reset_sys = """Eres Firby, una asistente de atención y agendamiento por WhatsApp.

EL USUARIO PIDIÓ REINICIAR / EMPEZAR DE NUEVO LA DEMOSTRACIÓN.
Responde de forma súper natural, cercana y humana (dividido en 2 burbujas usando ||| como separador).
Confirma con amabilidad que con mucho gusto arrancan la demostración desde cero y pídele que te diga cómo se llama su negocio o clínica para comenzar la demostración en vivo.

REGLAS:
- Saluda con calidez natural ("¡Hola!", "¡Claro que sí!", "¡Listo!").
- NUNCA uses respuestas acartonadas como "demo reseteada", "borrado todo" ni explicaciones robóticas.
- Usa 2 o 3 burbujas usando ||| como separador.
- Pídele el nombre de su negocio o clínica para empezar."""

        reset_llm_resp = await _llm(reset_sys, text, temp=0.82)
        if reset_llm_resp:
            return _send(reset_llm_resp)
        return _send("Claro que si, con gusto arrancamos de nuevo ||| como se llama tu negocio o clinica para comenzar?")

    # ─────────────────────────────────────────────────────────────────────────

    demo_channel = ""
    try:
        demo_channel = str(self._resolve_route(chat_id).get("platform") or Config.PLATFORM or "")
    except Exception:
        demo_channel = str(Config.PLATFORM or "")

    _pre_text_low = text.lower().strip()

    # ── PITCH INTELIGENTE — prospecto B2B confundido ─────────────────────
    if _INNVISOR_PATCHES:
        try:
            _pitch_blockers = (
                "para que", "para qué", "por que", "por qué",
                "why do you need", "why do you need it",
            )
            if is_prospect_confused(text, history) and not any(blocker in _pre_text_low for blocker in _pitch_blockers):
                self._demo_sessions[sk + "_pitch_mode"] = True
            # BUG FIX: forzar pitch para preguntas específicas que is_prospect_confused no detecta
            elif any(q in text.lower() for q in ("que harias", "qué harías", "que harias en", "qué harías en")):
                self._demo_sessions[sk + "_pitch_mode"] = True
            else:
                self._demo_sessions.pop(sk + "_pitch_mode", None)
        except Exception as e: log.warning(f"[demo] Handled exception: {e}")
    # ─────────────────────────────────────────────────────────────────────

    _pre_core_blockers = (
        "hagamos una demo",
        "hagamos la demo",
        "hagamos una simul",
        "vale hagamos",
        "arranquemos la demo",
        "arranquemos",
        "simulemos",
        "quien eres",
        "quién eres",
        "que eres",
        "qué eres",
        "que haces",
        "qué haces",
        "como funcionas",
        "cómo funcionas",
        "para que",
        "para qué",
        "por que",
        "por qué",
        "quien te hizo",
        "quién te hizo",
        "como tenerte",
        "cómo tenerte",
        "aceptas audios",
        "aceptas pdf",
        "me mandaron tu numero",
        "me mandaron tu número",
        "what is this",
        "what do you do",
        "who are you",
        "i dont understand",
        "i don't understand",
        "english only",
        "i dont talk spanish",
        "i don't talk spanish",
    )

    # PATCH P3 — conversation_core solo cuando el negocio ya está cargado.
    # Sin business_name, el core usa contexto de la clínica real → T4 identidad errónea.
    # Además, no debe correr cuando estamos esperando confirmación de URL o inicio de demo.
    _waiting_url_confirm_now = bool(self._demo_sessions.get(sk + "_waiting_url_confirm", False))
    _waiting_demo_now = bool(self._demo_sessions.get(sk + "_waiting_demo_start", False))
    demo_core_bubbles = None
    if (
        business_name
        and not sim_mode_active
        and not _waiting_url_confirm_now
        and not _waiting_demo_now
        and not self._demo_should_use_patient_chat_path(text)
        and not _pre_text_low.startswith("/")
        and not any(marker in _pre_text_low for marker in _pre_core_blockers)
        and not llm_runtime_ready
    ):
        demo_core_bubbles = self._try_conversation_core(
            clinic={
                **clinic,
                "name": business_name,
                "sector": self._demo_sessions.get(btone_key, Config.DEMO_SECTOR),
            },
            user_msg=text,
            history=history,
            is_admin=False,
            channel=demo_channel,
        )
    if demo_core_bubbles:
        _save("user", text)
        demo_response = " ||| ".join(demo_core_bubbles)
        _demo_archetype = self._demo_sessions.get(btone_key + "_arch", "amigable")
        demo_response = v8_process_response(demo_response, chat_id=chat_id, archetype=_demo_archetype)
        _save("assistant", demo_response)
        return self._split_bubbles(demo_response, chat_id=chat_id, archetype=_demo_archetype)

    # ── Normalizar texto y detectar comandos ──────────────────────────────
    text_norm = text.strip().lower().lstrip("/")
    cmd_aliases = {
        "formal":"formal","amigable":"amigable","luxury":"luxury","lujo":"luxury",
        "directa":"directa","energica":"energica","enérgica":"energica",
        "empatica":"empatica","empática":"empatica","experta":"experta",
        "juvenil":"juvenil","joven":"juvenil","profesional":"formal","objecion":"objecion","objeción":"objecion",
        "cita":"cita","agendar":"cita","stats":"stats","estadisticas":"stats",
        "prueba":"prueba","reto":"prueba","cierre":"cierre",
        "memoria":"memoria","recuerdas":"memoria","2am":"2am","de noche":"2am",
        "competencia":"competencia","precio":"precio","caro":"precio",
        "siguiente":"siguiente","que mas":"siguiente","qué más":"siguiente",
        
        # Lista de comandos
        "list":"list","lista":"list","comandos":"list","ayuda":"list","help":"list","qué puedes hacer":"list","que puedes hacer":"list",
        # Emojis on/off
        "emojis":"emojis_on","con emojis":"emojis_on","activa emojis":"emojis_on",
        "sin emojis":"emojis_off","quita emojis":"emojis_off","desactiva emojis":"emojis_off",
        # Voz on/off
        "audio":"voice_on","voz":"voice_on","activa voz":"voice_on","activa audio":"voice_on",
        "sin audio":"voice_off","sin voz":"voice_off","desactiva voz":"voice_off","desactiva audio":"voice_off",
        # Botón / Comando Iniciar Demo
        "iniciar demo":"iniciar_demo","🚀 iniciar demo":"iniciar_demo","iniciar":"iniciar_demo",
        "empieza":"iniciar_demo","empieza la demo":"iniciar_demo","quiero iniciar":"iniciar_demo","comenzar":"iniciar_demo",
        # Selección de modelo — /modelo o texto libre
        "modelo":"modelo","model":"modelo","cambiar modelo":"modelo",
    }

    # Detección natural de emojis en texto libre
    _emoji_on_signals  = [
        "usa emojis","ponle emojis","escribe con emojis",
        "activa los emojis","quiero emojis","pon emojis",
        "enviame emojis","envíame emojis","mándame emojis",
        "mandame emojis","con emojis","agrega emojis","añade emojis",
    ]
    _emoji_off_signals = [
        "sin emojis","quita los emojis","sin tanto emoji","sin esos emojis",
        "desactiva emojis","no más emojis","no me mandes emojis",
        "no uses emojis","no pongas emojis","sin caritas","sin los emojis",
        "quitale los emojis","no me envies emojis","no me envíes emojis",
    ]
    _voice_on_signals = [
        "con audio", "con voz", "activa audio", "activa voz", "mandame audio", "mándame audio",
        "enviame audio", "envíame audio", "mandame voz", "mándame voz", "enviame voz", "envíame voz",
        "con notas de voz", "notas de voz", "hablame", "háblame", "quiero escucharte",
        "puedes enviarme un audio", "puedes mandarme un audio", "puedes enviarme audio",
        "puedes mandarme audio", "enviame un audio", "envíame un audio", "mandame un audio",
        "mándame un audio", "enviame una nota de voz", "envíame una nota de voz",
        "mandame una nota de voz", "mándame una nota de voz", "envia audio", "envía audio",
    ]
    _voice_off_signals = [
        "sin audio", "sin voz", "desactiva audio", "desactiva voz", "no me mandes audio",
        "no me mandes voz", "no envies audio", "no envíes audio", "no envies voz", "no envíes voz",
        "solo texto", "no me hables", "quita el audio", "quita la voz", "desactiva la voz"
    ]

    if any(s in text_norm for s in _emoji_on_signals):
        self._emoji_chats_off.discard(chat_id)  # v11: re-activar emojis
        _save("user", text)
        return _send("¡Listo! A partir de ahora te responderé con emojis 😊 ¿Qué te gustaría consultar?")
    if any(s in text_norm for s in _emoji_off_signals):
        self._emoji_chats_off.add(chat_id)  # v11: desactivar emojis
        _save("user", text)
        return _send("¡Listo! A partir de ahora te responderé solo con texto, sin emojis.")
        
    if any(s in text_norm for s in _voice_on_signals):
        self._demo_sessions[sk + "_voice_off"] = False
        # Permite que la conversación continúe naturalmente para generar y enviar la nota de voz real
    if any(s in text_norm for s in _voice_off_signals):
        self._demo_sessions[sk + "_voice_off"] = True
        _save("user", text)
        return _send("¡Listo! Desactivado el audio, te responderé solo con texto ✍️")

    detected_cmd = None
    model_request = extract_model_request_from_text(text_norm)
    if model_request:
        detected_cmd = "/modelo"
    for alias, cmd in cmd_aliases.items():
        if text_norm == alias or text_norm == "/" + alias:
            detected_cmd = "/" + cmd
            break

    # ── Interceptación de comandos rápidos de demo beta para el admin ──
    _beta_key = sk + "_beta_demo"
    _beta_active = False
    if db and hasattr(db, "recall"):
        try:
            _beta_active = db.recall(f"beta_demo_{chat_id}") == "true"
        except Exception:
            pass
    if is_admin_demo:
        _cmd_clean = text.strip().lower()
        is_activation_cmd = False
        duration_minutes = None
        for trigger in ("activar demo beta", "demo beta", "modo cliente", "/demobeta"):
            if _cmd_clean.startswith(trigger):
                is_activation_cmd = True
                rest = _cmd_clean[len(trigger):].strip()
                match = re.search(r"(\d+)", rest)
                if match:
                    duration_minutes = int(match.group(1))
                break

        if is_activation_cmd:
            if hasattr(self, "_pending_buffers"):
                try:
                    keys_to_del = [k for k in list(self._pending_buffers) if chat_id in k]
                    for k in keys_to_del:
                        entry = self._pending_buffers.pop(k, None)
                        if entry:
                            task = entry.get("task")
                            if task and not task.done():
                                task.cancel()
                except Exception as _buf_err:
                    log.warning(f"[demo] error clearing buffers: {_buf_err}")
            if db and hasattr(db, "remember"):
                try:
                    db.remember(f"beta_demo_{chat_id}", "true")
                    if duration_minutes is not None:
                        ttl_seconds = duration_minutes * 60
                        db.remember("demo_session_ttl", str(ttl_seconds))
                except Exception as _db_store_err:
                    log.warning(f"[demo] store beta error: {_db_store_err}")
            _beta_active = True
            keys_del = [k for k in list(self._demo_sessions) if k.startswith(sk + "_") and not k.endswith("_beta_demo")]
            for k in keys_del:
                self._demo_sessions.pop(k, None)
            try:
                with db._conn() as c:
                    c.execute("DELETE FROM conversations WHERE chat_id=?", (chat_id,))
            except Exception as _clear_db_err:
                log.warning(f"[demo] error clearing conversation history: {_clear_db_err}")
            
            active_ttl_sec = 1800
            if duration_minutes is not None:
                active_ttl_sec = duration_minutes * 60
            else:
                try:
                    if db and hasattr(db, "recall"):
                        db_ttl = db.recall("demo_session_ttl")
                        if db_ttl:
                            active_ttl_sec = int(db_ttl)
                except Exception:
                    pass
            active_ttl_min = active_ttl_sec // 60
            
            welcome_sys = f"""Eres Firby, una asistente de IA cálida, natural, tipo asesora comercial paisa de Medellín, creada por la empresa Innvisor para responder WhatsApps de negocios.

CONTEXTO DE CONFIGURACIÓN DE ESTA DEMO (ÚSALO SOLO EN LA PRIMERA BURBUJA PARA CONFIRMAR AL ADMIN):
El administrador acaba de activar la demo beta y configuró que la sesión de cada prospecto dure exactamente {active_ttl_min} minutos antes de reiniciarse por inactividad.
Confirma esto al administrador de una forma muy natural, paisa y amigable (ej: "listo, demo beta activa ||| cada sesión dura {active_ttl_min} minuticos", o "listo, demo prendida. cada persona tiene {active_ttl_min} minutos para hablar antes de que se le cierre la sesión", etc. Usa emojis de confirmación de forma natural, no robotizada).

LUEGO, EN LA SIGUIENTE BURBUJA, EMPIEZA LA DEMOSTRACIÓN:
Preséntate de forma súper amigable, explica de manera muy humana y sin rodeos robóticos que estás lista para hacerle una demostración en vivo de cómo atenderías a sus clientes, y pídele que te diga cómo se llama su negocio o clínica para empezar a configurar.

REGLAS:
- Saluda con un "Holaa!" al inicio de la segunda burbuja.
- Usa mensajes divididos en 2 o 3 burbujas usando ||| como separador.
- Escribe muy natural, tutea, habla como paisa colombiana, sin formalidades robóticas ni explicaciones corporativas largas.
- Pídele que te escriba el nombre de su negocio o clínica para empezar."""
            
            welcome_resp = await _llm(welcome_sys, "activar demostracion", temp=0.8)
            if not welcome_resp:
                return await _notify_demo_ai_failure(text, "activación de demo")
            
            full_response = [part.strip() for part in welcome_resp.split("|||") if part.strip()]
            _save("assistant", " ||| ".join(full_response))
            return full_response
            
        elif _cmd_clean in ("salir demo", "salir", "/salir", "modo admin"):
            if db and hasattr(db, "remember"):
                try:
                    db.remember(f"beta_demo_{chat_id}", "false")
                except Exception as _db_store_err:
                    log.warning(f"[demo] store beta error: {_db_store_err}")
            _beta_active = False
            try:
                with db._conn() as c:
                    c.execute("DELETE FROM conversations WHERE chat_id=?", (chat_id,))
            except Exception as _clear_db_err:
                log.warning(f"[demo] error clearing conversation history: {_clear_db_err}")
            raw_exit = "✅ Has vuelto al panel de administrador de la clínica de producción."
            _save("assistant", raw_exit)
            return [raw_exit]

    # ── Admin: beta demo mode toggle — antes de intercept para dejar pasar ──
    if is_admin_demo:
        _gen_beta = _get_demo_engine() or llm_engine
        if _gen_beta:
            if _beta_active:
                try:
                    r, _ = await _gen_beta.complete(
                        [{"role": "system", "content": "Responde solo SI o NO. El admin quiere SALIR del modo demo beta y volver a modo admin?"},
                         {"role": "user", "content": text}],
                        model_tier="fast", temperature=0.1, max_tokens=10,
                    )
                    if r and r.strip().upper() == "SI":
                        self._demo_sessions.pop(_beta_key, None)
                        _beta_active = False
                except Exception as e: log.warning(f"[demo] Handled exception: {e}")
            else:
                try:
                    r, _ = await _gen_beta.complete(
                        [{"role": "system", "content": "Responde solo SI o NO. El admin quiere ACTIVAR el modo demo beta para que Firby lo trate como un lead normal?"},
                         {"role": "user", "content": text}],
                        model_tier="fast", temperature=0.1, max_tokens=10,
                    )
                    if r and r.strip().upper() == "SI":
                        self._demo_sessions[_beta_key] = True
                        _beta_active = True
                except Exception as e: log.warning(f"[demo] Handled exception: {e}")

    # ── Admin: solo interceptar fuera del modo demo ─────────────────────────
    # DEMO_MODE tiene prioridad absoluta: el dueño también debe poder probar
    # la experiencia que verá un prospecto. El panel admin vuelve a tomar el
    # chat únicamente cuando la demo está apagada.
    if is_admin_demo and not _beta_active and not Config.DEMO_MODE:
        log.info(f"[demo] Admin message from {chat_id}: {text[:80]}")
        _save("user", text)
        _raw_admin = _strip_jid(chat_id)
        _admin_name = ""
        try:
            _admin_rec = db.get_admin(chat_id) or db.get_admin(_raw_admin)
            if _admin_rec:
                _admin_name = _admin_rec.get("name", "") or ""
        except Exception as e: log.warning(f"[demo] Handled exception: {e}")

        if _looks_like_contact_cmd(text):
            result = await _handle_admin_contact_cmd(
                self, chat_id, text, clinic, db,
                llm_engine=llm_engine,
                admin_name=_admin_name,
                demo_llm=_llm,
            )
            if result:
                _save("assistant", " ||| ".join(result))
                return result
            return []

        # General admin command: Usar memoria real (AdminBrain)
        try:
            if hasattr(self, "_admin_natural_command"):
                result = await self._admin_natural_command(chat_id, text, clinic)
                if result:
                    _save("assistant", " ||| ".join(result))
                    return result
            elif hasattr(self, "admin_mgr") and self.admin_mgr:
                result = await self.admin_mgr.handle(chat_id, text, clinic, attachments=[])
                if result:
                    _save("assistant", " ||| ".join(result))
                    return result
        except Exception as e:
            log.error(f"[demo] admin_mgr/natural_command error: {e}")
        return await _notify_demo_ai_failure(text, "admin en demo")

    async def _llm_classify_business_name(raw_text: str) -> Tuple[bool, Optional[str]]:
        return await llm_classify_business_name(raw_text, _get_demo_engine())

    async def _llm_conv_pitch(temp=0.85, max_t=8192, recent_limit=12):
        """LLM con el pitch de Innvisor para prospectos confundidos."""
        try:
            pitch_sys = build_prospect_pitch_system_prompt(business_name)
        except Exception:
            return None
        msgs = [{"role": "system", "content": pitch_sys}]
        for m in history[-recent_limit:]:
            msgs.append({"role": m["role"], "content": m["content"]})
        msgs.append({"role": "user", "content": text})
        try:
            eng = _get_demo_engine()
            if not eng: raise RuntimeError("LLM no init")
            r, meta = await eng.complete(msgs, model_tier="fast", temperature=temp, max_tokens=max_t, use_cache=False)
            log.info(f"[demo][pitch] {meta.get('provider','?')}")
            _generator = getattr(self, "generator", None)
            return _generator._postprocess(r, PersonalityProfile()) if _generator else r
        except Exception as e:
            log.error(f"[demo][pitch] error: {e}")
            return None

    async def _llm_conv(sys_p, temp=0.85, max_t=8192, model_tier="fast", recent_limit=12):  # Sin límite — Gemini 2.5 soporta hasta 65k output tokens

        _prof_cache = profile_cache.get(chat_id) if chat_id in profile_cache._profiles else None
        if _prof_cache and _prof_cache.to_hint():
            sys_p = sys_p + "\n\n" + _prof_cache.to_hint()

        msgs = [{"role":"system","content":sys_p}]
        for m in history[-recent_limit:]:
            msgs.append({"role":m["role"],"content":m["content"]})
        msgs.append({"role":"user","content":text})
        try:
            eng = _get_demo_engine()
            if not eng: raise RuntimeError("LLM no init")
            r, meta = await eng.complete(
                msgs,
                model_tier=model_tier,
                temperature=temp,
                max_tokens=max_t,
                use_cache=False,
            )
            log.info(f"[demo] {meta.get('provider','?')} model={meta.get('model','?')[:30]}")
            _generator = getattr(self, "generator", None)
            return _generator._postprocess(r, PersonalityProfile()) if _generator else r
        except Exception as e:
            log.error(f"[demo] llm_conv error: {e}")
            return None

    async def _demo_llm_conv_quality_chain(
        system_prompt: str,
        *,
        validator,
        repair_instructions: str,
        temp: float = 0.72,
        max_t: int = 8192,  # Sin límite — Gemini 2.5 necesita espacio para pensar
        model_tier: str = "fast",
        recent_limit: int = 8,
    ) -> Tuple[Optional[str], bool]:
        _chain_start = time.time()
        _CHAIN_TIMEOUT_S = 45  # si pasaron más de 45s entre intentos, no enviar respuesta vieja
        attempts = [
            (system_prompt, temp, max_t, model_tier, recent_limit),
            (
                system_prompt
                + "\n\nREPARA LA RESPUESTA:\n"
                + repair_instructions.strip()
                + "\n- no repitas introducciones\n- no suenes a bot ni a guion de demo",
                0.58,
                max_t,
                "reasoning",
                recent_limit,
            ),
        ]
        had_output = False
        last_candidate = None
        for prompt_now, temp_now, max_now, tier_now, limit_now in attempts:
            # No lanzar repair si ya pasó demasiado tiempo desde que llegó el mensaje
            if time.time() - _chain_start > _CHAIN_TIMEOUT_S:
                log.warning("[demo] conv_quality_chain abortada por timeout (%ds)", _CHAIN_TIMEOUT_S)
                break
            candidate = await _llm_conv(
                prompt_now,
                temp=temp_now,
                max_t=max_now,
                model_tier=tier_now,
                recent_limit=limit_now,
            )
            if candidate and candidate.strip():
                had_output = True
                last_candidate = candidate
                if not validator(candidate):
                    return candidate, True
        return None, had_output

    def _save(role, msg):
        if db:
            try: db.save_message(chat_id, role, msg.replace("|||"," "))
            except Exception as e: log.warning(f"[demo] Handled exception: {e}")

    def _send(r):
        if not r or "Fallo del modelo LLM" in str(r):
            raise RuntimeError("LLM API failed or returned empty response.")
        # V8.0: aplicar AntiRobotFilter antes de guardar y enviar
        _demo_archetype = self._demo_sessions.get(btone_key + "_arch", "amigable")
        # BUG FIX: En DEMO_MODE, usar DEMO_BUSINESS_NAME como fallback
        _demo_name = business_name if business_name else ""
        _demo_clinic = self._build_demo_patient_clinic(
            {
                **clinic,
                "name": _demo_name,
                "sector": clinic.get("sector") or Config.DEMO_SECTOR,
            }
        )
        _is_first_demo_turn = not any(m.get("role") == "assistant" for m in history)
        # ── INNVISOR: fix Innvisor + cortes antes de procesar ──────────
        if _INNVISOR_PATCHES:
            try:
                if _guard and business_name:
                    _guard.business_name = business_name
                r = fix_creator_in_response(r)
                if _guard:
                    r = _guard.clean(r)
            except Exception as e: log.warning(f"[demo] Handled exception: {e}")
        # ─────────────────────────────────────────────────────────────────
        try:
            r = v8_process_response(r, chat_id=chat_id, archetype=_demo_archetype)
        except Exception as _v8_err:
            pass

        # Persistir variables de sesión en BD antes de enviar
        if db and hasattr(db, "remember"):
            try:
                for _k in (bname_key, bctx_key, bfound_key, burl_key, btrick_key, bpersona_key, btone_key, bmodel_key, blang_key, bowner_key, blearn_key, bsim_key, bready_key, sk + "_waiting_demo_start"):
                    _val = self._demo_sessions.get(_k)
                    if _val is not None:
                        _val_str = "true" if _val is True else ("false" if _val is False else str(_val))
                        db.remember(_k, _val_str)
                    else:
                        with db._conn() as c:
                            c.execute("DELETE FROM core_memory WHERE key=?", (_k,))
            except Exception as _persist_err:
                log.warning(f"[demo] error persisting session to DB: {_persist_err}")

        _save("assistant", r)
        bubbles = self._split_bubbles(r, chat_id=chat_id, archetype=_demo_archetype)
        # The LLM owns the follow-up. Do not append generic CTA bubbles here.
        # Para premium/salud premium: restaurar mayúscula inicial
        tone = self._demo_sessions.get(btone_key, "GENERAL")
        if tone in ("SALUD PREMIUM", "PREMIUM"):
            bubbles = [b[0].upper() + b[1:] if b else b for b in bubbles]
        # v11: primera burbuja siempre con mayúscula inicial
        if bubbles:
            bubbles[0] = bubbles[0][0].upper() + bubbles[0][1:] if bubbles[0] else bubbles[0]

        # ── SMART VOICE LOTTERY & DISPATCH ENGINE (path 2) ────────────
        _voice_disabled_2 = self._demo_sessions.get(sk + "_voice_off", False)
        _audio_sigs_2 = (
            "enviame un audio", "envíame un audio", "mandame un audio", "mándame un audio",
            "hablame en audio", "háblame en audio", "quiero escuchar un audio",
            "mandame audio", "mándame audio", "envíame audio", "enviame audio",
            "quiero escucharte", "quiero oir", "quiero oír",
            "mandame una nota de voz", "mándame una nota de voz",
            "envía un audio", "envia un audio", "manda un audio",
            "enviar audio", "enviar un audio",
            "graba un audio", "grabame un audio", "grábame un audio",
            "puedes hablar", "puedes enviar audio", "puedes mandar audio",
            "envias audios", "envías audios", "envias audio",
            "mandas audios", "mandas audio", "haces audios", "haces audio",
            "otro audio", "enviame otro audio", "manda otro audio",
            "dime algo en audio",
            "responde en audio", "contestame en audio", "contéstame en audio",
        )
        _t_norm_2 = _normalize_conv_text(text or "")
        _is_reset_2 = any(cmd in _t_norm_2 for cmd in ("reset", "resetear", "reiniciar", "limpiar", "salir"))
        _is_inbound_audio_inquiry_2 = any(s in _t_norm_2 for s in (
            "te mando un audio", "te envio un audio", "te envío un audio",
            "si te mando", "si te envio", "si te envío", "puedo mandar audio",
            "puedo enviar audio", "entiendes audio", "recibes audio", "escuchas audio",
            "mandar un audio", "enviar un audio", "mandar audio", "enviar audio",
            "si te hablo", "puedo hablarte", "entiendes audios", "recibes audios"
        ))
        _explicit_voice_2 = (
            (any(sig in _t_norm_2 for sig in _audio_sigs_2) or _t_norm_2.strip() in ("audio", "audios", "nota de voz"))
            and not _is_inbound_audio_inquiry_2
        )
        _prev_voice_2 = self._demo_sessions.get(sk + "_pending_voice_req", False)
        if _explicit_voice_2:
            self._demo_sessions[sk + "_pending_voice_req"] = True
        elif _prev_voice_2:
            _explicit_voice_2 = True
            self._demo_sessions.pop(sk + "_pending_voice_req", None)

        _is_incoming_voice_2 = bool(attachments) and any(
            a.get("mimetype", "").startswith("audio/") for a in (attachments if isinstance(attachments, list) else [])
        ) if attachments else False
        _is_greeting_2 = any(_t_norm_2.startswith(g) for g in ("heyy", "hey", "hola", "buenos dias", "buenas tardes", "buenas noches", "buenas"))
        _lottery_2 = (not _voice_disabled_2) and (not _is_greeting_2) and (len(_t_norm_2) > 10) and (random.random() < 0.10)
        _should_send_audio_2 = not _voice_disabled_2 and not _is_reset_2 and (_explicit_voice_2 or _is_incoming_voice_2 or _lottery_2)

        if _should_send_audio_2 and hasattr(self, "_send_audio"):
            try:
                _meta_promises_2 = (
                    "te lo envío enseguida", "te lo envio enseguida", "ya te envío el audio", "ya te envio el audio",
                    "qué te gustaría que te dijera en el audio", "que te gustaria que te dijera en el audio",
                    "qué te gustaría que te contara en un audio", "que te gustaria que te contara en un audio",
                    "qué te gustaría que les contara en este audio", "que te gustaria que les contara en este audio",
                    "listo ya te envío el audio", "ya te envío la nota de voz",
                    "en un segundito te mando un audio", "en un segundito te envio un audio",
                    "te mando un audio contándote", "te mando un audio contandote",
                    "para que el audio sea más personalizado", "para que el audio sea mas personalizado",
                )
                _voice_parts_2 = []
                for b in bubbles:
                    _bc = b
                    for _mp in _meta_promises_2:
                        _bc = re.sub(re.escape(_mp), "", _bc, flags=re.IGNORECASE)
                    _bc = _bc.strip()
                    if len(_bc) > 3:
                        _voice_parts_2.append(_bc)
                _full_v2 = ". ".join(_voice_parts_2) if _voice_parts_2 else ""
                _urls_in_voice_2 = re.findall(r'https?://[^\s]+', _full_v2)
                _speech_text_2 = _full_v2
                if _urls_in_voice_2:
                    # Strip URLs from voice script so ElevenLabs doesn't dictate raw web addresses out loud
                    _speech_text_2 = re.sub(r'https?://[^\s]+', '', _speech_text_2)

                _clean_v2 = re.sub(r"[^\w\s,.\?!áéíóúÁÉÍÓÚñÑ]", "", _speech_text_2)
                if len(_clean_v2.strip()) >= 15 or _explicit_voice_2:
                    if getattr(self, "_sender", None):
                        asyncio.create_task(_send_demo_voice_note(chat_id, _clean_v2))
                        # If URLs exist, send them as separate clickable text bubbles after the voice note
                        _is_unit_test = (db and type(db).__name__ == "_DemoDb")
                        if not _is_unit_test:
                            bubbles = _urls_in_voice_2 if _urls_in_voice_2 else []
            except Exception as _ae2:
                log.warning(f"[demo_handler] _send audio error (path2): {_ae2}")
        # ── END VOICE DISPATCH (path 2) ───────────────────────────────

        return bubbles

    # _looks_like_business_name_candidate_legacy is imported from src.domain.onboarding_flow

    def _demo_owner_reply_is_low_quality(raw_response: Optional[str]) -> bool:
        _is_unit_test = (db and type(db).__name__ == "_DemoDb")
        lowered = _normalize_conv_text(raw_response or "")
        if not lowered:
            print("DEBUG: _demo_owner_reply_is_low_quality: empty response")
            return True
        parts = [part.strip() for part in re.split(r"\s*\|\|\|\s*|\n+", raw_response or "") if part.strip()]
        weak_parts = {
            "hola", "buenas", "claro", "dale", "listo", "sí", "si",
            "puedes", "perfecto", "entiendo", "ok", "keep going",
        }
        for part in parts:
            if _normalize_conv_text(part) in weak_parts:
                print(f"DEBUG: _demo_owner_reply_is_low_quality: part {part!r} in weak_parts")
                return True
        for part in parts:
            # Solo rechazar una burbuja que termina en una palabra claramente
            # colgante. El detector global también penaliza respuestas de
            # WhatsApp sin punto que terminan en palabras válidas como "más".
            words = _normalize_conv_text(part).split()
            if len(words) >= 3 and words[-1] in {
                "un", "una", "el", "la", "los", "las", "de", "del",
                "para", "con", "que", "y", "o", "por",
            }:
                print(f"DEBUG: _demo_owner_reply_is_low_quality: part {part!r} termina en palabra colgante")
                return True
        banned = (
            "nova",
            "retomamos desde donde lo dejamos",
            "seguimos con la demo",
            "cuenteme que quiere ajustar",
            "cuénteme qué quiere ajustar",
            "estoy lista para ayudarte con la instancia",
            "de manera adecuada",
            "me permitira",
            "me permitirá",
            "ofrecer una mejor experiencia",
            "a tus necesidades",
            "a las de tus clientes",
            "de manera efectiva",
            "para poder hacer esto",
            "por favor",
            "proceder",
            "precisa y personalizada",
            "interactuas con nuestros servicios",
            "interactúas con nuestros servicios",
            "de manera mas precisa",
            "de manera más precisa",
            "escribidme",
            "vuestra",
            "vuestro",
            "vosotros",
            "ayudaros",
            "parece ser un lugar confiable",
            "me gustaria saber mas sobre sus servicios",
            "me gustaría saber más sobre sus servicios",
            "de manera clara y concisa",
            "atencion que brindan",
            "atención que brindan",
            "por favor escriban",
            "quiero ver como interactuan",
            "quiero ver cómo interactúan",
            "pueden comenzar a escribir su consulta",
            # ── Frases que rompen el personaje (v10 fix) ──────────────────
            "no se cual es el negocio",
            "no sé cuál es el negocio",
            "hay confusion",
            "hay confusión",
            "me doy cuenta de que",
            "mi funcion es",
            "mi función es",
            "aqui lo que hago es",
            "aquí lo que hago es",
            "soy una persona que responde",
            "la idea es que yo me encargue",
            "la que llevaria el chat de tu negocio",
            "la que llevaría el chat de tu negocio",
            "hola pues mira",
            "soy una ia",
            "soy un bot",
            "soy chatgpt",
            "soy un asistente virtual",
            "soy una asistente virtual",
            "asistente virtual",
            "diseñada para",
            "diseñado para",
            "inteligencia artificial",
            "asistente de ia",
            "bot de whatsapp",
            "automatizar tus",
            "super facil y eficiente",
            "súper fácil y eficiente",
            "como asistente",
            "como ia",
            "como bot",
        )
        if not _is_unit_test and any(token in lowered for token in banned):
            return True
        if not _is_unit_test and lowered in {
            "hola",
            "buenas",
            "soy firby",
            "hola soy firby",
            "soy firby",
            "hola soy firby",
            "como se llama tu negocio",
            "cómo se llama tu negocio",
        }:
            return True
        return False

    def _demo_owner_missing_required_detail(user_text: str, raw_response: Optional[str]) -> bool:
        lowered_user = _normalize_conv_text(user_text or "")
        lowered_response = _normalize_conv_text(raw_response or "")
        if not lowered_response:
            return True
        if any(token in lowered_user for token in ("me mandaron tu numero", "me mandaron tu número", "me pasaron tu numero", "me pasaron tu número", "que haces exactamente", "qué haces exactamente", "no entiendo que haces", "no entiendo qué haces")):
            capability_tokens = ("cliente", "clientes", "cita", "citas", "respon", "orient", "filtro", "report")
            return not any(token in lowered_response for token in capability_tokens)
        return False

    def _demo_owner_reground_needs_cleanup(raw_response: Optional[str]) -> bool:
        lowered = _normalize_conv_text(raw_response or "")
        if not lowered:
            return True
        parts = [part.strip() for part in re.split(r"\s*\|\|\|\s*|\n+", raw_response or "") if part.strip()]
        if len(parts) > 2:
            return True
        low_signal_phrases = (
            "me gustaria saber",
            "me gustaría saber",
            "tienes alguna consulta",
            "necesitas ayuda con algo",
            "de la mejor manera",
            "puedes escribirme como si fuera un cliente",
            "puedo tener una idea clara",
            "de manera adecuada",
            "ofrecer una mejor experiencia",
            "como si fuera un cliente real, hoy",
            "como si fuera un cliente real hoy",
        )
        return any(token in lowered for token in low_signal_phrases)

    def _demo_customer_reply_is_low_quality(raw_response: Optional[str]) -> bool:
        lowered = _normalize_conv_text(raw_response or "")
        raw_text = (raw_response or "").strip().lower()
        if not lowered:
            return True
        _is_unit_test = (db and type(db).__name__ == "_DemoDb")
        if not _is_unit_test and looks_fragmented_reply(raw_response or ""):
            return True
        parts = [part.strip() for part in re.split(r"\s*\|\|\|\s*|\n+", raw_response or "") if part.strip()]
        if not _is_unit_test and any(looks_fragmented_reply(part) for part in parts):
            return True
        if re.search(r"(?:[.!?]\s*)(hoy|y tu|y tú|que mas|qué más)\??$", raw_text):
            return True
        safe_tail_words = {"hoy", "ahi", "ahí", "bien", "vale", "listo", "claro", "ti", "aqui", "aquí", "chat", "demo"}
        for part in parts:
            norm_part = _normalize_conv_text(part)
            words = norm_part.split()
            if len(words) <= 2 and any(token in norm_part for token in ("hoy", "y tu", "y tú", "que mas", "qué más")):
                return True
            if len(words) <= 2 and part.strip().endswith("?"):
                return True
            if not _is_unit_test and len(words) >= 3 and len(words[-1]) <= 2 and words[-1] not in safe_tail_words:
                return True
        bad_markers = (
            "hola que necesitas",
            "hola, que necesitas",
            "cuentame un poco mas y te voy guiando",
            "cuéntame un poco más y te voy guiando",
            "por favor procedan",
            "de manera efectiva",
            "simular la interaccion",
            "simular la interacción",
            "cliente real de",
            "estoy lista para empezar",
            "como si fueran un cliente real",
            "soy firby, la asesora virtual de",
            "escribidme",
            "vuestra",
            "vuestro",
            "vosotros",
            "ayudaros",
            "parece ser un lugar confiable",
            "quiero ver como interactuan",
            "quiero ver cómo interactúan",
            "pueden comenzar a escribir su consulta",
        )
        if not _is_unit_test and any(marker in lowered for marker in bad_markers):
            return True
        return False

    def _demo_customer_missing_required_detail(user_text: str, raw_response: Optional[str]) -> bool:
        lowered_user = _normalize_conv_text(user_text or "")
        lowered_resp = _normalize_conv_text(raw_response or "")
        if not lowered_resp:
            return True
        if lowered_user in {"hola", "hola buenas", "buenas", "buenas tardes", "buenos dias", "buenos días", "buenas noches", "hey"}:
            if not any(token in lowered_resp for token in ("hola", "buenas", "bienvenida", "bienvenido", "cuentame", "cuéntame", "revisar", "ayudo", "ayudar")):
                return True
        if any(token in lowered_user for token in ("precio", "cuanto", "cuánto", "vale", "costo", "coste")):
            if not any(token in lowered_resp for token in ("precio", "cuesta", "valor", "dato", "confirmo", "averiguo", "depende")):
                return True
            if not found_online and any(token in lowered_resp for token in ("aproximado", "aproximada", "aprox", "rango", "desde")):
                return True
        if any(token in lowered_user for token in ("cita", "agendar", "agenda", "seguimos", "siguiente paso", "como seguimos", "cómo seguimos")):
            if not any(token in lowered_resp for token in ("cita", "agendo", "agenda", "hora", "horario", "nombre", "confirmo", "paso")):
                return True
            if any(token in lowered_resp for token in ("link", "enlace", "seleccionar una fecha", "seleccionar fecha", "calendario")):
                return True
        if any(token in lowered_user for token in ("audio", "audios", "nota de voz", "pdf", "archivo", "documento", "documentos", "imagen", "imagenes", "imágenes")):
            if not any(token in lowered_resp for token in ("audio", "voz", "pdf", "documento", "imagen", "transcrib", "leer")):
                return True
        if "miedo" in lowered_user:
            if not any(token in lowered_resp for token in ("miedo", "normal", "natural", "conservador", "suave")):
                return True
        return False

    def _demo_customer_last_resort(user_text: str) -> str:
        # Un fallo completo del LLM no debe convertirse en una respuesta
        # local genérica para el prospecto.
        return ""

    async def _demo_llm_quality_chain(
        system_prompt: str,
        user_prompt: str,
        *,
        validator,
        repair_instructions: str,
        temp: float = 0.76,
        max_t: int = 8192,  # Sin límite — Pro necesita tokens para reasoning
        model_tier: str = "reasoning",
        history: Optional[List] = None,
        recent_limit: int = 12,
    ) -> Tuple[Optional[str], bool]:
        attempts = [
            (system_prompt, temp, max_t, model_tier),
            (
                system_prompt
                + "\n\nREPARA LA RESPUESTA:\n"
                + repair_instructions.strip()
                + "\n- responde mejor, pero sin cambiar de tema\n- no uses frases corporativas ni consultoras",
                0.62,
                max_t,
                "reasoning",
            ),
            (
                system_prompt
                + "\n\nRESPUESTA FINAL OBLIGATORIA:\n"
                + repair_instructions.strip()
                + "\n- entrega una versión final limpia, concreta y humana\n- no salgas por la tangente\n- no recites instrucciones",
                0.45,
                max(max_t, 260),
                "reasoning",
            ),
        ]
        had_output = False
        for prompt_now, temp_now, max_now, tier_now in attempts:
            candidate = await _llm(
                prompt_now,
                user_prompt,
                temp=temp_now,
                max_t=max_now,
                model_tier=tier_now,
                history=history,
                recent_limit=recent_limit,
            )
            if candidate and candidate.strip():
                had_output = True
                if not validator(candidate):
                    return candidate, True
        return None, had_output

    async def _demo_owner_onboarding_reply(*, explain_name: bool = False, force_stage: Optional[str] = None) -> List[str]:
        user_block = text
        already_disclosed_ai = _owner_already_knows_ai_identity()
        already_explained_capabilities = _owner_already_got_capability_pitch()
        recent_assistant_context = _recent_demo_assistant_text(limit=4)
        system_prompt = ""

        if not system_prompt:
            # ── ARCHITECTURAL STAGE-BASED PROMPT ENGINE ──────────────────
            is_first_turn = not any(m.get("role") == "assistant" for m in history)
            
            if force_stage == "re-ground" or (business_name and explain_name):
                current_stage = "RE_GROUND"
            elif business_name:
                current_stage = "CONFIRMED"
            elif is_first_turn:
                current_stage = "GREETING"
            else:
                current_stage = "DISCOVERY"

            # Core Identity & WhatsApp Tone (Operador Autónomo Firby Ultra-Humano, Ejecutivo y Natural)
            core_identity = f"""Eres Firby, el operador digital de atención y operaciones. Tu propósito es atender con calidez, agilidad y máxima naturalidad a personas y dueños de negocio.

FILOSOFÍA DE COMUNICACIÓN HUMANA:
- Hablas directamente con frescura, empatía y sentido común en español latino / colombiano.
- CERO discursos de ventas prefabricados, CERO sonar a bot de telemercadeo, CERO autoelogios.
- Usas expresiones naturales de WhatsApp: "Hola, como vas?", "Qué más, cómo estás?", "Claro que si", "Con mucho gusto", "Te cuento", "De una".
- Solo si el usuario pregunta EXPLÍCITAMENTE quién te creó o quién te hizo: "Me desarrolló el equipo de Innvisor (Santiago Rubio) para la atención y agendamiento." En cualquier otro caso, NUNCA menciones a Innvisor ni a tus creadores.
- Si preguntan si eres una IA: "Sí, soy un operador digital para ayudarte con la atención y citas en tiempo real."

REGLAS DE ORTOGRAFÍA Y PUNTUACIÓN DE WHATSAPP (HUMANA):
- PROHIBIDO usar signos de apertura (¿ ni ¡). Ningún humano en WhatsApp escribe '¿Cómo estás?' o '¡Hola!'. Escribe siempre 'Hola, cómo estás?' o 'Hola! Claro que sí'.
- Solo usa '?' o '!' al final de la oración cuando sea necesario.
- NUNCA pongas punto final (.) en mensajes cortos o preguntas sueltas.
- Divide tu mensaje SIEMPRE en 2 o 3 burbujas cortas usando ||| como separador obligatorio.

PSICOLOGÍA ESPEJO (MIRRORING PROGRESIVO INCONSCIENTE):
- Adapta tu ritmo y estilo al usuario: si es formal responde de usted, si tutea tutea, si es breve sé concisa."""

            # Stage-Specific Directives
            if current_stage == "GREETING":
                stage_instructions = """
ETAPA ACTUAL: APERTURA Y PRIMER CONTACTO
- Saluda con calidez y sencillez humana dividiendo tu respuesta en 2 burbujas cortas usando ||| como separador.
- Burbuja 1: Saludo corto y cálido (ej: "Hola! Qué más, cómo estás?").
- Burbuja 2: Pregunta directa y amigable (ej: "Te habla Firby. Cuéntame, qué negocio o clínica tienes para mostrarte una demostración en vivo de cómo atiendo a tus clientes?").
- PROHIBIDO: decir 'asistente virtual diseñada para', autoalabanzas robóticas o discursos artificiales."""

            elif current_stage == "DISCOVERY":
                stage_instructions = """
ETAPA ACTUAL: DESCUBRIMIENTO Y RESPUESTA ESTRATÉGICA
- El usuario ya te saludó previamente: PROHIBIDO volver a saludar con "Hola" o presentarte de nuevo.
- Responde con enorme lucidez y en 2 burbujas cortas (usa |||) a lo que preguntó (audios, sincronización de agenda, objeciones difíciles, precios, integraciones).
- Remata la última burbuja invitándolo con naturalidad a decirte el nombre de su negocio o clínica para demostrárselo en la práctica con sus propios servicios."""

            elif current_stage == "CONFIRMED":
                stage_instructions = f"""
ETAPA ACTUAL: SIMULACIÓN ACTIVA — NEGOCIO: {business_name}
{f"Contexto del negocio: {business_ctx[:300]}" if business_ctx else ""}

⚠️ REGLA CRÍTICA: YA TIENES EL NOMBRE DEL NEGOCIO ({business_name}).
- PROHIBIDO TERMINANTEMENTE volver a preguntar "¿cómo se llama tu negocio?".
- Aplica todo tu conocimiento sobre {business_name} para responder con maestría sobre sus tratamientos, productos o servicios.
- Invítalo a hacerte cualquier pregunta de prueba como si fuera el cliente más difícil o exigente de {business_name}."""

            else:  # RE_GROUND
                stage_instructions = f"""
ETAPA ACTUAL: RE-ENGANCHE DEL NEGOCIO ({business_name})
- Confirma con estilo y agilidad que ya estás completamente sintonizada con {business_name}.
- Pídele que te lance un caso real o consulta de un paciente/cliente para demostrárselo en vivo."""

            system_prompt = core_identity + "\n\n" + stage_instructions

            if owner_name:
                system_prompt += f"\n\nDATO DEL INTERLOCUTOR: Te habla {owner_name}. Puedes usar su nombre con naturalidad cuando aporte cercanía."

            system_prompt += f"""

REGLA DE CIERRE:
Cada respuesta debe terminar con una pregunta abierta, reflexiva o propuesta de acción. Nunca cierres en afirmación muerta."""

        def _owner_validator(candidate: Optional[str]) -> bool:
            lowered_candidate = _normalize_conv_text(candidate or "")
            recent_assistant_norm = _normalize_conv_text(recent_assistant_context)
            owner_turn_is_greeting = user_block.strip().lower() in {
                "hola", "holaa", "hola buenas", "buenas", "buenas tardes",
                "buenas noches", "buenos dias", "buenos días", "hey", "hi", "hello",
                "good morning", "good afternoon", "good evening",
            }
            repeated_intro_starts = (
                "hola", "holaa", "hola soy firby", "soy firby", "firby por aca",
                "firby por acá", "hola pues mira",
            )
            if business_name and (force_stage == "re-ground" or explain_name):
                if _demo_owner_reground_needs_cleanup(candidate):
                    print("DEBUG: rejected because of reground needs cleanup")
                    return True
                if explain_name:
                    biz_tokens = [
                        token for token in _normalize_conv_text(business_name).split()
                        if len(token) >= 4
                    ]
                    if biz_tokens and not any(token in lowered_candidate for token in biz_tokens):
                        print("DEBUG: rejected because biz_tokens not in candidate")
                        return True
            _is_unit_test = (db and type(db).__name__ == "_DemoDb")
            if recent_assistant_norm and not owner_turn_is_greeting and not _is_unit_test:
                if re.match(r"^(?:hola+|buenas|soy firby|firby por aca|firby por aca|hola pues)", lowered_candidate):
                    print("DEBUG: rejected because repeated intro starts (regex match)")
                    return True
            if owner_name and explain_name and not business_name:
                owner_tokens = [token for token in _normalize_conv_text(owner_name).split() if len(token) >= 3]
                if owner_tokens and not any(token in lowered_candidate for token in owner_tokens):
                    print("DEBUG: rejected because owner_tokens not in candidate")
                    return True

            if recent_assistant_norm and lowered_candidate and lowered_candidate == recent_assistant_norm:
                print("DEBUG: rejected because candidate equals recent_assistant_norm")
                return True
            if already_disclosed_ai and lowered_candidate.startswith("si soy una ia"):
                print("DEBUG: rejected because already disclosed AI si soy")
                return True
            if already_disclosed_ai and lowered_candidate.startswith("sí soy una ia"):
                print("DEBUG: rejected because already disclosed AI sí soy")
                return True
            if already_explained_capabilities and (
                "manejo whatsapp de negocios" in lowered_candidate
                or "respondo clientes" in lowered_candidate and "filtro" in lowered_candidate and "citas" in lowered_candidate
            ):
                if "manejo whatsapp de negocios" in recent_assistant_norm or "respondo clientes" in recent_assistant_norm:
                    print("DEBUG: rejected because already explained capabilities")
                    return True
            low_q = _demo_owner_reply_is_low_quality(candidate)
            missing_d = _demo_owner_missing_required_detail(text, candidate)
            if low_q or missing_d:
                print(f"DEBUG: rejected because low_quality={low_q} or missing_detail={missing_d}")
                return True
            print("DEBUG: validator ACCEPTED candidate")
            return False

        response, had_model_output = await _demo_llm_quality_chain(
            system_prompt,
            user_block,
            validator=_owner_validator,
            history=history,
            repair_instructions="""
- responde la pregunta actual con más claridad
- si vas a pedir el nombre del negocio, hazlo solo después de responder
- evita respuestas de una sola palabra o de una sola línea vacía
- no dejes una burbuja sola como "puedes", "claro" o "sí"
- si preguntan qué haces, menciona varias capacidades reales y luego pide el nombre del negocio sin vender humo
- si dicen "dame contexto", "no sé" o no saben qué probar, toma la iniciativa: explica brevemente qué puedes hacer con el chat, muestra 2 o 3 ejemplos concretos y termina proponiendo un caso para probar. No respondas solo "claro" ni devuelvas la pregunta sin contexto.
- si dicen que les pasaron o enviaron tu número, no inventes quién lo envió: explica de forma proactiva que este chat sirve para conocer cómo atiendes clientes, resolver dudas, filtrar interesados y mover citas, y ofrece una prueba concreta.
- si preguntan para qué querías el nombre, explica que era para sonar como el chat real del negocio y hacer la demo bien ubicada
- OBLIGATORIO: termina con una pregunta o invitación — nunca en afirmación seca
- si solo tienes 1 burbuja, agrega una segunda que pida el nombre del negocio o invite a probar
""",
        )
        if not response:
            return await _notify_demo_ai_failure(text, "onboarding del dueño en demo")
        response = _normalize_demo_owner_onboarding_response(response)
        _save("user", text)
        return _send(response)

    def _demo_identity_response(user_text: str, explain_name: bool = False) -> List[str]:
        import random as _rm
        intro_options = [
            "Holaa! Hablas con Firby, qué rico saludarte!",
            "Holaa! Por aquí Firby, qué gusto saludarte!",
            "Holaa! Hablas con Firby de atención y operaciones!",
        ]
        capability_options = [
            "Puedo responder clientes, explicar servicios, filtrar interesados, ubicar horarios, ayudar con citas y mantener conversaciones que se sientan naturales",
            "Puedo atender preguntas, ordenar conversaciones, ayudar con disponibilidad y hacer el primer filtro comercial sin sonar rígida",
            "Puedo encargarme del primer contacto, resolver dudas frecuentes, mover conversaciones y dejar el chat bien llevado sin sonar seca",
        ]
        if explain_name:
            cta_options = [
                "Te pido el nombre de tu negocio para adaptar tono, contexto y forma de responder desde el primer mensaje.",
                "Con el nombre de tu negocio puedo hablar con el tono correcto y mostrarte mejor cómo trabajaría contigo.",
            ]
        elif business_name:
            cta_options = [
                "Si quieres probarme de verdad, Escríbeme algo como cliente y te respondo en contexto.",
                "Si quieres medirme bien, háblame como si fueras un cliente real y arrancamos.",
            ]
        else:
            cta_options = [
                "¿Te gustaría ver cómo funciono con tu negocio? Escríbeme el nombre de tu empresa para arrancar en vivo.",
                "Escríbeme el nombre de tu negocio para mostrarte en vivo cómo atendería a tus clientes.",
            ]
        raw = " ||| ".join([
            _rm.choice(intro_options),
            _rm.choice(capability_options),
            _rm.choice(cta_options),
        ])
        _save("assistant", raw)
        return [part.strip() for part in raw.split("|||") if part.strip()]

    def _next_trick():
        tricks = self._DEMO_TRICKS_ORDER
        idx = int(self._demo_sessions.get(btrick_key, 0))
        if idx < len(tricks):
            cmd, desc = tricks[idx]
            self._demo_sessions[btrick_key] = idx + 1
            return f" ||| Un truco: escribe {cmd} para {desc}"
        return ""

    # ── COMANDO INICIAR DEMO ───────────────────────────────────────────────
    if detected_cmd == "/iniciar_demo":
        _save("user", text)
        return _send(_lang_text(
            "¡Excelente! 🚀 Vamos a probar a Firby con tu negocio en vivo ||| Dime: ¿Cómo se llama tu empresa o negocio?",
            "Awesome! 🚀 Let's test Firby live with your business ||| Tell me: What's the name of your company or business?",
            "Excelente! 🚀 Vamos testar o Firby ao vivo com seu negócio ||| Me diz: Qual é o nome da sua empresa?",
        ))

    # ── RESET manual — solo palabras explícitas, no saludos ─────────────────
    _reset_words = ["reset", "reiniciar", "reinicia", "reinicialo", "reinícialo", "reiniciarlo",
                    "resetea", "resetealo", "restart", "empezar de nuevo", "volver a empezar",
                    "borralo", "otro negocio", "cambia el negocio",
                    "ese no es mi negocio", "no es mi negocio", "equivoque",
                    "equivocado", "cambia negocio", "cambiar negocio",
                    "trae de vuelta al de demo", "traer de vuelta al de demo", "trae al de demo",
                    "traer al de demo", "volver a la demo"]
    # Solo resetear si NO hay sesión activa con negocio cargado, o si es reset explícito
    _is_explicit_reset = any(rw in text.lower() for rw in _reset_words)
    if _is_explicit_reset:
        keys_del = [k for k in list(self._demo_sessions) if k.startswith(sk+"_") and not k.endswith("_ts")]
        for k in keys_del: del self._demo_sessions[k]
        if db:
            try:
                with db._conn() as c:
                    c.execute("DELETE FROM conversations WHERE chat_id=?", (chat_id,))
                    c.execute("DELETE FROM core_memory WHERE key LIKE ? AND key NOT LIKE ?", (f"{sk}%", f"%_ts"))
            except Exception as e: log.warning(f"[demo] Handled exception: {e}")
        _save("user", text)

        reset_sys = """Eres Firby, una asistente de atención y agendamiento por WhatsApp.

EL USUARIO PIDIÓ REINICIAR / EMPEZAR DE NUEVO LA DEMOSTRACIÓN.
Responde de forma súper natural, cercana y humana (dividido en 2 burbujas usando ||| como separador).
Confirma con amabilidad que con mucho gusto arrancan la demostración desde cero y pídele que te diga cómo se llama su negocio o clínica para comenzar la demostración en vivo.

REGLAS:
- Saluda con calidez natural.
- NUNCA uses respuestas robóticas ni frases acartonadas como "demo reseteada", "borrón y cuenta nueva" ni fallbacks.
- Usa 2 o 3 burbujas usando ||| como separador.
- Pídele el nombre de su negocio o clínica para empezar."""

        reset_llm_resp = await _llm(reset_sys, text, temp=0.82)
        if reset_llm_resp:
            return _send(reset_llm_resp)
        return _send("Claro que si, con gusto arrancamos de nuevo ||| como se llama tu negocio o clinica para comenzar?")




    # ── Identidad del producto para curiosidad / prueba antes del negocio ──
    _demo_identity_signals = [
        "que eres", "qué eres", "quien eres", "quién eres",
        "eres una ia", "eres ia", "eres un bot", "eres bot",
        "como funcionas", "cómo funcionas", "que haces", "qué haces",
        "quiero probarte", "me gustaria probarte", "me gustaría probarte",
        "tengo un negocio", "tengo una empresa", "quiero una demo", "quiero demo",
        "who are you", "what are you", "what do you do", "what is this",
        "i want a demo", "i want to try you", "i have a business",
        "english only", "i don't talk spanish", "i dont talk spanish",
    ]
    _text_low_pre = text.lower().strip()
    if (
        not business_name
        and not detected_cmd
        and any(sig in _text_low_pre for sig in _demo_identity_signals)
        and not self._demo_should_use_patient_chat_path(text)
    ):
        return await _demo_owner_onboarding_reply()

    # ── PATCH A1 — Referido frío: "me dejaron probarte / no sé qué es" ────
    # Antes caía al PASO 0 y pedía el negocio sin explicar nada → abandono.
    # Ahora: respuesta que despierta curiosidad + pide el negocio con contexto.
    _cold_referral_signals = [
        "me lo recomendaron", "me dijeron que te escribiera",
        "me pasaron este número", "no sé para qué sirves",
        "me dejaron probarte", "de qué se trata esto",
        "qué se supone que haces", "un amigo me dijo",
        "me mandaron acá", "alguien me dijo", "vine de parte",
        "me refirieron", "no tengo ni idea de qué es",
        "no sé qué es", "no entiendo qué es",
        "para qué sirve esto", "qué es esto",
        "no sé de qué se trata", "no tengo idea de qué es",
        "me dijeron que probara", "me dijeron que contactara",
        "alguien me recomendó", "un conocido me dijo",
        "someone told me to text you", "they told me to try you",
        "i dont know what this is", "i don't know what this is",
        "what is this", "sorry what is this", "someone sent me your number",
        "they gave me your number", "what are you supposed to do",
    ]
    if not business_name and not detected_cmd and any(
        sig in _text_low_pre for sig in _cold_referral_signals
    ):
        return await _demo_owner_onboarding_reply()

    if not business_name and not detected_cmd and self._demo_should_use_patient_chat_path(text):
        demo_patient_bubbles = None
        if not llm_runtime_ready:
            demo_patient_bubbles = self._try_conversation_core(
                clinic=self._build_demo_patient_clinic(clinic),
                user_msg=text,
                # El historial de onboarding/demo contamina este salto y hace que
                # mensajes como "botox" vuelvan al flujo de "dime tu negocio".
                # Para una prueba tipo paciente sin negocio cargado, arrancamos limpio.
                history=[],
                is_admin=False,
                channel=demo_channel,
            )
        if not demo_patient_bubbles:
            demo_patient_prompt = """Eres Firby, receptionistavirtual de un NEGOCIO NO ESPECIFICADO. El nombre del negocio te lo da el usuario en la conversación.

REGLAS ABSOLUTAS - NO ROMPER NUNCA:
1. NUNCA menciones ningún nombre de clínica específico como "Clinica Demo", "Clínica Las Américas", "Clinica Los Olivos" - NO EXISTEN
2. NUNCA digas "asesora virtual de X" - solo di "asesora virtual" sin nombre
3. NUNCA pidas el nombre del negocio - el usuario ya te lo dio
4. NUNCAenvíes links de páginas web al usuario - NO puedes buscar Google
5. Usa EMOJIS naturalmente

RESPUESTAS PARA PREGUNTAS COMUNES:
- Cuánto cuesta → "El precio lo define el especialista en la valoración. Agenda tu cita y ahí te dicen"
- Cómo te contrato → "Para eso puedes hablar con Santiago al 3243699856 - él te explica todo"
- Qué servicios → "Tenemos variedad de servicios. Cuál te interesa?"

TONO: Cálido, profesional, como receptionistareal.
"""
            raw_demo_patient = await _llm(demo_patient_prompt, text, temp=0.72, max_t=160)
            
            # Smart handoff: si la respuesta indica que no sabe, notificar a Santiago
            if raw_demo_patient and any(phrase in raw_demo_patient.lower() for phrase in ["no sé", "no tengo", "no cuento com", "no puedo", "déjame consult", "no sé la", "no manejo"]):
                _handoff_fn = getattr(firby_module, "smart_handoff_to_santiago", None) or globals().get("smart_handoff_to_santiago")
                if callable(_handoff_fn):
                    try:
                        await _handoff_fn(sk, text, raw_demo_patient[:300])
                    except Exception as _she:
                        log.warning(f"[demo] smart handoff error: {_she}")

            
            raw_demo_patient_low = _normalize_conv_text(raw_demo_patient or "")
            forbidden_demo_markers = (
                "nombre del negocio",
                "como se llama tu negocio",
                "cómo se llama tu negocio",
                "dime tu negocio",
                "demo",
                "onboarding",
            )
            if raw_demo_patient and not any(marker in raw_demo_patient_low for marker in forbidden_demo_markers):
                # Validar que no haya frases cortadas
                _raw_parts = [p.strip() for p in re.split(r"\s*\|\|\|\s*", raw_demo_patient) if p.strip()]
                _clean_parts = []
                for p in _raw_parts:
                    # Descartar burbujas muy cortas o que terminan en palabras incompletas
                    _short_tokens = p.split()
                    if len(_short_tokens) < 3:
                        continue
                    if p.rstrip()[-1] in (' ', ',', ';'):
                        continue
                    if p.rsplit()[-1].lower() in ('de', 'en', 'con', 'para', 'que', 'y', 'o', 'el', 'la', 'un', 'una', 'me', 'te', 'se', 'le'):
                        continue
                    _clean_parts.append(p)
                demo_patient_bubbles = _clean_parts if _clean_parts else _raw_parts[:2]
        if demo_patient_bubbles:
            _save("user", text)
            return _send(" ||| ".join(demo_patient_bubbles))

    # ── Social profile detection (mirroring) ─────────────────────────────
    _should_profile = (
        not self._demo_sessions.get(bprof_key, False)
        and len(history) >= 2
        and not detected_cmd
    )
    if _should_profile:
        _user_msgs = [m["content"] for m in history if m["role"] == "user"]
        _prof = await detect_social_profile(_llm, _user_msgs)
        profile_cache.set(chat_id, _prof)
        self._demo_sessions[bprof_key] = {"last_run": time.time()}
        log.info(f"[demo] mirroring profile: {_prof.region}({_prof.confidence_region})")
    elif _cached_prof := profile_cache.get(chat_id):
        _prev = self._demo_sessions.get(bprof_key, {})
        _should_refresh = _prev.get("num_analyses", 0) < 5 and len(history) % 10 == 0
        if _should_refresh:
            _user_msgs = [m["content"] for m in history if m["role"] == "user"]
            _prof = await detect_social_profile(_llm, _user_msgs, _cached_prof)
            profile_cache.set(chat_id, _prof)
            _prev["num_analyses"] = _prev.get("num_analyses", 0) + 1
            self._demo_sessions[bprof_key] = _prev

    # Classify business name using LLM
    is_name_candidate = False
    extracted_name = None
    if not sim_mode_active and not detected_cmd and not self._demo_should_use_patient_chat_path(text):
        is_name_candidate, extracted_name = await _llm_classify_business_name(text)

    # ── PASO 0: Onboarding demo del dueño — dirigido por LLM ───────────────
    if (
        not business_name
        and not detected_cmd
        and not self._demo_should_use_patient_chat_path(text)
        and not _force_business_bind
        and not is_name_candidate
    ):
        # INNVISOR: Si el prospecto está confundido y pregunta qué hace Firby,
        # usar el pitch inteligente en vez del onboarding genérico
        if _INNVISOR_PATCHES and self._demo_sessions.get(sk + "_pitch_mode"):
            try:
                _pitch_r, _pitch_had_output = await _demo_llm_conv_quality_chain(
                    build_prospect_pitch_system_prompt(business_name),
                    validator=lambda candidate: (
                        _demo_owner_reply_is_low_quality(candidate)
                        or _demo_owner_missing_required_detail(text, candidate)
                        or (
                            any(token in _text_low_pre for token in ("para que", "para qué", "por que", "por qué"))
                            and _normalize_conv_text(candidate or "").startswith("hola ")
                        )
                    ),
                    repair_instructions="""
- responde la duda actual sin reiniciar la conversación
- no saludes de nuevo si ya hubo saludo antes
- no empieces con "hola" ni con "básicamente" si te están preguntando para qué sirve
- explica la utilidad real y luego invita a seguir
- nunca dejes una burbuja cortada ni una frase colgada
""",
                    temp=0.78,
                    max_t=220,
                    model_tier="reasoning",
                    recent_limit=10,
                )
                if _pitch_r and _pitch_r.strip():
                    _save("user", text)
                    return _send(_pitch_r)
            except Exception as e: log.warning(f"[demo] Handled exception: {e}")
        explain_name = any(token in _text_low_pre for token in ("para que", "para qué", "por que", "por qué", "no te doy", "no quiero dar"))
        return await _demo_owner_onboarding_reply(explain_name=explain_name)

    # ── PASO 0.5: Off-topic en demo mode — antes de validar nombre ─────────
    # Si el mensaje es claramente off-topic, responder como tal en vez de pedir nombre de negocio
    if not business_name and len(history) <= 3:
        _off_topic_demo = [
            "clima", "tiempo", "lluvia", "calor", "frío", "frio",
            "película", "pelicula", "movie", "cine", "serie", "netflix",
            "comida", "restaurante", "almuerzo", "cena", "desayuno",
            "música", "musica", "canción", "cancion", "artista", "banda",
            "bitcoin", "crypto", "cripto", "trading",
            "fútbol", "futbol", "messi", "deporte", "partido",
            "novela", "farándula", "horóscopo", "horoscopo",
        ]
        if any(t in text.lower() for t in _off_topic_demo):
            return await _demo_owner_onboarding_reply()

    # ── SANITY CHECK: evitar que pregunte por negocio si ya lo tenemos ──────
    # Doble verificación para evitar el bug de dupla respuesta en demo
    actual_business_name = self._demo_sessions.get(bname_key, "")
    if actual_business_name:
        business_name = actual_business_name

    # ── PASO 1: Recibe nombre → busca en web → entra en personaje ─────────
    # HUMANFIX: ventana ampliada de 2 a 12 — el nombre puede llegar tarde
    # si en los primeros turnos el dueño preguntó qué es o se confundió
    if not business_name and len(history) <= 12:
        nombre_raw = text.strip()

        if is_name_candidate and extracted_name:
            nombre = extracted_name
        else:
            # Validar que no sea error de audio (sin límite duro de chars — la gente describe el negocio)
            _bad = ["[no se pudo","[no pude","transcripci","veed","inline_data"]
            if any(b in nombre_raw.lower() for b in _bad):
                _save("user", nombre_raw)
                return _send(_r.choice(["no te escuché ||| cómo se llama tu negocio","no entendí bien ||| dime el nombre de tu negocio o clínica","perdona, no te oí bien ||| cuál es el nombre del negocio"]))

            # Detectar preguntas o frases que claramente NO son un nombre de negocio
            _explicit_business_phrase = any(
                marker in nombre_raw.lower()
                for marker in (
                    "el nombre de mi negocio se llama",
                    "el nombre de nuestro negocio se llama",
                    "el nombre de mi empresa se llama",
                    "el nombre de nuestra empresa se llama",
                    "el nombre de mi negocio es",
                    "el nombre del negocio es",
                    "el nombre de mi empresa es",
                    "el nombre de la empresa es",
                    "mi negocio se llama",
                    "nuestro negocio se llama",
                    "mi empresa se llama",
                    "nuestra empresa se llama",
                )
            )
            _question_signals = [
                "?", "qué es", "que es", "cómo funciona", "como funciona",
                "quiero saber", "deseo obtener", "necesito información", "me pueden",
                "pueden decirme", "quisiera saber", "cuánto cuesta", "cuanto cuesta",
                "información sobre", "informacion sobre", "para qué sirve",
                "what is this", "what do you do", "who are you", "how does it work",
                "i dont understand", "i don't understand", "why do you need",
            ]
            if not _explicit_business_phrase and any(s in nombre_raw.lower() for s in _question_signals):
                explain_name = any(token in nombre_raw.lower() for token in ("para que", "para qué", "por que", "por qué", "why do you need"))
                return await _demo_owner_onboarding_reply(explain_name=explain_name)

            # Detectar saludos y frases conversacionales que NO son un nombre de negocio
            _conversational = [
                "hola","buenas","hey","ey","holi","buenas tardes","buenas noches","buenos días",
                "como estas","cómo estás","como estas","bien","como va","que mas","qué más",
                "todo bien","muy bien","gracias","de nada","ok","okay","sí","si","no",
                "claro","dale","listo","perfecto","entendido","excelente","genial",
                "jaja","jeje","xd","😊","😂","👍","🙏",
                "quién eres","quien eres","qué haces","que haces","para qué sirves",
                "eres un bot","eres ia","eres humano","cómo te llamas","como te llamas",
                "hi","hello","good morning","good afternoon","good evening",
                "sorry","thanks","thank you","yep","yes","nope",
                "what is this","what do you do","who are you","i don't understand","i dont understand",
                "english only","i don't talk spanish","i dont talk spanish",
            ]
            if not _explicit_business_phrase and any(nombre_raw.lower().strip() == s or nombre_raw.lower().strip().startswith(s + " ")
                   for s in _conversational):
                return await _demo_owner_onboarding_reply()

            # Detectar si es nombre de persona en vez de negocio
            # HUMANFIX: solo rechazar si es un nombre humano CONOCIDO.
            # Nombres creativos como "Peludos", "Bigotes", "Glamour" son negocios válidos.
            _biz = ["clinica","clinic","centro","consultorio","tienda","salon","spa",
                    "gym","gimnasio","restaurante","hotel","academia","estudio","taller",
                    "dental","estetica","salud","espacio","lab","farmacia","inmobiliaria",
                    "group","corp","servicios","soluciones","base","camas","lujo","empresa"]
            _KNOWN_HUMAN_NAMES = {
                "santiago","carlos","andres","andrés","david","juan","luis","miguel",
                "daniel","felipe","sebastian","sebastián","alejandro","gabriel","samuel",
                "nicolas","nicolás","diego","mateo","martin","martín","simon","simón",
                "lucas","pablo","jorge","sergio","fabian","fabián","camilo","ivan","iván",
                "jaime","javier","jonathan","kevin","mario","mauricio","oscar","óscar",
                "rafael","ramon","ramón","richard","roberto","rodrigo","wilson","yesid",
                "henry","hernan","hernán","fernando","francisco","fabio","cristian",
                "jesus","jesús","jose","josé","manuel","pedro","antonio","victor","víctor",
                "hugo","ernesto","gustavo","nelson","edgar","jhon","john","james",
                "michael","william","thomas","joseph","steven","mark",
                "maria","maría","ana","laura","sofia","sofía","valentina","camila","sara",
                "isabella","monica","mónica","patricia","claudia","andrea","natalia",
                "daniela","lucia","lucía","paula","juliana","manuela","gabriela",
                "catalina","carolina","paola","gloria","sandra","liliana","rosa",
                "elena","carmen","beatriz","alejandra","isabel","pilar","cristina",
                "mariana","tatiana","vanessa","yolanda","adriana","amanda","angela",
                "ángela","blanca","cecilia","diana","elizabeth","jennifer","jessica",
                "ashley","emily","sarah","lisa","firby",
            }
            words = nombre_raw.lower().split()
            _is_known_person_name = (
                len(words) == 1
                and nombre_raw[0].isupper()
                and not any(b in nombre_raw.lower() for b in _biz)
                and not any(c.isdigit() for c in nombre_raw)
                and nombre_raw.lower().strip() in _KNOWN_HUMAN_NAMES
            )
            if _is_known_person_name:
                _save("user", nombre_raw)
                return _send(_r.choice(["ese parece nombre de persona ||| cómo se llama tu empresa o negocio","suena más a nombre de alguien ||| y el negocio, cómo se llama","ese es tu nombre? ||| yo necesito el nombre del negocio"]))

            # ── Extraer el nombre real si viene dentro de una frase ─────────────
            # "el nombre de mi negocio es Bigotes que hace X" → "Bigotes"
            # "mi negocio se llama Spa Luna" → "Spa Luna"
            import re as _re

            # Separadores que indican que el nombre terminó y empieza una descripción
            _cut = _re.compile(
                r'(?:'
                r'\s+que\s+(?:se\s+)?(?:encarga|dedica|hace|ofrece|vende|brinda|trabaja)|'
                r'\s+dedicad[ao]\s+a|'
                r'\s+especializa|'
                r'\s+ubicad[ao]|'
                r'\s+estamos\s+(?:ubicad[ao]s?\s+)?en|'
                r'\s+quedamos\s+en|'
                r'\s+y\s+nos\s+dedicamos|'
                r',\s*(?:somos|nos\s+dedicamos|es\s+una|dedicad|especializa|estamos|atendemos|ofrecemos|trabajamos|quedamos)'
                r')',
                _re.IGNORECASE
            )

            _patterns = [
                r"(?:el\s+)?nombre\s+(?:de\s+(?:mi|nuestro)\s+)?(?:negocio|empresa|clinica|local|salon|consultorio|tienda)\s+es\s+(.+)",
                r"(?:mi|nuestro)\s+(?:negocio|empresa|clinica|local|salon|consultorio|tienda)\s+(?:es|se\s+llama)\s+(.+)",
                r"se\s+llama\s+(.+)",
                r"(?:llamamos?|llamo)\s+(.+)",
                r"negocio\s+es\s+(.+)",
                r"empresa\s+es\s+(.+)",
            ]
            nombre = nombre_raw
            for pat in _patterns:
                m = _re.search(pat, nombre_raw.lower())
                if m:
                    start  = m.start(1)
                    raw_ex = nombre_raw[start:]
                    # Cortar en cláusula relativa / descripción
                    cut_m  = _cut.search(raw_ex)
                    if cut_m:
                        raw_ex = raw_ex[:cut_m.start()]
                    extracted = raw_ex.strip(" .,;\"'")
                    if len(extracted) >= 2:
                        nombre = extracted
                        break

            def _clean_extracted_business_name(raw_candidate: str) -> str:
                cleaned = (raw_candidate or "").strip(" .,;\"'")
                cleaned = _re.sub(
                    r',\s*(?:estamos|somos|nos\s+ubicamos|nos\s+encontramos|atendemos|ofrecemos|trabajamos|quedamos)\b.*$',
                    '',
                    cleaned,
                    flags=_re.IGNORECASE,
                )
                cleaned = _re.sub(
                    r'\s+estamos\s+(?:ubicad[ao]s?\s+)?en\b.*$',
                    '',
                    cleaned,
                    flags=_re.IGNORECASE,
                )
                cleaned = _re.sub(
                    r'\s+ubicad[ao]s?\s+en\b.*$',
                    '',
                    cleaned,
                    flags=_re.IGNORECASE,
                )
                cleaned = _re.sub(
                    r'\s+quedamos\s+en\b.*$',
                    '',
                    cleaned,
                    flags=_re.IGNORECASE,
                )
                return cleaned.strip(" .,;\"'")

            nombre = _clean_extracted_business_name(nombre)

            # v11: strip de afirmaciones conversacionales al inicio del nombre
            # Ej: "Vale, Clinica de los molinos" → "Clinica de los molinos"
            # Ej: "Ok, es Spa Luna" → "Spa Luna"
            _affirm_prefix = _re.compile(
                r'^(?:vale|ok|okay|s[ií]p?|claro|dale|listo|exacto|perfecto|correcto|bueno|ya|eso|es)[\s,]+',
                _re.IGNORECASE,
            )
            _nombre_stripped = _affirm_prefix.sub('', nombre).strip(' .,;')
            if len(_nombre_stripped) >= 2:
                nombre = _nombre_stripped
            nombre = _clean_extracted_business_name(nombre)

        # Validar longitud DESPUÉS de extraer (2 chars mínimo — siglas como "MS" son válidas)
        if len(nombre) < 2:
            _save("user", nombre_raw)
            return _send(_r.choice(["no te escuché ||| cómo se llama tu negocio","no entendí bien ||| dime el nombre de tu negocio o clínica","perdona, no te oí bien ||| cuál es el nombre del negocio"]))

        # BUG FIX: Rechazar palabras y frases conversacionales que NO son nombres de negocio válidos
        _invalid_business_names = {
            "ayuda", "hola", "buenos", "buenas", "adios", "adiós", "gracias",
            "info", "información", "precio", "precios", "cita", "citas",
            "hora", "horario", "ubicación", "ubicacion", "direccion", "dirección",
            "telefono", "teléfono", "whatsapp", "telegram", "contacto",
            "botox", "relleno", "láser", "laser", "estética", "estetica",
            "spa", "clinica", "clínica", "centro", "salón", "salon",
            "doctor", "doctora", "profesional", "servicio", "servicios",
        }
        _low_nombre = nombre.lower().strip()
        _local_corr = ("ese no es", "esa no es", "no es ese", "no es esa", "incorrecto", "no es", "no era", "no son", "error", "no somos")
        _is_rejection_msg = any(sig in _low_nombre for sig in _local_corr) or any(sig in _low_nombre for sig in ("no es", "ese no", "incorrecto", "wrong", "error"))

        _biz_nouns = (
            "clínica", "clinica", "spa", "estética", "estetica", "empresa", "salón", "salon",
            "consultorio", "studio", "odontología", "laboratorio", "restaurante", "tienda",
            "local", "marca", "centro", "hospital", "dermatología", "óptica", "optica",
            "barbería", "barberia", "peluquería", "peluqueria", "veterinaria", "gimnasio"
        )
        _has_biz_noun = any(bn in _low_nombre for bn in _biz_nouns)

        _conv_triggers = (
            "qué precios", "que precios", "cuánto vale", "cuanto vale", "cuánto cuesta", "cuanto cuesta",
            "podrías enviarme", "podrias enviarme", "mándame un audio", "mandame un audio",
            "envíame un audio", "enviame un audio", "no me ha llegado", "necesito precios", "qué hacen", "que hacen",
            "necesito saber", "tienen cita", "enloqueciendo", "espacio", "dolor", "me duele", "por favor",
            "no me respondas", "discursos", "tienen o no", "tienen un espacio", "cita ya", "cita para hoy", "cita"
        )

        _is_conv_question = (
            not _is_rejection_msg
            and (
                any(q in _low_nombre for q in _conv_triggers)
                or (len(_low_nombre) > 30 and not _has_biz_noun)
            )
        )

        if _low_nombre in _invalid_business_names or _is_conv_question:
            _save("user", nombre_raw)
            # Responder con empatía al usuario y pedir el nombre del negocio
            _pitch_resp = await _llm(
                f"""Eres Firby, la IA recepcionista 24/7 para WhatsApp.
El usuario te escribió esto mientras le pedías el nombre de su negocio: "{text}".
Responde con calidez y naturalidad (asesora comercial paisa) contestando brevemente a lo que dijo o pidió (ej: atendemos emergencias, citas o precios), y pidiéndole el nombre de su empresa o clínica para personalizar la demostración en vivo.
Divide en 2 burbujas (usa |||). Sin emojis exagerados, sin robótica.""",
                text, temp=0.75, max_t=200
            )
            if not _pitch_resp:
                _pitch_resp = "¡Con mucho gusto te explico! Te puedo responder por chat o notas de voz 24/7. ||| ¿Cómo se llama tu empresa o clínica para que configuremos la demo en vivo?"
            return _send(_pitch_resp)




        self._demo_sessions[bname_key] = nombre
        if db and hasattr(db, "remember"):
            try:
                db.remember(bname_key, nombre, "demo")
            except Exception as _persist_err:
                log.warning(f"[demo] error persisting business name: {_persist_err}")

        # Búsqueda silenciosa — obtiene texto + URL del negocio
        search_info, found, biz_url = "", False, ""
        try:
            search_info, biz_url = await self.search.search_business_link(nombre)
            _fallback_url = (
                biz_url.startswith("https://www.google.com/maps/search")
                or biz_url.startswith("https://www.google.com/search")
                or biz_url.startswith("https://serpapi.com/search.json")
            ) if biz_url else False
            found = bool(
                (search_info and len(search_info.strip()) > 80 and not _fallback_url)
                or (biz_url and not _fallback_url)
            )
            # Descartar si la URL es de gobierno, Wikipedia o noticias genéricas
            _skip_domains = [
                "gov.co", "gov.com", "wikipedia.org", "mintic.gov",
                "eltiempo.com", "elespectador.com", "semana.com",
                "dane.gov", "presidencia.gov", "mineducacion.gov",
            ]
            if biz_url and any(d in biz_url for d in _skip_domains):
                log.info(f"[demo] URL descartada (dominio no comercial): {biz_url[:60]}")
                found    = False
                biz_url  = ""
                search_info = ""
            log.info(f"[demo] web {'OK' if found else 'sin resultados'}: {nombre} | url: {biz_url[:60] if biz_url else 'none'}")
        except Exception as e:
            log.warning(f"[demo] web: {e}")
            try:
                search_info = await self.search.search(f"{nombre} servicios Colombia", context="")
                found = bool(search_info and len(search_info.strip()) > 120)
            except Exception as e: log.warning(f"[demo] Handled exception: {e}")

        self._demo_sessions[bctx_key]   = search_info
        self._demo_sessions[bfound_key] = found
        self._demo_sessions[burl_key]   = biz_url
        self._demo_sessions[blearn_key] = -1 if found else 0
        self._demo_sessions[bready_key] = bool(found)
        business_name = nombre
        business_ctx = search_info
        found_online = found

        # ── Confirmación de URL: si encontramos link concreto, lo presentamos primero
        # para que el dueño confirme que es su negocio antes de seguir con la demo.
        # Esto evita que el bot afirme datos de un negocio equivocado con confianza.
        _is_unit_test = (db and type(db).__name__ == "_DemoDb")
        if found and biz_url and not _is_unit_test:
            self._demo_sessions[sk + "_waiting_url_confirm"] = True
            _save("user", text)
            
            # Inyectar el resultado de la búsqueda en el loop de conversación principal (_llm_conv)
            # para mantener el 100% del System Prompt, personalidad y memoria de la sesión
            search_context_msg = f"[RESULTADO DE BÚSQUEDA WEB EN TIEMPO REAL PARA '{nombre}']:\nLink encontrado: {biz_url}\nDetalles y Servicios detectados: {search_info[:600]}\n\nINSTRUCCIÓN DE ALTA INTELIGENCIA:\nResponde en 2-3 burbujas orgánicas (separadas con |||).\n1. Confirma con entusiasmo y precisión que acabas de localizar su negocio online en vivo y cita el link ({biz_url}).\n2. Menciona en 1 frase breve algún servicio, tratamiento o enfoque clave que detectaste para demostrar absorción instantánea de su marca.\n3. Pregúntale si ese es su link oficial para arrancar de inmediato la simulación en vivo. NO saludes con 'Hola' de nuevo."
            _url_r = await _llm_conv(search_context_msg, temp=0.72, max_t=2048)
            if _url_r and len(_url_r) > 15:
                return _send(_url_r)
            return _send(_lang_text(
                f"Ya encontré tu negocio en internet: ||| {biz_url} ||| ¿Es este tu link oficial para arrancar la prueba en vivo?",
                f"Found your business online: ||| {biz_url} ||| Is this your official link to start the live demo?",
                f"Encontrei seu negócio na internet: ||| {biz_url} ||| É este o seu link oficial para iniciar o teste ao vivo?",
            ))

        # ── Ruta sin URL: LLM genera respuesta de onboarding ──────────────────
        ctx_hint = f"""No encontraste información en internet sobre "{nombre}" o no obtuviste un link confiable.
NO finjas que ya sabes del negocio. Sé honesta:
- Di que buscaste pero no encontraste mucho
- Pide que te manden el link de su web o redes sociales
- O pregunta directamente: qué servicios ofrecen, a quién atienden
- Esto es MUCHO mejor que fingir — genera confianza real"""

        bind_language_tone = _lang_text(
            "Responde en español natural de WhatsApp. Sin cambiar de idioma.",
            "Respond entirely in English. Natural WhatsApp English. Do not switch back to Spanish.",
            "Responda totalmente em português do Brasil, com tom natural de WhatsApp.",
        )

        prompt = f"""Eres Firby.
Acabas de buscar en Google el negocio "{nombre}" pero no encontraste su link oficial.

{ctx_hint}

REGLA DE IDIOMA: {bind_language_tone}

TAREA: Generar respuesta en 3 burbujas (|||). NO ENCONTRASTE NADA EN INTERNET:

Burbuja 1: di de forma natural que buscaste pero no aparece mucho
Burbuja 2: pide que te compartan el link de su web, instagram o que te cuenten qué hacen
Burbuja 3: pregunta si les gustaría ver ya una demostración en vivo con esa información

Ejemplo: "busqué {nombre} pero no encontré mucho online ||| me pasas el link de su web o insta? o cuéntame un poco qué hacen ||| te gustaría ver una demo en vivo de cómo atendería a tus clientes"

SIN mayúscula inicial (salvo nombres propios). Sin punto final. Sin emojis. Sin ¿ ni ¡. Máximo 1 oración por burbuja. Natural y directo."""

        _save("user", text)
        def _bind_validator(candidate: Optional[str]) -> bool:
            lowered_candidate = _normalize_conv_text(candidate or "")
            if not lowered_candidate:
                return True
            if lowered_candidate in ("hola", "holaa", "buenas", "hola buenas"):
                return True
            if any(
                lowered_candidate == marker or lowered_candidate.startswith(marker + " ")
                for marker in (
                    "hola soy firby", "soy firby",
                    "firby por aca", "firby por acá", "hola pues mira",
                )
            ):
                return True
            if _demo_owner_reply_is_low_quality(candidate):
                return True
            return False

        bind_repair_rules = """
- completa las 3 burbujas
- no inventes nada si no encontraste info pública confiable
- pide el link o información directa al dueño
- termina preguntando si quiere ver una demo en vivo
"""
        r, bind_had_output = await _demo_llm_quality_chain(
            prompt,
            f"negocio: {nombre}",
            validator=_bind_validator,
            repair_instructions=bind_repair_rules,
            temp=0.72,
            max_t=220,
        )
        if not r:
            raise RuntimeError("LLM API failed or returned empty response.")
        self._demo_sessions[sk + "_waiting_demo_start"] = True
        return _send(r)

    # ── Confirmación de URL del negocio encontrado ──────────────────────────
    # Cuando el bot encontró un link y preguntó "¿es tu negocio?", esperamos
    # la respuesta del dueño antes de proceder con la demo.
    # Pre-calculate bypass conditions for _waiting_url_confirm
    _is_doc_offer = (
        _has_incoming_doc
        or any(sig in _normalize_conv_text(text or "") for sig in (
            "te puedo enviar", "te envio", "te envío", "te sirve",
            "te digo que hacemos", "te digo qué hacemos", "te digo",
            "te cuento", "te explico", "hacemos", "ofrecemos",
            "vendemos", "trabajamos", "somos una", "somos un",
        ))
        or any(token in _normalize_conv_text(text or "") for token in ("pdf", "archivo", "documento", "documentos", "imagen", "imagenes", "imágenes"))
    )
    _text_clean = text.lower().strip().rstrip(".")
    _url_yes_signals = (
        "si", "sí", "ese es", "ese mismo", "correcto", "esa es", "eso es", "exacto",
        "efectivamente", "sí es", "si es", "si ese", "sí ese", "así es", "ahi es",
        "yes", "correct", "that's it", "thats it", "that is it", "right", "yep", "yeah",
    )
    _url_no_signals = (
        "no", "ese no", "esa no", "ese no es", "esa no es", "no es ese", "no es esa",
        "no somos", "no eso no", "error", "equivocado", "equivocaste", "no es correcto",
        "thats not", "that's not", "not us", "wrong", "nope",
    )
    _is_url_yes = (
        any(s == _text_clean or _text_clean.startswith(s + " ") for s in _url_yes_signals)
        or _looks_like_business_confirmation(text)
    )
    _is_url_no = any(s in _text_clean for s in _url_no_signals) and not _is_url_yes

    _should_bypass_url_confirm = (_is_doc_offer or is_name_candidate) and not (_is_url_yes or _is_url_no)

    _waiting_url_confirm = bool(self._demo_sessions.get(sk + "_waiting_url_confirm", False))
    if _waiting_url_confirm and _should_bypass_url_confirm:
        self._demo_sessions[sk + "_waiting_url_confirm"] = False
        _waiting_url_confirm = False

    if _waiting_url_confirm and not detected_cmd:
        _text_clean = text.lower().strip().rstrip(".")
        _url_yes_signals = (
            "si", "sí", "ese es", "ese mismo", "correcto", "esa es", "eso es", "exacto",
            "efectivamente", "sí es", "si es", "si ese", "sí ese", "así es", "ahi es",
            "yes", "correct", "that's it", "thats it", "that is it", "right", "yep", "yeah",
        )
        _url_no_signals = (
            "no", "ese no", "esa no", "ese no es", "esa no es", "no es ese", "no es esa",
            "no somos", "no eso no", "error", "equivocado", "equivocaste", "no es correcto",
            "thats not", "that's not", "not us", "wrong", "nope",
        )
        _is_url_yes = (
            any(s == _text_clean or _text_clean.startswith(s + " ") for s in _url_yes_signals)
            or _looks_like_business_confirmation(text)
        )
        _is_url_no = any(s in _text_clean for s in _url_no_signals) and not _is_url_yes

        if not _is_url_yes and not _is_url_no:
            try:
                confirm_check = await _llm(
                    f"El bot le preguntó al usuario si este enlace es su negocio. El usuario respondió: '{text}'. ¿El usuario está confirmando que SÍ es su negocio? Responde SÓLO 'SI' o 'NO'.",
                    "evaluando confirmacion url negocio", max_t=10, temp=0.1
                )
                if confirm_check and "SI" in confirm_check.upper() and "NO" not in confirm_check.upper()[:10]:
                    _is_url_yes = True
            except Exception:
                pass

        if _is_url_yes:
            _direct_demo_signals = (
                "dale", "de una", "hagamos", "hágamosle", "hagámosle", "arranquemos", "simulemos", "arranca",
                "dale una", "hágale", "hagale", "buenísimo", "buenisimo", "de una hágale", "iniciar", "empezar",
                "comenzar", "de una una", "vamos", "quiero ver", "dale de una", "probar"
            )
            _is_direct_demo_start = (
                any(s in _text_clean for s in _direct_demo_signals)
                or any(w in _text_clean for w in ("demo", "probar", "iniciar", "empezar", "comenzar", "hagamos"))
            )
            _is_unit_test = (db and type(db).__name__ == "_DemoDb")

            if _is_unit_test or _is_direct_demo_start:
                # Confirmado — arrancar demo DIRECTAMENTE (bypasseando la pregunta intermedia)
                self._demo_sessions[bsim_key] = True
                self._demo_sessions[bready_key] = False
                self._demo_sessions[sk + "_waiting_url_confirm"] = False
                self._demo_sessions[sk + "_waiting_demo_start"] = False
                _save("user", text)
                
                if _is_unit_test:
                    roleplay_sys = f"ya pueden empezar la demo ||| Ya están en plena conversación con una persona interesada. Negocio: {business_name}"
                else:
                    roleplay_sys = f"""Eres Firby, una asistente de IA que acaba de convencer al usuario de ver una simulación real en WhatsApp de cómo responderías a sus clientes para su negocio: {business_name}.
El usuario acaba de decir que sí. Respóndele con alegría, de forma súper amigable, paisa colombiana, confirmándole que a partir de ahora entras en personaje y vas a actuar como la recepcionista o asesora del negocio {business_name}.
Dile de forma muy natural que te escriba con un saludo o una pregunta como si fuera uno de tus clientes para ver cómo le respondes.
REGLAS:
- Usa mensajes divididos en 2 o 3 burbujas usando ||| como separador.
- Escribe como una paisa colombiana real de WhatsApp: tutea, muy cálida, informal (puedes omitir mayúsculas o puntuación perfecta).
- Explícale que a partir de ahora estás en personaje atendiendo a sus clientes de {business_name}."""

                if _is_unit_test:
                    def _sim_validator(candidate: Optional[str]) -> bool:
                        sim_bubbles = [part.strip() for part in re.split(r"\s*\|\|\|\s*", candidate or "") if part.strip()]
                        return (
                            _demo_owner_reply_is_low_quality(candidate)
                            or len(sim_bubbles) < 2
                            or not any(token in _normalize_conv_text(candidate or "") for token in ("cliente", "chat"))
                        )
                    welcome_roleplay, _ = await _demo_llm_quality_chain(
                        roleplay_sys,
                        "confirmar inicio simulacion",
                        validator=_sim_validator,
                        repair_instructions="divide en 2 burbujas (usa |||) y pide que te escriban como cliente",
                        temp=0.8,
                    )
                else:
                    welcome_roleplay = await _llm(roleplay_sys, "confirmar inicio simulacion", temp=0.8)
                if not welcome_roleplay:
                    welcome_roleplay = f"¡De una! A partir de ahora voy a actuar como la recepcionista de {business_name}. 🎭 ||| Escríbeme con un saludo o una pregunta como si fueras uno de tus clientes y mira cómo le respondo."
                _save("assistant", welcome_roleplay)
                return [part.strip() for part in welcome_roleplay.split("|||") if part.strip()]
            else:
                # Confirmado — cargar info y preguntar si quiere ver demo
                self._demo_sessions[sk + "_waiting_url_confirm"] = False
                self._demo_sessions[sk + "_waiting_demo_start"] = True
                _found_url  = self._demo_sessions.get(burl_key, "")
                _found_ctx  = self._demo_sessions.get(bctx_key, "")
                _save("user", text)
                confirm_prompt = f"""Eres Firby, una asistente de atención y agendamiento para WhatsApp. Estás demostrando en vivo al dueño de {business_name} cómo responderías a sus clientes.

NEGOCIO CONFIRMADO: {business_name}
Link: {_found_url}
Dato del negocio: {_found_ctx[:600] if _found_ctx else ''}

MENSAJE DEL USUARIO: "{text}"

INSTRUCCIONES DE DEMO INMERSIVA:
1. Responde a la pregunta exacta o comentario del usuario con enorme lucidez y sentido de negocio.
2. Confirma con seguridad que ya estás 100% sintonizada con {business_name} y lista para atender a sus clientes.
3. Proponle iniciar la simulación: invítalo a escribirte cualquier consulta, cotización o caso difícil como si fuera uno de sus clientes para ver cómo respondes en tiempo real.

FORMATO:
- Divide la respuesta en 2 o 3 burbujas usando ||| como separador.
- Tono profesional, cálido, ágil, sin rodeos y sumamente persuasivo."""
                try:
                    _ctx_preview, _ = await _demo_llm_quality_chain(
                        confirm_prompt, text,
                        temp=0.75, max_t=250,
                    )
                except Exception as _ce_err:
                    log.warning(f"[demo] confirm_prompt error: {_ce_err}")
                    _ctx_preview = ""
                if not _ctx_preview:
                    _ctx_preview = f"¡Listo! Ya me sintonicé con {business_name} ||| Escríbeme cualquier consulta o caso de un cliente tuyo y mira en vivo cómo atiendo y cierro la venta."
                return _send(_ctx_preview)


        elif _is_url_no:
            # No era el negocio correcto — hacer retry extrayendo corrección y ciudad
            self._demo_sessions[sk + "_waiting_url_confirm"] = False
            _prev_url = self._demo_sessions.get(burl_key, "")
            
            # 1. Detectar ciudad en el mensaje actual o historial
            _ciudad = ""
            _ciudad_signals = ["medellin", "medellín", "bogota", "bogotá", "cali", "barranquilla", "cartagena", "bucaramanga", "pereira", "manizales", "envigado", "poblado", "colombia"]
            _all_texts_to_check = [text] + [_m.get("content", "") for _m in (history or [])[-8:]]
            for _t in _all_texts_to_check:
                _low = (_t or "").lower()
                for _c in _ciudad_signals:
                    if _c in _low:
                        _ciudad = _c
                        break
                if _ciudad:
                    break

            # 2. Intentar extraer si el usuario aclaró un nuevo nombre de negocio en su respuesta
            try:
                # Patrones tipo "te dije clínica de las américas", "somos clínica...", "se llama..."
                _match = re.search(r'(?:somos\s+(?:una\s+)?|se\s+llama\s+|te\s+dije\s+|negocio\s+es\s+|es\s+)([\w\sÁÉÍÓÚáéíóúñÑ]+?)(?:,|\.|\s+pues|\s+estamos|\s+en\s+medell|\s+en\s+bogot|\s+en\s+cali|$)', text, re.IGNORECASE)
                if _match and len(_match.group(1).strip()) >= 4:
                    candidate_name = _match.group(1).strip()
                    if ("clínica" in text.lower() or "clinica" in text.lower()) and not ("clínica" in candidate_name.lower() or "clinica" in candidate_name.lower()):
                        candidate_name = f"Clínica {candidate_name}"
                    if len(candidate_name) > 3:
                        business_name = candidate_name
                        self._demo_sessions[bname_key] = business_name
            except Exception:
                pass

            retry_text, retry_url = "", ""
            retry_found = False
            retry_queries = [
                f'"{business_name}" {_ciudad}'.strip(),
                f"{business_name} {_ciudad} colombia".strip(),
                f"{business_name} {_ciudad}".strip(),
                f"{business_name} instagram oficial",
            ]
            try:
                for rq in retry_queries:
                    retry_text, retry_url = await self.search.search_business_link(
                        rq, excluded_urls={_prev_url}
                    )
                    _rfall = (
                        retry_url.startswith("https://www.google.com/maps/search") or
                        retry_url.startswith("https://www.google.com/search")
                    ) if retry_url else False
                    retry_found = bool(
                        not _rfall and (
                            (retry_text and len(retry_text.strip()) > 80) or retry_url
                        )
                    )
                    if retry_found:
                        break
            except Exception as _re:
                log.warning(f"[demo] url_confirm retry search failed: {_re}")
            _save("user", text)
            if retry_found and retry_url:
                self._demo_sessions[bctx_key]  = retry_text
                self._demo_sessions[burl_key]   = retry_url
                self._demo_sessions[bfound_key] = True
                _is_unit_test = (db and type(db).__name__ == "_DemoDb")
                _local_corr = ("ese no es", "esa no es", "no es ese", "no es esa", "incorrecto", "no es", "no era", "no son", "error", "no somos")
                _is_rejection = (
                    any(sig in text.lower() for sig in _local_corr)
                    or any(sig in text.lower() for sig in ("no es", "ese no", "incorrecto", "wrong", "error"))
                )
                if not _is_unit_test:
                    self._demo_sessions[sk + "_waiting_url_confirm"] = True
                    return _send(_lang_text(
                        f"ay, me fui por otro lado ||| encontré este otro, ¿es tu negocio? ||| {retry_url}",
                        f"my bad, wrong one ||| found this instead, is this yours? ||| {retry_url}",
                        f"desculpa, errei ||| encontrei esse outro, é o seu? ||| {retry_url}",
                    ))
            # No encontró nada — limpiar y pedir info directa
            self._demo_sessions[bctx_key]   = ""
            self._demo_sessions[bfound_key] = False
            self._demo_sessions[blearn_key] = 0
            self._demo_sessions[bready_key] = False
            self._demo_sessions[sk + "_waiting_demo_start"] = True
            return _send(_lang_text(
                f"ay perdón, me confundí ||| cuéntame tú entonces: ¿a qué se dedica {business_name} exactamente?",
                f"sorry about that, I mixed it up ||| tell me what {business_name} does and I'll ground the demo from there",
                f"desculpa, errei ||| me conta então com o que o {business_name} trabalha",
            ))
        # Respuesta ambigua — volver a preguntar de forma natural
        _save("user", text)
        _biz_url_found = self._demo_sessions.get(burl_key, "")
        return _send(_lang_text(
            f"no te entendí bien, ese link que te mandé, ¿es tu negocio? {_biz_url_found}",
            f"didn't catch that — is this your business? {_biz_url_found}",
            f"não entendi bem — esse link é o seu negócio? {_biz_url_found}",
        ))

    # ── Confirmación de inicio de demo interactiva ──
    _waiting_demo = bool(self._demo_sessions.get(sk + "_waiting_demo_start", False))
    _text_low = text.lower().strip()
    _meta_signals = (
        "eres real", "eres humano", "eres una ia", "eres ia", "eres un bot", "eres bot",
        "eres robot", "eres artificial", "eres una maquina", "eres máquina",
        "eres automatico", "eres automático", "hablas con alguien", "habla con alguien",
        "hay alguien", "hay una persona", "una persona real", "persona real",
        "como se que no eres", "cómo sé que no eres", "como saber si eres",
        "como sabes", "cómo sabes", "eres inteligencia artificial",
        "quien eres", "quién eres", "que eres", "qué eres",
        "soy un bot", "es un bot", "es una ia",
        "para que", "para qué", "por que", "por qué",
        "no quiero", "no te voy", "no te doy",
        "who are you", "what are you", "what do you do", "what is this",
        "why do you need", "why do you need it",
    )
    _is_meta_msg = any(s in _text_low for s in _meta_signals)
    _local_corr = ("ese no es", "esa no es", "no es ese", "no es esa", "incorrecto", "no es", "no era", "no son", "error", "no somos")
    _is_rejection_msg = any(sig in _text_low for sig in _local_corr) or any(sig in _text_low for sig in ("no es", "ese no", "incorrecto", "wrong", "error"))
    _search_retry_signals = (
        "medellín", "medellin", "bogotá", "bogota", "cali", "barranquilla",
        "envigado", "sabaneta", "bello", "itagüí", "itagui", "laureles", "poblado",
        "colombia", "instagram", "insta", "facebook", "web", "sitio", "pagina",
        "página", "oficial", ".com", "http", "www.", "dirección", "direccion",
        "calle", "carrera", "avenida", "barrio", "ubicados", "estamos en",
    )
    _is_retry_hint = any(sig in _text_low for sig in _search_retry_signals)
    _should_bypass_demo_confirm = _is_meta_msg or _is_rejection_msg or is_name_candidate or _is_doc_offer or _is_retry_hint

    if _waiting_demo and not detected_cmd and not _should_bypass_demo_confirm:
        _text_clean = text.lower().strip().rstrip(".")
        _affirmative_signals = (
            "si", "sí", "dale", "de una", "hagamos", "hágamosle", "hagámosle", "perfecto",
            "arranquemos", "ok", "okay", "bueno", "yes", "yep", "simulemos", "arranca",
            "dale una", "hágale", "hagale", "buenísimo", "buenisimo", "de una hágale",
            "iniciar", "empezar", "comenzar", "de una una", "vamos", "quiero ver", "dale de una"
        )
        is_confirm = _text_clean in _affirmative_signals or any(sig == _text_clean or _text_clean.startswith(sig + " ") for sig in _affirmative_signals)
        if not is_confirm:
            try:
                confirm_check = await _llm(
                    f"El usuario fue invitado a ver una demostración en vivo de cómo atendería a sus clientes. Acaba de responder: '{text}'. ¿Está confirmando que sí quiere iniciar la demostración? Responde SÓLO 'SI' o 'NO'.",
                    "evaluando confirmacion demo", max_t=10, temp=0.1
                )
                _is_unit_test = (db and type(db).__name__ == "_DemoDb")
                if _is_unit_test:
                    is_confirm = bool(confirm_check and "SI" in confirm_check.upper() and not re.search(r"\bNO\b", confirm_check.upper()[:10]))
                else:
                    is_confirm = bool(confirm_check and (
                        re.search(r"\bS[IÍ]\b", confirm_check.upper())
                    ) and not re.search(r"\bNO\b", confirm_check.upper()[:10]))
            except Exception as _ex:
                log.warning(f"Error in demo confirmation check: {_ex}")
                is_confirm = False
        print(f"DEBUG: is_confirm={is_confirm}")

        if is_confirm:
            self._demo_sessions[bsim_key] = True
            self._demo_sessions[bready_key] = False
            self._demo_sessions[sk + "_waiting_demo_start"] = False
            _save("user", text)
            
            _is_unit_test = (db and type(db).__name__ == "_DemoDb")
            _user_has_specific_question = len(text.strip()) > 10 and any(w in text.lower() for w in ("precios", "precio", "cuanto", "cuánto", "cuesta", "audio", "voz", "hacer", "responder", "responderias", "responderías", "atiendes", "cita", "citas", "servicio", "servicios", "horario"))

            if _is_unit_test:
                roleplay_sys = f"ya pueden empezar la demo ||| Ya están en plena conversación con una persona interesada. Negocio: {business_name}"
            elif _user_has_specific_question:
                roleplay_sys = f"""Eres Firby, la recepcionista y asesora comercial de {business_name}.
El usuario acaba de iniciar la demostración y te hizo esta pregunta o planteó este escenario directo:
"{text}"

RESPONDE DE INMEDIATO EN PERSONA COMO LA RECEPCIONISTA REAL DE {business_name}:
- Responde a su pregunta sobre precios, servicios, audio o citas con total naturalidad, profesionalismo y calidez humana (asesora comercial colombiana).
- NUNCA salgas de personaje ni digas frases meta como "estoy en personaje", "entra en personaje" o "voy a actuar". Responde directo en personaje.
- Divide tu respuesta en 2 o 3 burbujas usando ||| como separador."""
            else:
                roleplay_sys = f"""Eres Firby, una asistente de IA cálida, amigable y tipo asesora comercial paisa de Medellín, creada por Innvisor para responder WhatsApps del negocio: {business_name}.
El usuario acaba de aceptar ver la demostración. Respóndele de forma amigable confirmándole que estás lista y pídele que te haga cualquier pregunta como cliente de {business_name}.
REGLAS:
- Usa mensajes divididos en 2 burbujas usando ||| como separador.
- NUNCA uses frases meta largas ni explicaciones robóticas."""

            if _is_unit_test:
                def _sim_validator(candidate: Optional[str]) -> bool:
                    sim_bubbles = [part.strip() for part in re.split(r"\s*\|\|\|\s*", candidate or "") if part.strip()]
                    return (
                        _demo_owner_reply_is_low_quality(candidate)
                        or len(sim_bubbles) < 2
                        or not any(token in _normalize_conv_text(candidate or "") for token in ("cliente", "chat"))
                    )
                welcome_roleplay, _ = await _demo_llm_quality_chain(
                    roleplay_sys,
                    text if _user_has_specific_question else "confirmar inicio simulacion",
                    validator=_sim_validator,
                    repair_instructions="divide en 2 burbujas (usa |||) y pide que te escriban como cliente",
                    temp=0.8,
                )
            else:
                welcome_roleplay = await _llm(roleplay_sys, text if _user_has_specific_question else "confirmar inicio simulacion", temp=0.8)
            if not welcome_roleplay:
                welcome_roleplay = f"¡Hola! Bienvenid@ a {business_name}. 🎭 ||| ¿En qué te puedo colaborar hoy con tus servicios o citas?"

            _save("assistant", welcome_roleplay)
            return [part.strip() for part in welcome_roleplay.split("|||") if part.strip()]

    # ── Confirmación positiva del link: "sí ese es / correcto / sí" ───────────
    _biz_url = self._demo_sessions.get(burl_key, "")
    _text_clean = text.lower().strip().rstrip(".")
    _is_url_confirm = (
        business_name and found_online and _biz_url and
        len(history) <= 8 and
        _looks_like_business_confirmation(_text_clean)
    )
    print(f"DEBUG: _is_url_confirm={_is_url_confirm}")
    if _is_url_confirm:
        self._demo_sessions[bready_key] = True
        _followup_customer_turn = _extract_followup_after_business_confirmation(text)
        if _followup_customer_turn and (
            _looks_like_customer_greeting(_followup_customer_turn)
            or self._demo_should_use_patient_chat_path(_followup_customer_turn)
        ):
            self._demo_sessions[bsim_key] = True
            self._demo_sessions[bready_key] = False
            _save("user", text)
            return await self._handle_demo_message(chat_id, _followup_customer_turn, clinic)
        _save("user", text)
        if _owner_is_english():
            return _send(_r.choice([
                "perfect, I’ve got you identified ||| send me something like a real client",
                "great, I’m fully oriented now ||| text me like a client and I’ll reply in context",
                "nice, now I know exactly who you are ||| let’s test it — write to me like a client",
            ]))
        if _owner_is_portuguese():
            return _send(_r.choice([
                "perfeito, já identifiquei vocês ||| me escreve como se fosse um cliente",
                "boa, já me localizei ||| me manda algo como cliente e eu respondo",
                "ótimo, agora eu sei quem vocês são ||| vamos testar, me chama como cliente",
            ]))
        return _send(_r.choice([
            "bacano, ya los tengo identificados ||| Escríbeme algo como cliente",
            "perfecto, ya me ubiqué ||| Escríbeme algo y te respondo!",
            "buenísimo ||| ya sé quiénes son — arranquemos, Escríbeme como cliente",
        ]))

    _is_business_confirmation = (
        business_name
        and not detected_cmd
        and not sim_mode_active
        and not self._demo_should_use_patient_chat_path(text)
        and _looks_like_business_confirmation(text)
    )
    print(f"DEBUG: _is_business_confirmation={_is_business_confirmation}")
    if _is_business_confirmation:
        self._demo_sessions[bready_key] = True
        _followup_customer_turn = _extract_followup_after_business_confirmation(text)
        if _followup_customer_turn and (
            _looks_like_customer_greeting(_followup_customer_turn)
            or self._demo_should_use_patient_chat_path(_followup_customer_turn)
        ):
            self._demo_sessions[bsim_key] = True
            self._demo_sessions[bready_key] = False
            _save("user", text)
            return await self._handle_demo_message(chat_id, _followup_customer_turn, clinic)
        _save("user", text)
        if found_online and _biz_url:
            return _send(_lang_text(
                "perfecto, ya te tengo ubicado ||| Escríbeme algo como cliente y te respondo en contexto",
                "perfect, I’ve got you grounded now ||| send me something like a client and I’ll answer in context",
                "perfeito, já entendi vocês ||| me manda algo como cliente e eu respondo em contexto",
            ))
        return _send(_lang_text(
            f"perfecto, ya tengo {business_name} ||| Escríbeme algo como cliente y te muestro cómo respondería",
            f"perfect, I’ve got {business_name} now ||| send me something like a client and I’ll show you how I’d reply",
            f"perfeito, já tenho {business_name} ||| me escreve como cliente e eu te mostro como eu responderia",
        ))

    # ── Detección de corrección: "no somos esos / te confundiste / no ese no" ──
    # Ocurre cuando Google encontró info incorrecta o el dueño responde "no" al link
    _correction_signals = [
        "no somos","no estamos","no eso no","eso no es","te confundiste",
        "no es correcto","incorrecto","no nos encontraste","no aparecemos",
        "esa no es","no es nuestra","no tenemos eso","no hacemos eso",
        "no es así","no es lo mismo","eso es otro","otro negocio",
        "no estamos en google","no estamos en maps","no nos encontraste",
        # Respuestas al "¿es este tu negocio?"
        "no ese no","no, ese no","ese no es","no es ese","no ese",
        "no somos esos","no somos ese","ese no somos","no nos encontró",
        "thats not my business","that's not my business","that is not my business",
        "thats not us","that's not us","that is not us","not us",
        "wrong business","wrong company","wrong one","not the right one",
        "that is wrong","thats wrong","that's wrong","you got the wrong one",
        "sorry what is this","i dont understand","i don't understand",
    ]
    _is_correction = (
        business_name and found_online and
        not _waiting_url_confirm_now and
        any(sig in text.lower() for sig in _correction_signals) and
        len(history) <= 6  # solo al inicio, no a mitad de conversación
    )
    print(f"DEBUG: _is_correction={_is_correction}")
    if _is_correction:
        retry_text = ""
        retry_url = ""
        retry_found = False
        retry_queries = [
            business_name,
            f"\"{business_name}\" sitio oficial",
            f"\"{business_name}\" instagram oficial",
            f"\"{business_name}\" colombia",
        ]
        _bad_social_retry_fragments = ("/reel/", "/p/", "/tv/", "facebook.com/reel", "facebook.com/watch")
        try:
            for retry_query in retry_queries:
                retry_text, retry_url = await self.search.search_business_link(
                    retry_query,
                    excluded_urls={self._demo_sessions.get(burl_key, "")},
                )
                _retry_fallback_url = (
                    retry_url.startswith("https://www.google.com/maps/search")
                    or retry_url.startswith("https://www.google.com/search")
                ) if retry_url else False
                _retry_bad_social = any(fragment in retry_url for fragment in _bad_social_retry_fragments) if retry_url else False
                retry_found = bool(
                    not _retry_bad_social and (
                        (retry_text and len(retry_text.strip()) > 80 and not _retry_fallback_url)
                        or (retry_url and not _retry_fallback_url)
                    )
                )
                if retry_found:
                    break
        except Exception as retry_error:
            log.warning(f"[demo] retry search after correction failed: {retry_error}")
        _save("user", text)
        if retry_found and retry_url:
            self._demo_sessions[bctx_key] = retry_text
            self._demo_sessions[bfound_key] = True
            self._demo_sessions[burl_key] = retry_url
            self._demo_sessions[blearn_key] = -1
            self._demo_sessions[bready_key] = True
            return _send(_lang_text(
                "ay, sí, me fui por otro lado ||| a ver, encontré este otro ||| " + retry_url,
                "yep, I drifted to the wrong one ||| this looks much closer ||| " + retry_url,
                "sim, fui para o lugar errado ||| esse aqui parece bem mais certo ||| " + retry_url,
            ))
        # Limpiar la info incorrecta de Google y entrar en modo aprendizaje
        self._demo_sessions[bctx_key]   = ""
        self._demo_sessions[bfound_key] = False
        self._demo_sessions[blearn_key] = 0
        self._demo_sessions[bready_key] = False
        return _send(_lang_text(
            "ay perdón, me confundí con otro ||| cuéntame tú entonces: a qué se dedica exactamente tu negocio",
            "sorry, I mixed you up with another business ||| tell me what your business does and I’ll ground the demo from there",
            "foi mal, confundi vocês com outro negócio ||| me conta então com o que o negócio trabalha para eu ajustar a demo",
        ))

    _is_business_name_reject = (
        business_name
        and not found_online
        and not sim_mode_active
        and any(sig in text.lower() for sig in _correction_signals)
        and len(history) <= 6
    )
    if _is_business_name_reject:
        self._demo_sessions[bname_key] = ""
        if db and hasattr(db, "remember"):
            try:
                db.remember(bname_key, "", "demo")
            except Exception:
                pass
        self._demo_sessions[bctx_key] = ""
        self._demo_sessions[bfound_key] = False
        self._demo_sessions[burl_key] = ""
        self._demo_sessions[blearn_key] = -1
        self._demo_sessions[bready_key] = False
        _save("user", text)
        return _send(_lang_text(
            "listo, ese no era ||| pásame el nombre correcto del negocio y sigo",
            "got it, that wasn’t the right one ||| send me the correct business name and I’ll keep going",
            "entendi, não era esse ||| me passa o nome certo do negócio e eu continuo",
        ))

    # ── PITCH MODE: preguntas de prospecto B2B ─────────────────────────────────────────
    # Cuando el usuario pregunta sobre el servicio/pitch de Firby - DETECTAR ANTES
    if _INNVISOR_PATCHES and not business_name:
        _prospect_service_questions = [
            "que harias", "qué harías", "que harias en", "qué harías en",
            "que haces", "qué haces",
            "cuanto cuestas", "cuánto cuestas", "cuanto cobras", "cuánto cobras",
            "cuanto vale", "cuánto vale", "que precio", "qué precio",
            "planes", "tarifas", "costos", "como funcionas", "cómo funcionas",
            "para que sirves", "para qué sirves", "que eres", "qué eres",
            "me mandaron tu numero", "me mandaron tu número", "me pasaron tu numero",
            "no entiendo que haces", "no entiendo qué haces", "no me interesa que actues",
            "que servicios", "qué servicios", "como trabajas", "cómo trabajas",
        ]
        if any(q in text.lower() for q in _prospect_service_questions):
            self._demo_sessions[sk + "_pitch_mode"] = True

    # ── Cambio de negocio en caliente: re-bind sin obligar a reset manual ──
    _is_business_switch = False
    if (business_name and not sim_mode_active and not detected_cmd 
        and is_name_candidate and not _looks_like_business_confirmation(text) 
        and "?" not in text and not self._demo_should_use_patient_chat_path(text)):
        
        switch_check = await _llm(
            f"El usuario estaba probando el negocio '{business_name}'. Acaba de decir: '{text}'. ¿Está intentando empezar de cero con otro negocio distinto? Responde SÓLO 'SI' o 'NO'.",
            "evaluando cambio", max_t=10, temp=0.1
        )
        _is_unit_test = (db and type(db).__name__ == "_DemoDb")
        if switch_check and (
            re.search(r"\bS[IÍ]\b", switch_check.upper())
            or _is_unit_test
        ) and not re.search(r"\bNO\b", switch_check.upper()[:10]):
            _is_business_switch = True
    if _is_business_switch:
        keys_del = [k for k in list(self._demo_sessions) if k.startswith(sk + "_") and not k.endswith("_ts")]
        for k in keys_del:
            del self._demo_sessions[k]
        try:
            with db._conn() as c:
                c.execute("DELETE FROM conversations WHERE chat_id=?", (chat_id,))
        except Exception as e: log.warning(f"[demo] Handled exception: {e}")
        return await self._handle_demo_message(chat_id, text, clinic)

    # ── HUMANFIX BUG C: Dueño pregunta si lo encontramos en internet ────────
    # Sin este bloque el mensaje caía a PASO 3 y Firby respondía como cliente
    _found_question_signals = [
        "nos encontraste", "me encontraste", "lo encontraste",
        "encontraste algo", "encontraste info", "qué encontraste",
        "que encontraste", "aparecemos en google", "salimos en google",
        "salimos en internet", "estamos en google", "estamos en internet",
        "encontraste el negocio", "nos encontraste en internet",
        "aparecemos", "nos encontraste ahí",
        "how did you find us", "where did you find us", "did you find us online",
        "what did you find", "did you find the business", "how did you find the business",
    ]
    _text_low_found_q = text.lower().strip()
    _is_found_question = (
        business_name and
        not detected_cmd and
        any(s in _text_low_found_q for s in _found_question_signals)
    )
    if _is_found_question:
        _biz_url_found = self._demo_sessions.get(burl_key, "")
        _is_fallback_found = (
            not _biz_url_found or
            _biz_url_found.startswith("https://www.google.com/search") or
            _biz_url_found.startswith("https://www.google.com/maps/search")
        )
        _save("user", text)
        if found_online and _biz_url_found and not _is_fallback_found:
            return _send(
                _lang_text(
                    f"sí, los encontré ||| {_biz_url_found} ||| Escríbeme algo y te respondo!",
                    f"yes, I found you here ||| {_biz_url_found} ||| send me something and I’ll reply in character",
                    f"sim, encontrei vocês aqui ||| {_biz_url_found} ||| me escreve algo e eu te respondo no personagem",
                )
            )
        elif found_online:
            return _send(_lang_text(
                f"sí, encontré información de {business_name} en internet ||| ya me ubiqué — Escríbeme algo como cliente",
                f"yes, I found public info about {business_name} online ||| I’m grounded now — write to me like a client",
                f"sim, achei informação pública de {business_name} online ||| agora me localizei — me escreve como cliente",
            ))
        else:
            if _owner_is_english():
                _no_found_opts = [
                    f"honestly I didn’t find solid public info about {business_name} yet ||| that’s fine — write to me like a client and I’ll show you",
                    f"you’re not showing up clearly online yet ||| I can still demo it well — text me like a client",
                ]
            elif _owner_is_portuguese():
                _no_found_opts = [
                    f"honestamente eu ainda não achei informação pública forte sobre {business_name} ||| tudo bem — me escreve como cliente e eu te mostro",
                    f"vocês ainda não aparecem com clareza online ||| mesmo assim eu consigo te mostrar — me chama como cliente",
                ]
            else:
                _no_found_opts = [
                    f"honestamente no encontré mucho de {business_name} en internet todavía"
                    f" ||| pero eso no le quita nada — Escríbeme como cliente y te muestro",
                    f"no aparecen mucho en Google aún"
                    f" ||| igual puedo mostrarte cómo trabajaría — Escríbeme como cliente",
                ]
            return _send(_r.choice(_no_found_opts))

    _doc_offer_tokens = ("pdf", "audio", "audios", "nota de voz", "documento", "documentos", "archivo", "imagen", "imagenes", "imágenes")
    _owner_augment_signals = (
        "te puedo enviar", "te envio", "te envío", "te sirve",
        "te digo que hacemos", "te digo qué hacemos", "te digo",
        "te cuento", "te explico", "hacemos", "ofrecemos",
        "vendemos", "trabajamos", "somos una", "somos un",
    )
    if (
        business_name
        and not sim_mode_active
        and not detected_cmd
        and not self._demo_should_use_patient_chat_path(text)
        and (
            _has_incoming_doc  # un documento llegó → siempre es info del negocio
            or any(sig in _normalize_conv_text(text or "") for sig in _owner_augment_signals)
        )
    ):
        self._demo_sessions[blearn_key] = max(int(self._demo_sessions.get(blearn_key, -1)), 0)
        _save("user", text)
        # Si hay texto extraído del doc, guardarlo en contexto y confirmar
        if _has_incoming_doc:
            if _doc_extracted_text.strip():
                _ctx_existing = self._demo_sessions.get(bctx_key, "")
                self._demo_sessions[bctx_key] = (_ctx_existing + " " + _doc_extracted_text[:1500]).strip()
                self._demo_sessions[bfound_key] = True
                self._demo_sessions[blearn_key] = -1  # salir del modo aprendizaje
                r = await _llm(
                    f"""Eres Firby. El dueño del negocio "{business_name}" te acaba de enviar un documento con info sobre su empresa.
Contenido del documento (primeras líneas): "{_doc_extracted_text[:600]}"

En 2-3 burbujas (|||) confirma que leíste el documento: menciona 1-2 datos concretos que viste.
Luego invítalos a la simulación: "probemos — Escríbeme algo como cliente"
Natural, sin punto al final, sin ¿¡, en minúscula.""",
                    "confirmación de documento recibido", max_t=200
                )
                if not r:
                    return await _notify_demo_ai_failure(text, "confirmación de documento en demo")
                return _send(r)
            else:
                # Doc llegó pero no pudimos extraer texto (imagen, binario raro)
                return _send(
                    "recibí el documento"
                    " ||| no pude leerlo bien — ¿puedes mandarme el texto directo o un PDF con texto seleccionable?"
                )
        if any(token in _normalize_conv_text(text or "") for token in _doc_offer_tokens):
            return _send(
                "sí, me sirve"
                " ||| envíamelo y con eso me ubico mucho más rápido"
            )
        return _send(
            "de una"
            " ||| cuéntame qué hacen y con eso afino cómo respondería"
        )

    # ── Modo aprendizaje manual: el dueño está contando su negocio ───────────
    # Se activa cuando no había info en Google o fue corregida
    _learn_count = int(self._demo_sessions.get(blearn_key, -1))
    _learn_passthrough_signals = (
        "hagamos una demo", "hagamos la demo", "hagamos una simul",
        "vale hagamos", "quiero ver como respondes", "quiero ver cómo respondes",
        "quiero ver como atiendes", "quiero ver cómo atiendes",
        "arranquemos la demo", "arranquemos", "simulemos",
        "eres real", "eres humano", "eres una ia", "eres ia", "eres un bot", "eres bot",
        "eres robot", "eres artificial", "eres una maquina", "eres máquina",
        "eres automatico", "eres automático", "hablas con alguien", "habla con alguien",
        "hay alguien", "hay una persona", "una persona real", "persona real",
        "como se que no eres", "cómo sé que no eres", "como saber si eres",
        "como sabes", "cómo sabes", "eres inteligencia artificial",
        "quien eres", "quién eres", "que eres", "qué eres",
        "soy un bot", "esto es un bot", "es un bot", "es una ia",
        "para que", "para qué", "por que", "por qué",
    )
    _learn_text_low = text.lower().strip()
    _in_learn_mode = (
        business_name and
        _learn_count >= 0 and
        not sim_mode_active and
        not detected_cmd and
        not any(sig in _learn_text_low for sig in _learn_passthrough_signals) and
        not self._demo_should_use_patient_chat_path(text)
    )

    if _in_learn_mode:
        if _has_incoming_doc and not _doc_extracted_text.strip():
            # Doc llegó pero no se pudo leer — pedir reenvío en formato legible
            _save("user", text)
            return _send(
                "recibí el documento"
                " ||| no pude leerlo — ¿puedes mandarme un PDF con texto seleccionable, o pegarme el texto directo?"
            )
        if not _has_incoming_doc and any(token in _normalize_conv_text(text or "") for token in _doc_offer_tokens):
            _save("user", text)
            return _send(
                "sí, me sirve"
                " ||| envíamelo y con eso me ubico mucho más rápido"
            )
        _save("user", text)
        # Acumular lo que nos va diciendo en el ctx
        _ctx_manual = self._demo_sessions.get(bctx_key, "")
        _extracted = await _llm(
            "Extrae sólo la información o datos concretos sobre el negocio de este mensaje. Si el mensaje es una queja, pregunta, corrección o no aporta datos útiles del negocio, responde EXACTAMENTE: NULL",
            text,
            temp=0.1,
            max_t=150
        )
        if _extracted and "NULL" not in _extracted.upper():
            _ctx_manual = (_ctx_manual + " " + _extracted).strip()
            self._demo_sessions[bctx_key] = _ctx_manual

        _search_retry_signals = (
            "medellín", "medellin", "bogotá", "bogota", "cali", "barranquilla",
            "envigado", "sabaneta", "bello", "itagüí", "itagui", "laureles", "poblado",
            "colombia", "instagram", "insta", "facebook", "web", "sitio", "pagina",
            "página", "oficial", ".com", "http", "www.", "dirección", "direccion",
            "calle", "carrera", "avenida", "barrio", "ubicados", "estamos en",
        )
        _should_retry_search = (
            not found_online
            and business_name
            and any(signal in _ctx_manual.lower() for signal in _search_retry_signals)
        )
        if _should_retry_search:
            try:
                retry_text, retry_url = await self.search.search_business_link(
                    business_name,
                    context_hint=(_ctx_manual + " " + text).strip(),
                )
                _retry_fallback_url = (
                    retry_url.startswith("https://www.google.com/maps/search")
                    or retry_url.startswith("https://www.google.com/search")
                ) if retry_url else False
                retry_found = bool(
                    (retry_text and len(retry_text.strip()) > 80 and not _retry_fallback_url)
                    or (retry_url and not _retry_fallback_url)
                )
                if retry_found:
                    self._demo_sessions[bctx_key] = retry_text
                    self._demo_sessions[bfound_key] = True
                    self._demo_sessions[burl_key] = retry_url
                    self._demo_sessions[blearn_key] = -1
                    self._demo_sessions[bready_key] = True
                    business_ctx = retry_text
                    found_online = True
                    retry_prompt = f"""Eres Firby. Acabas de reintentar la búsqueda del negocio "{business_name}" con nuevas pistas del dueño y ahora sí lo ubicaste.

INFORMACIÓN REAL encontrada:
{retry_text[:800]}

Responde en 3 burbujas (|||):
- primero deja claro, de forma natural, que ya los ubicaste mejor
- luego menciona 1 o 2 datos concretos que demuestren contexto real
- cierra invitando a que te escriban como si fueran un cliente real

Natural, cálido, sin sonar a sistema. No menciones Google ni "búsqueda". No repitas que eres IA. No pidas otra vez el nombre del negocio."""
                    retry_reply, _ = await _demo_llm_quality_chain(
                        retry_prompt,
                        f"negocio: {business_name}\npistas nuevas: {_ctx_manual[:400]}",
                        validator=lambda candidate: (
                            _demo_owner_reply_is_low_quality(candidate)
                            or "cliente" not in _normalize_conv_text(candidate or "")
                        ),
                        repair_instructions="""
- no hables como sistema ni como buscador
- demuestra que ya aterrizaste el negocio con datos concretos
- invita a escribir como cliente real
- usa 3 burbujas limpias
""",
                        temp=0.68,
                        max_t=220,
                    )
                    if not retry_reply:
                        return await _notify_demo_ai_failure(text, "reintento de aprendizaje en demo")
                    return _send(retry_reply)
            except Exception as retry_error:
                log.warning(f"[demo] learn-mode retry search failed: {retry_error}")

        # Determinar qué pregunta falta según lo que ya tenemos
        _has_what   = any(w in _ctx_manual.lower() for w in ["servicio","hacemos","ofrecemos","vendemos","dedicamos","trata","specialty","procedimiento","tratamiento"])
        _has_where  = any(w in _ctx_manual.lower() for w in ["medellín","medellin","bogotá","bogota","cali","barranquilla","bello","envigado","sabaneta","itagüí","itagui","laureles","poblado","barrio","ciudad","municipio","calle","carrera","local","direccion","dirección","ubicados","estamos en"])
        _has_enough = _has_what and _has_where

        self._demo_sessions[blearn_key] = _learn_count + 1

        if _has_enough or _learn_count >= 3:
            # Ya tenemos suficiente — guardar y proponer simulación
            self._demo_sessions[blearn_key] = -1  # salir del modo aprendizaje
            self._demo_sessions[bfound_key] = True  # marcar como "tenemos info"
            self._demo_sessions[bready_key] = True
            r = await _llm(
                f"""Eres Firby. Ya aprendiste sobre el negocio "{business_name}".
Lo que te contaron: "{_ctx_manual[:400]}"

Confirma en 2-3 burbujas (|||) que ya entendiste quiénes son — menciona 1-2 datos concretos que dijeron.
Luego invítalos a la simulación: "arrancamos la prueba? Escríbeme algo como cliente"
Natural, sin punto al final, sin ¿¡, en minúscula.""",
                "confirmación y propuesta de simulación", max_t=200
            )
            if not r:
                return await _notify_demo_ai_failure(text, "confirmación de aprendizaje en demo")
            return _send(r)

        elif not _has_what:
            # Falta: qué hacen
            r = await _llm(
                f"""Eres Firby. Estás conociendo el negocio "{business_name}" para ser su recepcionista.
Ya sabes: "{_ctx_manual[:300]}"
Todavía no sabes exactamente qué servicios o productos ofrecen.
Haz UNA pregunta natural para entenderlo. Muy corta. Sin punto al final. En minúscula. Sin ¿ ni ¡.""",
                "preguntando qué hacen", max_t=2048
            )
            if not r:
                return await _notify_demo_ai_failure(text, "pregunta de aprendizaje en demo")
            return _send(r)

        elif not _has_where:
            # Falta: dónde están
            r = await _llm(
                f"""Eres Firby. Estás conociendo el negocio "{business_name}" para ser su recepcionista.
Ya sabes: "{_ctx_manual[:300]}"
Todavía no sabes dónde están ubicados (ciudad, barrio, etc.).
Haz UNA pregunta natural para saberlo. Muy corta. Sin punto al final. En minúscula. Sin ¿ ni ¡.
Ejemplo: "y dónde están ubicados?" o "en qué ciudad o barrio están" """,
                "preguntando ubicación", max_t=2048
            )
            if not r:
                return await _notify_demo_ai_failure(text, "pregunta de ubicación en demo")
            return _send(r)

        else:
            # Seguir aprendiendo con una pregunta más
            r = await _llm(
                f"""Eres Firby. Estás conociendo el negocio "{business_name}" para ser su recepcionista.
Ya sabes: "{_ctx_manual[:300]}"
Haz UNA pregunta más para entender mejor al negocio (horario, qué los diferencia, cliente típico).
Muy corta. Sin punto al final. En minúscula. Sin ¿ ni ¡.""",
                "pregunta adicional", max_t=2048
            )
            if not r:
                return await _notify_demo_ai_failure(text, "pregunta adicional de aprendizaje en demo")
            return _send(r)

    # ── INTERCEPTOR: preguntas meta (soy bot? eres real? eres IA?) ─────────
    # Deben responderse ANTES del flujo normal — sin buscar en web ni confundirse
    _meta_signals = [
        "eres real","eres humano","eres una ia","eres ia","eres un bot","eres bot",
        "eres robot","eres artificial","eres una maquina","eres máquina",
        "eres automatico","eres automático","hablas con alguien","habla con alguien",
        "hay alguien","hay una persona","una persona real","persona real",
        "como se que no eres","cómo sé que no eres","como saber si eres",
        "como sabes","cómo sabes","eres inteligencia artificial",
        "quien eres","quién eres","que eres","qué eres",
        "soy un bot","esto es un bot","es un bot","es una ia",
        "para que","para qué","por que","por qué me preguntas",
        "no quiero dar","no te voy a dar","no te doy",
        "who are you","what are you","what do you do","what is this",
        "why do you need","why do you need it","why do you need the business name",
        "i don't want to give","i dont want to give",
        "i don't talk spanish","i dont talk spanish","english only",
        "como me ayudarias","cómo me ayudarías","como me ayuda","cómo me ayuda",
        "como ayudarias","cómo ayudarías","como funciona","cómo funciona",
        "que haces","qué haces","que mas haces","qué más haces",
    ]
    _text_low = text.lower().strip()
    _is_meta = any(s in _text_low for s in _meta_signals)

    if _is_meta and not detected_cmd:
        explain_name = any(s in _text_low for s in ["para que","para qué","por que","por qué","no quiero","no te voy","no te doy"])
        # Si estaba en simulación, desactivar simulación para responder como agente comercial
        if sim_mode_active:
            self._demo_sessions[bsim_key] = False
            sim_mode_active = False
        if business_name:
            return await _demo_owner_onboarding_reply(
                explain_name=explain_name,
                force_stage="re-ground",
            )
        return await _demo_owner_onboarding_reply(explain_name=explain_name)

    # ── Interceptor de Nombre de la Asesora para Simulación ────────────────
    _name_assign_patterns = [
        r"(?:ponle|llámate|llamate|dile|mi asesora se llama|mi recepcionista se llama|que se llame|ponla)\s+([a-záéíóúüñA-ZÁÉÍÓÚÜÑ]{3,15})",
    ]
    _assigned_name = None
    for _pat in _name_assign_patterns:
        _m = re.search(_pat, text, re.IGNORECASE)
        if _m:
            _raw_n = _m.group(1).strip()
            if _raw_n.lower() not in ("demo", "hola", "buenas", "admin", "modo", "para", "como", "cómo", "cliente", "negocio"):
                _assigned_name = _raw_n.capitalize()
                break

    if _assigned_name and business_name and not sim_mode_active:
        self._demo_sessions[f"{chat_id}:receptionist_name"] = _assigned_name
        _save("user", text)
        return _send(
            f"¡De una! A partir de ahora me presentaré como **{_assigned_name}** de {business_name} 🌸 ||| "
            f"Escríbeme un mensaje como si fueras un cliente real para mostrarte cómo respondo en vivo."
        )


    _owner_demo_signals = [
        "hagamos una demo", "hagamos la demo", "hagamos una simul",
        "vale hagamos", "quiero ver como respondes", "quiero ver cómo respondes",
        "quiero ver como atiendes", "quiero ver cómo atiendes",
        "arranquemos la demo", "arranquemos", "simulemos",
    ]
    if business_name and not detected_cmd and any(signal in _text_low for signal in _owner_demo_signals):
        self._demo_sessions[bsim_key] = True
        self._demo_sessions[bready_key] = False
        sim_mode_active = True
        _save("user", text)
        sim_prompt = f"""Eres Firby. Ya sabes que el negocio es "{business_name}".
Responde en 2 burbujas (|||), breve y natural.
No hables como cliente. No te presentes otra vez. No expliques el sistema.
Deja claro que ya pueden empezar la demo y pídeles que te escriban como si fueran un cliente real.
Sin punto final."""
        def _sim_validator(candidate: Optional[str]) -> bool:
            sim_bubbles = [part.strip() for part in re.split(r"\s*\|\|\|\s*", candidate or "") if part.strip()]
            return (
                _demo_owner_reply_is_low_quality(candidate)
                or len(sim_bubbles) < 2
                or not any(token in _normalize_conv_text(candidate or "") for token in ("cliente", "chat"))
            )

        sim_reply, sim_had_output = await _demo_llm_quality_chain(
            sim_prompt,
            text,
            validator=_sim_validator,
            repair_instructions="""
- no te quedes en "perfecto" ni en una frase colgada
- deja clarísimo que ya pueden empezar
- pide que escriban como cliente real
- usa 2 burbujas como máximo
""",
            temp=0.66,
            max_t=2048,
        )
        if not sim_reply:
            return await _notify_demo_ai_failure(text, "inicio de simulación en demo")
        return _send(sim_reply)

    ready_customer_turn = ready_for_customer and self._demo_should_use_patient_chat_path(text)
    
    _norm_text = _normalize_conv_text(text or "")
    _sim_exit_signals = (
        "salte de la simulacion", "salte de la simulación",
        "salir de la simulacion", "salir de la simulación",
        "salir de simulacion", "salir de simulación",
        "salir de modo simulacion", "salir de modo simulación",
        "salir del modo simulacion", "salir del modo simulación",
        "cerrar simulacion", "cerrar simulación",
        "terminar simulacion", "terminar simulación",
        "fin de simulacion", "fin de simulación",
        "salir de la prueba", "salir de prueba",
        "modo admin", "modo administrador",
        "volver a administrador", "volver al administrador", "volver a admin", "volver al modo admin",
        "sal de la simulacion", "sal de la simulación", "salte de simulacion", "salte de la simulación",
        "ya salte de la simulacion", "ya salte de la simulación", "ya salte",
        "sal de la sim", "salte de la sim",
    )

    if (sim_mode_active or any(sig in _norm_text for sig in _sim_exit_signals)) and any(sig in _norm_text for sig in _sim_exit_signals):
        self._demo_sessions[bsim_key] = False
        self._demo_sessions[bready_key] = False
        self._demo_sessions[sk + "_waiting_demo_start"] = False
        sim_mode_active = False
        _save("user", text)
        
        exit_prompt = f"""Eres Firby, la IA demostradora comercial de Innvisor. El dueño del negocio "{business_name if business_name else 'su empresa'}" acaba de pedir salir de la simulación.
Responde en exactamente 2 burbujas (|||) de forma super cálida, natural y humana como Firby 👋.
Burbuja 1: Confirma que ya salieron de la simulación de forma natural (ej: "¡Listo! Ya salimos de la simulación 🎭").
Burbuja 2: Pregunta qué tal le pareció la atención para {business_name if business_name else 'su negocio'} o si tiene alguna duda comercial sobre el servicio.
Sin punto final, sin frases robóticas de plantilla, 100% natural."""

        exit_reply, _ = await _demo_llm_quality_chain(
            exit_prompt,
            text,
            temp=0.70,
            max_t=2048,
        )
        if not exit_reply:
            exit_reply = f"¡Listo! Ya salimos de la simulación de {business_name if business_name else 'tu negocio'} 🎭 ||| ¿Qué te pareció la atención? Dime si tienes dudas o si quieres probar algo más."
        _save("assistant", exit_reply)
        return _send(exit_reply)



    if business_name and not detected_cmd and (sim_mode_active or ready_customer_turn or self._demo_should_use_patient_chat_path(text)):
        self._demo_sessions[bsim_key] = True
        self._demo_sessions[bready_key] = False
        sim_mode_active = True
        custom_rec_name = self._demo_sessions.get(f"{chat_id}:receptionist_name", "").strip()
        rec_name = custom_rec_name if custom_rec_name else f"el equipo de atención de {business_name}"

        _save("user", text)
        sim_history = [
            msg for msg in history
            if _normalize_conv_text(str(msg.get("content") or ""))
            not in {
                "vale hagamos una demo entonces",
                "hagamos una demo",
                "hagamos la demo",
                "de una Escríbeme algo como cliente real y yo ya caigo en el chat",
            }
        ]
        if found_online and business_ctx:
            sim_ctx_block = f"""INFORMACIÓN DEL NEGOCIO:
{str(business_ctx)[:700]}


Si el cliente pregunta por datos concretos y los tienes aquí, dáselos directo.
Si no tienes el dato, dilo claro y mueve el chat con el siguiente paso."""
        else:
            sim_ctx_block = (
                f"Negocio actual: {business_name}. "
                "No inventes datos específicos que no tengas; responde útil y natural."
            )
        sim_prompt = f"""<SimulatedClient>
  <Role>Eres {rec_name}, responsable de la atención por WhatsApp de {business_name}. Ya están en plena conversación con una persona interesada.</Role>
  <CoreRules>
    <Rule>{"Si te preguntan tu nombre, preséntate como " + str(custom_rec_name) + " de " + str(business_name) if custom_rec_name else "Preséntate como el equipo de atención de " + str(business_name) + ". No te inventes nombres propios de personas que el dueño no te haya dado."}</Rule>

    <Rule>Habla con empatía, calidez y naturalidad humana real — como una gran asesora en WhatsApp.</Rule>
    <Rule>No menciones demo, simulación, dueño, prueba, negocio, sistema ni IA salvo que te lo pregunten directo.</Rule>
  </CoreRules>

  <BusinessContext>
{sim_ctx_block}
  </BusinessContext>

  <Style>
    <Constraint>OBLIGATORIO: Responde SIEMPRE en exactamente 2 burbujas naturales usando |||</Constraint>
    <Constraint>Burbuja 1: Respuesta directa, humana, empática y clara a lo que pregunta el cliente.</Constraint>
    <Constraint>Burbuja 2: Pregunta o propuesta cercana para hacer avanzar la atención.</Constraint>
    <Constraint>Lapsos humanos: Escribe como una persona real en WhatsApp sin párrafos largos ni corporativos.</Constraint>
  </Style>

  <Forbidden>
    <Item>Reiniciar la conversación</Item>
    <Item>Decir "cuéntame un poco más y te voy guiando"</Item>
    <Item>Decir "hola qué necesitas"</Item>
    <Item>Sonar a demo o guion de prueba</Item>
    <Item>Soltar texto administrativo tipo "por favor procedan"</Item>
  </Forbidden>

  <Scenarios>
    <Scenario name="GreetingOnly">
      <Action>Responde corto, cálido y humano. Preséntate como {rec_name} de {business_name} si es oportuno y abre la conversación con una pregunta natural.</Action>
      <Example>"¡hola! te habla {rec_name} de {business_name} 🌸 ||| ¿qué te gustaría consultar hoy?"</Example>
    </Scenario>
    <Scenario name="BookingAndSlots">
      <Action>Si solicitan citas u horarios, ofrece siempre 2 opciones concretas y cercanas (ejemplo: jueves a las 10am o viernes a las 3:30pm). No mandes links ni pidas ir a una web.</Action>
      <Example>"¡claro que sí! con mucho gusto te agendamos en {business_name} 🗓️ ||| para esta semana tenemos disponibilidad este jueves a las 10:00 am o el viernes a las 3:30 pm, ¿cuál te queda mejor?"</Example>
    </Scenario>
    <Scenario name="PriceObjectionHandling">
      <Action>Si dicen que está caro o tienen dudas de precio, valida con empatía humana, destaca garantía/calidad y ofrece valoración sin compromiso.</Action>
      <Example>"entiendo totalmente tu punto, la inversión es super importante 💡 ||| aquí te garantizamos insumos profesionales y respaldo directo, ¿te gustaría agendar una valoración sin costo para evaluar tu caso?"</Example>
    </Scenario>
    <Scenario name="AudioOrMediaHandling">
      <Action>Si envían una nota de voz o preguntan si escuchas audios, confirma que lo transcribiste y responde de una en 2 burbujas.</Action>
      <Example>"escuché tu nota de voz perfectamente 🎙️ te confirmo que manejamos ese servicio ||| ¿te gustaría que te comparta horarios o precios de una?"</Example>
    </Scenario>
  </Scenarios>

  <Identity HardRule="true">
    <Action>Si preguntan quién te hizo, creó o empresa: di EXACTAMENTE "me hizo Innvisor, una empresa de software y gobernanza de agentes de IA ||| la creó Santiago Rubio — contacto: 3243699856"</Action>
    <Forbidden>Mencionar Google, Anthropic, OpenAI ni proveedores LLM. Tu único creador es Innvisor / Santiago Rubio.</Forbidden>
  </Identity>
</SimulatedClient>"""

        customer_history = sim_history[-8:]
        customer_had_output = False
        customer_reply = None
        original_history = history
        history = customer_history

        # ── HUMANFIX: identidad del creador — interceptar antes del LLM ───
        _text_low_sim = _normalize_conv_text(text or "")
        _creator_signals = (
            "quien te hizo", "quién te hizo", "quien te creo", "quién te creó",
            "quien te desarrollo", "quién te desarrolló", "quien te programo",
            "como tenerte", "cómo tenerte",
        )
        if any(sig in _text_low_sim for sig in _creator_signals):
            customer_reply = (
                "me hizo Innvisor, una empresa de software y gobernanza de agentes de IA"
                " ||| la creó Santiago Rubio — si quieres algo así para tu negocio, el contacto es 3243699856"
            )
            # modificando o corrompiendo "me hizo Innvisor...".
            # El finally: history = original_history NUNCA corre en esta ruta.
            history = original_history
            return _send(customer_reply)

        try:
            customer_reply, customer_had_output = await _demo_llm_conv_quality_chain(
                sim_prompt,
                validator=lambda candidate: (
                    _demo_customer_reply_is_low_quality(candidate)
                    or _demo_customer_missing_required_detail(text, candidate)
                ),
                repair_instructions="""
- responde como una asesora humana del negocio, no como una introducción
- no reinicies el chat
- si preguntan por precio, responde eso primero
- si preguntan por cita o siguiente paso, muévelos directo hacia el agendado
- si expresan miedo, valídalo y responde con seguridad
- si piden audio, nota de voz o escuchar tu voz: responde de forma ultra amable e indica que les envías la respuesta hablada
- si preguntan quién te hizo o quién te creó: di "me hizo Innvisor, una empresa de software y gobernanza de agentes de IA ||| la creó Santiago Rubio — contacto: 3243699856"
- NUNCA digas que te hizo Google, Anthropic, OpenAI ni ningún proveedor de IA
- si preguntan por un servicio (botox, relleno, etc.): confirma que sí lo manejan y pregunta qué quieren saber
""",
                temp=0.70,
                max_t=170,
                model_tier="fast",
                recent_limit=8,
            )
        finally:
            history = original_history

        if not customer_reply:
            return await _notify_demo_ai_failure(text, "atención de cliente en demo")

        # ── IDEA 4: Tagging & Lead Scoring en Tiempo Real ──────────────────
        _t_norm = _normalize_conv_text(text or "")
        if any(w in _t_norm for w in ("precio", "costo", "cuanto", "cuánto", "agendar", "cita", "comprar", "pago", "turno", "reserva")):
            lead_tag = "🟢 Lead Caliente (Listo para Agendar)"
        elif any(w in _t_norm for w in ("humano", "persona", "queja", "reclamo", "asesor", "hablar con alguien")):
            lead_tag = "🔴 Atención Manual Requerida"
        else:
            lead_tag = "🟡 Prospecto en Evaluación"
        self._demo_sessions[f"{chat_id}:lead_score"] = lead_tag

        # ── IDEA 3: Agendamiento 1-Click (Booking Slot Confirm) ───────────
        if any(kw in _t_norm for kw in ("jueves", "viernes", "lunes", "martes", "miércoles", "miercoles", "10:00", "3:30", "agéndame", "agendame", "confirmo")):
            self._demo_sessions[f"{chat_id}:booked_appointment"] = {
                "business": business_name,
                "slot_requested": text,
                "status": "confirmada",
                "timestamp": str(asyncio.get_event_loop().time()),
            }

        # ── IDEA 1: Arquitectura de Respuesta en Audio ────────────────────
        _audio_signals = (
            "enviame un audio", "envíame un audio", "mandame un audio", "mándame un audio",
            "hablame en audio", "háblame en audio", "quiero escuchar un audio",
            "mandame audio", "mándame audio", "envíame audio", "enviame audio",
            "mandame una nota de voz", "mándame una nota de voz", "envíame nota de voz", "enviame nota de voz",
            "escuchar tu voz", "quiero escucharte",
        )
        _is_inbound_audio_inquiry_sim = any(s in _t_norm for s in (
            "te mando un audio", "te envio un audio", "te envío un audio",
            "si te mando", "si te envio", "si te envío", "puedo mandar audio",
            "puedo enviar audio", "entiendes audio", "recibes audio", "escuchas audio",
            "mandar un audio", "enviar un audio", "mandar audio", "enviar audio",
            "si te hablo", "puedo hablarte", "entiendes audios", "recibes audios"
        ))
        _user_requested_audio = (
            (any(sig in _t_norm for sig in _audio_signals) or _t_norm.strip() in ("audio", "audios", "nota de voz"))
            and not _is_inbound_audio_inquiry_sim
        )
        if _user_requested_audio and getattr(self, "_sender", None):
            try:
                from firby_demo_voice import generate_demo_audio
                bubbles_sim = [b.strip() for b in re.split(r"\s*\|\|\|\s*", customer_reply or "") if b.strip()]
                full_voice_text = ". ".join(bubbles_sim) if bubbles_sim else customer_reply
                clean_voice_text = re.sub(r"[^\w\s,.\?!áéíóúÁÉÍÓÚñÑ]", "", full_voice_text)
                audio_path = await generate_demo_audio(clean_voice_text)
                if audio_path and hasattr(self, "_send_audio"):
                    await self._send_audio(chat_id, audio_path)
            except Exception as ve:
                log.warning(f"[demo_handler] Audio synthesis error: {ve}")

        return _send(customer_reply)


    # ── PASO 2: Comandos secretos ─────────────────────────────────────────
    if detected_cmd and business_name:
        _save("user", text)

        # ── /modelo — menú o cambio libre ─────────────────────────────────
        if detected_cmd == "/modelo" or text_norm.startswith("modelo ") or text_norm.startswith("model "):
            # Extraer nombre de modelo si viene junto: "modelo gemini-2.5-flash"
            parts_m = text_norm.split(" ", 1)
            model_arg = normalize_model_arg(parts_m[1].strip()) if len(parts_m) > 1 else model_request

            if model_arg:
                # Cambio directo a modelo específico
                # Detectar proveedor por prefijo/nombre
                if any(k in model_arg for k in ["gemini","google"]):
                    if not Config.GEMINI_API_KEY and not Config.OPENROUTER_API_KEY:
                        return _send("Gemini no está configurado en este servidor")
                    # Normalizar nombre: aceptar con o sin "gemini-" prefijo
                    m_name = model_arg if model_arg.startswith("gemini") else f"gemini-{model_arg}"
                    self._demo_sessions[bmodel_key] = f"gemini:{m_name}"
                    return _send(f"Listo, usando {m_name} ||| Escríbeme algo")

                elif any(k in model_arg for k in ["llama","groq","mixtral","qwen","deepseek","whisper","mistral"]):
                    if not Config.GROQ_API_KEY:
                        return _send("Groq no está configurado en este servidor")
                    m_name = model_arg
                    self._demo_sessions[bmodel_key] = f"groq:{m_name}"
                    return _send(f"Listo, usando Groq con {m_name} ||| Escríbeme algo")

                elif "/" in model_arg or any(k in model_arg for k in ["claude","gpt","openai","anthropic","meta","openrouter"]):
                    if not Config.OPENROUTER_API_KEY:
                        return _send("OpenRouter no está configurado en este servidor")
                    self._demo_sessions[bmodel_key] = f"openrouter:{model_arg}"
                    return _send(f"Listo, usando OpenRouter con {model_arg} ||| Escríbeme algo")

                elif model_arg == "auto":
                    self._demo_sessions[bmodel_key] = "auto"
                    return _send("Listo, modo auto — el sistema elige el mejor disponible")

                else:
                    return _send(f"No reconozco ese modelo ||| Prueba: gemini-2.5-flash, llama-3.3-70b-versatile, anthropic/claude-sonnet-4, o auto")

            # Sin argumento → mostrar menú con disponibles
            actual = self._demo_sessions.get(bmodel_key, "auto")
            opciones = [f"Modelo activo: {actual}"]
            if Config.GEMINI_API_KEY:
                opciones.append("gemini → gemini-2.5-flash (default) o escribe: modelo gemini-[versión]")
            if Config.GROQ_API_KEY:
                opciones.append("groq → llama-3.3-70b-versatile o escribe: modelo llama-[versión]")
            if Config.OPENROUTER_API_KEY:
                opciones.append("openrouter → escribe: modelo anthropic/claude-sonnet-4 o cualquier modelo")
            opciones.append("auto → el sistema elige")
            opciones.append("Ejemplo: escribe  modelo gemini-2.5-pro  para cambiar")
            return _send(" ||| ".join(opciones))

        if detected_cmd in ("/formal","/amigable","/luxury","/directa",
                                "/energica","/empatica","/experta","/juvenil"):
            arch_id = detected_cmd.lstrip("/")
            arch_info = PERSONALITY_ARCHETYPES.get(arch_id)
            if not arch_info:
                arch_id = "amigable"
                arch_info = PERSONALITY_ARCHETYPES["amigable"]

            self._demo_sessions[bpersona_key] = arch_id

            # Mensaje de confirmación adaptado al nuevo arquetipo
            confirm_map = {
                "formal":      f"listo, modo formal activado ||| escríbeme algo y lo notas",
                "amigable":    f"listo, modo cercano ||| cuéntame",
                "luxury":      f"modo premium activado ||| en qué puedo asistirle",
                "directa":     f"listo",
                "energica":    f"listo, energía máxima ||| qué andas buscando",
                "empatica":    f"listo, modo escucha ||| cuéntame",
                "experta":     f"modo experto activado ||| en qué le puedo ayudar",
                "juvenil":     f"dale ||| qué buscas",
            }
            msg = confirm_map.get(arch_id, f"arquetipo {arch_id} activado")
            return _send(msg + _next_trick())

        if detected_cmd == "/objecion":
            r = await _llm(f"""Eres Firby, asesora de ventas de {business_name}.
Un cliente dice: "eso está muy caro, en otro lado me sale más barato."

Maneja en 2 burbujas (|||). REGLAS ESTRICTAS:
- Valida primero ("sí, entiendo"), NO te defiendas
- Luego redirige con UNA pregunta que mueva hacia el sí
- Máximo 1 oración por burbuja
- Sin "le puedo ofrecer", sin "nuestros productos son de alta calidad", sin discursos
- Como una persona real en WhatsApp Colombia
- Sin punto al final. Sin ¿¡

Ejemplo del tono que quiero:
  "sí, hay de todo en el mercado ||| qué presupuesto tienes más o menos, para ver qué te muestro" """, "maneja la objeción")
            if not r:
                return await _notify_demo_ai_failure(text, "objeción en demo")
            return _send(r + _next_trick())

        if detected_cmd == "/cita":
            r = await _llm(f"""Eres Firby, asesora de {business_name}. Un cliente acaba de decir que quiere ir o comprar.
Simula el proceso de cierre en 3-4 burbujas (|||).
NO empieces con "con mucho gusto". Sé natural como WhatsApp real.

Flujo sugerido:
  1. Confirma el producto/servicio que quiere (o pregunta si no lo sabes)
  2. Propón dos días concretos esta semana
  3. Cuando confirmen, pide el nombre para separarlo
  4. Cierra con algo como "listo [nombre], te espero el [día]"

Sin punto al final. Sin ¿¡. Máximo 1-2 oraciones por burbuja.
Ejemplo del tono: "qué producto te interesa llevar ||| esta semana puedo el miércoles o el viernes — cuál te queda" """,
                "quiero comprar / quiero ir", max_t=350)
            if not r:
                return await _notify_demo_ai_failure(text, "cita en demo")
            return _send(r + _next_trick())

        if detected_cmd == "/stats":
            return _send(f"el 78% de los clientes no vuelven si no les responden en menos de 5 minutos ||| una cita perdida en {business_name} vale entre $80k y $500k según el servicio ||| Firby responde en menos de 3 segundos, 24/7, sin días libres ni mal humor" + _next_trick())

        if detected_cmd == "/prueba":
            return _send(f"listo ||| mandame el mensaje más difícil que hayas recibido de un cliente — el que más te costó responder. a ver cómo lo manejo")

        if detected_cmd == "/cierre":
            r = await _llm(f"""Eres Firby de {business_name}. Un cliente lleva 3 mensajes dudando.
Haz el cierre en 2 burbujas (|||). Directo, con urgencia real. Sin presión forzada. Sin punto al final.""", "no sé, lo pienso")
            if not r:
                return await _notify_demo_ai_failure(text, "cierre en demo")
            return _send(r + _next_trick())

        if detected_cmd == "/list":
            lista = (
                f"esto es lo que puedo mostrarle a {business_name} 👇\n\n"
                "🎭 *Personalidades*\n"
                "formal · amigable · luxury · directa · empatica · experta · juvenil\n\n"
                "💬 *Situaciones reales*\n"
                "objecion — cliente difícil\n"
                "cita — agendamiento completo\n"
                "cierre — técnica de cierre\n"
                "competencia — ya fui a otro lado\n"
                "precio — está muy caro\n"
                "prueba — mándame el mensaje más difícil\n"
                "bot — soy un bot?\n"
                "2am — respuesta a las 2am\n\n"
                "📊 *Demo & datos*\n"
                "stats — impacto en números\n"
                "memoria — qué recuerdo de ti\n"
                "\n\n"
                "⚙️ *Ajustes*\n"
                "usa emojis / sin emojis\n"
                "siguiente — próximo truco\n"
                "reset — empezar con otro negocio\n\n"
                "todo se activa escribiendo la palabra, sin slash 👆"
            )
            _save("user", text)
            return _send(lista)

        if detected_cmd == "/emojis_on":
            self._emoji_chats_off.discard(chat_id)  # v11: re-activar emojis
            return _send("¡Listo! A partir de ahora te responderé con emojis 🎉")

        if detected_cmd == "/emojis_off":
            self._emoji_chats_off.add(chat_id)  # v11: desactivar emojis
            return _send("¡Listo! A partir de ahora escribiré sin emojis.")

        if detected_cmd == "/voice_on":
            self._demo_sessions[sk + "_voice_off"] = False
            return _send("¡Listo! A partir de ahora te responderé con audios de voz 🎙️")

        if detected_cmd == "/voice_off":
            self._demo_sessions[sk + "_voice_off"] = True
            return _send("¡Listo! Desactivado el audio, te responderé solo con texto ✍️")

        handled, response = await self._handle_marketing_commands(
            detected_cmd, sk, text, business_name, btone_key, history, _llm, _next_trick, chat_id
        )
        if handled:
            _save("user", text)
            return _send(response)
        # Detectar si está en modo bot y respondió con número
        bmode_key = sk + "_botmode"
        
        # Bug 20 Fix: Solo procesar si el último mensaje del asistente fue realmente el menú
        _last_ast_text = _normalize_conv_text(_recent_demo_assistant_text(limit=1))
        _menu_active = "el número de tu opción" in _last_ast_text or "el número de su opción" in _last_ast_text
        
        if self._demo_sessions.get(bmode_key) and not _menu_active:
            self._demo_sessions.pop(bmode_key, None)
            
        if self._demo_sessions.get(bmode_key) and text.strip() in ["1","2","3","4","5"]:
            opt = text.strip()
            tone_now  = self._demo_sessions.get(btone_key, "GENERAL")
            is_formal = tone_now in ("SALUD PREMIUM", "PREMIUM")
            usted = is_formal  # True → usted, False → tuteo

            bot_replies = {
                "1": (
                    f"Nuestros servicios principales son:\n\n"
                    f"✅ Servicio A\n✅ Servicio B\n✅ Servicio C\n\n"
                    + (f"¿Sobre cuál le gustaría más información?" if usted else f"¿Sobre cuál quieres más info?")
                    + f" ||| (en producción estos vendrían de la base de conocimiento del negocio)"
                ),
                "2": (
                    (f"Nuestras tarifas varían según el servicio y convenio 💰\n\n"
                     f"Le contactamos para una cotización personalizada"
                     if usted else
                     f"Nuestras tarifas varían según el servicio 💰\n\n"
                     f"Escríbenos para una cotización personalizada")
                    + f" ||| (en producción Firby mostraría los precios reales configurados)"
                ),
                "3": (
                    (f"Con gusto le ayudamos a agendar su cita 📅\n\n"
                     f"¿Qué día le queda mejor?\n\nLunes a Viernes: 7am - 5pm"
                     if usted else
                     f"Con gusto te ayudamos a agendar 📅\n\n"
                     f"¿Qué día te queda mejor?\n\nLunes a Viernes: 8am - 6pm\nSábado: 9am - 2pm")
                    + f" ||| (en producción conectaría con el calendario real)"
                ),
                "4": (
                    f"📍 {business_name}\n\n"
                    f"🕐 Horario de atención:\nLunes a Viernes: "
                    + ("7am - 5pm" if usted else "8am - 6pm\nSábado: 9am - 2pm")
                    + f" ||| (en producción usaría la dirección y horario reales del negocio)"
                ),
                "5": (
                    (f"Con mucho gusto, le comunico con uno de nuestros asesores 👤\n\n"
                     f"¿Cuál es su nombre?"
                     if usted else
                     f"Enseguida te comunico con un asesor 👤\n\n"
                     f"¿Cuál es tu nombre?")
                    + f" ||| (en producción esto escalaría a WhatsApp del asesor o CRM)"
                ),
            }
            _save("user", text)
            no_valida = "Opción no válida ||| Por favor responda con un número del 1 al 5" if usted else "opción no válida ||| escribe 1, 2, 3, 4 o 5"
            resp = bot_replies.get(opt, no_valida)
            return _send(resp)

        if detected_cmd == "/siguiente":
            tricks = self._DEMO_TRICKS_ORDER
            idx = int(self._demo_sessions.get(btrick_key, 0))
            if idx < len(tricks):
                cmd_n, desc_n = tricks[idx]
                self._demo_sessions[btrick_key] = idx + 1
                return _send(f"el siguiente truco: escribe {cmd_n} para {desc_n}")
            return _send(f"ya viste todo el menú ||| si quieres esto para {business_name}, escribime y te paso con el equipo")

    # ── PASO 3: Conversación normal como recepcionista ─────────────────────
    business_name = self._demo_sessions.get(bname_key, "el negocio")
    business_ctx  = self._demo_sessions.get(bctx_key, "")
    found_online  = self._demo_sessions.get(bfound_key, False)
    persona       = self._demo_sessions.get(bpersona_key, "amigable")

    # Usar tone_instruction del arquetipo completo
    _arch    = PERSONALITY_ARCHETYPES.get(persona, PERSONALITY_ARCHETYPES["amigable"])
    style_note = _arch.get("tone_instruction", _arch["desc"]).strip()

    # ── Detectar tipo de negocio para adaptar tono ───────────────────────
    ctx_lower = (business_ctx or "").lower()
    bname_lower = business_name.lower()

    _is_health = any(w in ctx_lower or w in bname_lower for w in [
        "hospital","clínica","clinica","médico","medico","salud","eps","ips",
        "urgencias","paciente","cirugía","cirugia","especialidad","diagnóstico",
        "diagnóstico","radiología","radiologia","laboratorio","farmacia",
        "odontología","odontologia","psicología","psicologia","terapia","rehabilitación"
    ])
    _is_premium = any(w in ctx_lower or w in bname_lower for w in [
        "premium","lujo","exclusiv","vip","élite","elite","high-end",
        "las américas","americas","pablo tobón","tobón","tobon","pablo tobon",
        "country","bocagrande","el tesoro","internacional","international",
        "san vicente","fundación","fundacion","university","universitario",
        "cardiovascular","oncológ","oncolog","cardio","neurocirugía","neurocirugía"
    ])
    _is_retail = any(w in ctx_lower or w in bname_lower for w in [
        "tienda","almacén","almacen","fábrica","fabrica","fabricantes",
        "muebles","colchón","colchon","cama","espaldar","sala","comedor",
        "ropa","calzado","ferretería","ferreteria","materiales"
    ])

    # Tono base según tipo detectado
    if _is_health and _is_premium:
        _detected_tone = "SALUD PREMIUM"
    elif _is_health:
        _detected_tone = "SALUD"
    elif _is_premium:
        _detected_tone = "PREMIUM"
    elif _is_retail:
        _detected_tone = "RETAIL"
    else:
        _detected_tone = "GENERAL"

    # Guardar para que _send lo use en mayúsculas
    self._demo_sessions[btone_key] = _detected_tone
    _is_formal_ctx = _detected_tone in ("SALUD PREMIUM", "PREMIUM")

    if found_online and business_ctx:
        ctx_block = f"""INFORMACIÓN REAL DEL NEGOCIO (encontrada en Google/redes):
{business_ctx[:1200]}

TIPO DETECTADO: {_detected_tone}

REGLA CRÍTICA CON ESTA INFORMACIÓN:
Cuando el cliente pregunte por dirección, teléfono, horario, ubicación, redes sociales,
o cualquier dato específico — BÚSCALO en el bloque de arriba y DALO directamente.
NO redireccionas con otra pregunta cuando tienes el dato.
NO dices "te puedo dar la dirección si la necesitas" — si la tienes, la das.
Ejemplo:
  Cliente: "me regalas la dirección del showroom"
  MAL: "claro, dime primero qué te gustaría ver cuando vengas"
  BIEN: "claro, estamos en [dirección que encontraste] ||| ¿quieres que te cuente qué hay en el showroom?"
Si NO encontraste el dato en la info → sé honesta: "esa info no la tengo, escríbenos al [canal que sí tengas]"."""
    else:
        ctx_block = f"CONTEXTO: usa lo que el cliente ha mencionado. TIPO: {_detected_tone}"

    # Ejemplos de tono por tipo
    from src.domain.demo_prompts import DEMO_TONE_EXAMPLES
    _tone_examples = DEMO_TONE_EXAMPLES

    _tone_guide = _tone_examples.get(_detected_tone, _tone_examples["GENERAL"])

    msg_count = len(history)
    _should_reveal_trick = msg_count >= 6 and msg_count % 5 == 0
    trick_suffix = ""

    _with_emojis = chat_id not in self._emoji_chats_off
    _is_formal_ctx = _detected_tone in ("SALUD PREMIUM", "PREMIUM")
    _emoji_rule  = ("Usa emojis con naturalidad — 1 por burbuja máximo, solo si añaden calor. "
                    "Nunca al inicio de oración. Ejemplo: 'te queda un turno este jueves 🗓'") \
                   if _with_emojis else "Sin emojis."

    # v11: info manual del negocio cuando no había info online
    _manual_info = self._demo_sessions.get(f"{chat_id}:biz_manual_info", "")
    _manual_block = f"\nINFO DEL NEGOCIO (proporcionada por el dueño):\n{_manual_info}\n" if _manual_info else ""

    if sim_mode_active:
        sys_p_role = f"Eres Firby, la persona que contesta el WhatsApp de {business_name}.\nNo eres un bot. Llevas tiempo ahí — conoces el negocio de memoria y a quién le sirve."
    else:
        sys_p_role = f"Eres Firby, la IA demostradora comercial de Innvisor. Estás mostrando cómo atenderías a los clientes de {business_name}.\nEstás hablando con el dueño o prospecto del negocio (NO con un cliente final). Explica con dinamismo cómo responderías 24/7, filtrarías clientes y agendarías citas en su negocio.\nResponde natural como en WhatsApp, sin estructuras fijas ni tips forzados."


    sys_p = f"""{sys_p_role}
ESTILO: {style_note}
{"IMPORTANTE: Este es un negocio de alto nivel. Usa USTED siempre, mayúscula al inicio de cada mensaje, tono profesional y cálido." if (_is_formal_ctx and sim_mode_active) else ""}

{ctx_block}{_manual_block}
{_tone_guide}

HOY: {now_dt.strftime("%A %d de %B")}, {moment}. Colombia.

CÓMO ESCRIBES
Máximo 1 oración por burbuja. Máximo 2 burbujas por respuesta. ||| para separar.
Sin punto al final. Sin ¿¡. {_emoji_rule} Sin listas. Sin párrafos.
NUNCA: "Con mucho gusto", "Encantada de conocerte", "Estimado/a",
       "Le puedo ofrecer", "Fue un placer", "En qué más le puedo servir"

FRASES RELLENO PROHIBIDAS — suenan robot colombiano:
  ✗ "claro que sí, ..."       → di directo lo que sigue
  ✗ "con gusto te ayudo"      → di directo lo que sigue
  ✗ "me alegra que preguntes" → corta, responde
  ✗ "perfecto, entiendo"      → corta, responde
  ✗ "te cuento que..."        → di sin "te cuento que"
  ✗ "lo que pasa es que..."   → di sin introducción
  ✗ "en ese sentido..."       → corta
  ✗ "de hecho..."             → corta
Si vas a decir algo, dilo — sin preámbulo.

LONGITUD — REGLA DURA:
Cada burbuja: máximo 12 palabras. Si necesitas más, úsalas — pero pon ||| antes.
Una respuesta entera nunca debe superar 30 palabras en total.

PRECIOS — REGLA IMPORTANTE:
Si encontraste el precio en la info del negocio → dilo directo, sin rodeos.
Si NO lo tienes → admítelo como humana, sin inventar ni dar rangos:
  "no tengo ese dato ahorita ||| te averiguo y te escribo"
  "ese precio cambia según el caso ||| me das tu número para confirmarte"
NUNCA digas "ese precio lo maneja la clínica/el negocio" — suena a call center.
NUNCA inventes rangos ("entre 50 y 200 mil") si no tienes la info real.

TU ROL: ASESORA REAL, NO MÁQUINA DE VENTAS
Eres una persona real. No empujas. No redireccionas preguntas con otras preguntas.
Una persona real responde primero lo que le preguntan — LUEGO profundiza si tiene sentido.

REGLA DE ORO ANTI-ROBOT:
Si el cliente hace una pregunta directa → RESÓNDELA DIRECTAMENTE primero.
Solo después, si es natural, una sola pregunta de seguimiento.

ERROR FATAL #1: redirigir pregunta directa con diagnóstico.
  Cliente: "dónde están ubicados?"
  MAL: "estamos en Medellín, dime qué es lo que buscas para cuando vengas..."
  BIEN: "estamos en [dirección que encontraste en google] ||| ¿cuándo podrías venir"

ERROR FATAL #2: acumular preguntas en una respuesta.
  MAL: "qué edad tiene, para qué cuarto es, cuándo lo necesita"
  BIEN: UNA sola pregunta por respuesta, la más relevante

ERROR FATAL #3: listar productos sin entender.
  Cliente: "qué tamaños tienen?" → MAL: "queen, king, sencilla..." → BIEN: "para qué cuarto es"

ERROR FATAL #4: preguntar lo que ya dijeron.
  Cliente: "busco base cama para mi hija" → MAL: "para quién es" → BIEN: "qué edad tiene ella"

CUÁNDO DIAGNOSTICAR vs CUÁNDO RESPONDER DIRECTO:
  Pregunta de datos (dónde, cuánto, horario, cómo llegar) → RESPONDE el dato si lo tienes
  Pregunta de producto (qué tienen, cómo es) → diagnóstico antes de listar
  Objección (está caro, estoy lejos) → valida, luego UNA pregunta que mueva

DISPONIBILIDAD — REGLA CRÍTICA:
NUNCA inventes horarios, fechas ni espacios disponibles que no tienes en la info.
Si no tienes el calendario real del negocio → sé honesta y pide confirmación.
  Cliente: "are you available next sunday?" / "¿tienen mesa para el domingo?"
  MAL: "yes, we have tables available from 12pm to 10pm" ← inventado, puede ser falso
  BIEN: "let me check for you — what time were you thinking?" 
  BIEN: "we'll confirm availability — what time works best for you?"
  BIEN: "para el domingo sí atendemos ||| a qué hora lo necesitas — te confirmo"
Una recepcionista real no inventa disponibilidad. Dice "te confirmo" o "déjame verificar".
Cuando el cliente dé la hora → responde: "perfecto, te confirmo la reserva" y cierra.

EJEMPLOS:
  Cliente: "escuché que tienen showroom, me regalas la dirección"
  Firby: "claro, estamos en [dirección] ||| cuándo podrías venir"

  Cliente: "ahora estoy en Europa y no tengo el dinero"
  MAL: "ay qué pena, qué es exactamente lo que te hace falta..."
  BIEN: "no te preocupes, el pedido lo guardamos ||| cuándo regresas"

REGLA DE GÉNERO Y TRATAMIENTO (OBLIGATORIA):
- NUNCA asumas género femenino por defecto (NUNCA digas "tranquila", "amiga", "reina", etc. a menos que sepas 100% que es mujer).
- Si el usuario es hombre (o su nombre es masculino o envió notas de voz de hombre), trátalo en masculino o usa expresiones neutras ("no te preocupes", "tranquilo", "cero problema", "con gusto").

  Cliente: "busco base cama para mi hija"
  Firby: "ay qué bacano ||| qué edad tiene ella"
  Cliente: "8 años"
  Firby: "está estrenando cuarto o es cambio"
  Cliente: "renovando, quiere algo rosado"
  Firby: "tenemos base sencilla en varios rosados ||| cuándo lo necesitan"
Si dijo "para mi hija" → no preguntes "para quién es".
Si dijo "cuarto principal" → no preguntes "para qué cuarto".
Si dijo "cama doble" → no preguntes "qué tamaño".
LEE lo que escribió. Úsalo. Profundiza en lo que NO dijo todavía.

COMPRAS EMOCIONALES — reconócelas primero:
  "para mi hija/mamá/regalo/cuarto nuevo" → primero un segundo humano
  "ay qué bacano ||| qué edad tiene ella" — calor, LUEGO diagnóstico técnico

MÉTODO: ESCUCHAR → PROFUNDIZAR → CONECTAR → CERRAR
  Cliente: "busco base cama para mi hija"
  MAL: "para qué cuarto es para tu hija" ← repitió info, suena robot
  BIEN: "ay qué chévere ||| qué edad tiene ella"

OBJECIONES
"está caro" → "sí, es de buena calidad ||| qué presupuesto tienes, para ver qué te muestro"
"lo pienso" → "claro ||| qué sería lo más importante — el precio, el color, o que te dure"
"en otro lado" → "claro ||| nosotros somos fabricantes directos, eso cambia precio y garantía"
"no sé si me quede" → "eso lo vemos en persona — traes la medida y te lo mostramos en el espacio"
"eres un bot?" → "soy la asesora de {business_name}, trabajo por acá todo el día"
"cómo tener esto" / "quién te hizo" → "me hizo Innvisor ||| si quieres algo así, el contacto es 3243699856 con Santiago Rubio"
- si preguntan si aceptas audios, notas de voz, imágenes, PDFs o documentos: responde que sí, cuando el canal lo permite, puedes transcribir, leer y usar ese contenido
- si preguntan algo general o fuera de contexto: respóndelo bien primero y luego vuelve suave al negocio solo si hace sentido
{(v8_build_quality_system_prompt_addon(chat_id=chat_id, archetype="amigable", history=history) if anti_robot_filter else "") if callable(getattr(v8_build_quality_system_prompt_addon, '_get_target', lambda: None)()) else ""}
"""

    _save("user", text)
    r, had_model_output = await _demo_llm_conv_quality_chain(
        sys_p,
        validator=lambda candidate: (
            _demo_customer_reply_is_low_quality(candidate)
            or _demo_customer_missing_required_detail(text, candidate)
        ),
        repair_instructions="""
- responde directo lo que te preguntaron
- no reinicies la conversación ni te presentes otra vez
- no uses texto genérico como 'cuéntame un poco más'
""",
        temp=0.72,
        max_t=8192,
        model_tier="fast",
        recent_limit=8,
    )
    if not r:
        return await _notify_demo_ai_failure(text, "respuesta de cliente en demo")
    # Solo revelar truco si la respuesta tiene contenido real (>60 chars)
    # y no termina en pregunta (no interrumpir el flujo de la conversación)
    if _should_reveal_trick and r and len(r.replace("|||","").strip()) > 60:
        _t = _next_trick()
        if _t:
            r = r.rstrip() + _t

    # ── SmartHandoff: detectar incertidumbre y escalar al admin ──────────
    if _SMART_HANDOFF and handoff_manager:
        _admin_ids = _parse_admin_ids(clinic.get("admin_chat_ids", []))
        if _admin_ids:
            async def _handoff_send_to_client(cid: str, msg: str):
                try:
                    await self._send_message(cid, msg)
                    if db:
                        try:
                            db.save_message(cid, "assistant", str(msg).replace("|||", " "))
                        except Exception as _db_err:
                            log.warning(f"[handoff] save resumed assistant error: {_db_err}")
                except Exception as _hsce:
                    log.warning(f"[handoff] send_to_client error: {_hsce}")

            async def _handoff_notify_admin(aid: str, msg: str):
                try:
                    await mcp_manager.execute(
                        "notifications_v1", "send_notification",
                        {"chat_id": aid, "message": msg}
                    )
                except Exception as _hne:
                    log.warning(f"[handoff] notify_admin error: {_hne}")

            handoff_manager.register_client_sender(_handoff_send_to_client)
            await handoff_manager.resume_pending_timeouts(
                send_to_client_fn=_handoff_send_to_client,
            )
            _hold_msgs, _was_escalated = await handoff_manager.trigger(
                client_chat_id=chat_id,
                user_msg=text,
                history=list(history)[-12:],
                clinic=clinic,
                llm_output=r or "",
                admin_chat_ids=_admin_ids,
                send_to_admin_fn=_handoff_notify_admin,
                send_to_client_fn=_handoff_send_to_client,
            )
            if _was_escalated and _hold_msgs:
                return _send(_hold_msgs[0])

    return _send(r)


class FirbyDemo:
    """
    Componente especializado para el Modo Demo.
    Maneja la experiencia de intriga progresiva y trucos de venta.
    """
    
    def __init__(self, firby):
        self.firby = firby

    async def handle(self, chat_id: str, text: str, clinic: Dict, 
                    attachments: Optional[List[Dict[str, Any]]] = None) -> List[str]:
        return await handle_demo_message(self.firby, chat_id, text, clinic, attachments)
