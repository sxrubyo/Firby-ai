#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
send_whatsapp_voice.py — Genera un audio con Voicebox (Kokoro TTS) y lo envía por WhatsApp.

Uso:
  python3 send_whatsapp_voice.py --to "573001234567" --text "Hola Santi, te enviamos esta nota de voz generada 100% en vivo con Voicebox en LUCY."
"""

import argparse
import base64
import json
import os
import sys
import urllib.request
from pathlib import Path

# Importar VoiceboxTTS
TOOLS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS_DIR))

from voicebox_generator import VoiceboxTTS


def send_whatsapp_audio(to_number: str, audio_path: str) -> dict:
    """Lee un archivo de audio .wav, lo codifica en base64 y lo envía mediante el WhatsApp Bridge."""
    with open(audio_path, "rb") as f:
        audio_bytes = f.read()

    audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")

    payload = {
        "to": to_number,
        "audioBase64": audio_b64,
        "mimeType": "audio/wav",
        "ptt": True,  # ptt=True lo envía como Nota de Voz nativa con micrófono azul
    }

    url = "http://localhost:8002/send-audio"
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(req) as resp:
            res_data = json.loads(resp.read().decode("utf-8"))
            return res_data
    except Exception as e:
        print(f"❌ Error al enviar audio por WhatsApp Bridge: {e}", file=sys.stderr)
        raise e


def main():
    parser = argparse.ArgumentParser(description="Voicebox WhatsApp Audio Sender")
    parser.add_argument("--to", type=str, required=True, help="Número de WhatsApp destino (con código de país, sin +)")
    parser.add_argument("--text", type=str, required=True, help="Texto que dirá la voz de Voicebox")
    parser.add_argument("--voice", type=str, default="af_bella", help="Nombre de la voz (af_bella, af_sarah, am_adam, etc.)")
    parser.add_argument("--lang", type=str, default="es", help="Idioma (es, en-us)")
    args = parser.parse_args()

    tmp_audio = f"/tmp/voicebox_wa_{os.getpid()}.wav"

    print("🎙️ 1. Generando audio con Voicebox (Kokoro TTS)...")
    tts = VoiceboxTTS()
    tts.generate_speech(args.text, output_path=tmp_audio, voice=args.voice, lang=args.lang)

    print(f"📱 2. Enviando Nota de Voz de WhatsApp a: {args.to}...")
    res = send_whatsapp_audio(args.to, tmp_audio)
    print(f"✅ Respuesta del WhatsApp Bridge: {json.dumps(res, indent=2)}")

    if os.path.exists(tmp_audio):
        os.remove(tmp_audio)


if __name__ == "__main__":
    main()
