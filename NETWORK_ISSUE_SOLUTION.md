# Network Issue: pip Cannot Access PyPI

## Problem
pip is getting "Could not find a version that satisfies the requirement" because `pypi.org` is blocked by your network/firewall.

## Diagnosis
- ✓ Internet connectivity: Working
- ✗ pypi.org: Blocked (403 Forbidden)
- ✓ files.pythonhosted.org: Accessible

## Solutions

### Option 1: Use Corporate PyPI Mirror (Recommended)
If your organization has a PyPI mirror, configure pip to use it:

```bash
python3 -m pip install --user --index-url https://your-corporate-mirror.com/simple beautifulsoup4 requests pdfplumber google-generativeai python-dotenv loguru lxml
```

### Option 2: Configure Proxy
If you're behind a corporate proxy:

```bash
export HTTP_PROXY=http://proxy.company.com:8080
export HTTPS_PROXY=http://proxy.company.com:8080
python3 -m pip install --user beautifulsoup4 requests pdfplumber google-generativeai python-dotenv loguru lxml
```

### Option 3: Install from Different Network
- Use a personal hotspot
- Connect from home network
- Use a different VPN endpoint

### Option 4: Use Conda (if available)
```bash
conda install -c conda-forge beautifulsoup4 requests python-dotenv lxml
pip install pdfplumber google-generativeai loguru
```

### Option 5: Contact IT
Ask your IT department to:
- Whitelist pypi.org and pypi.python.org
- Provide corporate PyPI mirror URL
- Configure proxy settings for pip

## Quick Test
After installation, verify:
```bash
python3 -c "import bs4, requests, pdfplumber, google.generativeai, dotenv, loguru, lxml; print('All packages installed!')"
```

Then run the scraper:
```bash
python3 scripts/run_scraper.py
```


