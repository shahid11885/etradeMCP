#!/bin/bash

# Activate the virtual environment
source venv/bin/activate

# Run the CLI application, generate tokens and immediately exit

python src/cli/main.py  generate-tokens

