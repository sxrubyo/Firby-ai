# -*- coding: utf-8 -*-
"""
Firby AI — ElevenLabs Speech Engine Integration.
Maneja el protocolo Upstream WebSocket para Custom LLM y streaming de voz en tiempo real.
"""
from __future__ import annotations

import os
import re
import json
import logging
import asyncio
from typing import Dict, Any, Optional, AsyncGenerator

import httpx
from fastapi import WebSocket, WebSocketDisconnect

log = logging.getLogger("firby.speech_engine")

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")
SPEECH_ENGINE_ID = os.getenv("ELEVENLABS_SPEECH_ENGINE_ID", "")
DEFAULT_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "cjVigY5qzO86Huf0OWal")  # Eric (Conversational, Spanish, Premade, 100% Free API)


class SpeechEngineManager:
    """Administrador de sesiones de voz y protocolo upstream para ElevenLabs."""

    def __init__(self):
        self.api_key = ELEVENLABS_API_KEY
        self.engine_id = SPEECH_ENGINE_ID
        self.default_voice_id = DEFAULT_VOICE_ID
        # Almacén de acciones pendientes por sesión para que el widget web las ejecute
        self.pending_actions: Dict[str, Any] = {}
        # Conexiones activas de clientes web suscritos a eventos de acción en vivo
        self.web_subscribers: Dict[str, list[WebSocket]] = {}

    def update_credentials(self, api_key: str, engine_id: Optional[str] = None):
        self.api_key = api_key
        if engine_id:
            self.engine_id = engine_id

    async def get_signed_url(self, agent_id: Optional[str] = None) -> Optional[str]:
        """Obtiene una signed_url efímera desde ElevenLabs para iniciar sesión en el cliente."""
        target_id = agent_id or self.engine_id
        url = f"https://api.elevenlabs.io/v1/convai/conversation/get_signed_url?agent_id={target_id}"
        headers = {"xi-api-key": self.api_key}

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(url, headers=headers)
                if resp.status_code == 200:
                    data = resp.json()
                    signed = data.get("signed_url")
                    log.info(f"[speech_engine] Signed URL generada con éxito para {target_id}")
                    return signed
                else:
                    log.error(f"[speech_engine] Error obteniendo signed URL ({resp.status_code}): {resp.text}")
                    return None
        except Exception as e:
            log.error(f"[speech_engine] Excepción obteniendo signed URL: {e}")
            return None

    async def register_web_subscriber(self, session_id: str, ws: WebSocket):
        """Registra un widget web para recibir eventos de acción en tiempo real sincronizados con la voz."""
        if session_id not in self.web_subscribers:
            self.web_subscribers[session_id] = []
        self.web_subscribers[session_id].append(ws)

    def unregister_web_subscriber(self, session_id: str, ws: WebSocket):
        if session_id in self.web_subscribers:
            if ws in self.web_subscribers[session_id]:
                self.web_subscribers[session_id].remove(ws)
            if not self.web_subscribers[session_id]:
                del self.web_subscribers[session_id]

    async def broadcast_action_to_web(self, session_id: str, action_data: Dict[str, Any]):
        """Envía la acción visual (scroll, highlight, modal) al widget del navegador en tiempo real."""
        subscribers = list(self.web_subscribers.get(session_id, []))
        if not subscribers and self.web_subscribers:
            # En entorno DEV, difundir a las sesiones web activas para sincronización instantánea
            for ws_list in self.web_subscribers.values():
                for ws in ws_list:
                    if ws not in subscribers:
                        subscribers.append(ws)

        for ws in subscribers:
            try:
                await ws.send_text(json.dumps({
                    "type": "firby_action",
                    "action": action_data
                }))
            except Exception as e:
                log.debug(f"[speech_engine] Error enviando acción a suscriptor: {e}")

    async def handle_upstream_connection(self, websocket: WebSocket):
        """
        Servidor del protocolo de transcripciones de ElevenLabs Speech Engine.
        ElevenLabs conecta a este endpoint y envía transcripts; Firby responde con agent_response en streaming.
        """
        await websocket.accept()
        log.info("[speech_engine] Conexión Upstream de ElevenLabs establecida.")
        conversation_id = "default"

        try:
            while True:
                raw_msg = await websocket.receive_text()
                try:
                    data = json.loads(raw_msg)
                except Exception:
                    continue

                msg_type = data.get("type")

                # 1. Evento Init
                if msg_type == "init":
                    conversation_id = data.get("conversation_id", "default")
                    log.info(f"[speech_engine] Sesión upstream iniciada: {conversation_id}")
                    continue

                # 2. Evento Ping / Pong
                elif msg_type == "ping":
                    event_id = data.get("event_id", 0)
                    await websocket.send_text(json.dumps({
                        "type": "pong",
                        "event_id": event_id
                    }))
                    continue

                # 3. Transcripción del usuario (Speech-to-Text completado por ElevenLabs)
                elif msg_type == "user_transcript":
                    event_id = data.get("event_id", 0)
                    user_raw = data.get("user_transcript")
                    user_text = ""
                    if isinstance(user_raw, list):
                        for m in reversed(user_raw):
                            if isinstance(m, dict) and m.get("role") == "user":
                                user_text = str(m.get("content") or "").strip()
                                break
                    elif isinstance(user_raw, str):
                        user_text = user_raw.strip()
                    elif isinstance(user_raw, dict):
                        user_text = str(user_raw.get("content") or "").strip()

                    log.info(f"[speech_engine] User transcript recibido ({conversation_id}): '{user_text}'")

                    if not user_text:
                        await websocket.send_text(json.dumps({
                            "type": "agent_response",
                            "content": "",
                            "event_id": event_id,
                            "is_final": True
                        }))
                        continue

                    # Ejecutar el cerebro de Firby (Widget Operator / LLM Runtime)
                    try:
                        from src.core.widget_operator import widget_operator
                        # Procesar con el motor cognitivo de Firby
                        result = await widget_operator.handle_message(
                            message=user_text,
                            user_id=f"voice_{conversation_id}",
                            org_id="firby_landing",
                            web_context={"current_url": "/"}
                        )

                        bubbles = result.get("bubbles") or []
                        full_speech = " ".join(bubbles).strip() if bubbles else (result.get("response") or "Entendido.").strip()
                        ui_action = result.get("ui_action") or result.get("action")
                        log.info(f"[speech_engine] Firby respuesta: '{full_speech}' | Acción UI: {ui_action}")

                        # Si hubo una acción visual (scroll, highlight), emitirla al navegador de inmediato
                        if ui_action:
                            await self.broadcast_action_to_web(conversation_id, ui_action)

                        # Transmitir el texto a ElevenLabs para sintetizar la voz
                        # Enviamos en pequeños fragmentos para que la síntesis empiece al instante
                        words = full_speech.split()
                        chunk_size = 4
                        for i in range(0, len(words), chunk_size):
                            chunk_text = " ".join(words[i:i + chunk_size]) + " "
                            await websocket.send_text(json.dumps({
                                "type": "agent_response",
                                "content": chunk_text,
                                "event_id": event_id,
                                "is_final": False
                            }))
                            await asyncio.sleep(0.02)  # Pequeño delay de fluidez

                        # Marcar finalización del turno
                        await websocket.send_text(json.dumps({
                            "type": "agent_response",
                            "content": "",
                            "event_id": event_id,
                            "is_final": True
                        }))

                    except Exception as e_proc:
                        log.error(f"[speech_engine] Error procesando transcript con Firby: {e_proc}", exc_info=True)
                        await websocket.send_text(json.dumps({
                            "type": "agent_response",
                            "content": "Comprendo su solicitud. Estoy verificando los datos en este momento.",
                            "event_id": event_id,
                            "is_final": True
                        }))

                # 4. Evento Close
                elif msg_type == "close":
                    log.info(f"[speech_engine] Sesión upstream cerrada por ElevenLabs: {conversation_id}")
                    break

        except WebSocketDisconnect:
            log.info(f"[speech_engine] WebSocket desconectado ({conversation_id})")
        except Exception as e:
            log.error(f"[speech_engine] Error en loop upstream: {e}", exc_info=True)
        finally:
            log.info("[speech_engine] Conexión upstream finalizada.")

    @staticmethod
    def transform_voice_tags(text: str) -> str:
        """
        Convierte tags de expresividad y modulación ([pauses], [chuckles], [deep breath], [sighs])
        en pausas acústicas reales (...), risa conversacional (jaja, ) y respiraciones humanas (uf...)
        para el motor neuronal ElevenLabs (voz de Rafa N), evitando que pronuncie palabras en inglés.
        """
        if not text:
            return ""
        # Eliminar cualquier residuo de pensamiento (Chain of Thought / Monólogo interno)
        from src.core.operator.runtime import DigitalWebOperatorRuntime
        t = DigitalWebOperatorRuntime._strip_thought_traces(text)
        t = t.strip()
        # Sonrisas y risa cómplice sutil
        t = re.sub(r'\[(?:chuckles|laughs|risas?|jeje|jaja)\]', 'jaja, ', t, flags=re.I)
        # Pausas reflexivas y silencios naturales
        t = re.sub(r'\[(?:pauses?|pausa|silence)\]', '... ', t, flags=re.I)
        # Respiraciones, tomas de aire y suspiros
        t = re.sub(r'\[(?:deep breath|respiraci[oó]n|sighs?|suspiro)\]', '... uf... ', t, flags=re.I)
        # Carraspeo o aclaración reflexiva
        t = re.sub(r'\[(?:clears throat|carraspeo)\]', '... a ver... ', t, flags=re.I)
        # Pensamiento o hesitación reflexiva
        t = re.sub(r'\[(?:thinking|pensando|thoughtful pause)\]', '... déjame ver... ', t, flags=re.I)
        # Limpieza de metadatos o tags de sistema que no deben pronunciarse
        t = re.sub(r'\[(?:CHIPS|ACTION)[^\]]*\]', '', t, flags=re.I)
        t = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', t)
        t = re.sub(r'\[[^\]]*\]', '', t)
        # Limpieza de markdown
        t = re.sub(r'[#*_`~]', '', t)
        # Normalizar pausas y espaciado
        t = re.sub(r'\s*\.\.\.\s*', '... ', t)
        t = re.sub(r'\s+', ' ', t).strip()
        return t

    async def stream_tts_audio(
        self,
        text: str,
        voice_id: Optional[str] = None
    ) -> AsyncGenerator[bytes, None]:
        """
        Sintetiza texto en voz en tiempo real con latencia ultra-baja (eleven_turbo_v2_5)
        y devuelve un generador asíncrono de chunks de audio MP3 para streaming directo al navegador.
        """
        processed_text = self.transform_voice_tags(text)
        if not processed_text:
            return

        target_voice = voice_id or self.default_voice_id
        fallback_voice = "cjVigY5qzO86Huf0OWal"

        key_pool = [k for k in [self.api_key, os.getenv("ELEVENLABS_API_KEY_2", "")] if k]

        params = {
            "optimize_streaming_latency": "3",
            "output_format": "mp3_44100_128"
        }
        payload = {
            "text": processed_text,
            "model_id": "eleven_turbo_v2_5",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75,
                "style": 0.0,
                "use_speaker_boost": True
            }
        }

        # Intentar síntesis con la voz solicitada o fallback en el pool de llaves
        for key in key_pool:
            for v_id in ([target_voice, fallback_voice] if target_voice != fallback_voice else [target_voice]):
                url = f"https://api.elevenlabs.io/v1/text-to-speech/{v_id}/stream"
                headers = {
                    "xi-api-key": key,
                    "Content-Type": "application/json"
                }
                try:
                    async with httpx.AsyncClient(timeout=15.0) as client:
                        async with client.stream("POST", url, headers=headers, params=params, json=payload) as resp:
                            if resp.status_code == 200:
                                async for chunk in resp.aiter_bytes():
                                    if chunk:
                                        yield chunk
                                return
                            else:
                                err_body = await resp.aread()
                                log.warning(f"[speech_engine] ElevenLabs TTS {resp.status_code} (voz={v_id}): {err_body.decode('utf-8', errors='ignore')[:100]}")
                except Exception as ex:
                    log.warning(f"[speech_engine] Excepción en stream TTS (voz={v_id}): {ex}")
                    continue


# Instancia global única
speech_engine = SpeechEngineManager()
