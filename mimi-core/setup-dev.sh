#!/bin/bash

# Mimi Core Development Setup Script

set -e

echo "🚀 Setting up Mimi Core development environment..."

# Check Python version
if ! python3 --version | grep -q "Python 3\.[9-9]\|Python 3\.1[0-9]"; then
    echo "❌ Python 3.9+ required"
    exit 1
fi

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo "📚 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Copy environment template
if [ ! -f .env ]; then
    echo "⚙️  Creating .env from template..."
    cp .env.example .env
    echo "📝 Please edit .env with your OpenAI API key and other settings"
fi

# Start Qdrant with Docker Compose
echo "🗄️  Starting Qdrant..."
if command -v docker-compose &> /dev/null; then
    docker-compose up -d qdrant
elif command -v docker &> /dev/null && docker compose version &> /dev/null; then
    docker compose up -d qdrant
else
    echo "⚠️  Docker/docker-compose not found. Please start Qdrant manually:"
    echo "   docker run -p 6333:6333 qdrant/qdrant"
fi

# Wait for Qdrant to start
echo "⏳ Waiting for Qdrant to start..."
sleep 5

# Initialize database
echo "🗃️  Initializing database..."
python scripts/init_db.py

echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env with your settings (OpenAI API key is optional - using local embeddings)"
echo "2. Run: ./start.sh"
echo "3. Visit: http://localhost:8080/docs"
echo ""
echo "Available commands:"
echo "  ./start.sh           - Start the server (auto-activates venv)"
echo "  ./venv/bin/pytest   - Run tests"
echo "  ./venv/bin/python scripts/seed_data.py - Seed sample data"