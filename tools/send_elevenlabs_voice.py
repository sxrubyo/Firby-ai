#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
send_elevenlabs_voice.py — Genera notas de voz con ElevenLabs API y las envía por WhatsApp.
"""

import argparse
import base64
import json
import os
import sys
import urllib.request

ELEVENLABS_KEY = os.environ.get("ELEVENLABS_API_KEY", "")
DEFAULT_VOICE_ID = "21m00Tcm4TlvDq8ikWAM"  # Rachel / ElevenLabs natural voice


def generate_elevenlabs_audio(text: str, output_path: str, voice_id: str = DEFAULT_VOICE_ID) -> str:
    """Genera audio MP3 mediante ElevenLabs API."""
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {
        "xi-api-key": ELEVENLABS_KEY,
        "Content-Type": "application/json",
        "Accept": "audio/mpeg",
    }
    payload = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.75,
        },
    }

    req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req) as resp:
            audio_bytes = resp.read()
            with open(output_path, "wb") as f:
                f.write(audio_bytes)
            return output_path
    except Exception as e:
        print(f"❌ Error ElevenLabs API: {e}", file=sys.stderr)
        raise e


def send_whatsapp_audio(to_number: str, audio_path: str) -> dict:
    """Envía la nota de voz a través del WhatsApp Bridge."""
    with open(audio_path, "rb") as f:
        audio_bytes = f.read()

    audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")

    payload = {
        "to": to_number,
        "audioBase64": audio_b64,
        "mimeType": "audio/mp3",
        "ptt": True,
    }

    url = "http://localhost:8002/send-audio"
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))


def main():
    parser = argparse.ArgumentParser(description="ElevenLabs WhatsApp Voice Sender")
    parser.add_argument("--to", type=str, required=True, help="Número de WhatsApp destino")
    parser.add_argument("--text", type=str, required=True, help="Texto a decir")
    parser.add_argument("--voice_id", type=str, default=DEFAULT_VOICE_ID, help="Voice ID de ElevenLabs")
    args = parser.parse_args()

    tmp_mp3 = f"/tmp/elevenlabs_wa_{os.getpid()}.mp3"

    print("🎙️ Generando audio con ElevenLabs API (eleven_multilingual_v2)...")
    generate_elevenlabs_audio(args.text, tmp_mp3, voice_id=args.voice_id)

    print(f"📱 Enviando Nota de Voz de ElevenLabs a {args.to}...")
    res = send_whatsapp_audio(args.to, tmp_mp3)
    print(f"✅ Resultado: {json.dumps(res, indent=2)}")

    if os.path.exists(tmp_mp3):
        os.remove(tmp_mp3)


if __name__ == "__main__":
    main()
