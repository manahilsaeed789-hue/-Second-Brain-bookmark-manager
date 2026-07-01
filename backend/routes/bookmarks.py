"""Bookmark CRUD API routes."""

import shutil
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from backend.auth import get_current_user
from backend.config import get_settings
from backend.database import get_db
from backend.models import User
from backend.schemas import (
    BookmarkCreateNote,
    BookmarkCreatePaste,
    BookmarkCreateURL,
    BookmarkDetailResponse,
    BookmarkResponse,
    TagUpdate,
)
from backend.services import bookmark_service, clustering_service, embedding_service

router = APIRouter(prefix="/api/bookmarks", tags=["Bookmarks"])
settings = get_settings()


@router.get("", response_model=list[BookmarkResponse])
async def list_bookmarks(
    limit: int = 50,
    offset: int = 0,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    bookmarks = bookmark_service.list_bookmarks(db, user.id, limit, offset)
    return [BookmarkResponse.from_orm_bookmark(b) for b in bookmarks]


@router.get("/{bookmark_id}", response_model=BookmarkDetailResponse)
async def get_bookmark(
    bookmark_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    import json

    bookmark = bookmark_service.get_bookmark(db, bookmark_id, user.id)
    if not bookmark:
        raise HTTPException(status_code=404, detail="Bookmark not found")

    bookmark.view_count += 1
    db.commit()

    # Find similar bookmarks
    similar_results = embedding_service.find_similar_bookmarks(
        bookmark.id, user.id,
        bookmark.title, bookmark.original_content or "",
        bookmark.short_summary or "",
    )
    similar_bookmarks = []
    for r in similar_results:
        sim = bookmark_service.get_bookmark(db, r["bookmark_id"], user.id)
        if sim:
            similar_bookmarks.append(BookmarkResponse.from_orm_bookmark(sim))

    metadata = {}
    if bookmark.metadata_json:
        try:
            metadata = json.loads(bookmark.metadata_json)
        except json.JSONDecodeError:
            pass

    base = BookmarkResponse.from_orm_bookmark(bookmark)
    return BookmarkDetailResponse(
        **base.model_dump(),
        original_content=bookmark.original_content,
        metadata_json=metadata,
        similar_bookmarks=similar_bookmarks,
        collections=[c.name for c in bookmark.collections],
    )


@router.post("/url", response_model=BookmarkResponse)
async def save_url(
    data: BookmarkCreateURL,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    dup = clustering_service.detect_duplicates(db, user.id, data.url, data.url)
    if dup["is_duplicate"]:
        raise HTTPException(status_code=409, detail="Similar content already saved")

    bookmark = await bookmark_service.create_from_url(db, user.id, data.url, data.notes)
    return BookmarkResponse.from_orm_bookmark(bookmark)


@router.post("/note", response_model=BookmarkResponse)
async def save_note(
    data: BookmarkCreateNote,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    bookmark = await bookmark_service.create_from_note(
        db, user.id, data.title, data.content, data.source_url
    )
    return BookmarkResponse.from_orm_bookmark(bookmark)


@router.post("/paste", response_model=BookmarkResponse)
async def save_paste(
    data: BookmarkCreatePaste,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    bookmark = await bookmark_service.create_from_paste(
        db, user.id, data.content, data.title, data.source_url
    )
    return BookmarkResponse.from_orm_bookmark(bookmark)


@router.post("/upload", response_model=BookmarkResponse)
async def upload_file(
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    allowed = {".pdf", ".txt", ".md", ".markdown"}
    ext = Path(file.filename or "").suffix.lower()
    if ext not in allowed:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {ext}")

    settings.uploads_dir.mkdir(parents=True, exist_ok=True)
    filename = f"{uuid.uuid4()}{ext}"
    file_path = settings.uploads_dir / filename

    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    source_type = "pdf" if ext == ".pdf" else ("md" if ext in {".md", ".markdown"} else "txt")
    bookmark = await bookmark_service.create_from_file(db, user.id, str(file_path), source_type)
    return BookmarkResponse.from_orm_bookmark(bookmark)


@router.put("/{bookmark_id}/tags", response_model=BookmarkResponse)
async def update_tags(
    bookmark_id: int,
    data: TagUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    bookmark = bookmark_service.get_bookmark(db, bookmark_id, user.id)
    if not bookmark:
        raise HTTPException(status_code=404, detail="Bookmark not found")

    bookmark_service.update_bookmark_tags(db, bookmark, data.tags)
    db.refresh(bookmark)
    return BookmarkResponse.from_orm_bookmark(bookmark)


@router.put("/{bookmark_id}/favorite")
async def toggle_favorite(
    bookmark_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    bookmark = bookmark_service.get_bookmark(db, bookmark_id, user.id)
    if not bookmark:
        raise HTTPException(status_code=404, detail="Bookmark not found")

    bookmark.is_favorite = not bookmark.is_favorite
    db.commit()
    return {"is_favorite": bookmark.is_favorite}


@router.delete("/{bookmark_id}")
async def delete_bookmark(
    bookmark_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    bookmark = bookmark_service.get_bookmark(db, bookmark_id, user.id)
    if not bookmark:
        raise HTTPException(status_code=404, detail="Bookmark not found")

    bookmark_service.delete_bookmark(db, bookmark)
    return {"message": "Bookmark deleted"}
