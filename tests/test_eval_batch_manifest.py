"""Manifest and batch script smoke (no LLM)."""

from __future__ import annotations

import json
import subprocess
import unittest
from pathlib import Path

from scripts.eval_batch_manifest import (
    load_manifest,
    news_file_for_run_id,
    validate_manifest,
)

_REPO_ROOT = Path(__file__).resolve().parents[1]
_BATCH_PS1 = _REPO_ROOT / "scripts" / "run_eval_batch.ps1"


class TestEvalBatchManifest(unittest.TestCase):
    def test_manifest_has_ten_runs_with_news_files(self) -> None:
        errors = validate_manifest(_REPO_ROOT)
        self.assertEqual(errors, [], msg="; ".join(errors))

    def test_run_ids_match_json_basenames(self) -> None:
        news_dir = _REPO_ROOT / "tests" / "eval_news"
        json_stems = {p.stem for p in news_dir.glob("*.json") if p.name != "batch-manifest.json"}
        manifest_ids = set(load_manifest())
        self.assertEqual(manifest_ids, json_stems)

    def test_news_paths(self) -> None:
        for rid in load_manifest():
            path = news_file_for_run_id(rid, _REPO_ROOT)
            self.assertTrue(path.is_file(), msg=str(path))


class TestRunEvalBatchWhatIf(unittest.TestCase):
    @unittest.skipUnless(_BATCH_PS1.is_file(), "run_eval_batch.ps1 missing")
    def test_whatif_exits_zero(self) -> None:
        pwsh = "pwsh"
        try:
            subprocess.run([pwsh, "-NoProfile", "-Command", "$PSVersionTable.PSVersion.Major"],
                           capture_output=True, check=True, timeout=10)
        except (FileNotFoundError, subprocess.CalledProcessError):
            self.skipTest("pwsh (PowerShell 7+) not available")
        proc = subprocess.run(
            [
                pwsh,
                "-NoProfile",
                "-File",
                str(_BATCH_PS1),
                "-WhatIf",
                "-SkipExisting:$false",
            ],
            cwd=_REPO_ROOT,
            capture_output=True,
            text=True,
            timeout=60,
            check=False,
        )
        self.assertEqual(
            proc.returncode,
            0,
            msg=f"stdout:\n{proc.stdout}\nstderr:\n{proc.stderr}",
        )
        self.assertIn("run_eval.py", proc.stdout)
        self.assertIn("01-grid-outage", proc.stdout)
        self.assertIn("score_eval_candidates.py", proc.stdout)

    def test_manifest_json_valid(self) -> None:
        path = _REPO_ROOT / "tests" / "eval_news" / "batch-manifest.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(len(data["run_ids"]), 10)


if __name__ == "__main__":
    unittest.main()
