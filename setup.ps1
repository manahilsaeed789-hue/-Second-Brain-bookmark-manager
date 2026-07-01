# Second Brain — One-command setup script (Windows)
Write-Host "Second Brain — Setup" -ForegroundColor Cyan
Write-Host "========================"

# Create virtual environment
if (-not (Test-Path "venv")) {
    Write-Host "Creating virtual environment..."
    python -m venv venv
}

# Activate
& "venv\Scripts\Activate.ps1"

# Install dependencies
Write-Host "Installing dependencies (this may take a few minutes)..."
pip install -r requirements.txt

# Create .env if missing
if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "Created .env from template — edit to add your OPENAI_API_KEY"
}

# Create directories
New-Item -ItemType Directory -Force -Path "database", "embeddings\chroma_db", "uploads" | Out-Null

# Seed demo data
Write-Host "Seeding demo data..."
python database/seed.py

Write-Host ""
Write-Host "Setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Launch the app:"
Write-Host "  venv\Scripts\Activate.ps1"
Write-Host "  uvicorn app:app --reload"
Write-Host ""
Write-Host "Then open http://localhost:8000"
Write-Host "Demo login: demo@secondbrain.app / demo1234"
