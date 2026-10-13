#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
edge_tts_sender.py — Motor de Síntesis de Voz Neuronal Ultra-Realista (Edge Neural TTS) + Envío a WhatsApp.

Proporciona voces humanas fluidas y naturales en español colombiano, mexicano y español neutro sin sonar robótico.
"""

import argparse
import asyncio
import base64
import json
import os
import sys
import urllib.request
from pathlib import Path

import edge_tts


async def generate_edge_tts(text: str, output_path: str, voice: str = "es-CO-SalomeNeural"):
    """Sintetiza voz neuronal de alta definición."""
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_path)


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
    parser = argparse.ArgumentParser(description="Edge Neural TTS Sender")
    parser.add_argument("--to", type=str, required=True, help="Número de WhatsApp destino")
    parser.add_argument("--text", type=str, required=True, help="Texto a decir")
    parser.add_argument("--voice", type=str, default="es-CO-SalomeNeural", help="Voz (ej. es-CO-SalomeNeural, es-MX-DaliaNeural, es-CO-GonzaloNeural)")
    args = parser.parse_args()

    tmp_mp3 = f"/tmp/edge_tts_{os.getpid()}.mp3"

    print(f"🎙️ Generando voz neuronal HD [{args.voice}]...")
    asyncio.run(generate_edge_tts(args.text, tmp_mp3, voice=args.voice))

    print(f"📱 Enviando Nota de Voz a {args.to}...")
    res = send_whatsapp_audio(args.to, tmp_mp3)
    print(f"✅ Resultado: {json.dumps(res, indent=2)}")

    if os.path.exists(tmp_mp3):
        os.remove(tmp_mp3)


if __name__ == "__main__":
    main()
