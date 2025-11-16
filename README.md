# Mutual Fund FAQ Bot - Phase 1: Data Collection & Storage

A comprehensive scraper system for extracting mutual fund information from official sources using intelligent AI-powered data extraction.

## Features

- **Multi-Source Scraping**: Extracts data from AMFI PDFs, SEBI portal, Groww, and HDFC websites
- **Intelligent Extraction**: Uses Google Gemini AI to identify and extract relevant data points automatically
- **Flexible Data Storage**: Stores data in JSON format with support for dynamic/additional fields
- **SEBI PDF Handling**: Automatically downloads and parses PDFs from SEBI portal
- **Comprehensive Logging**: Detailed logs for debugging and monitoring

## Project Structure

```
mutual-fund-chatbot/
├── backend/
│   ├── scraper/
│   │   ├── pdf_scraper.py      # PDF download & parsing
│   │   ├── html_scraper.py     # HTML content extraction
│   │   ├── sebi_scraper.py     # SEBI portal scraper
│   │   └── data_extractor.py   # Main orchestrator with Gemini
│   ├── llm/
│   │   └── gemini_client.py    # Gemini API integration
│   └── database/
│       └── storage.py          # Data storage (JSON)
├── config/
│   └── fund_sources.json       # Fund URLs configuration
├── scripts/
│   ├── run_scraper.py          # Main scraper script
│   └── test_scraper.py         # Component test script
├── data/
│   └── scraped/                # Output directory
├── downloads/                   # Downloaded PDFs
└── logs/                        # Log files
```

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Create a `.env` file:

```bash
GEMINI_API_KEY=your_gemini_api_key_here
SCRAPER_DELAY=2
SCRAPER_TIMEOUT=30
```

Get your Gemini API key from [Google AI Studio](https://makersuite.google.com/app/apikey)

### 3. Run the Scraper

```bash
python scripts/run_scraper.py
```

### 4. Check Results

- Individual fund data: `data/scraped/{fund_name}_{timestamp}.json`
- Consolidated data: `data/scraped/all_funds_{timestamp}.json`
- Logs: `logs/scraper_{timestamp}.log`

## Data Sources

Currently configured for:
- **HDFC Large and Mid Cap Fund**
  - AMFI PDF, AMFI SSD PDF, SEBI portal, Groww website
- **HDFC Flexi Cap Fund**
  - AMFI PDF, AMFI SSD PDF, SEBI portal, HDFC website
- **HDFC ELSS Tax Saver Fund**
  - AMFI PDF, AMFI SSD PDF, SEBI portal, HDFC website

## Extracted Data Points

The scraper intelligently extracts:
- Expense ratio
- Exit load
- Minimum SIP amount
- Lock-in period (for ELSS)
- Riskometer rating
- Benchmark index
- Statement download procedures
- NAV, AUM
- Fund manager details
- Investment objective
- **Plus any other relevant data points found automatically**

## Documentation

See [SETUP.md](SETUP.md) for detailed setup instructions and troubleshooting.

## Next Steps

After Phase 1 completion:
- Phase 2: LLM Integration & RAG Pipeline
- Phase 3: Backend API Development
- Phase 4: Frontend Development

