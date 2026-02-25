# ABOUTME: DbRepository implementation backed by SQLAlchemy / PostgreSQL.
# ABOUTME: Implements the shared-lib DbRepository Protocol for the jarvis context store.

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from autobots_agents_jarvis.common.db.models import JarvisContextEntity

if TYPE_CHECKING:
    from collections.abc import Mapping

    from sqlalchemy.orm import Session, sessionmaker


class JarvisContextRepository:
    """Implements the shared-lib DbRepository Protocol using SQLAlchemy.

    Each public method opens a short-lived session, commits on success,
    and rolls back on any exception. When *prefix* is set, the same prefix
    is applied to the storage key so DB keys align with CacheBackedContextStore
    (e.g. cache and DB both use ``{prefix}_{context_key}``).
    """

    def __init__(
        self,
        session_factory: sessionmaker[Session],
        *,
        prefix: str = "",
    ) -> None:
        self._session_factory = session_factory
        self._prefix = prefix

    def _storage_key(self, context_key: str) -> str:
        """Return the key used in the DB (with prefix when configured)."""
        if not self._prefix:
            return context_key
        return f"{self._prefix}_{context_key}"

    def get(self, context_key: str) -> dict[str, Any] | None:
        """Return the stored context for *context_key*, or ``None`` if not found."""
        key = self._storage_key(context_key)
        with self._session_factory() as session:
            entity = session.get(JarvisContextEntity, key)
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
        key = self._storage_key(context_key)
        with self._session_factory() as session:
            try:
                entity = session.get(JarvisContextEntity, key)
                if entity is None:
                    entity = JarvisContextEntity(
                        context_key=key,
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
        key = self._storage_key(context_key)
        with self._session_factory() as session:
            try:
                entity = session.get(JarvisContextEntity, key)
                if entity is not None:
                    session.delete(entity)
                    session.commit()
            except Exception:
                session.rollback()
                raise
