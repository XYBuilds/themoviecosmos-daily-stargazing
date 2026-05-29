"""OpenAI-compatible LLM clients (MiMo primary, DeepSeek fallback)."""

from __future__ import annotations

import os
from typing import Final

from openai import OpenAI

from scripts.lib.env import default_llm_provider, load_env

_PROVIDERS: Final[dict[str, dict[str, str]]] = {
    "mimo": {
        "api_key": "MIMO_API_KEY",
        "base_url": "MIMO_BASE_URL",
        "model": "MIMO_MODEL",
    },
    "deepseek": {
        "api_key": "DEEPSEEK_API_KEY",
        "base_url": "DEEPSEEK_BASE_URL",
        "model": "DEEPSEEK_MODEL",
    },
}


def get_llm_client(provider: str | None = None) -> OpenAI:
    """Return an OpenAI SDK client for *provider* (default from env).

    Raises:
        ValueError: unknown provider name.
        RuntimeError: missing API key or base URL in environment.
    """
    load_env()
    name = (provider or default_llm_provider()).strip().lower()
    if name not in _PROVIDERS:
        allowed = ", ".join(sorted(_PROVIDERS))
        raise ValueError(f"Unknown LLM provider {name!r}; expected one of: {allowed}")

    cfg = _PROVIDERS[name]
    api_key = os.getenv(cfg["api_key"], "").strip()
    base_url = os.getenv(cfg["base_url"], "").strip()
    if not api_key:
        raise RuntimeError(
            f"Missing {cfg['api_key']} for provider {name!r}. "
            "Copy .env.example to .env and set your API credentials."
        )
    if not base_url:
        raise RuntimeError(
            f"Missing {cfg['base_url']} for provider {name!r}. "
            "Copy .env.example to .env and set the API base URL."
        )
    return OpenAI(api_key=api_key, base_url=base_url)
