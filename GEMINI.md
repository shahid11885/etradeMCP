# Project Overview

This project provides both an interactive Command Line Interface (CLI) application and a Model Context Protocol (MCP) server for the E*TRADE API. It allows users to authenticate via OAuth 1.0, view account balances, manage portfolios, get market quotes, and handle orders.

## Architecture

- **Entry Points:**
    - `etrade_client/etrade_client.py`: Handles the main CLI execution flow, including the OAuth 1.0 authentication process and the top-level main menu.
    - `etrade_client/etrade_mcp_server.py`: Implements an MCP server using `fastmcp` to expose E*TRADE functionality to LLM clients like Claude Desktop.
- **Modules:**
    - `etrade_client/accounts/`: Contains the `Accounts` class for listing accounts, viewing portfolios, and checking balances.
    - `etrade_client/market/`: Contains the `Market` class for retrieving stock quotes, option chains, and expiration dates.
    - `etrade_client/order/`: Contains the `Order` class for previewing, viewing, and canceling orders.

## MCP Tools

The `etrade_mcp_server.py` exposes the following tools to LLM clients:

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
    cp etrade_client/config.ini.example etrade_client/config.ini
    ```
    Edit `etrade_client/config.ini` and set your `CONSUMER_KEY` and `CONSUMER_SECRET`.

2.  **Dependencies:**
    Install the required Python packages:
    ```bash
    pip install -r requirements.txt
    pip install fastmcp
    ```
    *Dependencies include: `requests`, `rauth`, `fastmcp`*

### Execution

#### CLI Application
Run the application from the project's root directory:
```bash
python etrade_client/etrade_client.py
```
Follow the on-screen prompts to authenticate via the browser. This will generate `etrade_client/tokens.json`.

#### MCP Server
Once `tokens.json` is generated, you can run the MCP server:
```bash
python etrade_client/etrade_mcp_server.py
```
To run the server over HTTP (SSE), use:
```bash
fastmcp run etrade_client/etrade_mcp_server.py --transport sse
```
You can also specify a port with `--port <port_number>`.
Refer to `etrade_client/README_MCP.md` for details on connecting with Claude Desktop or using the MCP Inspector.

## Development Conventions

- **API Interaction:**
    - All API calls are authenticated using `rauth` sessions.
    - Endpoints are constructed using the base URL (Sandbox or Prod) defined in `config.ini`.
    - Responses are typically JSON, parsed and displayed to the user via the CLI or returned as tool outputs in the MCP server.
- **Project Structure:**
    - Each major feature set (Accounts, Market, Order) is encapsulated in its own directory and class within `etrade_client`.
    - Modules are shared between the CLI and the MCP server.
- **Authentication:**
    - The `get_session` function in `etrade_client.py` handles token persistence.
    - It first tries to load tokens from `etrade_client/tokens.json`. If missing or expired, it initiates the OAuth web flow.
- **Logging:**
    - The application uses `logging.handlers.RotatingFileHandler`.
    - Logs are written to `python_client.log`.
- **Error Handling:**
    - API errors are caught, and the JSON error message is parsed and displayed to the console or raised as an exception.
