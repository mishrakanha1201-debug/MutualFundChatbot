#!/bin/bash
echo "Attempting to install packages..."
echo "If this fails, you may need to:"
echo "1. Check your network/firewall settings"
echo "2. Configure proxy if behind corporate firewall"
echo "3. Install packages manually from another machine"
echo ""
python3 -m pip install --user beautifulsoup4 requests pdfplumber google-generativeai python-dotenv loguru lxml
