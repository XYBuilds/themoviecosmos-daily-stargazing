"""smoke_llm.py · LLM connectivity smoke test.

Sends a single user message and prints provider, model, and the first 200
characters of the reply. Exits non-zero on auth, model, or network errors.

Usage:
  python scripts/smoke_llm.py
  python scripts/smoke_llm.py --provider mimo
  python scripts/smoke_llm.py --provider deepseek
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from scripts.lib.env import default_llm_provider, load_env
from scripts.lib.llm import get_llm_client

_MODEL_ENV: dict[str, str] = {
    "mimo": "MIMO_MODEL",
    "deepseek": "DEEPSEEK_MODEL",
}

SMOKE_PROMPT = "Reply with exactly: pong"
REPLY_PREVIEW_LEN = 200


def _resolve_provider(explicit: str | None) -> str:
    if explicit is not None:
        return explicit.strip().lower()
    return default_llm_provider()


def _model_name(provider: str) -> str:
    load_env()
    env_key = _MODEL_ENV[provider]
    model = os.getenv(env_key, "").strip()
    if not model:
        raise RuntimeError(
            f"Missing {env_key} for provider {provider!r}. "
            "Copy .env.example to .env and set the model name."
        )
    return model


def run_smoke(provider: str) -> tuple[str, str]:
    """Call the LLM once; return (model_name, reply_text)."""
    load_env()
    client = get_llm_client(provider)
    model = _model_name(provider)

    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": SMOKE_PROMPT}],
    )
    reply = (response.choices[0].message.content or "").strip()
    reported_model = (getattr(response, "model", None) or "").strip() or model
    return reported_model, reply


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="Smoke-test LLM connectivity (MiMo or DeepSeek)."
    )
    parser.add_argument(
        "--provider",
        choices=("mimo", "deepseek"),
        default=None,
        help="LLM provider (default: DEFAULT_LLM_PROVIDER from .env).",
    )
    args = parser.parse_args(argv)
    provider = _resolve_provider(args.provider)

    try:
        model, reply = run_smoke(provider)
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)

    preview = reply[:REPLY_PREVIEW_LEN]
    print(f"provider: {provider}")
    print(f"model: {model}")
    print(f"reply (first {REPLY_PREVIEW_LEN} chars): {preview}")


if __name__ == "__main__":
    main()
