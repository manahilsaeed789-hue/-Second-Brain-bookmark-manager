"""Smart collection auto-grouping."""

from sqlalchemy.orm import Session

from backend.models import Bookmark, Collection

COLLECTION_RULES = {
    "Research": {
        "keywords": ["research", "study", "paper", "academic", "analysis", "hypothesis"],
        "icon": "microscope",
        "color": "#8b5cf6",
    },
    "Career": {
        "keywords": ["career", "job", "interview", "resume", "salary", "professional"],
        "icon": "briefcase",
        "color": "#f59e0b",
    },
    "Tutorials": {
        "keywords": ["tutorial", "how to", "guide", "step by step", "learn", "course"],
        "icon": "book-open",
        "color": "#10b981",
    },
    "Exams": {
        "keywords": ["exam", "test", "quiz", "certification", "certification"],
        "icon": "graduation-cap",
        "color": "#ef4444",
    },
    "Personal Growth": {
        "keywords": ["productivity", "habit", "mindset", "growth", "focus", "self-improvement"],
        "icon": "sparkles",
        "color": "#ec4899",
    },
    "AI & Tech": {
        "keywords": ["ai", "machine learning", "neural", "programming", "python", "data science"],
        "icon": "cpu",
        "color": "#6366f1",
    },
}


def _get_or_create_collection(db: Session, user_id: int, name: str, config: dict) -> Collection:
    collection = (
        db.query(Collection)
        .filter(Collection.user_id == user_id, Collection.name == name)
        .first()
    )
    if not collection:
        collection = Collection(
            user_id=user_id,
            name=name,
            description=f"Auto-grouped {name.lower()} content",
            is_auto_generated=True,
            icon=config.get("icon", "folder"),
            color=config.get("color", "#6366f1"),
        )
        db.add(collection)
        db.flush()
    return collection


def auto_assign_collections(db: Session, bookmark: Bookmark) -> None:
    """Assign bookmark to matching auto-collections based on content."""
    text = f"{bookmark.title} {bookmark.original_content or ''} {bookmark.short_summary or ''}".lower()
    tag_names = " ".join(t.name.lower() for t in bookmark.tags)

    for collection_name, config in COLLECTION_RULES.items():
        keywords = config["keywords"]
        if any(kw in text or kw in tag_names for kw in keywords):
            collection = _get_or_create_collection(db, bookmark.user_id, collection_name, config)
            if bookmark not in collection.bookmarks:
                collection.bookmarks.append(bookmark)

    db.commit()


def get_user_collections(db: Session, user_id: int) -> list[dict]:
    """Return collections with bookmark counts."""
    collections = db.query(Collection).filter(Collection.user_id == user_id).all()
    result = []
    for col in collections:
        result.append({
            "id": col.id,
            "name": col.name,
            "description": col.description,
            "icon": col.icon,
            "color": col.color,
            "is_auto_generated": col.is_auto_generated,
            "bookmark_count": len(col.bookmarks),
        })
    return sorted(result, key=lambda x: x["bookmark_count"], reverse=True)
