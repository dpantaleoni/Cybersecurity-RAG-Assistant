# Installation Guide

## Prerequisites

Before installing the NCL RAG system, ensure you have:

1. **Docker Desktop** (or Docker Engine + Docker Compose)
   - Download from: https://www.docker.com/products/docker-desktop
   - Version: 20.10+ recommended

2. **System Requirements**
   - RAM: 8GB minimum, 16GB recommended
   - Disk: 10GB free space (for models and data)
   - CPU: Modern multi-core processor
   - OS: macOS, Linux, or Windows with WSL2

3. **Optional: Python 3.10+** (for local development only)

## Installation Steps

### Option 1: Automated Setup (Recommended)

The easiest way to get started:

```bash
# 1. Navigate to the project directory
cd /Users/dominikpantaleoni/Documents/programming/ncl-rag-app

# 2. Run the automated setup script
./setup_and_test.sh
```

This script will:
- Build Docker containers
- Start all services
- Download the LLM model
- Ingest sample documents
- Run test queries
- Display system statistics

**Estimated time**: 10-15 minutes (first run)

### Option 2: Manual Setup

If you prefer manual control:

```bash
# 1. Navigate to project
cd /Users/dominikpantaleoni/Documents/programming/ncl-rag-app

# 2. Build and start services
docker-compose up -d --build

# 3. Wait for services to be ready (30-60 seconds)
sleep 60

# 4. Download the LLM model
docker exec ncl-rag-ollama ollama pull qwen2.5:7b-instruct

# 5. Verify services are running
docker-compose ps

# 6. Check health
curl http://localhost:8000/health

# 7. (Optional) Ingest sample documents
curl -X POST "http://localhost:8000/ingest/directory" \
  -H "Content-Type: application/json" \
  -d '{"directory_path": "/app/docs", "recursive": true}'
```

## Verification

### 1. Check Docker Containers

```bash
docker-compose ps
```

You should see two containers running:
- `ncl-rag-ollama` (Ollama service)
- `ncl-rag-api` (FastAPI service)

### 2. Test API Health

```bash
curl http://localhost:8000/health | python3 -m json.tool
```

Expected output:
```json
{
  "status": "healthy",
  "ollama_connected": true,
  "vector_store_initialized": true,
  "database_connected": true,
  "model": "qwen2.5:7b-instruct",
  "timestamp": "2025-10-22T..."
}
```

### 3. Run Test Query

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What is Base64 encoding?"}' \
  | python3 -m json.tool
```

### 4. View API Documentation

Open your browser to: http://localhost:8000/docs

## Troubleshooting

### Docker Not Running

**Error**: `Cannot connect to the Docker daemon`

**Solution**:
```bash
# macOS/Windows: Start Docker Desktop

# Linux: Start Docker service
sudo systemctl start docker
```

### Port Already in Use

**Error**: `Bind for 0.0.0.0:8000 failed: port is already allocated`

**Solution**:
```bash
# Find process using port 8000
lsof -i :8000

# Kill the process or change port in docker-compose.yml
# Edit ports: section to use different port (e.g., "8001:8000")
```

### Ollama Connection Failed

**Error**: `Failed to connect to Ollama`

**Solution**:
```bash
# Check if Ollama container is running
docker-compose ps

# View Ollama logs
docker-compose logs ollama

# Restart Ollama
docker-compose restart ollama

# Wait 30 seconds and retry
sleep 30
curl http://localhost:11434/api/tags
```

### Model Download Failed

**Error**: `Failed to pull model`

**Solution**:
```bash
# Ensure you have internet connection
ping google.com

# Try pulling model again
docker exec ncl-rag-ollama ollama pull qwen2.5:7b-instruct

# Or try a different model
docker exec ncl-rag-ollama ollama pull llama3.2:3b-instruct
```

### Permission Denied on Scripts

**Error**: `Permission denied: ./setup_and_test.sh`

**Solution**:
```bash
chmod +x setup_and_test.sh test_queries.sh test_client.py
```

### Out of Memory

**Error**: Container crashes or system becomes unresponsive

**Solution**:
```bash
# Use a smaller model
docker exec ncl-rag-ollama ollama pull qwen2.5:3b-instruct

# Update .env
echo "LLM_MODEL=qwen2.5:3b-instruct" >> .env

# Restart
docker-compose restart rag-api
```

## Post-Installation

### 1. Add Your Documents

```bash
# Copy your CTF notes to data directory
cp ~/my-ncl-notes/* /path/to/ncl-rag-app/data/

# Ingest them
curl -X POST "http://localhost:8000/ingest/directory" \
  -H "Content-Type: application/json" \
  -d '{"directory_path": "/app/data", "recursive": true}'
```

### 2. Organize by Category

```bash
# Create category directories
mkdir -p data/{crypto,web,network,forensics,passwords}

# Move files to appropriate categories
mv data/*crypto* data/crypto/
mv data/*web* data/web/

# Ingest with categories
curl -X POST "http://localhost:8000/ingest/directory" \
  -H "Content-Type: application/json" \
  -d '{"directory_path": "/app/data/crypto", "category": "crypto"}'
```

### 3. Test the System

```bash
# Run test queries
./test_queries.sh

# Or use Python client
python3 test_client.py
```

## Uninstallation

To completely remove the NCL RAG system:

```bash
# 1. Stop and remove containers
docker-compose down

# 2. Remove volumes (WARNING: Deletes all data)
docker-compose down -v

# 3. Remove images
docker rmi ncl-rag-app-rag-api ollama/ollama

# 4. (Optional) Remove project directory
cd ..
rm -rf ncl-rag-app
```

## Updating

To update to a newer version:

```bash
# 1. Pull latest changes (if using git)
git pull

# 2. Rebuild containers
docker-compose up -d --build

# 3. Pull latest model (if needed)
docker exec ncl-rag-ollama ollama pull qwen2.5:7b-instruct

# 4. Restart services
docker-compose restart
```

## Configuration

### Environment Variables

Edit `.env` file to customize:

```bash
# LLM Configuration
LLM_MODEL=qwen2.5:7b-instruct

# RAG Parameters
CHUNK_SIZE=512
TOP_K=5
USE_RERANKER=true

# Storage
DATA_DIR=/app/data
```

After editing, restart:
```bash
docker-compose restart rag-api
```

### Resource Limits

To limit Docker resource usage, edit `docker-compose.yml`:

```yaml
services:
  rag-api:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
```

## Next Steps

1. ✅ Read `QUICKSTART.md` for usage examples
2. ✅ Visit http://localhost:8000/docs for API documentation
3. ✅ Add your NCL notes to `data/` directory
4. ✅ Start querying!

## Support

- Check `README.md` for detailed documentation
- View logs: `docker-compose logs -f`
- Check health: `curl http://localhost:8000/health`
- Test API: http://localhost:8000/docs

## Success Indicators

✅ Docker containers running
✅ Health check returns "healthy"
✅ Test query returns answer
✅ API docs accessible at /docs
✅ Sample documents ingested

Your NCL RAG system is ready! 🎉

