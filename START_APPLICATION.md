# How to Start the Application

## Quick Start

### Step 1: Start Backend API (Terminal 1)

```bash
cd "/Users/kanha.m/Mutual Fund Chatbot"
python3 scripts/run_api.py
```

**Wait for:** `Uvicorn running on http://0.0.0.0:8000`

### Step 2: Start Frontend Server (Terminal 2)

**Option A: Using the Python server script**
```bash
cd "/Users/kanha.m/Mutual Fund Chatbot/frontend"
python3 serve.py
```

**Option B: Using the start script**
```bash
cd "/Users/kanha.m/Mutual Fund Chatbot/frontend"
./start.sh
```

**Option C: Using Python's built-in server**
```bash
cd "/Users/kanha.m/Mutual Fund Chatbot/frontend"
python3 -m http.server 3000
```

**Wait for:** `Frontend server running at http://localhost:3000`

### Step 3: Open in Browser

Navigate to: **http://localhost:3000**

## Verify Both Servers Are Running

**Check Backend:**
```bash
curl http://localhost:8000/api/health
```
Should return: `{"status":"ok",...}`

**Check Frontend:**
```bash
curl http://localhost:3000
```
Should return: HTML content

## Troubleshooting

### Error: "This site can't be reached" / "ERR_CONNECTION_REFUSED"

**Solution:** The frontend server is not running. Start it using Step 2 above.

### Error: "Failed to fetch" in browser console

**Solution:** The backend API is not running. Start it using Step 1 above.

### Port Already in Use

If you see "Address already in use":

**For port 3000 (Frontend):**
```bash
lsof -ti:3000 | xargs kill -9
```

**For port 8000 (Backend):**
```bash
lsof -ti:8000 | xargs kill -9
```

Then restart the servers.

## Testing

1. Open http://localhost:3000
2. You should see the welcome screen with:
   - "Mutual Fund Fact Finder" title
   - Welcome message
   - 3 example questions
   - Input bar at the bottom

3. Click an example question or type your own
4. You should see:
   - Your question in a gray bubble (right side)
   - Loading animation
   - Answer in a green bubble (left side)
   - Source link (green, clickable)
   - Timestamp

## Both Servers Must Be Running

⚠️ **Important:** Both the backend (port 8000) and frontend (port 3000) must be running simultaneously for the chatbot to work.


