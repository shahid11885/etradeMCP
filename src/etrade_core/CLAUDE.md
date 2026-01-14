# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

```bash
# Activate virtual environment (from the project root)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the CLI application
python src/cli/main.py

# Run the MCP server
python src/mcp/server.py
```

## Architecture

The project is structured into three main components, all located inside the `src/` directory: `etrade_core`, `cli`, and `mcp`.

### Core Library: `src/etrade_core`

This directory contains all the core logic for interacting with the E*TRADE API.

- **`auth.py`**: Handles OAuth 1.0 authentication and session management.
- **`accounts/accounts.py`**: Manages account listing, portfolio, and balance.
- **`market/market.py`**: Handles market data and quotes.
- **`order/order.py`**: Manages order creation and tracking.
- **`config.ini`**: Stores API credentials and base URLs.

### CLI Application: `src/cli`

- **`main.py`**: The entry point for the interactive command-line application. It imports and uses the `etrade_core` library.

### MCP Server: `src/mcp`

- **`server.py`**: The entry point for the MCP server, which exposes tools from `etrade_core` to LLM clients.

### API Pattern
All modules in `etrade_core` follow a similar pattern:
1. Construct URL: `self.base_url + "/v1/{endpoint}.json"`
2. Make request: `self.session.get/post(url, header_auth=True, ...)`
3. Parse JSON response.

### Logging
All API calls logged to `python_client.log` (rotating, 5MB max, 3 backups) at DEBUG level.
