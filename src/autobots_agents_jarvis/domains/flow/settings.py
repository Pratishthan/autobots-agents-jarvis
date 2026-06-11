# ABOUTME: Flow domain settings. Extends AppSettings with flow-specific config.

from __future__ import annotations

from pydantic import Field

from autobots_agents_jarvis.common.configs.settings import AppSettings, init_app_settings


class FlowSettings(AppSettings):
    """Flow domain settings."""

    app_name: str = Field(default="flow", description="Application name")
    flow_data_dir: str = Field(default="data/flows", description="Dir of generated flow JSON")


def get_flow_settings() -> FlowSettings:
    return FlowSettings()


def init_flow_settings() -> FlowSettings:
    s = get_flow_settings()
    init_app_settings(s)
    return s
