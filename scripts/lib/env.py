"""Load .env from repo root and expose DEFAULT_LLM_PROVIDER."""

from __future__ import annotations

import os

from dotenv import load_dotenv

from scripts.lib.paths import repo_root

_ENV_LOADED = False
DEFAULT_LLM_PROVIDER = "mimo"


def load_env() -> None:
    """Load `.env` from repository root once (no-op if already loaded)."""
    global _ENV_LOADED
    if _ENV_LOADED:
        return
    env_path = repo_root() / ".env"
    if env_path.is_file():
        load_dotenv(env_path)
    else:
        load_dotenv()
    _ENV_LOADED = True


def default_llm_provider() -> str:
    """Active provider name: ``mimo`` or ``deepseek`` (from env or default)."""
    load_env()
    return os.getenv("DEFAULT_LLM_PROVIDER", DEFAULT_LLM_PROVIDER).strip().lower()
