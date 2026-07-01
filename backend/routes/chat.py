"""RAG chat API routes."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.auth import get_current_user
from backend.database import get_db
from backend.models import User
from backend.schemas import ChatRequest, ChatResponse
from backend.services import rag_service

router = APIRouter(prefix="/api/chat", tags=["Chat"])


@router.post("", response_model=ChatResponse)
async def chat(
    data: ChatRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    result = await rag_service.chat_with_bookmarks(db, user.id, data.message)
    return ChatResponse(**result)
