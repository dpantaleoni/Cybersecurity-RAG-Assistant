# NCL CTF RAG System

A **100% local and free** Retrieval-Augmented Generation (RAG) system specialized for National Cyber League (NCL) capture-the-flag competition questions and documentation.

## 🎯 Features

- **Fully Local**: Runs completely offline using Ollama for LLM inference
- **Free & Open Source**: No API costs, no cloud dependencies
- **NCL CTF Optimized**: Specialized for cybersecurity documentation and CTF writeups
- **Fast Semantic Search**: FAISS vector store for efficient similarity search
- **Smart Reranking**: Optional BGE reranker for improved retrieval accuracy
- **Document Management**: SQLite-based metadata tracking
- **REST API**: FastAPI backend with comprehensive endpoints
- **Containerized**: Easy deployment with Docker Compose

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| LLM Runtime | Ollama (qwen2.5:7b-instruct / llama3.1:8b-instruct) |
| RAG Framework | LlamaIndex |
| Embeddings | sentence-transformers/bge-small-en-v1.5 |
| Reranker | BAAI/bge-reranker-base |
| Vector Store | FAISS (CPU-optimized) |
| API | FastAPI + Uvicorn |
| Database | SQLite |
| Container | Docker + Docker Compose |

## 📋 Prerequisites

- Docker & Docker Compose
- At least 8GB RAM (16GB recommended)
- 10GB free disk space

## 🚀 Quick Start

### 1. Clone and Setup

```bash
cd /path/to/ncl-rag-app

# Ensure directory structure exists
mkdir -p data storage/faiss storage/metadata
```

### 2. Start Services

```bash
# Build and start all services
docker-compose up -d

# Check service status
docker-compose ps
```

### 3. Pull Ollama Model

```bash
# Pull the default model
docker exec -it ncl-rag-ollama ollama pull qwen2.5:7b-instruct

# Or use llama3.1
docker exec -it ncl-rag-ollama ollama pull llama3.1:8b-instruct
```

### 4. Verify Installation

```bash
# Check health
curl http://localhost:8000/health

# View API docs
open http://localhost:8000/docs
```

## 📚 Usage

### Adding Documents

#### Upload via API

```bash
# Upload a single file
curl -X POST "http://localhost:8000/ingest/upload" \
  -F "file=@/path/to/document.pdf" \
  -F "category=crypto" \
  -F "tags=RSA,encryption"
```

#### Ingest from Filesystem

```bash
# Ingest a single file
curl -X POST "http://localhost:8000/ingest/file" \
  -H "Content-Type: application/json" \
  -d '{
    "file_path": "/app/data/ncl_crypto_guide.pdf",
    "category": "crypto",
    "tags": ["encryption", "CTF"]
  }'

# Ingest entire directory
curl -X POST "http://localhost:8000/ingest/directory" \
  -H "Content-Type: application/json" \
  -d '{
    "directory_path": "/app/data/ncl_docs",
    "recursive": true,
    "category": "general"
  }'
```

### Querying the System

```bash
# Ask a question
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is a SQL injection attack and how do I prevent it?",
    "top_k": 5,
    "return_sources": true
  }'
```

#### Python Example

```python
import requests

response = requests.post(
    "http://localhost:8000/query",
    json={
        "query": "Explain the difference between symmetric and asymmetric encryption",
        "top_k": 3,
        "return_sources": True
    }
)

result = response.json()
print("Answer:", result["answer"])
print("Sources:", len(result["sources"]))
```

### Document Retrieval (No LLM)

```bash
# Just retrieve relevant chunks without generating an answer
curl -X POST "http://localhost:8000/retrieve" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "buffer overflow vulnerability",
    "top_k": 5
  }'
```

### Management

```bash
# List all documents
curl http://localhost:8000/documents

# Get system statistics
curl http://localhost:8000/stats

# View recent queries
curl http://localhost:8000/queries/recent?limit=10

# Delete a document (metadata only)
curl -X DELETE http://localhost:8000/documents/1

# Clear entire index (admin)
curl -X POST http://localhost:8000/admin/clear-index
```

## 📁 Directory Structure

```
ncl-rag-app/
├── data/                      # Place your documents here
│   ├── uploads/              # API uploads go here
│   └── ncl_docs/             # Your NCL documentation
├── storage/
│   ├── faiss/                # FAISS vector index
│   ├── metadata/             # SQLite database
│   ├── models/               # Downloaded embedding models
│   └── app.log               # Application logs
├── src/
│   ├── config.py             # Configuration management
│   ├── database.py           # SQLite models
│   ├── embeddings.py         # Embedding models
│   ├── vector_store.py       # FAISS management
│   ├── ingestion.py          # Document processing
│   ├── rag_pipeline.py       # RAG orchestration
│   ├── schemas.py            # API models
│   └── main.py               # FastAPI app
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── README.md
```

## ⚙️ Configuration

Edit `.env` to customize settings:

```bash
# LLM Configuration
LLM_MODEL=qwen2.5:7b-instruct          # or llama3.1:8b-instruct
OLLAMA_BASE_URL=http://ollama:11434

# Embedding Configuration
EMBEDDING_MODEL=sentence-transformers/bge-small-en-v1.5
EMBEDDING_DIMENSION=384

# RAG Parameters
CHUNK_SIZE=512                          # Chunk size for splitting
CHUNK_OVERLAP=50                        # Overlap between chunks
TOP_K=5                                 # Documents to retrieve
RERANK_TOP_N=3                         # Documents after reranking
USE_RERANKER=true                      # Enable/disable reranking
SIMILARITY_THRESHOLD=0.7               # Minimum similarity score

# Storage Paths
FAISS_INDEX_PATH=/app/storage/faiss
METADATA_DB_PATH=/app/storage/metadata/documents.db
DATA_DIR=/app/data
```

### Switching LLM Models

```bash
# Pull a different model
docker exec -it ncl-rag-ollama ollama pull llama3.1:8b-instruct

# Update .env
LLM_MODEL=llama3.1:8b-instruct

# Restart API service
docker-compose restart rag-api
```

## 🔧 Development

### Local Development (without Docker)

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export OLLAMA_BASE_URL=http://localhost:11434
# ... other vars from .env

# Run locally
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

### Logs

```bash
# View API logs
docker-compose logs -f rag-api

# View Ollama logs
docker-compose logs -f ollama

# View application log file
tail -f storage/app.log
```

## 🎓 NCL CTF Categories

Organize your documents by NCL categories:

- **crypto**: Cryptography challenges
- **web**: Web application security
- **forensics**: Digital forensics
- **network**: Network analysis
- **osint**: Open-source intelligence
- **password**: Password cracking
- **scanning**: Network scanning
- **enumeration**: Service enumeration

Example:
```bash
curl -X POST "http://localhost:8000/ingest/directory" \
  -H "Content-Type: application/json" \
  -d '{
    "directory_path": "/app/data/crypto_docs",
    "category": "crypto",
    "recursive": true
  }'
```

## 📊 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API information |
| `/health` | GET | Health check |
| `/docs` | GET | Swagger UI |
| `/query` | POST | Ask a question |
| `/retrieve` | POST | Retrieve documents only |
| `/ingest/file` | POST | Ingest single file |
| `/ingest/directory` | POST | Ingest directory |
| `/ingest/upload` | POST | Upload and ingest |
| `/documents` | GET | List documents |
| `/documents/{id}` | DELETE | Delete document |
| `/stats` | GET | System statistics |
| `/queries/recent` | GET | Recent queries |
| `/admin/clear-index` | POST | Clear FAISS index |

## 🐛 Troubleshooting

### Ollama Connection Issues

```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Restart Ollama
docker-compose restart ollama
```

### Out of Memory

```bash
# Reduce chunk size and top_k in .env
CHUNK_SIZE=256
TOP_K=3

# Use smaller model
LLM_MODEL=qwen2.5:3b-instruct  # Smaller variant
```

### Slow Queries

```bash
# Disable reranker
USE_RERANKER=false

# Reduce top_k
TOP_K=3
```

### FAISS Index Corruption

```bash
# Clear and rebuild
curl -X POST http://localhost:8000/admin/clear-index

# Re-ingest documents
curl -X POST "http://localhost:8000/ingest/directory" \
  -H "Content-Type: application/json" \
  -d '{"directory_path": "/app/data"}'
```

## 🔒 Security Notes

- This system runs locally and doesn't send data externally
- No API keys or cloud services required
- All data stored on local filesystem
- Suitable for sensitive CTF documentation

## 📝 License

MIT License - Feel free to modify and use for your NCL preparation!

## 🙏 Acknowledgments

- [LlamaIndex](https://www.llamaindex.ai/) - RAG framework
- [Ollama](https://ollama.ai/) - Local LLM runtime
- [FAISS](https://github.com/facebookresearch/faiss) - Vector search
- [HuggingFace](https://huggingface.co/) - Embedding models
- [National Cyber League](https://nationalcyberleague.org/) - CTF competition

## 🚀 Next Steps

1. Add your NCL documentation to `data/`
2. Ingest documents via API
3. Start asking questions!
4. Review query logs to improve your knowledge base

Good luck with your CTF preparation! 🎯

