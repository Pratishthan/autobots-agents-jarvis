# ABOUTME: Concierge domain-specific settings.
# ABOUTME: Extends AppSettings with concierge-specific configuration (default city, joke category, etc.).

from pydantic import Field

from autobots_agents_jarvis.configs.settings import AppSettings, init_app_settings


class ConciergeSettings(AppSettings):
    """Concierge domain settings.
    Extends AppSettings with concierge-specific configuration."""

    # Concierge-specific settings
    default_city: str = Field(default="London", description="Default city for weather lookups")
    default_joke_category: str = Field(default="general", description="Default joke category")

    # Override app_name default for concierge domain
    app_name: str = Field(default="concierge", description="Application name")


def get_concierge_settings() -> ConciergeSettings:
    """Get concierge settings instance."""
    return ConciergeSettings()


def init_concierge_settings() -> ConciergeSettings:
    """Initialize concierge settings and register with shared-lib.

    Chains: concierge → app → dynagent

    Returns:
        The initialized ConciergeSettings instance.

    Call at app startup.
    """
    s = get_concierge_settings()
    init_app_settings(s)
    return s
