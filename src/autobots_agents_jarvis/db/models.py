# ABOUTME: SQLAlchemy ORM model for the jarvis context store table.
# ABOUTME: Stores typed context fields (user_name, repo_name, jira_number) keyed by context_key.

from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class JarvisContextEntity(Base):
    """Persistent store for jarvis agent context data.

    Each row holds the typed context fields for one context_key.
    """

    __tablename__ = "jarvis_context_store"

    context_key: Mapped[str] = mapped_column(String(512), primary_key=True)
    user_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    repo_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    jira_number: Mapped[str | None] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )
