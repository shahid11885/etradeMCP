# E*TRADE MCP Server Guide

This guide explains how to set up, connect to, and test the E*TRADE MCP server.

## 1. Prerequisites

Ensure you have installed the dependencies and configured your credentials.

1.  **Install Dependencies:**
    ```bash
    pip install -r ../requirements.txt
    pip install fastmcp
    ```

2.  **Configure Credentials:**
    Copy `config.ini.example` to `config.ini` and edit it with your E*TRADE Consumer Key and Secret.
    ```bash
    cp config.ini.example config.ini
    nano config.ini
    ```

## 2. Authentication (One-Time Setup)

The MCP server uses saved tokens to authenticate. You must run the CLI application once to log in via the browser.

```bash
python etrade_python_client.py
```
*   Follow the prompts to log in to E*TRADE.
*   Copy the verification code from the browser.
*   Once the menu appears, you can exit (Select option `3` or `5` depending on the menu).
*   Verify that a `tokens.json` file has been created in the directory.

## 3. Connecting with Claude Desktop

To use this server with Claude Desktop, add the following configuration to your `claude_desktop_config.json`:

**MacOS Location:** `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "etrade": {
      "command": "python",
      "args": [
        "/absolute/path/to/etrade_python_client/etrade_mcp_server.py"
      ]
    }
  }
}
```
*Replace `/absolute/path/to/...` with the actual full path to the `etrade_mcp_server.py` file.*

## 4. Testing with the MCP Inspector

You can inspect and test the server tools using the generic MCP inspector.

1.  **Install the Inspector:**
    ```bash
    npx @modelcontextprotocol/inspector python etrade_mcp_server.py
    ```
    *(Requires Node.js and npm installed)*

2.  **Usage:**
    The inspector will open a web interface where you can see the available tools (`list_accounts`, `get_portfolio`, etc.) and execute them.

## 5. Testing with a Python Script

You can also verify the server functionality using the provided test script `test_mcp_tools.py`.

```bash
python test_mcp_tools.py
```

This script will:
1.  Load your saved session.
2.  Fetch your account list.
3.  Fetch the balance for the first account found.
4.  Fetch a quote for "AAPL".

## Troubleshooting

*   **"Authentication failed":** Delete `tokens.json` and run `python etrade_python_client.py` again.
*   **"No module named 'fastmcp'":** Ensure you are in the correct virtual environment.
