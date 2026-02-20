# ABOUTME: Startup wiring for the write-through cache-backed context store.
# ABOUTME: Call init_context_store() once at server startup after settings are loaded.

from __future__ import annotations

from autobots_devtools_shared_lib.common.observability import get_logger
from autobots_devtools_shared_lib.common.services import (
    CacheBackedContextStore,
    InMemoryContextStore,
    set_context_store,
)

from autobots_agents_jarvis.configs.settings import get_app_settings
from autobots_agents_jarvis.db.engine import init_db_engine
from autobots_agents_jarvis.db.repository import JarvisContextRepository

logger = get_logger(__name__)


def init_context_store() -> None:
    """Initialise and register the write-through CacheBackedContextStore.

    Reads JARVIS_DATABASE_URL and REDIS_URL from AppSettings.
    - JARVIS_DATABASE_URL is required; raises RuntimeError if absent.
    - REDIS_URL is optional; falls back to InMemoryContextStore for the cache
      layer (suitable for local development without Redis).

    Call once at server startup, after load_dotenv() / init_app_settings().
    """
    settings = get_app_settings()

    session_factory = init_db_engine(settings.database_url)
    repo = JarvisContextRepository(session_factory)

    if settings.redis_url:
        from autobots_devtools_shared_lib.common.services.context import (
            RedisContextStore,
            _RedisConfig,
        )

        cache: InMemoryContextStore | RedisContextStore = RedisContextStore(
            _RedisConfig(url=settings.redis_url, prefix="jarvis_ctx")
        )
        logger.info("Context store: CacheBackedContextStore (Postgres + Redis)")
    else:
        cache = InMemoryContextStore()
        logger.warning(
            "REDIS_URL not set — using InMemoryContextStore as cache layer (dev mode only)"
        )

    set_context_store(CacheBackedContextStore(db=repo, cache=cache))
