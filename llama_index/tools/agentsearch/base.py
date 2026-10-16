"""AgentSearch tool spec."""
from __future__ import annotations

from typing import List, Optional

from llama_index.core.tools.tool_spec.base import BaseToolSpec

from . import _ops


class AgentSearchToolSpec(BaseToolSpec):
    """AgentSearch tool spec: live web search (free by default), plus paid extract and render.

    Args:
        mode: "auto" (paid if a wallet key is set, else free), "free" or "paid". Applies to search only.
    """

    spec_functions = ["search", "extract", "render"]

    def __init__(self, mode: str = "auto") -> None:
        if mode not in ("auto", "free", "paid"):
            raise ValueError("mode must be 'auto', 'free' or 'paid'")
        self.mode = mode

    def search(self, query: str, max_results: Optional[int] = None) -> str:
        """Live web search. Returns JSON with up to 5 ranked results (title, url, content).

        Args:
            query: the search query.
            max_results: 1-5, default 5.
        """
        return _ops.search(query, max_results, self.mode)

    def extract(self, url: str, formats: Optional[List[str]] = None, max_chars: Optional[int] = None,
                render_fallback: Optional[bool] = None) -> str:
        """Fetch a URL and return its main content as clean text/markdown. Best for articles, docs and static pages.
        If the result is empty or thin (JavaScript-heavy page, SPA, app shell), call render on the same URL, or pass
        render_fallback=True to do that automatically (a second $0.005 call). Paid: $0.005 per call (needs a wallet).

        Args:
            url: http(s) URL to extract.
            formats: e.g. ["markdown"].
            max_chars: optional cap on returned characters.
            render_fallback: if extract returns thin content, retry with render (extra $0.005).
        """
        return _ops.paid("extract", url=url, formats=formats, max_chars=max_chars, render_fallback=render_fallback)

    def render(self, url: str, formats: Optional[List[str]] = None, max_chars: Optional[int] = None,
               wait_until: Optional[str] = None, wait_for_selector: Optional[str] = None) -> str:
        """Render a page in a real headless browser. Use when extract returns empty or thin content, or for
        JavaScript-heavy pages (SPAs, content loaded by scripts). Paid: $0.005 per call (needs a wallet).

        Args:
            url: http(s) URL to render.
            formats: any of "markdown", "text", "html", "links".
            max_chars: optional cap on returned characters.
            wait_until: "domcontentloaded", "load" or "networkidle".
            wait_for_selector: CSS selector to wait for.
        """
        return _ops.paid("render", url=url, formats=formats, max_chars=max_chars,
                         wait_until=wait_until, wait_for_selector=wait_for_selector)
