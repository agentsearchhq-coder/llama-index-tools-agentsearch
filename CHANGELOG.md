# Changelog

## 0.6.2 (2026-11-21)

- News, Search + Read and Screenshot use the free relay by default (10 free calls per IP in total each). Paid x402 only when a wallet is set and AGENTSEARCH_MODE=paid. Extract and render gain the no-wallet free trial (5 and 3 calls/day per IP).

## 0.6.1 (2026-11-20)
- Free search wording: the free relay now allows **25 free searches per IP in total** (a lifetime allowance since 2026-11-19, not per day), then pay per call via x402 on Base ($0.003 per search at https://api.agentsearchhq.com; wallet setup https://agentsearchhq.com/wallet-setup). The search tool docstring/description, the free-limit (HTTP 429) message, `search_mode_label()` and the README no longer say "25 searches/day per IP", "resets daily" or "daily limit". The extract/render free trial is unchanged (5 extract and 3 render calls per day per IP). No behavior change.

## 0.6.0 (2026-11-19)
- **With a wallet, search pays by default.** In the default mode, search now pays $0.003 per call over x402 to AgentSearch's own API ($0.005 with `AGENTSEARCH_PAYMENT_ROUTE=pocket`) when a wallet is configured and the `[paid]` extra is installed. With no wallet it uses the free relay exactly as before. `AGENTSEARCH_MODE=free` (or `mode="free"`) is the opt-out. Spend caps are unchanged (per call and `AGENTSEARCH_MAX_TOTAL_ATOMIC`, default $1.00). Previously a wallet key alone kept search free.
- **Reuse an existing wallet:** `AGENTSEARCH_WALLET_FILE` points at a file holding a 64-hex key or JSON with `privateKey` (`agentcash` = AgentCash's `~/.agentcash/wallet.json`). Read only when signing; never logged. Encrypted keystores and remote signers (CDP server wallets) are a follow-up.
- **Mode is visible:** every search result has an `agentsearch_mode` field (`"free: ..."` / `"paid: ..."`), and the first paid search in a process logs one `AgentSearch search mode: paid ...` warning line.

## 0.5.4 (2026-11-18)
- Fix HTTP 400s from the free relay. `free_search()` (also what you get when you pass it to a framework as a plain function) now unwraps a whole tool-input dict passed as `query`, ignores a non-count dict in the `max_results` slot (such as a framework config object passed as the 2nd argument), accepts a numeric string or `{"max_results": n}` for the count and clamps it to 1-5. An empty, missing or non-string query raises `AgentSearchError` before any request (nothing sent or charged). `check_query` unwraps tool-input dicts and no longer stringifies arbitrary objects. `validate_max_results` unwraps tool-input dicts too (a dict with no count key means the default).

## 0.5.3 (2026-11-16)
- Docs only: README tool table: news_search $0.003/call and screenshot $0.004/call (were still $0.005). Live direct prices: search and news $0.003, extract $0.002, render $0.005, screenshot $0.004, search_and_read $0.005; Pocket route unchanged at $0.005. No code or behavior change.

## 0.5.2 (2026-11-15)
- Direct x402 list prices now match the live API (approved 2026-11-15): search and news $0.003, extract $0.002, render $0.005, screenshot $0.004, search_and_read $0.005. Runtime price constants, tool text, docs and tests updated. Pocket route remains $0.005. The per-call ceiling stays $0.020.

## 0.5.1 (2026-11-14)
- **Short-query guard.** Search, news and search-and-read now reject queries shorter than 2 characters (after trimming) before any network request, returning an `Error: ... rewrite the query (at least 2 characters) ...` string; nothing is sent or charged. Queries are trimmed before sending.
- **Relay input errors are final.** A 4xx from the free relay (other than 408/429) now tells the agent to fix the query instead of retrying it unchanged (the relay marks these `retryable:false`). Matches `langchain-agentsearch` 0.7.1 and `@agentsearchhq/agentsearch-mcp` 1.8.1.

## 0.5.0 (2026-11-12)
- **News search.** New `news_search` ($0.008): recent articles with title, URL, snippet, source and publish date (1-10, default 5); calls with no results are not charged.
- **Screenshots.** New `screenshot` ($0.010): PNG or JPEG of the viewport or full page (up to 4000 px), optional `viewport_width`/`viewport_height`. The image is saved to a file (`AGENTSEARCH_SCREENSHOT_DIR`, default a temp folder) and the tool returns its path and metadata, not base64.
- **Search filters** on paid search, news and search-and-read: `freshness`, `date_from`/`date_to`, `country`, `language`, `include_domains`/`exclude_domains` (up to 5). Free search ignores them; the Pocket route drops them (listed in `payment.droppedFields`).
- **Extract options on direct:** `max_chars` (up to 50000) and new `include_links` are now forwarded (0.4.0 dropped them).
- **Lower prices:** extract $0.004 (was $0.007), search-and-read $0.009 (was $0.015). `to_tool_list()` now has search, news_search, extract, render, screenshot and search_and_read. Matches `@agentsearchhq/agentsearch-mcp` 1.8.0, `langchain-agentsearch` 0.7.0 and `crewai-agentsearch` 0.5.0.

## 0.4.0 (2026-11-10)
- **Search + Read in one paid call.** New ``AgentSearchToolSpec.search_and_read`` posts to `https://api.agentsearchhq.com/x402/v1/search_and_read` at **$0.015**, charged only when at least one page returns text. Default 3 results (max 5), default 8000 characters per page (max 20000); `render_fallback=true` renders at most one thin page in the same call. About 48% less than a $0.008 search plus three $0.007 extracts ($0.029), and one payment instead of four.
- Direct-only: not on the Pocket route, not on a self-hosted base URL. A Pocket or no-wallet call refuses with nothing signed. Search itself stays free by default.
- Direct per-call ceiling raised to **$0.020** (`DIRECT_MAX_PER_CALL_ATOMIC = 20000`) so a $0.015 search-and-read can settle. An old `10000` cap now refuses with a hint to raise it to `20000`. Matches `@agentsearchhq/agentsearch-mcp` 1.7.0.

## 0.3.0 (2026-11-09)

### Changed: paid calls go directly to AgentSearch's x402 API by default

- With a wallet key, paid calls now go to AgentSearch's own x402 API on Base (`https://api.agentsearchhq.com/x402/v1/...`, payee `0xC49B157887e51c21CB655f39CF65D6a4c2a4C337`) instead of the Pocket Network Agentic Portal.
- **Price change for wallet users:** search $0.008, extract $0.007, render $0.010 per call (was $0.005 on Pocket). Failed and empty calls are not charged on the direct API.
- To keep the Pocket route and its $0.005 price, set `AGENTSEARCH_PAYMENT_ROUTE=pocket` (`AGENTSEARCH_X402_DIRECT=0` also works). Any other value refuses paid calls with nothing signed.
- Per-call hard cap is now `10000` atomic units ($0.010) on the direct route; it stays `5000` on Pocket. If you set `AGENTSEARCH_MAX_PER_CALL_ATOMIC` below the direct price, the refusal tells you how to fix it.
- On the direct route, extract and render take only `url` (and search `query`, `max_results`); other options are dropped and listed in `payment.droppedFields`. Use the Pocket route for options like `formats`, `max_chars` or screenshots.
- Free search with no wallet is unchanged.

## 0.2.1 (2026-10-20)

### Changed: paid search is now explicit opt-in (safety)

- In the default `mode="auto"`, `AgentSearchToolSpec` **no longer switches search to paid just because a wallet key** (`AGENTSEARCH_WALLET_PRIVATE_KEY` or `POCKET_PRIVATE_KEY`) is set. It stays on free search.
- To use paid search, opt in explicitly: `AgentSearchToolSpec(mode="paid")`, or set `AGENTSEARCH_MODE=paid` for the default `mode="auto"`.
- Explicit `mode="paid"` behaves exactly as before.
- If you relied on 0.2.0 auto-switching to paid when a key was set, add `AGENTSEARCH_MODE=paid` (or `mode="paid"`) to keep paid search.
- Extract and render are unchanged: they are paid tools and still need the wallet key.
- `max_results` is now validated: it must be an integer from 1 to 5 (or omitted for the default of 5). Out-of-range or non-integer values return `Error: max_results must be an integer from 1 to 5 ...` and no call is made (0.2.0 silently clamped them).

### Added

- `session_spent_atomic` and `reset_session_budget` are exported from `llama_index.tools.agentsearch` (previously only reachable via the internal `_client` module, which still works).

### Fixed

- In `mode="auto"` with `AGENTSEARCH_MODE=paid` but without the `[paid]` extra installed, search now falls back to free search with a logged warning instead of returning an error. Explicit `mode="paid"` without the extra still returns a clear error with the install command (`pip install 'llama-index-tools-agentsearch[paid]'`).

### Docs

- The free tier is described as up to 25 searches/day per IP (README, docstrings, and the free-limit message the agent sees).
- Documented `AGENTSEARCH_MODE` and `AGENTSEARCH_EXTRACT_RENDER_FALLBACK=1`.
- Pricing is unchanged: $0.005 per paid call (search, extract, render).

### Not changed

- Tool names stay `search`, `extract` and `render` to avoid a breaking change. (They are generic; a future major/minor release may rename them, e.g. to `agentsearch_search`. Until then, wrap them with `FunctionTool.from_defaults(..., name=...)` if you need distinct names.)

## 0.2.0 (2026-10-16)

- Client tag header, render guidance for extract/render, repository metadata.

## 0.1.0

- First release.
