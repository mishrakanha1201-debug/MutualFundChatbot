"""
Pydantic models for API request/response validation
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    """Request model for query endpoint"""
    question: str = Field(..., description="User's question about mutual funds", min_length=1)
    fund_name: Optional[str] = Field(None, description="Optional specific fund name to search in")
    top_k: int = Field(3, description="Number of relevant chunks to retrieve", ge=1, le=10)


class SourceInfo(BaseModel):
    """Source information for answer"""
    fund_name: str
    chunk_type: str
    similarity: float


class QueryResponse(BaseModel):
    """Response model for query endpoint"""
    answer: str = Field(..., description="Generated answer to the question")
    sources: List[SourceInfo] = Field(..., description="Sources used to generate the answer")
    confidence: float = Field(..., description="Confidence score (0-1)")
    query: str = Field(..., description="Original query")
    citation_link: str = Field(..., description="Citation link for the answer")
    timestamp: Optional[str] = Field(None, description="Last updated timestamp")
    rejected: Optional[bool] = Field(False, description="Whether query was rejected")
    rejection_reason: Optional[str] = Field(None, description="Reason for rejection if applicable")


class FundInfo(BaseModel):
    """Fund information"""
    name: str
    available: bool = True


class FundsResponse(BaseModel):
    """Response model for funds list endpoint"""
    funds: List[FundInfo]
    total: int


class HealthResponse(BaseModel):
    """Response model for health check"""
    status: str
    version: str = "1.0.0"
    rag_initialized: bool
    chunks_loaded: int
    funds_available: int


class ErrorResponse(BaseModel):
    """Error response model"""
    error: str
    detail: Optional[str] = None

