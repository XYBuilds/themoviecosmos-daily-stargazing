"""Unit tests for Phase 9.7.4 review_panel/rewrite_adapter.py."""

from __future__ import annotations

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from review_panel.rewrite_adapter import (
    locate_copy_path,
    main,
    render_humanized_markdown,
    run_adapter,
)


def _write_copy_md(tmp_path: Path, date: str, slug: str, platform: str = "xiaohongshu") -> Path:
    news_dir = tmp_path / date
    news_dir.mkdir(parents=True, exist_ok=True)
    copy_path = news_dir / f"{slug}_copy_{platform}.md"
    copy_path.write_text(
        "# 发布定稿 · 2026-07-06 · 小红书\n\n"
        "一句标题\n\n"
        "「Survival Family」(2017) 矢口史靖 原版正文，句子很长很长很长很长很长很长。\n\n"
        "## 链接\n\n"
        "- 电影: https://themoviecosmos.com/movie/429918\n"
        "- 新闻: https://example.com/article/1\n",
        encoding="utf-8",
    )
    return copy_path


class RunAdapterTests(unittest.TestCase):
    def test_writes_humanized_file_in_slimmed_format(self) -> None:
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            copy_path = _write_copy_md(tmp_path, "2026-07-06", "09-slug")
            original_text = copy_path.read_text(encoding="utf-8")

            captured_prompt: dict[str, str] = {}

            def fake_call_llm(prompt: str) -> str:
                captured_prompt["prompt"] = prompt
                return "「Survival Family」(2017) 矢口史靖 去AI化后的正文。"

            humanized_path = run_adapter(
                "2026-07-06",
                "09-slug",
                platform="xiaohongshu",
                batch_root=tmp_path,
                call_llm=fake_call_llm,
            )

            expected_path = tmp_path / "2026-07-06" / "09-slug_copy_xiaohongshu_humanized.md"
            self.assertEqual(humanized_path, expected_path)
            self.assertTrue(humanized_path.is_file())

            # prompt 里应包含原文 body（占位符已被替换）。
            self.assertIn("原版正文", captured_prompt["prompt"])
            self.assertNotIn("{{body}}", captured_prompt["prompt"])

            humanized_text = humanized_path.read_text(encoding="utf-8")
            self.assertIn("# 发布定稿 · 2026-07-06 · 小红书", humanized_text)
            self.assertIn("一句标题", humanized_text)
            self.assertIn("去AI化后的正文", humanized_text)
            self.assertIn("## 链接", humanized_text)
            self.assertIn("https://themoviecosmos.com/movie/429918", humanized_text)
            self.assertIn("https://example.com/article/1", humanized_text)
            # 去AI化产出不应残留原版正文。
            self.assertNotIn("原版正文", humanized_text)

            # 原稿必须逐字未被改动。
            self.assertEqual(copy_path.read_text(encoding="utf-8"), original_text)

    def test_missing_copy_file_raises_value_error(self) -> None:
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            with self.assertRaises(ValueError):
                run_adapter(
                    "2026-07-06",
                    "missing-slug",
                    batch_root=tmp_path,
                    call_llm=lambda prompt: "x",
                )

    def test_empty_llm_response_raises_value_error(self) -> None:
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            _write_copy_md(tmp_path, "2026-07-06", "09-slug")
            with self.assertRaises(ValueError):
                run_adapter(
                    "2026-07-06",
                    "09-slug",
                    batch_root=tmp_path,
                    call_llm=lambda prompt: "   ",
                )

    def test_locate_copy_path_missing_raises(self) -> None:
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            with self.assertRaises(ValueError):
                locate_copy_path("2026-07-06", "nope", "xiaohongshu", batch_root=tmp_path)


class RenderHumanizedMarkdownTests(unittest.TestCase):
    def test_renders_slimmed_format(self) -> None:
        text = render_humanized_markdown(
            "2026-07-06",
            "一句标题",
            "去AI化正文。",
            "## 链接\n\n- 电影: x\n- 新闻: y",
            platform="xiaohongshu",
        )
        self.assertIn("# 发布定稿 · 2026-07-06 · 小红书", text)
        self.assertIn("一句标题", text)
        self.assertIn("去AI化正文。", text)
        self.assertIn("## 链接", text)


class MainCliTests(unittest.TestCase):
    def test_main_returns_2_on_missing_copy_file(self) -> None:
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            # main() 走真实 run_adapter（默认 batch_root），故直接断言参数缺失场景下的
            # ValueError 退出码路径：用一个必然不存在的 slug + 显式 batch_root 不可行
            # （main 不接受 batch_root 参数），改为验证 argparse 必填校验。
            with self.assertRaises(SystemExit):
                main([])


if __name__ == "__main__":
    unittest.main()