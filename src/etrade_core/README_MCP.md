# E*TRADE MCP Server Guide

This guide explains how to set up, connect to, and test the E*TRADE MCP server.

## 1. Prerequisites

Ensure you have installed the dependencies and configured your credentials.

1.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    pip install fastmcp
    ```

2.  **Configure Credentials:**
    Copy `config/config.ini.example` to `config/config.ini` and edit it with your E*TRADE Consumer Key and Secret.
    ```bash
    cp config/config.ini.example config/config.ini
    nano config/config.ini
    ```
    **Note:** The application is designed to be flexible. If you only plan to use the production environment, you only need to provide the production keys. If you only use the sandbox, you only need the sandbox keys.

## 2. Authentication (One-Time Setup)

The MCP server uses saved tokens to authenticate. You must run the CLI application once to log in via the browser.

```bash
python src/cli/main.py
```
*   Follow the prompts to log in to E*TRADE.
*   Copy the verification code from the browser.
*   Once the menu appears, you can exit.
*   Verify that a `tokens.json` file has been created in the `config` directory.

## 3. Connecting with Claude Desktop

To use this server with Claude Desktop, add the following configuration to your `claude_desktop_config.json`:

**MacOS Location:** `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "etrade": {
      "command": "python",
      "args": [
        "/absolute/path/to/your/project/src/mcp/server.py"
      ]
    }
  }
}
```
*Replace `/absolute/path/to/your/project` with the actual full path to this project's root directory.*

## 4. Testing with the MCP Inspector

You can inspect and test the server tools using the generic MCP inspector.

1.  **Install the Inspector:**
    ```bash
    npx @modelcontextprotocol/inspector python src/mcp/server.py
    ```
    *(Requires Node.js and npm installed)*

2.  **Usage:**
    The inspector will open a web interface where you can see the available tools (`list_accounts`, `get_portfolio`, etc.) and execute them.

## 5. Testing with a Python Script

You can also verify the server functionality using the provided test script.

```bash
python src/mcp/test_tools.py
```

This script will:
1.  Load your saved session.
2.  Fetch your account list.
3.  Fetch the balance for the first account found.
4.  Fetch a quote for "AAPL".

## 6. Running over HTTP (SSE)

By default, the server runs using standard I/O (STDIN/STDOUT). You can also run it as an HTTP server using Server-Sent Events (SSE) transport:

```bash
# From the project root
fastmcp run src/mcp/server.py --transport sse
```

This will start the server on `http://127.0.0.1:8000`.

### Customizing Host and Port
You can specify a different host or port using the `--host` and `--port` flags:

```bash
fastmcp run src/mcp/server.py --transport sse --host 0.0.0.0 --port 8080
```

This is useful if you want to access the MCP server from remote clients or other applications that support SSE transport.

## Troubleshooting

*   **"Authentication failed":** Delete `src/etrade_core/tokens.json` and run `python src/cli/main.py` again.
*   **"No module named 'fastmcp'":** Ensure you are in the correct virtual environment.
