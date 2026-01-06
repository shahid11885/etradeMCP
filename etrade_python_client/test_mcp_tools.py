import sys
import json
from etrade_python_client import get_session
from accounts.accounts import Accounts
from market.market import Market

def main():
    print("--- E*TRADE Tool Test Script ---")

    # 1. Authenticate
    try:
        print("1. Loading Session...")
        session, base_url = get_session(headless=True)
        print("   Success! Base URL:", base_url)
    except Exception as e:
        print(f"   Failed: {e}")
        print("   Please run 'python etrade_python_client.py' to authenticate first.")
        sys.exit(1)

    # Initialize Clients
    accounts_client = Accounts(session, base_url)
    market_client = Market(session, base_url)

    # 2. List Accounts
    print("\n2. Testing 'list_accounts'...")
    try:
        accounts = accounts_client.fetch_account_list()
        print(f"   Found {len(accounts)} accounts.")
        if accounts:
            first_acct = accounts[0]
            print(f"   First Account ID: {first_acct.get('accountId')}")
            account_id_key = first_acct.get('accountIdKey')
    except Exception as e:
        print(f"   Failed: {e}")
        sys.exit(1)

    if not accounts:
        print("   No accounts found. Skipping portfolio/balance tests.")
        return

    # 3. Get Balance
    print(f"\n3. Testing 'get_balance' for account {account_id_key}...")
    try:
        balance = accounts_client.fetch_balance(account_id_key)
        val = balance.get('BalanceResponse', {}).get('Computed', {}).get('RealTimeValues', {}).get('totalAccountValue')
        print(f"   Total Account Value: ${val}")
    except Exception as e:
        print(f"   Failed: {e}")

    # 4. Get Portfolio
    print(f"\n4. Testing 'get_portfolio' for account {account_id_key}...")
    try:
        portfolio = accounts_client.fetch_portfolio(account_id_key)
        if portfolio:
            positions = portfolio.get('PortfolioResponse', {}).get('AccountPortfolio', [])
            print(f"   Retrieved portfolio data with {len(positions)} position groups.")
        else:
            print("   Portfolio is empty or unavailable.")
    except Exception as e:
        print(f"   Failed: {e}")

    # 5. Get Quote
    print("\n5. Testing 'get_quote' for AAPL...")
    try:
        quotes = market_client.fetch_quote(["AAPL"])
        if quotes:
            q = quotes[0]
            price = q.get('All', {}).get('lastTrade')
            print(f"   AAPL Last Price: ${price}")
        else:
            print("   No quote data returned.")
    except Exception as e:
        print(f"   Failed: {e}")

    # 6. Get Option Expiry Dates
    print("\n6. Testing 'get_option_expire_dates' for AAPL...")
    try:
        dates = market_client.fetch_option_expire_dates("AAPL")
        if dates:
            print(f"   Found {len(dates)} expiry dates.")
            first_date = dates[0]
            print(f"   First date: {first_date.get('month')}/{first_date.get('day')}/{first_date.get('year')} ({first_date.get('expiryType')})")
        else:
            print("   No expiry dates returned.")
    except Exception as e:
        print(f"   Failed: {e}")

    print("\n--- Test Complete ---")

if __name__ == "__main__":
    main()
