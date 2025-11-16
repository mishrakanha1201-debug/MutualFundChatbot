#!/bin/bash

# Start script for Railway deployment
# This script ensures the API server starts correctly

echo "Starting Mutual Fund Chatbot API..."

# Check if .env file exists and load it
if [ -f .env ]; then
    echo "Loading environment variables from .env"
    export $(cat .env | grep -v '^#' | xargs)
fi

# Start the API server
python3 scripts/run_api_simple.py

