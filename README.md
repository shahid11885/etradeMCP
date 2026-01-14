# E*TRADE API Python Sample Application

This sample Python application provides examples on using the ETRADE API endpoints.

## Table of Contents

* [Requirements](#requirements)
* [Setup](#setup)
* [Running Code](#running-code)

## Requirements

In order to run this sample application you need the following three items:

1. Python 3 - this sample application is written in Python and requires Python 3. If you do not
already have Python 3 installed, download it from

   [`https://www.python.org/downloads/`](https://www.python.org/downloads/).

2. An [E*TRADE](https://us.etrade.com) account

3. E*TRADE consumer key and consumer secret.

### Obtaining E*TRADE API Credentials

To get your Consumer Key and Consumer Secret:

1.  **E*TRADE Account:** You must have an existing E*TRADE account.
2.  **Developer Portal:** Navigate to the [E*TRADE Developer website](https://developer.etrade.com/home).
3.  **Log In:** Log in using your E*TRADE account credentials.
4.  **Create Keys:** Look for an option to "Create Key" or "Get Sandbox Key." You will typically be provided with both Sandbox and Live (Production) keys. For live keys, you might need to complete an API Developer Agreement and a User Intent Survey.
5.  **Record Keys:** Carefully record your Consumer Key and Consumer Secret for both Sandbox and Production environments. These will be used in your `config.ini` file.


## Setup

1. Unzip python zip file

2. Copy the example configuration file `config/config.ini.example` to `config/config.ini`.

   ```bash
   cp config/config.ini.example config/config.ini
   ```

3. Edit `config.ini` with your consumer key and consumer secret.

   **Note:** The application is designed to be flexible. If you only plan to use the production environment, you only need to provide the production keys. If you only use the sandbox, you only need the sandbox keys.

4. Create the virtual environment by running the Python's venv command; see the command syntax below

```
$ python3 -m venv venv
```

5. Activate the Python virtual environment

On Windows, run:

```
$ venv\Scripts\activate.bat
```

On Unix or Mac OS, run:

```
$ source venv/bin/activate
```

6. Use pip to install dependencies for the sample application

```
$ pip install -r requirements.txt
```

## Running Code

Complete these steps to run the code for the sample application:

1. Activate the Python virtual environment

On Windows, run:

```
$ venv\Scripts\activate.bat
```

On Unix or Mac OS, run:

```
$ source venv/bin/activate
```

2. Run the CLI application

```
$ python src/cli/main.py
```

3. Run the MCP server

```
$ python src/mcp/server.py
```