# Mimi Core – My Information, My Intelligence

## Overview

Mimi Core is a single-service MNVP (Minimum Non-Viable Product) implementation
of an intelligent document processing and retrieval system. It provides document
ingestion, normalization, chunking, embedding, indexing, and RAG (Retrieval
Augmented Generation) query capabilities with citations.

## Features

- **Document Ingestion**: Upload and process text/Markdown documents
- **Smart Processing**: Text normalization, intelligent chunking, and deduplication
- **Semantic Search**: Vector-based similarity search with embeddings
- **RAG Queries**: Retrieve relevant chunks with citations
- **Conversational Agent**: Natural language Q&A with OpenAI or Ollama LLMs
- **Admin Interface**: Monitor ingestion events and document metadata
- **Modular Architecture**: Ready for microservice decomposition

## Quick Start

### Prerequisites

- Python 3.9+
- Docker (for Qdrant vector store)
- OpenAI API key

### Installation

1. **Clone and setup environment:**

```bash
git clone <repository-url>
cd mimi-core
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

1. **Configure environment:**

```bash
cp .env.example .env
# Edit .env with your OpenAI API key and other settings
```

1. **Start Qdrant (recommended vector backend):**

```bash
docker run -p 6333:6333 qdrant/qdrant
```

1. **Initialize database:**

```bash
python scripts/init_db.py
```

1. **Start the application:**

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8080
```

1. **Access the API:**

- Interactive docs: <http://localhost:8080/docs>
- Health check: <http://localhost:8080/health>

### Basic Usage

**Upload a document:**

```bash
curl -X POST "http://localhost:8080/ingest/upload" \
  -F "file=@document.txt" \
  -F "path=docs/document.txt" \
  -F "lang=en"
```

**Query documents:**

```bash
curl -X POST "http://localhost:8080/rag/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the document about?", "limit": 5}'
```

## Architecture

### Project Structure

```text
mimi-core/
├── app/
│   ├── api/              # HTTP endpoints (no business logic)
│   │   ├── health/       # Health check endpoint
│   │   ├── ingest/       # Document upload endpoints
│   │   ├── rag/          # Query endpoints
│   │   └── admin/        # Admin/monitoring endpoints
│   ├── services/         # Core business logic
│   │   ├── pipeline_core/    # Document processing pipeline
│   │   ├── vector_adapter/   # Vector storage abstraction
│   │   └── metadata/         # SQLite metadata management
│   ├── infra/            # Infrastructure concerns
│   │   ├── config/       # Configuration management
│   │   └── logging/      # JSON logging setup
│   ├── models/           # DTOs and type definitions
│   ├── policies/         # Processing policies
│   └── tests/            # Unit and integration tests
├── docs/                 # Documentation
├── scripts/              # Utility scripts
├── .env.example          # Environment template
└── requirements.txt      # Python dependencies
```

### Key Components

- **Pipeline Core**: Handles document normalization, chunking, and metadata extraction
- **Vector Adapter**: Abstracts vector storage (supports Qdrant and OpenAI Vector Store)
- **Metadata Service**: SQLite-based storage for document and event tracking
- **Processing Policies**: Configurable text normalization, chunking, and deduplication rules

## Configuration

Key environment variables:

| Variable             | Default                        | Description                                   |
| -------------------- | ------------------------------ | --------------------------------------------- |
| `VECTOR_BACKEND`     | `qdrant`                       | Vector storage backend (`qdrant` or `openai`) |
| `OPENAI_API_KEY`     | -                              | Required for embeddings                       |
| `QDRANT_URL`         | `http://localhost:6333`        | Qdrant instance URL                           |
| `UPLOAD_MAX_SIZE_MB` | `10`                           | Maximum upload file size                      |
| `DATABASE_URL`       | `sqlite:///./mimi_metadata.db` | Metadata database                             |

See `.env.example` for full configuration options.

## API Endpoints

### Core Endpoints

- `GET /health` - Health check
- `POST /ingest/upload` - Upload document for processing
- `POST /rag/query` - Query documents with semantic search

### Admin Endpoints

- `GET /admin/updates` - List recent ingestion events
- `GET /admin/docs` - List processed documents

Full API documentation available at `/docs` when running.

## Testing

```bash

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test categories
pytest app/tests/test_chunking.py        # Unit tests
pytest app/tests/test_integration.py     # Integration tests
```

## Development

### Adding New Features

1. **Models**: Add DTOs in `app/models/`
2. **Business Logic**: Implement in `app/services/`
3. **API Endpoints**: Create routers in `app/api/`
4. **Tests**: Add tests in `app/tests/`

### Processing Pipeline

The document processing flow:

1. Upload → Validation → Normalization
2. Chunking → Metadata extraction
3. Vector embedding → Storage
4. Event logging → Response

### Vector Backends

**Qdrant (Recommended):**

- Self-hosted vector database
- Full-featured with filtering and metadata
- Good for development and production

**OpenAI Vector Store:**

- Managed service option
- Simplified deployment
- Limited MNVP implementation

## Production Deployment

### Docker

```bash
# Build image
docker build -t mimi-core .

# Run container
docker run -p 8080:8080 --env-file .env mimi-core
```

### Environment

- Set `APP_ENV=production`
- Configure vector backend with production credentials
- Set up proper logging and monitoring
- Consider database migration from SQLite to PostgreSQL

## Conversational Agent Configuration

Mimi Core now includes a conversational agent that provides natural language
answers based on your document collection.

### Agent Backends

#### OpenAI Backend (Recommended)

```bash
# Add to your .env file
AGENT_BACKEND=openai
OPENAI_API_KEY=your_openai_api_key
AGENT_OPENAI_MODEL=gpt-4o-mini  # or gpt-4, gpt-3.5-turbo
```

#### Ollama Backend (Local LLM)

1. **Install and start Ollama:**

```bash
# Install Ollama from https://ollama.ai
ollama pull mistral  # or llama3, phi3, etc.
ollama serve
```

1. **Configure environment:**

```bash
# Add to your .env file
AGENT_BACKEND=ollama
AGENT_OLLAMA_MODEL=mistral  # or your preferred model
```

### Agent Features

- **Natural Language Q&A**: Ask questions about your documents in plain English
- **Automatic Citations**: Responses include source document references
- **Conversation Memory**: Optional session-based conversation history
- **Configurable Models**: Choose between OpenAI or local Ollama models

### Example Usage

```bash
# Ask the agent a question
curl -X POST "http://localhost:8080/agent/ask" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "How do I book a ticket?",
    "top_k": 3
  }'
```

Example response:

```json
{
  "answer": "To book a ticket, you need to follow these steps...",
  "citations": [
    {"doc_id": "upload:booking_flow.txt", "path": "kb/booking_flow.txt"}
  ],
  "raw_chunks": [...]
}
```

### Conversation Memory (Optional)

```bash
# Add to your .env file
AGENT_ENABLE_MEMORY=true

# Include session_id in requests for conversation context
curl -X POST "http://localhost:8080/agent/ask" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Can you elaborate on step 3?",
    "session_id": "user-123",
    "top_k": 3
  }'
```

## Microservices Migration

The modular architecture enables easy service extraction:

- **Document Service**: `app/services/pipeline_core/`
- **Vector Service**: `app/services/vector_adapter/`
- **Metadata Service**: `app/services/metadata/`
- **Query Service**: `app/api/rag/`
- **Agent Service**: `app/services/agent_core/`

Each service has minimal dependencies and clear interfaces.

## Troubleshooting

### Common Issues

**Vector store connection failed:**

- Ensure Qdrant is running and accessible
- Check `QDRANT_URL` configuration
- Verify network connectivity

**OpenAI API errors:**

- Validate API key and credits
- Check rate limits and model availability

**Upload failures:**

- Verify file format and size limits
- Ensure UTF-8 encoding for text files

See `docs/runbook/` for detailed troubleshooting guides.

## Contributing

1. Follow the modular architecture patterns
2. Add tests for new features
3. Update documentation
4. Ensure backward compatibility

## License

[Add your license here]

## Support

For support and questions:

- Check the documentation in `docs/`
- Review API docs at `/docs`
- See troubleshooting in `docs/runbook/`
