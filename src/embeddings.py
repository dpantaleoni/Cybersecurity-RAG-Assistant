"""Embedding and reranking setup for the RAG pipeline."""
from typing import List, Optional
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core.postprocessor import SentenceTransformerRerank
from loguru import logger

from src.config import settings


class EmbeddingManager:
    """Manager for embeddings and reranking models."""
    
    def __init__(self):
        self.embedding_model = None
        self.reranker = None
        self._initialized = False
    
    def initialize(self):
        """Initialize embedding and reranking models."""
        if self._initialized:
            return
        
        logger.info(f"Loading embedding model: {settings.embedding_model}")
        try:
            self.embedding_model = HuggingFaceEmbedding(
                model_name=settings.embedding_model,
                cache_folder="./storage/models"
            )
            logger.info("Embedding model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            raise
        
        if settings.use_reranker:
            logger.info(f"Loading reranker model: {settings.reranker_model}")
            try:
                self.reranker = SentenceTransformerRerank(
                    model=settings.reranker_model,
                    top_n=settings.rerank_top_n
                )
                logger.info("Reranker model loaded successfully")
            except Exception as e:
                logger.error(f"Failed to load reranker model: {e}")
                logger.warning("Continuing without reranker")
                self.reranker = None
        
        self._initialized = True
    
    def get_embedding_model(self) -> HuggingFaceEmbedding:
        """Get the embedding model instance."""
        if not self._initialized:
            self.initialize()
        return self.embedding_model
    
    def get_reranker(self) -> Optional[SentenceTransformerRerank]:
        """Get the reranker instance if enabled."""
        if not self._initialized:
            self.initialize()
        return self.reranker


# Global embedding manager instance
embedding_manager = EmbeddingManager()

