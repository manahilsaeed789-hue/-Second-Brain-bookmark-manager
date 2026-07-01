"""RAG-based chat with saved bookmarks."""

import json
from typing import Optional

from sqlalchemy.orm import Session

from backend.config import get_settings
from backend.models import Bookmark, ChatMessage
from backend.schemas import BookmarkResponse
from backend.services import embedding_service

settings = get_settings()


async def chat_with_bookmarks(db: Session, user_id: int, message: str) -> dict:
    """
    RAG pipeline:
    1. Semantic search for relevant bookmarks
    2. Build context from top results
    3. Generate answer using OpenAI or local fallback
    """
    # Retrieve relevant bookmarks
    search_results = embedding_service.semantic_search(message, user_id, limit=5)

    bookmark_ids = [r["bookmark_id"] for r in search_results]
    bookmarks = (
        db.query(Bookmark)
        .filter(Bookmark.id.in_(bookmark_ids), Bookmark.user_id == user_id)
        .all()
    ) if bookmark_ids else []

    # Build context
    context_parts = []
    for bm in bookmarks:
        context_parts.append(
            f"[Bookmark #{bm.id}: {bm.title}]\n"
            f"Summary: {bm.short_summary or 'N/A'}\n"
            f"Content excerpt: {(bm.original_content or '')[:1500]}"
        )
    context = "\n\n---\n\n".join(context_parts) if context_parts else "No relevant bookmarks found."

    # Generate answer
    answer = await _generate_answer(message, context)

    # Save chat history
    db.add(ChatMessage(user_id=user_id, role="user", content=message))
    db.add(ChatMessage(
        user_id=user_id,
        role="assistant",
        content=answer,
        bookmark_ids=json.dumps(bookmark_ids),
    ))
    db.commit()

    return {
        "answer": answer,
        "sources": [BookmarkResponse.from_orm_bookmark(b) for b in bookmarks],
    }


async def _generate_answer(question: str, context: str) -> str:
    if not settings.has_openai:
        return _local_answer(question, context)

    try:
        from langchain_openai import ChatOpenAI
        from langchain_core.messages import HumanMessage, SystemMessage

        llm = ChatOpenAI(
            model=settings.openai_model,
            api_key=settings.openai_api_key,
            temperature=0.4,
        )

        response = await llm.ainvoke([
            SystemMessage(content=(
                "You are a personal knowledge assistant. Answer questions based ONLY on "
                "the user's saved bookmarks provided as context. If the context doesn't "
                "contain relevant information, say so honestly. Cite bookmark titles when relevant."
            )),
            HumanMessage(content=f"Context from saved bookmarks:\n\n{context}\n\nQuestion: {question}"),
        ])
        return response.content
    except Exception:
        return _local_answer(question, context)


def _local_answer(question: str, context: str) -> str:
    if "No relevant bookmarks" in context:
        return (
            "I couldn't find relevant bookmarks for your question. "
            "Try saving more content related to this topic, or rephrase your query."
        )

    lines = context.split("\n")
    titles = [line for line in lines if line.startswith("[Bookmark #")]
    if titles:
        return (
            f"Based on your saved bookmarks, I found relevant content including: "
            f"{', '.join(titles[:3])}. "
            f"Review these bookmarks for detailed information about your question: \"{question}\""
        )
    return f"Here's what I found in your knowledge base related to \"{question}\":\n\n{context[:800]}"
