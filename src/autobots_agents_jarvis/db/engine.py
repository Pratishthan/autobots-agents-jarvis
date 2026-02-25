# ABOUTME: SQLAlchemy engine factory for the jarvis agent database.
# ABOUTME: Initialises the engine, creates tables idempotently, and returns a session factory.

from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from autobots_agents_jarvis.db.models import Base

_SESSION_FACTORY: sessionmaker[Session] | None = None


def init_db_engine(database_url: str) -> sessionmaker[Session]:
    """Initialise the SQLAlchemy engine and create all tables (idempotent).

    Args:
        database_url: SQLAlchemy-compatible DSN, e.g.
            ``postgresql+psycopg2://user:pass@host:5432/dbname``.

    Returns:
        A bound :class:`sessionmaker` factory ready for use by repositories.

    Raises:
        RuntimeError: If database_url is empty.
    """
    global _SESSION_FACTORY

    if not database_url:
        msg = "database_url must not be empty — set JARVIS_DATABASE_URL in your environment."
        raise RuntimeError(msg)

    engine = create_engine(database_url, pool_pre_ping=True)
    Base.metadata.create_all(engine)
    _SESSION_FACTORY = sessionmaker(bind=engine, expire_on_commit=False)
    return _SESSION_FACTORY


def get_session_factory() -> sessionmaker[Session]:
    """Return the already-initialised session factory.

    Raises:
        RuntimeError: If :func:`init_db_engine` has not been called yet.
    """
    if _SESSION_FACTORY is None:
        msg = "Database engine has not been initialised. Call init_db_engine() first."
        raise RuntimeError(msg)
    return _SESSION_FACTORY
