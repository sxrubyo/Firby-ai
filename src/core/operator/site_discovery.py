# -*- coding: utf-8 -*-
"""
Firby AI — Site Discovery & Structured Knowledge Ingestion Engine
=================================================================
Descubre, analiza e indexa la estructura y el contenido completo de sitios web:
CUSTOMER WEBSITE -> SITE DISCOVERY -> ROOT PAGE -> SITE MAP -> SUBPAGES -> 
CONTENT EXTRACTION -> STRUCTURED KNOWLEDGE -> BUSINESS KNOWLEDGE -> AGENT CONTEXT

Capacidades del motor:
1. Crawling recursivo interno: descubre rutas y enlaces internos respetando estrictamente
   el dominio configurado.
2. Prevención de loops, duplicados y navegación infinita mediante un conjunto de URLs visitadas
   y límites de profundidad y páginas.
3. Extracción estructurada:
   - Páginas (ruta, título, headings, meta_description, texto limpio)
   - Secciones con ID ancla (#id)
   - Catálogo de servicios y precios
   - Horarios de atención y ubicaciones
   - Políticas oficiales (agendamiento, cancelación, privacidad)
   - Elementos interactivos (formularios, CTAs, botones)
4. Grafo de navegación y mapa de conocimiento navegable (SiteKnowledgeGraph).
5. Búsqueda y recuperación contextual con atribución a la página y sección de origen.
6. Capacidad de corrección y actualización manual desde el Workspace.
"""

from __future__ import annotations
import re
import os
import json
import logging
import urllib.parse
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Set, Tuple
from collections import deque
import bs4

log = logging.getLogger("firby.operator.site_discovery")


@dataclass
class DiscoveredSection:
    """Sección ancla o bloque temático dentro de una página."""
    section_id: str
    title: str
    content: str
    key_topics: List[str] = field(default_factory=list)
    ctas: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "section_id": self.section_id,
            "title": self.title,
            "content": self.content,
            "key_topics": self.key_topics,
            "ctas": self.ctas
        }


@dataclass
class DiscoveredElement:
    """Elemento interactivo (formulario, campo, botón, CTA) descubierto."""
    element_type: str  # form, button, input, cta
    label: str
    target_action: str
    selector: str = ""
    fields: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "element_type": self.element_type,
            "label": self.label,
            "target_action": self.target_action,
            "selector": self.selector,
            "fields": self.fields
        }


@dataclass
class DiscoveredPage:
    """Página del sitio descubierta e indexada."""
    path: str
    url: str
    title: str
    meta_description: str = ""
    headings: List[str] = field(default_factory=list)
    sections: List[DiscoveredSection] = field(default_factory=list)
    clean_text: str = ""
    internal_links: List[str] = field(default_factory=list)
    interactive_elements: List[DiscoveredElement] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "path": self.path,
            "url": self.url,
            "title": self.title,
            "meta_description": self.meta_description,
            "headings": self.headings,
            "sections": [s.to_dict() for s in self.sections],
            "clean_text": self.clean_text[:500] + ("..." if len(self.clean_text) > 500 else ""),
            "internal_links": self.internal_links,
            "interactive_elements": [e.to_dict() for e in self.interactive_elements]
        }


@dataclass
class DiscoveredService:
    """Servicio o tratamiento detectado en la web."""
    name: str
    description: str
    price_str: str = ""
    duration_str: str = ""
    source_page: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "price_str": self.price_str,
            "duration_str": self.duration_str,
            "source_page": self.source_page
        }


@dataclass
class DiscoveredPolicy:
    """Política oficial identificada en la web."""
    policy_type: str  # booking, cancellation, privacy, refund, data
    summary: str
    source_page: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "policy_type": self.policy_type,
            "summary": self.summary,
            "source_page": self.source_page
        }


@dataclass
class DiscoveredContact:
    """Canal de contacto u horario detectado."""
    contact_type: str  # phone, email, whatsapp, location, hours
    value: str
    source_page: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "contact_type": self.contact_type,
            "value": self.value,
            "source_page": self.source_page
        }


@dataclass
class SiteKnowledgeMatch:
    """Coincidencia factual con atribución a la página o sección de origen."""
    source_page: str
    source_section: Optional[str]
    title: str
    excerpt: str
    score: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source_page": self.source_page,
            "source_section": self.source_section,
            "title": self.title,
            "excerpt": self.excerpt,
            "score": self.score
        }


class SiteKnowledgeGraph:
    """
    Grafo estructurado de conocimiento y navegación del sitio web.
    Representa todo lo que Firby ha descubierto y entendido del negocio.
    """

    def __init__(self, base_domain: str = "firbyai.com"):
        self.base_domain = base_domain
        self.pages: Dict[str, DiscoveredPage] = {}
        self.sections_by_id: Dict[str, Tuple[str, DiscoveredSection]] = {}  # sec_id -> (page_path, section)
        self.services: List[DiscoveredService] = []
        self.policies: List[DiscoveredPolicy] = []
        self.contacts: List[DiscoveredContact] = []
        self.navigation_graph: Dict[str, List[str]] = {}  # page_path -> [linked_paths]

    def add_page(self, page: DiscoveredPage):
        self.pages[page.path] = page
        self.navigation_graph[page.path] = page.internal_links
        for s in page.sections:
            if s.section_id:
                clean_id = s.section_id.replace("#", "")
                self.sections_by_id[clean_id] = (page.path, s)

    def search_knowledge(self, query: str, top_k: int = 3) -> List[SiteKnowledgeMatch]:
        """
        Búsqueda contextual que recupera los fragmentos más relevantes
        e identifica con precisión en qué página y sección se encuentran.
        """
        q_tokens = self._tokenize(query)
        if not q_tokens:
            return []

        scored_matches: List[SiteKnowledgeMatch] = []

        # 1. Buscar en secciones específicas
        for sec_id, (page_path, sec) in self.sections_by_id.items():
            sec_text = f"{sec.title} {sec.content} {' '.join(sec.key_topics)}"
            score = self._compute_similarity(q_tokens, sec_text)
            if score > 0.08:
                scored_matches.append(SiteKnowledgeMatch(
                    source_page=page_path,
                    source_section=f"#{sec_id}",
                    title=sec.title or sec_id,
                    excerpt=sec.content[:340].strip(),
                    score=score + 0.12  # Bonus por ser sección ancla específica
                ))

        # 2. Buscar en páginas completas
        for path, page in self.pages.items():
            page_text = f"{page.title} {page.meta_description} {' '.join(page.headings)} {page.clean_text}"
            score = self._compute_similarity(q_tokens, page_text)
            if score > 0.08:
                scored_matches.append(SiteKnowledgeMatch(
                    source_page=path,
                    source_section=None,
                    title=page.title,
                    excerpt=page.clean_text[:300].strip(),
                    score=score
                ))

        scored_matches.sort(key=lambda x: x.score, reverse=True)

        # Deduplicar por página/sección
        seen = set()
        unique_matches = []
        for m in scored_matches:
            key = f"{m.source_page}:{m.source_section or ''}"
            if key not in seen:
                seen.add(key)
                unique_matches.append(m)
                if len(unique_matches) >= top_k:
                    break

        return unique_matches

    def get_navigation_map(self) -> List[Dict[str, Any]]:
        """Retorna una lista limpia de todas las rutas y secciones navegables."""
        nav_items = []
        for path, page in self.pages.items():
            item = {
                "path": path,
                "title": page.title,
                "sections": [{"id": f"#{s.section_id}", "title": s.title} for s in page.sections]
            }
            nav_items.append(item)
        return nav_items

    def to_dict(self) -> Dict[str, Any]:
        return {
            "base_domain": self.base_domain,
            "total_pages": len(self.pages),
            "pages": {p: page.to_dict() for p, page in self.pages.items()},
            "services": [s.to_dict() for s in self.services],
            "policies": [p.to_dict() for p in self.policies],
            "contacts": [c.to_dict() for c in self.contacts],
            "navigation_graph": self.navigation_graph
        }

    def _tokenize(self, text: str) -> Set[str]:
        stopwords = {
            "el", "la", "los", "las", "un", "una", "de", "del", "al", "a", "en", "con", "por",
            "para", "que", "como", "cual", "quien", "este", "esta", "ese", "mi", "tu", "su",
            "y", "o", "pero", "si", "no", "mas", "es", "son", "hay", "tiene", "tienen", "me", "te"
        }
        words = re.findall(r'\b[a-záéíóúüñA-ZÁÉÍÓÚÜÑ]{3,}\b', text.lower())
        return {w for w in words if w not in stopwords}

    def _compute_similarity(self, query_tokens: Set[str], target_text: str) -> float:
        target_lower = target_text.lower()
        matches = 0
        for token in query_tokens:
            if token in target_lower:
                count = target_lower.count(token)
                matches += min(count, 3)
        if not query_tokens:
            return 0.0
        return matches / (len(query_tokens) * 2.0)


# Alias de retrocompatibilidad
SiteMapKnowledge = SiteKnowledgeGraph


class SiteCrawler:
    """
    Crawler autónomo con prevención de loops, límites de dominio y profundidad.
    Descubre progresivamente todas las páginas internas de un sitio.
    """

    def __init__(self, base_domain: str, max_pages: int = 50, max_depth: int = 4):
        self.base_domain = base_domain.lower().replace("http://", "").replace("https://", "").split("/")[0]
        self.max_pages = max_pages
        self.max_depth = max_depth
        self.visited_urls: Set[str] = set()

    def is_internal_url(self, url: str) -> bool:
        """Verifica si una URL pertenece estrictamente al dominio autorizado."""
        if not url:
            return False
        # Rutas relativas son internas
        if url.startswith("/") and not url.startswith("//"):
            return True
        if url.startswith("#"):
            return False
        parsed = urllib.parse.urlparse(url)
        netloc = parsed.netloc.lower().split(":")[0]
        return netloc == self.base_domain or netloc.endswith("." + self.base_domain)

    def normalize_route(self, url: str) -> str:
        """Normaliza una URL a ruta absoluta interna sin parámetros ni fragmentos irrelevantes."""
        if not url:
            return "/"
        parsed = urllib.parse.urlparse(url)
        path = parsed.path or "/"
        # Normalizar trailing slash
        if len(path) > 1 and path.endswith("/"):
            path = path[:-1]
        return path


class SiteDiscoveryEngine:
    """
    Motor Maestro de Ingesta y Descubrimiento del Sitio Web.
    Soporta sitios locales (archivos HTML) y sitios remotos (HTTP).
    """

    _cached_graphs: Dict[str, SiteKnowledgeGraph] = {}

    @classmethod
    def get_or_create_graph(cls, tenant_id: str = "firby_landing") -> SiteKnowledgeGraph:
        """Obtiene o inicializa el grafo de conocimiento para un tenant."""
        if tenant_id not in cls._cached_graphs:
            cls._cached_graphs[tenant_id] = cls.ingest_local_static_site()
        return cls._cached_graphs[tenant_id]

    @classmethod
    def ingest_local_static_site(
        cls,
        static_dir: str = "/home/ubuntu/firby/src/interfaces/web/static",
        tenant_id: str = "firby_landing"
    ) -> SiteKnowledgeGraph:
        """
        Descubre e indexa las páginas HTML del sitio web local.
        Permite que el agente conozca al 100% las rutas, secciones y contenido.
        """
        graph = SiteKnowledgeGraph(base_domain="firbyai.com")

        route_mapping = {
            "firby-landing.html": "/",
            "about-us.html": "/sobre-nosotros",
            "faq.html": "/faq",
            "terms.html": "/terminos",
            "privacy.html": "/politica-de-privacidad",
            "data-agreement.html": "/data-agreement",
            "sign-up.html": "/sign-up",
            "sign-in.html": "/sign-in"
        }

        for filename, route_path in route_mapping.items():
            full_path = os.path.join(static_dir, filename)
            if not os.path.isfile(full_path):
                continue

            try:
                with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                    html_content = f.read()

                discovered_page = cls._parse_html(html_content, route_path, base_domain="firbyai.com")
                graph.add_page(discovered_page)

                # Extraer servicios y políticas detectadas
                cls._extract_entities_from_page(discovered_page, graph)
                log.info(f"[SiteDiscovery] Página indexada: {route_path} ({len(discovered_page.sections)} secciones)")
            except Exception as e:
                log.warning(f"[SiteDiscovery] Error indexando {filename}: {e}")

        cls._cached_graphs[tenant_id] = graph
        return graph

    @classmethod
    async def crawl_live_url(
        cls,
        root_url: str,
        tenant_id: str = "custom_tenant",
        max_pages: int = 30,
        max_depth: int = 3
    ) -> SiteKnowledgeGraph:
        """
        Crawl en vivo de un sitio web del cliente vía HTTP.
        Respeta dominios, previene loops y extrae la estructura completa.
        """
        import httpx
        parsed_root = urllib.parse.urlparse(root_url)
        base_domain = parsed_root.netloc or "client-site.com"
        crawler = SiteCrawler(base_domain=base_domain, max_pages=max_pages, max_depth=max_depth)
        graph = SiteKnowledgeGraph(base_domain=base_domain)

        queue = deque([(root_url, 0)])
        crawler.visited_urls.add(crawler.normalize_route(root_url))

        async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
            while queue and len(graph.pages) < max_pages:
                current_url, depth = queue.popleft()
                current_route = crawler.normalize_route(current_url)

                try:
                    res = await client.get(current_url, headers={"User-Agent": "FirbySiteDiscovery/2.0"})
                    if res.status_code != 200 or "text/html" not in res.headers.get("content-type", ""):
                        continue

                    page = cls._parse_html(res.text, current_route, base_domain=base_domain)
                    graph.add_page(page)
                    cls._extract_entities_from_page(page, graph)

                    if depth < max_depth:
                        for link in page.internal_links:
                            norm_link = crawler.normalize_route(link)
                            if norm_link not in crawler.visited_urls and crawler.is_internal_url(link):
                                crawler.visited_urls.add(norm_link)
                                abs_link = urllib.parse.urljoin(root_url, link)
                                queue.append((abs_link, depth + 1))
                except Exception as e:
                    log.warning(f"[SiteDiscovery] Fallo crawling en {current_url}: {e}")

        cls._cached_graphs[tenant_id] = graph
        return graph

    @classmethod
    def _parse_html(cls, html: str, path: str, base_domain: str = "firbyai.com") -> DiscoveredPage:
        """Parsea el HTML usando BeautifulSoup para extraer títulos, secciones, links y CTAs."""
        soup = bs4.BeautifulSoup(html, "html.parser")

        # 1. Título
        title_el = soup.find("title")
        title = title_el.get_text(strip=True) if title_el else path

        # 2. Meta descripción
        meta_desc_el = soup.find("meta", attrs={"name": re.compile(r"description", re.I)})
        meta_desc = meta_desc_el.get("content", "").strip() if meta_desc_el else ""

        # 3. Encabezados
        headings = []
        for h in soup.find_all(["h1", "h2", "h3"]):
            text = h.get_text(strip=True)
            if text and len(text) > 2 and text not in headings:
                headings.append(text)

        # 4. Secciones identificadas por id="..."
        sections = []
        for sec in soup.find_all(["section", "div", "article"], id=True):
            sec_id = sec.get("id", "").strip()
            if not sec_id or sec_id in ["root", "__next", "app"]:
                continue

            h_child = sec.find(["h1", "h2", "h3", "h4"])
            sec_title = h_child.get_text(strip=True) if h_child else sec_id

            # Texto limpio dentro de la sección
            sec_clean = cls._clean_text(sec.get_text(separator=" ", strip=True))
            if len(sec_clean) < 15:
                continue

            sec_topics = [w for w in cls._extract_topics(sec_clean) if len(w) > 3][:8]
            
            # CTAs dentro de la sección
            ctas = []
            for btn in sec.find_all(["a", "button"]):
                b_text = btn.get_text(strip=True)
                if b_text and len(b_text) < 40:
                    ctas.append(b_text)

            sections.append(DiscoveredSection(
                section_id=sec_id,
                title=sec_title,
                content=sec_clean[:650],
                key_topics=sec_topics,
                ctas=ctas[:5]
            ))

        # 5. Enlaces internos
        internal_links = []
        crawler = SiteCrawler(base_domain=base_domain)
        for a in soup.find_all("a", href=True):
            href = a["href"].strip()
            if crawler.is_internal_url(href):
                norm = crawler.normalize_route(href)
                if norm not in internal_links:
                    internal_links.append(norm)

        # 6. Elementos interactivos (formularios, inputs, CTAs)
        interactive_elements = []
        for form in soup.find_all("form"):
            form_action = form.get("action", "") or form.get("id", "form")
            inputs = [inp.get("name") or inp.get("placeholder") or "campo" for inp in form.find_all(["input", "textarea", "select"])]
            interactive_elements.append(DiscoveredElement(
                element_type="form",
                label=f"Formulario {form_action}",
                target_action=form_action,
                fields=[str(i) for i in inputs if i][:6]
            ))

        # 7. Texto limpio general
        clean_text = cls._clean_text(soup.get_text(separator=" ", strip=True))

        return DiscoveredPage(
            path=path,
            url=f"https://{base_domain}{path}",
            title=title,
            meta_description=meta_desc,
            headings=headings[:15],
            sections=sections,
            clean_text=clean_text[:3000],
            internal_links=internal_links[:25],
            interactive_elements=interactive_elements
        )

    @classmethod
    def _extract_entities_from_page(cls, page: DiscoveredPage, graph: SiteKnowledgeGraph):
        """Detecta entidades de servicios, políticas y contacto a partir del contenido de la página."""
        text = page.clean_text

        # Detectar teléfonos / WhatsApp
        phones = re.findall(r'(?:\+57\s*|57\s*)?[3][0-9]{2}[\s\-]?[0-9]{3}[\s\-]?[0-9]{4}', text)
        for ph in set(phones):
            graph.contacts.append(DiscoveredContact(
                contact_type="phone",
                value=ph.strip(),
                source_page=page.path
            ))

        # Detectar correos electrónicos
        emails = re.findall(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', text)
        for em in set(emails):
            if not em.endswith(".png") and not em.endswith(".jpg"):
                graph.contacts.append(DiscoveredContact(
                    contact_type="email",
                    value=em.strip(),
                    source_page=page.path
                ))

        # Detectar precios y servicios en tablas o bloques
        price_matches = re.findall(r'(\$[0-9]{2,3}(?:\.[0-9]{3})*|\$[0-9]{2,4}\s*USD)', text)
        if price_matches:
            for s in page.sections:
                if any(p in s.content for p in price_matches):
                    graph.services.append(DiscoveredService(
                        name=s.title,
                        description=s.content[:160],
                        price_str=price_matches[0],
                        source_page=page.path
                    ))

        # Detectar políticas
        if "cancel" in text.lower() or "reembolso" in text.lower():
            graph.policies.append(DiscoveredPolicy(
                policy_type="cancellation",
                summary="Política de cancelación y reprogramación descubierta en el sitio.",
                source_page=page.path
            ))

        if "privacidad" in page.path or "privacy" in page.path:
            graph.policies.append(DiscoveredPolicy(
                policy_type="privacy",
                summary="Tratamiento y protección de datos personales según la ley colombiana.",
                source_page=page.path
            ))

    @staticmethod
    def _clean_text(text: str) -> str:
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    @staticmethod
    def _extract_topics(text: str) -> List[str]:
        words = re.findall(r'\b[a-záéíóúüñA-ZÁÉÍÓÚÜÑ]{4,}\b', text.lower())
        freq: Dict[str, int] = {}
        for w in words:
            freq[w] = freq.get(w, 0) + 1
        return sorted(freq, key=freq.get, reverse=True)


# Instancia singleton del mapa de conocimiento del sitio
site_knowledge_engine = SiteDiscoveryEngine.ingest_local_static_site()
