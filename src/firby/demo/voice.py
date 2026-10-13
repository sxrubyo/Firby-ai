# -*- coding: utf-8 -*-
"""
DemoVoiceService — Módulo especializado en la generación dinámica de notas de voz y síntesis con ElevenLabs.
"""
from __future__ import annotations
import re
import logging
from typing import Optional, Any, Callable

log = logging.getLogger("firby.demo.voice")

class DemoVoiceService:
    """Gestiona la generación de guiones dinámicos por LLM y el envío de audios."""

    def __init__(self, llm_engine: Any = None, send_audio_fn: Optional[Callable] = None):
        self.llm_engine = llm_engine
        self.send_audio_fn = send_audio_fn

    async def generate_and_send_voice_note(
        self,
        chat_id: str,
        clean_text_to_send: str,
        business_name: str = "",
        recording_action_fn: Optional[Callable] = None
    ) -> bool:
        """
        Genera una nota de voz dinámica y la despacha al usuario sin fallbacks estáticos.
        """
        try:
            # Si el texto para el audio es corto, generar un guion dinámico con LLM
            if len(clean_text_to_send.strip()) < 25 and self.llm_engine:
                try:
                    prompt = (
                        f"Genera una frase corta, amable y 100% natural en español explicando "
                        f"cómo ayudas al negocio '{business_name or 'tu empresa'}' a atender clientes "
                        f"y agendar citas por WhatsApp 24/7. Máximo 25 palabras. Directo y conversacional."
                    )
                    messages = [{"role": "user", "content": prompt}]
                    response_text, _ = await self.llm_engine.complete(messages, model_tier="fast", temperature=0.75, max_tokens=150)
                    if response_text and len(response_text.strip()) > 10:
                        clean_text_to_send = response_text.strip()
                except Exception as script_err:
                    log.warning(f"[demo_voice] Error generando guion dinámico por LLM: {script_err}")

            # Limpiar caracteres especiales para el motor TTS
            clean_text_to_send = re.sub(r"[^\w\s,.\?!áéíóúÁÉÍÓÚñÑ]", "", clean_text_to_send).strip()
            if not clean_text_to_send:
                return False

            # Acción de 'grabando audio...'
            if recording_action_fn:
                try:
                    await recording_action_fn(chat_id, duration_ms=5000)
                except Exception as rec_err:
                    log.debug(f"[demo_voice] Action recording error: {rec_err}")

            # Sintetizar audio con ElevenLabs
            from firby_demo_voice import generate_demo_audio
            audio_path = await generate_demo_audio(clean_text_to_send)

            if audio_path and self.send_audio_fn:
                await self.send_audio_fn(chat_id, audio_path)
                log.info(f"[demo_voice] Nota de voz enviada exitosamente a {chat_id} ({audio_path})")
                return True

        except Exception as e:
            log.warning(f"[demo_voice] Fallo en generación de nota de voz: {e}")

        return False
