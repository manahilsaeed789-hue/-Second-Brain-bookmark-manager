"""Pydantic schemas for request/response validation."""

import json
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


# ── Auth ──────────────────────────────────────────────────────────────────────

class UserRegister(BaseModel):
    email: EmailStr
    username: str = Field(min_length=3, max_length=100)
    password: str = Field(min_length=6, max_length=128)


class UserLogin(BaseModel):
    email: EmailStr
    password: str
    remember_me: bool = False


class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Tags ──────────────────────────────────────────────────────────────────────

class TagResponse(BaseModel):
    id: int
    name: str
    tag_type: str
    is_auto_generated: bool

    model_config = {"from_attributes": True}


class TagUpdate(BaseModel):
    tags: list[str]


# ── Bookmarks ─────────────────────────────────────────────────────────────────

class BookmarkCreateURL(BaseModel):
    url: str
    notes: Optional[str] = None


class BookmarkCreateNote(BaseModel):
    title: str
    content: str
    source_url: Optional[str] = None


class BookmarkCreatePaste(BaseModel):
    title: Optional[str] = None
    content: str
    source_url: Optional[str] = None


class BookmarkResponse(BaseModel):
    id: int
    title: str
    source_url: Optional[str]
    source_type: str
    short_summary: Optional[str]
    detailed_summary: Optional[str]
    key_insights: Optional[list[str]] = None
    actionable_takeaways: Optional[list[str]] = None
    reading_time_minutes: int
    word_count: int
    is_favorite: bool
    view_count: int
    tags: list[TagResponse] = []
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}

    @classmethod
    def from_orm_bookmark(cls, bookmark) -> "BookmarkResponse":
        insights = []
        takeaways = []
        if bookmark.key_insights:
            try:
                insights = json.loads(bookmark.key_insights)
            except json.JSONDecodeError:
                insights = [bookmark.key_insights]
        if bookmark.actionable_takeaways:
            try:
                takeaways = json.loads(bookmark.actionable_takeaways)
            except json.JSONDecodeError:
                takeaways = [bookmark.actionable_takeaways]
        return cls(
            id=bookmark.id,
            title=bookmark.title,
            source_url=bookmark.source_url,
            source_type=bookmark.source_type,
            short_summary=bookmark.short_summary,
            detailed_summary=bookmark.detailed_summary,
            key_insights=insights,
            actionable_takeaways=takeaways,
            reading_time_minutes=bookmark.reading_time_minutes,
            word_count=bookmark.word_count,
            is_favorite=bookmark.is_favorite,
            view_count=bookmark.view_count,
            tags=[TagResponse.model_validate(t) for t in bookmark.tags],
            created_at=bookmark.created_at,
            updated_at=bookmark.updated_at,
        )


class BookmarkDetailResponse(BookmarkResponse):
    original_content: Optional[str] = None
    metadata_json: Optional[dict] = None
    similar_bookmarks: list[BookmarkResponse] = []
    collections: list[str] = []


# ── Search ────────────────────────────────────────────────────────────────────

class SearchRequest(BaseModel):
    query: str = Field(min_length=1, max_length=500)
    limit: int = Field(default=10, ge=1, le=50)


class SearchResult(BaseModel):
    bookmark: BookmarkResponse
    similarity_score: float


class SearchResponse(BaseModel):
    query: str
    results: list[SearchResult]
    total: int


# ── Collections ───────────────────────────────────────────────────────────────

class CollectionResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    icon: str
    color: str
    is_auto_generated: bool
    bookmark_count: int = 0

    model_config = {"from_attributes": True}


# ── Dashboard ─────────────────────────────────────────────────────────────────

class DashboardStats(BaseModel):
    total_bookmarks: int
    total_categories: int
    total_reading_time_minutes: int
    recent_bookmarks: list[BookmarkResponse]
    trending_tags: list[dict]
    daily_rediscovery: list[BookmarkResponse]
    recommended_revisit: list[BookmarkResponse]
    knowledge_map: list[dict]


# ── Analytics ─────────────────────────────────────────────────────────────────

class AnalyticsResponse(BaseModel):
    most_searched_topics: list[dict]
    most_saved_category: Optional[str]
    total_time_spent_hours: float
    weekly_insights: list[str]
    saves_by_week: list[dict]
    tags_distribution: list[dict]


# ── Chat ──────────────────────────────────────────────────────────────────────

class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)


class ChatResponse(BaseModel):
    answer: str
    sources: list[BookmarkResponse]


# ── Duplicate detection ───────────────────────────────────────────────────────

class DuplicateCheckResponse(BaseModel):
    is_duplicate: bool
    similar_bookmarks: list[BookmarkResponse]
