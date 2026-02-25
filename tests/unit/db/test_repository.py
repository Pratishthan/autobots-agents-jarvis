# ABOUTME: Unit tests for JarvisContextRepository using SQLite in-memory.
# ABOUTME: Validates CRUD operations without requiring a real PostgreSQL instance.

from __future__ import annotations

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from autobots_agents_jarvis.common.db.models import Base, JarvisContextEntity
from autobots_agents_jarvis.common.db.repository import JarvisContextRepository

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def session_factory():
    """SQLite in-memory engine with all tables created."""
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, expire_on_commit=False)
    yield factory
    engine.dispose()


@pytest.fixture()
def repo(session_factory):
    """Repository with no prefix (default)."""
    return JarvisContextRepository(session_factory)


@pytest.fixture()
def repo_with_prefix(session_factory):
    """Repository with prefix jarvis_ctx (matches CacheBackedContextStore usage)."""
    return JarvisContextRepository(session_factory, prefix="jarvis_ctx")


# ---------------------------------------------------------------------------
# get
# ---------------------------------------------------------------------------


def test_get_returns_none_when_missing(repo):
    assert repo.get("missing_key") is None


def test_get_returns_stored_data(repo, session_factory):
    with session_factory() as session:
        entity = JarvisContextEntity(
            context_key="k1",
            user_name="alice",
            repo_name="jarvis-repo",
            jira_number="JARVIS-1",
        )
        session.add(entity)
        session.commit()

    result = repo.get("k1")
    assert result == {"user_name": "alice", "repo_name": "jarvis-repo", "jira_number": "JARVIS-1"}


def test_get_omits_none_fields(repo, session_factory):
    """Fields that were not set are omitted from the returned dict."""
    with session_factory() as session:
        entity = JarvisContextEntity(context_key="k2", repo_name="only-repo")
        session.add(entity)
        session.commit()

    result = repo.get("k2")
    assert result == {"repo_name": "only-repo"}


# ---------------------------------------------------------------------------
# set (upsert)
# ---------------------------------------------------------------------------


def test_set_inserts_new_row(repo):
    repo.set("new_key", {"user_name": "bob", "repo_name": "repo1", "jira_number": "J-1"})

    result = repo.get("new_key")
    assert result == {"user_name": "bob", "repo_name": "repo1", "jira_number": "J-1"}


def test_set_updates_existing_row(repo):
    repo.set("upd_key", {"user_name": "carol", "repo_name": "old-repo"})
    repo.set("upd_key", {"user_name": "carol", "repo_name": "new-repo"})

    result = repo.get("upd_key")
    assert result == {"user_name": "carol", "repo_name": "new-repo"}


def test_set_user_id_alias_maps_to_user_name(repo, session_factory):
    """'user_id' key in the input dict is stored as the user_name column."""
    repo.set("alias_key", {"user_id": "dave", "repo_name": "alias-repo"})

    result = repo.get("alias_key")
    assert result.get("user_name") == "dave"
    assert "user_id" not in result

    with session_factory() as session:
        entity = session.get(JarvisContextEntity, "alias_key")
        assert entity is not None
        assert entity.user_name == "dave"


def test_set_ignores_unknown_keys(repo):
    """Unknown keys in the input dict are silently ignored."""
    repo.set("unk_key", {"user_name": "eve", "unknown_field": "ignored", "another": 42})

    result = repo.get("unk_key")
    assert result == {"user_name": "eve"}
    assert "unknown_field" not in result


def test_get_returns_none_after_unset_key(repo):
    assert repo.get("never_set") is None


# ---------------------------------------------------------------------------
# delete
# ---------------------------------------------------------------------------


def test_delete_removes_existing_row(repo, session_factory):
    with session_factory() as session:
        entity = JarvisContextEntity(context_key="del_key", user_name="frank")
        session.add(entity)
        session.commit()

    repo.delete("del_key")

    assert repo.get("del_key") is None


def test_delete_nonexistent_key_does_not_raise(repo):
    repo.delete("nonexistent")  # should not raise


# ---------------------------------------------------------------------------
# prefix (jarvis_ctx) — aligns with CacheBackedContextStore
# ---------------------------------------------------------------------------


def test_prefix_get_set_roundtrip(repo_with_prefix):
    """With prefix, get/set use storage key prefix_context_key in the DB."""
    repo_with_prefix.set("session_1", {"user_name": "alice", "repo_name": "r1"})
    result = repo_with_prefix.get("session_1")
    assert result == {"user_name": "alice", "repo_name": "r1"}


def test_prefix_stores_under_prefixed_key(repo_with_prefix, session_factory):
    """DB row uses prefixed context_key (jarvis_ctx_session_1)."""
    repo_with_prefix.set("session_1", {"user_name": "bob"})
    with session_factory() as session:
        entity = session.get(JarvisContextEntity, "jarvis_ctx_session_1")
        assert entity is not None
        assert entity.context_key == "jarvis_ctx_session_1"
        assert entity.user_name == "bob"


def test_prefix_get_returns_none_for_unprefixed_key(repo_with_prefix, session_factory):
    """Raw key in DB (no prefix) is not visible when repo uses prefix."""
    with session_factory() as session:
        entity = JarvisContextEntity(context_key="session_1", user_name="raw")
        session.add(entity)
        session.commit()
    # Repo with prefix looks up jarvis_ctx_session_1, not session_1
    assert repo_with_prefix.get("session_1") is None


def test_prefix_delete_removes_prefixed_row(repo_with_prefix, session_factory):
    repo_with_prefix.set("del_me", {"user_name": "x"})
    repo_with_prefix.delete("del_me")
    assert repo_with_prefix.get("del_me") is None
    with session_factory() as session:
        assert session.get(JarvisContextEntity, "jarvis_ctx_del_me") is None
