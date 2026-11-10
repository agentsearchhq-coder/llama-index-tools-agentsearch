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


# ---- 0.2.1 ----
from llama_index.tools import agentsearch as pkg
from llama_index.tools.agentsearch import _ops

FAKE_KEY = "0x" + "11" * 32


def test_top_level_budget_exports():
    assert pkg.session_spent_atomic is _client.session_spent_atomic
    assert pkg.reset_session_budget is _client.reset_session_budget
    pkg.reset_session_budget()
    assert pkg.session_spent_atomic() == 0
    assert {"session_spent_atomic", "reset_session_budget"} <= set(pkg.__all__)


def test_free_limit_message_per_ip():
    assert "per IP" in _client.FREE_LIMIT_MESSAGE and "per user" not in _client.FREE_LIMIT_MESSAGE


def test_free_limit_429_says_per_ip(monkeypatch):
    mock(monkeypatch, _client, 429, {"error": "limit"})
    out = AgentSearchToolSpec(mode="free").search("hi")
    assert out.startswith("Error:") and "per IP" in out


def test_auto_with_key_stays_free(monkeypatch):
    seen = mock(monkeypatch, _client, 200, {"results": []})
    monkeypatch.setenv("AGENTSEARCH_WALLET_PRIVATE_KEY", FAKE_KEY)
    monkeypatch.delenv("AGENTSEARCH_MODE", raising=False)
    monkeypatch.setattr(_client, "call_portal", lambda *a, **k: pytest.fail("paid path used"))
    out = AgentSearchToolSpec().search("hi")
    assert not out.startswith("Error:") and len(seen) == 1
    assert seen[0].url.host == "relay.agentsearchhq.com"


def test_auto_env_paid_uses_paid(monkeypatch):
    mock(monkeypatch, _client, 200, {})
    monkeypatch.setenv("AGENTSEARCH_MODE", "paid")
    monkeypatch.setattr(_client, "paid_extra_installed", lambda: True)
    monkeypatch.setattr(_client, "call_portal", lambda op, body, client=None: {"paid": op, "body": body})
    out = json.loads(AgentSearchToolSpec().search("hi", max_results=2))
    assert out == {"paid": "search", "body": {"query": "hi", "max_results": 2}}


def test_auto_env_paid_without_extra_falls_back(monkeypatch, caplog):
    seen = mock(monkeypatch, _client, 200, {"results": []})
    monkeypatch.setenv("AGENTSEARCH_MODE", "paid")
    monkeypatch.setattr(_client, "paid_extra_installed", lambda: False)
    monkeypatch.setattr(_client, "call_portal", lambda *a, **k: pytest.fail("paid path used"))
    with caplog.at_level("WARNING"):
        out = AgentSearchToolSpec().search("hi")
    assert not out.startswith("Error:") and len(seen) == 1
    assert "[paid] extra is not installed" in caplog.text


def test_explicit_paid_mode(monkeypatch):
    mock(monkeypatch, _client, 200, {})
    monkeypatch.setattr(_client, "call_portal", lambda op, body, client=None: {"paid": op})
    assert json.loads(AgentSearchToolSpec(mode="paid").search("hi")) == {"paid": "search"}


def test_explicit_free_ignores_env(monkeypatch):
    monkeypatch.setenv("AGENTSEARCH_MODE", "paid")
    assert _ops.resolve_search_mode("free") == "free"


@pytest.mark.parametrize("bad", [0, 6, -1, 2.5, "abc", True, [3]])
def test_max_results_validation(monkeypatch, bad):
    seen = mock(monkeypatch, _client, 200, {"results": []})
    out = AgentSearchToolSpec(mode="free").search("hi", max_results=bad)
    assert out.startswith("Error: max_results must be an integer from 1 to 5") and not seen


@pytest.mark.parametrize("ok,expected", [(1, 1), (5, 5), ("3", 3), (4.0, 4), (None, None)])
def test_max_results_valid(ok, expected):
    assert _client.validate_max_results(ok) == expected


def test_tool_names_unchanged():
    assert [t.metadata.name for t in AgentSearchToolSpec().to_tool_list()] == ["search", "extract", "render"]


def test_render_price_text_is_direct():
    # 0.3.0: direct x402 is the default paid route, render is $0.010
    assert "$0.010" in AgentSearchToolSpec.render.__doc__
