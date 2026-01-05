# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

```bash
# Activate virtual environment (from etrade_python_client directory)
source venv/bin/activate

# Install dependencies
pip install -r ../requirements.txt

# Run the application
python etrade_python_client.py
```

Note: The application must be run from the `etrade_python_client/` directory since it reads `config.ini` using a relative path.

## Architecture

This is an interactive CLI application for the E*TRADE API with OAuth 1 authentication.

### Entry Point Flow
`etrade_python_client.py` → `oauth()` (browser-based auth) → `main_menu()` (interactive CLI)

### Module Structure

```
etrade_python_client/
├── etrade_python_client.py   # OAuth flow and main menu
├── accounts/accounts.py      # Accounts class - list accounts, portfolio, balance
├── market/market.py          # Market class - stock quotes
├── order/order.py            # Order class - preview, view, cancel orders
└── config.ini                # API credentials and base URLs
```

### Key Classes

- **Accounts**: Manages account listing, portfolio positions, and balance queries. Creates `Order` instances for trading operations.
- **Market**: Retrieves real-time stock quotes
- **Order**: Handles order preview, viewing by status, and cancellation

### API Pattern
All modules follow the same pattern:
1. Construct URL: `self.base_url + "/v1/{endpoint}.json"`
2. Make request: `self.session.get/post(url, header_auth=True, ...)`
3. Parse JSON response and display via CLI menus

### Configuration
`config.ini` contains:
- `CONSUMER_KEY` / `CONSUMER_SECRET`: E*TRADE API credentials
- `SANDBOX_BASE_URL`: `https://apisb.etrade.com` (testing)
- `PROD_BASE_URL`: `https://api.etrade.com` (live trading)

### Logging
All API calls logged to `python_client.log` (rotating, 5MB max, 3 backups) at DEBUG level.

### Dependencies
- `rauth==0.7.3`: OAuth 1.0 authentication library for E*TRADE API
