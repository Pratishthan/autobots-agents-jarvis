# ABOUTME: Startup wiring for the write-through cache-backed context store.
# ABOUTME: Call init_context_store() once at server startup after settings are loaded.

from __future__ import annotations

from autobots_devtools_shared_lib.common.observability import get_logger
from autobots_devtools_shared_lib.common.services import (
    CacheBackedContextStore,
    InMemoryContextStore,
    set_context_store,
)

from autobots_agents_jarvis.common.configs.settings import get_app_settings
from autobots_agents_jarvis.common.db.engine import init_db_engine
from autobots_agents_jarvis.common.db.repository import JarvisContextRepository

logger = get_logger(__name__)


def init_context_store(*, app_name: str | None = None) -> None:
    """Initialise and register the write-through CacheBackedContextStore.

    Reads JARVIS_DATABASE_URL and REDIS_URL from AppSettings.
    - JARVIS_DATABASE_URL is optional; logs a warning and sets InMemoryContextStore
      if absent (suitable for local dev without a DB).
    - REDIS_URL is optional; falls back to InMemoryContextStore for the cache
      layer when absent.
    - app_name: Domain name for prefix isolation (e.g. 'concierge', 'sales').
      Defaults to settings.app_name; use '' if not set.

    Safe to call multiple times (idempotent per settings state).
    Call once at server startup, after load_dotenv() / init_app_settings().
    """
    settings = get_app_settings()
    prefix_app = app_name if app_name is not None else settings.app_name
    prefix = f"jarvis-{prefix_app}" if prefix_app else "jarvis"

    if not settings.database_url:
        logger.warning(
            "JARVIS_DATABASE_URL not set — context store not initialised; "
            "using in-memory fallback (data will not persist across restarts)"
        )
        set_context_store(InMemoryContextStore())
        return

    session_factory = init_db_engine(settings.database_url)
    repo = JarvisContextRepository(session_factory)

    if settings.redis_url:
        from autobots_devtools_shared_lib.common.services.context import (
            RedisContextStore,
            _RedisConfig,
        )

        # Redis prefix for multi-tenant isolation; CacheBackedContextStore applies own prefix to keys.
        cache: InMemoryContextStore | RedisContextStore = RedisContextStore(
            _RedisConfig(url=settings.redis_url)
        )
        logger.info("Context store: CacheBackedContextStore (Postgres + Redis)")
    else:
        cache = InMemoryContextStore()
        logger.warning(
            "REDIS_URL not set — using InMemoryContextStore as cache layer (dev mode only)"
        )

    set_context_store(CacheBackedContextStore(db=repo, cache=cache, prefix=prefix))
