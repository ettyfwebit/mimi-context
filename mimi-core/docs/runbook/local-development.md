# Mimi Core Runbook

## Local Development Setup

### Prerequisites

- Python 3.9+
- Docker (for Qdrant)
- OpenAI API key (for embeddings)

### Step 1: Environment Setup

```bash
# Clone and navigate to repository
cd mimi-core

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your settings:
# - Set OPENAI_API_KEY
# - Configure vector backend (qdrant recommended for local dev)
# - Set other configuration as needed
```

### Step 3: Start Qdrant (if using Qdrant backend)

```bash
# Start Qdrant with Docker
docker run -p 6333:6333 qdrant/qdrant

# Or use docker-compose (if provided)
docker-compose up -d qdrant
```

### Step 4: Initialize Database

```bash
# Run database initialization script
python scripts/init_db.py
```

### Step 5: Start Application

```bash
# Development server with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8080

# Production-like server
uvicorn app.main:app --host 0.0.0.0 --port 8080
```

### Step 6: Verify Installation

Visit http://localhost:8080/docs to access the interactive API documentation.

## Smoke Tests

### 1. Health Check

```bash
curl http://localhost:8080/health
# Expected: {"status": "ok"}
```

### 2. Document Upload

```bash
# Create test document
echo "This is a test document about booking tickets. The process involves selecting dates and destinations." > test_doc.txt

# Upload document
curl -X POST "http://localhost:8080/ingest/upload" \
  -F "file=@test_doc.txt" \
  -F "path=test/test_doc.txt" \
  -F "lang=en"

# Expected: {"ok": true, "doc_id": "upload:test_doc.txt", "chunks": 1}
```

### 3. RAG Query

```bash
curl -X POST "http://localhost:8080/rag/query" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "How to book tickets?",
    "top_k": 3
  }'

# Expected: {"answers": [{"text": "", "chunks": [...]}]}
```

### 4. Admin Endpoints

```bash
# List recent events
curl "http://localhost:8080/admin/updates?limit=10"

# List documents
curl "http://localhost:8080/admin/docs?limit=10"
```

## Running Tests

### Unit Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest app/tests/test_chunking.py

# Run with coverage
pytest --cov=app
```

### Integration Tests

```bash
# Run integration tests (requires running services)
pytest app/tests/test_integration.py

# Skip tests requiring external services
pytest -m "not external"
```

## Production Deployment

### Environment Variables

Ensure these are set in production:

- `APP_ENV=production`
- `OPENAI_API_KEY=your_api_key`
- `VECTOR_BACKEND=qdrant` (recommended)
- `QDRANT_URL=https://your-qdrant-instance`
- `QDRANT_API_KEY=your_qdrant_key` (if required)

### Docker Deployment

```bash
# Build image
docker build -t mimi-core .

# Run container
docker run -p 8080:8080 --env-file .env mimi-core
```

### Health Monitoring

- Health endpoint: `GET /health`
- Metrics: Check logs for ingestion events and performance data
- Error tracking: Monitor application logs for error patterns

## Troubleshooting

### Common Issues

**Vector store connection failed**

- Check Qdrant is running and accessible
- Verify QDRANT_URL and credentials
- Check network connectivity

**OpenAI API errors**

- Verify API key is valid and has credits
- Check rate limits and usage quotas
- Ensure embedding model is available

**Database initialization errors**

- Check file permissions for SQLite database
- Ensure database directory exists
- Verify disk space availability

**Large file upload failures**

- Check UPLOAD_MAX_SIZE_MB setting
- Verify file encoding (must be UTF-8)
- Ensure allowed file extensions

### Log Analysis

```bash
# View application logs
tail -f app.log

# Filter for errors
grep "ERROR" app.log

# Monitor ingestion events
grep "ingest" app.log
```
