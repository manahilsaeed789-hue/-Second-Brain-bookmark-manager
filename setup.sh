#!/usr/bin/env bash
# Second Brain — One-command setup script (Linux/macOS)

set -e

echo "🧠 Second Brain — Setup"
echo "========================"

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate
source venv/bin/activate

# Install dependencies
echo "Installing dependencies (this may take a few minutes)..."
pip install -r requirements.txt

# Create .env if missing
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "Created .env from template — edit to add your OPENAI_API_KEY"
fi

# Create directories
mkdir -p database embeddings/chroma_db uploads

# Seed demo data
echo "Seeding demo data..."
python database/seed.py

echo ""
echo "✅ Setup complete!"
echo ""
echo "Launch the app:"
echo "  source venv/bin/activate"
echo "  uvicorn app:app --reload"
echo ""
echo "Then open http://localhost:8000"
echo "Demo login: demo@secondbrain.app / demo1234"
