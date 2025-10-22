#!/usr/bin/env python3
"""
Simple Python client to test the NCL RAG API
"""

import requests
import json
from typing import Dict, List

class NCLRagClient:
    """Client for interacting with NCL RAG API."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
    
    def health_check(self) -> Dict:
        """Check API health."""
        response = requests.get(f"{self.base_url}/health")
        return response.json()
    
    def query(self, question: str, top_k: int = 5, return_sources: bool = True) -> Dict:
        """Ask a question to the RAG system."""
        response = requests.post(
            f"{self.base_url}/query",
            json={
                "query": question,
                "top_k": top_k,
                "return_sources": return_sources
            }
        )
        return response.json()
    
    def retrieve(self, query: str, top_k: int = 5) -> List[Dict]:
        """Retrieve relevant documents without generating answer."""
        response = requests.post(
            f"{self.base_url}/retrieve",
            json={
                "query": query,
                "top_k": top_k
            }
        )
        return response.json()
    
    def ingest_file(self, file_path: str, category: str = None, 
                   tags: List[str] = None, force: bool = False) -> Dict:
        """Ingest a single file."""
        response = requests.post(
            f"{self.base_url}/ingest/file",
            json={
                "file_path": file_path,
                "category": category,
                "tags": tags,
                "force": force
            }
        )
        return response.json()
    
    def ingest_directory(self, directory_path: str, recursive: bool = True,
                        category: str = None) -> Dict:
        """Ingest all files from a directory."""
        response = requests.post(
            f"{self.base_url}/ingest/directory",
            json={
                "directory_path": directory_path,
                "recursive": recursive,
                "category": category
            }
        )
        return response.json()
    
    def list_documents(self, category: str = None, limit: int = 100) -> List[Dict]:
        """List all ingested documents."""
        params = {"limit": limit}
        if category:
            params["category"] = category
        
        response = requests.get(f"{self.base_url}/documents", params=params)
        return response.json()
    
    def get_stats(self) -> Dict:
        """Get system statistics."""
        response = requests.get(f"{self.base_url}/stats")
        return response.json()
    
    def get_recent_queries(self, limit: int = 10) -> List[Dict]:
        """Get recent query history."""
        response = requests.get(
            f"{self.base_url}/queries/recent",
            params={"limit": limit}
        )
        return response.json()


def main():
    """Example usage."""
    client = NCLRagClient()
    
    print("=" * 60)
    print("NCL RAG Client Test")
    print("=" * 60)
    print()
    
    # Health check
    print("1. Health Check")
    print("-" * 60)
    health = client.health_check()
    print(f"Status: {health['status']}")
    print(f"Ollama Connected: {health['ollama_connected']}")
    print(f"Model: {health['model']}")
    print()
    
    # System stats
    print("2. System Statistics")
    print("-" * 60)
    stats = client.get_stats()
    print(f"Total Documents: {stats['total_documents']}")
    print(f"Total Chunks: {stats['total_chunks']}")
    print(f"Total Queries: {stats['total_queries']}")
    print()
    
    # Test queries
    test_questions = [
        "What is SQL injection and how do I test for it?",
        "How can I crack MD5 hashes?",
        "What tools are used for network traffic analysis?",
        "Explain steganography in CTF challenges",
        "What is a Caesar cipher?"
    ]
    
    print("3. Test Queries")
    print("-" * 60)
    
    for i, question in enumerate(test_questions, 1):
        print(f"\nQuestion {i}: {question}")
        print("-" * 60)
        
        try:
            result = client.query(question, top_k=3, return_sources=False)
            
            if result['status'] == 'success':
                print(f"Answer: {result['answer'][:300]}...")
                print(f"Retrieved Chunks: {result['retrieved_chunks']}")
                print(f"Response Time: {result['response_time']:.2f}s")
            else:
                print(f"Error: {result.get('error', 'Unknown error')}")
        except Exception as e:
            print(f"Request failed: {e}")
        
        print()
    
    # List documents
    print("4. Document List")
    print("-" * 60)
    docs = client.list_documents(limit=10)
    print(f"Found {len(docs)} documents:")
    for doc in docs:
        print(f"  - {doc['file_name']} ({doc['chunk_count']} chunks, "
              f"category: {doc.get('category', 'N/A')})")
    print()
    
    print("=" * 60)
    print("Test Complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()

