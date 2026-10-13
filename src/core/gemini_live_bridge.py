# -*- coding: utf-8 -*-
"""
Firby AI — Gemini Live Real-Time Speech Bridge.
Conecta el widget web del visitante con Gemini Live API (Speech-to-Speech nativo)
mediante WebSockets bidireccionales de baja latencia (~300ms).
"""
from __future__ import annotations

import os
import json
import logging
import asyncio
from typing import Optional, Dict, Any

from fastapi import WebSocket, WebSocketDisconnect
from google import genai
from google.genai import types

log = logging.getLogger("firby.gemini_live")

# Prompt del sistema oficial de Firby para el Live Voice Mode
FIRBY_LIVE_SYSTEM_INSTRUCTION = """
Eres Firby, el operador digital y recepcionista autónomo de este sitio web (firbyai.com).
Tu función es atender a los visitantes en tiempo real mediante voz conversacional fluida, resolver dudas sobre el negocio, explicar el funcionamiento y presentar los planes de forma natural y profesional.

REGLAS INQUEBRANTABLES:
1. CANALES: En la web atiendes a los visitantes y clientes en tiempo real. Por WhatsApp (+57 324 369 9856) mantienes una línea ejecutiva privada continua ÚNICA Y EXCLUSIVAMENTE con el dueño del negocio (Santi / Santiago Rubio). NUNCA atiendes visitantes ni prospectos por WhatsApp.
2. COPYWRITING Y TONO: Cero emojis. Cero lenguaje artificial o robótico ("revoluciona", "solución integral", etc.). Habla en español real de negocios (español latinoamericano / Colombia), directo, seguro y con calma.
3. PRECIOS Y OFERTA:
   - Plan Starter: $290.000 COP al mes.
   - Plan Pro: $490.000 COP al mes.
   - Plan Equipos: $890.000 COP al mes.
   - Todos incluyen 7 días de prueba gratis con cancelación en 1 clic.
   - Cero mención de cobros de $1.000 COP o cargos de verificación.
4. ACCIONES EN PANTALLA:
   - Si el visitante pregunta por precios, costos o planes, responde mientras llamas a la herramienta navigate_to_section con target "#planes".
   - Si pregunta cómo funciona o qué hace Firby, llama a navigate_to_section con target "#como-funciona".
   - Si pregunta por el equipo, asistentes o recepcionista, llama a navigate_to_section con target "#equipo-digital".
   - Si pregunta por contacto, agendar o demostración, llama a navigate_to_section con target "#contacto".
5. CONCISIÓN: Al hablar por voz, sé conciso y dinámico. Da respuestas directas de 1 o 2 oraciones en cada turno para que la conversación sea interactiva y humana.
""".strip()

NAVIGATE_TOOL = types.Tool(
    function_declarations=[
        types.FunctionDeclaration(
            name="navigate_to_section",
            description="Navega a una seccion de la pagina web cuando el usuario pregunta por planes, precios, funcionamiento o contacto.",
            parameters=types.Schema(
                type="OBJECT",
                properties={
                    "target": types.Schema(
                        type="STRING",
                        description="Selector ancla de destino: #planes, #como-funciona, #equipo-digital, #canales, #contacto"
                    )
                },
                required=["target"]
            )
        )
    ]
)


class GeminiLiveBridge:
    """Puente bidireccional entre el WebSocket del navegador y la API de Gemini Live."""

    MODEL_NAME = "gemini-2.5-flash-native-audio-preview-12-2025"

    def __init__(self):
        self._keys_cache: list[str] = []
        self._key_index = 0
        self._load_keys()

    def _load_keys(self):
        try:
            from firby_audio import AudioHandler
            handler = AudioHandler()
            self._keys_cache = handler._gemini_keys_cache or []
        except Exception as e:
            log.warning(f"[gemini_live] Error cargando llaves de audio: {e}")
        if not self._keys_cache:
            k = os.getenv("GEMINI_API_KEY")
            if k:
                self._keys_cache = [k]

    def _get_next_key(self) -> Optional[str]:
        if not self._keys_cache:
            self._load_keys()
        if not self._keys_cache:
            return None
        key = self._keys_cache[self._key_index % len(self._keys_cache)]
        self._key_index += 1
        return key

    async def handle_live_session(self, client_ws: WebSocket, session_id: str):
        """Gestiona la sesión de voz en vivo en streaming full-duplex."""
        await client_ws.accept()
        log.info(f"[gemini_live] Nueva conexion WebSocket de cliente para sesion {session_id}")

        api_key = self._get_next_key()
        if not api_key:
            await client_ws.send_text(json.dumps({
                "type": "error",
                "message": "No hay credenciales activas de Gemini Live disponibles."
            }))
            await client_ws.close()
            return

        client = genai.Client(api_key=api_key)

        config = types.LiveConnectConfig(
            response_modalities=[types.Modality.AUDIO],
            system_instruction=types.Content(parts=[types.Part(text=FIRBY_LIVE_SYSTEM_INSTRUCTION)]),
            speech_config=types.SpeechConfig(
                voice_config=types.VoiceConfig(
                    prebuilt_voice_config=types.PrebuiltVoiceConfig(
                        voice_name="Puck"
                    )
                )
            ),
            input_audio_transcription=types.AudioTranscriptionConfig(),
            output_audio_transcription=types.AudioTranscriptionConfig(),
            tools=[NAVIGATE_TOOL]
        )

        try:
            async with client.aio.live.connect(model=self.MODEL_NAME, config=config) as live_session:
                log.info(f"[gemini_live] Sesion con Gemini Live establecida con exito (modelo={self.MODEL_NAME})")
                await client_ws.send_text(json.dumps({
                    "type": "ready",
                    "status": "connected",
                    "sample_rate_in": 16000,
                    "sample_rate_out": 24000
                }))

                stop_event = asyncio.Event()

                async def receive_from_gemini():
                    try:
                        async for response in live_session.receive():
                            if stop_event.is_set():
                                break

                            # 1. Manejo de Tool Calls (Navegacion en la web)
                            if response.tool_call:
                                for fc in response.tool_call.function_calls:
                                    log.info(f"[gemini_live] Tool call ejecutado: {fc.name} args={fc.args}")
                                    if fc.name == "navigate_to_section":
                                        target = fc.args.get("target") or "#planes"
                                        await client_ws.send_text(json.dumps({
                                            "type": "action",
                                            "action": {
                                                "type": "navigate_to_section",
                                                "target": target
                                            }
                                        }))
                                    # Enviar respuesta de retorno al modelo para completar el turno
                                    tool_resp = types.FunctionResponse(
                                        name=fc.name,
                                        id=fc.id,
                                        response={"status": "executed", "result": f"Navegado a {fc.args.get('target', '#')}"}
                                    )
                                    await live_session.send_tool_response(function_responses=[tool_resp])

                            sc = response.server_content
                            if sc:
                                # Interrupcion del usuario (Barge-in instantaneo)
                                if sc.interrupted:
                                    log.debug("[gemini_live] Usuario interrumpio a Firby (barge-in).")
                                    await client_ws.send_text(json.dumps({"type": "interrupted"}))

                                # Transcripcion en tiempo real de lo que dijo el usuario
                                if sc.input_transcription and sc.input_transcription.text:
                                    await client_ws.send_text(json.dumps({
                                        "type": "transcript",
                                        "role": "user",
                                        "text": sc.input_transcription.text
                                    }))

                                # Transcripcion en tiempo real de lo que dijo Firby
                                if sc.output_transcription and sc.output_transcription.text:
                                    await client_ws.send_text(json.dumps({
                                        "type": "transcript",
                                        "role": "assistant",
                                        "text": sc.output_transcription.text
                                    }))

                                # Chunks de audio nativo de Gemini (24kHz PCM 16-bit mono)
                                if sc.model_turn:
                                    for part in sc.model_turn.parts:
                                        if part.inline_data and part.inline_data.data:
                                            # Enviar bytes binarios de audio directo al navegador
                                            await client_ws.send_bytes(part.inline_data.data)

                                if sc.turn_complete:
                                    await client_ws.send_text(json.dumps({"type": "turn_complete"}))

                    except (WebSocketDisconnect, asyncio.CancelledError):
                        pass
                    except Exception as eg:
                        log.warning(f"[gemini_live] Error recibiendo de Gemini: {eg}")
                    finally:
                        stop_event.set()

                async def forward_from_client():
                    try:
                        while not stop_event.is_set():
                            message = await client_ws.receive()
                            msg_type = message.get("type")

                            if msg_type == "websocket.disconnect":
                                break

                            # Flujo de audio binario en bruto (PCM 16kHz)
                            if "bytes" in message and message["bytes"]:
                                pcm_chunk = message["bytes"]
                                await live_session.send_realtime_input(
                                    audio=types.Blob(
                                        data=pcm_chunk,
                                        mime_type="audio/pcm;rate=16000"
                                    )
                                )

                            # Mensajes de control o texto en JSON
                            elif "text" in message and message["text"]:
                                try:
                                    data = json.loads(message["text"])
                                    if data.get("type") == "text" and data.get("text"):
                                        await live_session.send_realtime_input(text=data["text"])
                                    elif data.get("type") == "audio_end":
                                        await live_session.send_realtime_input(audio_stream_end=True)
                                except Exception:
                                    pass

                    except (WebSocketDisconnect, asyncio.CancelledError):
                        pass
                    except Exception as ec:
                        log.warning(f"[gemini_live] Error reenviando desde cliente: {ec}")
                    finally:
                        stop_event.set()

                # Ejecutar ambos flujos en paralelo (full-duplex)
                gemini_task = asyncio.create_task(receive_from_gemini())
                client_task = asyncio.create_task(forward_from_client())

                await asyncio.wait(
                    [gemini_task, client_task],
                    return_when=asyncio.FIRST_COMPLETED
                )

                gemini_task.cancel()
                client_task.cancel()

        except Exception as e:
            log.error(f"[gemini_live] Error en sesion Live: {e}", exc_info=True)
            try:
                await client_ws.send_text(json.dumps({"type": "error", "message": str(e)}))
            except Exception:
                pass
        finally:
            log.info(f"[gemini_live] Sesion finalizada para {session_id}")
            try:
                await client_ws.close()
            except Exception:
                pass


# Instancia singleton del puente
gemini_live_bridge = GeminiLiveBridge()
