"""Configuration and Guardrails for Firby Autonomous Growth Council.
Powered by Google Gemini 3.5 Flash.
"""

import os
from pathlib import Path
from google import genai

# Load environment variables from /home/ubuntu/firby/.env if not present
ENV_PATH = Path('/home/ubuntu/firby/.env')
if ENV_PATH.exists():
    with open(ENV_PATH, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                k = k.strip()
                v = v.strip().strip('\'"')
                if k not in os.environ:
                    os.environ[k] = v

GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY') or os.environ.get('GOOGLE_API_KEY')
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY or GOOGLE_API_KEY not found in environment or /home/ubuntu/firby/.env")

# Models
# Santi requested Gemini 3.5 Flash; gemini-3.5-flash-lite is the active high-quota 3.5 endpoint, with 3.6-flash and 2.5-flash fallbacks
PRIMARY_MODEL = "gemini-3.5-flash-lite"
SECONDARY_MODEL = "gemini-3.6-flash"
TERTIARY_MODEL = "gemini-2.5-flash"
QUOTA_LIMITED_MODEL = "gemini-3.5-flash"

ACTIVE_MODELS_CASCADE = [PRIMARY_MODEL, SECONDARY_MODEL, TERTIARY_MODEL, QUOTA_LIMITED_MODEL]

# Initialize Client
client = genai.Client(api_key=GEMINI_API_KEY)

# Global Inviolable Rules
FIRBY_CORE_IDENTITY = """
# REGLAS INQUEBRANTABLES DE FIRBY:
1. USUARIO Y DUEÑO:
   - El creador y dueño es Santiago Rubio Parra ("Santi" o "Santiago").
2. CANALES Y ARQUITECTURA DE PRODUCTO:
   - EN LA WEB (Visitantes / Leads): Firby vive en el sitio web del cliente como un widget/botón flotante 2D. Atiende en tiempo real, consulta disponibilidad real en Google Calendar, agenda citas confirmadas y tramita reservas en la web.
   - FIRBY NUNCA ATIENDE VISITANTES NI PROSPECTOS POR WHATSAPP.
   - EN WHATSAPP (+57 324 369 9856): Firby habla ÚNICA Y EXCLUSIVAMENTE CON EL DUEÑO DEL NEGOCIO (EL CLIENTE). Es una línea ejecutiva privada continua donde envía alertas de citas confirmadas, pide visto bueno para excepciones comerciales y responde consultas de gestión ("cuántas citas van hoy", "bloquea el viernes por la tarde", etc.).
3. COPYWRITING Y MARKETING:
   - CERO EMOJIS en todos los anuncios, titulares, copies, captions y piezas.
   - CERO MENCIÓN DE $1.000 COP (la oferta oficial es: "Prueba 7 días gratis. Cancela cuando quieras en 1 clic").
   - Idioma: Español real, directo, de negocios, profesional y punzante. Sin clichés de IA ("solución integral", "revoluciona", "en la era digital", etc.).
4. IDENTIDAD VISUAL:
   - Modo oscuro obsidiana (#0f0f11), acentos verde lima neón (#b9fa01), tipografía Neue Montreal, insignia squircle de app icon con monograma fi.
"""
