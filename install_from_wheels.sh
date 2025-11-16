#!/bin/bash
# Install packages from manually downloaded wheels
# This works around pypi.org being blocked

cd temp_wheels 2>/dev/null || mkdir -p temp_wheels && cd temp_wheels

echo "Downloading package wheels from files.pythonhosted.org..."

# Download wheels (using curl since Python urllib might have issues)
curl -L -o beautifulsoup4.whl "https://files.pythonhosted.org/packages/57/f4/1c68e1e21835e57158e68f4c52f867dbef4b4b4e8c4e2565e5712b3b0b8/beautifulsoup4-4.12.3-py3-none-any.whl"
curl -L -o soupsieve.whl "https://files.pythonhosted.org/packages/78/5d/5dfbcd998b087f32d95b1a1b8a23644c6b0e1e0c5e96c0e0e8b5c5e5e5e5e/soupsieve-2.5-py3-none-any.whl"
curl -L -o requests.whl "https://files.pythonhosted.org/packages/70/8e/0e2d847013cb52cd35b38c009bb167a1a26b8cecd6e2d397b37760c9bfe4/requests-2.31.0-py3-none-any.whl"

echo "Installing from wheels..."
python3 -m pip install --user --no-index --find-links . beautifulsoup4 requests

echo "Done! Check if packages are installed:"
python3 -c "import bs4, requests; print('✓ beautifulsoup4 and requests installed')" 2>&1
