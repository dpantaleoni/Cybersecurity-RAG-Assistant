"""Document ingestion service for processing and indexing files."""
import hashlib
from pathlib import Path
from typing import List, Optional, Dict
from llama_index.core import SimpleDirectoryReader
from llama_index.core.schema import Document as LlamaDocument
from llama_index.core.node_parser import SentenceSplitter
from loguru import logger

from src.config import settings
from src.database import db_manager
from src.vector_store import vector_store_manager


class DocumentIngestionService:
    """Service for ingesting and processing documents."""
    
    def __init__(self):
        self.node_parser = SentenceSplitter(
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap
        )
    
    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA256 hash of a file."""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    
    def _check_duplicate(self, file_path: str, file_hash: str) -> bool:
        """Check if document already exists in database."""
        # Check by path
        existing_doc = db_manager.get_document_by_path(file_path)
        if existing_doc:
            logger.info(f"Document already exists by path: {file_path}")
            return True
        
        # Check by hash
        existing_doc = db_manager.get_document_by_hash(file_hash)
        if existing_doc:
            logger.info(f"Document already exists by hash: {file_hash}")
            return True
        
        return False
    
    def ingest_file(self, file_path: Path, category: Optional[str] = None,
                   tags: Optional[List[str]] = None, notes: Optional[str] = None,
                   force: bool = False) -> Dict:
        """
        Ingest a single file into the RAG system.
        
        Args:
            file_path: Path to the file to ingest
            category: Optional category (e.g., "crypto", "web", "forensics")
            tags: Optional list of tags
            notes: Optional notes about the document
            force: Force re-ingestion even if document exists
            
        Returns:
            Dictionary with ingestion results
        """
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        logger.info(f"Ingesting file: {file_path}")
        
        # Calculate file hash
        file_hash = self._calculate_file_hash(file_path)
        file_size = file_path.stat().st_size
        
        # Check for duplicates
        if not force and self._check_duplicate(str(file_path), file_hash):
            return {
                "status": "skipped",
                "reason": "duplicate",
                "file_path": str(file_path)
            }
        
        try:
            # Load document - handle markdown/text files directly
            if file_path.suffix.lower() in ['.md', '.txt']:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                documents = [LlamaDocument(text=content, metadata={"file_path": str(file_path), "file_name": file_path.name})]
            else:
                # Use SimpleDirectoryReader for other file types
                documents = SimpleDirectoryReader(
                    input_files=[str(file_path)]
                ).load_data()
            
            if not documents:
                raise ValueError("No content extracted from file")
            
            # Add metadata to documents
            for doc in documents:
                doc.metadata.update({
                    "file_path": str(file_path),
                    "file_name": file_path.name,
                    "category": category or "general",
                    "tags": ",".join(tags) if tags else "",
                })
            
            # Parse into nodes (chunks)
            nodes = self.node_parser.get_nodes_from_documents(documents)
            chunk_count = len(nodes)
            
            logger.info(f"Created {chunk_count} chunks from {file_path.name}")
            
            # Add to vector store
            vector_store_manager.add_documents(nodes)
            
            # Save metadata to database
            tags_str = ",".join(tags) if tags else None
            db_manager.add_document(
                file_path=str(file_path),
                file_name=file_path.name,
                file_size=file_size,
                file_hash=file_hash,
                chunk_count=chunk_count,
                category=category,
                tags=tags_str,
                notes=notes
            )
            
            logger.info(f"Successfully ingested: {file_path.name}")
            
            return {
                "status": "success",
                "file_path": str(file_path),
                "file_name": file_path.name,
                "chunk_count": chunk_count,
                "file_size": file_size,
                "category": category
            }
            
        except Exception as e:
            logger.error(f"Failed to ingest {file_path}: {e}")
            return {
                "status": "error",
                "file_path": str(file_path),
                "error": str(e)
            }
    
    def ingest_directory(self, directory_path: Path, recursive: bool = True,
                        file_extensions: Optional[List[str]] = None,
                        category: Optional[str] = None) -> Dict:
        """
        Ingest all files from a directory.
        
        Args:
            directory_path: Path to directory
            recursive: Whether to search recursively
            file_extensions: List of file extensions to include (e.g., ['.txt', '.pdf'])
            category: Optional category for all files
            
        Returns:
            Dictionary with ingestion results
        """
        if not directory_path.exists() or not directory_path.is_dir():
            raise ValueError(f"Invalid directory: {directory_path}")
        
        logger.info(f"Ingesting directory: {directory_path}")
        
        # Default extensions for CTF documentation
        if file_extensions is None:
            file_extensions = ['.txt', '.md', '.pdf', '.docx', '.html']
        
        # Find files
        files = []
        if recursive:
            for ext in file_extensions:
                files.extend(directory_path.rglob(f"*{ext}"))
        else:
            for ext in file_extensions:
                files.extend(directory_path.glob(f"*{ext}"))
        
        logger.info(f"Found {len(files)} files to ingest")
        
        results = {
            "total_files": len(files),
            "successful": 0,
            "skipped": 0,
            "failed": 0,
            "details": []
        }
        
        for file_path in files:
            result = self.ingest_file(file_path, category=category)
            results["details"].append(result)
            
            if result["status"] == "success":
                results["successful"] += 1
            elif result["status"] == "skipped":
                results["skipped"] += 1
            else:
                results["failed"] += 1
        
        logger.info(f"Directory ingestion complete: {results['successful']} successful, "
                   f"{results['skipped']} skipped, {results['failed']} failed")
        
        return results
    
    def delete_document(self, doc_id: int) -> bool:
        """
        Delete a document from the system.
        Note: This only removes metadata; FAISS doesn't support deletion easily.
        For full deletion, rebuild the index.
        """
        logger.warning(f"Deleting document {doc_id} (metadata only)")
        return db_manager.delete_document(doc_id)


# Global ingestion service instance
ingestion_service = DocumentIngestionService()

