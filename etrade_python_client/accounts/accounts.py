import json
import logging
import configparser
from order.order import Order
from client_logger import logger

# loading configuration file
config = configparser.ConfigParser()
config.read('config.ini')


class Accounts:
    def __init__(self, session, base_url):
        """
        Initialize Accounts object with session and account information

        :param session: authenticated session
        """
        self.session = session
        self.account = {}
        self.base_url = base_url

    def fetch_account_list(self):
        """
        Fetches the list of accounts from the API.
        Returns the list of accounts or raises an exception on error.
        """
        url = self.base_url + "/v1/accounts/list.json"
        response = self.session.get(url, header_auth=True)
        logger.debug("Request Header: %s", response.request.headers)

        if response is not None and response.status_code == 200:
            parsed = json.loads(response.text)
            logger.debug("Response Body: %s", json.dumps(parsed, indent=4, sort_keys=True))
            data = response.json()
            if data is not None and "AccountListResponse" in data and "Accounts" in data["AccountListResponse"] \
                    and "Account" in data["AccountListResponse"]["Accounts"]:
                return data["AccountListResponse"]["Accounts"]["Account"]
            else:
                logger.debug("Response Body: %s", response.text)
                raise Exception("AccountList API service error")
        else:
            logger.debug("Response Body: %s", response.text)
            if response is not None and response.headers.get('Content-Type') == 'application/json':
                error_data = response.json()
                if "Error" in error_data and "message" in error_data["Error"]:
                    raise Exception(error_data["Error"]["message"])
            raise Exception("AccountList API service error")

    def account_list(self):
        """
        Calls account list API to retrieve a list of the user's E*TRADE accounts
        """
        try:
            accounts = self.fetch_account_list()
            while True:
                # Display account list
                count = 1
                print("\nBrokerage Account List:")
                # Filter closed accounts
                active_accounts = [d for d in accounts if d.get('accountStatus') != 'CLOSED']
                for account in active_accounts:
                    print_str = str(count) + ")\t"
                    if account is not None and "accountId" in account:
                        print_str = print_str + (account["accountId"])
                    if account is not None and "accountDesc" in account \
                            and account["accountDesc"].strip() is not None:
                        print_str = print_str + ", " + account["accountDesc"].strip()
                    if account is not None and "institutionType" in account:
                        print_str = print_str + ", " + account["institutionType"]
                    print(print_str)
                    count = count + 1
                print(str(count) + ")\t" "Go Back")

                # Select account option
                account_index = input("Please select an account: ")
                if account_index.isdigit() and 0 < int(account_index) < count:
                    self.account = active_accounts[int(account_index) - 1]
                    self.account_menu()
                elif account_index == str(count):
                    break
                else:
                    print("Unknown Account Selected!")
        except Exception as e:
            print(f"Error: {e}")

    def fetch_portfolio(self, account_id_key):
        """
        Fetches the portfolio for a specific account.
        """
        url = self.base_url + "/v1/accounts/" + account_id_key + "/portfolio.json"
        response = self.session.get(url, header_auth=True)
        logger.debug("Request Header: %s", response.request.headers)

        if response is not None and response.status_code == 200:
            parsed = json.loads(response.text)
            logger.debug("Response Body: %s", json.dumps(parsed, indent=4, sort_keys=True))
            data = response.json()
            return data
        elif response is not None and response.status_code == 204:
            return None
        else:
            logger.debug("Response Body: %s", response.text)
            if response is not None and response.headers.get('Content-Type') == 'application/json':
                error_data = response.json()
                if "Error" in error_data and "message" in error_data["Error"]:
                    raise Exception(error_data["Error"]["message"])
            raise Exception("Portfolio API service error")

    def portfolio(self):
        """
        Call portfolio API to retrieve a list of positions held in the specified account
        """
        try:
            data = self.fetch_portfolio(self.account["accountIdKey"])
            print("\nPortfolio:")
            
            if data is None:
                print("None")
                return

            if data is not None and "PortfolioResponse" in data and "AccountPortfolio" in data["PortfolioResponse"]:
                # Display balance information
                for acctPortfolio in data["PortfolioResponse"]["AccountPortfolio"]:
                    if acctPortfolio is not None and "Position" in acctPortfolio:
                        for position in acctPortfolio["Position"]:
                            print_str = ""
                            if position is not None and "symbolDescription" in position:
                                print_str = print_str + "Symbol: " + str(position["symbolDescription"])
                            if position is not None and "quantity" in position:
                                print_str = print_str + " | " + "Quantity #: " + str(position["quantity"])
                            if position is not None and "Quick" in position and "lastTrade" in position["Quick"]:
                                print_str = print_str + " | " + "Last Price: " \
                                            + str('${:,.2f}'.format(position["Quick"]["lastTrade"]))
                            if position is not None and "pricePaid" in position:
                                print_str = print_str + " | " + "Price Paid $: " \
                                            + str('${:,.2f}'.format(position["pricePaid"]))
                            if position is not None and "totalGain" in position:
                                print_str = print_str + " | " + "Total Gain $: " \
                                            + str('${:,.2f}'.format(position["totalGain"]))
                            if position is not None and "marketValue" in position:
                                print_str = print_str + " | " + "Value $: " \
                                            + str('${:,.2f}'.format(position["marketValue"]))
                            print(print_str)
                    else:
                        print("None")
        except Exception as e:
            print(f"Error: {e}")

    def fetch_balance(self, account_id_key, institution_type="BROKERAGE"):
        """
        Fetches the balance for a specific account.
        """
        url = self.base_url + "/v1/accounts/" + account_id_key + "/balance.json"
        params = {"instType": institution_type, "realTimeNAV": "true"}
        headers = {"consumerkey": config["DEFAULT"]["CONSUMER_KEY"]}

        response = self.session.get(url, header_auth=True, params=params, headers=headers)
        logger.debug("Request url: %s", url)
        logger.debug("Request Header: %s", response.request.headers)

        if response is not None and response.status_code == 200:
            parsed = json.loads(response.text)
            logger.debug("Response Body: %s", json.dumps(parsed, indent=4, sort_keys=True))
            return response.json()
        else:
            logger.debug("Response Body: %s", response.text)
            if response is not None and response.headers.get('Content-Type') == 'application/json':
                error_data = response.json()
                if "Error" in error_data and "message" in error_data["Error"]:
                    raise Exception(error_data["Error"]["message"])
            raise Exception("Balance API service error")

    def balance(self):
        """
        Calls account balance API to retrieve the current balance and related details for a specified account
        """
        try:
            data = self.fetch_balance(self.account["accountIdKey"], self.account["institutionType"])
            
            if data is not None and "BalanceResponse" in data:
                balance_data = data["BalanceResponse"]
                if balance_data is not None and "accountId" in balance_data:
                    print("\n\nBalance for " + balance_data["accountId"] + ":")
                else:
                    print("\n\nBalance:")
                # Display balance information
                if balance_data is not None and "accountDescription" in balance_data:
                    print("Account Nickname: " + balance_data["accountDescription"])
                if balance_data is not None and "Computed" in balance_data \
                        and "RealTimeValues" in balance_data["Computed"] \
                        and "totalAccountValue" in balance_data["Computed"]["RealTimeValues"]:
                    print("Net Account Value: "
                          + str('${:,.2f}'.format(balance_data["Computed"]["RealTimeValues"]["totalAccountValue"])))
                if balance_data is not None and "Computed" in balance_data \
                        and "marginBuyingPower" in balance_data["Computed"]:
                    print("Margin Buying Power: " + str('${:,.2f}'.format(balance_data["Computed"]["marginBuyingPower"])))
                if balance_data is not None and "Computed" in balance_data \
                        and "cashBuyingPower" in balance_data["Computed"]:
                    print("Cash Buying Power: " + str('${:,.2f}'.format(balance_data["Computed"]["cashBuyingPower"])))
        except Exception as e:
            print(f"Error: {e}")

    def account_menu(self):
        """
        Provides the different options for the sample application: balance, portfolio, view orders

        :param self: Pass in authenticated session and information on selected account
        """

        if self.account["institutionType"] == "BROKERAGE":
            menu_items = {"1": "Balance",
                          "2": "Portfolio",
                          "3": "Orders",
                          "4": "Go Back"}

            while True:
                print("")
                options = menu_items.keys()
                for entry in options:
                    print(entry + ")\t" + menu_items[entry])

                selection = input("Please select an option: ")
                if selection == "1":
                    self.balance()
                elif selection == "2":
                    self.portfolio()
                elif selection == "3":
                    order = Order(self.session, self.account, self.base_url)
                    order.view_orders()
                elif selection == "4":
                    break
                else:
                    print("Unknown Option Selected!")
        elif self.account["institutionType"] == "BANK":
            menu_items = {"1": "Balance",
                          "2": "Go Back"}

            while True:
                print("\n")
                options = menu_items.keys()
                for entry in options:
                    print(entry + ")\t" + menu_items[entry])

                selection = input("Please select an option: ")
                if selection == "1":
                    self.balance()
                elif selection == "2":
                    break
                else:
                    print("Unknown Option Selected!")
        else:
            menu_items = {"1": "Go Back"}

            while True:
                print("")
                options = menu_items.keys()
                for entry in options:
                    print(entry + ")\t" + menu_items[entry])

                selection = input("Please select an option: ")
                if selection == "1":
                    break
                else:
                    print("Unknown Option Selected!")