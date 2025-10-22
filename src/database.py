"""Database models and management for document metadata."""
from datetime import datetime
from pathlib import Path
from typing import List, Optional
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float, Text, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager

from src.config import settings

Base = declarative_base()


class DocumentMetadata(Base):
    """SQLite model for tracking ingested documents."""
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    file_path = Column(String(512), unique=True, nullable=False, index=True)
    file_name = Column(String(256), nullable=False)
    file_size = Column(Integer)  # bytes
    file_hash = Column(String(64), index=True)  # SHA256 hash
    chunk_count = Column(Integer, default=0)
    ingested_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    category = Column(String(128))  # e.g., "crypto", "web", "forensics", "network"
    tags = Column(Text)  # JSON string of tags
    notes = Column(Text)
    
    def __repr__(self):
        return f"<Document(id={self.id}, name={self.file_name}, chunks={self.chunk_count})>"


class QueryLog(Base):
    """SQLite model for logging queries and results."""
    __tablename__ = "query_logs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    query_text = Column(Text, nullable=False)
    response_text = Column(Text)
    retrieved_chunks = Column(Integer, default=0)
    response_time = Column(Float)  # seconds
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    success = Column(Integer, default=1)  # 1 = success, 0 = failure
    error_message = Column(Text)
    
    def __repr__(self):
        return f"<Query(id={self.id}, time={self.timestamp})>"


class DatabaseManager:
    """Manager for SQLite database operations."""
    
    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or settings.metadata_db_path
        self.engine = create_engine(f"sqlite:///{self.db_path}", echo=settings.debug)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self._create_tables()
    
    def _create_tables(self):
        """Create all tables if they don't exist."""
        Base.metadata.create_all(bind=self.engine)
    
    @contextmanager
    def get_session(self) -> Session:
        """Context manager for database sessions."""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
    
    def add_document(self, file_path: str, file_name: str, file_size: int,
                     file_hash: str, chunk_count: int, category: Optional[str] = None,
                     tags: Optional[str] = None, notes: Optional[str] = None) -> DocumentMetadata:
        """Add a new document to the database."""
        with self.get_session() as session:
            doc = DocumentMetadata(
                file_path=file_path,
                file_name=file_name,
                file_size=file_size,
                file_hash=file_hash,
                chunk_count=chunk_count,
                category=category,
                tags=tags,
                notes=notes
            )
            session.add(doc)
            session.commit()
            session.refresh(doc)
            return doc
    
    def get_document_by_path(self, file_path: str) -> Optional[DocumentMetadata]:
        """Retrieve a document by file path."""
        with self.get_session() as session:
            return session.query(DocumentMetadata).filter_by(file_path=file_path).first()
    
    def get_document_by_hash(self, file_hash: str) -> Optional[DocumentMetadata]:
        """Retrieve a document by hash."""
        with self.get_session() as session:
            return session.query(DocumentMetadata).filter_by(file_hash=file_hash).first()
    
    def list_documents(self, category: Optional[str] = None, limit: int = 100) -> List[DocumentMetadata]:
        """List all documents, optionally filtered by category."""
        with self.get_session() as session:
            query = session.query(DocumentMetadata)
            if category:
                query = query.filter_by(category=category)
            return query.order_by(DocumentMetadata.ingested_at.desc()).limit(limit).all()
    
    def delete_document(self, doc_id: int) -> bool:
        """Delete a document by ID."""
        with self.get_session() as session:
            doc = session.query(DocumentMetadata).filter_by(id=doc_id).first()
            if doc:
                session.delete(doc)
                session.commit()
                return True
            return False
    
    def log_query(self, query_text: str, response_text: Optional[str] = None,
                  retrieved_chunks: int = 0, response_time: float = 0.0,
                  success: bool = True, error_message: Optional[str] = None) -> QueryLog:
        """Log a query and its results."""
        with self.get_session() as session:
            log = QueryLog(
                query_text=query_text,
                response_text=response_text,
                retrieved_chunks=retrieved_chunks,
                response_time=response_time,
                success=1 if success else 0,
                error_message=error_message
            )
            session.add(log)
            session.commit()
            session.refresh(log)
            return log
    
    def get_recent_queries(self, limit: int = 50) -> List[QueryLog]:
        """Get recent query logs."""
        with self.get_session() as session:
            return session.query(QueryLog).order_by(QueryLog.timestamp.desc()).limit(limit).all()
    
    def get_stats(self) -> dict:
        """Get database statistics."""
        with self.get_session() as session:
            total_docs = session.query(DocumentMetadata).count()
            total_chunks = session.query(DocumentMetadata).with_entities(
                func.sum(DocumentMetadata.chunk_count)
            ).scalar() or 0
            total_queries = session.query(QueryLog).count()
            
            return {
                "total_documents": total_docs,
                "total_chunks": total_chunks,
                "total_queries": total_queries
            }


# Global database manager instance
db_manager = DatabaseManager()

