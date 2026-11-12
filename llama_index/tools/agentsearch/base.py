"""AgentSearch tool spec."""
from __future__ import annotations

from typing import List, Optional

from llama_index.core.tools.tool_spec.base import BaseToolSpec

from . import _ops


class AgentSearchToolSpec(BaseToolSpec):
    """AgentSearch tool spec: live web search (free by default), plus paid news, extract, render, screenshot and search-and-read.

    Args:
        mode: "auto" (default), "free" or "paid". Applies to search only. "auto" is free (up to 25
            searches/day per IP) unless AGENTSEARCH_MODE=paid is set; a wallet key alone never switches
            search to paid. If paid is opted in but the [paid] extra is missing, "auto" falls back to free.
    """

    spec_functions = ["search", "news_search", "extract", "render", "screenshot", "search_and_read"]

    def __init__(self, mode: str = "auto") -> None:
        if mode not in ("auto", "free", "paid"):
            raise ValueError("mode must be 'auto', 'free' or 'paid'")
        self.mode = mode

    def search(self, query: str, max_results: Optional[int] = None, freshness: Optional[str] = None,
               date_from: Optional[str] = None, date_to: Optional[str] = None, country: Optional[str] = None,
               language: Optional[str] = None, include_domains: Optional[List[str]] = None,
               exclude_domains: Optional[List[str]] = None) -> str:
        """Live web search. Returns JSON with up to 5 ranked results (title, url, content). Free by default; paid
        search ($0.008) also honors the filters below (free search ignores them). For recent news use news_search.

        Args:
            query: the search query.
            max_results: integer from 1 to 5, default 5. Other values return an error.
            freshness: "day", "week", "month" or "year" (paid only).
            date_from: earliest publish date YYYY-MM-DD (paid only).
            date_to: latest publish date YYYY-MM-DD (paid only).
            country: 2-letter country code such as us or gb (paid only).
            language: language code such as en, es or pt-BR (paid only).
            include_domains: only these domains, up to 5 (paid only).
            exclude_domains: never these domains, up to 5 (paid only).
        """
        return _ops.search(query, max_results, self.mode, freshness=freshness, date_from=date_from, date_to=date_to, country=country,
                       language=language, include_domains=include_domains, exclude_domains=exclude_domains)

    def news_search(self, query: str, max_results: Optional[int] = None, freshness: Optional[str] = None,
               date_from: Optional[str] = None, date_to: Optional[str] = None, country: Optional[str] = None,
               language: Optional[str] = None, include_domains: Optional[List[str]] = None,
               exclude_domains: Optional[List[str]] = None) -> str:
        """Search recent news articles and return title, URL, snippet, source domain and publish date for each (1-10, default 5).
        Use for current events, company or product news, and anything where recency matters. To read an article in full, pass
        its URL to extract. Paid: $0.008 per call via AgentSearch's direct x402 API (no results, no charge; needs a wallet).

        Args:
            query: the news search query.
            max_results: 1-10, default 5.
            freshness: "day", "week", "month" or "year".
            date_from: earliest publish date YYYY-MM-DD.
            date_to: latest publish date YYYY-MM-DD.
            country: 2-letter country code such as us or gb.
            language: language code such as en, es or pt-BR.
            include_domains: only these domains, up to 5.
            exclude_domains: never these domains, up to 5.
        """
        return _ops.news(query, max_results, freshness=freshness, date_from=date_from, date_to=date_to, country=country,
                       language=language, include_domains=include_domains, exclude_domains=exclude_domains)

    def extract(self, url: str, formats: Optional[List[str]] = None, max_chars: Optional[int] = None,
                render_fallback: Optional[bool] = None, include_links: Optional[bool] = None) -> str:
        """Fetch a URL and return its main content as clean text/markdown. Best for articles, docs and static pages.
        If the result is empty or thin (JavaScript-heavy page, SPA, app shell), call render on the same URL, or pass
        render_fallback=True to do that automatically (a second paid call). Paid: $0.004 per call via AgentSearch's x402 API (needs a wallet).

        Args:
            url: http(s) URL to extract.
            formats: e.g. ["markdown"].
            max_chars: optional cap on returned characters (up to 50000).
            render_fallback: if extract returns thin content, retry with render (a second paid call, $0.010).
            include_links: also return the page's links.
        """
        return _ops.paid("extract", url=url, formats=formats, max_chars=max_chars, include_links=include_links,
                         render_fallback=render_fallback)

    def render(self, url: str, formats: Optional[List[str]] = None, max_chars: Optional[int] = None,
               wait_until: Optional[str] = None, wait_for_selector: Optional[str] = None) -> str:
        """Render a page in a real headless browser. Use when extract returns empty or thin content, or for
        JavaScript-heavy pages (SPAs, content loaded by scripts). Paid: $0.010 per call via AgentSearch's x402 API (needs a wallet).

        Args:
            url: http(s) URL to render.
            formats: any of "markdown", "text", "html", "links".
            max_chars: optional cap on returned characters.
            wait_until: "domcontentloaded", "load" or "networkidle".
            wait_for_selector: CSS selector to wait for.
        """
        return _ops.paid("render", url=url, formats=formats, max_chars=max_chars,
                         wait_until=wait_until, wait_for_selector=wait_for_selector)

    def search_and_read(self, query: str, num_results: Optional[int] = None, max_chars: Optional[int] = None,
                        render_fallback: Optional[bool] = None, freshness: Optional[str] = None,
               date_from: Optional[str] = None, date_to: Optional[str] = None, country: Optional[str] = None,
               language: Optional[str] = None, include_domains: Optional[List[str]] = None,
               exclude_domains: Optional[List[str]] = None) -> str:
        """Search the live web and return the top results with each page's main text in one paid call ($0.009 USDC on Base, charged only when at least one page returns text).
        Cheaper than a $0.008 search plus three $0.004 extracts ($0.020) and one payment instead of four. Default 3 results (max 5), default 8000 characters per page (max 20000).
        Pass render_fallback=True to render at most one thin page in the same call. Direct x402 only — not available on Pocket. Search itself stays free by default.

        Args:
            query: the search query.
            num_results: how many top results to read, 1-5, default 3.
            max_chars: max characters of page text per result, default 8000, max 20000.
            render_fallback: if extract is thin, render at most one page in the same $0.009 call.
            freshness: "day", "week", "month" or "year".
            date_from: earliest publish date YYYY-MM-DD.
            date_to: latest publish date YYYY-MM-DD.
            country: 2-letter country code such as us or gb.
            language: language code such as en, es or pt-BR.
            include_domains: only these domains, up to 5.
            exclude_domains: never these domains, up to 5.
        """
        return _ops.search_and_read(query, num_results=num_results, max_chars=max_chars, render_fallback=render_fallback,
                                    freshness=freshness, date_from=date_from, date_to=date_to, country=country,
                       language=language, include_domains=include_domains, exclude_domains=exclude_domains)

    def screenshot(self, url: str, format: Optional[str] = None, full_page: Optional[bool] = None,
                   viewport_width: Optional[int] = None, viewport_height: Optional[int] = None) -> str:
        """Load a public URL in a real headless browser and capture a PNG or JPEG screenshot of the viewport or the full page
        (up to 4000 px tall), plus title, final URL and HTTP status. Use for visual checks and layout or UI questions; for page
        text use extract. The image is saved to a local file and its path is returned (no base64 in the output).
        Paid: $0.010 per call via AgentSearch's direct x402 API (needs a wallet).

        Args:
            url: full public http(s) URL to capture.
            format: "png" (default) or "jpeg".
            full_page: capture the whole page instead of the viewport.
            viewport_width: viewport width in CSS pixels (320-1920), e.g. 390 for mobile; default 1280.
            viewport_height: viewport height in CSS pixels (320-1920), e.g. 844 for mobile; default 800.
        """
        vp = None
        if viewport_width or viewport_height:
            vp = {"width": max(320, min(int(viewport_width or 1280), 1920)), "height": max(320, min(int(viewport_height or 800), 1920))}
        return _ops.screenshot(url, format=format, full_page=full_page, viewport=vp)
