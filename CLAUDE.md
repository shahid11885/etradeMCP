# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

E*TRADE MCP Server that connects LLM clients (Claude, Gemini) to the E*TRADE brokerage API for real-time portfolio analysis, quotes, and option chain data.

## Development Commands

```bash
# One-time setup (creates venv and installs deps)
./setup_env.sh

# Activate virtual environment
source venv/bin/activate

# Install dependencies manually
pip install -r requirements.txt

# Authenticate with E*TRADE (run daily before using MCP server)
./etrade-auth.sh
# Or interactively:
python src/cli/main.py

# Generate tokens only (non-interactive after browser auth)
python src/cli/main.py generate-tokens

# Run the MCP server (used by Claude/Gemini clients)
python src/mcp/server.py

# Test all MCP tools against live API
python src/mcp/test_tools.py
```

## Architecture

```
src/
├── etrade_core/     # Core library for E*TRADE API
│   ├── auth.py      # OAuth 1.0 authentication, token management
│   ├── accounts/    # Account list, portfolio, balance
│   └── market/      # Quotes, option chains, expiry dates
├── cli/             # Interactive CLI application
│   └── main.py      # Menu-driven interface using etrade_core
└── mcp/             # MCP server for LLM clients
    └── server.py    # FastMCP server exposing etrade_core as tools
```

### Data Flow

1. **Authentication**: `auth.py` handles OAuth 1.0 flow with E*TRADE, stores tokens in `config/tokens.json`
2. **Token Expiry**: Tokens expire daily; `load_tokens()` checks file mtime and forces re-auth if stale
3. **MCP Server**: Uses `get_session(headless=True)` - fails if no valid tokens exist (must authenticate via CLI first)
4. **API Pattern**: All `etrade_core` modules follow: construct URL → `session.get/post(url, header_auth=True)` → parse JSON

### Key Files

- `config/config.ini` - API credentials (copy from `config.ini.example`)
- `config/tokens.json` - OAuth tokens (auto-generated, expires daily)
- `logs/python_client.log` - Rotating debug log (5MB, 3 backups)

### MCP Tools Exposed

The server exposes these tools to LLM clients:
- `list_accounts` - Get all brokerage accounts
- `get_portfolio(account_id_key)` - Portfolio positions
- `get_balance(account_id_key)` - Account balance
- `get_quote(symbols)` - Real-time stock quotes
- `get_option_expire_dates(symbol)` - Option expiration dates
- `get_option_chains(symbol, ...)` - Full option chain data with Greeks

### Environment Modes

- **PROD**: Production E*TRADE API (real money)
- **SANDBOX**: E*TRADE sandbox for testing (configured in `config.ini`)
