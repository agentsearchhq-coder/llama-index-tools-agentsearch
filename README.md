# AgentSearch Tool Spec (llama-index-tools-agentsearch)

A LlamaIndex `ToolSpec` for [AgentSearch](https://agentsearchhq.com/?utm_source=llama-index-tools-agentsearch&utm_medium=package): live web search for agents. Free search needs no API key.

| Function | Cost |
|---|---|
| `search(query, max_results=None)` | **Free** with no wallet (25 free searches per IP in total, then pay per call, up to 5 results, no key). With a wallet and the `[paid]` extra, $0.003/call and unlimited (from 0.6.0; `mode="free"` or `AGENTSEARCH_MODE=free` keeps it free). |
| `news_search(query, max_results=None, freshness=None, ...)` | $0.003/call (recent news with publish dates; no results, no charge) |
| `extract(url, formats=None, max_chars=None, include_links=None)` | $0.002/call (USDC on Base via x402 to AgentSearch) |
| `render(url, formats=None, max_chars=None, wait_until=None, wait_for_selector=None)` | $0.005/call (headless browser for JS pages) |
| `screenshot(url, format=None, full_page=None, viewport_width=None, viewport_height=None)` | $0.004/call (PNG/JPEG saved to a local file; path returned) |
| `search_and_read(query, num_results=None, max_chars=None, ...)` | $0.005/call (search plus the top pages' text in one payment) |

Paid search, `news_search` and `search_and_read` accept filters: `freshness` (day/week/month/year), `date_from`/`date_to` (YYYY-MM-DD), `country`, `language`, and up to 5 `include_domains`/`exclude_domains` (free search ignores them). News, screenshot and search-and-read are direct-only (not on Pocket). Screenshots are saved in `AGENTSEARCH_SCREENSHOT_DIR` (default a temp folder) so base64 never floods the model's context.

## Install

```bash
pip install -U llama-index-tools-agentsearch
```

## Quickstart

```python
from llama_index.tools.agentsearch import AgentSearchToolSpec

spec = AgentSearchToolSpec()
print(spec.search("latest LlamaIndex release", max_results=3))  # JSON string

# With an agent
from llama_index.core.agent.workflow import FunctionAgent
from llama_index.llms.openai import OpenAI

agent = FunctionAgent(tools=spec.to_tool_list(), llm=OpenAI(model="gpt-4o-mini"))
# response = await agent.run("What changed in the latest LlamaIndex release? Cite URLs.")
```

Free-only tool list: `[t for t in spec.to_tool_list() if t.metadata.name == "search"]`. From 0.6.0, the default `mode="auto"` pays for search ($0.003) when a wallet is set; `AgentSearchToolSpec(mode="free")` pins it to free regardless of `AGENTSEARCH_MODE`, and `AGENTSEARCH_MODE=free` does the same from the environment. Every search result has an `agentsearch_mode` field (`free: ...` / `paid: ...`).

`max_results` must be an integer from 1 to 5 (default 5); other values return an `Error: max_results must be ...` string and no call is made.

## Paid mode

Install the `paid` extra (`pip install "llama-index-tools-agentsearch[paid]"`) and set `AGENTSEARCH_WALLET_PRIVATE_KEY` to the private key of a **new wallet made only for this**, funded with a little USDC on Base (e.g. $1; no ETH needed). Since 0.3.0 each call is paid over x402 **directly to AgentSearch's own API** (`https://api.agentsearchhq.com`, USDC on Base, settled only on success) using the official x402 Python SDK: search $0.003, news $0.003, extract $0.002, render $0.005, screenshot $0.004, search-and-read $0.005. $1 covers about 500 extracts or 200 search-and-read calls. Prefer the Pocket Network Agentic Portal ($0.005 per call)? Set `AGENTSEARCH_PAYMENT_ROUTE=pocket`. Extract and render use the key directly, and from 0.6.0 search pays too (unlimited, $0.003) unless you set `mode="free"` or `AGENTSEARCH_MODE=free`. In `mode="auto"`, if a wallet is set (or `AGENTSEARCH_MODE=paid`) but the `[paid]` extra is missing, search falls back to free with a logged warning.

**Reuse a wallet you already have (0.6.0+).** Instead of pasting a key, set `AGENTSEARCH_WALLET_FILE` to a file holding a 64-hex private key, or JSON with a `privateKey` field. `AGENTSEARCH_WALLET_FILE=agentcash` reuses AgentCash's `~/.agentcash/wallet.json`. The file is read only when signing and its contents are never logged. Encrypted keystores and remote signers (CDP server wallets) are not supported yet.

| Env var | Default |
|---|---|
| `AGENTSEARCH_MAX_TOTAL_ATOMIC` | `1000000` ($1.00 per process) |
| `AGENTSEARCH_PAYMENT_ROUTE` | `direct` (AgentSearch's x402 API); `pocket` = Pocket Network Agentic Portal at $0.005/call |
| `AGENTSEARCH_MAX_PER_CALL_ATOMIC` | `20000` on the direct route, `5000` on Pocket ($0.020 / $0.005; can only be lowered) |
| `AGENTSEARCH_SCREENSHOT_DIR` | a temp folder (`agentsearch-screenshots`) |
| `AGENTSEARCH_TIMEOUT_MS` | `30000` |
| `AGENTSEARCH_MODE` | unset = `auto` (paid search when a wallet is set); `free` keeps search free; `paid` forces paid (all apply when `mode="auto"`) |
| `AGENTSEARCH_WALLET_FILE` | unset (path to a wallet file instead of a pasted key; `agentcash` = `~/.agentcash/wallet.json`) |
| `AGENTSEARCH_EXTRACT_RENDER_FALLBACK` | unset (`1` = when extract returns thin content, render the URL once; a second paid call, $0.005) |

Limits are checked before anything is signed. The key is not included in tool output or error messages. Paid results include a `payment` object.

Budget helpers are exported at the top level:

```python
from llama_index.tools.agentsearch import reset_session_budget, session_spent_atomic

print(session_spent_atomic())  # USDC atomic units signed so far in this process (1_000_000 = $1)
reset_session_budget()
```

## Errors

Tools return `"Error: ..."` strings instead of raising. A 429 from the free relay means the free search allowance (25 free searches per IP in total, then pay per call) is used up or shared daily capacity is reached, and the message explains how to upgrade. Search, news and search-and-read reject queries shorter than 2 characters (after trimming) before any request, so nothing is sent or charged; other 4xx errors from the free relay say to fix the input instead of retrying it unchanged.

## Development

```bash
pip install -e ".[test]" && pytest     # unit tests (mocked)
AGENTSEARCH_LIVE=1 pytest -k live       # one real free search
```

Docs: https://agentsearchhq.com/agents.md?utm_source=llama-index-tools-agentsearch&utm_medium=package

MIT
