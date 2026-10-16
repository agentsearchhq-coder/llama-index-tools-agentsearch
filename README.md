# AgentSearch Tool Spec (llama-index-tools-agentsearch)

A LlamaIndex `ToolSpec` for [AgentSearch](https://agentsearchhq.com/?utm_source=llama-index-tools-agentsearch&utm_medium=package): live web search for agents. Free search needs no API key.

| Function | Cost |
|---|---|
| `search(query, max_results=None)` | **Free** (25 searches/day per user, up to 5 results, no key). Paid and unlimited if a wallet is set. |
| `extract(url, formats=None, max_chars=None)` | $0.005/call (USDC on Base via x402) |
| `render(url, formats=None, max_chars=None, wait_until=None, wait_for_selector=None)` | $0.005/call (headless browser for JS pages) |

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

Free-only tool list: `[t for t in spec.to_tool_list() if t.metadata.name == "search"]`. Force free search even with a wallet set: `AgentSearchToolSpec(mode="free")`.

## Paid mode

Install the `paid` extra (`pip install "llama-index-tools-agentsearch[paid]"`) and set `AGENTSEARCH_WALLET_PRIVATE_KEY` to the private key of a **new wallet made only for this**, funded with a little USDC on Base (e.g. $1; no ETH needed). Each call costs $0.005 and is paid over x402 through the Pocket Network Agentic Portal using the official x402 Python SDK. With a key set, search also goes paid and unlimited.

| Env var | Default |
|---|---|
| `AGENTSEARCH_MAX_TOTAL_ATOMIC` | `1000000` ($1.00 per process) |
| `AGENTSEARCH_MAX_PER_CALL_ATOMIC` | `5000` ($0.005; can only be lowered) |
| `AGENTSEARCH_TIMEOUT_MS` | `30000` |

Limits are checked before anything is signed. The key is never logged or returned. Paid results include a `payment` object.

## Errors

Tools return `"Error: ..."` strings instead of raising. A 429 from the free relay means the daily limit (25 searches/day per user) was hit, and the message explains how to upgrade.

## Development

```bash
pip install -e ".[test]" && pytest     # unit tests (mocked)
AGENTSEARCH_LIVE=1 pytest -k live       # one real free search
```

Docs: https://agentsearchhq.com/agents.md?utm_source=llama-index-tools-agentsearch&utm_medium=package

MIT
