# ABOUTME: SQLModel models for Jarvis context — shared fields in JarvisContextFields.
# ABOUTME: JarvisContextData (Pydantic) and JarvisContextEntity (ORM table) both extend JarvisContextFields.

from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import Column, DateTime, func
from sqlmodel import Field, SQLModel


class JarvisContextFields(SQLModel):
    """User-facing context fields shared between the Pydantic schema and the ORM table."""

    domain_name: str | None = Field(None, description="Active domain (e.g. concierge, sales)")
    user_name: str | None = Field(None, description="Logged-in user identifier")
    repo_name: str | None = Field(None, description="Repository name for the workspace")
    session_id: str | None = Field(None, description="Current session identifier")
    jira_number: str | None = Field(None, description="Jira ticket number for the active work item")


class JarvisContextData(JarvisContextFields):
    """Pure Pydantic view — used as context_cls in make_context_tools(). No table."""


class JarvisContextEntity(JarvisContextFields, table=True):
    """Persistent ORM table — adds infrastructure fields to JarvisContextFields."""

    __tablename__ = "jarvis_context_store"  # pyright: ignore[reportAssignmentType]

    context_key: str = Field(primary_key=True)
    created_at: datetime = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), server_default=func.now(), nullable=False),
    )
    updated_at: datetime = Field(
        default=None,
        sa_column=Column(
            DateTime(timezone=True),
            server_default=func.now(),
            onupdate=lambda: datetime.now(UTC),
            nullable=False,
        ),
    )
