#!/bin/bash

# This script automates the setup of the Python virtual environment.

# Check if the venv directory already exists
if [ -d "venv" ]; then
    echo "Virtual environment 'venv' already exists."
else
    echo "Creating virtual environment 'venv'..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "Error: Failed to create virtual environment."
        exit 1
    fi
fi

# Install dependencies using the virtual environment's pip
echo "Installing dependencies from requirements.txt..."
venv/bin/pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "Error: Failed to install dependencies."
    exit 1
fi

# Create logs directory if it doesn't exist
if [ ! -d "logs" ]; then
    echo "Creating 'logs' directory..."
    mkdir logs
    if [ $? -ne 0 ]; then
        echo "Error: Failed to create 'logs' directory."
        exit 1
    fi
fi

echo ""
echo "Environment setup complete."
echo "To activate the virtual environment, run:"
echo "source venv/bin/activate"
