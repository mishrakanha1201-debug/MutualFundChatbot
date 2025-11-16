# Mutual Fund Fact Finder - Frontend

A high-fidelity, minimalist chat interface for the Mutual Fund FAQ Bot, designed to match Groww's brand identity.

## Features

- ✅ Welcome state with example questions
- ✅ Clean chat interface with user and assistant bubbles
- ✅ Real-time API integration
- ✅ Source links and timestamps
- ✅ Loading states
- ✅ Responsive design
- ✅ Groww brand colors and typography

## Setup

1. **Start the Backend API** (in a separate terminal):
   ```bash
   cd "/Users/kanha.m/Mutual Fund Chatbot"
   python3 scripts/run_api.py
   ```

2. **Serve the Frontend**:
   
   Option 1: Using Python's built-in server:
   ```bash
   cd frontend
   python3 -m http.server 3000
   ```
   
   Option 2: Using Node.js http-server:
   ```bash
   npx http-server frontend -p 3000
   ```

3. **Open in Browser**:
   Navigate to `http://localhost:3000`

## API Configuration

The frontend is configured to connect to the backend API at `http://localhost:8000`.

To change the API URL, edit `app.jsx`:
```javascript
const API_BASE_URL = 'http://localhost:8000';
```

## Design Specifications

### Colors
- Primary Green: `#00B386`
- Light Green (Assistant): `#EBF9F5`
- Dark Text: `#44475B`
- Secondary Text: `#7C7E8C`
- User Bubble: `#F9F9F9`
- Borders: `#EFEFEF`

### Typography
- Font: Inter (fallback: Manrope)
- Body: 14px, Regular
- Headings: 18px, Semi-Bold
- Links: 14px, Medium

## Components

- **WelcomeState**: Initial screen with example questions
- **MessageBubble**: User and assistant message bubbles
- **LoadingBubble**: Loading animation
- **ChatApp**: Main application component

## Notes

- The frontend uses React via CDN (no build step required)
- All styling matches Groww's brand guidelines
- The interface is designed to be embedded in the Groww app/website


