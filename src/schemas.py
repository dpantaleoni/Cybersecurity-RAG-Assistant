"""Pydantic schemas for API request/response models."""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    """Request model for querying the RAG system."""
    query: str = Field(..., min_length=1, description="The question to ask")
    top_k: Optional[int] = Field(None, ge=1, le=20, description="Number of documents to retrieve")
    return_sources: bool = Field(True, description="Whether to return source documents")


class QueryResponse(BaseModel):
    """Response model for query results."""
    status: str
    answer: Optional[str] = None
    query: str
    retrieved_chunks: int = 0
    response_time: float
    model: Optional[str] = None
    sources: Optional[List[Dict[str, Any]]] = None
    error: Optional[str] = None


class RetrieveRequest(BaseModel):
    """Request model for document retrieval."""
    query: str = Field(..., min_length=1, description="The query text")
    top_k: Optional[int] = Field(None, ge=1, le=20, description="Number of documents to retrieve")


class IngestFileRequest(BaseModel):
    """Request model for ingesting a single file."""
    file_path: str = Field(..., description="Path to the file to ingest")
    category: Optional[str] = Field(None, description="Category (e.g., crypto, web, forensics)")
    tags: Optional[List[str]] = Field(None, description="List of tags")
    notes: Optional[str] = Field(None, description="Optional notes")
    force: bool = Field(False, description="Force re-ingestion even if exists")


class IngestDirectoryRequest(BaseModel):
    """Request model for ingesting a directory."""
    directory_path: str = Field(..., description="Path to directory to ingest")
    recursive: bool = Field(True, description="Search recursively")
    file_extensions: Optional[List[str]] = Field(None, description="File extensions to include")
    category: Optional[str] = Field(None, description="Category for all files")


class DocumentInfo(BaseModel):
    """Document metadata information."""
    id: int
    file_path: str
    file_name: str
    file_size: int
    file_hash: str
    chunk_count: int
    ingested_at: datetime
    updated_at: datetime
    category: Optional[str] = None
    tags: Optional[str] = None
    notes: Optional[str] = None


class SystemStats(BaseModel):
    """System statistics."""
    total_documents: int
    total_chunks: int
    total_queries: int
    vector_store: Dict[str, Any]
    configuration: Dict[str, Any]


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    ollama_connected: bool
    vector_store_initialized: bool
    database_connected: bool
    model: str
    timestamp: datetime

