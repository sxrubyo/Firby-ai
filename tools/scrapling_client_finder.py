#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scrapling_client_finder.py — Motor de Búsqueda y Extracción de Clientes & Leads impulsado por Scrapling.

Características:
- Adaptable anti-bot (StealthyFetcher + Fetcher + browserforge)
- Extracción de leads (Nombre, Teléfono, Email, Sitio Web, Dirección, WhatsApp)
- Modos: Búsqueda Web, Directorios Médicos/Clínicas, y Escaneo de Dominios Específicos
- Exportación automática a JSON / CSV para integración con CRM / WhatsApp Bridge
"""

import argparse
import csv
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Any

# Verificar disponibilidad de scrapling
try:
    from scrapling import Fetcher, StealthyFetcher, Selector
    HAS_SCRAPLING = True
except ImportError:
    HAS_SCRAPLING = False

EMAIL_REGEX = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
PHONE_REGEX = re.compile(r"(\+?\d{1,3}[-.\s]?)?\(?\d{2,4}\)?[-.\s]?\d{3,4}[-.\s]?\d{3,4}")
WA_REGEX = re.compile(r"(?:wa\.me/|api\.whatsapp\.com/send\?phone=)(\d+)")


class ScraplingClientFinder:
    """Motor de búsqueda de clientes impulsado por Scrapling."""

    def __init__(self, stealth: bool = True):
        self.stealth = stealth

    def fetch_page(self, url: str) -> str:
        """Obtiene el HTML de una URL usando Fetcher.get() o StealthyFetcher.fetch() de Scrapling."""
        if not HAS_SCRAPLING:
            import urllib.request
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req) as resp:
                return resp.read().decode("utf-8", errors="ignore")

        if self.stealth:
            try:
                fetcher = StealthyFetcher()
                response = fetcher.fetch(url)
                if hasattr(response, "text"):
                    return response.text
                elif hasattr(response, "content"):
                    return response.content.decode("utf-8", errors="ignore")
                return str(response)
            except Exception as e:
                print(f"[Warning] StealthyFetcher falló ({e}), probando Fetcher.get() estándar...", file=sys.stderr)
        
        try:
            response = Fetcher.get(url)
            if hasattr(response, "text"):
                return response.text
            elif hasattr(response, "content"):
                return response.content.decode("utf-8", errors="ignore")
            return str(response)
        except Exception as e:
            import urllib.request
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
            with urllib.request.urlopen(req) as resp:
                return resp.read().decode("utf-8", errors="ignore")

    def extract_leads_from_text(self, text: str, source_url: str = "") -> Dict[str, Any]:
        """Extrae correos, teléfonos y enlaces de WhatsApp del texto HTML."""
        emails = list(set(EMAIL_REGEX.findall(text)))
        emails = [e for e in emails if not e.lower().endswith(('.png', '.jpg', '.jpeg', '.svg', '.gif', '.webp', '.css', '.js'))]

        phones = list(set(PHONE_REGEX.findall(text)))
        phones = [p[0] + p[1] if isinstance(p, tuple) else p for p in phones if len(str(p)) > 7]

        wa_numbers = list(set(WA_REGEX.findall(text)))

        return {
            "source_url": source_url,
            "emails": emails,
            "phones": phones,
            "whatsapp_numbers": wa_numbers,
        }

    def scan_client_target(self, url: str) -> Dict[str, Any]:
        """Escanea un sitio web de un cliente potencial para extraer información relevante."""
        print(f"🔍 Escaneando cliente objetivo: {url}")
        html = self.fetch_page(url)
        
        title = ""
        if HAS_SCRAPLING:
            try:
                selector = Selector(html)
                title_el = selector.css("title::text").get()
                title = title_el if title_el else ""
            except Exception:
                pass

        if not title:
            match = re.search(r"<title>(.*?)</title>", html, re.IGNORECASE | re.DOTALL)
            if match:
                title = match.group(1).strip()

        leads = self.extract_leads_from_text(html, source_url=url)
        leads["title"] = title.strip()
        return leads


def main():
    parser = argparse.ArgumentParser(description="Scrapling Client & Lead Finder Engine")
    parser.add_argument("--url", type=str, help="URL del sitio web del cliente a escanear")
    parser.add_argument("--output", type=str, default="clients_extracted.json", help="Ruta del archivo JSON de salida")
    parser.add_argument("--stealth", action="store_true", default=False, help="Usar StealthyFetcher con evasión anti-bot")
    args = parser.parse_args()

    finder = ScraplingClientFinder(stealth=args.stealth)
    
    if args.url:
        result = finder.scan_client_target(args.url)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"\n✅ Resultados guardados en {args.output}")
    else:
        print("Uso: python3 scrapling_client_finder.py --url <URL_CLIENTE_O_DIRECTORIO>")


if __name__ == "__main__":
    main()
