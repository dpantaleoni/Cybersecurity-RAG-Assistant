"""RAG query pipeline using LlamaIndex and Ollama."""
import time
from typing import Optional, Dict, Any
from llama_index.llms.ollama import Ollama
from loguru import logger

from src.config import settings
from src.vector_store import vector_store_manager
from src.database import db_manager


class RAGPipeline:
    """RAG pipeline for processing queries."""
    
    def __init__(self):
        self.llm = None
        self._initialized = False
    
    def initialize(self):
        """Initialize the RAG pipeline with LLM."""
        if self._initialized:
            return
        
        try:
            logger.info(f"Initializing RAG pipeline with model: {settings.llm_model}")
            
            # Initialize Ollama LLM
            self.llm = Ollama(
                model=settings.llm_model,
                base_url=settings.ollama_base_url,
                request_timeout=120.0
            )
            
            # Test LLM connection
            try:
                test_response = self.llm.complete("test")
                logger.info("LLM connection successful")
            except Exception as e:
                logger.warning(f"LLM test failed: {e}")
            
            self._initialized = True
            logger.info("RAG pipeline initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize RAG pipeline: {e}")
            raise
    
    def query(
        self,
        query_text: str,
        top_k: Optional[int] = None,
        return_sources: bool = False
    ) -> Dict[str, Any]:
        """
        Process a query through the RAG pipeline.
        
        Args:
            query_text: The query string
            top_k: Number of chunks to retrieve
            return_sources: Whether to return source documents
            
        Returns:
            Dictionary with answer and metadata
        """
        if not self._initialized:
            self.initialize()
        
        start_time = time.time()
        
        try:
            logger.info(f"Processing query: {query_text[:100]}...")
            
            # Get query engine with our LLM
            query_engine = vector_store_manager.get_query_engine(similarity_top_k=top_k, llm=self.llm)
            
            # Execute query
            response = query_engine.query(query_text)
            
            # Extract response text
            answer = str(response)
            
            # Get source nodes if requested
            sources = []
            retrieved_chunks = 0
            
            if return_sources and hasattr(response, 'source_nodes'):
                retrieved_chunks = len(response.source_nodes)
                for node in response.source_nodes:
                    source_info = {
                        "text": node.node.get_content()[:500] + "..." if len(node.node.get_content()) > 500 else node.node.get_content(),
                        "score": float(node.score) if hasattr(node, 'score') else None,
                        "metadata": node.node.metadata
                    }
                    sources.append(source_info)
            
            response_time = time.time() - start_time
            
            # Log query
            db_manager.log_query(
                query_text=query_text,
                response_text=answer,
                retrieved_chunks=retrieved_chunks,
                response_time=response_time,
                success=True
            )
            
            result = {
                "status": "success",
                "answer": answer,
                "query": query_text,
                "retrieved_chunks": retrieved_chunks,
                "response_time": response_time,
                "model": settings.llm_model,
            }
            
            if return_sources:
                result["sources"] = sources
            
            logger.info(f"Query completed in {response_time:.2f}s with {retrieved_chunks} chunks")
            
            return result
            
        except Exception as e:
            response_time = time.time() - start_time
            error_msg = str(e)
            
            logger.error(f"Query failed: {error_msg}")
            
            # Log failed query
            db_manager.log_query(
                query_text=query_text,
                retrieved_chunks=0,
                response_time=response_time,
                success=False,
                error_message=error_msg
            )
            
            return {
                "status": "error",
                "answer": None,
                "query": query_text,
                "retrieved_chunks": 0,
                "response_time": response_time,
                "model": None,
                "sources": None if return_sources else None,
                "error": error_msg
            }
    
    def stream_query(
        self,
        query_text: str,
        top_k: Optional[int] = None
    ):
        """
        Stream a query response (for future use).
        
        Args:
            query_text: The query string
            top_k: Number of chunks to retrieve
            
        Yields:
            Response chunks as they're generated
        """
        if not self._initialized:
            self.initialize()
        
        query_engine = vector_store_manager.get_query_engine(similarity_top_k=top_k, llm=self.llm)
        
        streaming_response = query_engine.query(query_text)
        
        for text in streaming_response.response_gen:
            yield text
    
    def test_ollama_connection(self) -> Dict[str, Any]:
        """Test if Ollama is accessible."""
        try:
            if not self._initialized:
                self.initialize()
            self.llm.complete("test")
            return {"status": "success", "model": settings.llm_model}
        except Exception as e:
            logger.error(f"Ollama connection test failed: {e}")
            return {"status": "error", "error": str(e)}
    
    def get_stats(self) -> Dict[str, Any]:
        """Get pipeline statistics."""
        return {
            "initialized": self._initialized,
            "llm_model": settings.llm_model if self._initialized else None,
            "ollama_url": settings.ollama_base_url if self._initialized else None
        }


# Global RAG pipeline instance
rag_pipeline = RAGPipeline()

