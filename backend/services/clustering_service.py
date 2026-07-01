"""Semantic clustering and duplicate detection."""

from sqlalchemy.orm import Session

from backend.models import Bookmark
from backend.schemas import BookmarkResponse
from backend.services import embedding_service


def detect_duplicates(
    db: Session,
    user_id: int,
    title: str,
    content: str,
    threshold: float = 0.85,
) -> dict:
    """Check if similar content already exists before saving."""
    results = embedding_service.semantic_search(
        f"{title}\n{content[:2000]}", user_id, limit=3
    )

    similar = []
    is_duplicate = False
    for r in results:
        if r["similarity_score"] >= threshold:
            is_duplicate = True
        if r["similarity_score"] >= 0.7:
            bm = db.query(Bookmark).filter(
                Bookmark.id == r["bookmark_id"], Bookmark.user_id == user_id
            ).first()
            if bm:
                similar.append(BookmarkResponse.from_orm_bookmark(bm))

    return {"is_duplicate": is_duplicate, "similar_bookmarks": similar}


def get_semantic_clusters(db: Session, user_id: int) -> list[dict]:
    """
    Group bookmarks into semantic clusters using tag co-occurrence.
    Returns clusters with name and bookmark IDs.
    """
    bookmarks = db.query(Bookmark).filter(Bookmark.user_id == user_id).all()
    if not bookmarks:
        return []

    # Group by primary category tag
    clusters: dict[str, list] = {}
    for bm in bookmarks:
        category_tags = [t.name for t in bm.tags if t.tag_type == "category"]
        topic_tags = [t.name for t in bm.tags if t.tag_type == "topic"]

        cluster_key = category_tags[0] if category_tags else (topic_tags[0] if topic_tags else "Uncategorized")

        if cluster_key not in clusters:
            clusters[cluster_key] = []
        clusters[cluster_key].append({
            "id": bm.id,
            "title": bm.title,
            "tags": [t.name for t in bm.tags],
        })

    return [
        {"name": name, "bookmarks": items, "count": len(items)}
        for name, items in sorted(clusters.items(), key=lambda x: -len(x[1]))
    ]
