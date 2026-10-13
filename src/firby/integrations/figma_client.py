# -*- coding: utf-8 -*-
"""
Firby Figma Integration Client
Enables reading design files, extracting components, downloading SVGs/images,
and parsing design tokens directly from Figma.
"""
from __future__ import annotations

import os
import json
import logging
import urllib.parse
from typing import Dict, Any, List, Optional
import httpx

log = logging.getLogger("firby.figma")

FIGMA_TOKEN = os.getenv("FIGMA_ACCESS_TOKEN", "")
FIGMA_API_BASE = "https://api.figma.com/v1"


class FigmaClient:
    """Cliente para la API REST de Figma."""

    def __init__(self, token: str = FIGMA_TOKEN):
        self.token = token
        self.headers = {"X-Figma-Token": self.token}

    @staticmethod
    def extract_file_key(figma_url_or_key: str) -> str:
        """Extrae el file_key de una URL de Figma o devuelve el key directo."""
        if "figma.com" in figma_url_or_key:
            parsed = urllib.parse.urlparse(figma_url_or_key)
            parts = [p for p in parsed.path.split("/") if p]
            # Formatos típicos: /file/KEY/title o /design/KEY/title
            if len(parts) >= 2 and parts[0] in ("file", "design"):
                return parts[1]
        return figma_url_or_key.strip()

    async def get_current_user(self) -> Dict[str, Any]:
        """Obtiene la información del usuario autenticado en Figma."""
        async with httpx.AsyncClient(timeout=10.0) as client:
            res = await client.get(f"{FIGMA_API_BASE}/me", headers=self.headers)
            res.raise_for_status()
            return res.json()

    async def get_file(self, file_key: str, depth: Optional[int] = None) -> Dict[str, Any]:
        """Obtiene el árbol completo del documento de Figma."""
        key = self.extract_file_key(file_key)
        url = f"{FIGMA_API_BASE}/files/{key}"
        params = {}
        if depth is not None:
            params["depth"] = depth
        async with httpx.AsyncClient(timeout=30.0) as client:
            res = await client.get(url, headers=self.headers, params=params)
            res.raise_for_status()
            return res.json()

    async def get_file_nodes(self, file_key: str, node_ids: List[str]) -> Dict[str, Any]:
        """Obtiene detalles de nodos específicos dentro de un archivo de Figma."""
        key = self.extract_file_key(file_key)
        url = f"{FIGMA_API_BASE}/files/{key}/nodes"
        params = {"ids": ",".join(node_ids)}
        async with httpx.AsyncClient(timeout=20.0) as client:
            res = await client.get(url, headers=self.headers, params=params)
            res.raise_for_status()
            return res.json()

    async def export_node_images(
        self, file_key: str, node_ids: List[str], format: str = "svg", scale: float = 1.0
    ) -> Dict[str, str]:
        """
        Exporta nodos como imágenes (SVG, PNG, JPG, PDF) y devuelve un mapa {node_id: image_url}.
        """
        key = self.extract_file_key(file_key)
        url = f"{FIGMA_API_BASE}/images/{key}"
        params = {
            "ids": ",".join(node_ids),
            "format": format.lower(),
            "scale": scale
        }
        async with httpx.AsyncClient(timeout=20.0) as client:
            res = await client.get(url, headers=self.headers, params=params)
            res.raise_for_status()
            data = res.json()
            return data.get("images", {})

    async def download_image_to_file(self, image_url: str, output_path: str) -> bool:
        """Descarga una imagen renderizada por Figma y la guarda en disco."""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                res = await client.get(image_url)
                res.raise_for_status()
                with open(output_path, "wb") as f:
                    f.write(res.content)
            return True
        except Exception as e:
            log.error(f"[FigmaClient] Error descargando imagen {image_url}: {e}")
            return False
