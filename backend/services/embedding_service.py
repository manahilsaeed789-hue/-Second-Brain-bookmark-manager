"""ChromaDB vector store for semantic search and embeddings."""

from typing import Optional

import chromadb
from chromadb.config import Settings as ChromaSettings

from backend.config import get_settings

settings = get_settings()

_collection_name = "bookmarks"
_client: Optional[chromadb.ClientAPI] = None
_collection = None
_embedder = None


def _get_embedder():
    """Lazy-load sentence-transformers model."""
    global _embedder
    if _embedder is None:
        from sentence_transformers import SentenceTransformer

        _embedder = SentenceTransformer(settings.embedding_model)
    return _embedder


def _get_collection():
    """Get or create the ChromaDB collection."""
    global _client, _collection
    if _collection is None:
        from pathlib import Path

        persist_dir = Path(settings.chroma_persist_dir)
        persist_dir.mkdir(parents=True, exist_ok=True)

        _client = chromadb.PersistentClient(
            path=str(persist_dir),
            settings=ChromaSettings(anonymized_telemetry=False),
        )
        _collection = _client.get_or_create_collection(
            name=_collection_name,
            metadata={"hnsw:space": "cosine"},
        )
    return _collection


def _build_document(title: str, content: str, summary: str = "") -> str:
    """Combine fields into a single embeddable document."""
    parts = [title]
    if summary:
        parts.append(summary)
    if content:
        parts.append(content[:4000])
    return "\n\n".join(parts)


def embed_text(text: str) -> list[float]:
    """Generate embedding vector for text."""
    embedder = _get_embedder()
    return embedder.encode(text, normalize_embeddings=True).tolist()


def add_bookmark_embedding(
    bookmark_id: int,
    user_id: int,
    title: str,
    content: str,
    summary: str = "",
    tags: list[str] | None = None,
) -> None:
    """Store or update a bookmark's embedding in ChromaDB."""
    collection = _get_collection()
    doc_id = f"user_{user_id}_bookmark_{bookmark_id}"
    document = _build_document(title, content, summary)
    if tags:
        document += "\n\nTags: " + ", ".join(tags)

    embedding = embed_text(document)

    # Upsert: delete then add
    try:
        collection.delete(ids=[doc_id])
    except Exception:
        pass

    collection.add(
        ids=[doc_id],
        embeddings=[embedding],
        documents=[document],
        metadatas=[{"user_id": user_id, "bookmark_id": bookmark_id}],
    )


def delete_bookmark_embedding(bookmark_id: int, user_id: int) -> None:
    """Remove a bookmark from the vector store."""
    collection = _get_collection()
    doc_id = f"user_{user_id}_bookmark_{bookmark_id}"
    try:
        collection.delete(ids=[doc_id])
    except Exception:
        pass


def semantic_search(
    query: str,
    user_id: int,
    limit: int = 10,
    exclude_id: int | None = None,
) -> list[dict]:
    """
    Perform semantic search for a user.
    Returns list of {bookmark_id, score, document}.
    """
    collection = _get_collection()

    if collection.count() == 0:
        return []

    query_embedding = embed_text(query)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=min(limit + 5, 50),
        where={"user_id": user_id},
    )

    output = []
    if not results or not results["ids"] or not results["ids"][0]:
        return output

    for i, doc_id in enumerate(results["ids"][0]):
        bookmark_id = results["metadatas"][0][i]["bookmark_id"]
        if exclude_id and bookmark_id == exclude_id:
            continue

        distance = results["distances"][0][i] if results.get("distances") else 0
        # Convert cosine distance to similarity score (0-1)
        similarity = max(0.0, 1.0 - distance)

        output.append({
            "bookmark_id": bookmark_id,
            "similarity_score": round(similarity, 4),
            "document": results["documents"][0][i] if results.get("documents") else "",
        })

        if len(output) >= limit:
            break

    return output


def find_similar_bookmarks(
    bookmark_id: int,
    user_id: int,
    title: str,
    content: str,
    summary: str = "",
    limit: int = 5,
) -> list[dict]:
    """Find bookmarks similar to a given bookmark."""
    query = _build_document(title, content, summary)
    return semantic_search(query, user_id, limit=limit, exclude_id=bookmark_id)
