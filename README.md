# Mutual Fund FAQ Bot

A comprehensive FAQ assistant that answers factual questions about mutual fund schemes using data extracted from official sources. The bot uses Google Gemini AI for intelligent data extraction and retrieval-augmented generation (RAG) to provide accurate, fact-based answers.

**Disclaimer: Facts-only. No investment advice.** This bot provides factual information from official sources only. It does not provide investment recommendations or financial advice.

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

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- Google Gemini API key
- Internet connection for scraping

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create a `.env` file in the project root:

```bash
GEMINI_API_KEY=your_gemini_api_key_here
SCRAPER_DELAY=2
SCRAPER_TIMEOUT=30
```

**Getting your Gemini API key:**
1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key" or use an existing key
4. Copy the API key and add it to your `.env` file

### 3. Run Data Scraper (Optional - for initial data collection)

To scrape and collect data from official sources:

```bash
python scripts/run_scraper.py
```

**Output:**
- Individual fund data: `data/scraped/{fund_name}_{timestamp}.json`
- Consolidated data: `data/scraped/all_funds_{timestamp}.json`
- Logs: `logs/scraper_{timestamp}.log`

### 4. Start the Backend API

For local development:

```bash
cd backend/api
python main.py
```

Or use the provided script:

```bash
python scripts/start_backend.sh
```

The API will be available at `http://localhost:8000`

### 5. Deploy to Vercel (Production)

1. Connect your GitHub repository to Vercel
2. Add `GEMINI_API_KEY` as an environment variable in Vercel project settings
3. Deploy automatically on push to main branch

See [VERCEL_SETUP.md](VERCEL_SETUP.md) for detailed deployment instructions.

### 6. Access the Chatbot

- **Local**: Open `http://localhost:8000` in your browser
- **Vercel**: Access your deployed URL (e.g., `https://your-app.vercel.app`)

## Scope

### Asset Management Companies (AMCs)

Currently supported:
- **HDFC Mutual Fund** (HDFC Asset Management Company Limited)

### Mutual Fund Schemes

The bot currently provides information about the following HDFC Mutual Fund schemes:

1. **HDFC Large and Mid Cap Fund**
   - Category: Large & Mid Cap
   - Scheme Type: Open-ended

2. **HDFC Flexi Cap Fund**
   - Category: Flexi Cap
   - Scheme Type: Open-ended

3. **HDFC ELSS Tax Saver Fund**
   - Category: ELSS (Equity Linked Savings Scheme)
   - Scheme Type: Open-ended (with 3-year lock-in)

### Data Sources

All information is extracted from official sources:
- **AMFI Portal**: Association of Mutual Funds in India official documents
- **SEBI Portal**: Securities and Exchange Board of India fund details
- **AMC Websites**: Official fund house websites
- **Distributor Platforms**: Authorized distributor websites (e.g., Groww)

See [SOURCES.md](SOURCES.md) or [SOURCES.csv](SOURCES.csv) for complete list of source URLs.

### Supported Queries

The bot can answer questions about:
- Fund descriptions and investment objectives
- Expense ratios and fees
- Exit loads and redemption charges
- Minimum SIP and lump sum amounts
- Lock-in periods (for ELSS funds)
- Riskometer ratings
- Benchmark indices
- Statement download procedures
- NAV, AUM, and other fund metrics
- Fund manager details
- Asset allocation

See [SAMPLE_QA.md](SAMPLE_QA.md) for example queries and responses.

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

## Known Limitations

### Current Limitations

1. **Limited AMC Coverage**
   - Currently supports only HDFC Mutual Fund
   - Expansion to other AMCs is planned for future releases

2. **Limited Scheme Coverage**
   - Supports 3 HDFC schemes only
   - Additional schemes can be added by updating configuration

3. **Data Freshness**
   - Data is scraped periodically, not in real-time
   - NAV and AUM values may not reflect the latest market data
   - Users should verify current values from official sources

4. **API Rate Limits**
   - Gemini API has rate limits and quotas
   - The bot implements automatic retry with exponential backoff
   - High traffic may result in temporary unavailability

5. **Query Scope**
   - Answers are based on scraped official documents only
   - Cannot answer questions about:
     - Performance predictions
     - Investment recommendations
     - Tax planning advice
     - Market analysis

6. **Language Support**
   - Currently supports English only
   - Multi-language support is planned for future releases

7. **Serverless Constraints**
   - Cold starts may cause initial response delays
   - Data files must be included in deployment package
   - Limited file system access in serverless environments

### Workarounds

- **Rate Limiting**: The bot automatically retries failed requests with exponential backoff
- **Data Updates**: Run the scraper periodically to update fund information
- **Error Handling**: User-friendly error messages guide users when issues occur

## Disclaimer

**Facts-only. No investment advice.**

This chatbot provides factual information extracted from official mutual fund documents and regulatory sources. It does NOT provide:
- Investment recommendations
- Financial advice
- Performance predictions
- Tax planning suggestions
- Market analysis

All information is for educational and informational purposes only. Users should:
- Verify information from official sources
- Consult qualified financial advisors before making investment decisions
- Read scheme documents carefully before investing
- Understand that past performance does not guarantee future results

## Documentation

- [SOURCES.md](SOURCES.md) - Complete list of data source URLs
- [SOURCES.csv](SOURCES.csv) - Source URLs in CSV format
- [SAMPLE_QA.md](SAMPLE_QA.md) - Sample questions and answers
- [VERCEL_SETUP.md](VERCEL_SETUP.md) - Vercel deployment guide
- [API_QUICKSTART.md](API_QUICKSTART.md) - API documentation
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Common issues and solutions

## Contributing

This is a Groww FinTech project. For contributions or issues, please contact the development team.

## License

Proprietary - Groww Internal Project

