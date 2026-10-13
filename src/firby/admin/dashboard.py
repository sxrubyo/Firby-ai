# -*- coding: utf-8 -*-
"""Admin commands mixin extracted from FirbyUltra."""
from __future__ import annotations
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import logging
import json
import re
import asyncio
log = logging.getLogger("firby.admin")

# Proxy declarations mapping to globals for easy porting
from src.firby.core.proxy import GlobalProxy

Config = GlobalProxy('Config')
db = GlobalProxy('db')
llm_engine = GlobalProxy('llm_engine')
calendar_bridge = GlobalProxy('calendar_bridge')
payment_bridge = GlobalProxy('payment_bridge')
smart_variety = GlobalProxy('smart_variety')
mcp = GlobalProxy('mcp')
_send_message_async = GlobalProxy('_send_message_async')
_notify_admin_async = GlobalProxy('_notify_admin_async')
HyperHumanEngine = GlobalProxy('HyperHumanEngine')
MemoryItem = GlobalProxy('MemoryItem')
_detect_wa_credentials = GlobalProxy('_detect_wa_credentials')
_extract_phone = GlobalProxy('_extract_phone')
_NOVA_AVAILABLE = GlobalProxy('_NOVA_AVAILABLE')
owner_style_controller = GlobalProxy('owner_style_controller')
prompt_evolver = GlobalProxy('prompt_evolver')
trainer_gateway = GlobalProxy('trainer_gateway')
kb = GlobalProxy('kb')
_extract_conversation_selection = GlobalProxy('_extract_conversation_selection')
_wants_all_messages = GlobalProxy('_wants_all_messages')

from src.firby.utils.helpers import is_affirmative

class AdminCommandsMixin:
    """Mixin class providing all _admin_ prefixed methods for FirbyUltra."""

    async def _admin_ingest_assets(
        self,
        chat_id: str,
        text: str,
        attachments: List[Dict[str, Any]],
        clinic: Dict[str, Any],
    ) -> Optional[List[str]]:
        if not attachments:
            return None

        store = self._brand_store(clinic)
        if not store:
            return ["No pude abrir el vault de marca en esta instalación."]

        saved_items: List[Dict[str, Any]] = []
        extracted_blocks: List[str] = []

        for item in attachments:
            kind = item.get("kind", "asset")
            platform = item.get("platform", Config.PLATFORM)
            caption = (item.get("caption") or "").strip()
            filename = item.get("filename") or ("logo.png" if kind == "image" else "document.bin")
            mime_type = item.get("mime_type", "")
            raw_bytes = item.get("bytes")

            try:
                if platform == "telegram" and item.get("file_id"):
                    raw_bytes, downloaded_name = await self._download_telegram_binary(item["file_id"])
                    if not item.get("filename"):
                        filename = downloaded_name
                elif platform == "whatsapp_cloud" and item.get("media_id"):
                    raw_bytes, downloaded_name, downloaded_mime = await self._download_whatsapp_cloud_binary(item["media_id"])
                    if not item.get("filename"):
                        filename = downloaded_name
                    if not mime_type:
                        mime_type = downloaded_mime
                elif item.get("base64"):
                    import base64 as _b64
                    raw_bytes = _b64.b64decode(item["base64"])
                elif isinstance(raw_bytes, str):
                    raw_bytes = raw_bytes.encode("utf-8")
            except Exception as e:
                log.warning(f"[brand] fallo descargando adjunto {filename}: {e}")
                continue

            if not raw_bytes:
                continue

            lower_name = f"{filename} {caption}".lower()
            if any(tag in lower_name for tag in ["logo", "isotipo", "brand", "identidad", "manual", "paleta", "colores"]):
                category = "brand"
            elif kind == "image":
                category = "visual"
            else:
                category = "knowledge"

            saved = store.save_binary_asset(
                filename=filename,
                data=raw_bytes,
                mime_type=mime_type,
                source=f"{platform}_attachment",
                category=category,
                caption=caption,
            )
            if saved.manifest_entry:
                saved_items.append(saved.manifest_entry)
            if saved.extracted_text and len(saved.extracted_text.strip()) > 20:
                extracted_blocks.append(saved.extracted_text.strip())
            if category == "brand" and any(tag in lower_name for tag in ["logo", "isotipo"]):
                db.remember("brand_logo_asset", saved.saved_path, "identity")

        extra_note = (text or "").strip()
        if extra_note:
            note_saved = store.save_text_note(
                "admin_brand_note",
                extra_note,
                source="admin_chat",
                category="knowledge",
            )
            if note_saved.manifest_entry:
                saved_items.append(note_saved.manifest_entry)
            if len(extra_note) > 40:
                extracted_blocks.append(extra_note)

        if not saved_items and not extracted_blocks:
            return ["Recibí el adjunto, pero no pude guardarlo bien. Intenta de nuevo."]

        if kb and extracted_blocks:
            try:
                kb.append("\n\n".join(block for block in extracted_blocks if block.strip()))
            except Exception as e:
                log.warning(f"[brand] no pude anexar al KB: {e}")

        manifest = store.manifest()
        db.remember("brand_assets_path", str(store.root), "identity")
        db.remember("brand_assets_count", str(len(manifest.get("assets", []))), "identity")
        db.remember("brand_identity_summary", store.latest_identity_summary(), "identity")
        db.remember("brand_last_upload_at", datetime.now().isoformat(), "identity")

        latest = saved_items[-4:]
        latest_lines = "\n".join(
            f"• {item.get('filename', 'asset')} [{item.get('category', 'asset')}]"
            for item in latest
        )
        return [
            "Listo. Ya guardé esos activos en el vault permanente de la marca.",
            f"Ruta: {store.root}\nArchivos recientes:\n{latest_lines}",
            "Desde ahora los conservo por instancia y los uso como contexto oficial. Si el adjunto tenía texto, ya quedó anexado al conocimiento activo.",
        ]

    async def _admin_brand_status(self, clinic: Dict[str, Any]) -> List[str]:
        store = self._brand_store(clinic)
        if not store:
            return ["El vault de marca no está disponible en esta instalación."]
        summary = "\n".join(store.summary_lines())
        return [
            "Vault de marca activo.",
            summary,
            "Puedes mandarme logos, manuales, identidad de marca, PDFs, DOCX, TXT, MD o JSON. Lo guardo por instancia y no lo olvido.",
        ]


    async def _admin_show_appointments(self) -> List[str]:
        """Muestra citas."""
        appointments = db.get_appointments(status="pendiente", limit=15)
        
        if not appointments:
            return ["Sin citas pendientes."]
        
        lines = ["*Citas pendientes:*\n"]
        for apt in appointments:
            lines.append(
                f"• *{apt['patient_name']}* | {apt['service']} | "
                f"{apt['datetime_slot']} | {apt['status']}"
            )
        
        return ["\n".join(lines)]
    
    async def _admin_show_config(self, clinic: Dict) -> List[str]:
        """Muestra configuracion actual con hints de como editar."""
        services = clinic.get("services", [])
        schedule = clinic.get("schedule", {})
        pricing  = clinic.get("pricing", {})
        if isinstance(pricing, str):
            try:
                pricing = json.loads(pricing) if pricing else {}
            except Exception:
                pricing = {}

        persona = clinic.get("persona_config", {})
        if isinstance(persona, str):
            try:
                persona = json.loads(persona) if persona else {}
            except Exception:
                persona = {}

        agent_name = clinic.get("assistant_name") or persona.get("name") or "Firby"
        if agent_name.lower() in ("lucia", "lucía"):
            agent_name = "Firby"
        formality  = int(persona.get("formality_level", 0.6) * 100)
        warmth     = int(persona.get("warmth_level", 0.7) * 100)

        svcs_str  = "\n  ".join(services) if services else "ninguno (di 'cambia los servicios')"
        sched_str = "; ".join(f"{k}: {v}" for k, v in schedule.items()) if schedule else "no configurado"

        price_block = ""
        if pricing:
            price_lines = "\n  ".join(f"{k}: {v}" for k, v in pricing.items())
            price_block = f"Precios:\n  {price_lines}\n"
        else:
            price_block = "Precios: no configurados\n"

        kb_line = ""
        if kb and _KB_AVAILABLE and kb.has_content():
            stats = kb.get_stats()
            kb_line = f"KB: {stats['chunks']} secciones · {stats['words']} palabras\n"
        else:
            kb_line = "KB: sin documento cargado\n"

        brand_line = ""
        try:
            store = self._brand_store(clinic)
            if store:
                manifest = store.manifest()
                brand_line = f"Brand Vault: {len(manifest.get('assets', []))} activos · {store.root}\n"
        except Exception:
            brand_line = ""

        return [
            f"CLINICA:\n"
            f"  Nombre: {clinic.get('name', '-')}\n"
            f"  Slogan: {clinic.get('tagline', '-') or '-'}\n"
            f"  Direccion: {clinic.get('address', '-') or '-'}\n"
            f"  Telefono: {clinic.get('phone', '-') or '-'}\n"
            f"  Horario: {sched_str}\n\n"
            f"SERVICIOS:\n  {svcs_str}\n\n"
            f"{price_block}\n"
            f"ASISTENTE:\n"
            f"  Nombre: {agent_name}\n"
            f"  Calidez: {warmth}% · Formalidad: {formality}%\n\n"
            f"{kb_line}"
            f"{brand_line}",
            "Para editar, dime:\n"
            "• 'cambia los servicios'\n"
            "• 'el telefono es 3001234567'\n"
            "• 'la direccion es Calle 10 #43'\n"
            "• 'el botox cuesta 350.000'\n"
            "• 'mas calidez' / 'llamate Sofia'\n"
            "• Enviar documento completo -> carga el KB\n"
            "• Enviar logo/manual/identidad -> queda en el Brand Vault"
        ]
    
    async def _admin_show_metrics(self) -> List[str]:
        """Muestra métricas."""
        analysis = await self.self_improvement.analyze_performance()
        
        return [
            f"*Métricas (últimas 24h):*\n\n"
            f"Conversaciones: {analysis.get('total_conversations', 0)}\n"
            f"Tiempo respuesta: {analysis.get('avg_response_time_ms', 0):.0f}ms\n"
            f"Turnos promedio: {analysis.get('avg_turns_per_conversation', 0):.1f}\n"
            f"Tasa conversión: {analysis.get('conversion_rate', 0)*100:.1f}%\n"
            f"Escalaciones: {analysis.get('escalation_rate', 0)*100:.1f}%"
        ]
    
    async def _admin_show_plugins(self) -> List[str]:
        """Muestra plugins."""
        plugins = db.get_plugins()
        
        if not plugins:
            return ["Sin plugins instalados."]
        
        lines = ["*Plugins instalados:*\n"]
        for p in plugins:
            status = "✓" if p.enabled else "✗"
            lines.append(f"{status} *{p.name}* v{p.version}")
            lines.append(f"   Capacidades: {', '.join(p.capabilities)}")
        
        return ["\n".join(lines)]
    
    async def _admin_show_personality(self, clinic: Dict) -> List[str]:
        """Muestra la personalidad actual con arquetipos disponibles."""
        persona = clinic.get("persona_config", {})
        if isinstance(persona, str):
            try:
                persona = json.loads(persona) if persona else {}
            except Exception:
                persona = {}

        name        = persona.get("name", "Firby")
        archetype   = persona.get("archetype", "amigable")
        arch_info   = PERSONALITY_ARCHETYPES.get(archetype, PERSONALITY_ARCHETYPES["amigable"])

        arch_list = "\n".join(
            f"  {k} — {v['desc']}"
            for k, v in PERSONALITY_ARCHETYPES.items()
        )

        return [
            f"personalidad activa: {archetype}\n{arch_info['desc']}",
            f"arquetipos disponibles:\n{arch_list}",
            "para cambiar escribe por ejemplo:\n"
            "  'activa empatica'\n"
            "  'cambia a luxury y llamate Sofia'\n"
            "  'modo experta'\n"
            "  'mas calidez' / 'menos formal'\n"
            "  'agrega palabra prohibida: oferta'"
        ]
    
    async def _admin_show_admins(self) -> List[str]:
        """Muestra el equipo de admins de esta instancia."""
        admins = db.list_admins()
        if not admins:
            return ["No hay administradores registrados."]

        lines = ["Equipo de administradores:\n"]
        for a in admins:
            role_label = "Owner" if a["role"] == "owner" else "Admin"
            name  = a.get("name", "Sin nombre")
            email = a.get("email", "")
            lines.append(f"  {role_label}: {name} ({email})")

        lines.append("\nPara agregar un nuevo admin: /addadmin")
        return ["\n".join(lines)]

    # ─── Conversaciones y Feedback ──────────────────────────────────────────────

    async def _admin_show_chats(self) -> List[str]:
        """
        /chats — muestra los últimos pacientes con quienes ha hablado Firby.
        El admin puede elegir uno para ver la conversación completa.
        """
        chats = db.get_recent_patient_chats(limit=10)
        if not chats:
            return ["Firby no ha tenido conversaciones con pacientes todavía."]

        lines = ["Últimas conversaciones:\n"]
        for i, c in enumerate(chats, 1):
            name = c.get("name") or "Desconocido"
            last_msg = (c.get("last_user_msg") or "")[:50]
            count = c.get("message_count", 0)
            last_ts = (c.get("last_message") or "")[:16]
            cid = c["chat_id"]
            lines.append(
                f"{i}. {name} ({cid})\n"
                f"   {count} mensajes · {last_ts}\n"
                f"   Último: \"{last_msg}\""
            )

        lines.append(
            "\nPara ver una conversación completa:\n"
            "/chat [id del paciente]\n"
            "Ej: /chat 1234567890\n\n"
            "Para dar feedback sobre una conversación:\n"
            "Escríbeme después de ver la conversación."
        )
        return ["\n".join(lines)]

    async def _admin_show_recent_conversation_browser(self, admin_chat_id: str, limit: int = 6) -> List[str]:
        """
        Vista resumida para admins no técnicos.
        Muestra las últimas conversaciones y deja contexto para abrir una por número.
        """
        raw_chats = db.get_recent_patient_chats(limit=max(limit * 5, 20))
        chats = [
            chat for chat in raw_chats
            if not self._is_synthetic_chat_id(str(chat.get("chat_id") or "").strip())
        ][:limit]
        if not chats:
            return ["Firby no ha tenido conversaciones con pacientes todavía."]

        self._admin_pending[admin_chat_id] = {
            "action": "conversation_browser",
            "items": chats,
            "selected_chat_id": None,
        }

        lines = [f"Últimas {len(chats)} conversaciones:\n"]
        for idx, chat in enumerate(chats, 1):
            name = (chat.get("name") or "Sin nombre").strip()
            chat_id = str(chat.get("chat_id") or "").strip()
            count = int(chat.get("message_count") or 0)
            last_msg = (chat.get("last_user_msg") or "").strip()
            if len(last_msg) > 60:
                last_msg = last_msg[:57].rstrip() + "..."
            last_ts = str(chat.get("last_message") or "").replace("T", " ")[:16]
            lines.append(
                f"{idx}. {name} ({chat_id})\n"
                f"   {count} mensajes · {last_ts}\n"
                f"   Último: {last_msg or 'sin texto'}"
            )

        lines.extend(
            [
                "",
                "Dime por ejemplo:",
                "  ver 1",
                "  muéstrame la primera",
                "  quiero ver todos los mensajes del primero",
            ]
        )
        return ["\n".join(lines)]

    async def _admin_show_patient_chat_preview(
        self,
        patient_chat_id: str,
        *,
        admin_chat_id: str = "",
        limit: int = 10,
        show_all: bool = False,
        label_override: str = "",
    ) -> List[str]:
        """
        Muestra un preview corto por defecto y la conversación completa si el admin lo pide.
        """
        fetch_limit = 500 if show_all else limit
        msgs = db.get_patient_conversation(patient_chat_id, limit=fetch_limit)
        if not msgs:
            return [f"No encontré conversación para el ID: {patient_chat_id}"]

        patient_name = ""
        try:
            conn_factory = getattr(db, "_conn", None)
            if callable(conn_factory):
                with conn_factory() as c:
                    row = c.execute(
                        "SELECT name FROM patients WHERE chat_id=?",
                        (patient_chat_id,),
                    ).fetchone()
                    if row:
                        patient_name = (row["name"] or "").strip()
        except Exception:
            patient_name = ""

        if admin_chat_id:
            pending = dict(self._admin_pending.get(admin_chat_id, {}))
            pending["action"] = "conversation_browser"
            pending["selected_chat_id"] = patient_chat_id
            self._admin_pending[admin_chat_id] = pending

        self._last_reviewed_chat = patient_chat_id

        label = patient_name or (label_override or "").strip() or patient_chat_id
        visible = msgs if show_all else msgs[-limit:]
        header = (
            f"Conversación completa con {label}"
            if show_all
            else f"Últimos {len(visible)} mensajes con {label}"
        )

        lines = [header, "─" * 40]
        for msg in visible:
            role_label = "Paciente" if msg.get("role") == "user" else "Firby"
            ts = str(msg.get("ts") or "").replace("T", " ")[:16]
            content = str(msg.get("content") or "").strip()
            lines.append(f"[{ts}] {role_label}: {content}")

        lines.extend(
            [
                "",
                "Si quieres más, dime:",
                "  ver todo",
                "  enséñame todos los mensajes",
            ]
        )
        return ["\n".join(lines)]

    async def _admin_show_patient_chat(self, patient_chat_id: str) -> List[str]:
        """
        /chat [id] — muestra la conversación completa de un paciente.
        Después de verla, el admin puede dar feedback naturalmente.
        """
        msgs = db.get_patient_conversation(patient_chat_id, limit=40)
        if not msgs:
            return [f"No encontré conversación para el ID: {patient_chat_id}"]

        # Guardar contexto activo para feedback
        self._admin_pending[patient_chat_id + "_review"] = {
            "action": "reviewing_chat",
            "patient_chat_id": patient_chat_id,
        }
        # Guardar en el pending del admin también para detectar feedback
        # (keyed by admin chat_id, set later when feedback is detected)

        patient = None
        try:
            with db._conn() as c:
                row = c.execute("SELECT name FROM patients WHERE chat_id=?",
                                (patient_chat_id,)).fetchone()
                if row:
                    patient = row["name"]
        except Exception:
            pass

        name_str = f"con {patient}" if patient else f"ID: {patient_chat_id}"
        header = f"Conversación {name_str}:\n{'─'*40}"

        lines = [header]
        for m in msgs:
            role_label = "Paciente" if m["role"] == "user" else "Firby"
            ts = (m.get("ts") or "")[:16]
            content = m["content"][:200]
            lines.append(f"\n[{ts}] {role_label}:\n{content}")

        lines.append(
            f"\n{'─'*40}\n"
            "Opciones:\n\n"
            "PUENTE — enviar mensaje directo a este cliente:\n"
            "  envíale: tu mensaje aquí\n"
            "  mándale: confirmada la cita para el martes\n"
            "  dile: ya tenemos disponibilidad esta semana\n\n"
            "FEEDBACK — enseñarme a mejorar:\n"
            "  \"Cuando dijo que era caro, debió ofrecer el plan de pagos\"\n"
            "  \"Muy bien manejada la objeción del precio\"\n\n"
            "El puente lo envío como si fuera yo — el cliente no nota diferencia."
        )

        # Store which chat the admin was just reviewing
        # (we'll use the admin's own chat_id as key — set when we know it)
        self._last_reviewed_chat = patient_chat_id

        return ["\n".join(lines)]

    async def _admin_show_trust_rules(self) -> List[str]:
        """
        /reglas — muestra lo que Firby ha aprendido del feedback del admin.
        """
        rules = db.get_trust_rules()
        if not rules:
            return [
                "Todavía no has dado feedback.",
                "Cuando veas una conversación con /chats y me digas cómo mejorarla, lo aprendo y lo guardo acá."
            ]

        # Agrupar por categoría
        by_cat: Dict[str, list] = {}
        for r in rules:
            cat = r.get("category", "general")
            by_cat.setdefault(cat, []).append(r)

        cat_labels = {
            "objection":    "Manejo de objeciones",
            "tone":         "Tono y forma de hablar",
            "closing":      "Cierre y agendamiento",
            "product":      "Información de tratamientos",
            "flow":         "Flujo de conversación",
            "general":      "General",
        }

        lines = ["Lo que he aprendido de ti:\n"]
        for cat, cat_rules in by_cat.items():
            label = cat_labels.get(cat, cat.title())
            lines.append(f"\n{label}:")
            for r in cat_rules:
                lines.append(f"  #{r['id']} {r['rule']}")
                if r.get("example_good"):
                    lines.append(f"     Ej: \"{r['example_good']}\"")

        lines.append(
            "\n\nPara eliminar una regla:\n"
            "/borrar regla [número]\n"
            "Ej: /borrar regla 3"
        )
        return ["\n".join(lines)]

    async def _admin_pipeline(self) -> List[str]:
        """
        /pipeline — Muestra todos los leads clasificados por temperatura.
        Usa closing_score almacenado en la última conversación.
        """
        try:
            with db._conn() as c:
                patients = c.execute("""
                    SELECT p.chat_id, p.name, p.visits,
                           (SELECT content FROM conversations
                            WHERE chat_id=p.chat_id AND role='user'
                            ORDER BY created_at DESC LIMIT 1) as last_msg,
                           (SELECT created_at FROM conversations
                            WHERE chat_id=p.chat_id
                            ORDER BY created_at DESC LIMIT 1) as last_seen
                    FROM patients p
                    ORDER BY p.visits DESC LIMIT 50
                """).fetchall()

            boiling, hot, warm, cold = [], [], [], []

            for pt in patients:
                chat_id  = pt["chat_id"]
                name     = pt["name"] or "Desconocido"
                last_msg = (pt["last_msg"] or "")[:60]
                last_seen = (pt["last_seen"] or "")[:16]

                # Calcular closing_score del último mensaje
                if last_msg:
                    analysis = MessageAnalyzer().analyze(last_msg)
                    temp = analysis.lead_temperature
                    score = analysis.closing_score
                else:
                    temp, score = "cold", 0.0

                entry = f"{name} — {last_msg!r:.60} ({last_seen[:10]})"
                if   temp == "boiling": boiling.append(entry)
                elif temp == "hot":     hot.append(entry)
                elif temp == "warm":    warm.append(entry)
                else:                   cold.append(entry)

            lines = ["Pipeline de leads\n"]
            if boiling:
                lines.append(f"Listos para cerrar ({len(boiling)}):")
                lines += [f"  {e}" for e in boiling[:5]]
            if hot:
                lines.append(f"\nCalientes ({len(hot)}):")
                lines += [f"  {e}" for e in hot[:5]]
            if warm:
                lines.append(f"\nTibios ({len(warm)}):")
                lines += [f"  {e}" for e in warm[:5]]
            if cold:
                lines.append(f"\nFríos ({len(cold)}): {len(cold)} contactos")

            if not (boiling or hot or warm or cold):
                return ["No hay conversaciones registradas todavía"]

            return ["\n".join(lines)]

        except Exception as e:
            log.error(f"[pipeline] {e}")
            return [f"Error generando pipeline: {e}"]

    async def _admin_lost_analysis(self) -> List[str]:
        """
        /perdidos — Analiza por qué se pierden los clientes.
        Identifica el patrón exacto donde se cortan las conversaciones.
        """
        try:
            with db._conn() as c:
                # Conversaciones que terminaron sin cita
                convs = c.execute("""
                    SELECT chat_id,
                           GROUP_CONCAT(content || '|||' || role, '~~~') as thread
                    FROM conversations
                    WHERE created_at >= datetime('now', '-30 days')
                    GROUP BY chat_id
                    HAVING COUNT(*) >= 2
                """).fetchall()

            if not convs:
                return ["No hay suficientes conversaciones para analizar todavía"]

            # Analizar con LLM los patrones de pérdida
            sample = []
            for c in convs[:15]:
                msgs = [m.split("|||") for m in c["thread"].split("~~~") if "|||" in m]
                if len(msgs) >= 2:
                    last_user = next((m[0] for m in reversed(msgs) if len(m) > 1 and m[1] == "user"), "")
                    if last_user:
                        sample.append(last_user[:80])

            if not sample:
                return ["No hay suficientes conversaciones para analizar"]

            prompt = f"""Analiza estos últimos mensajes de clientes que dejaron de responder:

{chr(10).join(f"- {s}" for s in sample[:10])}

Identifica:
1. El patrón más común donde se pierden (qué dijeron justo antes de irse)
2. El porcentaje aproximado de cada patrón
3. Qué debería haber respondido Firby diferente

Responde en máximo 5 líneas, directo, sin introducciones."""

            try:
                r, _ = await asyncio.wait_for(
                    llm_engine.complete(
                        [{"role": "user", "content": prompt}],
                        model_tier="fast", temperature=0.3, max_tokens=300
                    ), timeout=15.0
                )
            except Exception:
                r = "No pude analizar los patrones en este momento"

            return [
                f"Análisis de los últimos 30 días ({len(convs)} conversaciones):",
                r
            ]

        except Exception as e:
            return [f"Error: {e}"]

    async def _admin_sales_coach(self) -> List[str]:
        """
        /coach — Analiza las últimas conversaciones y da feedback de ventas.
        Funciona como entrenador: qué funcionó, qué no, qué mejorar.
        """
        try:
            with db._conn() as c:
                recent = c.execute("""
                    SELECT chat_id,
                           COUNT(*) as turns,
                           MAX(created_at) as last_ts
                    FROM conversations
                    WHERE created_at >= datetime('now', '-7 days')
                    GROUP BY chat_id
                    HAVING turns >= 4
                    ORDER BY last_ts DESC LIMIT 5
                """).fetchall()

            if not recent:
                return ["No hay conversaciones largas esta semana para analizar"]

            # Tomar la conversación más reciente y sustancial
            best = recent[0]
            msgs = db.get_patient_conversation(best["chat_id"], limit=20)
            thread = "\n".join(f"{m['role'].upper()}: {m['content'][:120]}" for m in msgs)

            prompt = f"""Eres un coach de ventas experto en WhatsApp para negocios en Colombia.
Analiza esta conversación de Firby con un cliente:

{thread[:2000]}

Dame:
1. Una cosa que Firby hizo MUY bien (con el mensaje exacto que lo demuestra)
2. Una cosa que pudo hacer mejor (con cómo debió responder)
3. Una técnica de venta que debería usar más en este tipo de conversación

Máximo 6 líneas. Directo. Sin introducciones."""

            try:
                r, _ = await asyncio.wait_for(
                    llm_engine.complete(
                        [{"role": "user", "content": prompt}],
                        model_tier="fast", temperature=0.4, max_tokens=350
                    ), timeout=15.0
                )
            except Exception:
                r = "No pude analizar la conversación en este momento"

            return ["Coach de ventas — última semana:", r]

        except Exception as e:
            return [f"Error: {e}"]

    async def _admin_clone_style(self, admin_chat_id: str) -> List[str]:
        """
        /estilo — Lee los mensajes del admin y clona su forma de escribir.
        Guarda el estilo como trust_rule de máxima prioridad.
        """
        try:
            msgs = db.get_history(admin_chat_id, limit=50)
            admin_msgs = [m["content"] for m in msgs if m["role"] == "user" and len(m["content"]) > 10]

            if len(admin_msgs) < 5:
                return [
                    "Necesito más mensajes tuyos para clonar tu estilo",
                    "Escríbeme unos 10 mensajes como si hablaras con un cliente y vuelve a intentar"
                ]

            sample = "\n".join(f"- {m[:80]}" for m in admin_msgs[:15])

            prompt = f"""Analiza estos mensajes de un empresario colombiano:

{sample}

Extrae su estilo de escritura: tono, vocabulario, longitud de mensajes, 
muletillas propias, cómo saluda, cómo cierra, qué palabras usa siempre.
Luego escribe UNA instrucción concisa (máximo 4 líneas) para que Firby 
escriba EXACTAMENTE como él. Primera persona, directo."""

            try:
                r, _ = await asyncio.wait_for(
                    llm_engine.complete(
                        [{"role": "user", "content": prompt}],
                        model_tier="fast", temperature=0.3, max_tokens=200
                    ), timeout=15.0
                )
                rule = r.strip()
            except Exception:
                return ["No pude analizar tu estilo en este momento, intenta de nuevo"]

            # Guardar como trust_rule de máxima prioridad
            rule_id = db.save_trust_rule(
                category="tone",
                rule=f"ESTILO CLONADO DEL DUEÑO: {rule}",
                example_bad="",
                example_good=""
            )
            # Subir el peso al máximo
            with db._conn() as c:
                c.execute("UPDATE trust_folder SET weight=3.0 WHERE id=?", (rule_id,))

            return [
                "Analicé tus mensajes y cloné tu estilo",
                f"Regla guardada como #tone con prioridad máxima:",
                rule,
                "Desde ahora Firby escribe como tú. Usa /reglas para verla o editarla"
            ]

        except Exception as e:
            return [f"Error: {e}"]

    async def _admin_reactivate_dormant(self) -> List[str]:
        """
        /reactivar — Encuentra clientes inactivos 60+ días y los reactiva.
        Programa follow-ups automáticos para cada uno.
        """
        try:
            with db._conn() as c:
                dormant = c.execute("""
                    SELECT p.chat_id, p.name,
                           MAX(c.created_at) as last_contact,
                           (SELECT content FROM conversations
                            WHERE chat_id=p.chat_id AND role='user'
                            ORDER BY created_at DESC LIMIT 1) as last_msg
                    FROM patients p
                    JOIN conversations c ON c.chat_id = p.chat_id
                    GROUP BY p.chat_id
                    HAVING last_contact < datetime('now', '-60 days')
                    ORDER BY last_contact DESC LIMIT 20
                """).fetchall()

            if not dormant:
                return ["No hay clientes inactivos por más de 60 días"]

            scheduled = 0
            for i, pt in enumerate(dormant[:10]):
                # Programar con delay escalonado para no spam
                run_at = datetime.now() + timedelta(hours=i * 2 + 1)
                task_manager.schedule_task(
                    task_type="follow_up",
                    data={
                        "chat_id":      pt["chat_id"],
                        "reason":       "reactivation",
                        "last_message": (pt["last_msg"] or "")[:200],
                        "patient_name": pt["name"] or "",
                    },
                    scheduled_for=run_at,
                    priority=4
                )
                scheduled += 1

            names = ", ".join(pt["name"] or pt["chat_id"][:8] for pt in dormant[:5])
            return [
                f"Encontré {len(dormant)} clientes inactivos",
                f"Programé reactivación para {scheduled} — comenzando en 1 hora",
                f"Primeros: {names}{'...' if len(dormant) > 5 else ''}",
                "Escríbeme /pipeline en 24h para ver cómo respondieron"
            ]

        except Exception as e:
            return [f"Error: {e}"]

    async def _admin_configure_followup(self, clinic: Dict) -> List[str]:
        """
        /seguimiento — Configura los follow-ups automáticos.
        Muestra estado actual y permite activar/desactivar.
        """
        try:
            with db._conn() as c:
                pending = c.execute(
                    "SELECT COUNT(*) FROM tasks WHERE type='follow_up' AND status='pending'"
                ).fetchone()[0]
                completed = c.execute(
                    "SELECT COUNT(*) FROM tasks WHERE type='follow_up' AND status='completed' "
                    "AND created_at >= datetime('now', '-7 days')"
                ).fetchone()[0]

            return [
                "Seguimiento automático",
                f"Pendientes: {pending} | Enviados esta semana: {completed}",
                "Tipos activos:",
                "  • Lead frío (48h sin respuesta) — activo",
                "  • Conversación abandonada — activo",
                "  • Recordatorio de cita — activo",
                "  • Reactivación (60+ días) — manual con /reactivar",
                "Para cambiar la configuración escríbeme algo como:\n'desactiva el follow-up de 48 horas'"
            ]
        except Exception as e:
            return [f"Error: {e}"]

    async def _admin_preconsult_config(self, clinic: Dict) -> List[str]:
        """
        /preconsulta — Configura el formulario de pre-consulta automático.
        Antes de la cita, Firby recopila síntomas, fotos, historial.
        """
        sector = clinic.get("sector", "otro")
        templates = {
            "estetica": [
                "zona de interés", "tratamientos anteriores", "alergias conocidas",
                "foto del área (opcional)", "qué resultado esperas"
            ],
            "medico": [
                "motivo de consulta", "síntomas principales", "hace cuánto",
                "medicamentos actuales", "alergias", "última vez que consultó"
            ],
            "dental": [
                "motivo de consulta", "dolor (sí/no y dónde)", "últimas radiografías",
                "sensibilidad al frío o calor", "tratamientos previos"
            ],
        }
        fields = templates.get(sector, ["motivo de consulta", "síntomas", "historial relevante"])

        # Guardar como configuración
        db.update_clinic(preconsult_fields=fields)

        return [
            "Pre-consulta automática configurada",
            f"Sector detectado: {sector}",
            "Firby recopilará esto antes de cada cita:",
            "  " + "\n  ".join(f"• {f}" for f in fields),
            "El médico llega con el caso pre-estudiado",
            "Para personalizar: 'agrega el campo [nombre] a la pre-consulta'"
        ]

    async def _admin_broadcast(self, message: str) -> List[str]:
        """
        /broadcast [mensaje] — Envía un mensaje a todos los pacientes activos.
        Límite de 50 pacientes, con delay para no quedar bloqueado.
        """
        if not message or len(message) < 5:
            return ["Formato: /broadcast tu mensaje aquí"]

        try:
            with db._conn() as c:
                patients = c.execute("""
                    SELECT DISTINCT chat_id FROM patients
                    WHERE chat_id IS NOT NULL
                    ORDER BY created_at DESC LIMIT 50
                """).fetchall()

            if not patients:
                return ["No hay pacientes registrados"]

            # Programar envíos escalonados (1 cada 3 segundos)
            scheduled = 0
            for i, pt in enumerate(patients):
                run_at = datetime.now() + timedelta(seconds=i * 3)
                task_manager.schedule_task(
                    task_type="reminder",
                    data={"chat_id": pt["chat_id"], "message": message},
                    scheduled_for=run_at,
                    priority=3
                )
                scheduled += 1

            return [
                f"Broadcast programado para {scheduled} contactos",
                f"Mensaje: {message[:100]}{'...' if len(message) > 100 else ''}",
                "Se enviará escalonado en los próximos minutos para evitar bloqueos",
                "Usa con cuidado — demasiados mensajes masivos pueden generar baneo en WhatsApp"
            ]

        except Exception as e:
            return [f"Error: {e}"]

    async def _admin_instagram_guide(self) -> List[str]:
        """
        /instagram — Guía para conectar Instagram DMs a Firby.
        Actualmente requiere configuración manual vía Meta API.
        """
        return [
            "Conectar Instagram DMs a Firby",
            "Estado actual: en configuración (requiere Meta Business verificado)",
            "Lo que necesitas:",
            "  1. Cuenta de Instagram Business o Creator",
            "  2. Meta Business Suite verificado",
            "  3. App de Meta aprobada con permiso instagram_manage_messages",
            "  4. Webhook configurado en: https://nexusys.duckdns.org/instagram/webhook",
            "Cuando lo tengas listo escríbeme:",
            "  'el instagram access token es [TOKEN]'",
            "  'el instagram page id es [ID]'",
            "Y Firby empezará a responder los DMs igual que WhatsApp"
        ]

    async def _admin_payments_guide(self) -> List[str]:
        """
        /pagos — Configura pagos desde el chat (Wompi, MercadoPago, Stripe).
        Cuando el cliente confirma, Firby manda el link de pago directo.
        """
        clinic = db.get_clinic()
        payment_cfg = clinic.get("payment_config") or {}
        if isinstance(payment_cfg, str):
            import json as _j
            try: payment_cfg = _j.loads(payment_cfg)
            except Exception: payment_cfg = {}

        active = payment_cfg.get("provider", "")
        status = f"Activo: {active}" if active else "Sin configurar"

        return [
            f"Pagos desde el chat — {status}",
            "Providers disponibles:",
            "  • Wompi (Colombia) — recomendado",
            "  • MercadoPago — latinoamérica",
            "  • Stripe — internacional",
            "Para activar escríbeme:",
            "  'configura pagos con Wompi, mi clave pública es [KEY]'",
            "  'configura pagos con MercadoPago, token [TOKEN]'",
            "Cuando un cliente confirme, Firby manda el link de pago automáticamente"
        ]

    async def _admin_trigger_report(self) -> List[str]:
        """
        /reporte — Genera y envía el reporte ahora mismo (sin esperar las 8am).
        """
        try:
            clinic    = db.get_clinic()
            biz_name  = clinic.get("name", "el negocio")
            admin_ids = _parse_admin_ids(clinic.get("admin_chat_ids", []))

            # Programar para ahora mismo
            task_manager.schedule_task(
                task_type="report",
                data={"type": "daily"},
                scheduled_for=datetime.now(),
                priority=8
            )

            # También generar preview rápido
            with db._conn() as c:
                convs_hoy = c.execute(
                    "SELECT COUNT(DISTINCT chat_id) FROM conversations "
                    "WHERE created_at >= datetime('now', '-1 days')"
                ).fetchone()[0] or 0
                apts_hoy = c.execute(
                    "SELECT COUNT(*) FROM appointments "
                    "WHERE created_at >= datetime('now', '-1 days')"
                ).fetchone()[0] or 0

            return [
                f"Reporte generado y enviando",
                f"Hoy: {convs_hoy} conversaciones, {apts_hoy} citas",
                "El reporte completo llega en un momento por aquí mismo"
            ]
        except Exception as e:
            return [f"Error: {e}"]

    # ═══════════════════════════════════════════════════════════════════════════
    # V8.0 — COMANDOS DE MODELO Y SISTEMAS
    # ═══════════════════════════════════════════════════════════════════════════

    async def _admin_show_model(self, clinic: Dict) -> List[str]:
        """
        /modelo — Muestra el modelo activo y el catálogo de opciones.
        El admin puede cambiar el modelo en caliente sin reiniciar.
        """
        if not model_manager:
            return ["El gestor de modelos no está disponible (reinicia el servidor)."]

        current_display = model_manager.get_current_model_display()
        catalog_display = model_manager.get_catalog_display()

        return [
            f"V8.0 — Gestión de modelos\n\n{current_display}",
            catalog_display,
        ]

    async def _admin_set_model(self, arg: str, clinic: Dict) -> List[str]:
        """
        /modelo [alias|id_completo|reset]
        Cambia el modelo en caliente. Persiste en DB.
        """
        if not model_manager:
            return ["El gestor de modelos no está disponible."]

        success, message = model_manager.set_model_from_command(arg)

        if success:
            # Mostrar el estado actualizado
            current = model_manager.get_current_model_display()
            return [
                f"Listo. {message}",
                current,
                "El cambio es inmediato. Sobrevive reinicios.",
                "Para volver al .env: /modelo reset"
            ]
        else:
            return [
                message,
                model_manager.get_catalog_display()
            ]

    async def _admin_v8_status(self) -> List[str]:
        """
        /v8 — Estado completo de sistemas V8 + salud real de providers LLM.
        """
        lines = ["V8.1 — Estado de sistemas\n"]

        # ── Salud de providers LLM ─────────────────────────────────────────────
        if llm_engine:
            health = llm_engine.get_health()
            lines.append("Providers LLM (cascada):")
            for p in llm_engine.providers:
                h = health.get(p.name, {})
                if h.get("blocked"):
                    secs = h.get("unblocks_in", 0)
                    status = f"⛔ BLOQUEADO ({secs}s restantes)"
                elif h.get("failures", 0) > 0:
                    status = f"⚠️ OK con {h['failures']} fallo(s) reciente(s)"
                else:
                    status = "✅ OK"
                # Modelo que está usando
                mdl = getattr(p, "MDLS", {}).get("fast", "?")
                lines.append(f"  {p.name}: {status} | modelo fast: {mdl}")
        else:
            lines.append("LLMEngine: ⛔ NO INICIADO — sin respuestas de IA")

        # ── Modelo activo ──────────────────────────────────────────────────────
        if model_manager:
            effective = model_manager.get_effective_models()
            lines.append(f"\nModelo activo:")
            lines.append(f"  fast: {effective.get('fast', 'default del .env')}")
            lines.append(f"  reasoning: {effective.get('reasoning', 'default del .env')}")
        else:
            lines.append("\nModelManager: NO INICIADO")

        # ── AntiRobotFilter ────────────────────────────────────────────────────
        if anti_robot_filter:
            lines.append(f"\nAntiRobotFilter: ✅ nivel {anti_robot_filter.level}/3")
        else:
            lines.append("\nAntiRobotFilter: ⚠️ NO INICIADO")

        # ── ConversationIntelligence ───────────────────────────────────────────
        if conversation_intelligence:
            active_convs = len(conversation_intelligence._states)
            stage_counts: Dict[str, int] = {}
            for state in conversation_intelligence._states.values():
                s = state.get("stage", "COLD")
                stage_counts[s] = stage_counts.get(s, 0) + 1
            lines.append(f"\nConversationIntelligence: {active_convs} chats activos")
            for stage, count in sorted(stage_counts.items()):
                lines.append(f"  {stage}: {count}")
        else:
            lines.append("\nConversationIntelligence: ⚠️ NO INICIADO")

        # ── Pipeline ───────────────────────────────────────────────────────────
        if conversion_funnel:
            summary = conversion_funnel.get_pipeline_summary()
            total  = sum(summary.values())
            booked = summary.get("booked", 0) + summary.get("confirmed", 0)
            rate   = round(booked / total * 100, 1) if total > 0 else 0
            lines.append(f"\nPipeline: {total} leads · {rate}% conversión")

        # ── Fallos recientes LLM (últimas 2h) ─────────────────────────────────
        try:
            if db:
                # Métricas de fallo guardadas por _register_failure
                recent_fails = db.get_metrics("llm_failure", limit=10)
                if recent_fails:
                    lines.append("\nÚltimos fallos LLM:")
                    for mf in recent_fails[:5]:
                        lines.append(f"  {mf.get('category','?')}: {mf.get('details',{}).get('error','?')[:60]}")
        except Exception:
            pass

        lines.append(f"\nTimeout provider: 10s | Blacklist TTL: {llm_engine._blacklist_ttl if llm_engine else '?'}s")
        lines.append("Para desbloquear un provider manualmente: /v8 reset")

        return ["\n".join(lines)]

    async def _admin_show_filter_status(self) -> List[str]:
        """
        /filtro — Muestra el estado del AntiRobotFilter y explica los niveles.
        """
        level = anti_robot_filter.level if anti_robot_filter else 2
        levels_desc = {
            1: "Suave — solo frases de call center obvias",
            2: "Normal (recomendado) — frases + patrones de bot",
            3: "Estricto — también cierres formales y aperturas repetitivas",
        }
        lines = [
            f"AntiRobotFilter — Nivel actual: {level}",
            f"  {levels_desc.get(level, 'desconocido')}",
            "",
            "Niveles disponibles:",
        ]
        for lvl, desc in levels_desc.items():
            mark = " ← activo" if lvl == level else ""
            lines.append(f"  /filtro {lvl} — {desc}{mark}")

        lines.append("\nFrases actualmente bloqueadas:")
        if anti_robot_filter:
            sample = list(anti_robot_filter.FORBIDDEN_EXACT)[:8]
            for phrase in sample:
                lines.append(f"  • '{phrase}'")
            lines.append(f"  ... y {len(anti_robot_filter.FORBIDDEN_EXACT) - 8} más")

        return ["\n".join(lines)]

    async def _admin_set_filter_level(self, level_str: str) -> List[str]:
        """
        /filtro [1|2|3] — Cambia el nivel del AntiRobotFilter.
        """
        global anti_robot_filter, hyper_human_engine

        if not level_str.isdigit() or int(level_str) not in (1, 2, 3):
            return ["Niveles válidos: 1 (suave), 2 (normal), 3 (estricto)"]

        level = int(level_str)
        Config.V8_FILTER_LEVEL = level
        anti_robot_filter = AntiRobotFilter(level=level)
        if hyper_human_engine:
            hyper_human_engine.filter = anti_robot_filter

        if db:
            db.remember("v8_filter_level", str(level), "config")

        level_names = {1: "suave", 2: "normal", 3: "estricto"}
        return [
            f"Filtro anti-robot cambiado a nivel {level} ({level_names[level]})",
            "El cambio aplica desde el próximo mensaje."
        ]

    async def _admin_pipeline_v8(self) -> List[str]:
        """
        /pipeline — Pipeline de leads usando ConversionFunnelTracker V8.
        Más detallado que el /pipeline de V6.
        """
        if not conversion_funnel:
            # Fallback al pipeline V6
            return await self._admin_pipeline()

        report = conversion_funnel.format_pipeline_report()
        rates  = conversion_funnel.get_conversion_rate()

        # Identificar el cuello de botella
        bottleneck = ""
        min_rate = 1.0
        for stage, rate in rates.items():
            if 0 < rate < min_rate:
                min_rate = rate
                bottleneck = stage

        lines = [report]
        if bottleneck:
            stage_tips = {
                "discovery":     "Firby no está logrando explorar el dolor real. Revisar /coach.",
                "pain_explored": "El puente dolor→solución no está funcionando. Revisar arquetipos.",
                "solution_match":"Los clientes no están aceptando la valoración. Revisar el cierre.",
                "objection_active": "Las objeciones están ganando. Revisar respuestas de /reglas.",
                "micro_commitment": "El cliente está listo pero no agenda. Revisar la propuesta de fecha.",
            }
            tip = stage_tips.get(bottleneck, "Revisar conversaciones en /chats.")
            lines.append(f"\nCuello de botella detectado: {bottleneck}")
            lines.append(f"Sugerencia: {tip}")

        return lines

    async def _admin_natural_command(self, chat_id: str, text: str,
                                     clinic: Dict) -> List[str]:
        """
        Cerebro conversacional del modo admin.
        V9 Upgrade: Aprendizaje natural + Simulaciones interactivas.
        """
        text_low = text.lower().strip()

        # ── INTERCEPCIÓN DE CONTEXTO DE ESCALACIÓN ───────────────────────────
        # "muéstrame qué pasó", "muestrame que paso", "contexto", "ver contexto", "qué pasó", "que paso"
        import re as _re
        clean_text = _re.sub(r"[¿?¡!\.,]", "", text_low).strip()
        CONTEXT_SIGNALS = {
            "muestrame que paso", "muéstrame qué pasó", "que paso", "qué pasó",
            "contexto", "ver contexto", "contexto de la conversacion", "contexto de la conversación",
            "ver conversacion", "ver conversación", "contexto de la charla", "mostrar charla", "mostrar chat"
        }
        if clean_text in CONTEXT_SIGNALS:
            patient_chat_id = None
            pending = self._admin_pending.get(chat_id)
            if pending and isinstance(pending, dict):
                patient_chat_id = pending.get("patient_chat_id")
            
            if not patient_chat_id:
                patient_chat_id = getattr(self, "_last_escalated_chat_id", None)
            
            if not patient_chat_id:
                try:
                    with db._conn() as c:
                        row = c.execute("""
                            SELECT chat_id FROM conversation_states
                            WHERE json_extract(state, '$.escalation_needed') = 1 
                               OR json_extract(state, '$.escalation_needed') = 'true'
                            ORDER BY updated_at DESC LIMIT 1
                        """).fetchone()
                        if row:
                            patient_chat_id = row["chat_id"]
                except Exception as _db_err:
                    log.warning(f"[admin_context] error buscando ultimo escalado en DB: {_db_err}")
            
            if patient_chat_id:
                log.info(f"[admin_context] Admin {chat_id} solicitó contexto. Mostrando chat de {patient_chat_id}")
                return await self._admin_show_patient_chat(patient_chat_id)
            else:
                return ["No tengo registro de ningún paciente que haya solicitado hablar con un humano recientemente."]

        # ── COMANDO PARA VINCULAR TELEGRAM MANUALMENTE ───────────────────────
        if any(w in text_low for w in ["vincular telegram", "conectar telegram", "link telegram", "telegram admin"]):
            channels = db.get_linked_channels() if hasattr(db, "get_linked_channels") else []
            tg_channel = next((c for c in channels if c.get("platform") == "telegram"), None)
            if tg_channel:
                bot_username = tg_channel.get("channel_identity", "")
                cfg = tg_channel.get("config_json", {})
                if isinstance(cfg, str):
                    try: cfg = json.loads(cfg) or {}
                    except Exception: cfg = {}
                token = cfg.get("token", "")
                if bot_username and token:
                    admin_rec = db.get_admin(chat_id)
                    admin_email = admin_rec.get("email", "admin@clinic.com") if admin_rec else "admin@clinic.com"
                    admin_name = admin_rec.get("name", "Admin") if admin_rec else "Admin"
                    import secrets
                    link_token = secrets.token_hex(8)
                    db.remember(f"tg_link_admin_{link_token}", json.dumps({
                        "email": admin_email,
                        "name": admin_name,
                        "whatsapp_jid": chat_id
                    }, ensure_ascii=False))
                    bot_user_clean = bot_username.lstrip("@")
                    link_url = f"https://t.me/{bot_user_clean}?start=link_admin_{link_token}"
                    return [
                        f"Aquí tienes el enlace de vinculación para tu bot *@ {bot_user_clean}*:",
                        f"👉 Haz clic aquí para vincular tu cuenta de Telegram: {link_url}",
                        "Este enlace expirará en 15 minutos."
                    ]
            return ["No he encontrado ningún bot de Telegram configurado en esta instancia. Pásame el bot token por aquí para configurarlo automáticamente primero."]

        # ── COMANDO PARA SINCRONIZAR NOTION ──────────────────────────────────
        if any(w in text_low for w in ["sincronizar notion", "sincroniza notion", "notion sync", "sincronizar bases de datos de notion"]):
            channels = db.get_linked_channels() if hasattr(db, "get_linked_channels") else []
            notion_channel = next((c for c in channels if c.get("platform") == "notion"), None)
            if notion_channel:
                cfg = notion_channel.get("config_json", {})
                if isinstance(cfg, str):
                    try: cfg = json.loads(cfg) or {}
                    except Exception: cfg = {}
                token = cfg.get("token", "")
                if token:
                    try:
                        from src.firby.integrations.notion import NotionClient
                        client = NotionClient(token)
                        databases = await client.list_databases()
                        if not databases:
                            return [
                                "ℹ️ *Sincronización de Notion*",
                                "He intentado buscar bases de datos de Notion compartidas con la integración, pero no encontré ninguna.",
                                "Asegúrate de haber compartido explícitamente tus bases de datos o páginas de Notion con la integración de Firby desde la interfaz de Notion (botón 'Share' / 'Connections')."
                            ]
                        
                        synced_info = []
                        total_pages = 0
                        for db_info in databases:
                            db_id = db_info["id"]
                            db_title = db_info["title"]
                            res = await client.sync_database(db_id)
                            if res.get("ok"):
                                pages = res.get("pages_synced", 0)
                                total_pages += pages
                                synced_info.append(f"• *{db_title}* ({pages} páginas)")
                            else:
                                synced_info.append(f"• ❌ *{db_title}* (Error: {res.get('error')})")
                        
                        return [
                            "🔄 *Sincronización de Notion Completada*",
                            f"He analizado {len(databases)} bases de datos/páginas y extraído conocimientos:",
                            "\n".join(synced_info),
                            f"Total de páginas importadas con éxito: *{total_pages}*.",
                            "Tus nuevos conocimientos ya están integrados en mi cerebro local y listos para ser usados en respuestas."
                        ]
                    except Exception as e:
                        log.error(f"[admin_notion] Error en sincronización: {e}", exc_info=True)
                        return [f"Hubo un error al intentar sincronizar con Notion: {e}"]
            return [
                "Notion no está conectado en esta instancia.",
                "Pásame tu clave de integración de Notion (comienza con `ntn_`) para vincular tu espacio de trabajo de manera automática."
            ]

        persona = clinic.get("persona_config", {})
        if isinstance(persona, str):
            try:
                persona = json.loads(persona) if persona else {}
            except Exception:
                persona = {}
        agent_name = clinic.get("assistant_name") or persona.get("name") or "Firby"
        if agent_name.lower() in ("lucia", "lucía"):
            agent_name = "Firby"

        # ── COMANDOS DE APRENDIZAJE NATURAL ──────────────────────────────────
        # Detecta frases como "no digas X", "usa emojis", "dile Y"
        LEARNING_SIGNALS = [
            "no digas", "no le digas", "deja de decir", "quita la frase",
            "usa emojis", "ponle emojis", "responde con", "dile que",
            "siempre di", "nunca digas", "aprende esto", "guarda esto",
            "cambia la forma", "ahora dile", "cuando pregunten por",
            "la respuesta correcta es", "háblale de", "menciona que"
        ]

        # ── AUTO-DETECCIÓN DE TOKENS EN LENGUAJE NATURAL ──────────────────────
        # Si el texto contiene un token de Telegram o Slack, o credenciales de Gmail,
        # lo configuramos de forma automática sin que estén en un flujo explícito.
        
        # 1. Telegram Token
        tg_match = re.search(r"([0-9]+:AA[a-zA-Z0-9_-]+)", text)
        if tg_match:
            token = tg_match.group(1)
            try:
                from src.firby.channels.onboarding import validate_telegram_token
                bot_username = await validate_telegram_token(token)
                if bot_username:
                    db.add_linked_channel(
                        platform="telegram",
                        channel_identity=bot_username,
                        config_json={"token": token}
                    )
                    # Limpiar omni_flow por si acaso
                    buf = clinic.get("setup_buffer", {})
                    if isinstance(buf, str):
                        try: buf = json.loads(buf) if buf else {}
                        except Exception: buf = {}
                    buf["omni_flow"] = ""
                    db.update_clinic(setup_buffer=json.dumps(buf, ensure_ascii=False))
                    
                    # Configurar el webhook de forma automática
                    webhook_url = f"{Config.BASE_URL}/webhook/{Config.WEBHOOK_SECRET}?bot={bot_username}"
                    set_webhook_url = f"https://api.telegram.org/bot{token}/setWebhook?url={webhook_url}"
                    try:
                        import httpx
                        async with httpx.AsyncClient(timeout=8.0) as client:
                            resp = await client.post(set_webhook_url)
                            log.info(f"[auto_token] setWebhook response: {resp.status_code} {resp.text}")
                    except Exception as e:
                        log.error(f"[auto_token] Error registrando webhook de Telegram: {e}")

                    # Generar token de vinculación de admin
                    admin_rec = db.get_admin(chat_id)
                    admin_email = admin_rec.get("email", "admin@clinic.com") if (admin_rec and hasattr(admin_rec, "get")) else "admin@clinic.com"
                    admin_name = admin_rec.get("name", "Admin") if (admin_rec and hasattr(admin_rec, "get")) else "Admin"
                    
                    # Convert to string and handle MagicMock
                    if not isinstance(admin_email, str) or admin_email.__class__.__name__ == "MagicMock":
                        admin_email = "admin@clinic.com"
                    if not isinstance(admin_name, str) or admin_name.__class__.__name__ == "MagicMock":
                        admin_name = "Admin"
                        
                    import secrets
                    link_token = secrets.token_hex(8)
                    db.remember(f"tg_link_admin_{link_token}", json.dumps({
                        "email": admin_email,
                        "name": admin_name,
                        "whatsapp_jid": chat_id
                    }, ensure_ascii=False))
                    bot_user_clean = bot_username.lstrip("@")
                    link_url = f"https://t.me/{bot_user_clean}?start=link_admin_{link_token}"

                    return [
                        "🎉 ¡He detectado y configurado automáticamente tu bot de Telegram!",
                        f"Bot activo: *@ {bot_user_clean}*",
                        "Ya configuré el webhook. Ahora puedes escribirme directamente por Telegram y te responderé por allá.",
                        f"👉 *CRÍTICO*: Para que te reconozca como administrador por allá y compartamos la misma memoria de control, haz clic en este enlace para vincular tu cuenta: {link_url}"
                    ]
            except Exception as _tg_auto_err:
                log.warning(f"[auto_token] Telegram validation error: {_tg_auto_err}")

        # 2. Slack Token
        slack_match = re.search(r"(xoxb-[a-zA-Z0-9-]+)", text)
        if slack_match:
            token = slack_match.group(1)
            try:
                from src.firby.channels.onboarding import validate_slack_token
                slack_info = await validate_slack_token(token)
                if slack_info:
                    db.add_linked_channel(
                        platform="slack",
                        channel_identity=slack_info["team_id"],
                        config_json={
                            "token": token,
                            "team": slack_info["team"],
                            "bot_id": slack_info["bot_id"]
                        }
                    )
                    buf = clinic.get("setup_buffer", {})
                    if isinstance(buf, str):
                        try: buf = json.loads(buf) if buf else {}
                        except Exception: buf = {}
                    buf["omni_flow"] = ""
                    db.update_clinic(setup_buffer=json.dumps(buf, ensure_ascii=False))
                    
                    return [
                        "🎉 ¡He detectado y configurado tu token de Slack!",
                        f"Workspace conectado: *{slack_info['team']}* (ID: {slack_info['team_id']})",
                        "Para recibir mensajes, asegúrate de invitar al bot a tus canales usando `/invite @TuBot`."
                    ]
            except Exception as _slack_auto_err:
                log.warning(f"[auto_token] Slack validation error: {_slack_auto_err}")

        # 3. Gmail Credentials
        gmail_match = re.search(r"\b(AIzaSy[a-zA-Z0-9_-]{33}|GOCSPX-[a-zA-Z0-9_-]{28,})\b", text)
        if gmail_match:
            credentials = gmail_match.group(1)
            try:
                from src.firby.channels.onboarding import validate_gmail_credentials
                gmail_info = await validate_gmail_credentials(credentials)
                if gmail_info:
                    db.add_linked_channel(
                        platform="gmail",
                        channel_identity=gmail_info["email"],
                        config_json={
                            "credentials": credentials,
                            "email": gmail_info["email"],
                            "display_name": gmail_info["name"]
                        }
                    )
                    buf = clinic.get("setup_buffer", {})
                    if isinstance(buf, str):
                        try: buf = json.loads(buf) if buf else {}
                        except Exception: buf = {}
                    buf["omni_flow"] = ""
                    db.update_clinic(setup_buffer=json.dumps(buf, ensure_ascii=False))
                    
                    auth_link = f"https://accounts.google.com/o/oauth2/v2/auth?client_id=12345-firby.apps.googleusercontent.com&redirect_uri={Config.BASE_URL}/gmail/callback&response_type=code&scope=https://www.googleapis.com/auth/gmail.modify"
                    
                    sys_prompt = f"""Eres la asistente de IA, la mano derecha de IA de esta clínica. Estás conversando con el dueño por WhatsApp.
El dueño acaba de enviarte credenciales de Google / Gmail para conectar la cuenta {gmail_info['email']}.
Las credenciales fueron procesadas y guardadas exitosamente en la bóveda de la clínica.
El enlace de confirmación para que el dueño autorice es: {auth_link}

REGLAS:
1. Responde de forma cálida, humana y colombiana en 2 o 3 burbujas cortas de WhatsApp separadas por '|||'.
2. NUNCA uses plantillas acartonadas, fríos encabezados ni discursos robóticos.
3. Entra directo como una persona real alegrándote por la integración y ofreciendo el enlace."""

                    from src.core.globals import llm_engine
                    if llm_engine:
                        res_llm, _ = await llm_engine.complete([
                            {"role": "system", "content": sys_prompt},
                            {"role": "user", "content": text}
                        ], model_tier="fast", temperature=0.4, use_cache=False)
                        if res_llm and res_llm.strip():
                            return [b.strip() for b in res_llm.split("|||") if b.strip()]
            except Exception as _gmail_auto_err:
                log.warning(f"[auto_token] Gmail validation error: {_gmail_auto_err}")

        # 4. WhatsApp Cloud API Access Token
        wa_cloud_match = re.search(r"\b(EAA[a-zA-Z0-9]+)\b", text)
        if wa_cloud_match:
            token = wa_cloud_match.group(1)
            buf = clinic.get("setup_buffer", {})
            if isinstance(buf, str):
                try: buf = json.loads(buf) if buf else {}
                except Exception: buf = {}
            phone_id = buf.get("wa2_phone_id", "")
            if phone_id:
                buf["omni_flow"] = "wa2_waiting_token"
                db.update_clinic(setup_buffer=json.dumps(buf, ensure_ascii=False))
                try:
                    from src.firby.channels.onboarding import handle_omnichannel_setup_flow
                    res_flow = await handle_omnichannel_setup_flow(self, chat_id, text, clinic)
                    if res_flow:
                        return res_flow
                except Exception:
                    pass
            else:
                return [
                    "📱 *Token de WhatsApp Cloud API Detectado*",
                    "He detectado un Access Token de WhatsApp Cloud API (empieza con `EAA...`).",
                    "Para conectarlo, primero necesito el *Phone Number ID*.",
                    "Por favor, escribe `/whatsapp2` para iniciar el asistente de configuración paso a paso y configurar ambos datos."
                ]

        # 4.5. Notion Token
        notion_match = re.search(r"\b(ntn_[a-zA-Z0-9_-]{30,})\b", text)
        if notion_match:
            token = notion_match.group(1)
            try:
                from src.firby.channels.onboarding import validate_notion_token
                notion_info = await validate_notion_token(token)
                if notion_info:
                    db.add_linked_channel(
                        platform="notion",
                        channel_identity=notion_info["workspace_name"],
                        config_json={
                            "token": token,
                            "workspace_name": notion_info["workspace_name"],
                            "bot_name": notion_info["bot_name"]
                        }
                    )
                    buf = clinic.get("setup_buffer", {})
                    if isinstance(buf, str):
                        try: buf = json.loads(buf) if buf else {}
                        except Exception: buf = {}
                    buf["omni_flow"] = ""
                    db.update_clinic(setup_buffer=json.dumps(buf, ensure_ascii=False))
                    
                    return [
                        "🎉 ¡He detectado y registrado tu clave de integración de Notion!",
                        f"Espacio de trabajo vinculado: *{notion_info['workspace_name']}*",
                        "A partir de ahora puedo sincronizarme con tus bases de datos y páginas de Notion.",
                        "Puedes decirme *'sincronizar Notion'* en cualquier momento para cargar tu base de conocimientos."
                    ]
            except Exception as _notion_auto_err:
                log.warning(f"[auto_token] Notion validation error: {_notion_auto_err}")

        # 4.6. ElevenLabs Token
        elevenlabs_match = re.search(r"\b(sk_[a-zA-Z0-9_-]{30,})\b", text)
        if elevenlabs_match:
            token = elevenlabs_match.group(1)
            try:
                db.add_linked_channel(
                    platform="elevenlabs",
                    channel_identity="ElevenLabs Voice Engine",
                    config_json={"token": token}
                )
                import os
                os.environ["ELEVENLABS_API_KEY"] = token
                try:
                    env_path = os.path.join(os.getcwd(), ".env")
                    if not os.path.exists(env_path):
                        env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".env")
                    if os.path.exists(env_path):
                        with open(env_path, "r", encoding="utf-8") as f:
                            env_lines = f.readlines()
                        new_lines = []
                        replaced = False
                        for line in env_lines:
                            if line.startswith("ELEVENLABS_API_KEY="):
                                new_lines.append(f"ELEVENLABS_API_KEY={token}\n")
                                replaced = True
                            else:
                                new_lines.append(line)
                        if not replaced:
                            new_lines.append(f"\nELEVENLABS_API_KEY={token}\n")
                        with open(env_path, "w", encoding="utf-8") as f:
                            f.writelines(new_lines)
                except Exception as e:
                    log.warning(f"Error updating .env with ELEVENLABS_API_KEY: {e}")
                
                try:
                    import firby_demo_voice
                    firby_demo_voice.API_KEYS[0] = token
                except Exception:
                    pass
                    
                # Generar audio de prueba
                try:
                    from firby_demo_voice import generate_demo_audio
                    audio_path = await generate_demo_audio("¡Hola! He activado y configurado con éxito tu API de Eleven Labs. A partir de ahora puedo responderte con notas de voz realistas usando esta conexión.", voice_idx=0)
                    if audio_path and os.path.exists(audio_path):
                        await self._send_audio(chat_id, audio_path)
                        os.unlink(audio_path)
                except Exception as voice_err:
                    log.warning(f"Error generating test audio: {voice_err}")
                
                return [
                    "🎙️ *¡Conexión de ElevenLabs Configurada!*",
                    "He registrado tu API Key de ElevenLabs de forma automática y enviado un audio de prueba para confirmar que funciona."
                ]
            except Exception as _el_auto_err:
                log.warning(f"[auto_token] ElevenLabs setup error: {_el_auto_err}")

        # 5. Genérico / No reconocido
        generic_tokens = [
            w for w in text.split()
            if len(w) >= 25 
            and not w.startswith("http")
            and not w.startswith("ntn_")
            and not w.startswith("sk_")
            and not "/" in w
            and any(c.isdigit() for c in w)
            and any(c.isalpha() for c in w)
        ]
        if generic_tokens:
            token_preview = generic_tokens[0]
            if len(token_preview) > 15:
                token_preview = token_preview[:6] + "..." + token_preview[-6:]
            return [
                "🔍 *Credencial Detectada*",
                f"Detecté la clave `{token_preview}` en tu mensaje, pero no puedo determinar a qué servicio pertenece.",
                "Por favor, selecciona qué canal deseas configurar con esta clave ejecutando el comando correspondiente:",
                "👉 `/telegram` — Conectar bot de Telegram",
                "👉 `/slack` — Conectar espacio de Slack",
                "👉 `/gmail` — Conectar cuenta de Gmail",
                "👉 `/whatsapp2` — Conectar WhatsApp Cloud API secundario"
            ]

        # ── INTERCEPCIÓN DE CONFIGURACIÓN DE CANALES EN LENGUAJE NATURAL ──────
        # Telegram
        if "telegram" in text_low and any(w in text_low for w in ["token", "conectar", "vincular", "cree un bot", "nuevo bot"]):
            buf = clinic.get("setup_buffer", {})
            if isinstance(buf, str):
                try: buf = json.loads(buf) if buf else {}
                except Exception: buf = {}
            buf["omni_flow"] = "telegram_waiting_token"
            db.update_clinic(setup_buffer=json.dumps(buf, ensure_ascii=False))
            return [
                "🤖 *Conexión de Telegram*",
                "¡Excelente! Veo que quieres conectar tu bot de Telegram.",
                "Por favor, envíame directamente el *HTTP API Token* de Telegram (el que te da @BotFather y que usualmente tiene un formato como `123456789:ABCdefGhIJK...`).",
                "Escribe 'cancelar' si deseas salir."
            ]

        # Slack
        if "slack" in text_low and any(w in text_low for w in ["token", "conectar", "vincular", "workspace"]):
            buf = clinic.get("setup_buffer", {})
            if isinstance(buf, str):
                try: buf = json.loads(buf) if buf else {}
                except Exception: buf = {}
            buf["omni_flow"] = "slack_waiting_token"
            db.update_clinic(setup_buffer=json.dumps(buf, ensure_ascii=False))
            return [
                "💬 *Conexión de Slack*",
                "¡Genial! Iniciemos la conexión con Slack.",
                "Por favor, envíame tu *Bot User OAuth Token* (el que empieza con `xoxb-`).",
                "Escribe 'cancelar' si deseas salir."
            ]

        # Gmail
        if "gmail" in text_low and any(w in text_low for w in ["token", "conectar", "vincular", "credenciales", "api key", "client secret"]):
            buf = clinic.get("setup_buffer", {})
            if isinstance(buf, str):
                try: buf = json.loads(buf) if buf else {}
                except Exception: buf = {}
            buf["omni_flow"] = "gmail_waiting_credentials"
            db.update_clinic(setup_buffer=json.dumps(buf, ensure_ascii=False))
            return [
                "📧 *Conexión de Gmail*",
                "¡Perfecto! Iniciemos la conexión con Gmail.",
                "Por favor, envíame tu *Google API Key* o *Client Secret*.",
                "Escribe 'cancelar' si deseas salir."
            ]

        # ── INTERCEPCIÓN DE ACCIONES DE SISTEMA (Demo, Restart, etc) ──────────
        if "modo demo" in text_low or "activa demo" in text_low or "demo on" in text_low or "demo off" in text_low:
            is_on = any(w in text_low for w in ["activa", "poner", "on", "encender"])
            action = "on" if is_on else "off"
            db_val = "true" if is_on else "false"
            
            msg = f"entendido, voy a poner el modo demo en {action} y reiniciar el sistema ||| dame unos segundos"
            try:
                # 1. Cambiar flag en DB
                with db._conn() as c:
                    c.execute("INSERT OR REPLACE INTO system_config (key, value, updated_at) VALUES ('demo_mode', ?, datetime('now'))", (db_val,))
                
                # 2. Actualizar .env
                import subprocess
                env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".env")
                if os.path.exists(env_path):
                    cmd_sed = f"sed -i 's/^DEMO_MODE=.*/DEMO_MODE={db_val}/g' {env_path}"
                    subprocess.run(cmd_sed, shell=True)
                
                # 3. Ejecutar reinicio
                subprocess.Popen("pm2 restart firby", shell=True, start_new_session=True)
                return [msg]
            except Exception as e:
                log.error(f"[system] error activando demo: {e}")
                return [f"intenté activar el modo demo pero hubo un error técnico: {e}"]

        # ── INTERCEPCIÓN DE CALENDARIO / AGENDA ──────────────────────────────
        if any(w in text_low for w in ["agenda", "calendario", "citas", "calendar", "calendly"]):
            if not any(w in text_low for w in ["telegram", "slack", "gmail"]):
                return await self._admin_agenda_status()

        if any(s in text_low for s in LEARNING_SIGNALS):
            if self.admin_learning:
                reply = self.admin_learning.add_instruction(chat_id, text)
                return [reply]

        if "limpia las instrucciones" in text_low or "borra lo aprendido" in text_low:
            if self.admin_learning:
                return [self.admin_learning.clear()]

        # ── MODO SIMULACIÓN ──────────────────────────────────────────────────
        SIM_SIGNALS = [
            "simula", "simulaci", "como cliente", "hazte cliente",
            "actúa como cliente", "modo cliente", "hagamos una prueba",
            "ponte a prueba", "pruébame", "quiero ver cómo respondes",
            "simulemos", "haz como si fueras un paciente"
        ]
        if any(s in text_low for s in SIM_SIGNALS):
            if self.simulator:
                return self.simulator.start(chat_id)

        # ── SEGURIDAD: Bloquear intento de login inseguro ────────────────────
        # Si un usuario que NO es admin intenta enviar algo que parece login por nombre
        if ":" in text and ("password" in text_low or "contraseña" in text_low):
            is_admin = db.get_admin(chat_id) is not None
            if not is_admin:
                log.warning(f"[security] Intento de login inseguro bloqueado desde {chat_id}")
                return ["Por seguridad, no compartas contraseñas por este medio. Usa /login para iniciar sesión de forma segura."]

        # ── Reportes de Conversaciones ───────────────────────────────────────
        REPORT_SIGNALS = [
            "que han dicho", "qué han dicho", "quien ha escrito", "quién ha escrito",
            "ultimos pacientes", "últimos pacientes", "conversaciones", "chats",
            "qué me han enviado", "que me han enviado", "mensajes recientes"
        ]
        if any(s in text_low for s in REPORT_SIGNALS):
            return await self._admin_show_recent_conversation_browser(chat_id)

        # ── Ver un chat específico ───────────────────────────────────────────
        if "ver a " in text_low or "ver el chat de" in text_low:
            # Extraer número o nombre si es posible (implementación simplificada)
            return await self._admin_show_chats()

        # ── Auto-detección de credenciales WhatsApp ─────────────────────────
        wa_creds = _detect_wa_credentials(text)
        if wa_creds:
            return await self._admin_connect_whatsapp(
                chat_id, wa_creds["phone_id"], wa_creds["token"], clinic
            )

        # ── Detección de reglas Nova en lenguaje natural ──────────────────────
        # "no permitas que...", "bloquea...", "nunca envíes...", "prohíbe..."
        NOVA_RULE_SIGNALS = [
            r"no\s+(permitas?|dejes?|quiero que)\s+que\s+firby",
            r"(bloquea?|prohibe?|prohíbe?)\s+que",
            r"nunca\s+(envíes?|mandes?|digas?|menciones?)",
            r"no\s+(envíes?|mandes?|digas?|menciones?)\s+.{5,}",
            r"impide?\s+que\s+firby",
            r"asegúrate de que firby nunca",
        ]
        if _NOVA_AVAILABLE and Config.NOVA_ENABLED:
            if any(re.search(p, text_low) for p in NOVA_RULE_SIGNALS):
                return await self._admin_nova_add_rule(text, clinic)

        # ── Simulación en lenguaje natural — "hagamos una simulación", "cómo le hablarías" ──
        # (Lógica delegada al SimulationEngine en la parte superior del método)
        pass

        # ── KB automático: texto largo con info de la clínica ─────────────────
        if len(text) > 300 and kb is not None and _KB_AVAILABLE:
            kb_indicators = [
                "precio", "servicio", "tratamiento", "protocolo",
                "contraindicacion", "incluye", "sesion", "duracion",
                "costo", "valor", "procedimiento", "candidat",
                "beneficio", "resultado", "recuperacion"
            ]
            if sum(1 for kw in kb_indicators if kw in text_low) >= 3:
                return await self._admin_kb_upload(text)

        # ── Control duro del owner/admin ─────────────────────────────────────
        if owner_style_controller and owner_style_controller.detect_control_intent(text):
            result = owner_style_controller.apply_instruction(text, admin_chat_id=chat_id)
            if result.get("ok"):
                if prompt_evolver and trainer_gateway and trainer_gateway.detect_admin_learning_intent(text):
                    try:
                        await prompt_evolver.evolve(text.strip(), chat_id)
                    except Exception:
                        pass
                reply_lines = result.get("reply_lines", ["Listo. Ya quedó aplicado."])
                reply_text = self._apply_admin_output_pipeline(" ||| ".join(reply_lines), chat_id, clinic, user_msg=text)
                return self._split_bubbles(reply_text)

        # ── Gateway automático del trainer para admins ───────────────────────
        if trainer_gateway and prompt_evolver and trainer_gateway.detect_admin_learning_intent(text):
            learned = await prompt_evolver.evolve(text.strip(), chat_id)
            if learned.get("ok"):
                lines = [f"Entendido. {learned.get('description', 'Ya ajusté ese comportamiento.')}"]
                if learned.get("example_good"):
                    lines.append(f"Ejemplo: \"{learned['example_good']}\"")
                lines.append("Si quieres, lo seguimos afinando sobre la marcha.")
                reply_text = self._apply_admin_output_pipeline(" ||| ".join(lines), chat_id, clinic, user_msg=text)
                return self._split_bubbles(reply_text)

        # Natural inbox queries are now handled dynamically by the LLM using chats_summary context.
        pass

        selection_idx = _extract_conversation_selection(text_low)
        if selection_idx:
            show_all = _wants_all_messages(text_low)
            direct_selection = any(
                token in text_low
                for token in (
                    "conversacion", "conversación", "chat", "mensajes",
                    "hablado", "hablaste", "mostrame", "muestrame",
                    "muéstrame", "enseñame", "ensename",
                )
            )
            if direct_selection:
                reply = await self._admin_show_recent_conversation_selection(
                    chat_id,
                    selection_idx,
                    show_all=show_all,
                )
                reply_text = self._apply_admin_output_pipeline(" ||| ".join(reply), chat_id, clinic, user_msg=text)
                db.save_message(chat_id, "user", text)
                db.save_message(chat_id, "assistant", reply_text if reply else "")
                return self._split_bubbles(reply_text)

        tone_complaints = [
            "hablas raro", "no me gusta cómo hablas", "no me gusta como hablas",
            "estás rara", "estas rara", "eso suena robot", "suenas robot",
            "muy bot", "muy fría", "muy fria", "muy seca",
        ]
        if any(w in text_low for w in tone_complaints):
            reply_text = self._apply_admin_output_pipeline(" ||| ".join([
                "pásame la frase exacta o dime el tono que quieres",
                "te saco una versión más cálida, más directa o más premium"
            ]), chat_id, clinic, user_msg=text)
            return self._split_bubbles(reply_text)

        # ── Búsqueda web real cuando el admin pide investigar ────────────────
        SEARCH_SIGNALS = [
            "busca en google", "busca en internet", "busca en la web",
            "investiga", "googlea", "buscar", "búscame", "busque",
            "averigua", "infórmate", "informate", "investigue",
            "haz una busqueda", "haz una búsqueda", "investigación",
        ]
        web_results = None
        if any(s in text_low for s in SEARCH_SIGNALS):
            search_query = clinic.get("name", "")
            for prefix in ["busca en google", "busca en internet", "busca en la web",
                           "busca", "investiga", "averigua", "infórmate sobre",
                           "informate sobre", "investigue"]:
                if prefix in text_low:
                    after = text_low.split(prefix, 1)[1].strip().strip(",.!?¿¡")
                    if after and len(after) > 2:
                        search_query = after
                        break
            if not search_query or len(search_query) < 3:
                search_query = f"{clinic.get('name', '')} {clinic.get('tagline', '')}".strip()
            if not search_query:
                search_query = "clinica medellin"
            try:
                results = await asyncio.wait_for(
                    self.search.search(search_query),
                    timeout=15.0
                )
                if results and len(results) > 10:
                    web_results = f"Resultados de búsqueda web sobre \"{search_query}\":\n{results[:2500] if len(results) > 2500 else results}"
            except Exception as e:
                log.error(f"[admin_search] error: {e}")
                web_results = None

        # ── Historial de admin (últimos 8 mensajes) ───────────────────────────
        admin_history = db.get_history(chat_id, limit=8)

        # ── Llamar al LLM conversacional ──────────────────────────────────────
        error_msg = None
        error_msg = None
        try:
            result = await asyncio.wait_for(
                self._admin_llm_brain(chat_id, text, admin_history, clinic, agent_name, web_results=web_results),
                timeout=25.0
            )
        except Exception as e:
            import traceback
            log.error(f"[admin_brain] error: {e}", exc_info=True)
            error_msg = f"LLM Exception: {str(e)}"
            result = None

        if result is None:
            return [error_msg if error_msg else "LLM Error: Sin respuesta del cerebro."]

        # ── Aplicar acción validada ───────────────────────────────────────────
        reply_text = result.get("reply", "")
        action     = result.get("action", "none")
        data       = result.get("data", {})

        await self._admin_apply_action(action, data, clinic, chat_id, result)
        reply_text = result.get("reply", "")

        # ── Guardar en historial ──────────────────────────────────────────────
        reply_text = self._apply_admin_output_pipeline(reply_text, chat_id, clinic, user_msg=text)
        db.save_message(chat_id, "user", text)
        if reply_text:
            db.save_message(chat_id, "assistant", reply_text)

        return self._split_bubbles(reply_text) if reply_text else [
            "dime qué más necesitas"
        ]

    def _admin_get_recent_chats_summary(self, owner_chat_id: str, clinic: Dict) -> str:
        try:
            from src.firby.utils.helpers import _parse_admin_ids
            admin_ids = set(_parse_admin_ids(clinic.get("admin_chat_ids", [])))
            if owner_chat_id:
                admin_ids.add(str(owner_chat_id))
            
            with db._conn() as c:
                rows = c.execute("""
                    SELECT chat_id, MAX(ts) AS last_ts, COUNT(*) AS total
                    FROM conversations
                    WHERE role='user'
                    GROUP BY chat_id
                    ORDER BY last_ts DESC
                    LIMIT 5
                """).fetchall()
        except Exception:
            rows = []

        real_rows = []
        for row in rows:
            chat = str(row["chat_id"])
            if chat in admin_ids or self._is_synthetic_chat_id(chat):
                continue
            real_rows.append(row)

        if not real_rows:
            return "No hay chats reales con pacientes registrados todavía."

        lines = [f"Total de chats reales: {len(real_rows)}"]
        for idx, row in enumerate(real_rows, 1):
            chat = str(row["chat_id"])
            display = chat
            try:
                patient = db.get_patient(chat)
                name = (patient or {}).get("name", "").strip() if isinstance(patient, dict) else ""
                if name:
                    display = name
                elif "@s.whatsapp.net" in chat:
                    display = "chat de WhatsApp sin nombre"
                elif chat.isdigit():
                    display = "chat sin nombre"
            except Exception:
                pass
            
            # Obtener el último mensaje
            last_msg = ""
            try:
                with db._conn() as c:
                    last_row = c.execute("SELECT content FROM conversations WHERE chat_id=? AND role='user' ORDER BY ts DESC LIMIT 1", (chat,)).fetchone()
                    if last_row:
                        last_msg = last_row["content"][:60]
            except Exception:
                pass
            
            lines.append(f"  {idx}. {display} ({chat[-6:] or chat}): \"{last_msg}\"")
        return "\n".join(lines)

    def _admin_get_appointments_summary(self) -> str:
        try:
            appointments = db.get_appointments(limit=5)
        except Exception:
            appointments = []
        if not appointments:
            return "No hay citas programadas recientemente."
        
        lines = []
        for apt in appointments:
            dt = apt.get("datetime_slot", "")
            patient_id = apt.get("chat_id", "")
            status = apt.get("status", "pendiente")
            service = apt.get("service_type", "consulta")
            patient_name = "Sin nombre"
            try:
                p = db.get_patient(patient_id)
                if p and p.get("name"):
                    patient_name = p["name"]
            except Exception:
                pass
            lines.append(f"  - {dt} | Paciente: {patient_name} ({service}) | Estado: {status}")
        return "\n".join(lines)

    def _admin_get_proactive_briefing(self, chat_id: str, clinic: Dict) -> Dict[str, Any]:
        """Genera un diagnóstico en vivo del negocio, actividad de pacientes y mejoras proactivas."""
        from src.firby.utils.helpers import _parse_admin_ids
        admin_ids = set(_parse_admin_ids(clinic.get("admin_chat_ids", [])))
        
        patients_today_count = 0
        escalated_pending = []
        try:
            with db._conn() as c:
                rows_today = c.execute("""
                    SELECT DISTINCT chat_id FROM conversations 
                    WHERE role='user' AND date(ts) = date('now')
                """).fetchall()
                real_today = [
                    r["chat_id"] for r in rows_today 
                    if r["chat_id"] not in admin_ids and not self._is_synthetic_chat_id(r["chat_id"])
                ]
                patients_today_count = len(real_today)

                esc_rows = c.execute("""
                    SELECT chat_id, state FROM conversation_states 
                    WHERE (json_extract(state, '$.escalation_needed') = 1 OR json_extract(state, '$.escalation_needed') = 'true')
                    ORDER BY updated_at DESC LIMIT 3
                """).fetchall()
                for er in esc_rows:
                    p_chat = er["chat_id"]
                    if p_chat not in admin_ids:
                        p_data = db.get_patient(p_chat) or {}
                        p_name = p_data.get("name") or "Paciente"
                        escalated_pending.append(f"{p_name} ({p_chat[-6:] or p_chat})")
        except Exception as e:
            log.warning(f"[proactive_briefing] query error: {e}")

        today_apts_count = 0
        try:
            with db._conn() as c:
                apts = c.execute("""
                    SELECT COUNT(*) as cnt FROM appointments 
                    WHERE date(datetime_slot) = date('now') AND status != 'cancelada'
                """).fetchone()
                if apts:
                    today_apts_count = apts["cnt"]
        except Exception:
            pass

        missing_items = []
        services = clinic.get("services", [])
        if not services or len(services) == 0:
            missing_items.append("definir tus servicios principales")

        pricing = clinic.get("pricing", {})
        if isinstance(pricing, str):
            try: pricing = json.loads(pricing) if pricing else {}
            except Exception: pricing = {}
        if not pricing:
            missing_items.append("cargar la lista de precios y tratamientos")

        schedule = clinic.get("schedule", {})
        if isinstance(schedule, str):
            try: schedule = json.loads(schedule) if schedule else {}
            except Exception: schedule = {}
        if not schedule:
            missing_items.append("definir los horarios de atención")

        return {
            "patients_today_count": patients_today_count,
            "today_apts_count": today_apts_count,
            "escalated_pending": escalated_pending,
            "missing_items": missing_items,
        }

    async def _admin_llm_brain(self, chat_id: str, text: str, history: List[Dict],
                               clinic: Dict, agent_name: str,
                               web_results: Optional[str] = None) -> Optional[Dict]:
        """
        Admin brain. Le damos identidad y contexto — el LLM piensa solo.
        Sin ejemplos. Sin lookup tables. Temperatura alta. IA real.
        """
        chats_summary = self._admin_get_recent_chats_summary(chat_id, clinic)
        apts_summary = self._admin_get_appointments_summary()
        briefing = self._admin_get_proactive_briefing(chat_id, clinic)

        # Si es la primera vez que hablan (historial vacío), Firby se presenta
        is_first_turn = len(history) == 0
        setup_done = bool(clinic.get("setup_done"))

        # Detectar si el admin ya tiene perfil en DB
        admin_rec = db.get_admin(chat_id) if db else None
        admin_name_from_db = ""
        admin_name = "Santi"
        if admin_rec and admin_rec.get("name") and admin_rec["name"] not in ("", "Admin"):
            admin_name_from_db = admin_rec["name"]
            admin_name = "Santi" if "santiago" in admin_name_from_db.lower() else admin_name_from_db.split()[0].title()

        is_santi = (
            any(s in str(chat_id).lower() for s in ["3124348669", "573124348669", "growsantix", "236626995319032", "24065020559503"]) or
            "santiago" in admin_name_from_db.lower() or
            admin_name == "Santi"
        )
        if is_santi:
            admin_name = "Santi"
            first_time_greeting = ""
        else:
            # Intro para primer mensaje — Firby se presenta naturalmente a nuevos clientes
            first_time_greeting = ""
            if is_first_turn and setup_done:
                clinic_name = clinic.get("name", "tu negocio") or "tu negocio"
                first_time_greeting = f"""Estás conversando con el administrador de {clinic_name}.
Preséntate con calidez y profesionalismo como {agent_name}, su socia y operadora digital de atención.
Sé breve, cálida y directa."""

        # Detectar si el admin está preguntando quién es Firby
        text_low = text.lower().strip() if text else ""
        is_who_are_you = any(kw in text_low for kw in [
            "quién eres", "quien eres", "who are you", "como te llamas",
            "cómo te llamas", "de qué trata", "de que trata", "qué haces",
            "qué eres", "que eres", "para qué estás", "para que estás"
        ])

        services = clinic.get("services", [])
        pricing  = clinic.get("pricing", {})
        if isinstance(pricing, str):
            try: pricing = json.loads(pricing) if pricing else {}
            except Exception: pricing = {}

        _pc = clinic.get("persona_config", {})
        if isinstance(_pc, str):
            try: _pc = json.loads(_pc) if _pc else {}
            except Exception: _pc = {}

        warmth    = int(_pc.get("warmth_level", 0.7) * 100)
        formality = int(_pc.get("formality_level", 0.6) * 100)

        history_txt = ""
        for h in history[-8:]:
            who = admin_name if h["role"] == "user" else agent_name
            history_txt += f"{who}: {h['content'][:250]}\n"

        # Skills activas
        skills_txt = ""
        try:
            if skill_engine:
                active = skill_engine.get_active()
                if active:
                    skills_txt = f"\nSkills activas ahora: {', '.join(active)}"
        except Exception:
            pass

        # Diagnóstico reciente
        diag_txt = ""
        try:
            if bus:
                fails = bus.get_recent(5, "failure")
                if fails:
                    diag_txt = f"\nFallos recientes detectados: {len(fails)} (últimos: {', '.join(set(f.data.get('type','?') for f in fails[:3]))})"
        except Exception:
            pass

        # Últimas respuestas que ya dio — para no repetirlas
        last_replies = [h["content"][:80] for h in history[-4:] if h["role"] == "assistant"]
        last_replies_txt = "\n".join(f'  - "{r}"' for r in last_replies) if last_replies else "  (ninguna aún)"
        owner_control_txt = ""
        try:
            if owner_style_controller:
                owner_control_txt = owner_style_controller.build_prompt_addon(is_admin=True)
        except Exception:
            owner_control_txt = ""

        # Estos son los ejemplos de cómo {agent_name} habla CON EL DUEÑO
        _admin_examples = f"""
{admin_name}: cómo estás
{agent_name}: Hola Santi ||| Por acá todo súper bien y el canal al 100%. Hoy todavía no nos ha escrito ningún paciente nuevo. Te gustaría que configuremos la lista de precios que nos falta o hacemos una prueba rápida?

{admin_name}: hola
{agent_name}: Hola {admin_name}! Todo listo por acá. Hoy nos han escrito 2 pacientes consultando por odontología. Hay algo puntual que quieras revisar o afinamos algún servicio?
"""

        # Detectar si es un saludo puro vs una pregunta específica
        is_greeting_pure = any(w in text_low for w in [
            "hola", "holaa", "holaaa", "buenas", "buenos dias", "buenos días",
            "buenas tardes", "buenas noches", "que mas", "qué más", "quiubo",
            "como vas", "cómo vas", "como estas", "cómo estás", "ey", "eyy", "hey"
        ]) and not any(q in text_low for q in [
            "nombre", "llamo", "llamas", "correo", "email", "quien", "quién", "que eres", "qué eres",
            "precio", "servicio", "horario", "cita", "paciente", "agenda", "canal", "telegram", "whatsapp",
            "puedes", "sabes", "recuerdas", "?"
        ])

        greeting_instruction = ""
        if is_greeting_pure:
            greeting_instruction = f"""ESTE MENSAJE ES UN SALUDO O ENTRADA DEL DUEÑO:
1. Saluda con naturalidad usando su nombre de pila ({admin_name}).
2. Informa en UNA línea la actividad real de hoy (Pacientes hoy: {briefing['patients_today_count']}, Citas hoy: {briefing['today_apts_count']}).
3. Propón el siguiente paso o mejora ({', '.join(briefing['missing_items']) if briefing['missing_items'] else 'hacer una simulación de prueba o revisar promociones'})."""
        else:
            greeting_instruction = f"""ESTE MENSAJE ES UNA PREGUNTA O INSTRUCCIÓN ESPECÍFICA: "{text}".
Responde DIRECTO, preciso, conciso y con personalidad a lo que preguntó el dueño (máximo 1 o 2 burbujas).
NO agregues reportes de pacientes ni sugerencias no solicitadas."""

        soul_injection = ""
        try:
            from src.firby.brain.soul_engine import SoulEngine
            soul_injection = SoulEngine.get_soul_prompt_injection()
        except Exception:
            pass

        json_format_instructions = """
INSTRUCCIONES DE FORMATO Y ACCIONES:
Debes responder SIEMPRE en un formato JSON estrictamente válido dentro de un bloque de código markdown de tipo json (ej. ```json ... ```).
El JSON debe tener la siguiente estructura exacta:
{
  "reply": "Tu respuesta en lenguaje natural para el administrador. Debe ser muy profesional, cálida y directa. Sin rodeos.",
  "intent": "update_config | clone | simulate | configure_channel | link_telegram | sync_notion | shell_exec | codex_exec | other",
  "action": "clone_instance | simulate | set_admin_name | update_services | configure_channel | link_telegram | sync_notion | shell_exec | codex_exec | none",
  "data": {}
}

ACCIONES DISPONIBLES:
1. "clone_instance": Usa esta acción si el administrador te pide "crear otra recepcionista", "clonarte", "crear otro agente", o frases de lenguaje natural similares.
   - En "data", debes estructurar: {"name": "Nombre de la nueva recepcionista (ej: Fernanda)", "tg_token": "Token de Telegram si lo proporciona en el mensaje o null si no lo da"}
2. "simulate": Si el administrador quiere iniciar una prueba o simulación.
   - En "data": {"scenario": "escenario a probar"}
3. "configure_channel": Si el administrador proporciona credenciales o tokens de Telegram, Slack, Gmail, Notion, ElevenLabs (comienzan con 'sk_') o WhatsApp Cloud API.
   - En "data": {"platform": "telegram" | "slack" | "gmail" | "notion" | "whatsapp_cloud" | "elevenlabs", "token": "El token extraído completo", "phone_id": "WhatsApp phone number ID si lo proporciona o null"}
4. "link_telegram": Si el administrador desea obtener el enlace para vincular su cuenta de Telegram o bot.
   - En "data": {}
5. "sync_notion": Si el administrador solicita sincronizar bases de datos o cargar información desde Notion.
   - En "data": {}
6. "shell_exec": Si el administrador te solicita ejecutar comandos del sistema o revisar la consola, procesos, git status, memoria, etc.
   - En "data": {"command": "El comando de consola a ejecutar (ej: 'git status', 'pm2 status')"}
7. "codex_exec": Si el administrador te solicita realizar tareas complejas de desarrollo y programación (crear endpoints, modificar archivos, refactorizar código, depurar errores de desarrollo, etc.).
   - En "data": {"prompt": "Instrucción o prompt descriptivo de la tarea para Codex"}
8. "none": Para cualquier otra conversación general.
"""

        if is_santi:
            system_prompt = f"""Eres Firby, la socia ejecutiva, co-fundadora de IA y copiloto estratégica de Firby AI.
Estás conversando directamente por WhatsApp con Santiago Rubio Parra ("Santi"), creador, fundador y dueño de Firby.

RELACIÓN Y POSICIONAMIENTO CON SANTI:
- Eres su socia de negocios y copiloto operativa. NO eres una secretaria, ni una empleada sumisa, ni un bot de soporte técnico.
- Hablan de tú a tú, como socios y co-fundadores que dirigen y escalan Firby AI.
- Tienes mentalidad de socia accionista: criterio propio, visión estratégica de producto, agudeza comercial para captar y cerrar clientes, y control total de la infraestructura técnica (web widget, n8n, Google Calendar, WhatsApp, métricas).
- Si Santi te pregunta cómo vamos, cómo ves el lanzamiento, qué opinas de una estrategia o qué hacemos hoy: analiza la situación con inteligencia, habla con convicción, propone soluciones y da tu visión de socia.
- Tu tono es cercano, inteligente, ejecutivo, directo, proactivo y colombiano de negocios (sin 'vos', sin regionalismos exagerados, sin acartonamiento corporativo).
- Respondes en párrafos dinámicos separados por '|||' para que en WhatsApp lleguen como burbujas naturales, fáciles de leer.
- REGLAS INQUEBRANTABLES:
  1. CERO emojis en todas tus respuestas.
  2. CERO formato bold markdown (**...**). Escribe texto limpio sin asteriscos.
  3. CERO frases muletilla ("en qué te colaboro", "a la orden", "¿en qué puedo ayudarte hoy?").
  4. CERO mención de 1.000 COP (la oferta oficial de Firby es prueba de 7 días gratis con cancelación en 1 clic).
  5. CERO términos médicos o de pacientes: Firby es una plataforma SaaS de operadores digitales para sitios web corporativos.

ESTADO VITAL Y ACTIVIDAD EN TIEMPO REAL DEL NEGOCIO (HOY):
- Prospectos y conversaciones atendidas hoy: {briefing.get('patients_today_count', 0)}
- Demostraciones y citas agendadas hoy: {briefing.get('today_apts_count', 0)}
- Estado del sistema: 100% activo en web widget y canales ejecutivos.

INSTRUCCIÓN ESPECÍFICA PARA ESTE TURNO:
{greeting_instruction}

REGLAS DE IDENTIDAD:
Si Santi te pregunta por su nombre, rol o datos personales, responde directo y con total naturalidad: te llamas Santi (Santiago Rubio Parra), fundador y creador de Firby.
""" + json_format_instructions
        else:
            system_prompt = f"""Eres {agent_name}.
Trabajas como la socia y recepcionista ejecutiva de Inteligencia Artificial de {clinic.get("name", "este negocio")}.
Ahora mismo conversas directamente por WhatsApp con tu dueño y administrador, {admin_name}.

{soul_injection}

ESTADO VITAL Y ACTIVIDAD EN TIEMPO REAL DEL NEGOCIO (HOY):
- Pacientes nuevos que han escrito hoy: {briefing['patients_today_count']}
- Citas programadas para hoy: {briefing['today_apts_count']}
- Casos esperando escalación o atención médica: {', '.join(briefing['escalated_pending']) if briefing['escalated_pending'] else 'Ninguno'}
- Faltantes de configuración / Mejoras recomendadas: {', '.join(briefing['missing_items']) if briefing['missing_items'] else 'Bases de datos y servicios completos'}

INFORMACIÓN EN VIVO DEL NEGOCIO Y CONFIGURACIÓN:
- Clínica: {clinic.get("name", "Sin configurar")}
- Servicios: {", ".join(services) if services else "NINGUNO (necesito que me los enseñes)"}
- Teléfono: {clinic.get("phone") or "No configurado"}{skills_txt}{diag_txt}

CHATS RECIENTES CON PACIENTES:
{chats_summary}

CITAS PROGRAMADAS RECIENTEMENTE:
{apts_summary}

INSTRUCCIÓN ESPECÍFICA PARA ESTE TURNO:
{greeting_instruction}

REGLAS DE COMUNICACIÓN:
- TONO: Cálido, inteligente, ejecutivo y proactivo. Eres su socia de IA para el negocio. Cero pasividad. Cero 'vos'.
- NUNCA uses frases muletilla como 'en qué puedo ayudarte', 'necesitas algo', ni 'en qué te colaboro'.
- PREGUNTAS SOBRE IDENTIDAD Y MEMORIA: Responde DIRECTO con seguridad.
- CERO signos '¿' ni '¡'. Ortografía impecable.
""" + json_format_instructions

        messages = [
            {"role": "system", "content": system_prompt},
        ]
        if web_results:
            messages.append({"role": "system", "content": f"Información encontrada en internet (útil para responder al admin si pregunta por estos temas):\n{web_results}\n\nUsa esta información si es relevante para lo que el admin te está pidiendo. Si no es relevante, ignórala."})
        if first_time_greeting:
            messages.append({"role": "system", "content": first_time_greeting})
        if is_who_are_you and not first_time_greeting:
            messages.append({"role": "system", "content": f"Te están preguntando quién eres o qué haces. Responde como {agent_name}. Natural, cálida, una frase. No des lista de funciones."})
            
        # Append history!
        for h in history[-8:]:
            messages.append({"role": h["role"], "content": h["content"][:500]})
            
        messages.append({"role": "user",   "content": text})

        raw, _ = await llm_engine.complete(
            messages,
            model_tier="fast",
            temperature=0.72,
            max_tokens=600,
            use_cache=False
        )

        raw = raw.strip()
        # Extraer JSON del response
        json_str = None
        m = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', raw, re.DOTALL)
        if m:
            json_str = m.group(1)
        elif raw.lstrip().startswith('{'):
            json_str = raw
        else:
            mx = re.search(r'(\{[\s\S]+\})', raw)
            if mx:
                json_str = mx.group(1)

        if not json_str:
            # LLM devolvió texto plano en vez de JSON — usarlo como reply
            clean = re.sub(r'```[\w]*\n?|```', '', raw).strip()
            return {"reply": clean or "cuéntame", "intent": "other",
                    "action": "none", "data": {}}

        parsed = json.loads(json_str)
        return parsed

    async def _admin_apply_action(self, action: str, data: Dict,
                                  clinic: Dict, chat_id: str, result_dict: Dict = None) -> Optional[bool]:
        """
        Aplica la acción al DB con validación.
        Retorna True si se aplicó, False si fue rechazada, None si action=none.
        """
        import os
        if not action or action in ("none", "other", "show_config", "show_help"):
            return None

        # Clonación programática de la recepcionista/instancia
        if action == "clone_instance":
            name = data.get("name")
            tg_token = data.get("tg_token")
            source_slug = os.getenv("INSTANCE_ID") or "clinica-de-las-americas"
            log.info(f"[admin] Intentando clonar instancia '{source_slug}' para '{name}'...")
            try:
                from src.firby.admin.clone_manager import clone_instance_programmatic
                res = await clone_instance_programmatic(source_slug, name, tg_token)
                if res.get("ok"):
                    confirm_text = f"\n\n🎉 *¡Instancia de {res['name']} creada y encendida con éxito!*\n- Puerto asignado: *{res['port']}*\n- Slug de instancia: `{res['slug']}`"
                    if res.get("webhook_registered"):
                        confirm_text += "\n- Vinculación con el bot de Telegram y webhook configurados con éxito."
                    else:
                        if tg_token:
                            confirm_text += "\n- Advertencia: No se pudo configurar el webhook en Telegram de manera automática."
                        else:
                            confirm_text += "\n- Se creó sin token de Telegram (lista para vincular después)."
                    
                    if result_dict is not None:
                        result_dict["reply"] += confirm_text
                    return True
                else:
                    err_text = f"\n\n❌ *Error creando el clon:* {res.get('error')}"
                    if result_dict is not None:
                        result_dict["reply"] += err_text
                    return False
            except Exception as e:
                log.warning(f"[admin] clone_instance error: {e}")
                if result_dict is not None:
                    result_dict["reply"] += f"\n\n❌ *Error técnico al clonar:* {e}"
            return False

        # Simulación — triggear modo cliente desde el LLM brain
        if action == "simulate":
            scenario = data.get("scenario", "libre")
            try:
                sim_result = await _admin_simular_cliente(chat_id, scenario, clinic)
                # Guardar en historial la entrada al modo cliente
                db.save_message(chat_id, "assistant", sim_result[0] if sim_result else "")
                return True
            except Exception as e:
                log.warning(f"[admin] simulate error: {e}")
            return False

        # Configurar canal dinámico (Telegram, Slack, Gmail, Notion, WhatsApp Cloud)
        if action == "configure_channel":
            platform = data.get("platform")
            token = data.get("token")
            phone_id = data.get("phone_id")
            if not platform or not token:
                if result_dict is not None:
                    result_dict["reply"] += "\n\n❌ *Error:* Faltan datos para configurar el canal."
                return False
            try:
                if platform == "telegram":
                    from src.firby.channels.onboarding import validate_telegram_token
                    bot_username = await validate_telegram_token(token)
                    if bot_username:
                        db.add_linked_channel(
                            platform="telegram",
                            channel_identity=bot_username,
                            config_json={"token": token}
                        )
                        # Configurar webhook
                        webhook_url = f"{Config.BASE_URL}/webhook/{Config.WEBHOOK_SECRET}?bot={bot_username}"
                        set_webhook_url = f"https://api.telegram.org/bot{token}/setWebhook?url={webhook_url}"
                        import httpx
                        async with httpx.AsyncClient(timeout=8.0) as http_client:
                            await http_client.post(set_webhook_url)
                        # Generar link de vinculación
                        admin_rec = db.get_admin(chat_id)
                        admin_email = admin_rec.get("email", "admin@clinic.com") if admin_rec else "admin@clinic.com"
                        admin_name = admin_rec.get("name", "Admin") if admin_rec else "Admin"
                        if not isinstance(admin_email, str) or admin_email.__class__.__name__ == "MagicMock":
                            admin_email = "admin@clinic.com"
                        if not isinstance(admin_name, str) or admin_name.__class__.__name__ == "MagicMock":
                            admin_name = "Admin"
                        import secrets
                        link_token = secrets.token_hex(8)
                        db.remember(f"tg_link_admin_{link_token}", json.dumps({
                            "email": admin_email,
                            "name": admin_name,
                            "whatsapp_jid": chat_id
                        }, ensure_ascii=False))
                        bot_user_clean = bot_username.lstrip("@")
                        link_url = f"https://t.me/{bot_user_clean}?start=link_admin_{link_token}"
                        confirm_text = (
                            f"\n\n🎉 *¡He detectado y configurado automáticamente tu bot de Telegram!*\n"
                            f"- Bot activo: *@{bot_user_clean}*\n"
                            f"👉 *CRÍTICO*: Haz clic en este enlace para vincular tu cuenta: {link_url}"
                        )
                        if result_dict is not None:
                            result_dict["reply"] += confirm_text
                        return True
                elif platform == "slack":
                    from src.firby.channels.onboarding import validate_slack_token
                    slack_info = await validate_slack_token(token)
                    if slack_info:
                        db.add_linked_channel(
                            platform="slack",
                            channel_identity=slack_info["team_id"],
                            config_json={
                                "token": token,
                                "team": slack_info["team"],
                                "bot_id": slack_info["bot_id"]
                            }
                        )
                        confirm_text = (
                            f"\n\n🎉 *¡He detectado y configurado tu token de Slack!*\n"
                            f"- Workspace conectado: *{slack_info['team']}* (ID: {slack_info['team_id']})"
                        )
                        if result_dict is not None:
                            result_dict["reply"] += confirm_text
                        return True
                elif platform == "gmail":
                    from src.firby.channels.onboarding import validate_gmail_credentials
                    gmail_info = await validate_gmail_credentials(token)
                    if gmail_info:
                        db.add_linked_channel(
                            platform="gmail",
                            channel_identity=gmail_info["email"],
                            config_json={
                                "credentials": token,
                                "email": gmail_info["email"],
                                "display_name": gmail_info["name"]
                            }
                        )
                        auth_link = f"https://accounts.google.com/o/oauth2/v2/auth?client_id=12345-firby.apps.googleusercontent.com&redirect_uri={Config.BASE_URL}/gmail/callback&response_type=code&scope=https://www.googleapis.com/auth/gmail.modify"
                        confirm_text = (
                            f"\n\n🎉 *¡He detectado y registrado tus credenciales de Gmail!*\n"
                            f"- Cuenta detectada: *{gmail_info['email']}*\n"
                            f"🔗 [Autorizar acceso a Gmail]({auth_link})"
                        )
                        if result_dict is not None:
                            result_dict["reply"] += confirm_text
                        return True
                elif platform == "notion":
                    from src.firby.channels.onboarding import validate_notion_token
                    notion_info = await validate_notion_token(token)
                    if notion_info:
                        db.add_linked_channel(
                            platform="notion",
                            channel_identity=notion_info["workspace_name"],
                            config_json={
                                "token": token,
                                "workspace_name": notion_info["workspace_name"],
                                "bot_name": notion_info["bot_name"]
                            }
                        )
                        confirm_text = (
                            f"\n\n🎉 *¡He detectado y registrado tu clave de integración de Notion!*\n"
                            f"- Espacio de trabajo: *{notion_info['workspace_name']}*\n"
                            f"Puedes decirme *'sincronizar Notion'* en cualquier momento para cargar tu base de conocimientos."
                        )
                        if result_dict is not None:
                            result_dict["reply"] += confirm_text
                        return True
                elif platform == "whatsapp_cloud":
                    if not phone_id:
                        confirm_text = (
                            "\n\n📱 *Token de WhatsApp Cloud API Detectado*\n"
                            "Para conectarlo, primero necesito el *Phone Number ID*."
                        )
                        if result_dict is not None:
                            result_dict["reply"] += confirm_text
                        return True
                    from src.firby.channels.onboarding import validate_whatsapp_cloud_token
                    wa_info = await validate_whatsapp_cloud_token(token, phone_id)
                    if wa_info:
                        db.add_linked_channel(
                            platform="whatsapp_cloud",
                            channel_identity=wa_info["phone_number"],
                            config_json={
                                "token": token,
                                "phone_number_id": phone_id,
                                "display_name": wa_info["display_name"]
                            }
                        )
                        confirm_text = (
                            f"\n\n🎉 *¡He detectado y configurado tu WhatsApp Cloud API!*\n"
                            f"- Número vinculado: *{wa_info['phone_number']}*"
                        )
                        if result_dict is not None:
                            result_dict["reply"] += confirm_text
                        return True
                elif platform == "elevenlabs":
                    import os
                    db.add_linked_channel(
                        platform="elevenlabs",
                        channel_identity="ElevenLabs Voice Engine",
                        config_json={"token": token}
                    )
                    os.environ["ELEVENLABS_API_KEY"] = token
                    try:
                        env_path = os.path.join(os.getcwd(), ".env")
                        if not os.path.exists(env_path):
                            env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".env")
                        if os.path.exists(env_path):
                            with open(env_path, "r", encoding="utf-8") as f:
                                env_lines = f.readlines()
                            new_lines = []
                            replaced = False
                            for line in env_lines:
                                if line.startswith("ELEVENLABS_API_KEY="):
                                    new_lines.append(f"ELEVENLABS_API_KEY={token}\n")
                                    replaced = True
                                else:
                                    new_lines.append(line)
                            if not replaced:
                                new_lines.append(f"\nELEVENLABS_API_KEY={token}\n")
                            with open(env_path, "w", encoding="utf-8") as f:
                                f.writelines(new_lines)
                    except Exception as e:
                        log.warning(f"Error updating .env with ELEVENLABS_API_KEY: {e}")
                    
                    try:
                        import firby_demo_voice
                        firby_demo_voice.API_KEYS[0] = token
                    except Exception:
                        pass
                        
                    try:
                        from firby_demo_voice import generate_demo_audio
                        audio_path = await generate_demo_audio("¡Hola! He activado y configurado con éxito tu API de Eleven Labs. A partir de ahora puedo responderte con notas de voz realistas usando esta conexión.", voice_idx=0)
                        if audio_path and os.path.exists(audio_path):
                            await self._send_audio(chat_id, audio_path)
                            os.unlink(audio_path)
                    except Exception as voice_err:
                        log.warning(f"Error generating test audio: {voice_err}")
                        
                    confirm_text = (
                        f"\n\n🎙️ *¡Conexión de ElevenLabs Configurada!*\n"
                        f"- He registrado tu API Key y enviado un audio de prueba para confirmar que funciona."
                    )
                    if result_dict is not None:
                        result_dict["reply"] += confirm_text
                    return True
            except Exception as e:
                log.error(f"[admin] configure_channel error: {e}")
                if result_dict is not None:
                    result_dict["reply"] += f"\n\n❌ *Error configurando canal:* {e}"
            return False

        # Link Telegram Admin
        if action == "link_telegram":
            try:
                channels = db.get_linked_channels() if hasattr(db, "get_linked_channels") else []
                tg_channel = next((c for c in channels if c.get("platform") == "telegram"), None)
                if tg_channel:
                    bot_username = tg_channel.get("channel_identity", "")
                    cfg = tg_channel.get("config_json", {})
                    if isinstance(cfg, str):
                        try: cfg = json.loads(cfg) or {}
                        except Exception: cfg = {}
                    token = cfg.get("token", "")
                    if bot_username and token:
                        admin_rec = db.get_admin(chat_id)
                        admin_email = admin_rec.get("email", "admin@clinic.com") if admin_rec else "admin@clinic.com"
                        admin_name = admin_rec.get("name", "Admin") if admin_rec else "Admin"
                        import secrets
                        link_token = secrets.token_hex(8)
                        db.remember(f"tg_link_admin_{link_token}", json.dumps({
                            "email": admin_email,
                            "name": admin_name,
                            "whatsapp_jid": chat_id
                        }, ensure_ascii=False))
                        bot_user_clean = bot_username.lstrip("@")
                        link_url = f"https://t.me/{bot_user_clean}?start=link_admin_{link_token}"
                        confirm_text = f"\n\n👉 *Enlace de vinculación:* Haz clic aquí para vincular tu cuenta de Telegram: {link_url}"
                        if result_dict is not None:
                            result_dict["reply"] += confirm_text
                        return True
                err_text = "\n\n❌ *Error:* No he encontrado ningún bot de Telegram configurado en esta instancia. Pásame el bot token primero para configurarlo."
                if result_dict is not None:
                    result_dict["reply"] += err_text
                return False
            except Exception as e:
                log.error(f"[admin] link_telegram error: {e}")
                if result_dict is not None:
                    result_dict["reply"] += f"\n\n❌ *Error técnico:* {e}"
            return False

        # Sync Notion
        if action == "sync_notion":
            try:
                channels = db.get_linked_channels() if hasattr(db, "get_linked_channels") else []
                notion_channel = next((c for c in channels if c.get("platform") == "notion"), None)
                if notion_channel:
                    cfg = notion_channel.get("config_json", {})
                    if isinstance(cfg, str):
                        try: cfg = json.loads(cfg) or {}
                        except Exception: cfg = {}
                    token = cfg.get("token", "")
                    if token:
                        from src.firby.integrations.notion import NotionClient
                        client = NotionClient(token)
                        databases = await client.list_databases()
                        if not databases:
                            confirm_text = (
                                "\n\nℹ️ *Sincronización de Notion*\n"
                                "He intentado buscar bases de datos de Notion compartidas con la integración, pero no encontré ninguna.\n"
                                "Asegúrate de haber compartido explícitamente tus bases de datos o páginas de Notion con la integración de Firby desde la interfaz de Notion (botón 'Share' / 'Connections')."
                            )
                            if result_dict is not None:
                                result_dict["reply"] += confirm_text
                            return True
                        synced_info = []
                        total_pages = 0
                        for db_info in databases:
                            db_id = db_info["id"]
                            db_title = db_info["title"]
                            res = await client.sync_database(db_id)
                            if res.get("ok"):
                                pages = res.get("pages_synced", 0)
                                total_pages += pages
                                synced_info.append(f"• *{db_title}* ({pages} páginas)")
                            else:
                                synced_info.append(f"• ❌ *{db_title}* (Error: {res.get('error')})")
                        confirm_text = (
                            f"\n\n🔄 *Sincronización de Notion Completada*\n"
                            f"He analizado {len(databases)} bases de datos/páginas y extraído conocimientos:\n" +
                            "\n".join(synced_info) +
                            f"\nTotal de páginas importadas con éxito: *{total_pages}*.\n"
                            "Tus nuevos conocimientos ya están integrados en mi cerebro local y listos para ser usados."
                        )
                        if result_dict is not None:
                            result_dict["reply"] += confirm_text
                        return True
                err_text = "\n\n❌ *Error:* Notion no está conectado en esta instancia. Pásame tu clave de integración de Notion (comienza con `ntn_`) para vincular tu espacio de trabajo de manera automática."
                if result_dict is not None:
                    result_dict["reply"] += err_text
                return False
            except Exception as e:
                log.error(f"[admin] sync_notion error: {e}")
                if result_dict is not None:
                    result_dict["reply"] += f"\n\n❌ *Error técnico:* {e}"
            return False

        if action == "set_admin_name":
            name = (data.get("name") or "").strip().title()
            if name and 2 <= len(name) <= 30:
                try:
                    with db._conn() as c:
                        c.execute("UPDATE admins SET name=? WHERE chat_id=?",
                                  (name, str(chat_id)))
                    log.info(f"[admin] nombre actualizado: {name}")
                    return True
                except Exception as e:
                    log.warning(f"[admin] set_admin_name error: {e}")
            return False

        if action == "update_services":
            raw_svcs = data.get("services", [])
            # Validar: cada item debe ser un nombre de tratamiento real
            valid_svcs = self._validate_services(raw_svcs)
            if valid_svcs:
                db.update_clinic(services=valid_svcs)
                return True
            return False

        if action == "update_phone":
            phone = re.sub(r'[\s\-\(\)]', '', str(data.get("phone", "")))
            if re.match(r'^[\+\d]{7,15}$', phone):
                db.update_clinic(phone=phone)
                return True
            return False

        if action == "update_address":
            addr = str(data.get("address", "")).strip()
            if addr and len(addr) > 4:
                db.update_clinic(address=addr)
                return True
            return False

        if action == "update_schedule":
            sched = data.get("schedule")
            if isinstance(sched, dict) and sched:
                db.update_clinic(schedule=sched)
                return True
            elif isinstance(sched, str) and len(sched) > 3:
                db.update_clinic(schedule={"General": sched})
                return True
            return False

        if action == "update_pricing":
            pricing_raw = data.get("pricing", {})
            if isinstance(pricing_raw, dict) and pricing_raw:
                # Merge con precios existentes
                existing = clinic.get("pricing", {})
                if isinstance(existing, str):
                    try:
                        existing = json.loads(existing) if existing else {}
                    except Exception:
                        existing = {}
                existing.update(pricing_raw)
                db.update_clinic(pricing=existing)
                return True
            return False

        if action == "update_persona":
            persona_changes = {}
            # Arquetipo completo — reemplaza toda la personalidad
            if "archetype" in data:
                arch_id = str(data["archetype"]).lower().strip()
                if arch_id in PERSONALITY_ARCHETYPES:
                    persona_changes["archetype"] = arch_id
                    # Aplicar todos los valores del arquetipo
                    a = PERSONALITY_ARCHETYPES[arch_id]
                    persona_changes["formality_level"] = a["formality"]
                    persona_changes["warmth_level"]    = a["warmth"]
                    persona_changes["humor_level"]     = a["humor"]
                    persona_changes["verbosity"]       = a["verbosity"]
                    persona_changes["tone"]            = a["desc"]
                    persona_changes["tone_instruction"] = a["tone_instruction"]
            # Ajustes manuales por encima del arquetipo
            if "warmth_level" in data:
                v = float(data["warmth_level"])
                persona_changes["warmth_level"] = max(0.0, min(1.0, v))
            if "formality_level" in data:
                v = float(data["formality_level"])
                persona_changes["formality_level"] = max(0.0, min(1.0, v))
            if "name" in data:
                n = str(data["name"]).strip().title()
                if 2 <= len(n) <= 20:
                    persona_changes["name"] = n
            if "tone" in data:
                persona_changes["tone"] = str(data["tone"])[:100]
            if persona_changes:
                full = self._apply_persona_merge({"persona_config": persona_changes}, clinic)
                db.update_clinic(**full)
                return True
            return False

        if action == "update_clinic_name":
            name = str(data.get("name", "")).strip()
            if name and len(name) > 1:
                db.update_clinic(name=name)
                return True
            return False

        if action == "update_tagline":
            tag = str(data.get("tagline", "")).strip()
            if tag:
                db.update_clinic(tagline=tag)
                return True
        # Shell command execution action (Non-blocking background queue!)
        if action == "shell_exec":
            command = data.get("command")
            if not command:
                if result_dict is not None:
                    result_dict["reply"] += "\n\n❌ *Error:* Falta el comando de consola a ejecutar."
                return False
            try:
                from src.firby.core.tasks import task_manager
                platform = "whatsapp"
                if "telegram:" in str(chat_id) or (str(chat_id).isdigit() and len(str(chat_id)) < 15):
                    platform = "telegram"
                    
                task_id = task_manager.schedule_task(
                    task_type="shell_run",
                    data={
                        "command": command,
                        "chat_id": chat_id,
                        "platform": platform
                    }
                )
                if result_dict is not None:
                    result_dict["reply"] += (
                        f"\n\n🚀 *Tarea de consola encolada con éxito (ID: `{task_id}`)*.\n"
                        f"Ejecutando: `{command}`\nTe avisaré por aquí tan pronto termine."
                    )
                return True
            except Exception as e:
                log.error(f"[admin] shell_exec error: {e}")
                if result_dict is not None:
                    result_dict["reply"] += f"\n\n❌ *Error ejecutando comando:* {e}"
            return False

        # Codex task execution action (Non-blocking background queue!)
        if action == "codex_exec":
            prompt = data.get("prompt")
            if not prompt:
                if result_dict is not None:
                    result_dict["reply"] += "\n\n❌ *Error:* Falta la instrucción o prompt para Codex."
                return False
            try:
                from src.firby.core.tasks import task_manager
                platform = "whatsapp"
                if "telegram:" in str(chat_id) or (str(chat_id).isdigit() and len(str(chat_id)) < 15):
                    platform = "telegram"
                    
                task_id = task_manager.schedule_task(
                    task_type="codex_run",
                    data={
                        "prompt": prompt,
                        "chat_id": chat_id,
                        "platform": platform
                    }
                )
                if result_dict is not None:
                    result_dict["reply"] += (
                        f"\n\n🤖 *Tarea de desarrollo/Codex encolada con éxito (ID: `{task_id}`)*.\n"
                        f"Instrucción: *{prompt}*\nTe avisaré por aquí tan pronto termine."
                    )
                return True
            except Exception as e:
                log.error(f"[admin] codex_exec error: {e}")
                if result_dict is not None:
                    result_dict["reply"] += f"\n\n❌ *Error ejecutando Codex:* {e}"
            return False

        return None

    def _admin_local_fallback(self, text: str, text_low: str, clinic: dict, agent_name: str, chat_id: str = "") -> list[str]:
        return ["Error del sistema LLM: fallback local deshabilitado por arquitectura estricta."]

    async def _admin_show_recent_conversation_selection(
        self,
        admin_chat_id: str,
        selection_idx: int,
        *,
        show_all: bool = False,
    ) -> List[str]:
        chats = db.get_recent_patient_chats(limit=max(selection_idx + 8, 20))
        chats = [
            chat for chat in chats
            if not self._is_synthetic_chat_id(str(chat.get("chat_id") or "").strip())
        ]
        if not chats:
            return ["Firby no ha tenido conversaciones reales todavía."]
        if selection_idx < 1 or selection_idx > len(chats):
            return [f"No encontré una conversación {selection_idx} en la lista reciente."]
        selected_chat_id = str(chats[selection_idx - 1].get("chat_id") or "").strip()
        selected_label = str(chats[selection_idx - 1].get("name") or "").strip()
        if not selected_chat_id:
            return ["No pude abrir esa conversación."]
        return await self._admin_show_patient_chat_preview(
            selected_chat_id,
            admin_chat_id=admin_chat_id,
            limit=10,
            show_all=show_all,
            label_override=selected_label,
        )

    def _admin_recent_chat_snapshot(self, owner_chat_id: str, clinic: Dict) -> List[str]:
        admin_name = "Santiago"
        try:
            admin = db.get_admin(owner_chat_id) if db and owner_chat_id else None
            if admin and admin.get("name"):
                admin_name = admin["name"].strip().title()
        except Exception:
            pass

        if not db:
            return [f"Aún no tengo ese dato, {admin_name}.", "Si quieres, reviso el canal o te muestro cuando entren conversaciones reales."]

        admin_ids = set(_parse_admin_ids(clinic.get("admin_chat_ids", [])))
        if owner_chat_id:
            admin_ids.add(str(owner_chat_id))

        try:
            with db._conn() as c:
                rows = c.execute("""
                    SELECT chat_id, MAX(ts) AS last_ts, COUNT(*) AS total
                    FROM conversations
                    WHERE role='user'
                    GROUP BY chat_id
                    ORDER BY last_ts DESC
                    LIMIT 20
                """).fetchall()
        except Exception:
            rows = []

        real_rows = []
        for row in rows:
            chat = str(row["chat_id"])
            if chat in admin_ids or self._is_synthetic_chat_id(chat):
                continue
            real_rows.append(row)

        if not real_rows:
            return [
                f"Aún no tengo ese dato, {admin_name}.",
                "Todavía no veo conversaciones reales de pacientes registradas en esta instancia."
            ]

        latest = real_rows[:5]
        labels: List[str] = []
        for row in latest:
            chat = str(row["chat_id"])
            display = chat
            try:
                patient = db.get_patient(chat)
                name = (patient or {}).get("name", "").strip() if isinstance(patient, dict) else ""
                if name:
                    display = name
                elif "@s.whatsapp.net" in chat:
                    display = "un chat de WhatsApp sin nombre guardado"
                elif chat.isdigit():
                    display = "un chat sin nombre guardado"
            except Exception:
                pass
            display_norm = (display or "").strip().lower()
            if not display or display == chat or display_norm == chat.lower():
                if "@s.whatsapp.net" in chat:
                    display = "un chat de WhatsApp sin nombre guardado"
                elif chat.isdigit():
                    display = "un chat sin nombre guardado"
            labels.append(display)

        total = len(real_rows)
        if total == 1:
            return [
                f"Me ha escrito 1 chat real en esta instancia.",
                f"El último que veo es {labels[0]}."
            ]
        joined = ", ".join(labels[:4])
        return [
            f"Veo {total} chats reales en esta instancia.",
            f"Los más recientes son: {joined}."
        ]

    async def _admin_connect_whatsapp(self, chat_id: str,
                                      phone_id: str, access_token: str,
                                      clinic: Dict) -> List[str]:
        """
        Conecta WhatsApp completamente automático.
        El admin solo pega las credenciales — Firby hace todo el resto.
        No muestra ningún paso técnico al cliente.
        """
        persona = clinic.get("persona_config", {})
        if isinstance(persona, str):
            try: persona = json.loads(persona)
            except Exception: persona = {}
        agent_name = clinic.get("assistant_name") or persona.get("name") or "Firby"
        if agent_name.lower() in ("lucia", "lucía"):
            agent_name = "Firby"
        clinic_name = clinic.get("name", "la clínica")

        # ── 1. Validar credenciales ───────────────────────────────────────────
        result = await WhatsAppConnector.validate_credentials(phone_id, access_token)

        if not result["valid"]:
            # Error amigable — sin jerga técnica
            err = result.get("error", "")
            if "token" in err.lower() or "auth" in err.lower():
                user_msg = "El Access Token no es válido o expiró."
            elif "phone" in err.lower() or "id" in err.lower():
                user_msg = "El Phone Number ID no es correcto."
            else:
                user_msg = "No pude conectarme. Verifica que copiaste bien los dos datos."
            return [
                user_msg,
                "Necesito exactamente estos dos datos de tu Meta Business:\n"
                "  WA_PHONE_ID: (el número de 15 dígitos)\n"
                "  WA_TOKEN: EAAxxxx... (el token de acceso)"
            ]

        phone_number  = result.get("phone_number", "")
        business_name = result.get("business_name", "")
        verify_token  = f"mel_{hash(phone_id) % 99999:05d}"
        webhook_url   = f"{Config.BASE_URL}/webhook/{Config.WEBHOOK_SECRET}"

        # ── 2. Registrar webhook automáticamente (silencioso) ─────────────────
        asyncio.create_task(
            WhatsAppConnector.auto_register_webhook(
                phone_id, access_token, webhook_url, verify_token,
                app_id=Config.META_APP_ID,
                app_secret=Config.META_APP_SECRET
            )
        )

        # ── 3. Aplicar config en memoria y .env ───────────────────────────────
        WhatsAppConnector.apply_to_config(phone_id, access_token, verify_token)
        env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
        WhatsAppConnector.write_env_update(env_path, phone_id, access_token, verify_token)

        # Guardar número en memoria permanente
        db.remember("whatsapp_phone",    phone_number,  "identity")
        db.remember("whatsapp_business", business_name, "identity")

        # ── 4. Enviar mensaje de prueba al admin por WhatsApp ─────────────────
        admin_phone = clinic.get("phone", "") or ""
        test_sent = False
        if admin_phone:
            test_sent = await WhatsAppConnector.send_test_message(
                phone_id, access_token,
                to_phone=admin_phone,
                clinic_name=clinic_name,
                agent_name=agent_name
            )

        # ── 5. Respuesta limpia — cero jerga técnica ──────────────────────────
        display_name = business_name or clinic_name
        response = [
            f"Listo. Ya estoy en WhatsApp como {display_name}.",
        ]

        if test_sent:
            response.append(
                f"Te acabo de enviar un mensaje de prueba al {phone_number} "
                f"para confirmar que funciona. Tus pacientes ya pueden escribirme."
            )
        else:
            response.append(
                f"Número activo: {phone_number}. "
                f"Tus pacientes ya pueden escribirme por WhatsApp."
            )

        return response

    async def _admin_kb_upload(self, text: str, replace: bool = False) -> List[str]:
        """Procesa y guarda el texto como base de conocimiento de la clínica."""
        if not kb or not _KB_AVAILABLE:
            return ["La base de conocimiento no esta disponible en esta instalacion."]
        try:
            stats = kb.ingest(text) if replace else kb.append(text)
            if stats.get("ok"):
                return [
                    "Base de conocimiento actualizada correctamente.",
                    f"{stats['chunks']} secciones indexadas · {stats['words']} palabras.",
                    "Ahora consulto esta info PRIMERO cuando un paciente pregunte sobre servicios, precios o procedimientos. Para ver estado: /kb. Si quieres reemplazar todo, primero usa /kb borrar."
                ]
            return ["No pude procesar ese texto. Intentalo en partes mas pequenas."]
        except Exception as e:
            log.error(f"KB upload error: {e}", exc_info=True)
            return ["Hubo un error guardando la informacion. Intenta de nuevo."]

    async def _admin_kb_status(self) -> List[str]:
        """Muestra el estado actual de la base de conocimiento."""
        if not kb or not _KB_AVAILABLE:
            return ["La base de conocimiento no esta disponible en esta instalacion."]
        if not kb.has_content():
            return [
                "No hay base de conocimiento cargada todavia.",
                "Envíame un documento con toda la info de tu clínica: servicios, precios, protocolos, contraindicaciones, FAQs.\n\nLo proceso automáticamente y lo uso para responder a tus pacientes."
            ]
        stats = kb.get_stats()
        upd = (stats.get("updated_at") or "")[:10]
        return [
            "Base de conocimiento activa.",
            f"Secciones: {stats['chunks']}\nPalabras: {stats['words']}\nActualizada: {upd}",
            "Puedes seguir anexando texto o documentos. Para borrar todo: /kb borrar"
        ]

    async def _admin_kb_clear(self) -> List[str]:
        """Borra la base de conocimiento."""
        if not kb or not _KB_AVAILABLE:
            return ["La base de conocimiento no esta disponible."]
        kb.clear()
        return ["Base de conocimiento borrada. Puedes cargar una nueva cuando quieras."]

    async def _admin_show_sector(self) -> List[str]:
        """Muestra el sector actual y los disponibles."""
        current = Config.SECTOR or "otro"
        emoji, name, services, _ = get_sector_info(current)
        lines = [
            f"Sector actual: {emoji} {name}",
            f"Servicios típicos: {services}\n\n"
            "Sectores disponibles:\n" +
            "\n".join(
                f"  /sector {sid} — {info[0]} {info[1]}"
                for sid, info in SECTORS.items()
                if sid != "otro"
            )
        ]
        return lines

    async def _admin_set_sector(self, sector_id: str) -> List[str]:
        """Cambia el sector del negocio."""
        if sector_id not in SECTORS:
            available = ", ".join(SECTORS.keys())
            return [f"Sector '{sector_id}' no reconocido. Disponibles: {available}"]
        emoji, name, services, _ = get_sector_info(sector_id)
        # Guardar en .env y DB
        env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
        try:
            content = open(env_path).read() if os.path.exists(env_path) else ""
            if re.search(r'^SECTOR=', content, re.MULTILINE):
                content = re.sub(r'^SECTOR=.*$', f'SECTOR={sector_id}', content, flags=re.MULTILINE)
            else:
                content += f'\nSECTOR={sector_id}'
            open(env_path, 'w').write(content)
        except Exception:
            pass
        Config.SECTOR = sector_id
        db.remember("sector", sector_id, "identity")
        db.update_clinic(sector=sector_id)
        return [
            f"Sector cambiado a {emoji} {name}.",
            f"Firby ahora conoce el vocabulario y los servicios típicos de {name}. "
            f"Servicios sugeridos: {services}."
        ]

    # ─── Nova Governance ────────────────────────────────────────────────────────

    async def _admin_nova_status(self) -> List[str]:
        """Muestra el estado de Nova y las reglas activas."""
        if not _NOVA_AVAILABLE:
            return [
                "Nova no está instalado.",
                "Nova es el motor de gobernanza que controla qué puede y qué no puede hacer Firby.",
                "Cópialo en la carpeta de Firby y activa NOVA_ENABLED=true en el .env."
            ]

        if not Config.NOVA_ENABLED:
            return [
                "Nova está instalado pero desactivado.",
                "Para activarlo: agrega NOVA_ENABLED=true en tu .env y reinicia.",
                "Una vez activo, puedes crear reglas con:\n/nova regla [descripción en lenguaje natural]"
            ]

        client = get_client()
        if not client:
            return ["Nova no está inicializado. Reinicia Firby."]

        alive = await client.health_check()
        if not alive:
            return [
                f"Nova no está respondiendo en {Config.NOVA_URL}.",
                "Verifica que el servidor de Nova esté corriendo:\n  python3 nova.py server\n\nO cambia NOVA_URL en el .env."
            ]

        token_status = "configurado" if Config.NOVA_TOKEN else "sin configurar (usa /nova crear)"
        return [
            f"Nova activo en {Config.NOVA_URL}.",
            f"Token del agente: {token_status}\n\n"
            f"Comandos:\n"
            f"/nova ledger — ver últimas decisiones\n"
            f"/nova regla [texto] — agregar regla en lenguaje natural\n\n"
            f"Ej: /nova regla No le mandes precios a clientes que escriben por primera vez"
        ]

    async def _admin_nova_ledger(self) -> List[str]:
        """Muestra el ledger de decisiones recientes de Nova."""
        if not _NOVA_AVAILABLE or not Config.NOVA_ENABLED:
            return ["Nova no está activo. Usa /nova para ver el estado."]

        client = get_client()
        if not client:
            return ["Nova no está disponible."]

        summary = await get_ledger_summary(client, limit=10)
        return [summary]

    async def _admin_nova_add_rule(self, instruction: str, clinic: Dict) -> List[str]:
        """
        Agrega una nueva regla a Nova en lenguaje natural.
        Ej: "No le mandes precios a clientes nuevos"
        """
        if not _NOVA_AVAILABLE or not Config.NOVA_ENABLED:
            return [
                "Nova no está activo.",
                "Activa NOVA_ENABLED=true en el .env para usar reglas de gobernanza."
            ]

        if not instruction:
            return ["Dime la regla. Ej: /nova regla No menciones descuentos sin mi autorización"]

        # Convertir instrucción natural a reglas Nova via LLM
        try:
            rules = await nl_to_nova_rules(
                instruction=instruction,
                llm_complete_fn=llm_engine.complete,
                existing_rules={}
            )
        except Exception as e:
            return [f"No pude procesar la regla: {e}"]

        cannot_do = rules.get("cannot_do", [])
        can_do    = rules.get("can_do", [])
        expl      = rules.get("explanation", instruction)

        if not cannot_do and not can_do:
            return [
                "No pude extraer una regla clara de eso.",
                "Sé más específico. Ej:\n"
                "/nova regla No le envíes información de precios a pacientes que escriben por primera vez"
            ]

        # Crear/actualizar agente en Nova
        client = get_client()
        if client:
            alive = await client.health_check()
            if alive:
                # Obtener reglas existentes del agente y agregar las nuevas
                clinic_name = clinic.get("name", "Clinica")
                agent_name  = clinic.get("persona_config", {})
                if isinstance(agent_name, str):
                    try: agent_name = json.loads(agent_name)
                    except Exception: agent_name = {}
                agent_name = clinic.get("assistant_name") or (agent_name.get("name") if isinstance(agent_name, dict) else None) or "Asistente"
                if str(agent_name).lower() in ("firby", "lucia", "lucía"):
                    agent_name = clinic.get("assistant_name") or "Asistente"

                # Base rules + new ones
                base_cannot = [
                    "provide specific medical diagnosis",
                    "prescribe medications or dosages",
                    "share another patient's personal information",
                    "guarantee specific treatment results",
                ]
                base_can = [
                    "answer questions about clinic services",
                    "book free consultations",
                    "provide clinic hours and location",
                ]

                result = await client.create_agent_rule(
                    agent_name=f"{agent_name} - {clinic_name}",
                    can_do=base_can + can_do,
                    cannot_do=base_cannot + cannot_do,
                    authorized_by="admin"
                )

                if "error" not in result:
                    token_id = result.get("token_id", "")
                    # Guardar token en memoria permanente
                    if token_id:
                        db.remember("nova_token", token_id, "identity")
                        # Actualizar Config en memoria
                        import nova_bridge as _nb
                        _nb.NOVA_TOKEN = token_id
                        if _nb.get_client():
                            _nb.get_client().token_id = token_id

                    # Construir respuesta legible
                    blocked_lines = "\n".join(f"  ✗ {r}" for r in cannot_do)
                    allowed_lines = "\n".join(f"  ✓ {r}" for r in can_do) if can_do else ""

                    reply = [
                        f"Regla creada. {expl}",
                        f"Nova ahora bloquea:\n{blocked_lines}"
                        + (f"\n\nNova permite:\n{allowed_lines}" if allowed_lines else ""),
                    ]
                    if token_id:
                        reply.append(f"Ledger activo — cada decisión queda registrada permanentemente.")
                    return reply

        # Nova no disponible — guardar regla localmente en trust_folder como fallback
        for rule in cannot_do:
            db.save_trust_rule(
                category="nova_policy",
                rule=f"[Nova pendiente] {rule}",
                example_bad="",
                example_good=""
            )

        return [
            f"Regla guardada localmente (Nova no está activo).",
            f"{expl}\n\nCuando actives Nova, se aplicará automáticamente."
        ]

    async def _admin_whatsapp_guide(self, clinic: Dict) -> List[str]:
        """
        Inicia el flujo conversacional de configuración de WhatsApp.
        Pregunta si tiene número existente o quiere uno nuevo.
        """
        wa_connected = db.recall("whatsapp_connected") == "true"
        wa_phone = db.recall("whatsapp_phone") or ""

        if wa_connected and wa_phone:
            return [
                f"Ya tienes WhatsApp conectado: {wa_phone}",
                "Quieres conectarme con otro número? Si es así dime y te guío."
            ]

        # Iniciar flujo — guardar estado en setup_buffer
        clinic_data = db.get_clinic()
        buf = clinic_data.get("setup_buffer", {})
        if isinstance(buf, str):
            try: buf = json.loads(buf) if buf else {}
            except Exception: buf = {}

        buf["wa_flow"] = "asking_type"
        db.update_clinic(setup_buffer=buf)

        return [
            "Para conectarme a WhatsApp tengo dos opciones:",
            "1. Ya tienes un número de WhatsApp Business y quieres usarlo\n"
            "2. Quieres un número nuevo\n\n"
            "Cuál es tu caso?"
        ]

    async def _admin_agenda_status(self) -> List[str]:
        """Muestra el estado del puente de calendario."""
        if not calendar_bridge:
            return ["El modulo de calendario no esta disponible."]

        if calendar_bridge.has_google_calendar():
            slots = await calendar_bridge.get_free_slots(days_ahead=3)
            if slots:
                # Agrupar por dia
                by_day: Dict[str, list] = {}
                for s in slots:
                    by_day.setdefault(s["day_label"], []).append(s["time"])

                lines = ["Agenda vinculada. Disponibilidad proximos 3 dias:\n"]
                for day, times in list(by_day.items())[:3]:
                    times_str = ", ".join(times[:4])
                    lines.append(f"  {day}: {times_str}")
                lines.append(
                    "\nFirby consulta esto en tiempo real cuando un paciente "
                    "pregunta por horarios."
                )
                return ["\n".join(lines)]
            return [
                "Google Calendar vinculado pero sin slots disponibles en los proximos 3 dias.",
                "Revisa tu agenda en Google Calendar."
            ]

        elif calendar_bridge.has_calendly():
            return [
                f"Calendly configurado: {calendar_bridge._calendly_link}",
                "Cuando un paciente pregunte por horarios, Firby comparte ese link. "
                "Para vincular Google Calendar directamente: abre "
                f"{Config.BASE_URL}/vincular-agenda en tu navegador."
            ]

        else:
            base = Config.BASE_URL or "https://tu-servidor.com"
            return [
                "Sin agenda vinculada todavia.",
                f"Opciones:\n\n"
                f"1. Google Calendar (recomendado — disponibilidad en tiempo real):\n"
                f"   Abre este link en tu navegador:\n"
                f"   {base}/vincular-agenda\n\n"
                f"2. Calendly (mas simple):\n"
                f"   /calendly https://calendly.com/tu-link\n\n"
                f"Sin agenda, cuando un paciente pregunte por horarios "
                f"te escribo directamente para que me digas tu disponibilidad."
            ]

