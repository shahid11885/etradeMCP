import sys
import os
import json
from datetime import datetime

# Add project root to sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)

from etrade_core import auth
from etrade_core.accounts.accounts import Accounts
from etrade_core.market.market import Market

def main():
    print("--- E*TRADE Tool Test Script ---")

    # 1. Authenticate
    try:
        print("1. Loading Session...")
        session, base_url = auth.get_session(headless=True)
        print("   Success! Base URL:", base_url)
    except Exception as e:
        print(f"   Failed: {e}")
        print("   Please run 'python cli/main.py' to authenticate first.")
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
            # Prefer an active account -- closed accounts make some endpoints
            # (notably transactions) stall instead of returning cleanly.
            active = [a for a in accounts if a.get('accountStatus') != 'CLOSED']
            first_acct = active[0] if active else accounts[0]
            print(f"   Using Account ID: {first_acct.get('accountId')} ({first_acct.get('accountStatus')})")
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

    # 5. List Transactions (trailing 12 months; the default window is often empty)
    today = datetime.now()
    end_date = today.strftime("%m%d%Y")
    start_date = today.replace(year=today.year - 1).strftime("%m%d%Y")
    print(f"\n5. Testing 'list_transactions' for account {account_id_key} "
          f"({start_date} - {end_date})...")
    # This endpoint stalls intermittently, so give it one retry before failing.
    for attempt in (1, 2):
        try:
            data = accounts_client.fetch_transactions(account_id_key, start_date=start_date,
                                                      end_date=end_date, sort_order="DESC", count=5)
            if data and "TransactionListResponse" in data:
                resp = data["TransactionListResponse"]
                txns = resp.get("Transaction", [])
                print(f"   Retrieved {len(txns)} transactions (more available: {resp.get('moreTransactions')}).")
                if txns:
                    t = txns[0]
                    print(f"   Most recent: {t.get('transactionType')} | "
                          f"amount={t.get('amount')} | date={t.get('transactionDate')}")
            else:
                print("   No transactions in this window (204).")
            break
        except Exception as e:
            print(f"   Attempt {attempt} failed: {e}")

    # 6. Get Quote
    print("\n6. Testing 'get_quote' for AAPL...")
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

    # 7. Get Option Expiry Dates
    print("\n7. Testing 'get_option_expire_dates' for AAPL...")
    try:
        dates = market_client.fetch_option_expire_dates("AAPL")
        if dates:
            print(f"   Found {len(dates)} expiry dates.")
            first_date = dates[0]
            print(f"   First date: {first_date.get('month')}/{first_date.get('day')}/{first_date.get('year')} ({first_date.get('expiryType')})")
            
            # Use this date for the next test
            exp_year = first_date.get('year')
            exp_month = first_date.get('month')
            exp_day = first_date.get('day')
        else:
            print("   No expiry dates returned.")
            exp_year, exp_month, exp_day = None, None, None
    except Exception as e:
        print(f"   Failed: {e}")
        exp_year, exp_month, exp_day = None, None, None

    # 8. Get Option Chains
    if exp_year:
        print(f"\n8. Testing 'get_option_chains' for AAPL expiring on {exp_month}/{exp_day}/{exp_year}...")
        try:
            chain = market_client.fetch_option_chains(
                "AAPL", 
                expiry_year=exp_year, 
                expiry_month=exp_month, 
                expiry_day=exp_day,
                chain_type="CALL",
                no_of_strikes=2
            )
            if chain:
                pairs = chain.get("OptionPair", [])
                print(f"   Retrieved {len(pairs)} option pairs.")
                if pairs:
                    first_call = pairs[0].get("Call")
                    if first_call:
                        print(f"   Sample Call: Strike=${first_call.get('strikePrice')} Last=${first_call.get('lastPrice')}")
            else:
                print("   No option chain data returned.")
        except Exception as e:
            print(f"   Failed: {e}")
    else:
        print("\n8. Skipping 'get_option_chains' (no expiry date available).")

    # 9. Get Option Greeks
    if exp_year:
        print(f"\n9. Testing 'get_option_greeks' for AAPL expiring on {exp_month}/{exp_day}/{exp_year}...")
        try:
            contracts = market_client.fetch_option_greeks(
                "AAPL",
                expiry_year=exp_year,
                expiry_month=exp_month,
                expiry_day=exp_day,
                chain_type="CALLPUT",
                no_of_strikes=2
            )
            print(f"   Retrieved {len(contracts)} contracts.")
            if contracts:
                c = contracts[0]
                print(f"   Sample: {c.get('optionType')} ${c.get('strikePrice')} exp {c.get('expiry')}")
                print(f"   Greeks: iv={c.get('iv')} delta={c.get('delta')} gamma={c.get('gamma')} "
                      f"theta={c.get('theta')} vega={c.get('vega')} rho={c.get('rho')}")
                missing = [x for x in contracts if x.get("delta") is None]
                if missing:
                    print(f"   Note: {len(missing)} of {len(contracts)} contracts had no Greeks data.")
        except Exception as e:
            print(f"   Failed: {e}")
    else:
        print("\n9. Skipping 'get_option_greeks' (no expiry date available).")

    print("\n--- Test Complete ---")

if __name__ == "__main__":
    main()
