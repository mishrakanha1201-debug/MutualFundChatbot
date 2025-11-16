"""
FastAPI Backend for Mutual Fund FAQ Bot
"""
import sys
from pathlib import Path
from typing import Optional
import logging
import os

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    from fastapi import FastAPI, HTTPException, Query
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import JSONResponse, FileResponse
    from fastapi.staticfiles import StaticFiles
except ImportError:
    # Fallback if FastAPI not installed
    print("FastAPI not installed. Please install: pip install fastapi uvicorn")
    sys.exit(1)

from backend.api.models import (
    QueryRequest, QueryResponse, FundsResponse, 
    HealthResponse, ErrorResponse, SourceInfo
)
from backend.rag.rag_pipeline import RAGPipeline

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Mutual Fund FAQ Bot API",
    description="API for querying mutual fund information using RAG",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global RAG pipeline instance
rag_pipeline: Optional[RAGPipeline] = None


# Initialize RAG pipeline (lazy initialization for serverless)
def get_rag_pipeline():
    """Get or initialize RAG pipeline (lazy loading for serverless)"""
    global rag_pipeline
    if rag_pipeline is None:
        try:
            logger.info("Initializing RAG pipeline...")
            rag_pipeline = RAGPipeline()
            logger.info("RAG pipeline initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing RAG pipeline: {e}")
            rag_pipeline = None
    return rag_pipeline

@app.on_event("startup")
async def startup_event():
    """Initialize RAG pipeline on startup (for traditional deployments)"""
    get_rag_pipeline()

# Load frontend files for Vercel serverless deployment
# Try to load from public directory (works in local dev), fall back to reading at runtime
project_root = Path(__file__).parent.parent.parent
public_path = project_root / "public"

def load_frontend_file(filename: str) -> str:
    """Load frontend file from public directory - tries multiple paths for Vercel"""
    # Try multiple possible paths
    possible_paths = [
        public_path / filename,  # Standard path
        project_root / "public" / filename,  # Explicit project root
        Path.cwd() / "public" / filename,  # Current working directory
        Path(__file__).parent.parent.parent / "public" / filename,  # From this file
    ]
    
    for file_path in possible_paths:
        if file_path.exists():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    logger.info(f"Successfully loaded {filename} from {file_path}")
                    return content
            except Exception as e:
                logger.warning(f"Error reading {filename} from {file_path}: {e}")
                continue
    
    logger.error(f"Could not load {filename} from any path. Tried: {[str(p) for p in possible_paths]}")
    return ""

# Load frontend files at module load time
FRONTEND_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mutual Fund Broww - Groww</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Inter', 'Manrope', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background-color: #FFFFFF;
            color: #44475B;
            line-height: 1.5;
        }
        
        #root {
            width: 100%;
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
    </style>
</head>
<body>
    <div id="root"></div>
    <link rel="stylesheet" href="styles.css">
    <script crossorigin src="https://unpkg.com/react@18/umd/react.production.min.js"></script>
    <script crossorigin src="https://unpkg.com/react-dom@18/umd/react-dom.production.min.js"></script>
    <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
    <script type="text/babel" id="app-jsx-script"></script>
    <script>
        // Load app.jsx inline to avoid external file loading issues
        fetch('/app.jsx')
            .then(response => response.text())
            .then(code => {
                const script = document.getElementById('app-jsx-script');
                script.textContent = code;
                // Trigger Babel transformation
                if (window.Babel) {
                    const transformed = Babel.transform(code, { presets: ['react'] }).code;
                    eval(transformed);
                }
            })
            .catch(error => {
                console.error('Error loading app.jsx:', error);
                document.getElementById('root').innerHTML = '<p style="padding: 20px; color: #44475B;">Error loading application. Please refresh the page.</p>';
            });
    </script>
</body>
</html>"""

# Load JSX and CSS files at module startup
FRONTEND_APP_JSX = load_frontend_file("app.jsx")
FRONTEND_STYLES_CSS = load_frontend_file("styles.css")

# Log loading status
if FRONTEND_APP_JSX:
    logger.info(f"Successfully loaded app.jsx ({len(FRONTEND_APP_JSX)} chars)")
else:
    logger.error("Failed to load app.jsx - frontend will not work")
    FRONTEND_APP_JSX = "console.error('app.jsx failed to load');"

if FRONTEND_STYLES_CSS:
    logger.info(f"Successfully loaded styles.css ({len(FRONTEND_STYLES_CSS)} chars)")
else:
    logger.error("Failed to load styles.css - frontend styling will not work")
    FRONTEND_STYLES_CSS = "/* styles.css failed to load */"

from fastapi.responses import HTMLResponse, Response

# Serve frontend files
@app.get("/app.jsx")
async def serve_app_jsx():
    """Serve app.jsx"""
    if not FRONTEND_APP_JSX:
        raise HTTPException(status_code=500, detail="app.jsx not loaded")
    return Response(
        content=FRONTEND_APP_JSX, 
        media_type="application/javascript",
        headers={"Cache-Control": "no-cache"}
    )

@app.get("/styles.css")
async def serve_styles_css():
    """Serve styles.css"""
    if not FRONTEND_STYLES_CSS:
        raise HTTPException(status_code=500, detail="styles.css not loaded")
    return Response(
        content=FRONTEND_STYLES_CSS, 
        media_type="text/css",
        headers={"Cache-Control": "no-cache"}
    )

@app.get("/")
async def serve_frontend():
    """Serve frontend index.html at root"""
    return HTMLResponse(
        content=FRONTEND_HTML,
        headers={"Cache-Control": "no-cache"}
    )


@app.get("/api/", response_model=dict)
async def api_root():
    """API root endpoint"""
    return {
        "message": "Mutual Fund FAQ Bot API",
        "version": "1.0.0",
        "endpoints": {
            "/api/query": "POST - Ask questions about mutual funds",
            "/api/schemes": "GET - List available mutual fund schemes",
            "/api/health": "GET - Health check",
            "/docs": "API documentation"
        }
    }


@app.post("/api/query", response_model=QueryResponse)
async def query_funds(request: QueryRequest):
    """
    Query the mutual fund knowledge base
    
    Args:
        request: Query request with question and optional parameters
        
    Returns:
        QueryResponse with answer and sources
    """
    # Lazy initialize RAG pipeline (for serverless)
    pipeline = get_rag_pipeline()
    if not pipeline:
        raise HTTPException(
            status_code=503,
            detail="RAG pipeline not initialized. Please check server logs."
        )
    
    try:
        logger.info(f"Processing query: {request.question}")
        
        # Query RAG pipeline
        result = pipeline.query(
            question=request.question,
            fund_name=request.fund_name,
            top_k=request.top_k
        )
        
        # Convert sources to response format
        sources = [
            SourceInfo(
                fund_name=src['fund_name'],
                chunk_type=src['chunk_type'],
                similarity=src['similarity']
            )
            for src in result['sources']
        ]
        
        return QueryResponse(
            answer=result['answer'],
            sources=sources,
            confidence=result['confidence'],
            query=request.question,
            citation_link=result.get('citation_link', ''),
            timestamp=result.get('timestamp'),
            rejected=result.get('rejected', False),
            rejection_reason=result.get('rejection_reason')
        )
        
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing query: {str(e)}"
        )


@app.get("/api/schemes", response_model=FundsResponse)
async def list_schemes():
    """
    List all available mutual fund schemes
    
    Returns:
        FundsResponse with list of available funds
    """
    # Lazy initialize RAG pipeline (for serverless)
    pipeline = get_rag_pipeline()
    if not pipeline:
        raise HTTPException(
            status_code=503,
            detail="RAG pipeline not initialized"
        )
    
    try:
        funds = pipeline.list_available_funds()
        
        fund_info = [
            {"name": fund, "available": True}
            for fund in funds
        ]
        
        return FundsResponse(
            funds=fund_info,
            total=len(fund_info)
        )
        
    except Exception as e:
        logger.error(f"Error listing schemes: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error listing schemes: {str(e)}"
        )


@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint
    
    Returns:
        HealthResponse with system status
    """
    # Lazy initialize RAG pipeline (for serverless)
    pipeline = get_rag_pipeline()
    rag_initialized = pipeline is not None
    chunks_loaded = len(pipeline.chunks) if pipeline else 0
    funds_available = len(pipeline.list_available_funds()) if pipeline else 0
    
    status = "healthy" if pipeline else "unhealthy"
    
    return HealthResponse(
        status=status,
        rag_initialized=rag_initialized,
        chunks_loaded=chunks_loaded,
        funds_available=funds_available
    )


@app.get("/api/query/simple")
async def query_simple(question: str = Query(..., description="Question about mutual funds")):
    """
    Simple GET endpoint for queries (for easy testing)
    
    Args:
        question: User's question
        
    Returns:
        Simple JSON response with answer
    """
    # Lazy initialize RAG pipeline (for serverless)
    pipeline = get_rag_pipeline()
    if not pipeline:
        raise HTTPException(
            status_code=503,
            detail="RAG pipeline not initialized"
        )
    
    try:
        result = pipeline.query(question=question)
        return {
            "question": question,
            "answer": result['answer'],
            "confidence": result['confidence']
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": str(exc)}
    )

