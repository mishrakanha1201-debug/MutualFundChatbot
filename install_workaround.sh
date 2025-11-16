#!/bin/bash
# Workaround installation script for network-restricted environments

echo "Attempting to install packages with various workarounds..."

# Method 1: Try with different index
echo "Method 1: Using alternative index..."
python3 -m pip install --user --index-url https://pypi.python.org/simple/ beautifulsoup4 requests pdfplumber google-generativeai python-dotenv loguru lxml

if [ $? -eq 0 ]; then
    echo "✓ Installation successful!"
    exit 0
fi

# Method 2: Try with trusted hosts
echo "Method 2: Using trusted hosts..."
python3 -m pip install --user --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org beautifulsoup4 requests pdfplumber google-generativeai python-dotenv loguru lxml

if [ $? -eq 0 ]; then
    echo "✓ Installation successful!"
    exit 0
fi

# Method 3: Try upgrading pip first
echo "Method 3: Upgrading pip and retrying..."
python3 -m pip install --user --upgrade pip
python3 -m pip install --user beautifulsoup4 requests pdfplumber google-generativeai python-dotenv loguru lxml

if [ $? -eq 0 ]; then
    echo "✓ Installation successful!"
    exit 0
fi

echo "✗ All methods failed. Please check:"
echo "  1. Network connectivity"
echo "  2. Firewall/proxy settings"
echo "  3. VPN configuration"
echo "  4. Corporate network restrictions"


