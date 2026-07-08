"""Unit tests for Phase 9.8.3 review_panel/regenerate_adapter.py."""

from __future__ import annotations

import contextlib
import io
import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from review_panel.regenerate_adapter import main, run_adapter

_ORIGINAL_HEADLINE = "一句原始标题"
_ORIGINAL_BODY = "「Survival Family」(2017) 矢口史靖 原版正文，句子很长很长很长很长很长。"


def _write_news(news_dir: Path) -> None:
    payload = {
        "title": "Test headline",
        "description": "Test description.",
        "url": "https://example.com/article/1",
    }
    (news_dir / "news.json").write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")


def _write_retrieve(news_dir: Path, tmdb_id: int = 429918) -> None:
    payload = {
        "candidates": [
            {
                "tmdb_id": tmdb_id,
                "title": "Survival Family",
                "overview": "An overview.",
                "genres": "Comedy, Drama",
                "release_year": 2017,
                "movie_url": f"https://themoviecosmos.com/movie/{tmdb_id}",
            }
        ]
    }
    (news_dir / "retrieve.json").write_text(
        json.dumps(payload, ensure_ascii=False), encoding="utf-8"
    )


def _write_copy_md(
    batch_root: Path,
    date: str,
    slug: str,
    platform: str = "xiaohongshu",
    headline: str = _ORIGINAL_HEADLINE,
    body: str = _ORIGINAL_BODY,
) -> Path:
    date_dir = batch_root / date
    date_dir.mkdir(parents=True, exist_ok=True)
    copy_path = date_dir / f"{slug}_copy_{platform}.md"
    copy_path.write_text(
        f"# 发布定稿 · {date} · 小红书\n\n"
        f"{headline}\n\n"
        f"{body}\n\n"
        "## 链接\n\n"
        "- 电影: https://themoviecosmos.com/movie/429918\n"
        "- 新闻: https://example.com/article/1\n",
        encoding="utf-8",
    )
    return copy_path


def _make_batch(tmp_path: Path, date: str, slug: str, tmdb_id: int = 429918) -> None:
    news_dir = tmp_path / date / slug
    news_dir.mkdir(parents=True)
    _write_news(news_dir)
    _write_retrieve(news_dir, tmdb_id=tmdb_id)
    _write_copy_md(tmp_path, date, slug)


def _fake_run_publish(candidate, news, *, provider=None, judge=None, platform=None):
    return {
        "tmdb_id": candidate["tmdb_id"],
        "headline": "新标题不该被采用",
        "body": "重新创作的正文XYZ",
    }


def _empty_body_run_publish(candidate, news, *, provider=None, judge=None, platform=None):
    return {"tmdb_id": candidate["tmdb_id"], "headline": "x", "body": "   "}


class RegenerateBodyTests(unittest.TestCase):
    def test_regenerates_body_preserves_headline_deletes_humanized(self) -> None:
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            _make_batch(tmp_path, "2026-07-06", "09-slug")
            humanized_path = tmp_path / "2026-07-06" / "09-slug_copy_xiaohongshu_humanized.md"
            humanized_path.write_text("旧的 humanized 内容", encoding="utf-8")

            copy_path = run_adapter(
                "2026-07-06",
                "09-slug",
                429918,
                "body",
                batch_root=tmp_path,
                run_publish=_fake_run_publish,
            )

            content = copy_path.read_text(encoding="utf-8")
            self.assertIn("重新创作的正文XYZ", content)
            # 新 headline 不应被采用，原 headline 保留。
            self.assertNotIn("新标题不该被采用", content)
            self.assertIn(_ORIGINAL_HEADLINE, content)
            # 链接分区保留。
            self.assertIn("https://themoviecosmos.com/movie/429918", content)
            self.assertIn("https://example.com/article/1", content)
            # humanized 被删除（D4）。
            self.assertFalse(humanized_path.is_file())

    def test_empty_body_raises_value_error(self) -> None:
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            _make_batch(tmp_path, "2026-07-06", "09-slug")

            with self.assertRaises(ValueError):
                run_adapter(
                    "2026-07-06",
                    "09-slug",
                    429918,
                    "body",
                    batch_root=tmp_path,
                    run_publish=_empty_body_run_publish,
                )


class RegenerateHeadlineTests(unittest.TestCase):
    def test_regenerates_headline_preserves_body_passes_current_body(self) -> None:
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            _make_batch(tmp_path, "2026-07-06", "09-slug")
            humanized_path = tmp_path / "2026-07-06" / "09-slug_copy_xiaohongshu_humanized.md"
            humanized_path.write_text("humanized 内容", encoding="utf-8")

            captured: dict = {}

            def fake_run_headline(candidate, news, current_body, *, provider=None, judge=None, platform=None):
                captured["current_body"] = current_body
                return {"tmdb_id": candidate["tmdb_id"], "headline": "贴合正文的新标题"}

            copy_path = run_adapter(
                "2026-07-06",
                "09-slug",
                429918,
                "headline",
                batch_root=tmp_path,
                run_headline=fake_run_headline,
            )

            content = copy_path.read_text(encoding="utf-8")
            self.assertIn("贴合正文的新标题", content)
            # body 未变。
            self.assertIn(_ORIGINAL_BODY, content)
            # run_headline 收到的 current_body 就是原稿正文。
            self.assertEqual(captured["current_body"], _ORIGINAL_BODY)
            # humanized 未被删除（headline 变化不影响 body）。
            self.assertTrue(humanized_path.is_file())
            self.assertEqual(humanized_path.read_text(encoding="utf-8"), "humanized 内容")

    def test_empty_body_raises_before_calling_run_headline(self) -> None:
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            news_dir = tmp_path / "2026-07-06" / "09-slug"
            news_dir.mkdir(parents=True)
            _write_news(news_dir)
            _write_retrieve(news_dir, tmdb_id=429918)
            _write_copy_md(tmp_path, "2026-07-06", "09-slug", body="")

            called = {"count": 0}

            def should_not_be_called(*args, **kwargs):
                called["count"] += 1
                return {"tmdb_id": 429918, "headline": "x"}

            with self.assertRaises(ValueError):
                run_adapter(
                    "2026-07-06",
                    "09-slug",
                    429918,
                    "headline",
                    batch_root=tmp_path,
                    run_headline=should_not_be_called,
                )
            self.assertEqual(called["count"], 0)


class ErrorPathTests(unittest.TestCase):
    def test_missing_copy_file_raises_value_error(self) -> None:
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            news_dir = tmp_path / "2026-07-06" / "09-slug"
            news_dir.mkdir(parents=True)
            _write_news(news_dir)
            _write_retrieve(news_dir, tmdb_id=429918)
            # 有意不写 copy md。

            with self.assertRaises(ValueError):
                run_adapter(
                    "2026-07-06",
                    "09-slug",
                    429918,
                    "body",
                    batch_root=tmp_path,
                    run_publish=_fake_run_publish,
                )

    def test_missing_copy_file_main_exits_2(self) -> None:
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            news_dir = tmp_path / "2026-07-06" / "09-slug"
            news_dir.mkdir(parents=True)
            _write_news(news_dir)
            _write_retrieve(news_dir, tmdb_id=429918)

            with patch(
                "review_panel.regenerate_adapter._default_batch_root", return_value=tmp_path
            ):
                code = main(
                    [
                        "--date",
                        "2026-07-06",
                        "--slug",
                        "09-slug",
                        "--tmdb-id",
                        "429918",
                        "--target",
                        "body",
                    ]
                )
            self.assertEqual(code, 2)


class MainCliTests(unittest.TestCase):
    def test_main_headline_end_to_end_prints_wrote_and_returns_0(self) -> None:
        # 注：``run_adapter`` 的 ``run_headline: Any = compose.run_headline`` 默认值
        # 在模块加载时就绑定了函数对象；main() 调用 run_adapter 时不传
        # run_headline，事后 patch ``compose.run_headline`` 属性不会回填这个已绑定的
        # 默认值（Python 默认参数早绑定的经典坑，publish_adapter.py 里同款设计也有
        # 这个问题，只是没被测到）。因此这里改为直接 patch ``run_adapter`` 本身，
        # 只验证 main() 的 CLI 参数解析→调用→打印→返回码这条薄管线，不再假设
        # module-attribute patch 能穿透进已绑定的默认参数。
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            expected_path = tmp_path / "2026-07-06" / "09-slug_copy_xiaohongshu.md"
            captured_call: dict = {}

            def fake_run_adapter(date, slug, tmdb_id, target, **kwargs):
                captured_call.update(
                    date=date, slug=slug, tmdb_id=tmdb_id, target=target, kwargs=kwargs
                )
                return expected_path

            with patch(
                "review_panel.regenerate_adapter.run_adapter",
                side_effect=fake_run_adapter,
            ):
                stderr_buf = io.StringIO()
                with contextlib.redirect_stderr(stderr_buf):
                    code = main(
                        [
                            "--date",
                            "2026-07-06",
                            "--slug",
                            "09-slug",
                            "--tmdb-id",
                            "429918",
                            "--target",
                            "headline",
                        ]
                    )

            self.assertEqual(code, 0)
            self.assertIn(f"Wrote {expected_path.resolve()}", stderr_buf.getvalue())
            self.assertEqual(captured_call["date"], "2026-07-06")
            self.assertEqual(captured_call["slug"], "09-slug")
            self.assertEqual(captured_call["tmdb_id"], "429918")
            self.assertEqual(captured_call["target"], "headline")


if __name__ == "__main__":
    unittest.main()