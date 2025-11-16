# Railway Deployment Guide

## Prerequisites

1. **GitHub Repository**: Your code should be pushed to GitHub
2. **Railway Account**: Sign up at https://railway.app
3. **Environment Variables**: You'll need to set up your Gemini API key

## Deployment Steps

### 1. Connect Repository to Railway

1. Go to https://railway.app
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Choose your repository: `mishrakanha1201-debug/MutualFundChatbot`

### 2. Configure Environment Variables

In Railway dashboard, go to your project → Variables tab and add:

```
GEMINI_API_KEY=your_gemini_api_key_here
```

### 3. Railway Configuration

The project includes:
- `Procfile` - Tells Railway how to start the app
- `railway.json` - Railway-specific configuration
- `start.sh` - Alternative start script

Railway will automatically:
- Detect Python
- Install dependencies from `requirements.txt`
- Run the start command from `Procfile`

### 4. Deploy

Railway will automatically deploy when you push to GitHub, or you can:
- Click "Deploy" in Railway dashboard
- Or push a new commit to trigger deployment

## Start Command

The app uses: `python3 scripts/run_api_simple.py`

This script:
- Uses Python standard library (no FastAPI/uvicorn needed)
- Automatically uses Railway's PORT environment variable
- Initializes the RAG pipeline on startup

## Health Check

After deployment, check:
- Health endpoint: `https://your-app.railway.app/api/health`
- Should return: `{"status": "ok", "rag_initialized": true, ...}`

## Troubleshooting

### "No start command found"
- Ensure `Procfile` exists in root directory
- Check that `railway.json` has correct startCommand

### Port binding issues
- The script automatically uses Railway's PORT env variable
- Defaults to 8000 if PORT is not set

### Missing dependencies
- Check `requirements.txt` includes all needed packages
- Railway installs from this file automatically

### API Key issues
- Ensure `GEMINI_API_KEY` is set in Railway variables
- The app reads from environment variables

## Notes

- The frontend is not included in this deployment (backend only)
- For full-stack deployment, you may need separate services
- Data files (`data/scraped/`, `data/embeddings/`) are included in the repo

