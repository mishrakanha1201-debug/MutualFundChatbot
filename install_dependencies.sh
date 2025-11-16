#!/bin/bash
# Installation script for Mutual Fund Chatbot dependencies

echo "Installing Python dependencies..."

# Try pip3 first, then python3 -m pip
if command -v pip3 &> /dev/null; then
    pip3 install --user beautifulsoup4 requests pdfplumber google-generativeai python-dotenv loguru lxml
elif command -v python3 &> /dev/null; then
    python3 -m pip install --user beautifulsoup4 requests pdfplumber google-generativeai python-dotenv loguru lxml
else
    echo "Error: Neither pip3 nor python3 found"
    exit 1
fi

echo "Installation complete!"
echo "You can now run: python3 scripts/run_scraper.py"


