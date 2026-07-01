# Second Brain — Architecture Documentation

## System Overview

Second Brain is an AI-powered bookmark manager that transforms saved web content into a searchable, intelligent personal knowledge base.

```
┌─────────────────────────────────────────────────────────────────┐
│                        Client (Browser)                         │
│              HTML / CSS / JavaScript (Responsive UI)              │
└──────────────────────────┬──────────────────────────────────────┘
                           │ HTTP
┌──────────────────────────▼──────────────────────────────────────┐
│                     FastAPI Application                          │
│  ┌──────────┐ ┌───────────┐ ┌──────────┐ ┌──────────────────┐  │
│  │   Auth   │ │ Bookmarks │ │  Search  │ │ Dashboard/Chat   │  │
│  │  Routes  │ │  Routes   │ │  Routes  │ │    Routes        │  │
│  └────┬─────┘ └─────┬─────┘ └────┬─────┘ └────────┬─────────┘  │
│       │             │            │                 │            │
│  ┌────▼─────────────▼────────────▼─────────────────▼─────────┐  │
│  │                     Service Layer                          │  │
│  │  bookmark_service │ ai_service │ embedding_service │ rag   │  │
│  └────┬─────────────┬────────────┬─────────────────┬──────────┘  │
└───────┼─────────────┼────────────┼─────────────────┼─────────────┘
        │             │            │                 │
┌───────▼──────┐ ┌────▼─────┐ ┌───▼────────┐ ┌─────▼──────────┐
│   SQLite     │ │  OpenAI  │ │  ChromaDB  │ │  Sentence      │
│   Database   │ │  API     │ │  Vectors   │ │  Transformers  │
└──────────────┘ └──────────┘ └────────────┘ └────────────────┘
```

## Data Flow: Saving Content

```
User Input (URL/Note/Paste/File)
        │
        ▼
Content Extractor (BeautifulSoup / pdfplumber)
        │
        ▼
AI Summary Engine (OpenAI / Local Fallback)
        │
        ├── Short Summary
        ├── Detailed Summary
        ├── Key Insights
        └── Actionable Takeaways
        │
        ▼
Tag Generator (Topic, Category, Intent, Learning)
        │
        ▼
Embedding Generator (Sentence Transformers)
        │
        ▼
Storage: SQLite + ChromaDB
        │
        ▼
Auto-Collection Assignment
```

## Data Flow: Semantic Search

```
Natural Language Query
        │
        ▼
Query Embedding (Sentence Transformers)
        │
        ▼
ChromaDB Cosine Similarity Search
        │
        ▼
Ranked Results (with similarity scores)
        │
        ▼
Return matching bookmarks from SQLite
```

## Data Flow: RAG Chat

```
User Question
        │
        ▼
Semantic Search (top 5 bookmarks)
        │
        ▼
Context Assembly (summaries + excerpts)
        │
        ▼
LLM Generation (OpenAI / Local Fallback)
        │
        ▼
Answer + Source Citations
```

## Database Schema

See [DATABASE.md](./DATABASE.md) for full schema documentation.

## Key Technologies

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Backend | FastAPI | REST API + page serving |
| Database | SQLite + SQLAlchemy | Relational data storage |
| Vectors | ChromaDB | Embedding storage & search |
| Embeddings | Sentence Transformers | Local vector generation |
| AI | OpenAI GPT-4o-mini | Summaries, tags, chat |
| Frontend | HTML/CSS/JS | Responsive UI with dark/light mode |

## Security

- Passwords hashed with bcrypt via passlib
- Session-based authentication with signed cookies
- User data isolation (all queries scoped by user_id)
- File upload type validation

## Scalability Notes

For production deployment:
- Replace SQLite with PostgreSQL
- Use Redis for session storage
- Deploy ChromaDB as a separate service
- Add Celery for async AI processing
- Implement rate limiting on AI endpoints
