# How to Start the Backend API

## Option 1: Simple HTTP Server (Recommended - No Dependencies)

This uses only Python standard library, no FastAPI needed:

```bash
cd "/Users/kanha.m/Mutual Fund Chatbot"
python3 scripts/run_api_simple.py
```

**Wait for:**
```
Starting API server on http://localhost:8000
```

## Option 2: FastAPI Server (If FastAPI is installed)

```bash
cd "/Users/kanha.m/Mutual Fund Chatbot"
python3 scripts/run_api.py
```

## Verify Backend is Running

```bash
curl http://localhost:8000/api/health
```

**Expected response:**
```json
{
  "status": "ok",
  "message": "API is running smoothly.",
  "rag_initialized": true,
  ...
}
```

## Test a Query

```bash
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{"question":"What is the expense ratio of HDFC ELSS Fund?"}'
```

## Complete Setup

**Terminal 1 - Backend:**
```bash
cd "/Users/kanha.m/Mutual Fund Chatbot"
python3 scripts/run_api_simple.py
```

**Terminal 2 - Frontend:**
```bash
cd "/Users/kanha.m/Mutual Fund Chatbot/frontend"
python3 serve.py
```

**Browser:**
Open http://localhost:3000

## Troubleshooting

**Port 8000 already in use:**
```bash
lsof -ti:8000 | xargs kill -9
```

**Backend not responding:**
- Check terminal for error messages
- Verify .env file has GEMINI_API_KEY
- Check that data/scraped directory exists with fund data


