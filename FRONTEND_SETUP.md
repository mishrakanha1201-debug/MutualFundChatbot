# Frontend Setup Guide

## Quick Start

### 1. Start the Backend API

In one terminal:
```bash
cd "/Users/kanha.m/Mutual Fund Chatbot"
python3 scripts/run_api.py
```

The API will run on `http://localhost:8000`

### 2. Start the Frontend Server

In another terminal:

**Option 1: Using Python (Recommended)**
```bash
cd "/Users/kanha.m/Mutual Fund Chatbot/frontend"
python3 serve.py
```

**Option 2: Using Python's built-in server**
```bash
cd "/Users/kanha.m/Mutual Fund Chatbot/frontend"
python3 -m http.server 3000
```

**Option 3: Using Node.js http-server**
```bash
cd "/Users/kanha.m/Mutual Fund Chatbot/frontend"
npx http-server -p 3000
```

### 3. Open in Browser

Navigate to: `http://localhost:3000`

## Features

✅ **Welcome State**
- Clean header with "Mutual Fund Fact Finder" title
- Welcome message
- Disclaimer text
- 3 clickable example questions

✅ **Chat Interface**
- User messages (right-aligned, gray background)
- Assistant messages (left-aligned, green background)
- Source links (clickable, green color)
- Timestamps (subtle gray text)
- Loading animation

✅ **Design**
- Matches Groww brand colors exactly
- Inter font family
- Minimalist, professional design
- Responsive layout

## API Configuration

The frontend connects to the backend API. To change the API URL, edit `frontend/app.jsx`:

```javascript
const API_BASE_URL = 'http://localhost:8000';
```

## File Structure

```
frontend/
├── index.html      # Main HTML file
├── app.jsx         # React application
├── styles.css      # Groww brand styling
├── serve.py        # Python server script
└── README.md       # Documentation
```

## Testing

1. Start both backend and frontend servers
2. Open `http://localhost:3000` in your browser
3. Try the example questions or type your own
4. Verify:
   - Welcome state displays correctly
   - Questions are sent to API
   - Answers display with source links
   - Timestamps are shown
   - Loading state works

## Troubleshooting

**CORS Errors:**
- Make sure the backend API has CORS enabled (already configured)
- Check that API is running on port 8000

**API Connection Failed:**
- Verify backend is running: `curl http://localhost:8000/api/health`
- Check browser console for errors
- Verify API_BASE_URL in app.jsx

**Styling Issues:**
- Ensure `styles.css` is loaded
- Check browser console for CSS errors
- Verify Inter font is loading

## Design Specifications

All design elements match Groww's brand guidelines:

- **Colors**: Primary Green (#00B386), Light Green (#EBF9F5), etc.
- **Typography**: Inter font, 14px body, 18px headings
- **Spacing**: Consistent padding and margins
- **Components**: Minimalist, no unnecessary elements


