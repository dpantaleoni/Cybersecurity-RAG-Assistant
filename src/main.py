"""FastAPI application for NCL CTF RAG system."""
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
import sys

from src.config import settings
from src.schemas import (
    QueryRequest, QueryResponse, RetrieveRequest,
    IngestFileRequest, IngestDirectoryRequest,
    DocumentInfo, SystemStats, HealthResponse
)
from src.rag_pipeline import rag_pipeline
from src.ingestion import ingestion_service
from src.database import db_manager
from src.vector_store import vector_store_manager
from src.embeddings import embedding_manager

# Configure logging
logger.remove()
logger.add(sys.stderr, level="INFO")
logger.add("./storage/app.log", rotation="100 MB", retention="10 days", level="DEBUG")

# Create FastAPI app
app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    description="Local RAG system for NCL CTF documentation using Ollama, LlamaIndex, and FAISS"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    logger.info("Starting NCL RAG API...")
    
    try:
        # Initialize components
        embedding_manager.initialize()
        vector_store_manager.initialize()
        rag_pipeline.initialize()
        
        logger.info("All services initialized successfully")
    except Exception as e:
        logger.error(f"Startup failed: {e}")
        raise


@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint."""
    return {
        "message": "NCL CTF RAG API",
        "version": settings.api_version,
        "docs": "/docs"
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    # Test Ollama connection
    ollama_test = rag_pipeline.test_ollama_connection()
    ollama_connected = ollama_test["status"] == "success"
    
    # Check vector store
    vector_store_stats = vector_store_manager.get_index_stats()
    vector_store_initialized = vector_store_stats.get("initialized", False)
    
    # Check database
    database_connected = True
    try:
        db_manager.get_stats()
    except Exception:
        database_connected = False
    
    overall_status = "healthy" if (ollama_connected and vector_store_initialized and database_connected) else "degraded"
    
    return HealthResponse(
        status=overall_status,
        ollama_connected=ollama_connected,
        vector_store_initialized=vector_store_initialized,
        database_connected=database_connected,
        model=settings.llm_model,
        timestamp=datetime.utcnow()
    )


@app.post("/query", response_model=QueryResponse)
async def query_rag(request: QueryRequest):
    """
    Query the RAG system with a question.
    """
    try:
        result = rag_pipeline.query(
            query_text=request.query,
            top_k=request.top_k,
            return_sources=request.return_sources
        )
        return QueryResponse(**result)
    except Exception as e:
        logger.error(f"Query endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/retrieve", response_model=List[Dict[str, Any]])
async def retrieve_documents(request: RetrieveRequest):
    """
    Retrieve relevant documents without generating an answer.
    """
    try:
        results = rag_pipeline.retrieve_only(
            query_text=request.query,
            top_k=request.top_k
        )
        return results
    except Exception as e:
        logger.error(f"Retrieve endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ingest/file", response_model=Dict[str, Any])
async def ingest_file(request: IngestFileRequest):
    """
    Ingest a single file into the RAG system.
    """
    try:
        file_path = Path(request.file_path)
        result = ingestion_service.ingest_file(
            file_path=file_path,
            category=request.category,
            tags=request.tags,
            notes=request.notes,
            force=request.force
        )
        return result
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Ingest file endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ingest/directory", response_model=Dict[str, Any])
async def ingest_directory(request: IngestDirectoryRequest):
    """
    Ingest all files from a directory.
    """
    try:
        directory_path = Path(request.directory_path)
        result = ingestion_service.ingest_directory(
            directory_path=directory_path,
            recursive=request.recursive,
            file_extensions=request.file_extensions,
            category=request.category
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Ingest directory endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ingest/upload")
async def upload_file(
    file: UploadFile = File(...),
    category: str = None,
    tags: str = None
):
    """
    Upload and ingest a file.
    """
    try:
        # Save uploaded file
        upload_dir = settings.data_dir / "uploads"
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        file_path = upload_dir / file.filename
        
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Ingest the file
        tag_list = tags.split(",") if tags else None
        result = ingestion_service.ingest_file(
            file_path=file_path,
            category=category,
            tags=tag_list
        )
        
        return result
    except Exception as e:
        logger.error(f"Upload endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/documents", response_model=List[DocumentInfo])
async def list_documents(category: str = None, limit: int = 100):
    """
    List all ingested documents.
    """
    try:
        docs = db_manager.list_documents(category=category, limit=limit)
        return [DocumentInfo(
            id=doc.id,
            file_path=doc.file_path,
            file_name=doc.file_name,
            file_size=doc.file_size,
            file_hash=doc.file_hash,
            chunk_count=doc.chunk_count,
            ingested_at=doc.ingested_at,
            updated_at=doc.updated_at,
            category=doc.category,
            tags=doc.tags,
            notes=doc.notes
        ) for doc in docs]
    except Exception as e:
        logger.error(f"List documents error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/documents/{doc_id}")
async def delete_document(doc_id: int):
    """
    Delete a document (metadata only, not from FAISS).
    """
    try:
        success = ingestion_service.delete_document(doc_id)
        if success:
            return {"status": "success", "message": f"Document {doc_id} deleted"}
        else:
            raise HTTPException(status_code=404, detail=f"Document {doc_id} not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete document error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stats", response_model=SystemStats)
async def get_stats():
    """
    Get system statistics.
    """
    try:
        db_stats = db_manager.get_stats()
        vector_stats = vector_store_manager.get_index_stats()
        
        return SystemStats(
            total_documents=db_stats["total_documents"],
            total_chunks=db_stats["total_chunks"],
            total_queries=db_stats["total_queries"],
            vector_store=vector_stats,
            configuration={
                "llm_model": settings.llm_model,
                "embedding_model": settings.embedding_model,
                "chunk_size": settings.chunk_size,
                "top_k": settings.top_k,
                "use_reranker": settings.use_reranker
            }
        )
    except Exception as e:
        logger.error(f"Stats endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/queries/recent")
async def get_recent_queries(limit: int = 50):
    """
    Get recent query logs.
    """
    try:
        queries = db_manager.get_recent_queries(limit=limit)
        return [{
            "id": q.id,
            "query": q.query_text,
            "response": q.response_text,
            "retrieved_chunks": q.retrieved_chunks,
            "response_time": q.response_time,
            "timestamp": q.timestamp,
            "success": bool(q.success),
            "error": q.error_message
        } for q in queries]
    except Exception as e:
        logger.error(f"Recent queries error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/admin/clear-index")
async def clear_index():
    """
    Clear the FAISS index (admin operation).
    """
    try:
        vector_store_manager.clear_index()
        return {"status": "success", "message": "FAISS index cleared"}
    except Exception as e:
        logger.error(f"Clear index error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

