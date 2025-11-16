# Quick Fix: Backend Connection Error

## If you see: "Unable to connect to the server"

### Step 1: Restart the Backend

**Kill old process and start fresh:**

```bash
# Kill any existing backend
lsof -ti:8000 | xargs kill -9

# Start the backend
cd "/Users/kanha.m/Mutual Fund Chatbot"
python3 scripts/run_api_simple.py
```

**Wait for this message:**
```
INFO:__main__:Starting API server on http://localhost:8000
```

### Step 2: Verify Backend is Running

**In a new terminal, test:**
```bash
curl http://localhost:8000/api/health
```

**Expected response:**
```json
{"status":"ok","message":"API is running smoothly.",...}
```

### Step 3: Refresh Browser

1. Go to http://localhost:3000
2. Press **Ctrl+R** (or **Cmd+R** on Mac) to refresh
3. Try asking a question

## Common Issues

### Backend takes time to start
- The RAG pipeline needs to load (takes 5-10 seconds)
- Wait for: "RAG pipeline ready!" message
- Then: "Starting API server on http://localhost:8000"

### Port already in use
```bash
# Find and kill process on port 8000
lsof -ti:8000 | xargs kill -9
```

### Backend crashes on startup
- Check terminal for error messages
- Verify .env file has GEMINI_API_KEY
- Check that data/scraped directory exists

## Both Servers Must Run

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

## Test Connection

```bash
# Health check
curl http://localhost:8000/api/health

# Test query
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{"question":"What is the expense ratio?"}'
```

If both return JSON, the backend is working! ✅


