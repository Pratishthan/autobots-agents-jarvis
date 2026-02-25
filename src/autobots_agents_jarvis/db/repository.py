# ABOUTME: DbRepository implementation backed by SQLAlchemy / PostgreSQL.
# ABOUTME: Implements the shared-lib DbRepository Protocol for the jarvis context store.

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from autobots_agents_jarvis.db.models import JarvisContextEntity

if TYPE_CHECKING:
    from collections.abc import Mapping

    from sqlalchemy.orm import Session, sessionmaker


class JarvisContextRepository:
    """Implements the shared-lib DbRepository Protocol using SQLAlchemy.

    Each public method opens a short-lived session, commits on success,
    and rolls back on any exception.
    """

    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory

    def get(self, context_key: str) -> dict[str, Any] | None:
        """Return the stored context for *context_key*, or ``None`` if not found."""
        with self._session_factory() as session:
            entity = session.get(JarvisContextEntity, context_key)
            if entity is None:
                return None
            return {
                k: v
                for k, v in {
                    "user_name": entity.user_name,
                    "repo_name": entity.repo_name,
                    "jira_number": entity.jira_number,
                }.items()
                if v is not None
            }

    def set(self, context_key: str, data: Mapping[str, Any]) -> None:
        """Upsert the context for *context_key*.

        Only the three known fields are persisted; unknown keys are silently
        ignored. ``user_id`` is accepted as an alias for ``user_name``.
        """
        user_name = data.get("user_name") or data.get("user_id")
        repo_name = data.get("repo_name")
        jira_number = data.get("jira_number")
        with self._session_factory() as session:
            try:
                entity = session.get(JarvisContextEntity, context_key)
                if entity is None:
                    entity = JarvisContextEntity(
                        context_key=context_key,
                        user_name=user_name,
                        repo_name=repo_name,
                        jira_number=jira_number,
                    )
                    session.add(entity)
                else:
                    entity.user_name = user_name
                    entity.repo_name = repo_name
                    entity.jira_number = jira_number
                session.commit()
            except Exception:
                session.rollback()
                raise

    def delete(self, context_key: str) -> None:
        """Remove the context for *context_key* (no-op if not found)."""
        with self._session_factory() as session:
            try:
                entity = session.get(JarvisContextEntity, context_key)
                if entity is not None:
                    session.delete(entity)
                    session.commit()
            except Exception:
                session.rollback()
                raise
