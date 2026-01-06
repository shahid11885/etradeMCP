import json
import logging
from client_logger import logger

class Market:
    def __init__(self, session, base_url):
        self.session = session
        self.base_url = base_url

    def fetch_quote(self, symbols):
        """
        Fetches quotes for the given symbols.
        :param symbols: A string of comma-separated symbols (e.g., "AAPL,GOOG") or a list of symbols.
        :return: List of quote data dictionaries.
        """
        if isinstance(symbols, list):
            symbols = ",".join(symbols)
            
        url = self.base_url + "/v1/market/quote/" + symbols + ".json"
        response = self.session.get(url)
        logger.debug("Request Header: %s", response.request.headers)

        if response is not None and response.status_code == 200:
            parsed = json.loads(response.text)
            logger.debug("Response Body: %s", json.dumps(parsed, indent=4, sort_keys=True))
            data = response.json()
            
            if data is not None and "QuoteResponse" in data and "QuoteData" in data["QuoteResponse"]:
                return data["QuoteResponse"]["QuoteData"]
            else:
                 if (data is not None and 'QuoteResponse' in data and 'Messages' in data["QuoteResponse"]
                        and 'Message' in data["QuoteResponse"]["Messages"]
                        and data["QuoteResponse"]["Messages"]["Message"] is not None):
                     messages = [m["description"] for m in data["QuoteResponse"]["Messages"]["Message"]]
                     raise Exception(f"API Error: {', '.join(messages)}")
                 raise Exception("Quote API service error")
        else:
            logger.debug("Response Body: %s", response)
            raise Exception("Quote API service error")

    def quotes(self):
        """
        Calls quotes API to provide quote details for equities, options, and mutual funds
        """
        symbols = input("\nPlease enter Stock Symbol: ")
        
        try:
            quotes_data = self.fetch_quote(symbols)
            
            # Print table header
            print("\n" + "=" * 80)
            print(f"{ 'MARKET QUOTES':^80}")
            print("=" * 80)

            for quote in quotes_data:
                all_data = quote.get("All", {})
                product = quote.get("Product", {})

                symbol = product.get("symbol", "N/A")
                sec_type = product.get("securityType", "N/A")
                date_time = quote.get("dateTime", "N/A")

                last_price = all_data.get("lastTrade", 0)
                change = all_data.get("changeClose", 0)
                change_pct = all_data.get("changeClosePercentage", 0)
                prev_close = all_data.get("previousClose", 0)
                bid = all_data.get("bid", 0)
                bid_size = all_data.get("bidSize", 0)
                ask = all_data.get("ask", 0)
                ask_size = all_data.get("askSize", 0)
                low = all_data.get("low", 0)
                high = all_data.get("high", 0)
                volume = all_data.get("totalVolume", 0)

                # Determine change color indicator
                change_indicator = "▲" if change >= 0 else "▼"

                print(f"\n  {symbol} ({sec_type})")
                print(f"  {date_time}")
                print("-" * 80)
                print(f"  {'Last Price:':<20} ${last_price:>12,.2f}")
                print(f"  {'Change:':<20} {change_indicator} {change:>+10,.2f} ({change_pct:+.2f}%)")
                print("-" * 80)
                print(f"  {'Previous Close:':<20} ${prev_close:>12,.2f}")
                print(f"  {'Day Range:':<20} ${low:>10,.2f} - ${high:,.2f}")
                print("-" * 80)
                print(f"  {'Bid:':<20} ${bid:>12,.2f} x {bid_size}")
                print(f"  {'Ask:':<20} ${ask:>12,.2f} x {ask_size}")
                print("-" * 80)
                print(f"  {'Volume:':<20} {volume:>13,}")

            print("\n" + "=" * 80)
        except Exception as e:
             print(f"Error: {e}")


    def fetch_option_expire_dates(self, symbol, expiry_type=None):
        """
        Fetches option expiration dates for a given symbol.
        :param symbol: The stock symbol.
        :param expiry_type: Optional filter (ALL, WEEKLY, MONTHLY, QUARTERLY).
        :return: List of expiration date dictionaries.
        """
        url = self.base_url + "/v1/market/optionexpiredate.json"
        params = {"symbol": symbol}
        if expiry_type:
            params["expiryType"] = expiry_type

        response = self.session.get(url, params=params)
        logger.debug("Request Header: %s", response.request.headers)

        if response is not None and response.status_code == 200:
            parsed = json.loads(response.text)
            logger.debug("Response Body: %s", json.dumps(parsed, indent=4, sort_keys=True))
            data = response.json()
            
            if data is not None and "OptionExpireDateResponse" in data \
                    and "ExpirationDate" in data["OptionExpireDateResponse"]:
                return data["OptionExpireDateResponse"]["ExpirationDate"]
            elif data is not None and "Error" in data and "message" in data["Error"]:
                raise Exception(data["Error"]["message"])
            else:
                raise Exception("Option Expire Date API service error")
        else:
            logger.debug("Response Body: %s", response)
            raise Exception("Option Expire Date API service error")

    def option_expire_dates(self):
        """
        Calls option expire dates API to retrieve expiration dates for a given symbol

        :param self: Passes authenticated session in parameter
        """
        symbol = input("\nPlease enter Stock Symbol: ")

        # Optional expiry type filter
        expiry_types = {
            "1": "ALL",
            "2": "WEEKLY",
            "3": "MONTHLY",
            "4": "QUARTERLY",
            "5": None  # No filter
        }

        print("\nExpiry Type Filter:")
        print("1)\tAll")
        print("2)\tWeekly")
        print("3)\tMonthly")
        print("4)\tQuarterly")
        print("5)\tNo Filter (default)")
        expiry_selection = input("Select expiry type (default: 5): ").strip() or "5"
        expiry_type = expiry_types.get(expiry_selection, None)

        try:
            expiration_dates = self.fetch_option_expire_dates(symbol, expiry_type)

            # Print table header
            print("\n" + "=" * 60)
            print(f"{ 'OPTION EXPIRATION DATES - ' + symbol.upper():^60}")
            print("=" * 60)
            print(f"  {'#':<4} {'Date':<20} {'Type':<15}")
            print("-" * 60)

            for idx, exp_date in enumerate(expiration_dates, 1):
                year = exp_date.get("year", 0)
                month = exp_date.get("month", 0)
                day = exp_date.get("day", 0)
                exp_type = exp_date.get("expiryType", "N/A")

                date_str = f"{month:02d}/{day:02d}/{year}"
                print(f"  {idx:<4} {date_str:<20} {exp_type:<15}")

            print("-" * 60)
            print(f"  Total: {len(expiration_dates)} expiration dates")
            print("=" * 60)

        except Exception as e:
            print(f"Error: {e}")

    def fetch_option_chains(self, symbol, expiry_year=None, expiry_month=None, expiry_day=None,
                           chain_type="CALLPUT", strike_price_near=None, no_of_strikes=None,
                           include_weekly=False, skip_adjusted=True, option_category="STANDARD",
                           price_type="ATNM"):
        """
        Fetches option chains for a given symbol.
        :return: Dict containing the OptionChainResponse.
        """
        # Build parameters
        params = {"symbol": symbol, "chainType": chain_type}
        
        if expiry_year: params["expiryYear"] = expiry_year
        if expiry_month: params["expiryMonth"] = expiry_month
        if expiry_day: params["expiryDay"] = expiry_day
        if strike_price_near: params["strikePriceNear"] = strike_price_near
        if no_of_strikes: params["noOfStrikes"] = no_of_strikes
        
        params["includeWeekly"] = "true" if include_weekly else "false"
        params["skipAdjusted"] = "true" if skip_adjusted else "false"
        params["optionCategory"] = option_category
        params["priceType"] = price_type

        # Build URL for the API endpoint
        url = self.base_url + "/v1/market/optionchains.json"

        # Make API call for GET request
        response = self.session.get(url, params=params)
        logger.debug("Request Header: %s", response.request.headers)

        if response is not None and response.status_code == 200:
            parsed = json.loads(response.text)
            logger.debug("Response Body: %s", json.dumps(parsed, indent=4, sort_keys=True))

            data = response.json()
            if data is not None and "OptionChainResponse" in data:
                return data["OptionChainResponse"]
            elif data is not None and "Error" in data and "message" in data["Error"]:
                raise Exception(data["Error"]["message"])
            else:
                raise Exception("Option Chain API service error")
        else:
            logger.debug("Response Body: %s", response)
            if response is not None:
                try:
                    error_data = response.json()
                    if "Error" in error_data and "message" in error_data["Error"]:
                        raise Exception(error_data["Error"]["message"])
                except:
                    pass
            raise Exception("Option Chain API service error")

    def option_chains(self):
        """
        Calls option chains API to retrieve option chain data for a given symbol

        :param self: Passes authenticated session in parameter
        """
        symbol = input("\nPlease enter Stock Symbol: ")
        
        # Expiration date (optional)
        print("\nEnter expiration date (leave blank to skip):")
        expiry_year = input("  Expiry Year (e.g., 2026): ").strip()
        expiry_month = None
        expiry_day = None
        
        if expiry_year:
            expiry_month = input("  Expiry Month (1-12): ").strip()
            expiry_day = input("  Expiry Day (1-31): ").strip()

        # Chain type
        chain_types = {"1": "CALLPUT", "2": "CALL", "3": "PUT"}
        print("\nChain Type:")
        print("1)\tCalls and Puts (default)")
        print("2)\tCalls Only")
        print("3)\tPuts Only")
        chain_selection = input("Select chain type (default: 1): ").strip() or "1"
        chain_type = chain_types.get(chain_selection, "CALLPUT")

        # Strike price filter
        strike_near = input("\nStrike price near (leave blank for default): ").strip()
        
        # Number of strikes
        no_of_strikes = input("Number of strikes to retrieve (leave blank for default): ").strip()

        # Include weekly options
        print("\nInclude weekly options?")
        print("1)\tNo (default)")
        print("2)\tYes")
        weekly_selection = input("Select (default: 1): ").strip() or "1"
        include_weekly = True if weekly_selection == "2" else False

        try:
            chain_response = self.fetch_option_chains(
                symbol, expiry_year, expiry_month, expiry_day,
                chain_type, strike_near, no_of_strikes, include_weekly
            )
            
            option_pairs = chain_response.get("OptionPair", [])
            near_price = chain_response.get("nearPrice", 0)
            selected = chain_response.get("SelectedED", {})

            exp_month = selected.get("month", "")
            exp_day = selected.get("day", "")
            exp_year = selected.get("year", "")
            exp_date_str = f"{exp_month}/{exp_day}/{exp_year}" if exp_year else "N/A"

            # Print table header
            print("\n" + "=" * 120)
            print(f"{ 'OPTION CHAIN - ' + symbol.upper():^120}")
            print(f"{ 'Expiration: ' + exp_date_str + ' | Near Price: $' + str(near_price):^120}")
            print("=" * 120)

            if chain_type in ["CALLPUT", "CALL"]:
                self._print_option_chain_header("CALLS")
                for pair in option_pairs:
                    call = pair.get("Call")
                    if call:
                        self._print_option_row(call)
                print("-" * 120)

            if chain_type in ["CALLPUT", "PUT"]:
                self._print_option_chain_header("PUTS")
                for pair in option_pairs:
                    put = pair.get("Put")
                    if put:
                        self._print_option_row(put)
                print("-" * 120)

            print(f"\n  Total Option Pairs: {len(option_pairs)}")
            print("=" * 120)

        except Exception as e:
            print(f"Error: {e}")

    def _print_option_chain_header(self, option_type):
        """Print header row for option chain table"""
        print(f"\n  {option_type}")
        print("-" * 120)
        print(f"  {'Strike':>10} {'Last':>10} {'Bid':>10} {'Ask':>10} {'Volume':>10} {'Open Int':>10} {'IV':>10} {'Delta':>8} {'Theta':>8}")
        print("-" * 120)

    def _print_option_row(self, option):
        """Print a single option row"""
        strike = option.get("strikePrice", 0)
        last = option.get("lastPrice", 0)
        bid = option.get("bid", 0)
        ask = option.get("ask", 0)
        volume = option.get("volume", 0)
        open_int = option.get("openInterest", 0)

        greeks = option.get("OptionGreeks", {})
        iv = greeks.get("iv", 0) * 100 if greeks.get("iv") else 0
        delta = greeks.get("delta", 0)
        theta = greeks.get("theta", 0)

        print(f"  {strike:>10.2f} {last:>10.2f} {bid:>10.2f} {ask:>10.2f} {volume:>10,} {open_int:>10,} {iv:>9.1f}% {delta:>8.3f} {theta:>8.3f}")