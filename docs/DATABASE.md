# Database Schema

## Entity Relationship Diagram

```
users ──────────< bookmarks >────────── tags
  │                  │                     │
  │                  │                     │
  │            bookmark_tags               │
  │                  │                     │
  │                  ▼                     │
  │            collections >── collection_bookmarks
  │
  └──────────< search_history
  │
  └──────────< chat_messages
```

## Tables

### users
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | Auto-increment ID |
| email | VARCHAR(255) UNIQUE | User email |
| username | VARCHAR(100) UNIQUE | Display name |
| hashed_password | VARCHAR(255) | bcrypt hash |
| created_at | DATETIME | Registration date |
| last_login | DATETIME | Last login timestamp |

### bookmarks
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | Auto-increment ID |
| user_id | INTEGER FK | Owner reference |
| title | VARCHAR(500) | Content title |
| source_url | VARCHAR(2000) | Original URL |
| source_type | VARCHAR(50) | url, note, paste, pdf, txt, md |
| original_content | TEXT | Full extracted content |
| short_summary | TEXT | 2-3 line AI summary |
| detailed_summary | TEXT | Paragraph summary |
| key_insights | TEXT | JSON array of insights |
| actionable_takeaways | TEXT | JSON array of takeaways |
| metadata_json | TEXT | JSON metadata |
| reading_time_minutes | INTEGER | Estimated read time |
| word_count | INTEGER | Word count |
| is_favorite | BOOLEAN | Favorite flag |
| view_count | INTEGER | View counter |
| time_spent_seconds | INTEGER | Time spent reading |
| created_at | DATETIME | Save timestamp |
| updated_at | DATETIME | Last update |

### tags
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | Auto-increment ID |
| user_id | INTEGER FK | Owner reference |
| name | VARCHAR(100) | Tag name |
| tag_type | VARCHAR(50) | topic, category, intent, learning |
| is_auto_generated | BOOLEAN | AI vs manual tag |

### bookmark_tags (junction)
| Column | Type | Description |
|--------|------|-------------|
| bookmark_id | INTEGER FK | Bookmark reference |
| tag_id | INTEGER FK | Tag reference |

### collections
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | Auto-increment ID |
| user_id | INTEGER FK | Owner reference |
| name | VARCHAR(200) | Collection name |
| description | TEXT | Description |
| is_auto_generated | BOOLEAN | Auto vs manual |
| icon | VARCHAR(50) | Icon identifier |
| color | VARCHAR(20) | Hex color code |
| created_at | DATETIME | Creation date |

### collection_bookmarks (junction)
| Column | Type | Description |
|--------|------|-------------|
| collection_id | INTEGER FK | Collection reference |
| bookmark_id | INTEGER FK | Bookmark reference |

### search_history
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | Auto-increment ID |
| user_id | INTEGER FK | Owner reference |
| query | VARCHAR(500) | Search query text |
| results_count | INTEGER | Number of results |
| search_type | VARCHAR(50) | semantic or keyword |
| created_at | DATETIME | Search timestamp |

### chat_messages
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | Auto-increment ID |
| user_id | INTEGER FK | Owner reference |
| role | VARCHAR(20) | user or assistant |
| content | TEXT | Message content |
| bookmark_ids | TEXT | JSON referenced bookmark IDs |
| created_at | DATETIME | Message timestamp |

## Vector Store (ChromaDB)

Embeddings stored separately in ChromaDB with:
- **Collection**: `bookmarks`
- **Document ID**: `user_{user_id}_bookmark_{bookmark_id}`
- **Metadata**: `{user_id, bookmark_id}`
- **Space**: cosine similarity
- **Model**: all-MiniLM-L6-v2 (384 dimensions)
