# Project Overview

This project provides both an interactive Command Line Interface (CLI) application and a Model Context Protocol (MCP) server for the E*TRADE API. It allows users to authenticate via OAuth 1.0, view account balances, manage portfolios, get market quotes, and handle orders.

## Architecture

The project is structured into three main components, all located under the `src/` directory:

- **`etrade_core/`**: A library containing all the core logic for interacting with the E*TRADE API.
    - `auth.py`: Handles OAuth 1.0 authentication and session management.
    - `accounts/`: Manages account listing, portfolio, and balance.
    - `market/`: Handles market data, quotes, and option chains.
    - `order/`: Manages order creation and tracking.
    - `client_logger.py`: Provides a shared logger.

- **`config/`**: Contains configuration files.
    - `config.ini.example`: The template for API credentials.
    - `config.ini`: Your actual API credentials (ignored by git).
    - `tokens.json`: Stores authentication tokens (ignored by git).

- **`cli/`**: The interactive command-line application.
    - `main.py`: The entry point for the CLI, which imports from `etrade_core`.

- **`mcp/`**: The Model Context Protocol (MCP) server.
    - `server.py`: The entry point for the MCP server, exposing tools from `etrade_core`.
    - `test_tools.py`: A script to test the MCP tools.

## MCP Tools

The `src/mcp/server.py` exposes the following tools to LLM clients:

- `list_accounts()`: List all available brokerage accounts.
- `get_portfolio(account_id_key)`: Get portfolio positions for a specific account.
- `get_balance(account_id_key)`: Get balance details for a specific account.
- `get_quote(symbols)`: Get real-time quotes for one or more stock symbols.
- `get_option_expire_dates(symbol, expiry_type)`: Get option expiration dates for a symbol.
- `get_option_chains(symbol, ...)`: Get detailed option chain data with various filters (expiry, strike, chain type).

## Building and Running

### Prerequisites

- Python 3.x
- E*TRADE API Credentials (Consumer Key and Secret)

### Setup

1.  **Configuration:**
    Copy the example configuration file and update it with your credentials:
    ```bash
    cp config/config.ini.example config/config.ini
    ```
    Edit `config/config.ini` and set your `CONSUMER_KEY` and `CONSUMER_SECRET`.

    **Note:** The application is designed to be flexible. If you only plan to use the production environment, you only need to provide the production keys (`PROD_CONSUMER_KEY`, `PROD_CONSUMER_SECRET`, `PROD_BASE_URL`). Similarly, if you only use the sandbox, you only need the sandbox keys. The application will intelligently use the keys provided and will not raise an error if one set of keys is missing.

2.  **Dependencies:**
    Install the required Python packages:
    ```bash
    pip install -r requirements.txt
    pip install fastmcp
    ```
    *Dependencies include: `requests`, `rauth`, `fastmcp`*

### Execution

First, authenticate by running the CLI application. This will create a `config/tokens.json` file, which is needed by the MCP server.

#### CLI Application
Run the application from the project's root directory:
```bash
python src/cli/main.py
```

#### Generating Tokens
If you only need to generate and save the authentication tokens without running the interactive menu, you can use the `generate-tokens` command:
```bash
python src/cli/main.py generate-tokens
```
This is useful for setting up the `tokens.json` file for other applications, like the MCP server.

#### MCP Server
Once `config/tokens.json` is generated, you can run the MCP server:
```bash
python src/mcp/server.py
```
To run the server over HTTP (SSE), use:
```bash
fastmcp run src/mcp/server.py --transport sse
```
You can also specify a port with `--port <port_number>`.

## Development Conventions

- **API Interaction:**
    - All API calls are authenticated using `rauth` sessions managed by `src/etrade_core/auth.py`.
    - Endpoints are constructed using the base URL (Sandbox or Prod) defined in `config/config.ini`.
- **Project Structure:**
    - The project is separated into a core library (`etrade_core`) and two entry-point applications (`cli` and `mcp`), all within the `src` directory. Configuration files are in the top-level `config` directory. This promotes separation of concerns.
- **Authentication:**
    - The `get_session` function in `src/etrade_core/auth.py` handles token persistence.
    - It first tries to load tokens from `config/tokens.json`. If missing or expired, it initiates the interactive OAuth web flow (when run from the CLI).
- **Logging:**
    - The application uses a shared logger defined in `src/etrade_core/client_logger.py`.
    - Logs are written to `logs/python_client.log`.
