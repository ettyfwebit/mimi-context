#!/bin/bash

# Mimi Core Start Script
# This script activates the virtual environment and starts the server

set -e

echo "🚀 Starting Mimi Core..."

# Navigate to project directory
cd "$(dirname "$0")"

# Activate virtual environment
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run ./setup-dev.sh first"
    exit 1
fi

echo "📦 Activating virtual environment..."
source venv/bin/activate

# Check if Qdrant is running
echo "🔍 Checking Qdrant connection..."
if ! curl -s http://localhost:6333/ >/dev/null 2>&1; then
    echo "🗄️  Starting Qdrant..."
    docker run -d --name qdrant -p 6333:6333 qdrant/qdrant:latest 2>/dev/null || \
    docker start qdrant 2>/dev/null || \
    echo "⚠️  Please start Qdrant manually: docker run -d --name qdrant -p 6333:6333 qdrant/qdrant:latest"
    
    # Wait for Qdrant to start
    echo "⏳ Waiting for Qdrant to start..."
    sleep 5
fi

echo "🌐 Starting Mimi Core server on http://localhost:8080"
echo "📚 API docs available at: http://localhost:8080/docs"
echo "🛑 Press Ctrl+C to stop"
echo ""

# Start the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8080