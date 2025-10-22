"""Configuration management for NCL RAG application."""
import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Ollama Configuration
    ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    llm_model: str = os.getenv("LLM_MODEL", "qwen2.5:7b-instruct")
    
    # Embedding Configuration
    embedding_model: str = os.getenv("EMBEDDING_MODEL", "sentence-transformers/bge-small-en-v1.5")
    embedding_dimension: int = int(os.getenv("EMBEDDING_DIMENSION", "384"))
    
    # Reranker Configuration
    reranker_model: str = os.getenv("RERANKER_MODEL", "BAAI/bge-reranker-base")
    use_reranker: bool = os.getenv("USE_RERANKER", "true").lower() == "true"
    
    # Storage Paths
    faiss_index_path: Path = Path(os.getenv("FAISS_INDEX_PATH", "./storage/faiss"))
    metadata_db_path: Path = Path(os.getenv("METADATA_DB_PATH", "./storage/metadata/documents.db"))
    data_dir: Path = Path(os.getenv("DATA_DIR", "./data"))
    
    # RAG Configuration
    chunk_size: int = int(os.getenv("CHUNK_SIZE", "512"))
    chunk_overlap: int = int(os.getenv("CHUNK_OVERLAP", "50"))
    top_k: int = int(os.getenv("TOP_K", "5"))
    rerank_top_n: int = int(os.getenv("RERANK_TOP_N", "3"))
    similarity_threshold: float = float(os.getenv("SIMILARITY_THRESHOLD", "0.7"))
    
    # API Configuration
    api_title: str = os.getenv("API_TITLE", "NCL CTF RAG API")
    api_version: str = os.getenv("API_VERSION", "1.0.0")
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    class Config:
        env_file = ".env"
        case_sensitive = False
    
    def ensure_directories(self):
        """Create necessary directories if they don't exist."""
        self.faiss_index_path.mkdir(parents=True, exist_ok=True)
        self.metadata_db_path.parent.mkdir(parents=True, exist_ok=True)
        self.data_dir.mkdir(parents=True, exist_ok=True)


# Global settings instance
settings = Settings()
settings.ensure_directories()

