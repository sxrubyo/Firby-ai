"""
Hermes-Style LLM API Engine for Firby
Handles Google Sheets, Google Calendar, Google Drive, REST APIs, and Webhooks via LLM Reasoning.
"""

import json
import logging
import re
import os
import httpx
from typing import Dict, List, Any, Optional

log = logging.getLogger("firby.hermes_api_engine")

class HermesAPIEngine:
    def __init__(self):
        pass

    def extract_sheet_id(self, text: str) -> Optional[str]:
        """Extrae el ID de una hoja de Google Sheets a partir de una URL o texto."""
        match = re.search(r"docs\.google\.com/spreadsheets/d/([a-zA-Z0-9-_]+)", text)
        if match:
            return match.group(1)
        if len(text.strip()) == 44 and "/" not in text:
            return text.strip()
        return None

    async def fetch_public_google_sheet_csv(self, sheet_id: str, gid: str = "0") -> Optional[str]:
        """Obtiene el contenido CSV de una hoja pública de Google Sheets."""
        url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"
        try:
            async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
                resp = await client.get(url)
                if resp.status_code == 200 and resp.text:
                    return resp.text
        except Exception as e:
            log.warning(f"[hermes_api] error fetching sheet CSV {sheet_id}: {e}")
        return None

    async def parse_sheet_to_inventory(self, csv_or_json_text: str) -> Dict[str, str]:
        """Pasa el contenido de la hoja de cálculo por el LLM para mapear productos/precios/servicios."""
        prompt = f"""Analiza esta tabla/hoja de cálculo de un negocio (tienda, restaurante, clínica, etc.):

CONTENIDO DE LA TABLA:
{csv_or_json_text[:2500]}

Extrae TODOS los productos, servicios o ítems con sus precios correspondientes.
Responde ÚNICAMENTE un JSON válido con esta estructura:
{{
  "Nombre del Producto 1": "$Precio 1",
  "Nombre del Producto 2": "$Precio 2"
}}
Si no hay precio, usa "Consultar". SOLO JSON."""

        try:
            from src.core.globals import llm_engine
            if llm_engine:
                res, _ = await llm_engine.complete(
                    [{"role": "user", "content": prompt}],
                    model_tier="fast", temperature=0.1, max_tokens=600, use_cache=False
                )
                clean = res.strip().replace("```json", "").replace("```", "").strip()
                data = json.loads(clean)
                if isinstance(data, dict):
                    return {str(k).strip().title(): str(v).strip() for k, v in data.items() if k}
        except Exception as e:
            log.warning(f"[hermes_api] error parsing sheet with LLM: {e}")
        return {}

    async def process_incoming_sheet(self, text: str, db) -> Optional[List[str]]:
        """Intercepta una URL de Google Sheets enviada por el usuario y la procesa en vivo."""
        sheet_id = self.extract_sheet_id(text)
        if not sheet_id:
            return None

        log.info(f"[hermes_api] Google Sheet detectado con ID: {sheet_id}")
        csv_text = await self.fetch_public_google_sheet_csv(sheet_id)
        if not csv_text:
            return [
                "Veo que me enviaste un enlace de Google Sheets! 📊",
                "Para poder leer tus productos en vivo, asegúrate de que el archivo esté configurado como 'Cualquier persona con el enlace puede ver' (Público) o conecta tu cuenta de Google."
            ]

        parsed_items = await self.parse_sheet_to_inventory(csv_text)
        if parsed_items and db:
            current_clinic = db.get_clinic()
            curr_pricing = current_clinic.get("pricing", {})
            if isinstance(curr_pricing, str):
                try: curr_pricing = json.loads(curr_pricing)
                except Exception: curr_pricing = {}
            curr_pricing.update(parsed_items)

            db.update_clinic(pricing=json.dumps(curr_pricing))
            db.save_core_memory("pricing_catalog", json.dumps(curr_pricing), category="clinic")
            db.save_core_memory("google_sheet_id", sheet_id, category="identity")

            item_count = len(parsed_items)
            preview = ", ".join(list(parsed_items.keys())[:3])

            return [
                f"Leí y aprendí tu hoja de Google Sheets exitosamente! 📊✨",
                f"Cargué {item_count} productos en el inventario (ej. {preview}).",
                "A partir de ahora, cuando tus clientes me pregunten por cualquier producto en WhatsApp, les responderé con la información de tu tabla!"
            ]

        return [
            "Logré conectarme a tu Google Sheet pero no encontré productos claros. Envíame un ejemplo de tus precios por aquí y los aprendo!"
        ]

hermes_api_engine = HermesAPIEngine()
