import json
import os

import httpx
import pytest


def mock(monkeypatch, mod, status, body):
    real = httpx.Client
    seen = []

    def handler(r):
        seen.append(r)
        return httpx.Response(status, json=body)
    monkeypatch.setattr(mod.httpx, "Client", lambda **kw: real(transport=httpx.MockTransport(handler)))
    for n in ("AGENTSEARCH_WALLET_PRIVATE_KEY", "POCKET_PRIVATE_KEY"):
        monkeypatch.delenv(n, raising=False)
    return seen

from llama_index.tools.agentsearch import AgentSearchToolSpec
from llama_index.tools.agentsearch import _client


def test_spec_tools():
    names = [t.metadata.name for t in AgentSearchToolSpec().to_tool_list()]
    assert names == ["search", "extract", "render"]


def test_free_search(monkeypatch):
    mock(monkeypatch, _client, 200, {"results": [{"title": "t", "url": "https://a", "content": "c"}]})
    tool = AgentSearchToolSpec().to_tool_list()[0]
    out = json.loads(tool.call(query="hi", max_results=1).content)
    assert out["results"][0]["url"] == "https://a"


def test_paid_without_wallet(monkeypatch):
    seen = mock(monkeypatch, _client, 200, {})
    assert "no call was made" in AgentSearchToolSpec().render("https://example.com") and not seen


@pytest.mark.skipif(not os.environ.get("AGENTSEARCH_LIVE"), reason="set AGENTSEARCH_LIVE=1")
def test_live_free_search():
    out = json.loads(AgentSearchToolSpec(mode="free").search("LlamaIndex tool spec", max_results=2))
    assert out["results"][0]["url"].startswith("http")
