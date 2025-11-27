#!/bin/bash
# NCL RAG Setup and Test Script

set -e

echo "================================"
echo "NCL RAG System Setup & Test"
echo "================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Docker is running
echo "Checking Docker..."
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}Error: Docker is not running. Please start Docker first.${NC}"
    exit 1
fi
echo -e "${GREEN}Docker is running${NC}"
echo ""

# Build and start services
echo "Building and starting services..."
docker-compose up -d --build

echo ""
echo "Waiting for services to be ready..."
sleep 10

# Check Ollama health
echo "Checking Ollama service..."
for i in {1..30}; do
    if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
        echo -e "${GREEN}Ollama is ready${NC}"
        break
    fi
    echo "Waiting for Ollama... ($i/30)"
    sleep 2
done

# Check API health
echo "Checking API service..."
for i in {1..30}; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo -e "${GREEN}API is ready${NC}"
        break
    fi
    echo "Waiting for API... ($i/30)"
    sleep 2
done

echo ""
echo "================================"
echo "Pulling LLM Model"
echo "================================"
echo "This may take several minutes..."
echo ""

# Pull the default model
docker exec ncl-rag-ollama ollama pull qwen2.5:7b-instruct

echo ""
echo -e "${GREEN}Model downloaded${NC}"
echo ""

# Ingest sample documents
echo "================================"
echo "Ingesting Sample Documents"
echo "================================"
echo ""

# Wait a moment for API to fully initialize
sleep 5

# Ingest the docs directory
curl -X POST "http://localhost:8000/ingest/directory" \
  -H "Content-Type: application/json" \
  -d '{
    "directory_path": "/app/docs",
    "recursive": true,
    "category": "ncl-guides"
  }' | python3 -m json.tool

echo ""
echo ""
echo "================================"
echo "Testing RAG System"
echo "================================"
echo ""

# Test query 1
echo -e "${YELLOW}Test Query 1: SQL Injection${NC}"
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is SQL injection and how can I test for it?",
    "top_k": 3,
    "return_sources": false
  }' | python3 -m json.tool

echo ""
echo ""

# Test query 2
echo -e "${YELLOW}Test Query 2: Cryptography${NC}"
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "How do I decode Base64 in CTF challenges?",
    "top_k": 3,
    "return_sources": false
  }' | python3 -m json.tool

echo ""
echo ""

# Get stats
echo "================================"
echo "System Statistics"
echo "================================"
echo ""

curl -s http://localhost:8000/stats | python3 -m json.tool

echo ""
echo ""
echo "================================"
echo "Setup Complete!"
echo "================================"
echo ""
echo -e "${GREEN}Your NCL RAG system is ready!${NC}"
echo ""
echo "Access points:"
echo "  - API Documentation: http://localhost:8000/docs"
echo "  - Health Check: http://localhost:8000/health"
echo "  - Ollama: http://localhost:11434"
echo ""
echo "Example query:"
echo "  curl -X POST http://localhost:8000/query \\"
echo "    -H 'Content-Type: application/json' \\"
echo "    -d '{\"query\": \"What is XSS?\"}'"
echo ""
echo "View logs:"
echo "  docker-compose logs -f rag-api"
echo ""
echo "Stop services:"
echo "  docker-compose down"
echo ""

