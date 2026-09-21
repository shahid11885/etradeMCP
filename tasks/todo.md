# Add `get_option_greeks` MCP Tool

## Problem
Greeks are only reachable today by calling `get_option_chains` and digging into
`OptionPair[].Call|Put.OptionGreeks`. The full chain response is also large, so an
LLM client pays a lot of context to read a few numbers.

## Todo
- [x] 1. Add `fetch_option_greeks()` to `src/etrade_core/market/market.py` — reuse
      `fetch_option_chains()`, flatten `OptionPair[]` into one row per contract
      containing only identity + pricing + Greeks.
- [x] 2. Expose `get_option_greeks()` in `src/mcp/server.py` as a thin pass-through
      (same pattern as the other five tools).
- [x] 3. Add step 8 to `src/mcp/test_tools.py` exercising the new method.
- [x] 4. Update the "MCP Tools Exposed" list in `CLAUDE.md`.

## Design Decisions

**Return shape** — flat list, one dict per contract:
```
[{"symbol": "AAPL", "optionType": "CALL", "strikePrice": 230.0,
  "expiry": "2026-09-25", "bid": 1.2, "ask": 1.25, "lastPrice": 1.22,
  "volume": 1234, "openInterest": 5678,
  "iv": 0.2841, "delta": 0.51, "gamma": 0.03, "theta": -0.12,
  "vega": 0.09, "rho": 0.02}, ...]
```
Rationale: an LLM can read/sort this directly; drops the ~20 fields per contract
(osiKey, netChange, adjustedFlag, timeStamp, quoteDetail, ...) that the Greeks
question never needs.

**Expiry** — pass-through. If the caller omits expiry, E*TRADE already defaults to
the nearest expiration; no extra API call added.

**Filtering** — same `strike_price_near` / `no_of_strikes` / `chain_type` args as
`get_option_chains`, so callers can keep the payload small.

**Missing Greeks** — if E*TRADE omits `OptionGreeks` for a contract, the Greek
fields come back as `None` rather than 0, so "no data" is distinguishable from a
genuine zero. (The CLI printer currently coerces to 0 — not changing that.)

## Scope Guard
- No change to `fetch_option_chains`, `get_option_chains`, or any existing tool.
- No change to auth, CLI, or the chain-printing code.
- New code is one method + one tool function.

## Review

### Summary of Changes

**`src/etrade_core/market/market.py`** — Added `fetch_option_greeks()` (appended as the
last method of `Market`, ~55 lines). It calls the existing `fetch_option_chains()`,
reads the expiry once from `SelectedED`, then walks `OptionPair[]` emitting one dict
per Call/Put with 15 fields. Greeks read from `option.get("OptionGreeks") or {}` so
both an absent block and an explicit `null` degrade to `None` values rather than
raising. Malformed/missing `SelectedED` yields `expiry: None` instead of an exception.

**`src/mcp/server.py`** — Added the `get_option_greeks` tool (`@mcp.tool()`), a thin
pass-through matching the pattern of the other five. Docstring tells the client to
prefer it over `get_option_chains` for Greeks-only questions and to use `no_of_strikes`
to bound the response.

**`src/mcp/test_tools.py`** — Added step 8, mirroring step 7: fetches 2 strikes for the
nearest AAPL expiry, prints a sample contract with all six Greeks, and reports how many
contracts came back without Greeks data.

**`CLAUDE.md`** — Added `get_option_greeks` to the "MCP Tools Exposed" list.

### Verification

- Offline test against stub chain data: 3 contracts flattened correctly; a pair with no
  `OptionGreeks` block and one with `OptionGreeks: null` both produced `None` Greeks; a
  pair with a Call but no Put did not raise; missing `SelectedED` produced `expiry: None`.
- FastMCP registration confirmed: 7 tools now register, and `get_option_greeks` exposes
  all 9 parameters with correct JSON schema types.
- **Verified against the live PROD API** (2026-09-21, tokens renewed):
  - `test_tools.py` step 8 passed — 4 contracts for the nearest AAPL expiry, sample
    `CALL $340.0 exp 2026-09-21` with `iv=0.20674 delta=0.1129 gamma=0.29858
    theta=-0.03511 vega=0.00616 rho=3e-05`.
  - Omitting the expiry args does default to the nearest expiration (2026-09-21),
    confirming no extra API call is needed.
  - Flat output is byte-identical to the raw chain when both read the *same* API
    response (compared type/strike/delta across all contracts). An initial mismatch
    was live quote drift between two separate requests, not a flattening defect.
  - 50-contract pull: zero missing values across all six Greeks.
  - Call deltas fall in 0.0..1.0, put deltas in -1.0..0.0; `chain_type="PUT"` returns
    puts only.
  - Payload: 2,165 bytes flat vs 5,304 bytes for the full chain on the same 8
    contracts (~59% smaller).

### What's Unchanged

- `fetch_option_chains()` and the `get_option_chains` tool — untouched.
- Auth, CLI, accounts, and the chain-printing helpers — zero changes.
- The CLI printer still coerces missing Greeks to `0`; only the new method uses `None`.
