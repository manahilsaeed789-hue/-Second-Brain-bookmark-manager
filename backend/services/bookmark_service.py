"""Business logic for bookmark CRUD, collections, and analytics."""

import json
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy import desc, func
from sqlalchemy.orm import Session

from backend.models import Bookmark, Collection, SearchHistory, Tag, User
from backend.schemas import BookmarkResponse, CollectionResponse
from backend.services import ai_service, content_extractor, embedding_service


# ── Tag helpers ───────────────────────────────────────────────────────────────

def get_or_create_tag(db: Session, user_id: int, name: str, tag_type: str, auto: bool = True) -> Tag:
    tag = (
        db.query(Tag)
        .filter(Tag.user_id == user_id, Tag.name == name, Tag.tag_type == tag_type)
        .first()
    )
    if not tag:
        tag = Tag(user_id=user_id, name=name, tag_type=tag_type, is_auto_generated=auto)
        db.add(tag)
        db.flush()
    return tag


def apply_tags(db: Session, bookmark: Bookmark, tags_dict: dict) -> None:
    """Apply auto-generated tags to a bookmark."""
    bookmark.tags.clear()
    type_map = {
        "topic": "topic",
        "category": "category",
        "intent": "intent",
        "learning": "learning",
    }
    for key, tag_type in type_map.items():
        for name in tags_dict.get(key, []):
            if name and isinstance(name, str):
                tag = get_or_create_tag(db, bookmark.user_id, name.strip(), tag_type)
                if tag not in bookmark.tags:
                    bookmark.tags.append(tag)


def update_bookmark_tags(db: Session, bookmark: Bookmark, tag_names: list[str]) -> None:
    """Replace bookmark tags with user-provided custom tags."""
    bookmark.tags.clear()
    for name in tag_names:
        name = name.strip()
        if name:
            tag = get_or_create_tag(db, bookmark.user_id, name, "topic", auto=False)
            bookmark.tags.append(tag)
    db.commit()


# ── Collection helpers ────────────────────────────────────────────────────────

DEFAULT_COLLECTIONS = [
    {"name": "Research", "icon": "microscope", "color": "#8b5cf6", "keywords": ["research", "study", "paper"]},
    {"name": "Career", "icon": "briefcase", "color": "#f59e0b", "keywords": ["career", "job", "interview"]},
    {"name": "Tutorials", "icon": "book-open", "color": "#10b981", "keywords": ["tutorial", "how to", "guide", "learn"]},
    {"name": "Exams", "icon": "graduation-cap", "color": "#ef4444", "keywords": ["exam", "test", "certification"]},
    {"name": "Personal Growth", "icon": "sparkles", "color": "#ec4899", "keywords": ["growth", "productivity", "habit", "mindset"]},
]


def ensure_default_collections(db: Session, user_id: int) -> None:
    for coll_def in DEFAULT_COLLECTIONS:
        existing = (
            db.query(Collection)
            .filter(Collection.user_id == user_id, Collection.name == coll_def["name"])
            .first()
        )
        if not existing:
            db.add(Collection(
                user_id=user_id,
                name=coll_def["name"],
                description=f"Auto-grouped {coll_def['name'].lower()} content",
                icon=coll_def["icon"],
                color=coll_def["color"],
                is_auto_generated=True,
            ))
    db.commit()


def auto_assign_collections(db: Session, bookmark: Bookmark) -> None:
    """Assign bookmark to matching auto-collections based on tags and content."""
    text = f"{bookmark.title} {bookmark.original_content or ''}".lower()
    tag_names = [t.name.lower() for t in bookmark.tags]

    for coll_def in DEFAULT_COLLECTIONS:
        collection = (
            db.query(Collection)
            .filter(Collection.user_id == bookmark.user_id, Collection.name == coll_def["name"])
            .first()
        )
        if not collection:
            continue

        matched = any(kw in text for kw in coll_def["keywords"]) or any(
            any(kw in tag for kw in coll_def["keywords"]) for tag in tag_names
        )
        if matched and bookmark not in collection.bookmarks:
            collection.bookmarks.append(bookmark)
        elif not matched and bookmark in collection.bookmarks:
            collection.bookmarks.remove(bookmark)

    db.commit()


# ── Bookmark creation pipeline ────────────────────────────────────────────────

async def create_bookmark_from_content(
    db: Session,
    user_id: int,
    title: str,
    content: str,
    source_type: str,
    source_url: Optional[str] = None,
    metadata: Optional[dict] = None,
) -> Bookmark:
    """Full pipeline: summarize, tag, embed, and store a bookmark."""
    ensure_default_collections(db, user_id)

    # AI processing
    summary_data = await ai_service.generate_summary(title, content)
    tags_data = await ai_service.generate_tags(title, content)

    bookmark = Bookmark(
        user_id=user_id,
        title=title,
        source_url=source_url,
        source_type=source_type,
        original_content=content,
        short_summary=summary_data["short_summary"],
        detailed_summary=summary_data["detailed_summary"],
        key_insights=json.dumps(summary_data["key_insights"]),
        actionable_takeaways=json.dumps(summary_data["actionable_takeaways"]),
        metadata_json=json.dumps(metadata or {}),
        reading_time_minutes=content_extractor.estimate_reading_time(content),
        word_count=content_extractor.count_words(content),
    )
    db.add(bookmark)
    db.flush()

    apply_tags(db, bookmark, tags_data)
    auto_assign_collections(db, bookmark)

    # Generate embedding
    tag_names = [t.name for t in bookmark.tags]
    embedding_service.add_bookmark_embedding(
        bookmark.id, user_id, title, content,
        summary=summary_data["short_summary"],
        tags=tag_names,
    )

    db.commit()
    db.refresh(bookmark)
    return bookmark


async def create_from_url(db: Session, user_id: int, url: str, notes: Optional[str] = None) -> Bookmark:
    extracted = content_extractor.extract_from_url(url)
    content = extracted["content"]
    if notes:
        content += f"\n\n--- User Notes ---\n{notes}"
    return await create_bookmark_from_content(
        db, user_id, extracted["title"], content, "url", url, extracted["metadata"]
    )


async def create_from_note(db: Session, user_id: int, title: str, content: str, source_url: Optional[str] = None) -> Bookmark:
    extracted = content_extractor.extract_from_note(title, content)
    return await create_bookmark_from_content(
        db, user_id, extracted["title"], extracted["content"], "note", source_url, extracted["metadata"]
    )


async def create_from_paste(db: Session, user_id: int, content: str, title: Optional[str] = None, source_url: Optional[str] = None) -> Bookmark:
    extracted = content_extractor.extract_from_paste(content, title)
    return await create_bookmark_from_content(
        db, user_id, extracted["title"], extracted["content"], "paste", source_url, extracted["metadata"]
    )


async def create_from_file(db: Session, user_id: int, file_path: str, source_type: str) -> Bookmark:
    if source_type == "pdf":
        extracted = content_extractor.extract_from_pdf(file_path)
    else:
        extracted = content_extractor.extract_from_text_file(file_path)
    return await create_bookmark_from_content(
        db, user_id, extracted["title"], extracted["content"], source_type, None, extracted["metadata"]
    )


def delete_bookmark(db: Session, bookmark: Bookmark) -> None:
    embedding_service.delete_bookmark_embedding(bookmark.id, bookmark.user_id)
    db.delete(bookmark)
    db.commit()


def get_bookmark(db: Session, bookmark_id: int, user_id: int) -> Optional[Bookmark]:
    return (
        db.query(Bookmark)
        .filter(Bookmark.id == bookmark_id, Bookmark.user_id == user_id)
        .first()
    )


def list_bookmarks(db: Session, user_id: int, limit: int = 50, offset: int = 0) -> list[Bookmark]:
    return (
        db.query(Bookmark)
        .filter(Bookmark.user_id == user_id)
        .order_by(desc(Bookmark.created_at))
        .offset(offset)
        .limit(limit)
        .all()
    )


def record_search(db: Session, user_id: int, query: str, results_count: int) -> None:
    db.add(SearchHistory(user_id=user_id, query=query, results_count=results_count))
    db.commit()


# ── Dashboard ─────────────────────────────────────────────────────────────────

def get_dashboard_stats(db: Session, user_id: int) -> dict:
    bookmarks = db.query(Bookmark).filter(Bookmark.user_id == user_id).all()
    total = len(bookmarks)
    total_reading = sum(b.reading_time_minutes for b in bookmarks)

    categories = (
        db.query(Tag.name, func.count(Tag.id))
        .filter(Tag.user_id == user_id, Tag.tag_type == "category")
        .group_by(Tag.name)
        .order_by(desc(func.count(Tag.id)))
        .limit(10)
        .all()
    )

    recent = list_bookmarks(db, user_id, limit=5)

    # Trending tags (most used in last 30 days)
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    trending = (
        db.query(Tag.name, func.count(bookmark_tags.c.bookmark_id))
        .join(bookmark_tags, Tag.id == bookmark_tags.c.tag_id)
        .join(Bookmark, Bookmark.id == bookmark_tags.c.bookmark_id)
        .filter(Tag.user_id == user_id, Bookmark.created_at >= thirty_days_ago)
        .group_by(Tag.name)
        .order_by(desc(func.count(bookmark_tags.c.bookmark_id)))
        .limit(8)
        .all()
    )

    # Daily rediscovery: random old bookmarks not viewed recently
    rediscovery = (
        db.query(Bookmark)
        .filter(Bookmark.user_id == user_id)
        .order_by(Bookmark.view_count.asc(), func.random())
        .limit(3)
        .all()
    )

    # Recommended revisit: favorites or high reading time, not viewed recently
    revisit = (
        db.query(Bookmark)
        .filter(Bookmark.user_id == user_id)
        .order_by(desc(Bookmark.reading_time_minutes), Bookmark.view_count.asc())
        .limit(3)
        .all()
    )

    # Knowledge map: tag clusters
    tag_counts = (
        db.query(Tag.name, Tag.tag_type, func.count(bookmark_tags.c.bookmark_id))
        .outerjoin(bookmark_tags, Tag.id == bookmark_tags.c.tag_id)
        .filter(Tag.user_id == user_id)
        .group_by(Tag.name, Tag.tag_type)
        .all()
    )
    knowledge_map = [
        {"tag": name, "type": ttype, "count": count}
        for name, ttype, count in tag_counts if count > 0
    ]

    return {
        "total_bookmarks": total,
        "total_categories": len(categories),
        "total_reading_time_minutes": total_reading,
        "recent_bookmarks": [BookmarkResponse.from_orm_bookmark(b) for b in recent],
        "trending_tags": [{"name": n, "count": c} for n, c in trending],
        "daily_rediscovery": [BookmarkResponse.from_orm_bookmark(b) for b in rediscovery],
        "recommended_revisit": [BookmarkResponse.from_orm_bookmark(b) for b in revisit],
        "knowledge_map": knowledge_map,
    }


# ── Analytics ─────────────────────────────────────────────────────────────────

def get_analytics(db: Session, user_id: int) -> dict:
    # Most searched topics
    searches = (
        db.query(SearchHistory.query, func.count(SearchHistory.id))
        .filter(SearchHistory.user_id == user_id)
        .group_by(SearchHistory.query)
        .order_by(desc(func.count(SearchHistory.id)))
        .limit(10)
        .all()
    )

    # Most saved category
    top_category = (
        db.query(Tag.name, func.count(bookmark_tags.c.bookmark_id))
        .join(bookmark_tags, Tag.id == bookmark_tags.c.tag_id)
        .filter(Tag.user_id == user_id, Tag.tag_type == "category")
        .group_by(Tag.name)
        .order_by(desc(func.count(bookmark_tags.c.bookmark_id)))
        .first()
    )

    # Time spent
    total_seconds = (
        db.query(func.sum(Bookmark.time_spent_seconds))
        .filter(Bookmark.user_id == user_id)
        .scalar() or 0
    )

    # Saves by week (last 8 weeks)
    eight_weeks_ago = datetime.utcnow() - timedelta(weeks=8)
    bookmarks = (
        db.query(Bookmark)
        .filter(Bookmark.user_id == user_id, Bookmark.created_at >= eight_weeks_ago)
        .all()
    )
    weekly: dict[str, int] = {}
    for b in bookmarks:
        week_key = b.created_at.strftime("%Y-W%W")
        weekly[week_key] = weekly.get(week_key, 0) + 1

    # Tag distribution
    tag_dist = (
        db.query(Tag.tag_type, func.count(Tag.id))
        .filter(Tag.user_id == user_id)
        .group_by(Tag.tag_type)
        .all()
    )

    total_bookmarks = db.query(Bookmark).filter(Bookmark.user_id == user_id).count()
    weekly_insights = _generate_weekly_insights(db, user_id, total_bookmarks, searches)

    return {
        "most_searched_topics": [{"query": q, "count": c} for q, c in searches],
        "most_saved_category": top_category[0] if top_category else None,
        "total_time_spent_hours": round(total_seconds / 3600, 1),
        "weekly_insights": weekly_insights,
        "saves_by_week": [{"week": k, "count": v} for k, v in sorted(weekly.items())],
        "tags_distribution": [{"type": t, "count": c} for t, c in tag_dist],
    }


def _generate_weekly_insights(db: Session, user_id: int, total: int, searches: list) -> list[str]:
    insights = []
    week_ago = datetime.utcnow() - timedelta(days=7)
    recent_count = (
        db.query(Bookmark)
        .filter(Bookmark.user_id == user_id, Bookmark.created_at >= week_ago)
        .count()
    )
    if recent_count > 0:
        insights.append(f"You saved {recent_count} new items this week — great momentum!")
    if total > 10:
        insights.append(f"Your knowledge base has grown to {total} bookmarks.")
    if searches:
        insights.append(f"Your top search: \"{searches[0][0]}\" — you're actively exploring your saves.")
    if not insights:
        insights.append("Start saving content to build your second brain!")
    return insights


# ── Collections listing ───────────────────────────────────────────────────────

def get_collections(db: Session, user_id: int) -> list[CollectionResponse]:
    collections = db.query(Collection).filter(Collection.user_id == user_id).all()
    result = []
    for c in collections:
        resp = CollectionResponse(
            id=c.id,
            name=c.name,
            description=c.description,
            icon=c.icon,
            color=c.color,
            is_auto_generated=c.is_auto_generated,
            bookmark_count=len(c.bookmarks),
        )
        result.append(resp)
    return result


# Import bookmark_tags for queries
from backend.models import bookmark_tags  # noqa: E402
