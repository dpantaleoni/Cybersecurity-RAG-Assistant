"""FAISS vector store management and persistence."""
import os
import pickle
from pathlib import Path
from typing import Optional, List
import faiss
from llama_index.core import VectorStoreIndex, StorageContext, Settings, load_index_from_storage
from llama_index.core.schema import Document as LlamaDocument
from llama_index.vector_stores.faiss import FaissVectorStore
from loguru import logger

from src.config import settings
from src.embeddings import embedding_manager


class VectorStoreManager:
    """Manager for FAISS vector store operations."""
    
    def __init__(self):
        self.vector_store = None
        self.index = None
        self.storage_context = None
        self._initialized = False
    
    def initialize(self):
        """Initialize or load existing FAISS index."""
        if self._initialized:
            return
        
        # Set up LlamaIndex global settings
        Settings.embed_model = embedding_manager.get_embedding_model()
        Settings.chunk_size = settings.chunk_size
        Settings.chunk_overlap = settings.chunk_overlap
        
        # Set global LLM to avoid initialization issues
        from llama_index.llms.ollama import Ollama
        Settings.llm = Ollama(model=settings.llm_model, base_url=settings.ollama_base_url, request_timeout=120.0)
        
        # Check if persisted storage exists
        persist_dir = str(settings.faiss_index_path)
        docstore_file = settings.faiss_index_path / "docstore.json"
        
        if docstore_file.exists():
            logger.info("Loading existing FAISS index from storage...")
            try:
                # Load FAISS vector store
                self.vector_store = FaissVectorStore.from_persist_dir(persist_dir)
                
                # Create storage context with the loaded vector store
                self.storage_context = StorageContext.from_defaults(
                    persist_dir=persist_dir,
                    vector_store=self.vector_store
                )
                
                # Build index from stored nodes (they link vectors to text via docstore)
                from llama_index.core import VectorStoreIndex
                # The vectors are already in FAISS, the nodes are in docstore
                # We just need to create the index wrapper without re-embedding
                self.index = VectorStoreIndex(
                    nodes=[],  # Empty - vectors already in FAISS
                    storage_context=self.storage_context,
                    show_progress=False
                )
                
                logger.info(f"FAISS index loaded successfully with {self.vector_store._faiss_index.ntotal} vectors")
            except Exception as e:
                logger.error(f"Failed to load FAISS index: {e}")
                logger.info("Creating new FAISS index...")
                self._create_new_index()
        else:
            logger.info("Creating new FAISS index...")
            self._create_new_index()
        
        self._initialized = True
    
    def _create_new_index(self):
        """Create a new FAISS index."""
        # Create FAISS index with L2 distance
        faiss_index = faiss.IndexFlatL2(settings.embedding_dimension)
        
        # Wrap in LlamaIndex FAISS vector store
        self.vector_store = FaissVectorStore(faiss_index=faiss_index)
        self.storage_context = StorageContext.from_defaults(vector_store=self.vector_store)
        
        # Create empty index
        self.index = VectorStoreIndex(
            [],
            storage_context=self.storage_context
        )
        
        logger.info("New FAISS index created")
    
    def _load_index(self):
        """Load existing FAISS index from disk."""
        from llama_index.core.storage.docstore import SimpleDocumentStore
        
        index_file = settings.faiss_index_path / "index.faiss"
        docstore_file = settings.faiss_index_path / "docstore.pkl"
        
        # Load FAISS index
        faiss_index = faiss.read_index(str(index_file))
        
        # Load docstore
        with open(docstore_file, 'rb') as f:
            docstore_data = pickle.load(f)
        
        # Create vector store with text storage enabled
        self.vector_store = FaissVectorStore(
            faiss_index=faiss_index,
            stores_text=True
        )
        
        # Create docstore and populate it
        docstore = SimpleDocumentStore()
        if docstore_data:
            for doc_id, doc in docstore_data.items():
                docstore.add_documents([doc])
        
        # Create storage context with loaded components
        self.storage_context = StorageContext.from_defaults(
            vector_store=self.vector_store,
            docstore=docstore
        )
        
        # Create index from existing vector store
        self.index = VectorStoreIndex.from_vector_store(
            vector_store=self.vector_store,
            storage_context=self.storage_context
        )
    
    def save_index(self):
        """Persist FAISS index to disk."""
        if not self._initialized or not self.storage_context:
            logger.warning("Cannot save uninitialized index")
            return
        
        try:
            persist_dir = str(settings.faiss_index_path)
            self.storage_context.persist(persist_dir=persist_dir)
            logger.info(f"FAISS index saved to {settings.faiss_index_path}")
        except Exception as e:
            logger.error(f"Failed to save FAISS index: {e}")
            raise
    
    def add_documents(self, documents: List) -> int:
        """Add documents or nodes to the vector store."""
        if not self._initialized:
            self.initialize()
        
        if not documents:
            logger.warning("No documents to add")
            return 0
        
        try:
            # If index doesn't exist yet (first ingestion), create it
            if self.index is None:
                from llama_index.core import VectorStoreIndex
                self.index = VectorStoreIndex(
                    documents,
                    storage_context=self.storage_context
                )
            else:
                # Add nodes to existing index
                for doc in documents:
                    self.index.insert_nodes([doc])
            
            # Save index
            self.save_index()
            
            logger.info(f"Added {len(documents)} documents to vector store")
            return len(documents)
        except Exception as e:
            logger.error(f"Failed to add documents: {e}")
            raise
    
    def get_retriever(self, similarity_top_k: Optional[int] = None):
        """Get a retriever for querying the index."""
        if not self._initialized:
            self.initialize()
        
        top_k = similarity_top_k or settings.top_k
        
        # If index exists, use it
        if self.index is not None:
            return self.index.as_retriever(
                similarity_top_k=top_k,
                vector_store_query_mode="default"
            )
        else:
            # For loaded FAISS stores without index, create retriever from vector store
            from llama_index.core.retrievers import VectorIndexRetriever
            from llama_index.core.indices.vector_store import VectorStoreIndex
            
            # Create a temporary index wrapper for the retriever
            temp_index = VectorStoreIndex.from_vector_store(
                vector_store=self.vector_store,
                storage_context=self.storage_context,
                show_progress=False
            )
            
            return temp_index.as_retriever(similarity_top_k=top_k)
    
    def get_query_engine(self, similarity_top_k: Optional[int] = None, llm=None):
        """Get a query engine for the index."""
        if not self._initialized:
            self.initialize()
        
        top_k = similarity_top_k or settings.top_k
        
        # Get reranker if available
        reranker = embedding_manager.get_reranker()
        
        # If index exists, use it
        if self.index is not None:
            if reranker:
                return self.index.as_query_engine(
                    similarity_top_k=top_k,
                    node_postprocessors=[reranker],
                    llm=llm
                )
            else:
                return self.index.as_query_engine(
                    similarity_top_k=top_k,
                    llm=llm
                )
        else:
            # For loaded FAISS stores without index, build query engine from retriever
            from llama_index.core.query_engine import RetrieverQueryEngine
            retriever = self.get_retriever(similarity_top_k=top_k)
            
            if reranker:
                return RetrieverQueryEngine.from_args(
                    retriever=retriever,
                    node_postprocessors=[reranker],
                    llm=llm
                )
            else:
                return RetrieverQueryEngine.from_args(
                    retriever=retriever,
                    llm=llm
                )
    
    def get_index_stats(self) -> dict:
        """Get statistics about the vector store."""
        if not self._initialized or not self.vector_store:
            return {"initialized": False}
        
        try:
            num_vectors = self.vector_store._faiss_index.ntotal
            return {
                "initialized": True,
                "num_vectors": num_vectors,
                "dimension": settings.embedding_dimension
            }
        except Exception as e:
            logger.error(f"Failed to get index stats: {e}")
            return {"initialized": True, "error": str(e)}
    
    def clear_index(self):
        """Clear all vectors from the index."""
        logger.warning("Clearing FAISS index...")
        self._create_new_index()
        self.save_index()
        logger.info("FAISS index cleared")


# Global vector store manager instance
vector_store_manager = VectorStoreManager()

