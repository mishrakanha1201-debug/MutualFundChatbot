"""
FastAPI Backend for Mutual Fund FAQ Bot
"""
import sys
from pathlib import Path
from typing import Optional
import logging

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    from fastapi import FastAPI, HTTPException, Query
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import JSONResponse
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


@app.get("/", response_model=dict)
async def root():
    """Root endpoint"""
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
    if not rag_pipeline:
        raise HTTPException(
            status_code=503,
            detail="RAG pipeline not initialized. Please check server logs."
        )
    
    try:
        logger.info(f"Processing query: {request.question}")
        
        # Query RAG pipeline
        result = rag_pipeline.query(
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
    if not rag_pipeline:
        raise HTTPException(
            status_code=503,
            detail="RAG pipeline not initialized"
        )
    
    try:
        funds = rag_pipeline.list_available_funds()
        
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
    rag_initialized = rag_pipeline is not None
    chunks_loaded = len(rag_pipeline.chunks) if rag_pipeline else 0
    funds_available = len(rag_pipeline.list_available_funds()) if rag_pipeline else 0
    
    status = "healthy" if rag_initialized else "unhealthy"
    
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

