"""This Python script provides examples on using the E*TRADE API endpoints"""
from __future__ import print_function
import webbrowser
import json
import logging
import configparser
import sys
import os
import requests
from rauth import OAuth1Service
import datetime
from client_logger import logger
from accounts.accounts import Accounts
from market.market import Market

# loading configuration file
BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
config      = configparser.ConfigParser()  # noqa: E501
config.read(os.path.join(BASE_DIR, 'config.ini'))

# logger settings
# (Managed by client_logger, which is imported)

TOKEN_FILE = os.path.join(BASE_DIR, 'tokens.json')

def get_etrade_service(env="PROD"):
    """Initializes and returns the OAuth1Service"""
    if env == "PROD":
        consumer_key        = config["DEFAULT"]["PROD_CONSUMER_KEY"]
        consumer_secret     = config["DEFAULT"]["PROD_CONSUMER_SECRET"]
        base_url            = config["DEFAULT"]["PROD_BASE_URL"]
    else:  # SANDBOX
        consumer_key        = config["DEFAULT"]["SANDBOX_CONSUMER_KEY"]
        consumer_secret     = config["DEFAULT"]["SANDBOX_CONSUMER_SECRET"]
        base_url            = config["DEFAULT"]["SANDBOX_BASE_URL"]

    return OAuth1Service(
        name                = "etrade",  # noqa: E501
        consumer_key        = consumer_key,
        consumer_secret     = consumer_secret,
        request_token_url   = f"{base_url}/oauth/request_token",   # noqa: E501
        access_token_url    = f"{base_url}/oauth/access_token",    # noqa: E501
        authorize_url       = "https://us.etrade.com/e/t/etws/authorize?key={}&token={}",  # noqa: E501
        base_url=base_url)

def save_tokens(token, secret, base_url):
    """Saves the access token and secret to a file"""
    data = {
        "access_token": token,
        "access_token_secret": secret,
        "base_url": base_url
    }
    with open(TOKEN_FILE, 'w') as f:
        json.dump(data, f)
    logger.info("Tokens saved to %s", TOKEN_FILE)

def load_tokens():
    """Loads the access token and secret from a file"""
    if os.path.exists(TOKEN_FILE):
        # Get file modification time
        file_mtime = datetime.datetime.fromtimestamp(os.path.getmtime(TOKEN_FILE)).date()
        
        # Get current date
        current_date = datetime.date.today()
        
        # If token file is older than today, return None to force re-authentication
        if file_mtime < current_date:
            logger.info("Token file is older than today, forcing re-authentication.")
            return None

        try:
            with open(TOKEN_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error("Error loading tokens: %s", e)
    return None

def get_session(headless=False):
    """
    Returns an authenticated session.
    If headless is True, it will only try to load from file and raise error if not found.
    """
    tokens = load_tokens()

    if tokens:
        # Determine environment from saved base_url
        if tokens["base_url"] == config["DEFAULT"]["SANDBOX_BASE_URL"]:
            env = "SANDBOX"
        else:
            env = "PROD"
        etrade = get_etrade_service(env)
        session = etrade.get_session(
            (tokens["access_token"], tokens["access_token_secret"])
        )
        return session, tokens["base_url"]

    if headless:
        raise Exception("No saved tokens found. Please run the CLI application first to authenticate.")

    # Interactive Auth Flow
    menu_items = {"1": "Sandbox Consumer Key",
                  "2": "Prod Consumer Key",
                  "3": "Exit"}
    while True:
        print("")
        options         = list(menu_items.keys())  # noqa: E501
        for entry in options:
            print(entry + ")\t" + menu_items[entry])
        selection       = input("Please select Consumer Key Type: ")  # noqa: E501
        if selection == "1":
            env         = "SANDBOX"
            break
        elif selection == "2":
            env         = "PROD"  # noqa: E501
            break
        elif selection == "3":
            sys.exit(0)
        else:
            print("Unknown Option Selected!")
    print("")

    etrade = get_etrade_service(env)
    base_url = etrade.base_url

    # Step 1: Get OAuth 1 request token and secret
    request_token, request_token_secret = etrade.get_request_token(
        params={"oauth_callback": "oob", "format": "json"})

    # Step 2: Go through the authentication flow. Login to E*TRADE.
    authorize_url = etrade.authorize_url.format(etrade.consumer_key, request_token)
    webbrowser.open(authorize_url)
    print("Please accept agreement and enter verification code from browser.")
    text_code = input("Verification Code: ")

    # Step 3: Exchange the authorized request token for an authenticated OAuth 1 session
    session = etrade.get_auth_session(request_token,
                                  request_token_secret,
                                  params={"oauth_verifier": text_code})

    save_tokens(session.access_token, session.access_token_secret, base_url)
    return session, base_url

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
