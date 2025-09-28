# Mimi Context - Intelligence Document Processing System

A full-stack application for intelligent document processing, retrieval, and conversational AI.

## Project Structure

- **`mimi-core/`** - Backend FastAPI service for document processing, embedding, and RAG queries
- **`mimi-web/`** - Frontend React application with TypeScript and Tailwind CSS

## Features

- **Document Ingestion**: Upload and process text/Markdown documents
- **Smart Processing**: Text normalization, intelligent chunking, and deduplication
- **Semantic Search**: Vector-based similarity search with embeddings  
- **RAG Queries**: Retrieve relevant chunks with citations
- **Conversational Agent**: Natural language Q&A with OpenAI or Ollama LLMs
- **Modern UI**: Clean, responsive interface built with React and Tailwind CSS

## Quick Start

### Prerequisites

- Python 3.9+
- Node.js 16+
- Docker (for Qdrant vector store)
- OpenAI API key (optional, can use Ollama)

### Backend Setup

```bash
cd mimi-core
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your OpenAI API key and other settings

# Start Qdrant
docker run -p 6333:6333 qdrant/qdrant

# Initialize database
python scripts/init_db.py

# Start backend
./start.sh
```

### Frontend Setup

```bash
cd mimi-web
npm install
npm run dev
```

## Development

- Backend runs on: http://localhost:8080
- Frontend runs on: http://localhost:3000
- API Documentation: http://localhost:8080/docs

## Architecture

Built as a modular system ready for microservice decomposition:

- **FastAPI Backend**: RESTful APIs for document processing and AI queries
- **React Frontend**: Modern SPA with TypeScript and Tailwind CSS
- **Vector Database**: Qdrant for semantic search capabilities
- **SQLite**: Metadata storage and system state
- **LLM Integration**: OpenAI GPT models or local Ollama support

## License

[Add your license here]