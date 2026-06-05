"""Offline checks: eval news corpus is English; phase 3.8 runner helpers."""

from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

from scripts.eval_batch_manifest import load_manifest, news_file_for_run_id
from scripts.run_phase38_eval import contains_cjk, find_cjk_violations, phase38_run_dir

_REPO = Path(__file__).resolve().parents[1]
_MANIFEST = _REPO / "tests" / "eval_news" / "batch-manifest.json"
_CJK_RE = re.compile(r"[\u4e00-\u9fff\u3400-\u4dbf\uf900-\ufaff]")


class TestEvalEnglishCorpus(unittest.TestCase):
    def test_manifest_declares_english_v2(self) -> None:
        data = json.loads(_MANIFEST.read_text(encoding="utf-8"))
        self.assertEqual(data.get("version"), 2)
        self.assertEqual(data.get("language"), "en")
        self.assertIn("lineage", data)
        self.assertEqual(len(data["run_ids"]), 10)

    def test_news_title_and_description_are_english(self) -> None:
        violations: list[str] = []
        for rid in load_manifest():
            path = news_file_for_run_id(rid, _REPO)
            payload = json.loads(path.read_text(encoding="utf-8"))
            for field in ("title", "description"):
                text = str(payload.get(field, ""))
                if _CJK_RE.search(text):
                    violations.append(f"{rid}.{field}")
                if not text.strip():
                    violations.append(f"{rid}.{field}:empty")
        self.assertEqual(violations, [], msg="; ".join(violations))

    def test_contains_cjk_helper(self) -> None:
        self.assertFalse(contains_cjk("Rotational blackout risks rise"))
        self.assertTrue(contains_cjk("维萨亚斯群岛"))

    def test_find_cjk_violations_empty_when_missing(self) -> None:
        run_id = "__nonexistent_phase38_run__"
        self.assertEqual(find_cjk_violations(phase38_run_dir(run_id)), [])


if __name__ == "__main__":
    unittest.main()
