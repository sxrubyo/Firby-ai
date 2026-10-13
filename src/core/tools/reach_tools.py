# -*- coding: utf-8 -*-
"""
Firby Internet & Web Reach Tools (inspired by Agent-Reach).
Provides internet research capabilities: semantic search via Exa MCP,
universal web extraction to markdown via Jina Reader, and GitHub search.
"""
from __future__ import annotations

import json
import logging
import re
import shutil
import subprocess
import urllib.parse
import urllib.request
from typing import Dict, Any, List, Optional

from bs4 import BeautifulSoup

logger = logging.getLogger("firby.reach_tools")

_UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
_MAX_RESPONSE_BYTES = 5 * 1024 * 1024
_ANTIBOT_SCAN_BYTES = 4096


def _is_antibot_page(body: bytes) -> bool:
    """Recognize high-confidence Jina/Cloudflare challenge responses."""
    sample = body[:_ANTIBOT_SCAN_BYTES].decode("utf-8", errors="ignore").casefold()
    jina_captcha_warning = "warning:" in sample and "requiring captcha" in sample
    challenge_structure = any(
        marker in sample
        for marker in (
            "title: just a moment...",
            "## performing security verification",
            "title: attention required! | cloudflare",
        )
    )
    cloudflare_block = "title: attention required! | cloudflare" in sample and (
        "ray id" in sample or "/cdn-cgi/challenge-platform/" in sample
    )
    return (jina_captcha_warning and challenge_structure) or cloudflare_block


class ReachTools:
    """
    Toolkit for internet research, semantic search, and web extraction.
    Integrates Agent-Reach patterns natively.
    """

    def __init__(self):
        self.mcporter_bin = shutil.which("mcporter")

    def web_search(
        self,
        query: str,
        objective: str = "General research",
        num_results: int = 5,
    ) -> Dict[str, Any]:
        """
        Performs semantic web search using Exa MCP via mcporter.
        Falls back to DuckDuckGo instant API if mcporter is unavailable.
        """
        if self.mcporter_bin:
            try:
                cmd = [
                    self.mcporter_bin,
                    "call",
                    "exa.web_search_exa",
                    f"query={query}",
                    f"objective={objective}",
                    f"numResults={num_results}",
                ]
                proc = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=20,
                )
                if proc.returncode == 0 and proc.stdout.strip():
                    return {
                        "success": True,
                        "source": "exa_mcp",
                        "query": query,
                        "content": proc.stdout.strip(),
                    }
                else:
                    logger.warning(f"Exa MCP search returned error or empty: {proc.stderr}")
            except Exception as exc:
                logger.warning(f"Failed to call Exa MCP: {exc}")

        # Fallback: DuckDuckGo HTML/Instant API search
        return self._search_duckduckgo_fallback(query, num_results)

    def _search_duckduckgo_fallback(self, query: str, num_results: int = 5) -> Dict[str, Any]:
        """Simple HTML fallback search on DuckDuckGo."""
        try:
            encoded = urllib.parse.quote_plus(query)
            url = f"https://html.duckduckgo.com/html/?q={encoded}"
            req = urllib.request.Request(
                url,
                headers={"User-Agent": _UA},
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                html = resp.read().decode("utf-8", errors="replace")

            soup = BeautifulSoup(html, "html.parser")
            results = []
            for result_div in soup.find_all("div", class_="result__body")[:num_results]:
                title_elem = result_div.find("a", class_="result__a")
                snippet_elem = result_div.find("a", class_="result__snippet")
                if title_elem:
                    results.append({
                        "title": title_elem.get_text(strip=True),
                        "url": title_elem.get("href", ""),
                        "snippet": snippet_elem.get_text(strip=True) if snippet_elem else "",
                    })

            formatted = "\n\n".join(
                f"Title: {r['title']}\nURL: {r['url']}\nSnippet: {r['snippet']}"
                for r in results
            )
            return {
                "success": True,
                "source": "duckduckgo_fallback",
                "query": query,
                "content": formatted or "No search results found.",
                "results": results,
            }
        except Exception as exc:
            return {
                "success": False,
                "source": "failed",
                "query": query,
                "error": str(exc),
            }

    def fetch_web_page(self, url: str, max_chars: int = 15000) -> Dict[str, Any]:
        """
        Reads any webpage content converted to clean markdown via Jina Reader.
        Falls back to local BeautifulSoup extractor if Jina faces challenges.
        """
        if not url.startswith(("http://", "https://")):
            url = "https://" + url

        jina_url = f"https://r.jina.ai/{url}"
        try:
            req = urllib.request.Request(
                jina_url,
                headers={"User-Agent": _UA, "Accept": "text/plain"},
            )
            with urllib.request.urlopen(req, timeout=25) as resp:
                body = resp.read(_MAX_RESPONSE_BYTES)

            if not _is_antibot_page(body):
                md_content = body.decode("utf-8", errors="replace")
                return {
                    "success": True,
                    "source": "jina_reader",
                    "url": url,
                    "content": md_content[:max_chars],
                    "total_length": len(md_content),
                }
        except Exception as exc:
            logger.warning(f"Jina Reader fetch failed for {url}: {exc}")

        # Local fallback using BeautifulSoup
        return self._fetch_local_fallback(url, max_chars)

    def _fetch_local_fallback(self, url: str, max_chars: int = 15000) -> Dict[str, Any]:
        """Extracts clean text and paragraphs from URL directly using BeautifulSoup."""
        try:
            req = urllib.request.Request(
                url,
                headers={"User-Agent": _UA},
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                html = resp.read().decode("utf-8", errors="replace")

            soup = BeautifulSoup(html, "html.parser")
            # Remove scripts and styles
            for elem in soup(["script", "style", "nav", "footer", "header", "noscript"]):
                elem.extract()

            text = soup.get_text(separator="\n", strip=True)
            # Remove excessive whitespace
            clean_text = re.sub(r"\n{3,}", "\n\n", text)

            title = soup.title.string.strip() if soup.title and soup.title.string else url

            return {
                "success": True,
                "source": "bs4_fallback",
                "url": url,
                "title": title,
                "content": f"# {title}\n\n{clean_text[:max_chars]}",
                "total_length": len(clean_text),
            }
        except Exception as exc:
            return {
                "success": False,
                "source": "failed",
                "url": url,
                "error": str(exc),
            }

    def github_search(self, query: str, num_results: int = 5) -> Dict[str, Any]:
        """
        Searches GitHub repositories using the public GitHub API or gh CLI.
        """
        gh_bin = shutil.which("gh")
        if gh_bin:
            try:
                cmd = [gh_bin, "search", "repos", query, "--limit", str(num_results), "--json", "fullName,description,url,stargazersCount"]
                proc = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
                if proc.returncode == 0:
                    data = json.loads(proc.stdout)
                    return {"success": True, "source": "gh_cli", "results": data}
            except Exception as e:
                logger.warning(f"gh cli search failed: {e}")

        # Public GitHub REST API fallback
        try:
            encoded = urllib.parse.quote(query)
            api_url = f"https://api.github.com/search/repositories?q={encoded}&per_page={num_results}"
            req = urllib.request.Request(
                api_url,
                headers={"User-Agent": "FirbyAI-Autonomous-Agent", "Accept": "application/vnd.github.v3+json"},
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            items = []
            for item in data.get("items", []):
                items.append({
                    "full_name": item.get("full_name"),
                    "description": item.get("description"),
                    "url": item.get("html_url"),
                    "stars": item.get("stargazers_count"),
                })
            return {"success": True, "source": "github_rest_api", "results": items}
        except Exception as exc:
            return {"success": False, "error": str(exc)}
