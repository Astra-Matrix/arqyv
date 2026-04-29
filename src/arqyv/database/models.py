"""SQLAlchemy ORM models for the ARQYV media library."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class MediaFile(Base):
    """Core record for every indexed file."""

    __tablename__ = "media_files"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    path: Mapped[str] = mapped_column(String(4096), unique=True, nullable=False, index=True)
    filename: Mapped[str] = mapped_column(String(512), nullable=False)
    extension: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    size_bytes: Mapped[int] = mapped_column(BigInteger, default=0)
    mime_type: Mapped[str | None] = mapped_column(String(128))

    # File system timestamps
    fs_created_at: Mapped[datetime | None] = mapped_column(DateTime)
    fs_modified_at: Mapped[datetime | None] = mapped_column(DateTime)

    # DB record timestamps
    indexed_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Media-specific
    duration_seconds: Mapped[float | None] = mapped_column(Float)
    width: Mapped[int | None] = mapped_column(Integer)
    height: Mapped[int | None] = mapped_column(Integer)
    fps: Mapped[float | None] = mapped_column(Float)
    bit_rate: Mapped[int | None] = mapped_column(Integer)
    video_codec: Mapped[str | None] = mapped_column(String(64))
    audio_codec: Mapped[str | None] = mapped_column(String(64))

    # AI-generated
    ai_tags: Mapped[str | None] = mapped_column(Text)         # JSON array
    ai_summary: Mapped[str | None] = mapped_column(Text)
    ai_transcript: Mapped[str | None] = mapped_column(Text)
    ai_analyzed: Mapped[bool] = mapped_column(Boolean, default=False)

    # Thumbnail
    thumbnail_path: Mapped[str | None] = mapped_column(String(4096))

    # Cloud sync
    cloud_provider: Mapped[str | None] = mapped_column(String(32))
    cloud_id: Mapped[str | None] = mapped_column(String(256))

    # Relationships
    tags: Mapped[list["Tag"]] = relationship(
        "Tag", secondary="file_tags", back_populates="files", lazy="selectin"
    )

    def get_tags(self) -> list[str]:
        if self.ai_tags:
            try:
                return json.loads(self.ai_tags)
            except json.JSONDecodeError:
                return []
        return []

    def set_tags(self, tags: list[str]) -> None:
        self.ai_tags = json.dumps(tags)

    def __repr__(self) -> str:
        return f"<MediaFile id={self.id} path={self.path!r}>"


class Tag(Base):
    """Reusable tag entity."""

    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(256), unique=True, nullable=False, index=True)
    color: Mapped[str | None] = mapped_column(String(16))  # hex color

    files: Mapped[list[MediaFile]] = relationship(
        "MediaFile", secondary="file_tags", back_populates="tags"
    )


class FileTag(Base):
    """Association table: MediaFile ↔ Tag (many-to-many)."""

    __tablename__ = "file_tags"

    file_id: Mapped[int] = mapped_column(ForeignKey("media_files.id", ondelete="CASCADE"), primary_key=True)
    tag_id: Mapped[int] = mapped_column(ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True)


class WatchedFolder(Base):
    """Directory paths registered for auto-indexing."""

    __tablename__ = "watched_folders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    path: Mapped[str] = mapped_column(String(4096), unique=True, nullable=False)
    recursive: Mapped[bool] = mapped_column(Boolean, default=True)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    added_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class SearchHistory(Base):
    """Tracks recent user searches for autocomplete / analytics."""

    __tablename__ = "search_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    query: Mapped[str] = mapped_column(String(1024), nullable=False)
    result_count: Mapped[int] = mapped_column(Integer, default=0)
    searched_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
