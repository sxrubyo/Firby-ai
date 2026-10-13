# -*- coding: utf-8 -*-
"""Motor de búsquedas web e integraciones SerpAPI, Brave y Apify modularizado de globals.py."""
from __future__ import annotations
import os
import re
import json
import logging
import random
from typing import List, Dict, Tuple, Optional, Any, Set

log = logging.getLogger("firby.search")

# Proxies dinámicos para evitar import circular en la inicialización
from src.firby.core.proxy import GlobalProxy

Config = GlobalProxy("Config")
httpx = GlobalProxy("httpx")
_normalize_conv_text = GlobalProxy("_normalize_conv_text")
_EXTERNAL_SEARCH = GlobalProxy("_EXTERNAL_SEARCH")
_ExternalSearchEngine = GlobalProxy("_ExternalSearchEngine")

class WebSearchEngine:
    """
    Motor de busqueda. Si search.py esta disponible lo usa (SerpAPI -> Brave -> Apify).
    V9 Upgrade: Soporte para rotación masiva de 20+ claves (estilo OpenClaw).
    """

    def __init__(self):
        if _EXTERNAL_SEARCH:
            self._ext = _ExternalSearchEngine()
            log.info("[search] usando search.py externo (SerpAPI disponible)")
        else:
            self._ext = None
            log.info("[search] search.py no encontrado, usando motor interno")
        
        # Colección de llaves masiva
        self.brave_keys = Config.BRAVE_API_KEYS or ([Config.BRAVE_API_KEY] if Config.BRAVE_API_KEY else [])
        self.apify_keys = Config.APIFY_API_KEYS or ([Config.APIFY_API_KEY] if Config.APIFY_API_KEY else [])
        self.serp_keys  = Config.SERP_API_KEYS  or ([Config.SERP_API_KEY]  if Config.SERP_API_KEY  else [])
        # Compatibilidad con rutas legacy que todavía leen attrs singulares.
        self.brave_key = self.brave_keys[0] if self.brave_keys else ""
        self.apify_key = self.apify_keys[0] if self.apify_keys else ""
        self.serp_key = self.serp_keys[0] if self.serp_keys else ""
        
        # Índices para rotación simple (Round Robin)
        self._brave_idx = 0
        self._apify_idx = 0
        self._serp_idx  = 0

    def _next_key(self, keys: List[str], current_idx: int) -> Tuple[str, int]:
        if not keys: return "", 0
        idx = current_idx % len(keys)
        return keys[idx], idx + 1

    async def search(self, query: str, context: str = "") -> str:
        """Busqueda con contexto. Usa motor externo si disponible."""
        if self._ext:
            return await self._ext.search(query, context=context)
        return await self._fallback_search(query, context)

    async def medical(self, procedure: str, question: str = "",
                      patient_age: int = None,
                      clinic_services: list = None) -> str:
        """Busqueda medica especializada."""
        if self._ext:
            return await self._ext.medical(procedure, question, patient_age, clinic_services)
        q = f"{procedure} tratamiento estetico beneficios edad Medellin {question}"
        return await self._fallback_search(q, "")

    def detect_procedure(self, text: str):
        if self._ext:
            return self._ext.detect_procedure(text)
        return None

    def extract_age(self, text: str):
        if self._ext:
            return self._ext.extract_age(text)
        return None

    async def _fallback_search(self, query: str, context: str) -> str:
        """Motor interno de fallback: Rotación de SerpAPI -> Brave -> Apify."""
        full_query = f"{context} {query}".strip() if context else query

        # 1. SerpAPI (si hay keys)
        for _ in range(len(self.serp_keys)):
            key, self._serp_idx = self._next_key(self.serp_keys, self._serp_idx)
            result = await self._serp_search(full_query, key)
            if result: return result

        # 2. Brave (si hay keys)
        for _ in range(len(self.brave_keys)):
            key, self._brave_idx = self._next_key(self.brave_keys, self._brave_idx)
            result = await self._brave_search(full_query, key)
            if result: return result

        # 3. Apify (si hay keys)
        for _ in range(len(self.apify_keys)):
            key, self._apify_idx = self._next_key(self.apify_keys, self._apify_idx)
            result = await self._apify_search(full_query, key)
            if result: return result

        return ""

    async def _serp_search(self, query: str, key: str) -> str:
        if not key: return ""
        try:
            async with httpx.AsyncClient(timeout=12.0) as client:
                r = await client.get(
                    "https://serpapi.com/search",
                    params={"engine": "google", "q": query, "api_key": key,
                            "hl": "es", "gl": "co", "num": 5, "safe": "active"},
                )
                if r.status_code == 429: return ""
                r.raise_for_status()
                data = r.json()
                parts = []
                ab = data.get("answer_box", {})
                if ab:
                    s = ab.get("answer") or ab.get("snippet") or ""
                    if s: parts.append(s.strip()[:600])
                for res in data.get("organic_results", [])[:4]:
                    link_str = f" (Link: {res['link']})" if res.get("link") else ""
                    if res.get("snippet"):
                        parts.append(f"{res['snippet'][:300]}{link_str}")
                    elif res.get("title"):
                        parts.append(f"{res['title']}{link_str}")
                return "\n".join(parts)[:1500]
        except Exception:
            return ""

    async def _brave_search(self, query: str, key: str, count: int = 5) -> str:
        if not key: return ""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                r = await client.get(
                    "https://api.search.brave.com/res/v1/web/search",
                    headers={"Accept": "application/json",
                             "X-Subscription-Token": key},
                    params={"q": query, "count": count, "search_lang": "es", "country": "ALL"},
                )
                if r.status_code == 429: return ""
                r.raise_for_status()
                data = r.json()
                results = data.get("web", {}).get("results", [])
                snippets = [res.get("description", "") for res in results if res.get("description")]
                return " ".join(snippets)[:1200]
        except Exception:
            return ""

    async def _apify_search(self, query: str, key: str) -> str:
        if not key: return ""
        try:
            async with httpx.AsyncClient(timeout=25.0) as client:
                r = await client.post(
                    "https://api.apify.com/v2/acts/apify~google-search-scraper/run-sync-get-dataset-items",
                    headers={"Authorization": f"Bearer {key}"},
                    json={"queries": query, "maxPagesPerQuery": 1,
                          "resultsPerPage": 5, "languageCode": "es", "countryCode": "co"},
                    params={"timeout": 20, "memory": 256},
                )
                if r.status_code == 429: return ""
                r.raise_for_status()
                items = r.json()
                if items and isinstance(items, list):
                    snippets = []
                    for item in items[:1]:
                        for res in item.get("organicResults", [])[:5]:
                            if res.get("description"):
                                snippets.append(res["description"])
                    if snippets:
                        return " ".join(snippets)[:1200]
        except Exception:
            return ""

    async def _apify_search_candidates(self, query: str, count: int = 5) -> List[Dict]:
        if not self.apify_keys:
            return []
        for apify_key in self.apify_keys:
            try:
                async with httpx.AsyncClient(timeout=25.0) as client:
                    r = await client.post(
                        "https://api.apify.com/v2/acts/apify~google-search-scraper/run-sync-get-dataset-items",
                        headers={"Authorization": f"Bearer {apify_key}"},
                        json={
                            "queries": query,
                            "maxPagesPerQuery": 1,
                            "resultsPerPage": count,
                            "languageCode": "es",
                            "countryCode": "co",
                        },
                        params={"timeout": 20, "memory": 256},
                    )
                    r.raise_for_status()
                    items = r.json()
                    if not items or not isinstance(items, list):
                        continue
                    results = []
                    for item in items[:1]:
                        for res in item.get("organicResults", [])[:count]:
                            results.append({
                                "title": res.get("title", ""),
                                "url": res.get("url", ""),
                                "description": res.get("description", ""),
                            })
                    if results:
                        return results
            except Exception as e:
                log.warning(f"Apify candidate search error: {e}")
                continue
        return []

    async def search_business_link(
        self,
        nombre: str,
        excluded_urls: Optional[set] = None,
        context_hint: str = "",
    ) -> tuple:
        """
        Busca un negocio y devuelve (snippet_text, url).
        Prioridad: Google Maps → website oficial → primer organic result.
        """
        from urllib.parse import urlparse

        nombre_clean = " ".join(str(nombre or "").split()).strip()
        nombre_norm = _normalize_conv_text(nombre_clean)
        hint_clean = " ".join(str(context_hint or "").split()).strip()
        hint_norm = _normalize_conv_text(hint_clean)
        query_variants: List[str] = []

        def _push_query(candidate_query: str) -> None:
            normalized = " ".join(str(candidate_query or "").split()).strip()
            if normalized and normalized not in query_variants:
                query_variants.append(normalized)

        if hint_clean:
            _push_query(f"{nombre_clean} {hint_clean}")
            if "colombia" not in hint_norm:
                _push_query(f"{nombre_clean} {hint_clean} Colombia")
        _push_query(nombre_clean if "colombia" in nombre_norm else f"{nombre_clean} Colombia")

        excluded = {u for u in (excluded_urls or set()) if u}
        serp_keys = getattr(self, "serp_keys", None) or ([getattr(self, "serp_key", "")] if getattr(self, "serp_key", "") else [])
        brave_keys = getattr(self, "brave_keys", None) or ([getattr(self, "brave_key", "")] if getattr(self, "brave_key", "") else [])
        apify_keys = getattr(self, "apify_keys", None) or ([getattr(self, "apify_key", "")] if getattr(self, "apify_key", "") else [])
        url   = ""
        text  = ""
        skip = [
            "facebook.com/pages","facebook.com/p/","facebook.com/profile",
            "amarillasinternet","paginasamarillas","directorio",
            "yelp","foursquare","tripadvisor","cylex","infobel",
            "clinicasesteticas.com","bookimed.com","doctoralia","topdoctors",
            "treatwell","multiestetica","medicosdoc",
            "wikipedia.org","es.wikipedia.org","en.wikipedia.org","wikimedia.org","wiktionary.org",
            "reddit.com","quora.com","tiktok.com","youtube.com/watch",
        ]
        bad_social_fragments = ("/reel/", "/p/", "/tv/", "facebook.com/reel", "facebook.com/watch")
        directory_markers = (
            "doctores de", "mejores especialistas", "encuentre los mejores",
            "cerca de", "top ", "ranking", "listado", "centros de",
            "clinicasesteticas", "bookimed", "doctoralia", "top doctors",
        )
        generic_tokens = {
            "clinica", "clinicas", "clinic", "hospital", "centro", "centros", "medicina",
            "medico", "medicos", "medica", "medicas", "estetica", "estetico", "esteticos",
            "spa", "salud", "medical", "colombia", "medellin", "medellín", "bogota",
            "bogotá", "consultorio", "ips", "sas", "sede", "oficial", "instagram",
            "servicios", "servicio", "grupo", "empresa", "negocio", "esteticos", "esteticas",
        }
        name_tokens = [
            tok for tok in re.findall(r"[a-z0-9áéíóúüñ]+", nombre_norm)
            if len(tok) >= 3
        ]
        strong_tokens = [tok for tok in name_tokens if tok not in generic_tokens]

        anchor_families = {
            "clinica": ("clinica", "clinic"),
            "hospital": ("hospital",),
            "dental": ("dental", "odont", "odontologia", "odontológica", "odontologica"),
            "laboratorio": ("laboratorio", "laboratories", "lab"),
        }

        required_anchor = None
        for anchor_name, variants in anchor_families.items():
            if any(variant in nombre_norm for variant in variants):
                required_anchor = (anchor_name, variants)
                break

        candidates: List[Dict[str, Any]] = []

        def _accept_url(candidate: str) -> bool:
            if not candidate:
                return False
            if any(s in candidate for s in skip):
                return False
            if any(fragment in candidate for fragment in bad_social_fragments):
                return False
            if candidate in excluded:
                return False
            return True

        def _norm_join(*parts: str) -> str:
            return _normalize_conv_text(" ".join(part for part in parts if part))

        def _register_candidate(source: str, candidate_url: str, title: str = "", description: str = "") -> None:
            if not _accept_url(candidate_url):
                return
            candidates.append({
                "source": source,
                "url": candidate_url,
                "title": title or "",
                "description": description or "",
            })

        def _candidate_score(candidate: Dict[str, Any]) -> Optional[int]:
            candidate_url = candidate.get("url", "") or ""
            title = candidate.get("title", "") or ""
            description = candidate.get("description", "") or ""
            haystack = _norm_join(title, description, candidate_url)
            title_url_haystack = _norm_join(title, candidate_url)
            domain = _normalize_conv_text(urlparse(candidate_url).netloc or "")

            if required_anchor and not any(variant in title_url_haystack for variant in required_anchor[1]):
                return None

            exact_name = bool(nombre_norm and nombre_norm in haystack)
            matched_name_tokens = [tok for tok in name_tokens if tok in haystack]
            matched_strong_tokens = [tok for tok in strong_tokens if tok in haystack]
            title_strong_tokens = [tok for tok in strong_tokens if tok in title_url_haystack]
            domain_strong_tokens = [tok for tok in strong_tokens if tok in domain]

            if strong_tokens:
                if not exact_name and not title_strong_tokens and not domain_strong_tokens:
                    return None
            elif len(matched_name_tokens) < 2 and not exact_name:
                return None

            if any(marker in haystack for marker in directory_markers) and not exact_name:
                return None

            source_bonus = {
                "local_maps": 10,
                "local_website": 7,
                "knowledge_graph": 6,
                "organic": 2,
                "brave": 1,
                "apify": 1,
            }.get(candidate.get("source", ""), 0)

            score = source_bonus
            score += 6 if exact_name else 0
            score += len(title_strong_tokens) * 4
            score += len(domain_strong_tokens) * 3
            score += len(matched_strong_tokens) * 1
            score += min(len(matched_name_tokens), 3)

            if "instagram.com" in candidate_url or "facebook.com" in candidate_url:
                score -= 2
                if not title_strong_tokens and not domain_strong_tokens:
                    return None

            if strong_tokens and len(strong_tokens) == 1 and required_anchor is None:
                lone_token = strong_tokens[0]
                if lone_token in description.lower() and lone_token not in title_url_haystack and lone_token not in domain:
                    return None

            return score

        def _select_best_candidate() -> Optional[Dict[str, Any]]:
            scored: List[Tuple[int, Dict[str, Any]]] = []
            for candidate in candidates:
                score = _candidate_score(candidate)
                if score is None:
                    continue
                scored.append((score, candidate))
            if not scored:
                return None
            scored.sort(key=lambda item: item[0], reverse=True)
            best_score, best_candidate = scored[0]
            if best_score < 5:
                return None
            return best_candidate

        # ── SerpAPI: Maps + Knowledge Graph + Organic ─────────────────────────
        for query in query_variants:
            if serp_keys:
                for key in serp_keys:
                    if not key:
                        continue
                    try:
                        async with httpx.AsyncClient(timeout=12.0) as client:
                            r = await client.get(
                                "https://serpapi.com/search",
                                params={"engine": "google", "q": query, "api_key": key,
                                        "hl": "es", "gl": "co", "num": 5},
                            )
                            r.raise_for_status()
                            data = r.json()

                            local_raw = data.get("local_results") or {}
                            if isinstance(local_raw, dict):
                                local_places = local_raw.get("places") or local_raw.get("results") or []
                            elif isinstance(local_raw, list):
                                local_places = local_raw
                            else:
                                local_places = []
                            first_local = local_places[0] if local_places and isinstance(local_places[0], dict) else {}

                            if first_local:
                                maps_link = (first_local.get("links", {}).get("directions")
                                             or first_local.get("place_id_search")
                                             or "")
                                website   = first_local.get("links", {}).get("website", "")
                                title = first_local.get("title", "")
                                biz_type = first_local.get("type", "")
                                addr = first_local.get("address", "")
                                rating = first_local.get("rating", "")
                                local_desc_parts = []
                                if biz_type:
                                    local_desc_parts.append(f"Tipo: {biz_type}")
                                if addr:
                                    local_desc_parts.append(f"Dirección: {addr}")
                                if rating:
                                    local_desc_parts.append(f"Rating: {rating}")
                                local_desc = " | ".join(local_desc_parts)
                                _register_candidate("local_maps", maps_link, title, local_desc)
                                _register_candidate("local_website", website, title, local_desc)

                            kg  = data.get("knowledge_graph", {})
                            local_map = data.get("local_map") or {}
                            candidate_url = (kg.get("website") or kg.get("local_map", "") or local_map.get("link", "") or "")
                            _register_candidate(
                                "knowledge_graph",
                                candidate_url,
                                kg.get("title", ""),
                                kg.get("description", ""),
                            )

                            for res in data.get("organic_results", [])[:5]:
                                _register_candidate(
                                    "organic",
                                    res.get("link", ""),
                                    res.get("title", ""),
                                    res.get("snippet", ""),
                                )
                        if _select_best_candidate():
                            break
                    except Exception as e:
                        log.warning(f"[search_link] SerpAPI error: {e}")
                if _select_best_candidate():
                    break

            if brave_keys:
                for key in brave_keys:
                    if not key:
                        continue
                    try:
                        async with httpx.AsyncClient(timeout=10.0) as client:
                            r = await client.get(
                                "https://api.search.brave.com/res/v1/web/search",
                                headers={"Accept": "application/json",
                                         "X-Subscription-Token": key},
                                params={"q": query, "count": 5, "search_lang": "es", "country": "ALL"},
                            )
                            r.raise_for_status()
                            results = r.json().get("web", {}).get("results", [])
                            for res in results[:5]:
                                _register_candidate(
                                    "brave",
                                    res.get("url", ""),
                                    res.get("title", ""),
                                    res.get("description", ""),
                                )
                        if _select_best_candidate():
                            break
                    except Exception as e:
                        log.warning(f"[search_link] Brave error: {e}")
                if _select_best_candidate():
                    break

            if apify_keys:
                try:
                    apify_results = await self._apify_search_candidates(query, count=6)
                    for res in apify_results:
                        _register_candidate(
                            "apify",
                            res.get("url", ""),
                            res.get("title", ""),
                            res.get("description", ""),
                        )
                    if _select_best_candidate():
                        break
                except Exception as e:
                    log.warning(f"[search_link] Apify error: {e}")

        best_candidate = _select_best_candidate()
        if best_candidate:
            url = best_candidate.get("url", "")
            parts = []
            title = (best_candidate.get("title") or "").strip()
            description = (best_candidate.get("description") or "").strip()
            if title:
                parts.append(f"Negocio: {title}")
            if description:
                parts.append(description[:320])
            text = "\n".join(parts)[:800]

        # ── Fallback: Google Maps (mucho más útil que Google Search para negocios) ──
        if not url:
            import urllib.parse
            url = f"https://www.google.com/maps/search/{urllib.parse.quote(nombre)}+Colombia"
            text = ""

        return text, url


# ═══════════════════════════════════════════════════════════════════════════════
# SISTEMA DE PLUGINS MCP
# ═══════════════════════════════════════════════════════════════════════════════

