# Project Overview

This project provides both an interactive Command Line Interface (CLI) application and a Model Context Protocol (MCP) server for the E*TRADE API. It allows users to authenticate via OAuth 1.0, view account balances, manage portfolios, get market quotes, and handle orders.

## Architecture

- **Entry Points:**
    - `etrade_python_client.py`: Handles the main CLI execution flow, including the OAuth 1.0 authentication process and the top-level main menu.
    - `etrade_mcp_server.py`: Implements an MCP server using `fastmcp` to expose E*TRADE functionality to LLM clients like Claude Desktop.
- **Modules:**
    - `accounts/`: Contains the `Accounts` class for listing accounts, viewing portfolios, and checking balances.
    - `market/`: Contains the `Market` class for retrieving stock quotes and option chains.
    - `order/`: Contains the `Order` class for previewing, viewing, and canceling orders.
- **Configuration:**
    - `config.ini`: Stores API credentials and base URLs.
    - `tokens.json`: Stores authenticated session tokens for reuse (generated after first CLI login).
- **Logging:** Logs debug information and API interactions to `python_client.log` via `client_logger.py`.

## Building and Running

### Prerequisites

- Python 3.x
- E*TRADE API Credentials (Consumer Key and Secret)

### Setup

1.  **Configuration:**
    Copy the example configuration file and update it with your credentials:
    ```bash
    cp config.ini.example config.ini
    ```
    Edit `config.ini` and set your `CONSUMER_KEY` and `CONSUMER_SECRET`.

2.  **Dependencies:**
    Install the required Python packages:
    ```bash
    pip install -r ../requirements.txt
    pip install fastmcp
    ```
    *Dependencies include: `requests`, `rauth`, `fastmcp`*

### Execution

#### CLI Application
Run the application from the `etrade_python_client/` directory:
```bash
python etrade_python_client.py
```
Follow the on-screen prompts to authenticate via the browser. This will generate `tokens.json`.

#### MCP Server
Once `tokens.json` is generated, you can run the MCP server:
```bash
python etrade_mcp_server.py
```
Refer to `README_MCP.md` for details on connecting with Claude Desktop or using the MCP Inspector.

## Development Conventions

- **API Interaction:**
    - All API calls are authenticated using `rauth` sessions.
    - Endpoints are constructed using the base URL (Sandbox or Prod) defined in `config.ini`.
    - Responses are typically JSON, parsed and displayed to the user via the CLI or returned as tool outputs in the MCP server.
- **Project Structure:**
    - Each major feature set (Accounts, Market, Order) is encapsulated in its own directory and class.
    - Modules are shared between the CLI and the MCP server.
- **Authentication:**
    - The `get_session` function in `etrade_python_client.py` handles token persistence.
    - It first tries to load tokens from `tokens.json`. If missing or expired, it initiates the OAuth web flow.
- **Logging:**
    - The application uses `logging.handlers.RotatingFileHandler`.
    - Logs are written to `python_client.log` (max 5MB, 3 backups).
- **Error Handling:**
    - API errors are caught, and the JSON error message is parsed and displayed to the console or raised as an exception.
