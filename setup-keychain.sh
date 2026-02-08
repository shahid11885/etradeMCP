#!/bin/bash

# Activate the virtual environment
source venv/bin/activate

# Store E*TRADE credentials in macOS Keychain
python src/cli/main.py setup-keychain
