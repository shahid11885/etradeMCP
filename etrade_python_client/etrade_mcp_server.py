from fastmcp import FastMCP
from etrade_python_client import get_session
from accounts.accounts import Accounts
from market.market import Market

# Initialize FastMCP server
mcp = FastMCP("E*TRADE")

# Global instances
accounts_client = None
market_client = None

def get_clients():
    """
    Lazy initialization of clients.
    This ensures that the server can start even if credentials aren't ready,
    but tools will fail gracefully if authentication is missing.
    """
    global accounts_client, market_client
    if accounts_client is None or market_client is None:
        try:
            session, base_url = get_session(headless=True)
            accounts_client = Accounts(session, base_url)
            market_client = Market(session, base_url)
        except Exception as e:
            raise RuntimeError(f"Authentication failed: {e}")
    return accounts_client, market_client

@mcp.tool()
def list_accounts() -> list:
    """
    List all available brokerage accounts.
    Returns a list of account dictionaries containing details like accountId, accountDesc, etc.
    """
    accts, _ = get_clients()
    return accts.fetch_account_list()

@mcp.tool()
def get_portfolio(account_id_key: str) -> dict:
    """
    Get the portfolio positions for a specific account.
    Args:
        account_id_key: The unique key for the account (available from list_accounts).
    Returns:
        A dictionary containing the portfolio data.
    """
    accts, _ = get_clients()
    return accts.fetch_portfolio(account_id_key)

@mcp.tool()
def get_balance(account_id_key: str) -> dict:
    """
    Get the balance details for a specific account.
    Args:
        account_id_key: The unique key for the account.
    Returns:
        A dictionary containing balance information.
    """
    accts, _ = get_clients()
    return accts.fetch_balance(account_id_key)

@mcp.tool()
def get_quote(symbols: list[str]) -> list:
    """
    Get real-time quotes for one or more stock symbols.
    Args:
        symbols: A list of stock symbols (e.g., ["AAPL", "GOOG"]).
    Returns:
        A list of quote dictionaries.
    """
    _, mkt = get_clients()
    return mkt.fetch_quote(symbols)

if __name__ == "__main__":
    mcp.run()
