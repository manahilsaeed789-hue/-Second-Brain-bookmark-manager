"""SQLAlchemy ORM models for Second Brain."""

from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Table,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from backend.database import Base

bookmark_tags = Table(
    "bookmark_tags",
    Base.metadata,
    Column("bookmark_id", Integer, ForeignKey("bookmarks.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
)

collection_bookmarks = Table(
    "collection_bookmarks",
    Base.metadata,
    Column("collection_id", Integer, ForeignKey("collections.id", ondelete="CASCADE"), primary_key=True),
    Column("bookmark_id", Integer, ForeignKey("bookmarks.id", ondelete="CASCADE"), primary_key=True),
)


class User(Base):
  __tablename__ = "users"

  id = Column(Integer, primary_key=True, index=True)
  email = Column(String(255), unique=True, index=True, nullable=False)
  username = Column(String(100), unique=True, index=True, nullable=False)
  hashed_password = Column(String(255), nullable=False)
  created_at = Column(DateTime, default=datetime.utcnow)
  last_login = Column(DateTime, nullable=True)

  bookmarks = relationship("Bookmark", back_populates="user", cascade="all, delete-orphan")
  collections = relationship("Collection", back_populates="user", cascade="all, delete-orphan")
  search_history = relationship("SearchHistory", back_populates="user", cascade="all, delete-orphan")


class Bookmark(Base):
  __tablename__ = "bookmarks"

  id = Column(Integer, primary_key=True, index=True)
  user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
  title = Column(String(500), nullable=False)
  source_url = Column(String(2000), nullable=True)
  source_type = Column(String(50), nullable=False, default="url")  # url, note, paste, pdf, txt, md
  original_content = Column(Text, nullable=True)
  short_summary = Column(Text, nullable=True)
  detailed_summary = Column(Text, nullable=True)
  key_insights = Column(Text, nullable=True)  # JSON array as string
  actionable_takeaways = Column(Text, nullable=True)  # JSON array as string
  metadata_json = Column(Text, nullable=True)
  reading_time_minutes = Column(Integer, default=1)
  word_count = Column(Integer, default=0)
  is_favorite = Column(Boolean, default=False)
  view_count = Column(Integer, default=0)
  time_spent_seconds = Column(Integer, default=0)
  created_at = Column(DateTime, default=datetime.utcnow, index=True)
  updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

  user = relationship("User", back_populates="bookmarks")
  tags = relationship("Tag", secondary=bookmark_tags, back_populates="bookmarks")
  collections = relationship("Collection", secondary=collection_bookmarks, back_populates="bookmarks")


class Tag(Base):
  __tablename__ = "tags"
  __table_args__ = (UniqueConstraint("user_id", "name", "tag_type", name="uq_user_tag"),)

  id = Column(Integer, primary_key=True, index=True)
  user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
  name = Column(String(100), nullable=False, index=True)
  tag_type = Column(String(50), nullable=False, default="topic")  # topic, category, intent, learning
  is_auto_generated = Column(Boolean, default=True)

  bookmarks = relationship("Bookmark", secondary=bookmark_tags, back_populates="tags")


class Collection(Base):
  __tablename__ = "collections"
  __table_args__ = (UniqueConstraint("user_id", "name", name="uq_user_collection"),)

  id = Column(Integer, primary_key=True, index=True)
  user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
  name = Column(String(200), nullable=False)
  description = Column(Text, nullable=True)
  is_auto_generated = Column(Boolean, default=True)
  icon = Column(String(50), default="folder")
  color = Column(String(20), default="#6366f1")
  created_at = Column(DateTime, default=datetime.utcnow)

  user = relationship("User", back_populates="collections")
  bookmarks = relationship("Bookmark", secondary=collection_bookmarks, back_populates="collections")


class SearchHistory(Base):
  __tablename__ = "search_history"

  id = Column(Integer, primary_key=True, index=True)
  user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
  query = Column(String(500), nullable=False)
  results_count = Column(Integer, default=0)
  search_type = Column(String(50), default="semantic")  # semantic, keyword
  created_at = Column(DateTime, default=datetime.utcnow, index=True)

  user = relationship("User", back_populates="search_history")


class ChatMessage(Base):
  __tablename__ = "chat_messages"

  id = Column(Integer, primary_key=True, index=True)
  user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
  role = Column(String(20), nullable=False)  # user, assistant
  content = Column(Text, nullable=False)
  bookmark_ids = Column(Text, nullable=True)  # JSON list of referenced bookmark IDs
  created_at = Column(DateTime, default=datetime.utcnow)
