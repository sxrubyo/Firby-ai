"""
Módulo de manejo de audio y transcripción de alta fidelidad para Firby.

Lógica de procesamiento:
1. Normalización de audio a WAV PCM 16kHz mono mediante ffmpeg (elimina inconsistencias de WebM/Opus).
2. Pool de credenciales Gemini (10 llaves activas con rotación round-robin y failover automático).
3. Transcripción estricta con gemini-2.5-flash y thinkingBudget=0 (elimina alucinaciones conversacionales).
4. Filtro de silencio y validación anti-alucinación.
5. Fallback ultrarrápido con Groq Whisper (whisper-large-v3-turbo, ~300ms).
6. Fallback secundario con OpenRouter Whisper.
"""
from __future__ import annotations

import base64
import os
import re
import subprocess
import tempfile
import logging
from typing import Optional, List, Tuple

import httpx

try:
    from firby_config import Config
except ImportError:
    class Config:
        TELEGRAM_TOKEN = ""
        WA_ACCESS_TOKEN = ""
        GEMINI_API_KEY = ""
        GEMINI_API_KEYS = []
        GROQ_API_KEY = ""
        OPENROUTER_API_KEY = ""

log = logging.getLogger("firby_audio")


class AudioHandler:
    """
    Manejador de audio y transcripción para Firby con pool multi-proveedor
    y prevención estricta de alucinaciones.
    """

    _gemini_keys_cache: Optional[List[str]] = None
    _gemini_key_index: int = 0
    _groq_key_cache: Optional[str] = None
    _openrouter_key_cache: Optional[str] = None

    def __init__(self):
        self._audio_cache: dict = {}
        self._ensure_keys_loaded()

    @classmethod
    def _ensure_keys_loaded(cls):
        """Carga y desduplica todas las credenciales disponibles en entorno y archivos .env."""
        if cls._gemini_keys_cache is None:
            raw_keys: List[str] = []

            # 1. Variables de entorno
            for i in range(1, 25):
                k = os.getenv("GEMINI_API_KEY" if i == 1 else f"GEMINI_API_KEY_{i}")
                if k and len(k) > 20 and k not in raw_keys:
                    raw_keys.append(k)

            # 2. Config de Python si existe
            if hasattr(Config, "GEMINI_API_KEYS") and Config.GEMINI_API_KEYS:
                for k in Config.GEMINI_API_KEYS:
                    if k and len(k) > 20 and k not in raw_keys:
                        raw_keys.append(k)
            if getattr(Config, "GEMINI_API_KEY", "") and Config.GEMINI_API_KEY not in raw_keys:
                raw_keys.append(Config.GEMINI_API_KEY)

            # 3. Escaneo de archivos .env
            env_paths = [
                "/home/ubuntu/firby/.env",
                "/home/ubuntu/firby/instances/production/.env",
                "/home/ubuntu/.hermes/.env"
            ]
            pat = re.compile(r"AIza[0-9A-Za-z_-]{35}")
            for ep in env_paths:
                if os.path.exists(ep):
                    try:
                        with open(ep, "r", encoding="utf-8") as f:
                            for m in pat.findall(f.read()):
                                if m not in raw_keys:
                                    raw_keys.append(m)
                    except Exception as e:
                        log.debug(f"[audio] Error leyendo {ep}: {e}")

            cls._gemini_keys_cache = raw_keys
            log.info(f"[audio] Pool de Gemini inicializado con {len(cls._gemini_keys_cache)} llaves.")

        if cls._groq_key_cache is None:
            groq_key = os.getenv("GROQ_API_KEY") or getattr(Config, "GROQ_API_KEY", "")
            if not groq_key:
                env_paths = [
                    "/home/ubuntu/firby/.env",
                    "/home/ubuntu/firby/instances/production/.env",
                    "/home/ubuntu/.hermes/.env"
                ]
                for ep in env_paths:
                    if os.path.exists(ep):
                        try:
                            with open(ep, "r", encoding="utf-8") as f:
                                m = re.search(r"GROQ_API_KEY\s*=\s*([^\s#]+)", f.read())
                                if m:
                                    groq_key = m.group(1).strip()
                                    break
                        except Exception:
                            pass
            cls._groq_key_cache = groq_key or ""
            if cls._groq_key_cache:
                log.info("[audio] Groq Whisper API key cargada con éxito.")

        if cls._openrouter_key_cache is None:
            or_key = os.getenv("OPENROUTER_API_KEY") or getattr(Config, "OPENROUTER_API_KEY", "")
            if not or_key:
                env_paths = [
                    "/home/ubuntu/.hermes/.env",
                    "/home/ubuntu/firby/.env",
                    "/home/ubuntu/firby/instances/production/.env"
                ]
                for ep in env_paths:
                    if os.path.exists(ep):
                        try:
                            with open(ep, "r", encoding="utf-8") as f:
                                m = re.search(r"OPENROUTER_API_KEY\s*=\s*([^\s#]+)", f.read())
                                if m:
                                    or_key = m.group(1).strip()
                                    break
                        except Exception:
                            pass
            cls._openrouter_key_cache = or_key or ""

    def _audio_suffix(self, mime: str) -> str:
        """Mapea mime type a extensión de archivo."""
        clean_mime = (mime or "").split(";")[0].strip().lower()
        mapping = {
            "audio/ogg": ".ogg",
            "audio/oga": ".ogg",
            "audio/opus": ".ogg",
            "audio/mp3": ".mp3",
            "audio/mpeg": ".mp3",
            "audio/wav": ".wav",
            "audio/x-wav": ".wav",
            "audio/mp4": ".m4a",
            "audio/x-m4a": ".m4a",
            "audio/webm": ".webm",
        }
        return mapping.get(clean_mime, ".webm")

    def _normalize_to_wav(self, audio_bytes: bytes, mime_type: str = "audio/webm") -> Optional[bytes]:
        """
        Normaliza cualquier flujo de audio (WebM, Opus, MP4, OGG) a WAV PCM 16kHz mono.
        Garantiza que Gemini y Whisper reciban muestras acústicas limpias sin problemas de decodificación.
        """
        if not audio_bytes or len(audio_bytes) < 80:
            return None

        # Auto-alineación para flujos WebM/Matroska u OGG que tengan offsets o paquetes residuales
        if b"\x1a\x45\xdf\xa3" in audio_bytes:
            idx = audio_bytes.find(b"\x1a\x45\xdf\xa3")
            if idx > 0:
                audio_bytes = audio_bytes[idx:]
        elif b"OggS" in audio_bytes:
            idx = audio_bytes.find(b"OggS")
            if idx > 0:
                audio_bytes = audio_bytes[idx:]

        suffix = self._audio_suffix(mime_type)
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as f_in:
            f_in.write(audio_bytes)
            in_path = f_in.name

        out_path = in_path + ".normalized.wav"
        try:
            cmd = [
                "ffmpeg", "-y", "-v", "error",
                "-i", in_path,
                "-ar", "16000",
                "-ac", "1",
                "-c:a", "pcm_s16le",
                "-f", "wav",
                out_path
            ]
            res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=8)
            if res.returncode != 0 or not os.path.exists(out_path):
                # Reintento con flags permisivos de contenedor streaming
                cmd_retry = [
                    "ffmpeg", "-y", "-v", "error",
                    "-fflags", "+nobuffer+igndts",
                    "-i", in_path,
                    "-ar", "16000",
                    "-ac", "1",
                    "-c:a", "pcm_s16le",
                    "-f", "wav",
                    out_path
                ]
                res = subprocess.run(cmd_retry, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=8)

            if res.returncode == 0 and os.path.exists(out_path):
                with open(out_path, "rb") as f_out:
                    data = f_out.read()
                    if len(data) > 200:
                        return data
        except Exception as e:
            log.warning(f"[audio] Error en normalización ffmpeg: {e}")
        finally:
            for p in (in_path, out_path):
                if os.path.exists(p):
                    try:
                        os.unlink(p)
                    except Exception:
                        pass
        return None

    def _has_voice_activity(self, audio_bytes: bytes) -> bool:
        """
        Filtro acústico VAD ultra-rápido en memoria (<1ms) para descartar silencios o ruido estático.
        Calcula la energía RMS del flujo PCM 16-bit 16kHz mono sin llamadas a disco ni APIs externas.
        """
        if not audio_bytes or len(audio_bytes) < 1600:
            return False
        try:
            import struct, math
            # Solo si tiene encabezado WAV (44 bytes), extraer la porción PCM y calcular RMS
            if not audio_bytes.startswith(b"RIFF"):
                return True
            pcm_data = audio_bytes[44:] if len(audio_bytes) > 44 else audio_bytes
            sample_count = len(pcm_data) // 2
            if sample_count < 800:
                return False
            samples = struct.unpack(f"<{sample_count}h", pcm_data[:sample_count * 2])
            sum_squares = sum(s * s for s in samples)
            rms = math.sqrt(sum_squares / sample_count)
            # Umbral de silencio acústico: debajo de 45 es silencio absoluto
            return rms > 45
        except Exception:
            return True

    def _is_hallucination_or_silence(self, text: str) -> bool:
        """Detecta si el texto devuelto es silencio o una alucinación conocida de contestador."""
        if not text:
            return True
        t = text.strip().lower()
        clean = re.sub(r"[\[\]\(\)\s_.:;¡!¿?]+", "", t)
        if clean in (
            "silencio", "sinaudio", "ruido", "gracias", "muchasgracias",
            "amaraorg", "subtitulosporlacomunidaddeamaraorg", "vacio", ""
        ):
            return True
        if "silencio" in clean or "sinaudio" in clean or "sin_audio" in clean or "sin-audio" in clean:
            return True
        prompt_hallucinations = (
            "firby", "santiago rubio", "santi", "firby santiago rubio santi",
            "firby santiago rubio", "santiago rubio santi", "firby santiago",
            "conversacion en espanol de colombia", "subtitulos realizados por",
            "transcripcion de audio en espanol latinoamericano",
            "transcripcion de audio en espanol"
        )
        clean_no_accents = clean.replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u")
        for ph in prompt_hallucinations:
            clean_ph = re.sub(r"[\[\]\(\)\s_.:;¡!¿?]+", "", ph)
            if clean_no_accents == clean_ph:
                return True
        return False

    async def transcribe_audio(
        self, 
        file_id: str, 
        platform: str = "telegram",
        wa_media_id: str = None
    ) -> str:
        """
        Transcribe audio con Whisper / Gemini Flash 2.5 (10 keys en rotación) con fallback automático.
        
        Args:
            file_id: ID del archivo de audio o 'wa_b64:<mime>:<data>'
            platform: Plataforma de origen (telegram, whatsapp, whatsapp_cloud, web)
            wa_media_id: ID de media de WhatsApp Cloud (si aplica)
            
        Returns:
            Texto transcrito o mensaje de error descriptivo
        """
        audio_bytes, mime_type = None, "audio/webm"
        
        try:
            # WhatsApp Bridge / Web Widget (audio base64 inline)
            if (platform in ("whatsapp", "web")) and file_id.startswith("wa_b64:"):
                try:
                    _, mime_part, b64_data = file_id.split(":", 2)
                    mime_type = mime_part or "audio/webm"
                    audio_bytes = base64.b64decode(b64_data)
                except Exception as eb64:
                    log.warning(f"[audio] Error decodificando base64: {eb64}")
                    return "[no pude escuchar, puedes escribirlo?]"

            elif platform == "telegram":
                async with httpx.AsyncClient(timeout=30.0) as client:
                    r = await client.get(
                        f"https://api.telegram.org/bot{Config.TELEGRAM_TOKEN}/getFile",
                        params={"file_id": file_id}
                    )
                    fp = r.json().get("result", {}).get("file_path", "")
                    if fp:
                        ext = fp.rsplit(".", 1)[-1].lower() if "." in fp else "ogg"
                        mime_type = {
                            "ogg": "audio/ogg", "mp3": "audio/mp3", "wav": "audio/wav",
                            "m4a": "audio/mp4", "oga": "audio/ogg", "opus": "audio/ogg"
                        }.get(ext, "audio/ogg")
                        ar = await client.get(
                            f"https://api.telegram.org/file/bot{Config.TELEGRAM_TOKEN}/{fp}"
                        )
                        audio_bytes = ar.content

            elif platform == "whatsapp_cloud" and wa_media_id:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    mr = await client.get(
                        f"https://graph.facebook.com/v20.0/{wa_media_id}",
                        headers={"Authorization": f"Bearer {Config.WA_ACCESS_TOKEN}"}
                    )
                    url = mr.json().get("url", "")
                    if url:
                        dl = await client.get(
                            url, 
                            headers={"Authorization": f"Bearer {Config.WA_ACCESS_TOKEN}"}
                        )
                        audio_bytes, mime_type = (
                            dl.content, 
                            mr.json().get("mime_type", "audio/ogg")
                        )

            if not audio_bytes or len(audio_bytes) < 150:
                log.info("[audio] Archivo de audio vacío o demasiado corto.")
                return "[no pude escuchar, puedes escribirlo?]"

            # Guardar copia para auditoría/debug de audio recibido
            try:
                with open("/tmp/last_received_audio.bin", "wb") as f_dbg:
                    f_dbg.write(audio_bytes)
            except Exception:
                pass

            # Normalizar audio a WAV PCM 16kHz mono para compatibilidad universal
            wav_bytes = self._normalize_to_wav(audio_bytes, mime_type)
            effective_bytes = wav_bytes if wav_bytes else audio_bytes
            effective_mime = "audio/wav" if wav_bytes else mime_type

            # Filtro acústico VAD en memoria: descarta silencios y ruido antes de invocar APIs externas
            if not self._has_voice_activity(effective_bytes):
                log.info("[audio] Filtro VAD: no se detectó actividad de voz en las muestras PCM.")
                return "[no pude escuchar, puedes escribirlo?]"

            # 1. Motor Primario: Groq Whisper Large V3 Turbo (ASR acústico especializado, ~300ms, cero alucinación LLM)
            whisper_result = await self._transcribe_groq_whisper(effective_bytes, effective_mime)
            if whisper_result and not self._is_hallucination_or_silence(whisper_result):
                log.info(f"[audio] Transcripción exitosa (Groq Whisper): {whisper_result[:80]}")
                return whisper_result

            # 2. Motor Secundario: OpenRouter Whisper
            openrouter_result = await self._transcribe_openrouter_whisper(effective_bytes, effective_mime)
            if openrouter_result and not self._is_hallucination_or_silence(openrouter_result):
                log.info(f"[audio] Transcripción exitosa (OpenRouter Whisper): {openrouter_result[:80]}")
                return openrouter_result

            # 3. Motor Terciario de contingencia: Gemini 2.5 Flash (pool multi-key)
            gemini_result = await self._transcribe_gemini(effective_bytes, effective_mime)
            if gemini_result and not self._is_hallucination_or_silence(gemini_result):
                log.info(f"[audio] Transcripción exitosa (Gemini 2.5 Flash contingencia): {gemini_result[:80]}")
                return gemini_result

            # Si Whisper o Gemini detectaron silencio explícito
            if (whisper_result and self._is_hallucination_or_silence(whisper_result)) or \
               (gemini_result and self._is_hallucination_or_silence(gemini_result)):
                log.info("[audio] Silencio o ruido de fondo detectado.")
                return "[no pude escuchar, puedes escribirlo?]"

            return "[no se pudo transcribir el audio]"

        except Exception as e:
            log.error(f"[audio] Error general en transcripción: {e}", exc_info=True)
            return "[no pude escuchar, puedes escribirlo?]"

    async def _transcribe_gemini(self, audio_bytes: bytes, mime_type: str) -> Optional[str]:
        """Transcribe usando Gemini Flash con rotación en el pool de llaves."""
        self._ensure_keys_loaded()
        keys = self._gemini_keys_cache or []
        if not keys:
            log.warning("[audio] No hay claves de Gemini disponibles.")
            return None

        clean_mime = (mime_type or "audio/wav").split(";")[0].strip().lower()
        effective_mime = "audio/wav" if "wav" in clean_mime else clean_mime
        b64 = base64.b64encode(audio_bytes).decode()

        strict_prompt = (
            "Eres un sistema de reconocimiento automático de voz (ASR) de máxima precisión acústica. "
            "Escucha atentamente el audio en español latinoamericano. "
            "Transcribe exactamente cada palabra o frase pronunciada en el audio sin omitir ni inventar nada. "
            "Si el audio contiene únicamente silencio absoluto, ruido de fondo, estática o sonido ininteligible sin voz humana, responde exactamente: [SILENCIO]. "
            "No agregues explicaciones, no inventes palabras, no respondas a las preguntas del audio y no agregues saludos. "
            "Devuelve estrictamente el texto literal pronunciado."
        )

        payload = {
            "contents": [{
                "parts": [
                    {"inline_data": {"mime_type": effective_mime, "data": b64}},
                    {"text": strict_prompt}
                ]
            }],
            "generationConfig": {
                "temperature": 0.0,
                "maxOutputTokens": 300,
                "thinkingConfig": {"thinkingBudget": 0}
            }
        }

        total_keys = len(keys)
        for attempt in range(total_keys):
            idx = (AudioHandler._gemini_key_index + attempt) % total_keys
            gkey = keys[idx]
            kid = f"KEY_{idx+1:02d}"

            try:
                async with httpx.AsyncClient(timeout=18.0) as client:
                    resp = await client.post(
                        f"https://generativelanguage.googleapis.com/v1beta/models/"
                        f"gemini-2.5-flash:generateContent?key={gkey}",
                        json=payload
                    )

                if resp.status_code == 200:
                    AudioHandler._gemini_key_index = (idx + 1) % total_keys
                    parts = resp.json().get("candidates", [{}])[0].get("content", {}).get("parts", [])
                    text_part = next((p.get("text", "") for p in parts if isinstance(p, dict) and "text" in p), "").strip()
                    if text_part:
                        log.info(f"[audio] Gemini {kid} OK: {text_part[:80]}")
                        return text_part
                elif resp.status_code in (429, 500, 502, 503, 504):
                    log.warning(f"[audio] Gemini {kid} devolvió {resp.status_code}. Rotando a siguiente llave...")
                    continue
                else:
                    log.warning(f"[audio] Gemini {kid} status {resp.status_code}: {resp.text[:120]}")
                    continue

            except Exception as eg:
                log.warning(f"[audio] Gemini {kid} error: {eg}")
                continue

        return None

    async def _transcribe_groq_whisper(
        self, 
        audio_bytes: bytes, 
        mime_type: str
    ) -> Optional[str]:
        """Transcribe usando Groq Whisper (whisper-large-v3-turbo, ultra baja latencia)."""
        self._ensure_keys_loaded()
        groq_key = self._groq_key_cache
        if not groq_key:
            return None

        clean_mime = (mime_type or "audio/wav").split(";")[0].strip().lower()
        suffix = ".wav" if "wav" in clean_mime else self._audio_suffix(clean_mime)
        filename = f"audio{suffix}"

        tmp_path = None
        try:
            with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
                tmp.write(audio_bytes)
                tmp_path = tmp.name

            async with httpx.AsyncClient(timeout=25.0) as client:
                with open(tmp_path, "rb") as f:
                    resp = await client.post(
                        "https://api.groq.com/openai/v1/audio/transcriptions",
                        headers={"Authorization": f"Bearer {groq_key}"},
                        files={"file": (filename, f, clean_mime)},
                        data={
                            "model": "whisper-large-v3-turbo",
                            "language": "es",
                            "response_format": "json",
                            "temperature": "0",
                        },
                    )

            if resp.status_code == 200:
                payload = resp.json()
                t = (payload.get("text") or "").strip()
                if t:
                    log.info(f"[audio] Groq Whisper OK: {t[:80]}")
                    return t
            else:
                log.warning(f"[audio] Groq Whisper {resp.status_code}: {resp.text[:160]}")

        except Exception as eg:
            log.warning(f"[audio] Groq Whisper error: {eg}")
        finally:
            if tmp_path and os.path.exists(tmp_path):
                try:
                    os.unlink(tmp_path)
                except Exception:
                    pass

        return None

    async def _transcribe_openrouter_whisper(
        self, 
        audio_bytes: bytes, 
        mime_type: str
    ) -> Optional[str]:
        """Transcribe usando OpenRouter Whisper (fallback secundario)."""
        self._ensure_keys_loaded()
        or_key = self._openrouter_key_cache
        if not or_key:
            return None

        clean_mime = (mime_type or "audio/wav").split(";")[0].strip().lower()
        suffix = ".wav" if "wav" in clean_mime else self._audio_suffix(clean_mime)
        filename = f"audio{suffix}"

        tmp_path = None
        try:
            with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
                tmp.write(audio_bytes)
                tmp_path = tmp.name

            async with httpx.AsyncClient(timeout=35.0) as client:
                with open(tmp_path, "rb") as f:
                    resp = await client.post(
                        "https://openrouter.ai/api/v1/audio/transcriptions",
                        headers={"Authorization": f"Bearer {or_key}"},
                        files={"file": (filename, f, clean_mime)},
                        data={
                            "model": getattr(Config, "WHISPER_MODEL", "openai/whisper-large-v3"),
                            "language": "es",
                        },
                    )

            if resp.status_code == 200:
                t = resp.json().get("text", "").strip()
                if t:
                    log.info(f"[audio] OpenRouter Whisper OK: {t[:80]}")
                    return t
            else:
                log.warning(f"[audio] OpenRouter Whisper {resp.status_code}: {resp.text[:160]}")

        except Exception as ew:
            log.warning(f"[audio] OpenRouter Whisper error: {ew}")
        finally:
            if tmp_path and os.path.exists(tmp_path):
                try:
                    os.unlink(tmp_path)
                except Exception:
                    pass

        return None

    def clear_cache(self) -> None:
        """Limpia la caché de audio."""
        self._audio_cache.clear()


async def transcribe_audio(
    file_id: str, 
    platform: str = "telegram",
    wa_media_id: str = None
) -> str:
    """Función de conveniencia para transcripción de audio."""
    handler = AudioHandler()
    return await handler.transcribe_audio(file_id, platform, wa_media_id)