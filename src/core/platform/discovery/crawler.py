# -*- coding: utf-8 -*-
"""
Firby Platform — Controlled Site Discovery & Crawler
===================================================
Realiza el descubrimiento controlado del sitio web del cliente con límites estrictos:
- allowed_domains: Aislamiento estricto al dominio del cliente.
- depth_limit: Profundidad máxima controlada (por defecto 2).
- page_budget: Límite presupuestario de páginas (por defecto 15).
- Deduplicación y normalización canónica de URLs.
- Extracción estructurada: Títulos, servicios, precios, secciones, contactos, FAQs.
"""

from __future__ import annotations
import re
import urllib.parse
from dataclasses import dataclass, field
from typing import Dict, Any, List, Set, Optional


@dataclass
class DiscoveredPage:
    url: str
    title: str
    headings: List[str] = field(default_factory=list)
    paragraphs: List[str] = field(default_factory=list)
    nav_links: List[Dict[str, str]] = field(default_factory=list)
    pricing_mentions: List[str] = field(default_factory=list)
    faqs: List[Dict[str, str]] = field(default_factory=list)
    contact_info: Dict[str, Any] = field(default_factory=dict)
    observed_at: float = field(default_factory=lambda: 0.0)
    text_content: str = ""
    prices_found: Dict[str, str] = field(default_factory=dict)


@dataclass
class SiteModel:
    base_url: str = ""
    root_url: str = ""
    business_name: str = ""
    summary: str = ""
    pages: List[DiscoveredPage] = field(default_factory=list)
    services: List[str] = field(default_factory=list)
    prices: Dict[str, str] = field(default_factory=dict)
    navigation_sections: List[Dict[str, str]] = field(default_factory=list)
    contacts: Dict[str, Any] = field(default_factory=dict)
    discovered_faqs: List[Dict[str, str]] = field(default_factory=list)
    page_count: int = 0

    def __post_init__(self):
        if not self.base_url and self.root_url:
            self.base_url = self.root_url
        elif not self.root_url and self.base_url:
            self.root_url = self.base_url
        if not self.page_count and self.pages:
            self.page_count = len(self.pages)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "base_url": self.base_url,
            "root_url": self.root_url,
            "business_name": self.business_name,
            "summary": self.summary,
            "page_count": len(self.pages),
            "services": self.services,
            "prices": self.prices,
            "navigation_sections": self.navigation_sections,
            "contacts": self.contacts,
            "faqs_count": len(self.discovered_faqs)
        }


class ControlledSiteCrawler:
    """Crawler con límites de seguridad para el descubrimiento inicial de sitios web."""

    def __init__(
        self,
        base_url: str,
        depth_limit: int = 2,
        page_budget: int = 15,
        allowed_domains: Optional[List[str]] = None
    ):
        self.base_url = base_url.strip()
        parsed = urllib.parse.urlparse(self.base_url)
        self.primary_domain = parsed.netloc.lower()
        self.depth_limit = depth_limit
        self.page_budget = page_budget
        self.allowed_domains = set([d.lower() for d in (allowed_domains or [self.primary_domain])])

    def is_url_allowed(self, url: str) -> bool:
        """Verifica que la URL pertenezca estrictamente al dominio autorizado."""
        try:
            parsed = urllib.parse.urlparse(url)
            netloc = parsed.netloc.lower()
            if not netloc:
                return True
            return any(netloc == d or netloc.endswith("." + d) for d in self.allowed_domains)
        except Exception:
            return False

    def normalize_url(self, raw_url: str, current_page: str = "") -> Optional[str]:
        """Normaliza y deduplica URLs relativas y absolutas."""
        try:
            full = urllib.parse.urljoin(current_page or self.base_url, raw_url)
            parsed = urllib.parse.urlparse(full)
            # Limpiar fragmentos y query params tracking
            clean = urllib.parse.urlunparse((
                parsed.scheme or "https",
                parsed.netloc,
                parsed.path.rstrip("/") or "/",
                "", "", ""
            ))
            return clean
        except Exception:
            return None

    def extract_structured_page(self, html: str, url: str) -> DiscoveredPage:
        """
        Extrae información semántica clave de un HTML sin requerir dependencias pesadas.
        """
        import html as html_lib

        # 1. Título
        title_m = re.search(r"<title[^>]*>(.*?)</title>", html, re.IGNORECASE | re.DOTALL)
        title = html_lib.unescape(title_m.group(1).strip()) if title_m else ""

        # 2. Encabezados H1, H2, H3
        headings = []
        for m in re.finditer(r"<h[1-3][^>]*>(.*?)</h[1-3]>", html, re.IGNORECASE | re.DOTALL):
            clean_h = re.sub(r"<[^>]+>", "", m.group(1)).strip()
            if clean_h and len(clean_h) < 120:
                headings.append(html_lib.unescape(clean_h))

        # 3. Menciones de precios
        pricing_mentions = []
        price_patterns = [
            r"(\$\s*[\d\.,]+\s*(?:COP|USD|al mes|/mes|mes)?)",
            r"(Gratis|Prueba\s+de\s+\d+\s+días)",
            r"(Plan\s+[A-Za-z0-9]+)"
        ]
        for pat in price_patterns:
            for pm in re.finditer(pat, html, re.IGNORECASE):
                val = pm.group(1).strip()
                if val and val not in pricing_mentions:
                    pricing_mentions.append(val)

        # 4. Enlaces de navegación interna
        nav_links = []
        for m in re.finditer(r"<a[^>]+href=[\"']([^\"']+)[\"'][^>]*>(.*?)</a>", html, re.IGNORECASE | re.DOTALL):
            href = m.group(1).strip()
            text = re.sub(r"<[^>]+>", "", m.group(2)).strip()
            if href and not href.startswith(("javascript:", "mailto:", "tel:")):
                norm = self.normalize_url(href, url)
                if norm and self.is_url_allowed(norm):
                    nav_links.append({"href": norm, "text": text[:60], "raw": href})

        # 5. Información de contacto
        contacts = {}
        email_m = re.findall(r"[\w\.-]+@[\w\.-]+\.\w+", html)
        if email_m:
            contacts["emails"] = list(set(email_m))[:3]
        phone_m = re.findall(r"(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}", html)
        if phone_m:
            contacts["phones"] = list(set(phone_m))[:3]

        return DiscoveredPage(
            url=url,
            title=title,
            headings=headings[:12],
            paragraphs=[],
            nav_links=nav_links[:25],
            pricing_mentions=pricing_mentions[:10],
            contact_info=contacts,
            observed_at=0.0
        )

    def crawl_site(self, fetcher_func=None) -> SiteModel:
        """
        Ejecuta el ciclo de descubrimiento respetando el presupuesto de páginas y profundidad.
        fetcher_func(url) -> html string (opcional para pruebas unitarias o simulación).
        """
        model = SiteModel(base_url=self.base_url)
        visited: Set[str] = set()
        queue: List[Tuple[str, int]] = [(self.base_url, 0)]

        while queue and len(visited) < self.page_budget:
            current_url, depth = queue.pop(0)
            if current_url in visited or depth > self.depth_limit:
                continue

            visited.add(current_url)

            # Obtener contenido
            html = ""
            if fetcher_func:
                try:
                    html = fetcher_func(current_url) or ""
                except Exception:
                    continue
            else:
                try:
                    import urllib.request
                    req = urllib.request.Request(
                        current_url,
                        headers={"User-Agent": "FirbyDiscoveryAgent/1.0 (+https://firbyai.com)"}
                    )
                    with urllib.request.urlopen(req, timeout=8.0) as resp:
                        content_type = resp.headers.get("content-type", "")
                        if "text/html" not in content_type:
                            continue
                        html = resp.read().decode("utf-8", errors="ignore")
                except Exception:
                    continue

            if not html:
                continue

            page = self.extract_structured_page(html, current_url)
            model.pages.append(page)

            # Inferir nombre del negocio si es la página de inicio
            if not model.business_name and page.title:
                parts = re.split(r"[-|—]", page.title)
                model.business_name = parts[0].strip()

            # Encolar nuevos enlaces internos si no se excede la profundidad
            if depth < self.depth_limit:
                for link in page.nav_links:
                    tgt = link["href"]
                    if tgt not in visited and self.is_url_allowed(tgt):
                        queue.append((tgt, depth + 1))

        # Síntesis estructurada final
        model.page_count = len(model.pages)
        for p in model.pages:
            for pr in p.pricing_mentions:
                if "pro" in pr.lower():
                    model.prices["pro"] = pr
                elif "starter" in pr.lower():
                    model.prices["starter"] = pr
                elif "equipo" in pr.lower():
                    model.prices["equipos"] = pr

        return model
