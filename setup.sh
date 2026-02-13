#!/bin/bash
# Quick start script for YTScriptify

set -e

echo "🚀 YTScriptify Setup Script"
echo "================================"

# Check Python version
echo "✓ Checking Python version..."
python_version=$(python --version 2>&1 | awk '{print $2}')
echo "  Python $python_version"

# Install dependencies
echo "✓ Installing dependencies..."
pip install -r requirements.txt

# Create database
echo "✓ Creating database..."
python -c "from models import db; from app import app; app.app_context().push(); db.create_all()"

# Check for .env
if [ ! -f .env ]; then
    echo "✓ Creating .env from .env.example..."
    cp .env.example .env
    echo "  ⚠️  Update .env with your API_KEY and SECRET_KEY!"
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Make sure Redis is running: redis-server"
echo "2. Start Celery worker: celery -A celery_app worker --loglevel=info"
echo "3. Start Flask app: python app.py"
echo ""
