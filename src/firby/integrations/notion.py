# -*- coding: utf-8 -*-
"""Integración con la API de Notion para importar base de conocimientos."""
from __future__ import annotations
import logging
import httpx
from typing import Dict, Any, List, Optional
import src.core.globals as g

log = logging.getLogger("firby.integrations.notion")

class NotionClient:
    """Cliente para interactuar con Notion API y extraer información de bases de datos/páginas."""

    def __init__(self, token: str):
        self.token = token.strip()
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Notion-Version": "2022-06-28",
            "Content-Type": "application/json"
        }

    async def list_databases(self) -> List[Dict[str, Any]]:
        """Busca todas las bases de datos a las que tiene acceso el token."""
        url = "https://api.notion.com/v1/search"
        payload = {
            "filter": {
                "value": "database",
                "property": "object"
            }
        }
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.post(url, headers=self.headers, json=payload)
                if resp.status_code == 200:
                    results = resp.json().get("results", [])
                    databases = []
                    for db in results:
                        db_id = db.get("id")
                        # Extraer título
                        title_list = db.get("title", [])
                        title = "".join(t.get("plain_text", "") for t in title_list) or "Sin título"
                        databases.append({
                            "id": db_id,
                            "title": title
                        })
                    return databases
                else:
                    log.error(f"[notion] Search fail: {resp.status_code} - {resp.text}")
        except Exception as e:
            log.error(f"[notion] Exception listing databases: {e}")
        return []

    async def get_page_text(self, page_id: str) -> str:
        """
        Recupera el contenido de bloques de texto (párrafos, listas, encabezados)
        de una página para transformarlo en texto plano.
        """
        url = f"https://api.notion.com/v1/blocks/{page_id}/children"
        text_lines = []
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(url, headers=self.headers)
                if resp.status_code == 200:
                    blocks = resp.json().get("results", [])
                    for block in blocks:
                        b_type = block.get("type")
                        if not b_type:
                            continue
                        # Extraer texto enriquecido de los tipos de bloques comunes
                        rich_text = block.get(b_type, {}).get("rich_text", [])
                        block_text = "".join(t.get("plain_text", "") for t in rich_text).strip()
                        if block_text:
                            if b_type.startswith("heading_"):
                                text_lines.append(f"\n## {block_text}\n")
                            elif b_type == "bulleted_list_item":
                                text_lines.append(f"• {block_text}")
                            elif b_type == "numbered_list_item":
                                text_lines.append(f"1. {block_text}")
                            else:
                                text_lines.append(block_text)
                else:
                    log.error(f"[notion] Blocks fail: {resp.status_code} - {resp.text}")
        except Exception as e:
            log.error(f"[notion] Exception getting page children: {e}")
        return "\n".join(text_lines)

    async def sync_database(self, database_id: str) -> Dict[str, Any]:
        """
        Consulta las páginas de una base de datos de Notion, extrae sus contenidos
        y los consolida para ser ingeridos en la Base de Conocimiento de Firby.
        """
        url = f"https://api.notion.com/v1/databases/{database_id}/query"
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.post(url, headers=self.headers)
                if resp.status_code != 200:
                    log.error(f"[notion] Query fail: {resp.status_code} - {resp.text}")
                    return {"ok": False, "error": f"Error Notion API: {resp.status_code}"}

                pages = resp.json().get("results", [])
                if not pages:
                    return {"ok": True, "pages_synced": 0, "facts_extracted": 0}

                facts = []
                for page in pages:
                    page_id = page.get("id")
                    # Intentar obtener título de la página
                    title = "Página sin título"
                    properties = page.get("properties", {})
                    for prop_name, prop_val in properties.items():
                        if prop_val.get("type") == "title":
                            title_list = prop_val.get("title", [])
                            title = "".join(t.get("plain_text", "") for t in title_list) or title
                            break

                    # Obtener contenido interno
                    content_text = await self.get_page_text(page_id)
                    
                    # También añadir propiedades en formato de texto
                    prop_details = []
                    for prop_name, prop_val in properties.items():
                        p_type = prop_val.get("type")
                        if p_type == "title":
                            continue
                        elif p_type in ("rich_text", "text"):
                            rt = prop_val.get("rich_text", [])
                            val_str = "".join(t.get("plain_text", "") for t in rt)
                            if val_str:
                                prop_details.append(f"{prop_name}: {val_str}")
                        elif p_type == "select":
                            sel = prop_val.get("select")
                            if sel:
                                prop_details.append(f"{prop_name}: {sel.get('name')}")
                        elif p_type == "multi_select":
                            ms = prop_val.get("multi_select", [])
                            vals = [item.get("name", "") for item in ms]
                            if vals:
                                prop_details.append(f"{prop_name}: {', '.join(vals)}")
                        elif p_type == "number":
                            val_num = prop_val.get("number")
                            if val_num is not None:
                                prop_details.append(f"{prop_name}: {val_num}")

                    page_doc = f"=== PÁGINA: {title} ===\n"
                    if prop_details:
                        page_doc += "PROPIEDADES:\n" + "\n".join(prop_details) + "\n"
                    if content_text:
                        page_doc += f"CONTENIDO:\n{content_text}\n"
                    
                    facts.append(page_doc)

                # Ingerir en el KB
                if facts:
                    unified_text = "\n\n".join(facts)
                    if g.kb:
                        # Usar append para no pisar el KB maestro si ya tiene datos
                        # (O ingest si queremos que Notion sea la única fuente)
                        g.kb.ingest(unified_text)
                        return {
                            "ok": True,
                            "pages_synced": len(pages),
                            "facts_extracted": len(facts),
                            "chars": len(unified_text)
                        }
                    else:
                        return {"ok": False, "error": "Base de conocimiento local no inicializada"}

                return {"ok": True, "pages_synced": len(pages), "facts_extracted": 0}

        except Exception as e:
            log.error(f"[notion] Exception querying database: {e}", exc_info=True)
            return {"ok": False, "error": str(e)}
