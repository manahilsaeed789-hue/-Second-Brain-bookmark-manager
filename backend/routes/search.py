"""Semantic search API routes."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.auth import get_current_user
from backend.database import get_db
from backend.models import User
from backend.schemas import BookmarkResponse, SearchRequest, SearchResponse, SearchResult
from backend.services import bookmark_service, embedding_service

router = APIRouter(prefix="/api/search", tags=["Search"])


@router.post("", response_model=SearchResponse)
async def semantic_search(
    data: SearchRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    results = embedding_service.semantic_search(data.query, user.id, limit=data.limit)

    search_results = []
    for r in results:
        bookmark = bookmark_service.get_bookmark(db, r["bookmark_id"], user.id)
        if bookmark:
            search_results.append(SearchResult(
                bookmark=BookmarkResponse.from_orm_bookmark(bookmark),
                similarity_score=r["similarity_score"],
            ))

    bookmark_service.record_search(db, user.id, data.query, len(search_results))

    return SearchResponse(query=data.query, results=search_results, total=len(search_results))
