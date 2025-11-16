# Quick Start Guide

## Start the Application

### Terminal 1: Backend API
```bash
cd "/Users/kanha.m/Mutual Fund Chatbot"
python3 scripts/run_api.py
```
✅ Backend running on http://localhost:8000

### Terminal 2: Frontend
```bash
cd "/Users/kanha.m/Mutual Fund Chatbot/frontend"
python3 serve.py
```
✅ Frontend running on http://localhost:3000

### Open Browser
Navigate to: **http://localhost:3000**

## Test the Chatbot

1. Click on an example question, OR
2. Type your own question like:
   - "What is the expense ratio of HDFC ELSS Fund?"
   - "What is the lock-in period for ELSS?"
   - "What is the minimum SIP amount?"

## Features

- ✅ Welcome screen with example questions
- ✅ Real-time chat interface
- ✅ Source links in every answer
- ✅ Timestamps for all responses
- ✅ Loading states
- ✅ Groww brand styling

## Troubleshooting

**Backend not responding?**
- Check if API is running: `curl http://localhost:8000/api/health`
- Check terminal for errors

**Frontend not loading?**
- Check browser console (F12)
- Verify both servers are running
- Try refreshing the page

**CORS errors?**
- Backend has CORS enabled
- Make sure backend is running on port 8000
