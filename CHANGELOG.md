# Changelog

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
