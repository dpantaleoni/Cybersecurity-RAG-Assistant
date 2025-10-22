# NCL RAG Quick Start Guide

Get your local RAG system running in 5 minutes!

## Prerequisites

- Docker Desktop installed and running
- 8GB+ RAM available
- 10GB+ free disk space

## Step 1: Navigate to Project

```bash
cd /Users/dominikpantaleoni/Documents/programming/ncl-rag-app
```

## Step 2: Automated Setup

Run the automated setup script:

```bash
./setup_and_test.sh
```

This script will:
1. ✅ Build and start Docker containers
2. ✅ Pull the LLM model (qwen2.5:7b-instruct)
3. ✅ Ingest sample NCL documentation
4. ✅ Run test queries
5. ✅ Display system statistics

**Note:** The first run takes 10-15 minutes to download the LLM model.

## Step 3: Verify Installation

### Check Health

```bash
curl http://localhost:8000/health | python3 -m json.tool
```

You should see all services as healthy.

### Try a Query

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What is SQL injection?", "top_k": 3}' \
  | python3 -m json.tool
```

### View API Documentation

Open your browser to: http://localhost:8000/docs

## Step 4: Add Your Own Documents

### Method 1: Copy Files to Data Directory

```bash
# Copy your NCL notes/guides
cp ~/path/to/your/ctf-notes.md data/

# Ingest via API
curl -X POST "http://localhost:8000/ingest/directory" \
  -H "Content-Type: application/json" \
  -d '{"directory_path": "/app/data", "recursive": true}'
```

### Method 2: Upload via API

```bash
curl -X POST "http://localhost:8000/ingest/upload" \
  -F "file=@/path/to/document.pdf" \
  -F "category=crypto"
```

## Common Commands

### Query the System

```bash
# Basic query
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "How do I crack MD5 hashes?"}' \
  | python3 -m json.tool
```

### List Documents

```bash
curl http://localhost:8000/documents | python3 -m json.tool
```

### View Statistics

```bash
curl http://localhost:8000/stats | python3 -m json.tool
```

### View Logs

```bash
# API logs
docker-compose logs -f rag-api

# Ollama logs
docker-compose logs -f ollama
```

## Testing Queries

Run the test script to see various queries in action:

```bash
./test_queries.sh
```

## Switching Models

### Try Llama 3.1

```bash
# Pull model
docker exec ncl-rag-ollama ollama pull llama3.1:8b-instruct

# Update environment variable
# Edit .env and change:
# LLM_MODEL=llama3.1:8b-instruct

# Restart API
docker-compose restart rag-api
```

### Available Models

- `qwen2.5:7b-instruct` (default, good for general Q&A)
- `llama3.1:8b-instruct` (Meta's latest)
- `llama3.2:3b-instruct` (smaller, faster)
- `mistral:7b-instruct` (Mistral AI)
- `codellama:7b-instruct` (optimized for code)

## Management

### Stop Services

```bash
docker-compose down
```

### Restart Services

```bash
docker-compose restart
```

### Clear Index and Start Fresh

```bash
# Clear FAISS index
curl -X POST http://localhost:8000/admin/clear-index

# Re-ingest documents
curl -X POST "http://localhost:8000/ingest/directory" \
  -H "Content-Type: application/json" \
  -d '{"directory_path": "/app/docs", "recursive": true}'
```

### View Container Status

```bash
docker-compose ps
```

## Troubleshooting

### Services Won't Start

```bash
# Check Docker is running
docker info

# View error logs
docker-compose logs
```

### Ollama Connection Failed

```bash
# Check Ollama is running
curl http://localhost:11434/api/tags

# Restart Ollama
docker-compose restart ollama
```

### Out of Memory

Edit `.env` and reduce settings:

```bash
CHUNK_SIZE=256
TOP_K=3
USE_RERANKER=false
```

Then restart:

```bash
docker-compose restart rag-api
```

### Slow Queries

1. Disable reranker: `USE_RERANKER=false`
2. Reduce `TOP_K=3`
3. Use smaller model: `llama3.2:3b-instruct`

## Python Client Example

```python
import requests

def ask_rag(question):
    response = requests.post(
        "http://localhost:8000/query",
        json={"query": question, "top_k": 3}
    )
    return response.json()

# Ask a question
result = ask_rag("What tools are used for password cracking?")
print(result["answer"])
```

## Next Steps

1. ✅ Add your NCL notes and CTF writeups to `data/`
2. ✅ Ingest them via API or upload endpoint
3. ✅ Start asking questions!
4. ✅ Organize by categories (crypto, web, forensics, etc.)
5. ✅ Review `/stats` and `/queries/recent` to track usage

## Useful Endpoints

| What | URL |
|------|-----|
| Interactive API docs | http://localhost:8000/docs |
| Health check | http://localhost:8000/health |
| System stats | http://localhost:8000/stats |
| List documents | http://localhost:8000/documents |
| Recent queries | http://localhost:8000/queries/recent |

## Category Organization

Organize your documents by NCL categories:

```bash
# Crypto documents
curl -X POST "http://localhost:8000/ingest/directory" \
  -H "Content-Type: application/json" \
  -d '{"directory_path": "/app/data/crypto", "category": "crypto"}'

# Web exploitation
curl -X POST "http://localhost:8000/ingest/directory" \
  -H "Content-Type: application/json" \
  -d '{"directory_path": "/app/data/web", "category": "web"}'

# Network analysis
curl -X POST "http://localhost:8000/ingest/directory" \
  -H "Content-Type: application/json" \
  -d '{"directory_path": "/app/data/network", "category": "network"}'
```

## Performance Tips

1. **First query is slow** - Models need to load, subsequent queries are faster
2. **Use categories** - Helps organize and filter documents
3. **Batch ingest** - Ingest entire directories at once
4. **Monitor stats** - Check `/stats` to see index size

## Support

For issues or questions:
1. Check logs: `docker-compose logs`
2. Review README.md for detailed documentation
3. Check `/health` endpoint for service status

Happy CTF preparation! 🎯

