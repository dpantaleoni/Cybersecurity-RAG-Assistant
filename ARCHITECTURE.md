# NCL RAG System Architecture

## System Overview

```
┌─────────────┐
│   Client    │ (Browser, curl, Python client)
└──────┬──────┘
       │ HTTP
       ▼
┌─────────────────────────────────────────┐
│         FastAPI Backend (Port 8000)     │
│  ┌───────────────────────────────────┐  │
│  │         API Endpoints             │  │
│  │  /query, /ingest, /retrieve, etc  │  │
│  └────────────┬──────────────────────┘  │
│               │                         │
│  ┌────────────▼──────────────────────┐  │
│  │      RAG Pipeline                 │  │
│  │  - Query processing               │  │
│  │  - Document retrieval             │  │
│  │  - Response generation            │  │
│  └────┬──────────────┬────────────┬──┘  │
│       │              │            │     │
│  ┌────▼────┐   ┌─────▼────┐  ┌───▼───┐ │
│  │ Vector  │   │Embedding │  │  LLM  │ │
│  │ Store   │   │ Manager  │  │Client │ │
│  │(FAISS)  │   │  (BGE)   │  │(Ollama)│
│  └────┬────┘   └──────────┘  └───┬───┘ │
│       │                          │     │
└───────┼──────────────────────────┼─────┘
        │                          │
        ▼                          ▼
  ┌──────────┐            ┌──────────────┐
  │  SQLite  │            │    Ollama    │
  │ Metadata │            │   Service    │
  │ Database │            │  (Port 11434)│
  └──────────┘            └──────────────┘
```

## Component Details

### 1. FastAPI Backend (`src/main.py`)

**Responsibilities:**
- Expose REST API endpoints
- Request validation with Pydantic
- Error handling and logging
- CORS configuration

**Key Endpoints:**
- `POST /query` - Ask questions
- `POST /ingest/file` - Ingest single file
- `POST /ingest/directory` - Ingest directory
- `GET /documents` - List documents
- `GET /stats` - System statistics
- `GET /health` - Health check

### 2. RAG Pipeline (`src/rag_pipeline.py`)

**Responsibilities:**
- Orchestrate query workflow
- Manage retrieval + generation
- Interface with Ollama LLM
- Query logging

**Workflow:**
```
User Query
    ↓
Embedding (BGE)
    ↓
Vector Search (FAISS)
    ↓
Reranking (Optional)
    ↓
Context Assembly
    ↓
LLM Generation (Ollama)
    ↓
Response
```

### 3. Vector Store Manager (`src/vector_store.py`)

**Responsibilities:**
- FAISS index management
- Document storage and retrieval
- Index persistence
- Query execution

**Storage Format:**
- `storage/faiss/index.faiss` - FAISS index
- `storage/faiss/docstore.pkl` - Document store

### 4. Embedding Manager (`src/embeddings.py`)

**Responsibilities:**
- Load embedding model (BGE)
- Load reranker model
- Manage model caching

**Models:**
- Embedding: `sentence-transformers/bge-small-en-v1.5`
  - Dimension: 384
  - CPU-friendly
- Reranker: `BAAI/bge-reranker-base`
  - Improves retrieval accuracy

### 5. Document Ingestion (`src/ingestion.py`)

**Responsibilities:**
- File loading and parsing
- Text chunking
- Deduplication
- Metadata extraction

**Process:**
```
File Upload
    ↓
Hash Calculation
    ↓
Duplicate Check
    ↓
Content Extraction
    ↓
Chunking (512 tokens, 50 overlap)
    ↓
Embedding
    ↓
Store in FAISS + SQLite
```

### 6. Database Manager (`src/database.py`)

**Responsibilities:**
- Document metadata tracking
- Query logging
- Statistics

**Tables:**
- `documents` - File metadata
- `query_logs` - Query history

### 7. Configuration (`src/config.py`)

**Responsibilities:**
- Environment variable loading
- Settings validation
- Directory creation

## Data Flow

### Query Flow

```python
1. Client sends query → FastAPI
2. FastAPI → RAG Pipeline
3. RAG Pipeline:
   a. Embed query (BGE)
   b. Search FAISS index
   c. Get top-k documents
   d. (Optional) Rerank results
   e. Build prompt with context
   f. Call Ollama LLM
   g. Return response
4. Log to SQLite
5. Return to client
```

### Ingestion Flow

```python
1. Client uploads file → FastAPI
2. FastAPI → Ingestion Service
3. Ingestion Service:
   a. Calculate file hash
   b. Check for duplicates
   c. Load file content
   d. Split into chunks
   e. Generate embeddings
   f. Store in FAISS
   g. Save metadata to SQLite
4. Return status to client
```

## Storage Layout

```
ncl-rag-app/
├── storage/
│   ├── faiss/
│   │   ├── index.faiss          # Vector index
│   │   └── docstore.pkl         # Document content
│   ├── metadata/
│   │   └── documents.db         # SQLite database
│   ├── models/                  # Cached embedding models
│   └── app.log                  # Application logs
├── data/
│   ├── uploads/                 # API uploads
│   └── [user documents]
└── docs/                        # Sample documents
```

## Configuration

### Environment Variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `OLLAMA_BASE_URL` | `http://ollama:11434` | Ollama API URL |
| `LLM_MODEL` | `qwen2.5:7b-instruct` | LLM model name |
| `EMBEDDING_MODEL` | `bge-small-en-v1.5` | Embedding model |
| `CHUNK_SIZE` | `512` | Chunk size in tokens |
| `TOP_K` | `5` | Retrieved documents |
| `USE_RERANKER` | `true` | Enable reranking |

### Customization Points

1. **LLM Model**: Change `LLM_MODEL` in `.env`
2. **Chunk Size**: Adjust `CHUNK_SIZE` for different granularity
3. **Retrieval Count**: Modify `TOP_K` for more/fewer results
4. **Reranking**: Toggle `USE_RERANKER` for performance vs accuracy

## Scalability Considerations

### Current Limitations

- **FAISS**: In-memory index, limited by RAM
- **SQLite**: Single-writer, suitable for moderate load
- **Ollama**: Single instance, sequential processing

### Scaling Options

1. **Horizontal Scaling**
   - Multiple API instances behind load balancer
   - Shared storage (NFS or object store)
   - Redis for caching

2. **Vector Store Upgrade**
   - FAISS → Qdrant/Milvus for distributed search
   - Sharding by category

3. **Database Upgrade**
   - SQLite → PostgreSQL for better concurrency
   - Separate read replicas

4. **LLM Scaling**
   - Multiple Ollama instances
   - GPU acceleration
   - Model quantization (4-bit)

## Performance Optimization

### Query Performance

1. **Embedding Cache**: Cache frequent query embeddings
2. **Index Optimization**: Use IVF indices for large datasets
3. **Reranker Toggle**: Disable for faster responses
4. **Model Size**: Use smaller models (3B vs 7B)

### Ingestion Performance

1. **Batch Processing**: Ingest files in batches
2. **Async Processing**: Background job queue
3. **Incremental Updates**: Only re-index changed files

## Security Considerations

### Current Setup

- Local execution (no data leaves system)
- No external API calls
- File system isolation
- No authentication (localhost only)
- No input sanitization for file paths

### Production Hardening

1. **Add Authentication**: JWT or API keys
2. **Input Validation**: Strict file path validation
3. **Rate Limiting**: Prevent abuse
4. **HTTPS**: TLS encryption
5. **Sandboxing**: Restrict file system access

## Monitoring

### Metrics to Track

1. **Query Metrics**
   - Response time
   - Success rate
   - Retrieved chunks

2. **System Metrics**
   - Memory usage (FAISS index size)
   - Disk usage
   - CPU/GPU utilization

3. **Document Metrics**
   - Total documents
   - Total chunks
   - Categories distribution

### Logging

- **Application Logs**: `storage/app.log`
- **Docker Logs**: `docker-compose logs`
- **Query Logs**: SQLite `query_logs` table

## Troubleshooting

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| Slow queries | Large index or weak hardware | Reduce `TOP_K`, disable reranker |
| OOM errors | Large index + embeddings | Reduce `CHUNK_SIZE`, limit documents |
| Ollama timeout | Model too large | Use smaller model |
| Empty results | No documents ingested | Check `/stats`, ingest docs |

### Debug Mode

Enable debug logging in `.env`:
```bash
DEBUG=true
```

## Technology Choices

### Why Ollama?
- Free and local
- Easy model management
- Good performance
- Active development

### Why FAISS?
- Fast similarity search
- CPU-optimized
- Battle-tested by Facebook
- No server required

### Why LlamaIndex?
- High-level RAG abstractions
- Good documentation
- Active community
- Multiple integrations

### Why FastAPI?
- Fast and modern
- Automatic API docs
- Type validation
- Async support

## Future Enhancements

1. **Multi-modal Support**: Images, PDFs with OCR
2. **Conversational Memory**: Track chat history
3. **Advanced Retrieval**: Hybrid search (BM25 + vector)
4. **Evaluation**: Metrics for RAG quality
5. **Web UI**: Streamlit/Gradio interface
6. **Export**: Save conversations as markdown
7. **Agents**: ReAct-style reasoning
8. **Fine-tuning**: Adapt embeddings for CTF domain

