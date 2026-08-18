"""P0 GitLab restore: non-deploying CI adapter and tracker guidance."""

from __future__ import annotations

import ast
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
_CI = (_ROOT / ".gitlab-ci.yml").read_text(encoding="utf-8").replace("\r\n", "\n")
_AGENTS = (_ROOT / "AGENTS.md").read_text(encoding="utf-8").replace("\r\n", "\n")
_TRACKER = (_ROOT / "docs" / "agents" / "issue-tracker.md").read_text(encoding="utf-8").replace("\r\n", "\n")
_README = (_ROOT / "README.md").read_text(encoding="utf-8").replace("\r\n", "\n")
_ENV_EXAMPLE = (_ROOT / ".env.example").read_text(encoding="utf-8").replace("\r\n", "\n")

PRODUCTION_CREDENTIAL_NAMES = (
    "SUPABASE_URL",
    "SUPABASE_SERVICE_ROLE_KEY",
    "KAGGLE_USERNAME",
    "KAGGLE_KEY",
    "CLOUDFLARE_ACCOUNT_ID",
    "CLOUDFLARE_API_TOKEN",
    "OG_INDEX_KV_NAMESPACE_ID",
    "OG_INDEX_KV_API_TOKEN",
    "R2_ACCOUNT_ID",
    "R2_ACCESS_KEY_ID",
    "R2_SECRET_ACCESS_KEY",
    "R2_BUCKET",
    "R2_PUBLIC_BASE_URL",
    "TMDB_API_KEY",
    "MIMO_API_KEY",
    "DEEPSEEK_API_KEY",
    "GUARDIAN_API_KEY",
)


def test_ci_runs_pytest_without_deploy_schedules_or_production_credentials() -> None:
    assert "python -m pytest" in _CI
    assert "git diff --check" in _CI
    assert 'CI_PIPELINE_SOURCE == "schedule"' in _CI
    assert "when: never" in _CI
    assert "\nschedule:" not in f"\n{_CI}"
    assert "\ndeploy:" not in f"\n{_CI.lower()}"
    assert "pages:" not in _CI.lower()
    assert "requirements.txt" not in _CI
    assert "torch" not in _CI
    assert "sentence-transformers" not in _CI
    for name in PRODUCTION_CREDENTIAL_NAMES:
        assert name not in _CI


def test_retrieve_does_not_import_sentence_transformers_until_model_load() -> None:
    tree = ast.parse((_ROOT / "scripts" / "retrieve.py").read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.ImportFrom) and node.module == "sentence_transformers":
            raise AssertionError("sentence_transformers must not be imported at module load")
        if isinstance(node, ast.Import) and any(alias.name == "sentence_transformers" for alias in node.names):
            raise AssertionError("sentence_transformers must not be imported at module load")


def test_env_files_are_bitwarden_deployment_copies_not_secrets_authority() -> None:
    assert "Bitwarden" in _README
    assert "secrets authority" in _README.lower()
    assert "deployment copies" in _README.lower()
    assert "Bitwarden" in _ENV_EXAMPLE
    assert "secrets authority" in _ENV_EXAMPLE.lower()


def test_agents_and_tracker_name_gitlab_and_portable_parent() -> None:
    assert "GitLab" in _AGENTS
    assert "glab" in _AGENTS
    assert "docs/agents/issue-tracker.md" in _AGENTS
    assert "Human merge and Issue closure approval are mandatory" in _AGENTS
    assert "GitLab" in _TRACKER
    assert "glab" in _TRACKER
    assert "tmc:daily:" in _TRACKER
    assert "Blocked by" in _TRACKER
    assert "tmc:chronicle:01M08QA80S7XA8P5ZVKM3EVD8Q" in _TRACKER
    assert "`gh` CLI" not in _TRACKER
    assert "Do not copy Chronicle-owned runtime" in _AGENTS
