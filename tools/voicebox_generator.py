#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
voicebox_generator.py — Motor de Síntesis de Voz Local (Open Source ElevenLabs Alternative)

Basado en la arquitectura Voicebox (Jamie Pine) y Kokoro TTS Engine.
Permite generar archivos de audio WAV/MP3 ultra-realistas directamente en la máquina.
"""

import argparse
import os
import sys
from pathlib import Path

try:
    from kokoro_onnx import Kokoro
    import soundfile as sf
    HAS_KOKORO = True
except ImportError:
    HAS_KOKORO = False

MODEL_URL = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx"
VOICES_URL = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin"


class VoiceboxTTS:
    """Motor local de clonación y generación de voz."""

    def __init__(self, models_dir: str = "/home/ubuntu/.voicebox/models"):
        self.models_dir = Path(models_dir)
        self.models_dir.mkdir(parents=True, exist_ok=True)
        self.model_path = self.models_dir / "kokoro-v1.0.onnx"
        self.voices_path = self.models_dir / "voices-v1.0.bin"
        self.kokoro = None

    def ensure_models(self):
        """Descarga los modelos ONNX y voces de Kokoro si no existen."""
        import subprocess
        if not self.model_path.exists():
            print(f"📥 Descargando modelo Kokoro ONNX (~88MB)...")
            subprocess.run(["curl", "-L", "-o", str(self.model_path), MODEL_URL], check=True)
        if not self.voices_path.exists():
            print(f"📥 Descargando catálogo de voces (~20MB)...")
            subprocess.run(["curl", "-L", "-o", str(self.voices_path), VOICES_URL], check=True)

    def load_engine(self):
        if not self.kokoro:
            self.ensure_models()
            print("🎙️ Cargando motor Voicebox/Kokoro TTS...")
            self.kokoro = Kokoro(str(self.model_path), str(self.voices_path))

    def generate_speech(self, text: str, output_path: str = "output.wav", voice: str = "af_sarah", lang: str = "en-us"):
        """Genera un archivo de audio .wav a partir de texto."""
        self.load_engine()
        print(f"🗣️ Generando voz para: '{text[:50]}...' [Voz: {voice}]")
        samples, sample_rate = self.kokoro.create(text, voice=voice, speed=1.0, lang=lang)
        sf.write(output_path, samples, sample_rate)
        print(f"✅ Audio guardado exitosamente en: {output_path}")
        return output_path


def main():
    parser = argparse.ArgumentParser(description="Voicebox Local Text-to-Speech Generator")
    parser.add_argument("--text", type=str, required=True, help="Texto a sintetizar")
    parser.add_argument("--output", type=str, default="generated_voice.wav", help="Archivo de audio de salida")
    parser.add_argument("--voice", type=str, default="af_sarah", help="Voz a utilizar (ej. af_sarah, am_adam, af_bella, am_michael)")
    parser.add_argument("--lang", type=str, default="en-us", help="Idioma (en-us, es, etc.)")
    args = parser.parse_args()

    if not HAS_KOKORO:
        print("❌ Error: kokoro-onnx no está instalado.", file=sys.stderr)
        sys.exit(1)

    tts = VoiceboxTTS()
    tts.generate_speech(args.text, output_path=args.output, voice=args.voice, lang=args.lang)


if __name__ == "__main__":
    main()
