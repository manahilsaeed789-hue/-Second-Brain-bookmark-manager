# Second Brain — AI-Powered Bookmark Manager

> Your personal knowledge base powered by AI embeddings, semantic search, and intelligent summarization.

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

Second Brain transforms how you save and rediscover information. Save URLs, notes, articles, and PDFs — then let AI automatically summarize, tag, and embed your content for intelligent retrieval.

## Features

- **Multi-format saving** — URLs, notes, pasted text, PDF/TXT/Markdown uploads
- **AI summarization** — Short & detailed summaries, key insights, actionable takeaways
- **Intelligent tagging** — Auto-generated topic, category, intent, and learning tags
- **Semantic search** — Natural language queries powered by ChromaDB + Sentence Transformers
- **Smart collections** — Auto-grouped bookmarks (Research, Career, Tutorials, etc.)
- **Knowledge dashboard** — Stats, trending interests, daily rediscovery, knowledge map
- **RAG chat** — Ask questions about your saved bookmarks
- **Analytics** — Search trends, category insights, weekly summaries
- **Dark/light mode** — Premium responsive UI

## Quick Start

### Prerequisites

- Python 3.10+
- pip

### One-Command Setup

**Windows:**
```powershell
cd second-brain
.\setup.ps1
```

**Linux/macOS:**
```bash
cd second-brain
chmod +x setup.sh
./setup.sh
```

### Manual Setup

```bash
# 1. Clone and enter project
cd second-brain

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY (optional — local fallbacks work without it)

# 5. Seed demo data (optional)
python database/seed.py

# 6. Launch the app
uvicorn app:app --reload
```

Open **http://localhost:8000** in your browser.

### Demo Account

After running the seed script:
- **Email:** demo@secondbrain.app
- **Password:** demo1234

## Project Structure

```
second-brain/
├── app.py                  # FastAPI application entry point
├── requirements.txt        # Python dependencies
├── .env.example            # Environment template
├── backend/
│   ├── config.py           # Settings management
│   ├── database.py         # SQLAlchemy setup
│   ├── models.py           # Database models
│   ├── schemas.py          # Pydantic schemas
│   ├── auth.py             # Authentication utilities
│   ├── routes/             # API route handlers
│   └── services/           # Business logic layer
│       ├── ai_service.py           # AI summarization & tagging
│       ├── embedding_service.py    # ChromaDB vector operations
│       ├── content_extractor.py    # URL/PDF/text extraction
│       ├── bookmark_service.py     # Bookmark CRUD pipeline
│       ├── rag_service.py          # RAG chat
│       └── clustering_service.py   # Duplicate detection & clustering
├── frontend/               # Frontend assets reference
├── templates/              # Jinja2 HTML templates
├── static/
│   ├── css/style.css       # Premium UI styles
│   └── js/                 # Page-specific JavaScript
├── database/
│   └── seed.py             # Demo data seeder
├── embeddings/             # ChromaDB vector storage
├── uploads/                # Uploaded files
├── tests/                  # Test suite
└── docs/                   # Architecture & API docs
```

## Architecture

```
Browser → FastAPI → Services → SQLite (data) + ChromaDB (vectors)
                              → OpenAI (summaries/tags/chat)
                              → Sentence Transformers (embeddings)
```

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for detailed diagrams and data flows.

## API Documentation

Interactive docs available at:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

Full reference: [docs/API.md](docs/API.md)

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python, FastAPI, Uvicorn |
| Database | SQLite, SQLAlchemy |
| Vectors | ChromaDB, Sentence Transformers |
| AI | OpenAI GPT-4o-mini (with local fallbacks) |
| Frontend | HTML, CSS, JavaScript, Jinja2 |
| Auth | bcrypt, session cookies |

## Running Tests

```bash
pytest tests/ -v
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key (optional) | — |
| `SECRET_KEY` | Session signing key | dev key |
| `DATABASE_URL` | SQLite connection string | `./database/second_brain.db` |
| `CHROMA_PERSIST_DIR` | ChromaDB storage path | `./embeddings/chroma_db` |
| `OPENAI_MODEL` | OpenAI model name | `gpt-4o-mini` |
| `EMBEDDING_MODEL` | Sentence Transformers model | `all-MiniLM-L6-v2` |

## Screenshots

The app includes:
- **Dashboard** — Stats, recent saves, trending tags, knowledge map
- **Save Content** — Tabbed interface for URL, notes, paste, file upload
- **Semantic Search** — Natural language queries with similarity scores
- **Bookmark Detail** — Summaries, insights, similar content
- **AI Chat** — RAG-powered Q&A over your bookmarks
- **Analytics** — Search trends and weekly insights

## License

MIT License — free for personal and commercial use.

## Author

Built as a portfolio project demonstrating AI engineering concepts: embeddings, semantic search, RAG, and intelligent content processing.
