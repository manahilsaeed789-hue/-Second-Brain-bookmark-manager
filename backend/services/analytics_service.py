"""Dashboard and analytics services."""

from collections import Counter
from datetime import datetime, timedelta

from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from backend.models import Bookmark, SearchHistory, Tag
from backend.schemas import BookmarkResponse
from backend.services import embedding_service


def get_dashboard_data(db: Session, user_id: int) -> dict:
    """Build dashboard statistics and AI widgets."""
    bookmarks = (
        db.query(Bookmark)
        .options(joinedload(Bookmark.tags))
        .filter(Bookmark.user_id == user_id)
        .order_by(Bookmark.created_at.desc())
        .all()
    )

    total = len(bookmarks)
    categories = set()
    for b in bookmarks:
        for t in b.tags:
            if t.tag_type == "category":
                categories.add(t.name)

    total_reading = sum(b.reading_time_minutes for b in bookmarks)
    recent = [BookmarkResponse.from_orm_bookmark(b) for b in bookmarks[:5]]

    # Trending tags (last 30 days)
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    recent_bookmarks = [b for b in bookmarks if b.created_at >= thirty_days_ago]
    tag_counter: Counter = Counter()
    for b in recent_bookmarks:
        for t in b.tags:
            tag_counter[t.name] += 1
    trending = [{"tag": tag, "count": count} for tag, count in tag_counter.most_common(8)]

    # Daily rediscovery: random older bookmark
    import random

    old_bookmarks = [b for b in bookmarks if b.created_at < datetime.utcnow() - timedelta(days=7)]
    rediscovery = []
    if old_bookmarks:
        picks = random.sample(old_bookmarks, min(3, len(old_bookmarks)))
        rediscovery = [BookmarkResponse.from_orm_bookmark(b) for b in picks]

    # Recommended revisit: least recently viewed favorites or high-value content
    revisit_candidates = sorted(
        [b for b in bookmarks if b.view_count < 3],
        key=lambda b: b.created_at,
    )[:3]
    recommended = [BookmarkResponse.from_orm_bookmark(b) for b in revisit_candidates]

    # Knowledge map: tag clusters
    knowledge_map = []
    tag_groups: dict[str, list] = {}
    for b in bookmarks:
        for t in b.tags:
            if t.tag_type in ("topic", "category"):
                tag_groups.setdefault(t.name, []).append(b.id)
    for tag_name, ids in sorted(tag_groups.items(), key=lambda x: len(x[1]), reverse=True)[:10]:
        knowledge_map.append({"tag": tag_name, "bookmark_count": len(ids), "bookmark_ids": ids[:5]})

    return {
        "total_bookmarks": total,
        "total_categories": len(categories),
        "total_reading_time_minutes": total_reading,
        "recent_bookmarks": recent,
        "trending_tags": trending,
        "daily_rediscovery": rediscovery,
        "recommended_revisit": recommended,
        "knowledge_map": knowledge_map,
    }


def get_analytics(db: Session, user_id: int) -> dict:
    """Compute user analytics."""
    bookmarks = db.query(Bookmark).filter(Bookmark.user_id == user_id).all()
    searches = (
        db.query(SearchHistory)
        .filter(SearchHistory.user_id == user_id)
        .order_by(SearchHistory.created_at.desc())
        .limit(100)
        .all()
    )

    # Most searched topics
    search_counter: Counter = Counter()
    for s in searches:
        search_counter[s.query.lower()] += 1
    most_searched = [{"query": q, "count": c} for q, c in search_counter.most_common(10)]

    # Most saved category
    category_counter: Counter = Counter()
    for b in bookmarks:
        for t in b.tags:
            if t.tag_type == "category":
                category_counter[t.name] += 1
    most_category = category_counter.most_common(1)[0][0] if category_counter else None

    # Time spent
    total_seconds = sum(b.time_spent_seconds for b in bookmarks)
    total_hours = round(total_seconds / 3600, 1)

    # Saves by week (last 8 weeks)
    saves_by_week = []
    for week in range(7, -1, -1):
        start = datetime.utcnow() - timedelta(weeks=week + 1)
        end = datetime.utcnow() - timedelta(weeks=week)
        count = sum(1 for b in bookmarks if start <= b.created_at < end)
        saves_by_week.append({
            "week": f"W{8 - week}",
            "count": count,
            "label": start.strftime("%b %d"),
        })

    # Tags distribution
    tag_counter: Counter = Counter()
    for b in bookmarks:
        for t in b.tags:
            tag_counter[t.name] += 1
    tags_dist = [{"tag": t, "count": c} for t, c in tag_counter.most_common(15)]

    # Weekly insights
    insights = _generate_weekly_insights(bookmarks, searches, tag_counter)

    return {
        "most_searched_topics": most_searched,
        "most_saved_category": most_category,
        "total_time_spent_hours": total_hours,
        "weekly_insights": insights,
        "saves_by_week": saves_by_week,
        "tags_distribution": tags_dist,
    }


def _generate_weekly_insights(bookmarks, searches, tag_counter) -> list[str]:
    """Generate human-readable weekly insights."""
    insights = []
    week_ago = datetime.utcnow() - timedelta(days=7)
    recent = [b for b in bookmarks if b.created_at >= week_ago]

    if recent:
        insights.append(f"You saved {len(recent)} new items this week — keep building your knowledge base!")
    else:
        insights.append("No new saves this week. Try bookmarking something interesting today.")

    if tag_counter:
        top_tag = tag_counter.most_common(1)[0]
        insights.append(f"Your top interest area is '{top_tag[0]}' with {top_tag[1]} tagged items.")

    unread = [b for b in bookmarks if b.view_count == 0]
    if unread:
        insights.append(f"You have {len(unread)} unread bookmarks waiting for you.")

    if searches:
        insights.append(f"You performed {len(searches)} searches recently — great active learning!")

    total_reading = sum(b.reading_time_minutes for b in bookmarks)
    if total_reading > 60:
        insights.append(f"Your saved content represents ~{total_reading // 60} hours of reading material.")

    return insights[:5]
