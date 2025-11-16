# Troubleshooting Guide

## Error: "Sorry, I encountered an error. Please try again later."

This error means the **backend API is not running** or not accessible.

### Solution 1: Start the Backend API

**In a new terminal window:**

```bash
cd "/Users/kanha.m/Mutual Fund Chatbot"
python3 scripts/run_api.py
```

**Wait for this message:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Solution 2: Check if Backend is Running

```bash
curl http://localhost:8000/api/health
```

**Expected response:**
```json
{"status":"ok","message":"API is running smoothly.",...}
```

**If you get "Connection refused":**
- The backend is not running
- Start it using Solution 1

### Solution 3: Check Browser Console

1. Open browser Developer Tools (F12 or Cmd+Option+I)
2. Go to Console tab
3. Look for error messages like:
   - `Failed to fetch`
   - `NetworkError`
   - `CORS error`

### Solution 4: Verify Both Servers Are Running

**Check Frontend (port 3000):**
```bash
lsof -ti:3000
```
Should show a process ID

**Check Backend (port 8000):**
```bash
lsof -ti:8000
```
Should show a process ID

### Solution 5: Install Missing Dependencies

If you see import errors when starting the backend:

```bash
# Try installing FastAPI (if network allows)
pip install fastapi uvicorn

# Or use the workaround (standard library only)
# The backend should work without FastAPI for testing
```

### Solution 6: Test API Directly

```bash
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{"question":"What is the expense ratio of HDFC ELSS Fund?"}'
```

**Expected:** JSON response with answer

**If this fails:** Backend is not running or has errors

## Quick Fix Checklist

- [ ] Backend API is running on port 8000
- [ ] Frontend server is running on port 3000
- [ ] No firewall blocking localhost connections
- [ ] Browser console shows no CORS errors
- [ ] API health endpoint responds: `curl http://localhost:8000/api/health`

## Common Issues

### Issue: "FastAPI not installed"
**Solution:** The backend uses standard library workarounds. It should work without FastAPI installation, but if you see import errors, the backend may need to be started differently.

### Issue: Port already in use
**Solution:**
```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9

# Kill process on port 3000
lsof -ti:3000 | xargs kill -9
```

### Issue: CORS errors
**Solution:** The backend has CORS enabled. If you still see errors, check that:
- Backend is running on http://localhost:8000
- Frontend is making requests to http://localhost:8000
- No proxy or VPN interfering

## Still Not Working?

1. Check terminal output for error messages
2. Check browser console (F12) for JavaScript errors
3. Verify .env file has GEMINI_API_KEY set
4. Test backend directly with curl commands
5. Check that data/scraped directory has fund data


