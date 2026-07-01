# API Documentation

Base URL: `http://localhost:8000`

All authenticated endpoints require a valid session cookie (set via login).

---

## Authentication

### POST /api/auth/register
Register a new user.

**Body:**
```json
{
  "email": "user@example.com",
  "username": "johndoe",
  "password": "securepassword"
}
```

**Response:** `200` — User object

---

### POST /api/auth/login
Login and create session.

**Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword",
  "remember_me": false
}
```

**Response:** `200` — `{ "message": "Login successful", "user": {...} }`

---

### POST /api/auth/logout
Clear session.

**Response:** `200` — `{ "message": "Logged out successfully" }`

---

### GET /api/auth/me
Get current user info.

**Response:** `200` — User object

---

## Bookmarks

### GET /api/bookmarks
List all bookmarks for the current user.

**Query params:** `limit` (default 50), `offset` (default 0)

**Response:** `200` — Array of bookmark objects

---

### GET /api/bookmarks/{id}
Get bookmark detail with similar content.

**Response:** `200` — Bookmark detail object

---

### POST /api/bookmarks/url
Save content from a URL.

**Body:**
```json
{
  "url": "https://example.com/article",
  "notes": "Optional personal notes"
}
```

---

### POST /api/bookmarks/note
Save a manual note.

**Body:**
```json
{
  "title": "My Note",
  "content": "Note content here...",
  "source_url": null
}
```

---

### POST /api/bookmarks/paste
Save pasted article text.

**Body:**
```json
{
  "title": "Optional title",
  "content": "Pasted article text...",
  "source_url": null
}
```

---

### POST /api/bookmarks/upload
Upload a file (PDF, TXT, MD).

**Form data:** `file` — multipart file upload

---

### PUT /api/bookmarks/{id}/tags
Update bookmark tags.

**Body:**
```json
{
  "tags": ["AI", "Research", "Custom Tag"]
}
```

---

### PUT /api/bookmarks/{id}/favorite
Toggle favorite status.

**Response:** `{ "is_favorite": true/false }`

---

### DELETE /api/bookmarks/{id}
Delete a bookmark.

---

## Search

### POST /api/search
Semantic search across saved bookmarks.

**Body:**
```json
{
  "query": "articles about improving focus",
  "limit": 10
}
```

**Response:**
```json
{
  "query": "...",
  "results": [
    {
      "bookmark": { ... },
      "similarity_score": 0.85
    }
  ],
  "total": 5
}
```

---

## Dashboard & Analytics

### GET /api/dashboard
Dashboard statistics and widgets.

### GET /api/analytics
Usage analytics and insights.

### GET /api/collections
Smart collections with bookmark counts.

### GET /api/clusters
Semantic bookmark clusters.

---

## Chat (RAG)

### POST /api/chat
Ask questions about saved bookmarks.

**Body:**
```json
{
  "message": "What have I saved about machine learning?"
}
```

**Response:**
```json
{
  "answer": "Based on your bookmarks...",
  "sources": [ ... bookmark objects ... ]
}
```

---

## Health

### GET /health
```json
{
  "status": "healthy",
  "app": "Second Brain",
  "version": "1.0.0"
}
```

---

## Interactive Docs

FastAPI auto-generates interactive API docs:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
