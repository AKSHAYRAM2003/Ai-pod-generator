#!/bin/bash

# AI Podcast Generator - Backend Setup and Start Script

set -e

echo "🚀 Setting up AI Podcast Generator Backend..."

# Check if Python 3.8+ is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📚 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "⚙️ Creating .env file from template..."
    cp .env.example .env
    echo "📝 Please update the .env file with your configuration before running the server."
    echo "   Key settings to update:"
    echo "   - DATABASE_URL: Your PostgreSQL connection string"
    echo "   - JWT_SECRET_KEY: A secure secret key for JWT tokens"
    echo "   - SMTP_*: Email service configuration"
    echo ""
    echo "   Example PostgreSQL URL: postgresql://username:password@localhost:5432/ai_podcast_db"
    echo ""
    read -p "Press Enter when you've updated the .env file..."
fi

# Run database migrations
echo "🗄️ Running database migrations..."
alembic upgrade head

# Start the server
echo "🌟 Starting FastAPI server..."
echo "📍 Server will be available at: http://localhost:8000"
echo "📖 API documentation: http://localhost:8000/api/docs"
echo "🔍 Health check: http://localhost:8000/health"
echo ""
echo "Press Ctrl+C to stop the server"

uvicorn main:app --host 0.0.0.0 --port 8000 --reload
