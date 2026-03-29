"""Pydantic schemas for API request/response models."""

from pydantic import BaseModel, Field
from typing import List, Optional


class ChatRequest(BaseModel):
    """Request body for /chat endpoint."""
    query: str = Field(..., description="User's question or message")
    session_id: str = Field(default="default", description="Session ID for conversation memory")
    model: Optional[str] = Field(default=None, description="LLM model override (gemini, llama, gemma)")


class SourceInfo(BaseModel):
    """Source citation metadata."""
    chunk_index: Optional[int] = None
    source: Optional[str] = None
    page: Optional[int] = None
    content_preview: Optional[str] = None
    title: Optional[str] = None
    url: Optional[str] = None
    type: Optional[str] = None
    tools_used: Optional[List[str]] = None


class ChatResponse(BaseModel):
    """Structured response from /chat endpoint."""
    answer: str
    route: str = Field(description="Route taken: rag, web, or eligibility")
    sources: List[dict] = Field(default_factory=list)
    session_id: str


class IngestRequest(BaseModel):
    """Request body for /ingest endpoint (URL-based ingestion)."""
    url: str = Field(..., description="URL to ingest")


class IngestResponse(BaseModel):
    """Response from /ingest endpoint."""
    status: str
    source: Optional[str] = None
    chunks_ingested: Optional[int] = None
    message: Optional[str] = None


class EligibilityRequest(BaseModel):
    """Request for /eligibility endpoint."""
    query: str = Field(..., description="Eligibility question")
    scheme_name: Optional[str] = None
    age: Optional[int] = None
    income: Optional[float] = None
    state: Optional[str] = None
    category: Optional[str] = None
    model: Optional[str] = Field(default=None, description="LLM model override")


class EligibilityResponse(BaseModel):
    """Response from /eligibility endpoint."""
    answer: str
    tools_used: List[str] = Field(default_factory=list)
    sources: List[dict] = Field(default_factory=list)


class SchemeInfo(BaseModel):
    """Basic scheme information for /schemes listing."""
    name: str
    description: str
    category: Optional[str] = None
    ministry: Optional[str] = None
