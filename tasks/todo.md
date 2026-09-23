# Add `list_transactions` MCP Tool

## Problem
The MCP server exposes positions (`get_portfolio`) and cash (`get_balance`), but
there is no way to see account *history* — what was bought/sold, dividends,
fees, transfers. Any question like "what did I trade last month" or "how much
did I pay in fees this year" is unanswerable today.

E*TRADE provides this via:
- `GET /v1/accounts/{accountIdKey}/transactions.json`
  params: `startDate` (MMDDYYYY), `endDate` (MMDDYYYY), `sortOrder` (ASC|DESC),
  `marker` (pagination cursor), `count`
- response: `TransactionListResponse` → `Transaction[]`, `marker`,
  `moreTransactions`, `transactionCount`, `totalCount`

## Todo
- [x] 1. Add `fetch_transactions()` to `src/etrade_core/accounts/accounts.py`,
      following the existing `fetch_portfolio` / `fetch_balance` pattern
      (construct URL → `session.get(..., header_auth=True, params=...)` → parse,
      204 → None, error → raise with E*TRADE's message).
- [x] 2. Add `transactions()` display method + a "Transactions" entry in the
      BROKERAGE branch of `account_menu()`, matching the existing
      `balance()` / `portfolio()` style.
- [x] 3. Expose `list_transactions()` in `src/mcp/server.py` as a thin
      pass-through, same shape as the other tools.
- [x] 4. Add a test step to `src/mcp/test_tools.py` exercising the new method
      against the live API.
- [x] 5. Update the "MCP Tools Exposed" list in `CLAUDE.md`.

## Design Decisions

**Date arguments** — accept `start_date` / `end_date` as `MMDDYYYY` strings and
pass them straight through (that is E*TRADE's format). Both optional; when
omitted E*TRADE returns its own default window.

**Pagination** — expose `count` and `marker` as arguments; the raw response
already carries `marker` / `moreTransactions` back to the caller, so an LLM can
page through a long history. No auto-pagination loop — that risks a huge
unbounded response.

**Return shape** — raw `TransactionListResponse` passthrough (decided with
Shahid), consistent with `get_portfolio` and `get_balance`. No flattening layer
to keep in sync with E*TRADE's schema.

**Out of scope**: the per-transaction details endpoint
(`/transactions/{transactionId}`) — a possible follow-up.

## Review

### Changes made
- **`src/etrade_core/accounts/accounts.py`**
  - `fetch_transactions()` — the API call. Optional `start_date` / `end_date`
    (MMDDYYYY), `sort_order`, `marker`, `count`. Returns the raw
    `TransactionListResponse`; `None` on 204 (empty window); raises with
    E*TRADE's own message on error.
  - `transactions()` — CLI display, one line per transaction, and a note when
    more pages are available.
  - `_format_transaction_date()` — renders E*TRADE's epoch-millisecond dates as
    MM/DD/YYYY.
  - `account_menu()` — "Transactions" added to the BROKERAGE branch (now 4,
    "Go Back" moved to 5).
- **`src/mcp/server.py`** — `list_transactions` tool, thin pass-through.
- **`src/mcp/test_tools.py`** — new step 5; later steps renumbered 6-9.
- **`CLAUDE.md`** — tool added to the "MCP Tools Exposed" list.

### Verified against the live PROD API
Full `test_tools.py` run passes all 9 steps with no regressions, with step 5
returning real data (a 200 with an "Online Transfer" row). The 204 path (empty
window) and the error path were both exercised during development too.

Caveat: because of finding 2 below, step 5 does not pass on *every* run — an
identical call sometimes times out. It is given one retry.

### Two findings worth recording
1. **Response casing differs from E*TRADE's docs.** The nested objects come
   back as lowercase `brokerage` / `product`, not `Brokerage` / `Product` as
   documented. The CLI display reads both spellings so it will not silently
   break if E*TRADE changes this.

2. **This endpoint is genuinely unreliable, in two distinct ways.** Costly to
   rediscover, so: against a **CLOSED** account it either stalls indefinitely or
   returns a misleading `oauth_problem=nonce_used` — the OAuth nonce is fine
   (rauth generates a fresh one per request and nothing seeds `random`); E*TRADE
   just reports the wrong error. Separately, even on an **active** account with a
   valid date range, the identical call sometimes returns instantly and
   sometimes hangs for minutes.

   Mitigations: `fetch_transactions` takes `timeout=30` (rauth's default is
   300s, far too long to leave an MCP client hanging), `test_tools.py` retries
   once, and it now picks the first non-CLOSED account rather than
   `accounts[0]` — which happened to be a closed account and was the source of
   the early failures.

### Follow-up not done
The per-transaction details endpoint (`/transactions/{transactionId}`) is still
unexposed; the list response carries a `detailsURI` per row. Worth adding if
multi-leg option trades need their individual legs broken out.
