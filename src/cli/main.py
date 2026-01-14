"""This Python script provides examples on using the E*TRADE API endpoints"""
from __future__ import print_function
import sys
import os

# Add project root to sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)

from etrade_core.auth import get_session
from etrade_core.accounts.accounts import Accounts
from etrade_core.market.market import Market


def oauth():
    """Allows user authorization for the sample application with OAuth 1"""
    try:
        session, base_url = get_session()
        main_menu(session, base_url)
    except Exception as e:
        print(f"An error occurred: {e}")

def main_menu(session, base_url):
    """
    Provides the different options for the sample application: Market Quotes, Option Expire Dates, Option Chains, Account List

    :param session: authenticated session
    """

    menu_items = {"1": "Market Quotes",
                  "2": "Option Expire Dates",
                  "3": "Option Chains",
                  "4": "Account List",
                  "5": "Exit"}

    while True:
        print("")
        options = menu_items.keys()
        for entry in options:
            print(entry + ")\t" + menu_items[entry])
        selection = input("Please select an option: ")
        if selection == "1":
            market = Market(session, base_url)
            market.quotes()
        elif selection == "2":
            market = Market(session, base_url)
            market.option_expire_dates()
        elif selection == "3":
            market = Market(session, base_url)
            market.option_chains()
        elif selection == "4":
            accounts = Accounts(session, base_url)
            accounts.account_list()
        elif selection == "5":
            break
        else:
            print("Unknown Option Selected!")


if __name__ == "__main__":
    oauth()
