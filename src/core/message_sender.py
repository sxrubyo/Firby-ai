import os
import re
import json
import time
import random
import asyncio
import httpx
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional

from src.core.globals import _route_platform

log = logging.getLogger("firby")

class MessageSender:
    def __init__(self, config, db, demo_sessions=None, emoji_chats_off=None):
        self.config = config
        self.db = db
        self._chat_routes: Dict[str, Dict[str, Any]] = {}
        self._demo_sessions = demo_sessions if demo_sessions is not None else {}
        self._emoji_chats_off = emoji_chats_off if emoji_chats_off is not None else set()

    def _remember_route(self, chat_id: str, route: Optional[Dict[str, Any]] = None):
        if not route or not isinstance(route, dict):
            return
        clean = {
            "platform": route.get("platform") or self.config.PLATFORM,
            "channel_identity": route.get("channel_identity"),
            "seen_at": time.time(),
        }
        self._chat_routes[str(chat_id)] = clean
        try:
            if self.db:
                self.db.remember_contact_route(chat_id, clean["platform"], clean["channel_identity"])
        except Exception:
            pass

    def _resolve_route(self, chat_id: str, route: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        if route:
            self._remember_route(chat_id, route)
            return route
        remembered = self._chat_routes.get(str(chat_id))
        if remembered:
            return remembered
        try:
            if self.db:
                persisted = self.db.get_contact_route_details(chat_id)
                if persisted:
                    self._chat_routes[str(chat_id)] = persisted
                    return persisted
        except Exception:
            pass
        normalized_chat_id = str(chat_id or "").lower()
        if any(marker in normalized_chat_id for marker in (
            "@lid", "@s.whatsapp.net", "@g.us", "@broadcast",
        )):
            return {"platform": "whatsapp"}
        return {"platform": self.config.PLATFORM}

    async def _mark_read_action(self, chat_id: str, route: Optional[Dict[str, Any]] = None):
        """
        Marca visto el mensaje en WhatsApp enviando chulos azules en el momento natural.
        """
        try:
            route = self._resolve_route(chat_id, route)
            platform = _route_platform(route)
            if platform == "whatsapp" and self.config.WHATSAPP_BRIDGE_URL:
                async with httpx.AsyncClient(timeout=5.0) as client:
                    await client.post(
                        f"{self.config.WHATSAPP_BRIDGE_URL}/read",
                        json={"to": chat_id},
                        timeout=3.0
                    )
        except Exception as e:
            log.debug(f"[mark_read] error: {e}")

    async def _typing_action(
        self,
        chat_id: str,
        text: str = "",
        message_id: str = "",
        route: Optional[Dict[str, Any]] = None,
    ):
        """
        Indica 'escribiendo...' proporcional al texto que va a enviar.
        En WhatsApp Bridge también marca como leído si hay message_id.
        """
        try:
            route = self._resolve_route(chat_id, route)
            platform = _route_platform(route)
            # Duración proporcional: ~50ms por char, entre 1.5s y 8s
            chars    = len(text) if text else 60
            duration = max(1500, min(int(chars * 50), 8000))

            if platform == "telegram":
                tg_token = self.config.TELEGRAM_TOKEN
                if self.db:
                    channel_identity = route.get("channel_identity") if route else None
                    if channel_identity:
                        try:
                            with self.db._conn() as c:
                                row = c.execute(
                                    "SELECT config_json FROM linked_channels WHERE platform='telegram' AND channel_identity=? AND is_active=1",
                                    (channel_identity,)
                                ).fetchone()
                                if row:
                                    cfg = json.loads(row["config_json"]) if isinstance(row["config_json"], str) else row["config_json"]
                                    if cfg.get("token"):
                                        tg_token = cfg["token"]
                        except Exception as _re:
                            log.error(f"[Router] Error resolviendo token en typing: {_re}")
                async with httpx.AsyncClient(timeout=5.0) as client:
                    await client.post(
                        f"https://api.telegram.org/bot{tg_token}/sendChatAction",
                        json={"chat_id": chat_id, "action": "typing"}
                    )

            elif platform == "whatsapp_cloud":
                pass  # no soportado en API v17+

            elif platform == "evolution":
                if self.config.EVOLUTION_URL and self.config.EVOLUTION_API_KEY:
                    async with httpx.AsyncClient(timeout=5.0) as client:
                        await client.post(
                            f"{self.config.EVOLUTION_URL}/chat/sendPresence/{self.config.EVOLUTION_INSTANCE}",
                            headers={"apikey": self.config.EVOLUTION_API_KEY},
                            json={"number": chat_id, "presence": "composing", "delay": duration}
                        )

            elif platform == "whatsapp":
                if self.config.WHATSAPP_BRIDGE_URL:
                    async with httpx.AsyncClient(timeout=8.0) as client:
                        # Aparecer online PRIMERO — sin esto WhatsApp no muestra "escribiendo"
                        # y el mensaje llega con un solo chulo gris
                        try:
                            await client.post(
                                f"{self.config.WHATSAPP_BRIDGE_URL}/presence",
                                json={"status": "available", "timeout": 1800000},
                                timeout=3.0
                            )
                        except Exception:
                            pass
                        # Typing proporcional al mensaje
                        await client.post(
                            f"{self.config.WHATSAPP_BRIDGE_URL}/typing",
                            json={"to": chat_id, "duration": duration}
                        )
        except Exception:
            pass

    async def _recording_action(
        self,
        chat_id: str,
        duration_ms: int = 4000,
        route: Optional[Dict[str, Any]] = None,
    ):
        """
        Indica 'grabando audio...' ('recording_audio' / 'recording' / 'record_voice') en WhatsApp/Evolution/Telegram/Bridge.
        """
        try:
            route = self._resolve_route(chat_id, route)
            platform = _route_platform(route)

            if platform == "telegram":
                tg_token = self.config.TELEGRAM_TOKEN
                if self.db:
                    channel_identity = route.get("channel_identity") if route else None
                    if channel_identity:
                        try:
                            with self.db._conn() as c:
                                row = c.execute(
                                    "SELECT config_json FROM linked_channels WHERE platform='telegram' AND channel_identity=? AND is_active=1",
                                    (channel_identity,)
                                ).fetchone()
                                if row:
                                    cfg = json.loads(row["config_json"]) if isinstance(row["config_json"], str) else row["config_json"]
                                    if cfg.get("token"):
                                        tg_token = cfg["token"]
                        except Exception: pass
                async with httpx.AsyncClient(timeout=5.0) as client:
                    await client.post(
                        f"https://api.telegram.org/bot{tg_token}/sendChatAction",
                        json={"chat_id": chat_id, "action": "record_voice"}
                    )

            elif platform == "evolution":
                if self.config.EVOLUTION_URL and self.config.EVOLUTION_API_KEY:
                    async with httpx.AsyncClient(timeout=5.0) as client:
                        await client.post(
                            f"{self.config.EVOLUTION_URL}/chat/sendPresence/{self.config.EVOLUTION_INSTANCE}",
                            headers={"apikey": self.config.EVOLUTION_API_KEY},
                            json={"number": chat_id, "presence": "recording", "delay": duration_ms}
                        )

            elif platform == "whatsapp":
                if self.config.WHATSAPP_BRIDGE_URL:
                    async with httpx.AsyncClient(timeout=8.0) as client:
                        try:
                            await client.post(
                                f"{self.config.WHATSAPP_BRIDGE_URL}/presence",
                                json={"status": "available", "timeout": 1800000},
                                timeout=3.0
                            )
                        except Exception:
                            pass
                        await client.post(
                            f"{self.config.WHATSAPP_BRIDGE_URL}/typing",
                            json={"to": chat_id, "action": "recording", "presence": "recording", "duration": duration_ms}
                        )
        except Exception as e:
            log.debug(f"[recording_action] error: {e}")

    def sanitize_outgoing(self, text: Optional[str]) -> Optional[str]:
        """
        Sanitiza TODO mensaje saliente antes de enviarlo.
        Previene JSON bleed, debug messages y respuestas vacías.
        """
        if not text:
            return None
        t = text.strip()
        if not t:
            return None
        if t.startswith('{') or t.startswith('['):
            log.error(f"[sanitize] JSON bleed blocked: {t[:80]}")
            return None
        if '|||' in t:
            t = t.split('|||')[0].strip()
        internal_phrases = [
            "todavía no tengo este chat enlazado",
            "ya recibí tu mensaje",
            "no tengo este chat",
            "[error",
            "[internal",
            "{",
        ]
        if any(phrase in t.lower() for phrase in internal_phrases):
            log.error(f"[sanitize] internal debug message blocked: {t[:80]}")
            return None
        return t if t else None

    def _strip_emojis(self, text: str) -> str:
        """Elimina todos los emojis."""
        emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"
            "\U0001F300-\U0001F5FF"
            "\U0001F680-\U0001F6FF"
            "\U0001F1E0-\U0001F1FF"
            "\u2600-\u26FF"
            "\u2700-\u27BF"
            "]+",
            flags=re.UNICODE
        )
        return emoji_pattern.sub(r"", text)

    async def _send_audio(self, chat_id: str, audio_path: str, route: Optional[Dict[str, Any]] = None):
        """Send audio file as voice note via WhatsApp bridge."""
        route = self._resolve_route(chat_id, route)
        try:
            await self._recording_action(chat_id, duration_ms=4000, route=route)
            import base64

            with open(audio_path, "rb") as f:
                audio_b64 = base64.b64encode(f.read()).decode()
            async with httpx.AsyncClient(timeout=15.0) as client:
                r = await client.post(
                    f"{self.config.WHATSAPP_BRIDGE_URL}/send-audio",
                    json={"to": chat_id, "audioBase64": audio_b64, "ptt": True},
                )

                if r.status_code in (200, 201, 202):
                    log.info(f"[voice] audio sent to {chat_id[:10]}...")
                else:
                    log.warning(f"[voice] send failed: {r.status_code}")
        except Exception as e:
            log.debug(f"[voice] send_audio error: {e}")

    async def _send_message(self, chat_id: str, text: str, route: Optional[Dict[str, Any]] = None):
        """
        Envia mensaje al paciente/admin segun la plataforma configurada.
        Plataformas soportadas: telegram | whatsapp_cloud | evolution | whatsapp
        """
        text = self.sanitize_outgoing(text)
        if not text:
            return
        if chat_id in self._emoji_chats_off:
            text = self._strip_emojis(text)
        text = text.replace('\u00bf', '').replace('\u00a1', '').strip()  # ¿ ¡
        if not text:
            return

        route = self._resolve_route(chat_id, route)
        platform = _route_platform(route)
        channel_identity = route.get("channel_identity")

        tg_token = self.config.TELEGRAM_TOKEN
        slack_token = None
        
        if self.db:
            try:
                if platform == "telegram" and channel_identity:
                    with self.db._conn() as c:
                        row = c.execute(
                            "SELECT config_json FROM linked_channels WHERE platform='telegram' AND channel_identity=? AND is_active=1",
                            (channel_identity,)
                        ).fetchone()
                        if row:
                            cfg = json.loads(row["config_json"]) if isinstance(row["config_json"], str) else row["config_json"]
                            if cfg.get("token"):
                                tg_token = cfg["token"]
                
                if platform == "slack":
                    if channel_identity:
                        with self.db._conn() as c:
                            row = c.execute(
                                "SELECT config_json FROM linked_channels WHERE platform='slack' AND channel_identity=? AND is_active=1",
                                (channel_identity,)
                            ).fetchone()
                            if row:
                                cfg = json.loads(row["config_json"]) if isinstance(row["config_json"], str) else row["config_json"]
                                slack_token = cfg.get("token")
                    
                    if not slack_token:
                        with self.db._conn() as c:
                            row = c.execute(
                                "SELECT config_json FROM linked_channels WHERE platform='slack' AND is_active=1 LIMIT 1"
                            ).fetchone()
                            if row:
                                cfg = json.loads(row["config_json"]) if isinstance(row["config_json"], str) else row["config_json"]
                                slack_token = cfg.get("token")
            except Exception as _re:
                log.error(f"[Router] Error resolviendo token dinámico: {_re}")

        try:
            if platform == "telegram":
                if not tg_token:
                    log.error("[telegram] TELEGRAM_TOKEN no configurado")
                    return
                
                media_path = None
                if "/static/library/" in text:
                    for token_word in text.split():
                        if "/static/library/" in token_word:
                            clean_rel = token_word.strip("[]()'\" ")
                            possible_paths = [
                                Path("/home/ubuntu/firby/src/interfaces/web") / clean_rel.lstrip("/"),
                                Path("/home/ubuntu/firby/instances/clinica-de-las-americas") / clean_rel.lstrip("/"),
                                Path("/home/ubuntu/firby") / clean_rel.lstrip("/")
                            ]
                            for p in possible_paths:
                                if p.exists() and p.is_file():
                                    media_path = p
                                    break
                            if media_path:
                                break

                async with httpx.AsyncClient(timeout=20.0) as client:
                    if media_path and media_path.suffix.lower() in ('.png', '.jpg', '.jpeg', '.webp'):
                        with open(media_path, "rb") as f:
                            await client.post(
                                f"https://api.telegram.org/bot{tg_token}/sendPhoto",
                                data={"chat_id": chat_id, "caption": "📷 Recurso Adjunto de la Biblioteca"},
                                files={"photo": (media_path.name, f, "image/png")}
                            )
                    elif media_path and media_path.suffix.lower() in ('.pdf', '.doc', '.docx'):
                        with open(media_path, "rb") as f:
                            await client.post(
                                f"https://api.telegram.org/bot{tg_token}/sendDocument",
                                data={"chat_id": chat_id, "caption": "📄 Documento Adjunto de la Biblioteca"},
                                files={"document": (media_path.name, f, "application/pdf")}
                            )
                    else:
                        try:
                            res = await client.post(
                                f"https://api.telegram.org/bot{tg_token}/sendMessage",
                                json={"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}
                            )
                            if res.status_code >= 400:
                                await client.post(
                                    f"https://api.telegram.org/bot{tg_token}/sendMessage",
                                    json={"chat_id": chat_id, "text": text}
                                )
                        except Exception:
                            await client.post(
                                f"https://api.telegram.org/bot{tg_token}/sendMessage",
                                json={"chat_id": chat_id, "text": text}
                            )

            elif platform == "slack":
                if not slack_token:
                    log.error("[slack] slack_token no configurado")
                    return
                async with httpx.AsyncClient(timeout=15.0) as client:
                    r = await client.post(
                        "https://slack.com/api/chat.postMessage",
                        headers={
                            "Authorization": f"Bearer {slack_token}",
                            "Content-Type": "application/json; charset=utf-8"
                        },
                        json={"channel": chat_id, "text": text}
                    )
                    if r.status_code >= 400 or not r.json().get("ok"):
                        log.error(f"[slack] send error {r.status_code}: {r.text[:200]}")

            elif platform == "whatsapp_cloud":
                payload = {
                    "messaging_product": "whatsapp",
                    "recipient_type": "individual",
                    "to": chat_id,
                    "type": "text",
                    "text": {"preview_url": True, "body": text},
                }
                url = f"{self.config.WHATSAPP_CLOUD_URL}/{self.config.WHATSAPP_CLOUD_NUMBER_ID}/messages"
                headers = {
                    "Authorization": f"Bearer {self.config.WHATSAPP_CLOUD_TOKEN}",
                    "Content-Type": "application/json",
                }
                async with httpx.AsyncClient(timeout=10.0) as client:
                    r = await client.post(url, json=payload, headers=headers)
                    if r.status_code not in (200, 201):
                        log.error(f"[wa_cloud] error {r.status_code}: {r.text}")

            elif platform == "evolution":
                url = f"{self.config.EVOLUTION_URL}/message/sendText/{self.config.EVOLUTION_INSTANCE}"
                headers = {
                    "apikey": self.config.EVOLUTION_API_KEY,
                    "Content-Type": "application/json",
                }
                payload = {
                    "number": chat_id,
                    "text": text,
                    "options": {"delay": 1200, "presence": "composing", "linkPreview": True}
                }
                async with httpx.AsyncClient(timeout=15.0) as client:
                    r = await client.post(url, headers=headers, json=payload)
                    if r.status_code not in (200, 201):
                        log.error(f"[evolution] error {r.status_code}: {r.text}")

            elif platform == "whatsapp":
                if not self.config.WHATSAPP_BRIDGE_URL:
                    log.error("[wa_bridge] URL no configurada")
                    return
                async with httpx.AsyncClient(timeout=15.0) as client:
                    r = await client.post(
                        f"{self.config.WHATSAPP_BRIDGE_URL}/send",
                        json={"to": chat_id, "message": text, "text": text},
                    )
                    if r.status_code not in (200, 201):
                        log.warning(f"[wa_bridge] res {r.status_code}")

        except Exception as e:
            log.debug(f"[send_message] error: {e}")

    async def _send_library_media(
        self, chat_id: str, asset_id: str, route: Optional[Dict[str, Any]] = None
    ):
        """
        Resolve a [MEDIA:asset_id] tag to a real file and send it
        via the appropriate platform API (sendPhoto, sendVoice, sendDocument).
        """
        lib_path = Path("/home/ubuntu/firby/instances/clinica-de-las-americas/library.json")
        if not lib_path.exists():
            lib_path = Path("/home/ubuntu/firby/library.json")
        if not lib_path.exists():
            log.warning(f"[media_dispatch] library.json not found")
            return

        items = json.loads(lib_path.read_text())
        item = next((i for i in items if i.get("id") == asset_id), None)
        if not item:
            log.warning(f"[media_dispatch] asset '{asset_id}' not found in library.json")
            return

        rel_url = item.get("url", "")
        if not rel_url:
            return

        # Resolve file path
        possible_paths = [
            Path("/home/ubuntu/firby/instances/clinica-de-las-americas") / rel_url.lstrip("/"),
            Path("/home/ubuntu/firby/src/interfaces/web") / rel_url.lstrip("/"),
            Path("/home/ubuntu/firby") / rel_url.lstrip("/"),
        ]
        media_path = None
        for p in possible_paths:
            if p.exists() and p.is_file():
                media_path = p
                break
        if not media_path:
            log.warning(f"[media_dispatch] file not found for {rel_url}")
            return

        route = self._resolve_route(chat_id, route)
        platform = _route_platform(route)
        tg_token = self.config.TELEGRAM_TOKEN
        caption = item.get("name", "")
        suffix = media_path.suffix.lower()

        log.info(f"[media_dispatch] Sending {media_path.name} ({suffix}) to {chat_id} via {platform}")

        if platform == "telegram":
            async with httpx.AsyncClient(timeout=20.0) as client:
                if suffix in ('.png', '.jpg', '.jpeg', '.webp', '.gif'):
                    with open(media_path, "rb") as f:
                        await client.post(
                            f"https://api.telegram.org/bot{tg_token}/sendPhoto",
                            data={"chat_id": chat_id},
                            files={"photo": (media_path.name, f, f"image/{suffix.lstrip('.')}")}
                        )
                elif suffix in ('.ogg', '.oga', '.opus'):
                    with open(media_path, "rb") as f:
                        await client.post(
                            f"https://api.telegram.org/bot{tg_token}/sendVoice",
                            data={"chat_id": chat_id},
                            files={"voice": (media_path.name, f, "audio/ogg")}
                        )
                elif suffix in ('.mp3', '.m4a', '.wav'):
                    with open(media_path, "rb") as f:
                        await client.post(
                            f"https://api.telegram.org/bot{tg_token}/sendAudio",
                            data={"chat_id": chat_id},
                            files={"audio": (media_path.name, f, f"audio/{suffix.lstrip('.')}")}
                        )
                elif suffix in ('.pdf', '.doc', '.docx'):
                    with open(media_path, "rb") as f:
                        await client.post(
                            f"https://api.telegram.org/bot{tg_token}/sendDocument",
                            data={"chat_id": chat_id},
                            files={"document": (media_path.name, f, "application/octet-stream")}
                        )
                elif suffix in ('.mp4', '.mov', '.avi'):
                    with open(media_path, "rb") as f:
                        await client.post(
                            f"https://api.telegram.org/bot{tg_token}/sendVideo",
                            data={"chat_id": chat_id},
                            files={"video": (media_path.name, f, f"video/{suffix.lstrip('.')}")}
                        )
                else:
                    with open(media_path, "rb") as f:
                        await client.post(
                            f"https://api.telegram.org/bot{tg_token}/sendDocument",
                            data={"chat_id": chat_id},
                            files={"document": (media_path.name, f, "application/octet-stream")}
                        )
        elif platform in ("whatsapp", "evolution"):
            if suffix in ('.ogg', '.oga', '.opus', '.mp3', '.m4a', '.wav'):
                await self._send_audio(chat_id, str(media_path), route=route)
            else:
                hosted_url = f"https://firbyai.com{rel_url}"
                await self._send_message(chat_id, hosted_url, route=route)

    async def _send_bubbles(
        self,
        chat_id: str,
        bubbles: List[str],
        message_id: str = "",
        route: Optional[Dict[str, Any]] = None,
        user_text: str = "",
    ):
        """Envía burbujas con typing proporcional y pausas naturales."""
        route = self._resolve_route(chat_id, route)
        platform = _route_platform(route)
        is_wa = platform in ("whatsapp", "evolution")

        # Limpieza estricta de puntuación e imprecisiones de texto (Remover '¿', '¡' y artefactos visuales como '):*')
        try:
            from firby_nuke_robot_phrases import humanize_whatsapp_punctuation
            bubbles = [humanize_whatsapp_punctuation(b) for b in bubbles if humanize_whatsapp_punctuation(b)]
        except Exception:
            pass

        # ── 100x Audio Engine Activation (Demo & Production) ──────────
        _is_demo_active = False
        if self.db:
            try:
                _is_demo_active = self.db.recall(f"beta_demo_{chat_id}") == "true"
            except Exception:
                pass

        _is_voice_off = self._demo_sessions.get(f"demo_{chat_id}_voice_off", False)

        _has_eleven_key = bool(os.getenv("ELEVENLABS_API_KEY") or os.getenv("ELEVENLABS_API_KEY_2") or os.getenv("ELEVENLABS_API_KEY_3"))
        if not _has_eleven_key:
            try:
                from firby_voice import API_KEYS
                _has_eleven_key = any(k for k in API_KEYS if k)
            except Exception:
                pass

        if _has_eleven_key and not _is_voice_off and is_wa and bubbles:
            try:
                from firby_voice import generate_tts_audio, should_send_voice, inject_human_disfluencies
                history_len = len(self.db.get_history(chat_id)) if self.db else 0
                
                # Check if the user executed a reset command or explicitly requested voice
                _user_requested_voice = False
                _is_reset_cmd = False
                
                # Check user_text parameter directly (the actual incoming message!)
                _check_text = (user_text or "").strip().lower()
                if not _check_text and self.db:
                    _hist = self.db.get_history(chat_id, limit=3)
                    for _h in _hist:
                        if _h.get("role") == "user":
                            _check_text = _h.get("content", "").strip().lower()
                            break

                if _check_text:
                    if any(cmd in _check_text for cmd in ["reset", "resetear", "reiniciar", "limpiar", "salir", "demo beta", "/reset", "/salir", "/demobeta"]):
                        _is_reset_cmd = True
                    voice_keywords = [
                        "audio", "audios", "voz", "escuchar", "hablar", "nota de voz", "notas de voz", 
                        "otro", "otra", "hablado", "por voz", "por audio", "dilo", "[audio]", "[nota de voz]",
                        "mandame", "mándame", "envíame", "enviame", "manda", "envia", "hablando", "argentino", "escucharme"
                    ]
                    if any(w in _check_text for w in voice_keywords):
                        _user_requested_voice = True

                _full_joined_text = ". ".join(b.strip() for b in bubbles if b.strip())
                # Normalización fonética inmediata antes de cualquier limpieza de regex
                _full_joined_text = re.sub(r"\b24\s*/\s*7\b", "veinticuatro siete", _full_joined_text, flags=re.IGNORECASE)
                _full_joined_text = re.sub(r"\b24-7\b", "veinticuatro siete", _full_joined_text, flags=re.IGNORECASE)
                _full_joined_text = re.sub(r"\b100\s*%\b", "cien por ciento", _full_joined_text)
                _full_joined_text = re.sub(r"(\d+)\s*%", r"\1 por ciento", _full_joined_text)

                clean_voice_text = re.sub(r"[^\w\s,.\?!áéíóúÁÉÍÓÚñÑüÜ]", "", _full_joined_text).strip()
                _is_long_enough = len(clean_voice_text) >= 25

                # En DEMO_MODE, demo_handler.py maneja sus propios audios.
                # NO activar production_voice, pero SÍ continuar para enviar las burbujas de texto.
                _skip_production_voice = self.config.DEMO_MODE

                _is_initial_contact = any(_check_text.startswith(g) for g in ("heyy", "hey", "hola", "buenos dias", "buenas tardes", "buenas noches", "buenas")) or (history_len <= 2)
                _should_trigger_voice = not _skip_production_voice and (_user_requested_voice or (not _is_initial_contact and (_is_demo_active or (_is_long_enough and should_send_voice(_full_joined_text, history_len // 2, False)))))

                if not _is_reset_cmd and _should_trigger_voice:
                    try:
                        # 🟢 Pausa de Reacción Humana (1.8s - 2.8s) ANTES de mostrar 'Grabando audio...'
                        human_read_pause = round(random.uniform(1.8, 2.8), 2)
                        await asyncio.sleep(human_read_pause)

                        rec_ms = max(4000, min(14000, len(_full_joined_text) * 85))
                        await self._recording_action(chat_id, duration_ms=rec_ms, route=route)

                        voice_text_to_speak = _full_joined_text
                        clean_voice_text = inject_human_disfluencies(voice_text_to_speak, user_text=_check_text)
                        if len(clean_voice_text.strip()) >= 10:
                            audio_path = await generate_tts_audio(clean_voice_text, user_text=_check_text)
                            if audio_path:
                                try:
                                    await self._send_audio(chat_id, audio_path, route=route)
                                    log.info(f"[production_voice] Audio enviado con éxito a {chat_id}.")
                                    if _user_requested_voice:
                                        return
                                finally:
                                    if os.path.exists(audio_path):
                                        os.unlink(audio_path)
                    except Exception as _tts_err:
                        log.warning(f"[production_voice] Error generando/enviando audio: {_tts_err}, procediendo con texto")
            except Exception as e:
                log.debug(f"[production_voice] skipped: {e}")


        # 🟢 Pausa Humana de Lectura (1.8s) + Marcar VISTO (Chulos Azules) antes de Escribir
        if is_wa and bubbles:
            try:
                await asyncio.sleep(1.8)
                await self._mark_read_action(chat_id, route=route)
                await asyncio.sleep(0.8)
            except Exception:
                pass

        for i, bubble in enumerate(bubbles):
            if not bubble.strip():
                continue

            # ── Detect [MEDIA:xxx] tags in the bubble ──────────────────────
            media_ids = re.findall(r'\[MEDIA:([^\]]+)\]', bubble)
            clean_bubble = re.sub(r'\s*\[MEDIA:[^\]]+\]\s*', '', bubble).strip()
            
            # 🟢 Filtro de Ortografía Humana WhatsApp: Eliminar signos invertidos ¿ e ¡ y punto final frío
            if is_wa:
                clean_bubble = clean_bubble.replace("¿", "").replace("¡", "")
                if clean_bubble.endswith(".") and not clean_bubble.endswith("...") and not re.search(r'\b(dr|dra|sr|sra|etc)\.$', clean_bubble, re.I):
                    clean_bubble = clean_bubble[:-1].rstrip()

            # Typing proporcional al bubble + read receipt en primera burbuja
            mid = message_id if i == 0 else ""
            text_to_type = clean_bubble or bubble
            
            chars = len(text_to_type)
            typing_duration_s = max(1.5, min(chars * 0.05, 8.0))
            typing_time = chars / 38

            pause = max(
                typing_duration_s + 0.15,
                self.config.BUBBLE_PAUSE_MIN,
                min(typing_time + random.uniform(0.1, 0.5), self.config.BUBBLE_PAUSE_MAX + 0.8)
            )

            # 🟢 Heartbeat de Presencia Continuo: Mantiene "Escribiendo..." activo sin interrupciones hasta enviar
            async def _keep_presence_alive():
                end_time = time.time() + pause
                while time.time() < end_time:
                    try:
                        await self._typing_action(chat_id, text=text_to_type, message_id=mid, route=route)
                    except Exception:
                        pass
                    await asyncio.sleep(2.2)

            presence_task = asyncio.create_task(_keep_presence_alive())
            try:
                await asyncio.sleep(pause)
            finally:
                presence_task.cancel()

            # Send text (without the [MEDIA:] tag)
            if clean_bubble:
                await self._send_message(chat_id, clean_bubble, route=route)

            # Send each matched media file
            for media_id in media_ids:
                try:
                    await self._send_library_media(chat_id, media_id.strip(), route=route)
                except Exception as _media_err:
                    log.warning(f"[media_dispatch] error sending {media_id}: {_media_err}")

            if i < len(bubbles) - 1:
                inter_pause = random.uniform(1.4, 2.8) if is_wa else random.uniform(0.8, 1.8)
                await asyncio.sleep(inter_pause)

