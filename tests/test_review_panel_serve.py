"""Unit tests for Phase 8.3 review_panel/serve.py.

优先测纯路由函数 route()（不起真实端口），符合 serve.py 里「传输层与路由逻辑
解耦」的设计：造临时 batch_root + mini 数据，直接调 route() 验证行为。
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace

from review_panel.serve import (
    parse_copy_markdown,
    read_selection,
    replace_body_in_copy_markdown,
    route,
)


def _write_news(news_dir: Path) -> None:
    payload = {
        "title": "Test headline",
        "description": "Test description.",
        "pub_time": "2026-07-05T14:02:46Z",
        "source_name": "Guardian",
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
                "language": "ja",
                "poster_path": "/poster.jpg",
                "movie_url": f"https://themoviecosmos.com/movie/{tmdb_id}",
                "similarity": 0.42,
                "hit_sources": [],
            }
        ]
    }
    (news_dir / "retrieve.json").write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")


def _write_judge_scores(news_dir: Path, tmdb_id: int = 429918) -> None:
    payload = {
        "version": "1",
        "calibration": {},
        "scores": [
            {
                "tmdb_id": str(tmdb_id),
                "judge_score": 3,
                "judge_resonance_type": "深层共振",
                "rationale": "rationale text",
                "causal_test": "causal test text",
            }
        ],
    }
    (news_dir / "llm-judge-scores.json").write_text(
        json.dumps(payload, ensure_ascii=False), encoding="utf-8"
    )


def _make_batch(tmp_path: Path, date: str, slug: str, tmdb_id: int = 429918) -> None:
    news_dir = tmp_path / date / slug
    news_dir.mkdir(parents=True)
    _write_news(news_dir)
    _write_retrieve(news_dir, tmdb_id=tmdb_id)
    # build_data 会过滤掉无 judge_score 的候选（与 briefing 口径一致），故 fixture 必须
    # 带一条 judge 分，否则 /api/data 的 candidates 会被过滤空。
    _write_judge_scores(news_dir, tmdb_id=tmdb_id)


class DatesRouteTests(unittest.TestCase):
    def test_returns_dates_in_descending_order(self) -> None:
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            _make_batch(tmp_path, "2026-07-05", "01-slug")
            _make_batch(tmp_path, "2026-07-06", "01-slug")

            status, payload = route("GET", "/api/dates", {}, None, batch_root=tmp_path)

            self.assertEqual(status, 200)
            self.assertEqual(payload, {"dates": ["2026-07-06", "2026-07-05"]})


class DataRouteTests(unittest.TestCase):
    def test_returns_panel_dict_with_news_items(self) -> None:
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            _make_batch(tmp_path, "2026-07-06", "09-slug")

            status, payload = route(
                "GET", "/api/data", {"date": "2026-07-06"}, None, batch_root=tmp_path
            )

            self.assertEqual(status, 200)
            self.assertEqual(payload["date"], "2026-07-06")
            self.assertEqual(len(payload["news_items"]), 1)
            self.assertEqual(payload["news_items"][0]["slug"], "09-slug")
            self.assertEqual(payload["news_items"][0]["candidates"][0]["title"], "Survival Family")

    def test_missing_date_param_returns_400(self) -> None:
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            status, payload = route("GET", "/api/data", {}, None, batch_root=tmp_path)
            self.assertEqual(status, 400)
            self.assertIn("error", payload)

    def test_unknown_date_returns_404(self) -> None:
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            status, payload = route(
                "GET", "/api/data", {"date": "2099-01-01"}, None, batch_root=tmp_path
            )
            self.assertEqual(status, 404)
            self.assertIn("error", payload)


class SelectRouteTests(unittest.TestCase):
    def test_writes_selection_json(self) -> None:
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            _make_batch(tmp_path, "2026-07-06", "09-slug")

            status, payload = route(
                "POST",
                "/api/select",
                {},
                {"date": "2026-07-06", "news_slug": "09-slug", "tmdb_id": 429918, "title": "Survival Family"},
                batch_root=tmp_path,
            )

            self.assertEqual(status, 200)
            self.assertTrue(payload["ok"])
            selection = read_selection(tmp_path, "2026-07-06")
            self.assertEqual(selection["selected"]["news_slug"], "09-slug")
            self.assertEqual(selection["selected"]["tmdb_id"], 429918)
            # D4：新写入的 selection 用 copies dict，未发布时为空 dict，
            # 不再有顶层 published/copy_path 字段。
            self.assertEqual(selection["copies"], {})
            self.assertNotIn("published", selection)
            self.assertNotIn("copy_path", selection)

    def test_repeated_select_is_idempotent_last_wins(self) -> None:
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            _make_batch(tmp_path, "2026-07-06", "09-slug")
            _make_batch(tmp_path, "2026-07-06", "10-slug", tmdb_id=99)

            route(
                "POST",
                "/api/select",
                {},
                {"date": "2026-07-06", "news_slug": "09-slug", "tmdb_id": 429918, "title": "Survival Family"},
                batch_root=tmp_path,
            )
            route(
                "POST",
                "/api/select",
                {},
                {"date": "2026-07-06", "news_slug": "10-slug", "tmdb_id": 99, "title": "Other Movie"},
                batch_root=tmp_path,
            )

            selection = read_selection(tmp_path, "2026-07-06")
            self.assertEqual(selection["selected"]["news_slug"], "10-slug")
            self.assertEqual(selection["selected"]["tmdb_id"], 99)

    def test_missing_required_field_returns_400(self) -> None:
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            status, payload = route(
                "POST", "/api/select", {}, {"date": "2026-07-06"}, batch_root=tmp_path
            )
            self.assertEqual(status, 400)
            self.assertFalse(payload["ok"])


class PublishRouteTests(unittest.TestCase):
    def test_success_updates_selection_and_returns_copy_path(self) -> None:
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            _make_batch(tmp_path, "2026-07-06", "09-slug")
            route(
                "POST",
                "/api/select",
                {},
                {"date": "2026-07-06", "news_slug": "09-slug", "tmdb_id": 429918, "title": "Survival Family"},
                batch_root=tmp_path,
            )

            expected_copy_path = tmp_path / "2026-07-06" / "09-slug_copy_xiaohongshu.md"

            def fake_run_subprocess(cmd, capture_output, text):  # noqa: ANN001
                # 断言子进程命令行的确切形态：脚本路径 + --date/--news-slug/--tmdb-id/--platform。
                self.assertIn("--date", cmd)
                self.assertIn("2026-07-06", cmd)
                self.assertIn("--news-slug", cmd)
                self.assertIn("09-slug", cmd)
                self.assertIn("--tmdb-id", cmd)
                self.assertIn("429918", cmd)
                self.assertIn("--platform", cmd)
                self.assertIn("xiaohongshu", cmd)
                return SimpleNamespace(
                    returncode=0, stdout="", stderr=f"Wrote {expected_copy_path}\n"
                )

            status, payload = route(
                "POST",
                "/api/publish",
                {},
                {"date": "2026-07-06"},
                batch_root=tmp_path,
                run_subprocess=fake_run_subprocess,
            )

            self.assertEqual(status, 200)
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["copy_path"], str(expected_copy_path))

            selection = read_selection(tmp_path, "2026-07-06")
            # D4：发布结果写入 copies.xiaohongshu，humanized_path 初始为 None。
            entry = selection["copies"]["xiaohongshu"]
            self.assertTrue(entry["published"])
            self.assertEqual(entry["copy_path"], str(expected_copy_path))
            self.assertIsNone(entry["humanized_path"])

    def test_failure_returns_ok_false_and_stderr(self) -> None:
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            _make_batch(tmp_path, "2026-07-06", "09-slug")
            route(
                "POST",
                "/api/select",
                {},
                {"date": "2026-07-06", "news_slug": "09-slug", "tmdb_id": 429918, "title": "Survival Family"},
                batch_root=tmp_path,
            )

            def fake_run_subprocess(cmd, capture_output, text):  # noqa: ANN001
                return SimpleNamespace(returncode=2, stdout="", stderr="error: tmdb_id not found")

            status, payload = route(
                "POST",
                "/api/publish",
                {},
                {"date": "2026-07-06"},
                batch_root=tmp_path,
                run_subprocess=fake_run_subprocess,
            )

            self.assertEqual(status, 500)
            self.assertFalse(payload["ok"])
            self.assertIsNone(payload["copy_path"])
            self.assertEqual(payload["stderr"], "error: tmdb_id not found")

            selection = read_selection(tmp_path, "2026-07-06")
            self.assertEqual(selection["copies"], {})

    def test_missing_selection_returns_400(self) -> None:
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            _make_batch(tmp_path, "2026-07-06", "09-slug")

            status, payload = route(
                "POST", "/api/publish", {}, {"date": "2026-07-06"}, batch_root=tmp_path
            )

            self.assertEqual(status, 400)
            self.assertFalse(payload["ok"])


class SelectDeletesStaleCopyTests(unittest.TestCase):
    """G8 修复：改选时删旧 {slug}_copy.md，恢复 copy_path=null ⇔ 无 _copy.md 不变量。"""

    def _select(self, tmp_path: Path, slug: str, tmdb_id: int) -> None:
        route(
            "POST",
            "/api/select",
            {},
            {"date": "2026-07-06", "news_slug": slug, "tmdb_id": tmdb_id, "title": slug},
            batch_root=tmp_path,
        )

    def test_reselect_other_slug_deletes_previous_orphan_copy(self) -> None:
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            _make_batch(tmp_path, "2026-07-06", "09-slug")
            _make_batch(tmp_path, "2026-07-06", "10-slug", tmdb_id=99)

            # 选 09-slug 并模拟已 publish 出稿。
            self._select(tmp_path, "09-slug", 429918)
            stale = tmp_path / "2026-07-06" / "09-slug_copy_xiaohongshu.md"
            stale.write_text("旧稿 Rule Breakers", encoding="utf-8")

            # 改选到别的新闻 10-slug：旧孤儿稿应被删除。
            self._select(tmp_path, "10-slug", 99)

            self.assertFalse(stale.exists())
            selection = read_selection(tmp_path, "2026-07-06")
            self.assertEqual(selection["selected"]["news_slug"], "10-slug")
            self.assertEqual(selection["copies"], {})

    def test_reselect_same_slug_deletes_its_copy(self) -> None:
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            _make_batch(tmp_path, "2026-07-06", "09-slug")

            self._select(tmp_path, "09-slug", 429918)
            copy = tmp_path / "2026-07-06" / "09-slug_copy_xiaohongshu.md"
            copy.write_text("已出稿", encoding="utf-8")

            # 重复选同片：其稿也应删除，强制重新 publish。
            self._select(tmp_path, "09-slug", 429918)

            self.assertFalse(copy.exists())

    def test_select_without_existing_copy_is_idempotent(self) -> None:
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            _make_batch(tmp_path, "2026-07-06", "09-slug")

            status, payload = route(
                "POST",
                "/api/select",
                {},
                {"date": "2026-07-06", "news_slug": "09-slug", "tmdb_id": 429918, "title": "Survival Family"},
                batch_root=tmp_path,
            )

            self.assertEqual(status, 200)
            self.assertTrue(payload["ok"])


class SelectionMigrationTests(unittest.TestCase):
    """D4 向后兼容：旧格式（顶层 published/copy_path）读出时应无损迁移为 copies dict。"""

    def test_old_format_selection_is_migrated_losslessly(self) -> None:
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            date = "2026-07-06"
            old_payload = {
                "date": date,
                "selected": {"news_slug": "09-slug", "tmdb_id": 429918, "title": "Survival Family"},
                "selected_at": "2026-07-06T00:00:00+00:00",
                "published": True,
                "copy_path": str(tmp_path / date / "09-slug_copy.md"),
            }
            selection_path = tmp_path / date / "selection.json"
            selection_path.parent.mkdir(parents=True)
            selection_path.write_text(json.dumps(old_payload, ensure_ascii=False), encoding="utf-8")

            migrated = read_selection(tmp_path, date)

            self.assertNotIn("published", migrated)
            self.assertNotIn("copy_path", migrated)
            entry = migrated["copies"]["xiaohongshu"]
            self.assertTrue(entry["published"])
            self.assertEqual(entry["copy_path"], old_payload["copy_path"])
            self.assertIsNone(entry["humanized_path"])
            # selected/selected_at 等其他字段无损保留。
            self.assertEqual(migrated["selected"], old_payload["selected"])
            self.assertEqual(migrated["selected_at"], old_payload["selected_at"])

    def test_new_format_selection_passes_through_unchanged(self) -> None:
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            date = "2026-07-06"
            new_payload = {
                "date": date,
                "selected": {"news_slug": "09-slug", "tmdb_id": 429918, "title": "Survival Family"},
                "selected_at": "2026-07-06T00:00:00+00:00",
                "copies": {
                    "xiaohongshu": {
                        "published": True,
                        "copy_path": "some/path_copy_xiaohongshu.md",
                        "humanized_path": None,
                    }
                },
            }
            selection_path = tmp_path / date / "selection.json"
            selection_path.parent.mkdir(parents=True)
            selection_path.write_text(json.dumps(new_payload, ensure_ascii=False), encoding="utf-8")

            result = read_selection(tmp_path, date)
            self.assertEqual(result, new_payload)


class SelectionRouteTests(unittest.TestCase):
    """9.7.7 · GET /api/selection：刷新后恢复选中态的服务端支点。"""

    def test_missing_date_returns_400(self) -> None:
        with TemporaryDirectory() as tmp:
            status, payload = route("GET", "/api/selection", {}, None, batch_root=Path(tmp))
            self.assertEqual(status, 400)
            self.assertIn("error", payload)

    def test_no_selection_file_returns_200_null(self) -> None:
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            _make_batch(tmp_path, "2026-07-06", "09-slug")
            status, payload = route(
                "GET", "/api/selection", {"date": "2026-07-06"}, None, batch_root=tmp_path
            )
            self.assertEqual(status, 200)
            self.assertIsNone(payload["selection"])

    def test_existing_selection_returned_and_migrated(self) -> None:
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            date = "2026-07-06"
            # 旧格式落盘，验证 /api/selection 返回的是迁移后的 copies dict 形状。
            old_payload = {
                "date": date,
                "selected": {"news_slug": "09-slug", "tmdb_id": 429918, "title": "Survival Family"},
                "selected_at": "2026-07-06T00:00:00+00:00",
                "published": True,
                "copy_path": str(tmp_path / date / "09-slug_copy_xiaohongshu.md"),
            }
            selection_path = tmp_path / date / "selection.json"
            selection_path.parent.mkdir(parents=True)
            selection_path.write_text(json.dumps(old_payload, ensure_ascii=False), encoding="utf-8")

            status, payload = route(
                "GET", "/api/selection", {"date": date}, None, batch_root=tmp_path
            )
            self.assertEqual(status, 200)
            sel = payload["selection"]
            self.assertEqual(sel["selected"]["news_slug"], "09-slug")
            self.assertIn("copies", sel)
            self.assertNotIn("published", sel)
            self.assertTrue(sel["copies"]["xiaohongshu"]["published"])


class ParseCopyMarkdownTests(unittest.TestCase):
    """9.7.3 · parse_copy_markdown 是纯函数，直接喂文本断言即可，不用起 batch_root。"""

    def test_extracts_headline_and_body(self) -> None:
        text = (
            "# 发布定稿 · 2026-07-06 · 小红书\n"
            "\n"
            "这是标题\n"
            "\n"
            "这是正文第一行。\n"
            "\n"
            "## 链接\n"
            "\n"
            "- 电影: https://example.com/movie/1\n"
            "- 新闻: https://example.com/news/1\n"
        )
        result = parse_copy_markdown(text)
        self.assertEqual(result["headline"], "这是标题")
        self.assertEqual(result["body"], "这是正文第一行。")

    def test_multi_paragraph_body_preserved(self) -> None:
        text = (
            "# 发布定稿 · 2026-07-06 · 小红书\n"
            "\n"
            "标题\n"
            "\n"
            "第一段。\n"
            "\n"
            "第二段。\n"
            "\n"
            "## 链接\n"
            "- 电影: https://example.com\n"
        )
        result = parse_copy_markdown(text)
        self.assertEqual(result["headline"], "标题")
        self.assertEqual(result["body"], "第一段。\n\n第二段。")

    def test_missing_links_section_returns_all_remaining_as_body(self) -> None:
        text = "# 发布定稿 · 2026-07-06 · 小红书\n\n标题\n\n正文没有链接分区。\n"
        result = parse_copy_markdown(text)
        self.assertEqual(result["headline"], "标题")
        self.assertEqual(result["body"], "正文没有链接分区。")

    def test_missing_h1_and_content_returns_empty_strings(self) -> None:
        result = parse_copy_markdown("")
        self.assertEqual(result, {"headline": "", "body": ""})


class CopyRouteTests(unittest.TestCase):
    """9.7.3 · GET /api/copy：读 {slug}_copy_{platform}.md，解析 headline/body/humanized。"""

    def _write_copy(self, tmp_path: Path, date: str, slug: str, platform: str = "xiaohongshu") -> Path:
        path = tmp_path / date / f"{slug}_copy_{platform}.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            "# 发布定稿 · " + date + " · 小红书\n\n"
            "原版标题\n\n"
            "原版正文。\n\n"
            "## 链接\n\n"
            "- 电影: https://example.com/movie/1\n"
            "- 新闻: https://example.com/news/1\n",
            encoding="utf-8",
        )
        return path

    def test_returns_parsed_content_when_copy_exists(self) -> None:
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            self._write_copy(tmp_path, "2026-07-06", "09-slug")

            status, payload = route(
                "GET",
                "/api/copy",
                {"date": "2026-07-06", "slug": "09-slug", "platform": "xiaohongshu"},
                None,
                batch_root=tmp_path,
            )

            self.assertEqual(status, 200)
            self.assertEqual(payload["headline"], "原版标题")
            self.assertEqual(payload["body"], "原版正文。")
            self.assertIsNone(payload["humanized_body"])
            self.assertFalse(payload["has_humanized"])
            self.assertEqual(payload["platform"], "xiaohongshu")

    def test_defaults_platform_to_xiaohongshu(self) -> None:
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            self._write_copy(tmp_path, "2026-07-06", "09-slug")

            status, payload = route(
                "GET", "/api/copy", {"date": "2026-07-06", "slug": "09-slug"}, None, batch_root=tmp_path
            )

            self.assertEqual(status, 200)
            self.assertEqual(payload["platform"], "xiaohongshu")

    def test_missing_copy_file_returns_404(self) -> None:
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            status, payload = route(
                "GET",
                "/api/copy",
                {"date": "2026-07-06", "slug": "09-slug"},
                None,
                batch_root=tmp_path,
            )
            self.assertEqual(status, 404)
            self.assertIn("error", payload)

    def test_missing_date_or_slug_returns_400(self) -> None:
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            status, payload = route(
                "GET", "/api/copy", {"slug": "09-slug"}, None, batch_root=tmp_path
            )
            self.assertEqual(status, 400)
            self.assertIn("error", payload)

            status, payload = route(
                "GET", "/api/copy", {"date": "2026-07-06"}, None, batch_root=tmp_path
            )
            self.assertEqual(status, 400)
            self.assertIn("error", payload)

    def test_has_humanized_true_when_humanized_file_present(self) -> None:
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            self._write_copy(tmp_path, "2026-07-06", "09-slug")
            humanized_path = tmp_path / "2026-07-06" / "09-slug_copy_xiaohongshu_humanized.md"
            humanized_path.write_text(
                "# 发布定稿 · 2026-07-06 · 小红书\n\n"
                "去AI化标题\n\n"
                "去AI化正文。\n\n"
                "## 链接\n\n"
                "- 电影: https://example.com/movie/1\n",
                encoding="utf-8",
            )

            status, payload = route(
                "GET",
                "/api/copy",
                {"date": "2026-07-06", "slug": "09-slug"},
                None,
                batch_root=tmp_path,
            )

            self.assertEqual(status, 200)
            self.assertTrue(payload["has_humanized"])
            self.assertEqual(payload["humanized_body"], "去AI化正文。")
            # 原版 body 不受 humanized 影响。
            self.assertEqual(payload["body"], "原版正文。")


class RewriteRouteTests(unittest.TestCase):
    """9.7.4：/api/rewrite 通过注入的 run_subprocess stub 验证，不调真实 LLM。"""

    def _write_copy_md(self, tmp_path: Path, date: str, slug: str, platform: str = "xiaohongshu") -> Path:
        copy_path = tmp_path / date / f"{slug}_copy_{platform}.md"
        copy_path.parent.mkdir(parents=True, exist_ok=True)
        copy_path.write_text(
            "# 发布定稿 · 2026-07-06 · 小红书\n\n"
            "一句标题\n\n"
            "「Survival Family」(2017) 矢口史靖 原版正文。\n\n"
            "## 链接\n\n"
            "- 电影: https://themoviecosmos.com/movie/429918\n"
            "- 新闻: https://example.com/article/1\n",
            encoding="utf-8",
        )
        return copy_path

    def test_success_updates_selection_and_returns_humanized_body(self) -> None:
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            _make_batch(tmp_path, "2026-07-06", "09-slug")
            route(
                "POST",
                "/api/select",
                {},
                {"date": "2026-07-06", "news_slug": "09-slug", "tmdb_id": 429918, "title": "Survival Family"},
                batch_root=tmp_path,
            )
            self._write_copy_md(tmp_path, "2026-07-06", "09-slug")

            humanized_path = tmp_path / "2026-07-06" / "09-slug_copy_xiaohongshu_humanized.md"

            def fake_write_humanized() -> None:
                humanized_path.write_text(
                    "# 发布定稿 · 2026-07-06 · 小红书\n\n"
                    "一句标题\n\n"
                    "「Survival Family」(2017) 矢口史靖 去AI化正文。\n\n"
                    "## 链接\n\n"
                    "- 电影: https://themoviecosmos.com/movie/429918\n"
                    "- 新闻: https://example.com/article/1\n",
                    encoding="utf-8",
                )

            def fake_run_subprocess(cmd, capture_output, text):  # noqa: ANN001
                self.assertIn("--date", cmd)
                self.assertIn("2026-07-06", cmd)
                self.assertIn("--slug", cmd)
                self.assertIn("09-slug", cmd)
                self.assertIn("--platform", cmd)
                self.assertIn("xiaohongshu", cmd)
                fake_write_humanized()
                return SimpleNamespace(
                    returncode=0, stdout="", stderr=f"Wrote {humanized_path}\n"
                )

            status, payload = route(
                "POST",
                "/api/rewrite",
                {},
                {"date": "2026-07-06", "slug": "09-slug", "platform": "xiaohongshu"},
                batch_root=tmp_path,
                run_subprocess=fake_run_subprocess,
            )

            self.assertEqual(status, 200)
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["humanized_path"], str(humanized_path))
            self.assertIn("去AI化正文", payload["humanized_body"])

            selection = read_selection(tmp_path, "2026-07-06")
            entry = selection["copies"]["xiaohongshu"]
            self.assertEqual(entry["humanized_path"], str(humanized_path))
            # copy_path/published 字段应保持原状（本测试未先 publish，故 copy_path 为空占位）。
            self.assertIsNone(entry.get("copy_path"))

    def test_failure_returns_500(self) -> None:
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            _make_batch(tmp_path, "2026-07-06", "09-slug")
            route(
                "POST",
                "/api/select",
                {},
                {"date": "2026-07-06", "news_slug": "09-slug", "tmdb_id": 429918, "title": "Survival Family"},
                batch_root=tmp_path,
            )
            self._write_copy_md(tmp_path, "2026-07-06", "09-slug")

            def fake_run_subprocess(cmd, capture_output, text):  # noqa: ANN001
                return SimpleNamespace(returncode=2, stdout="", stderr="error: empty body")

            status, payload = route(
                "POST",
                "/api/rewrite",
                {},
                {"date": "2026-07-06", "slug": "09-slug"},
                batch_root=tmp_path,
                run_subprocess=fake_run_subprocess,
            )

            self.assertEqual(status, 500)
            self.assertFalse(payload["ok"])
            self.assertIsNone(payload["humanized_path"])
            self.assertEqual(payload["stderr"], "error: empty body")

    def test_slug_fallback_from_selection(self) -> None:
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            _make_batch(tmp_path, "2026-07-06", "09-slug")
            route(
                "POST",
                "/api/select",
                {},
                {"date": "2026-07-06", "news_slug": "09-slug", "tmdb_id": 429918, "title": "Survival Family"},
                batch_root=tmp_path,
            )
            self._write_copy_md(tmp_path, "2026-07-06", "09-slug")
            humanized_path = tmp_path / "2026-07-06" / "09-slug_copy_xiaohongshu_humanized.md"

            def fake_run_subprocess(cmd, capture_output, text):  # noqa: ANN001
                # slug 未在 body 里传，应从 selection.json 兜底解析出 09-slug。
                self.assertIn("--slug", cmd)
                self.assertIn("09-slug", cmd)
                humanized_path.write_text(
                    "# 发布定稿 · 2026-07-06 · 小红书\n\n一句标题\n\n去AI化正文。\n\n## 链接\n\n- 电影: x\n- 新闻: y\n",
                    encoding="utf-8",
                )
                return SimpleNamespace(returncode=0, stdout="", stderr=f"Wrote {humanized_path}\n")

            # body 不含 slug，只给 date，走 selection.json 兜底分支。
            status, payload = route(
                "POST",
                "/api/rewrite",
                {},
                {"date": "2026-07-06"},
                batch_root=tmp_path,
                run_subprocess=fake_run_subprocess,
            )

            self.assertEqual(status, 200)
            self.assertTrue(payload["ok"])


class PublishThenRewriteE2ETests(unittest.TestCase):
    """9.7.5 gap-fill: select→publish→rewrite 全链路，验证 copies.xiaohongshu 三字段。"""

    def test_publish_then_rewrite_preserves_published_and_copy_path(self) -> None:
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            _make_batch(tmp_path, "2026-07-06", "09-slug")
            route(
                "POST",
                "/api/select",
                {},
                {"date": "2026-07-06", "news_slug": "09-slug", "tmdb_id": 429918, "title": "Survival Family"},
                batch_root=tmp_path,
            )

            copy_path = tmp_path / "2026-07-06" / "09-slug_copy_xiaohongshu.md"

            def fake_publish_subprocess(cmd, capture_output, text):  # noqa: ANN001
                copy_path.write_text(
                    "# 发布定稿 · 2026-07-06 · 小红书\n\n一句标题\n\n原版正文。\n\n"
                    "## 链接\n\n- 电影: https://example.com/movie/1\n",
                    encoding="utf-8",
                )
                return SimpleNamespace(returncode=0, stdout="", stderr=f"Wrote {copy_path}\n")

            status, publish_payload = route(
                "POST",
                "/api/publish",
                {},
                {"date": "2026-07-06"},
                batch_root=tmp_path,
                run_subprocess=fake_publish_subprocess,
            )
            self.assertEqual(status, 200)

            humanized_path = tmp_path / "2026-07-06" / "09-slug_copy_xiaohongshu_humanized.md"

            def fake_rewrite_subprocess(cmd, capture_output, text):  # noqa: ANN001
                humanized_path.write_text(
                    "# 发布定稿 · 2026-07-06 · 小红书\n\n一句标题\n\n去AI化正文。\n\n"
                    "## 链接\n\n- 电影: https://example.com/movie/1\n",
                    encoding="utf-8",
                )
                return SimpleNamespace(returncode=0, stdout="", stderr=f"Wrote {humanized_path}\n")

            status, rewrite_payload = route(
                "POST",
                "/api/rewrite",
                {},
                {"date": "2026-07-06"},
                batch_root=tmp_path,
                run_subprocess=fake_rewrite_subprocess,
            )
            self.assertEqual(status, 200)

            selection = read_selection(tmp_path, "2026-07-06")
            entry = selection["copies"]["xiaohongshu"]
            self.assertTrue(entry["published"])
            self.assertEqual(entry["copy_path"], str(copy_path))
            self.assertEqual(entry["humanized_path"], str(humanized_path))


class PublishMigratesOldFormatSelectionTests(unittest.TestCase):
    """9.7.5 gap-fill: handle_publish 读到旧格式 selection.json 时应先迁移再写回。"""

    def test_legacy_selection_migrated_through_handle_publish(self) -> None:
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            date = "2026-07-06"
            _make_batch(tmp_path, date, "09-slug")

            legacy_payload = {
                "date": date,
                "selected": {"news_slug": "09-slug", "tmdb_id": 429918, "title": "Survival Family"},
                "selected_at": "2026-07-06T00:00:00+00:00",
                "published": False,
                "copy_path": None,
            }
            selection_path = tmp_path / date / "selection.json"
            selection_path.parent.mkdir(parents=True, exist_ok=True)
            selection_path.write_text(json.dumps(legacy_payload, ensure_ascii=False), encoding="utf-8")

            expected_copy_path = tmp_path / date / "09-slug_copy_xiaohongshu.md"

            def fake_run_subprocess(cmd, capture_output, text):  # noqa: ANN001
                return SimpleNamespace(
                    returncode=0, stdout="", stderr=f"Wrote {expected_copy_path}\n"
                )

            status, payload = route(
                "POST",
                "/api/publish",
                {},
                {"date": date},
                batch_root=tmp_path,
                run_subprocess=fake_run_subprocess,
            )

            self.assertEqual(status, 200)
            self.assertTrue(payload["ok"])

            selection = read_selection(tmp_path, date)
            self.assertNotIn("published", selection)
            self.assertNotIn("copy_path", selection)
            entry = selection["copies"]["xiaohongshu"]
            self.assertTrue(entry["published"])
            self.assertEqual(entry["copy_path"], str(expected_copy_path))

            # 写回磁盘的原始 JSON 也不应有顶层 published/copy_path 残留。
            raw_on_disk = json.loads(selection_path.read_text(encoding="utf-8"))
            self.assertNotIn("published", raw_on_disk)
            self.assertNotIn("copy_path", raw_on_disk)
            self.assertIn("copies", raw_on_disk)


class ReplaceBodyInCopyMarkdownTests(unittest.TestCase):
    """9.8.4：纯函数，不用起 batch_root，直接喂文本断言。"""

    def test_normal_file_preserves_header_headline_and_links(self) -> None:
        text = (
            "# 发布定稿 · 2026-07-06 · 小红书\n"
            "\n"
            "原版标题\n"
            "\n"
            "原版正文。\n"
            "\n"
            "## 链接\n"
            "\n"
            "- 电影: https://example.com/movie/1\n"
            "- 新闻: https://example.com/news/1\n"
        )
        result = replace_body_in_copy_markdown(text, "新的正文")
        parsed = parse_copy_markdown(result)
        self.assertEqual(parsed["headline"], "原版标题")
        self.assertEqual(parsed["body"], "新的正文")
        self.assertIn("## 链接", result)
        self.assertIn("- 电影: https://example.com/movie/1", result)
        self.assertIn("- 新闻: https://example.com/news/1", result)
        self.assertIn("# 发布定稿 · 2026-07-06 · 小红书", result)

    def test_multi_paragraph_new_body_preserved(self) -> None:
        text = (
            "# 发布定稿 · 2026-07-06 · 小红书\n\n"
            "标题\n\n"
            "旧正文。\n\n"
            "## 链接\n\n"
            "- 电影: https://example.com\n"
        )
        result = replace_body_in_copy_markdown(text, "第一段。\n\n第二段。")
        parsed = parse_copy_markdown(result)
        self.assertEqual(parsed["headline"], "标题")
        self.assertEqual(parsed["body"], "第一段。\n\n第二段。")

    def test_no_links_section_still_works(self) -> None:
        text = "# 发布定稿 · 2026-07-06 · 小红书\n\n标题\n\n旧正文没有链接分区。\n"
        result = replace_body_in_copy_markdown(text, "新正文。")
        parsed = parse_copy_markdown(result)
        self.assertEqual(parsed["headline"], "标题")
        self.assertEqual(parsed["body"], "新正文。")
        self.assertNotIn("## 链接", result)
        self.assertTrue(result.endswith("\n"))


    def test_new_body_containing_h1_and_links_heading_lookalikes_preserved_verbatim(self) -> None:
        # 新正文里若恰好含 "# ..." 或字面 "## 链接" 行，替换逐字保留原链接分区不受干扰
        # （replace_body_in_copy_markdown 只按原文件结构定位链接分区起点，不重新扫描新 body）。
        text = (
            "# 发布定稿 · 2026-07-06 · 小红书\n\n"
            "原版标题\n\n"
            "原版正文。\n\n"
            "## 链接\n\n"
            "- 电影: https://example.com/movie/1\n"
            "- 新闻: https://example.com/news/1\n"
        )
        new_body = "# 这是正文里的一级标题\n\n这段提到了 ## 链接 这个词但不是分区。"
        result = replace_body_in_copy_markdown(text, new_body)
        parsed = parse_copy_markdown(result)

        self.assertEqual(parsed["headline"], "原版标题")
        self.assertEqual(parsed["body"], new_body)
        # 原链接分区完整保留，不被 body 里的字面 "## 链接" 误吞。
        self.assertIn("- 电影: https://example.com/movie/1", result)
        self.assertIn("- 新闻: https://example.com/news/1", result)
        self.assertEqual(result.count("## 链接"), 2)


class EditBodyRouteTests(unittest.TestCase):
    """9.8.4：POST /api/edit-body 无 LLM，纯文本直改。"""

    def _write_copy_md(self, tmp_path: Path, date: str, slug: str, platform: str = "xiaohongshu") -> Path:
        copy_path = tmp_path / date / f"{slug}_copy_{platform}.md"
        copy_path.parent.mkdir(parents=True, exist_ok=True)
        copy_path.write_text(
            "# 发布定稿 · 2026-07-06 · 小红书\n\n"
            "原版标题\n\n"
            "原版正文。\n\n"
            "## 链接\n\n"
            "- 电影: https://example.com/movie/1\n"
            "- 新闻: https://example.com/news/1\n",
            encoding="utf-8",
        )
        return copy_path

    def test_success_updates_body_preserves_headline_and_links_invalidates_humanized(self) -> None:
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            date = "2026-07-06"
            _make_batch(tmp_path, date, "09-slug")
            route(
                "POST",
                "/api/select",
                {},
                {"date": date, "news_slug": "09-slug", "tmdb_id": 429918, "title": "Survival Family"},
                batch_root=tmp_path,
            )
            self._write_copy_md(tmp_path, date, "09-slug")

            humanized_path = tmp_path / date / "09-slug_copy_xiaohongshu_humanized.md"
            humanized_path.write_text("旧 humanized 稿", encoding="utf-8")
            selection = read_selection(tmp_path, date)
            selection["copies"]["xiaohongshu"] = {
                "published": True,
                "copy_path": str(tmp_path / date / "09-slug_copy_xiaohongshu.md"),
                "humanized_path": str(humanized_path),
            }
            from review_panel.serve import write_selection

            write_selection(tmp_path, date, selection)

            status, payload = route(
                "POST",
                "/api/edit-body",
                {},
                {"date": date, "slug": "09-slug", "platform": "xiaohongshu", "body": "新的正文"},
                batch_root=tmp_path,
            )

            self.assertEqual(status, 200)
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["headline"], "原版标题")
            self.assertEqual(payload["body"], "新的正文")

            on_disk = (tmp_path / date / "09-slug_copy_xiaohongshu.md").read_text(encoding="utf-8")
            self.assertIn("- 电影: https://example.com/movie/1", on_disk)
            self.assertIn("- 新闻: https://example.com/news/1", on_disk)

            self.assertFalse(humanized_path.exists())
            updated_selection = read_selection(tmp_path, date)
            self.assertIsNone(updated_selection["copies"]["xiaohongshu"]["humanized_path"])
            self.assertTrue(updated_selection["copies"]["xiaohongshu"]["published"])

    def test_empty_body_returns_400(self) -> None:
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            date = "2026-07-06"
            self._write_copy_md(tmp_path, date, "09-slug")

            status, payload = route(
                "POST",
                "/api/edit-body",
                {},
                {"date": date, "slug": "09-slug", "body": "   "},
                batch_root=tmp_path,
            )
            self.assertEqual(status, 400)
            self.assertFalse(payload["ok"])

    def test_missing_copy_file_returns_404(self) -> None:
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            status, payload = route(
                "POST",
                "/api/edit-body",
                {},
                {"date": "2026-07-06", "slug": "09-slug", "body": "新正文"},
                batch_root=tmp_path,
            )
            self.assertEqual(status, 404)
            self.assertFalse(payload["ok"])

    def test_slug_fallback_from_selection(self) -> None:
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            date = "2026-07-06"
            _make_batch(tmp_path, date, "09-slug")
            route(
                "POST",
                "/api/select",
                {},
                {"date": date, "news_slug": "09-slug", "tmdb_id": 429918, "title": "Survival Family"},
                batch_root=tmp_path,
            )
            self._write_copy_md(tmp_path, date, "09-slug")

            status, payload = route(
                "POST",
                "/api/edit-body",
                {},
                {"date": date, "body": "新正文"},
                batch_root=tmp_path,
            )
            self.assertEqual(status, 200)
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["body"], "新正文")


class RegenerateRouteTests(unittest.TestCase):
    """9.8.4：POST /api/regenerate 通过注入 run_subprocess stub 验证，不调真实 LLM。"""

    def _write_copy_md(self, tmp_path: Path, date: str, slug: str, platform: str = "xiaohongshu") -> Path:
        copy_path = tmp_path / date / f"{slug}_copy_{platform}.md"
        copy_path.parent.mkdir(parents=True, exist_ok=True)
        copy_path.write_text(
            "# 发布定稿 · 2026-07-06 · 小红书\n\n"
            "原版标题\n\n"
            "原版正文。\n\n"
            "## 链接\n\n"
            "- 电影: https://example.com/movie/1\n"
            "- 新闻: https://example.com/news/1\n",
            encoding="utf-8",
        )
        return copy_path

    def _select(self, tmp_path: Path, date: str, slug: str = "09-slug", tmdb_id: int = 429918) -> None:
        _make_batch(tmp_path, date, slug, tmdb_id=tmdb_id)
        route(
            "POST",
            "/api/select",
            {},
            {"date": date, "news_slug": slug, "tmdb_id": tmdb_id, "title": "Survival Family"},
            batch_root=tmp_path,
        )

    def test_target_body_clears_humanized_path(self) -> None:
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            date = "2026-07-06"
            self._select(tmp_path, date)
            copy_path = self._write_copy_md(tmp_path, date, "09-slug")

            humanized_path = tmp_path / date / "09-slug_copy_xiaohongshu_humanized.md"
            humanized_path.write_text("旧 humanized", encoding="utf-8")
            selection = read_selection(tmp_path, date)
            selection["copies"]["xiaohongshu"] = {
                "published": True,
                "copy_path": str(copy_path),
                "humanized_path": str(humanized_path),
            }
            from review_panel.serve import write_selection

            write_selection(tmp_path, date, selection)

            def fake_run_subprocess(cmd, capture_output, text):  # noqa: ANN001
                self.assertIn("--target", cmd)
                self.assertIn("body", cmd)
                self.assertIn("--tmdb-id", cmd)
                self.assertIn("429918", cmd)
                self.assertIn("--slug", cmd)
                self.assertIn("09-slug", cmd)
                self.assertIn("--date", cmd)
                self.assertIn(date, cmd)
                copy_path.write_text(
                    "# 发布定稿 · 2026-07-06 · 小红书\n\n"
                    "原版标题\n\n"
                    "新的正文。\n\n"
                    "## 链接\n\n"
                    "- 电影: https://example.com/movie/1\n"
                    "- 新闻: https://example.com/news/1\n",
                    encoding="utf-8",
                )
                humanized_path.unlink()
                return SimpleNamespace(returncode=0, stdout="", stderr=f"Wrote {copy_path}\n")

            status, payload = route(
                "POST",
                "/api/regenerate",
                {},
                {"date": date, "slug": "09-slug", "platform": "xiaohongshu", "target": "body"},
                batch_root=tmp_path,
                run_subprocess=fake_run_subprocess,
            )

            self.assertEqual(status, 200)
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["target"], "body")
            self.assertEqual(payload["body"], "新的正文。")
            self.assertEqual(payload["headline"], "原版标题")

            updated_selection = read_selection(tmp_path, date)
            self.assertIsNone(updated_selection["copies"]["xiaohongshu"]["humanized_path"])

    def test_target_headline_does_not_clear_humanized_path(self) -> None:
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            date = "2026-07-06"
            self._select(tmp_path, date)
            copy_path = self._write_copy_md(tmp_path, date, "09-slug")

            humanized_path = tmp_path / date / "09-slug_copy_xiaohongshu_humanized.md"
            humanized_path.write_text("旧 humanized", encoding="utf-8")
            selection = read_selection(tmp_path, date)
            selection["copies"]["xiaohongshu"] = {
                "published": True,
                "copy_path": str(copy_path),
                "humanized_path": str(humanized_path),
            }
            from review_panel.serve import write_selection

            write_selection(tmp_path, date, selection)

            def fake_run_subprocess(cmd, capture_output, text):  # noqa: ANN001
                copy_path.write_text(
                    "# 发布定稿 · 2026-07-06 · 小红书\n\n"
                    "新的标题\n\n"
                    "原版正文。\n\n"
                    "## 链接\n\n"
                    "- 电影: https://example.com/movie/1\n"
                    "- 新闻: https://example.com/news/1\n",
                    encoding="utf-8",
                )
                return SimpleNamespace(returncode=0, stdout="", stderr=f"Wrote {copy_path}\n")

            status, payload = route(
                "POST",
                "/api/regenerate",
                {},
                {"date": date, "slug": "09-slug", "platform": "xiaohongshu", "target": "headline"},
                batch_root=tmp_path,
                run_subprocess=fake_run_subprocess,
            )

            self.assertEqual(status, 200)
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["headline"], "新的标题")
            self.assertEqual(payload["body"], "原版正文。")

            updated_selection = read_selection(tmp_path, date)
            self.assertEqual(
                updated_selection["copies"]["xiaohongshu"]["humanized_path"], str(humanized_path)
            )

    def test_invalid_target_returns_400(self) -> None:
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            date = "2026-07-06"
            self._select(tmp_path, date)

            status, payload = route(
                "POST",
                "/api/regenerate",
                {},
                {"date": date, "slug": "09-slug", "target": "nope"},
                batch_root=tmp_path,
            )
            self.assertEqual(status, 400)
            self.assertFalse(payload["ok"])

    def test_missing_selection_returns_400(self) -> None:
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            date = "2026-07-06"
            _make_batch(tmp_path, date, "09-slug")

            status, payload = route(
                "POST",
                "/api/regenerate",
                {},
                {"date": date, "target": "body"},
                batch_root=tmp_path,
            )
            self.assertEqual(status, 400)
            self.assertFalse(payload["ok"])

    def test_subprocess_failure_returns_500(self) -> None:
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            date = "2026-07-06"
            self._select(tmp_path, date)
            self._write_copy_md(tmp_path, date, "09-slug")

            def fake_run_subprocess(cmd, capture_output, text):  # noqa: ANN001
                return SimpleNamespace(returncode=2, stdout="", stderr="error: something broke")

            status, payload = route(
                "POST",
                "/api/regenerate",
                {},
                {"date": date, "slug": "09-slug", "target": "body"},
                batch_root=tmp_path,
                run_subprocess=fake_run_subprocess,
            )
            self.assertEqual(status, 500)
            self.assertFalse(payload["ok"])
            self.assertEqual(payload["stderr"], "error: something broke")


class GenerateDraftsRouteTests(unittest.TestCase):
    """10.4：POST /api/generate-drafts 通过注入 run_subprocess stub 验证，不调真实 LLM。"""

    def _write_pool(self, tmp_path: Path, date: str, slug: str, pool: list, platform: str = "xiaohongshu") -> Path:
        path = tmp_path / date / f"{slug}_drafts_{platform}.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(pool, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return path

    def test_success_returns_pool_and_asserts_cmd(self) -> None:
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            date = "2026-07-06"
            _make_batch(tmp_path, date, "09-slug")
            route(
                "POST",
                "/api/select",
                {},
                {"date": date, "news_slug": "09-slug", "tmdb_id": 429918, "title": "Survival Family"},
                batch_root=tmp_path,
            )
            pool = [
                {"draft_id": "The-Sage", "headline": "理性之眼", "body": "「Survival Family」以求真视角。"},
                {"draft_id": "The-Hero", "headline": "抗争之路", "body": "「Survival Family」以抗争视角。"},
            ]
            pool_path = self._write_pool(tmp_path, date, "09-slug", pool)

            def fake_run_subprocess(cmd, capture_output, text):  # noqa: ANN001
                self.assertIn("--date", cmd)
                self.assertIn(date, cmd)
                self.assertIn("--news-slug", cmd)
                self.assertIn("09-slug", cmd)
                self.assertIn("--tmdb-id", cmd)
                self.assertIn("429918", cmd)
                self.assertIn("--platform", cmd)
                self.assertIn("xiaohongshu", cmd)
                # 全量扇出无 --combine。
                self.assertNotIn("--combine", cmd)
                return SimpleNamespace(returncode=0, stdout="", stderr=f"Wrote {pool_path}\n")

            status, payload = route(
                "POST",
                "/api/generate-drafts",
                {},
                {"date": date},
                batch_root=tmp_path,
                run_subprocess=fake_run_subprocess,
            )

            self.assertEqual(status, 200)
            self.assertTrue(payload["ok"])
            self.assertEqual(len(payload["drafts"]), 2)
            self.assertEqual(payload["drafts"][0]["draft_id"], "The-Sage")

    def test_missing_selection_returns_400(self) -> None:
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            _make_batch(tmp_path, "2026-07-06", "09-slug")

            status, payload = route(
                "POST", "/api/generate-drafts", {}, {"date": "2026-07-06"}, batch_root=tmp_path
            )
            self.assertEqual(status, 400)
            self.assertFalse(payload["ok"])

    def test_missing_date_returns_400(self) -> None:
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            status, payload = route("POST", "/api/generate-drafts", {}, {}, batch_root=tmp_path)
            self.assertEqual(status, 400)
            self.assertFalse(payload["ok"])

    def test_subprocess_failure_returns_500(self) -> None:
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            date = "2026-07-06"
            _make_batch(tmp_path, date, "09-slug")
            route(
                "POST",
                "/api/select",
                {},
                {"date": date, "news_slug": "09-slug", "tmdb_id": 429918, "title": "Survival Family"},
                batch_root=tmp_path,
            )

            def fake_run_subprocess(cmd, capture_output, text):  # noqa: ANN001
                return SimpleNamespace(returncode=2, stdout="", stderr="error: empty triggered_by")

            status, payload = route(
                "POST",
                "/api/generate-drafts",
                {},
                {"date": date},
                batch_root=tmp_path,
                run_subprocess=fake_run_subprocess,
            )
            self.assertEqual(status, 500)
            self.assertFalse(payload["ok"])
            self.assertEqual(payload["stderr"], "error: empty triggered_by")


class SelectDraftRouteTests(unittest.TestCase):
    """10.4：POST /api/select-draft 无 LLM，指针派生当前稿 + 失效 humanized + 写 selected_draft_id。"""

    def _setup_pool(self, tmp_path: Path, date: str, slug: str = "09-slug") -> Path:
        _make_batch(tmp_path, date, slug)
        route(
            "POST",
            "/api/select",
            {},
            {"date": date, "news_slug": slug, "tmdb_id": 429918, "title": "Survival Family"},
            batch_root=tmp_path,
        )
        pool = [
            {"draft_id": "The-Sage", "headline": "理性之眼", "body": "「Survival Family」以求真视角写正文。"},
            {"draft_id": "The-Hero", "headline": "抗争之路", "body": "「Survival Family」以抗争视角写正文。"},
        ]
        pool_path = tmp_path / date / f"{slug}_drafts_xiaohongshu.json"
        pool_path.write_text(json.dumps(pool, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return pool_path

    def test_derives_current_copy_and_writes_pointer(self) -> None:
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            date = "2026-07-06"
            self._setup_pool(tmp_path, date)

            status, payload = route(
                "POST",
                "/api/select-draft",
                {},
                {"date": date, "draft_id": "The-Hero"},
                batch_root=tmp_path,
            )

            self.assertEqual(status, 200)
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["headline"], "抗争之路")
            self.assertEqual(payload["selected_draft_id"], "The-Hero")

            copy_path = tmp_path / date / "09-slug_copy_xiaohongshu.md"
            self.assertTrue(copy_path.is_file())
            on_disk = copy_path.read_text(encoding="utf-8")
            # 派生当前稿逐字对齐 publish 产出：headline + body + 链接分区（movie_url 来自 retrieve.json）。
            self.assertIn("抗争之路", on_disk)
            self.assertIn("## 链接", on_disk)
            self.assertIn("https://themoviecosmos.com/movie/429918", on_disk)

            selection = read_selection(tmp_path, date)
            entry = selection["copies"]["xiaohongshu"]
            self.assertEqual(entry["selected_draft_id"], "The-Hero")
            self.assertTrue(entry["published"])
            self.assertEqual(entry["copy_path"], str(copy_path))
            self.assertIsNone(entry["humanized_path"])

    def test_reselect_invalidates_humanized(self) -> None:
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            date = "2026-07-06"
            self._setup_pool(tmp_path, date)
            route("POST", "/api/select-draft", {}, {"date": date, "draft_id": "The-Sage"}, batch_root=tmp_path)

            # 模拟已跑过去AI化：humanized 稿存在 + selection 记录 humanized_path。
            humanized_path = tmp_path / date / "09-slug_copy_xiaohongshu_humanized.md"
            humanized_path.write_text("旧去AI化稿", encoding="utf-8")
            selection = read_selection(tmp_path, date)
            selection["copies"]["xiaohongshu"]["humanized_path"] = str(humanized_path)
            from review_panel.serve import write_selection

            write_selection(tmp_path, date, selection)

            # 改选另一张卡：body 变 ⇒ humanized 必须失效。
            status, payload = route(
                "POST", "/api/select-draft", {}, {"date": date, "draft_id": "The-Hero"}, batch_root=tmp_path
            )
            self.assertEqual(status, 200)
            self.assertFalse(humanized_path.exists())
            entry = read_selection(tmp_path, date)["copies"]["xiaohongshu"]
            self.assertIsNone(entry["humanized_path"])
            self.assertEqual(entry["selected_draft_id"], "The-Hero")

    def test_legacy_selection_without_pointer_field_is_backward_compatible(self) -> None:
        # 向后兼容（ADR-0017 D4）：旧 selection 的 copies 条目无 selected_draft_id 字段
        # （Phase 10 前发布产生），select-draft 应正常补上指针而不报错。
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            date = "2026-07-06"
            self._setup_pool(tmp_path, date)

            # 构造一个缺 selected_draft_id 的旧格式条目（含 published/copy_path/humanized_path）。
            from review_panel.serve import write_selection

            selection = read_selection(tmp_path, date)
            legacy_humanized = tmp_path / date / "09-slug_copy_xiaohongshu_humanized.md"
            legacy_humanized.write_text("旧去AI化稿（Phase 10 前）", encoding="utf-8")
            selection.setdefault("copies", {})["xiaohongshu"] = {
                "published": True,
                "copy_path": str(tmp_path / date / "09-slug_copy_xiaohongshu.md"),
                "humanized_path": str(legacy_humanized),
            }
            write_selection(tmp_path, date, selection)

            status, payload = route(
                "POST", "/api/select-draft", {}, {"date": date, "draft_id": "The-Sage"}, batch_root=tmp_path
            )

            self.assertEqual(status, 200)
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["selected_draft_id"], "The-Sage")
            # 旧 humanized 稿随 body 变而失效。
            self.assertFalse(legacy_humanized.exists())
            entry = read_selection(tmp_path, date)["copies"]["xiaohongshu"]
            self.assertEqual(entry["selected_draft_id"], "The-Sage")
            self.assertIsNone(entry["humanized_path"])

    def test_unknown_draft_id_returns_400(self) -> None:
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            date = "2026-07-06"
            self._setup_pool(tmp_path, date)

            status, payload = route(
                "POST", "/api/select-draft", {}, {"date": date, "draft_id": "The-Nobody"}, batch_root=tmp_path
            )
            self.assertEqual(status, 400)
            self.assertFalse(payload["ok"])
            self.assertIn("not in pool", payload["error"])

    def test_missing_pool_returns_404(self) -> None:
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            date = "2026-07-06"
            _make_batch(tmp_path, date, "09-slug")
            route(
                "POST",
                "/api/select",
                {},
                {"date": date, "news_slug": "09-slug", "tmdb_id": 429918, "title": "Survival Family"},
                batch_root=tmp_path,
            )

            status, payload = route(
                "POST", "/api/select-draft", {}, {"date": date, "draft_id": "The-Sage"}, batch_root=tmp_path
            )
            self.assertEqual(status, 404)
            self.assertFalse(payload["ok"])

    def test_missing_draft_id_returns_400(self) -> None:
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            status, payload = route(
                "POST", "/api/select-draft", {}, {"date": "2026-07-06"}, batch_root=tmp_path
            )
            self.assertEqual(status, 400)
            self.assertFalse(payload["ok"])


class CombineDraftsRouteTests(unittest.TestCase):
    """10.4：POST /api/combine-drafts 恒调单版 subprocess；>2 由 serve 直接 4xx 拦掉。"""

    def _setup(self, tmp_path: Path, date: str, slug: str = "09-slug") -> Path:
        _make_batch(tmp_path, date, slug)
        route(
            "POST",
            "/api/select",
            {},
            {"date": date, "news_slug": slug, "tmdb_id": 429918, "title": "Survival Family"},
            batch_root=tmp_path,
        )
        pool = [
            {"draft_id": "The-Sage", "headline": "理性之眼", "body": "求真正文。"},
            {"draft_id": "The-Hero", "headline": "抗争之路", "body": "抗争正文。"},
        ]
        pool_path = tmp_path / date / f"{slug}_drafts_xiaohongshu.json"
        pool_path.write_text(json.dumps(pool, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return pool_path

    def test_combine_two_appends_single_version(self) -> None:
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            date = "2026-07-06"
            pool_path = self._setup(tmp_path, date)

            def fake_run_subprocess(cmd, capture_output, text):  # noqa: ANN001
                self.assertIn("--combine", cmd)
                self.assertIn("The-Sage,The-Hero", cmd)
                # serve 恒调单版：绝不传 --combine-mode both。
                self.assertNotIn("--combine-mode", cmd)
                self.assertNotIn("both", cmd)
                pool = json.loads(pool_path.read_text(encoding="utf-8"))
                pool.append({"draft_id": "The-Sage+The-Hero", "headline": "融合", "body": "融合正文。"})
                pool_path.write_text(json.dumps(pool, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
                return SimpleNamespace(returncode=0, stdout="", stderr=f"Wrote {pool_path}\n")

            status, payload = route(
                "POST",
                "/api/combine-drafts",
                {},
                {"date": date, "draft_ids": ["The-Sage", "The-Hero"]},
                batch_root=tmp_path,
                run_subprocess=fake_run_subprocess,
            )

            self.assertEqual(status, 200)
            self.assertTrue(payload["ok"])
            self.assertEqual(len(payload["drafts"]), 3)
            self.assertEqual(payload["drafts"][-1]["draft_id"], "The-Sage+The-Hero")

    def test_more_than_two_returns_400_without_subprocess(self) -> None:
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            date = "2026-07-06"
            self._setup(tmp_path, date)

            called = {"n": 0}

            def fake_run_subprocess(cmd, capture_output, text):  # noqa: ANN001
                called["n"] += 1
                return SimpleNamespace(returncode=0, stdout="", stderr="")

            status, payload = route(
                "POST",
                "/api/combine-drafts",
                {},
                {"date": date, "draft_ids": ["The-Sage", "The-Hero", "The-Lover"]},
                batch_root=tmp_path,
                run_subprocess=fake_run_subprocess,
            )
            self.assertEqual(status, 400)
            self.assertFalse(payload["ok"])
            # >2 应在 serve 层直接拦下，绝不启动 subprocess。
            self.assertEqual(called["n"], 0)

    def test_non_list_draft_ids_returns_400(self) -> None:
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            date = "2026-07-06"
            self._setup(tmp_path, date)
            status, payload = route(
                "POST",
                "/api/combine-drafts",
                {},
                {"date": date, "draft_ids": "The-Sage"},
                batch_root=tmp_path,
            )
            self.assertEqual(status, 400)
            self.assertFalse(payload["ok"])


class UnknownRouteTests(unittest.TestCase):
    def test_unknown_path_returns_404(self) -> None:
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            status, payload = route("GET", "/api/nope", {}, None, batch_root=tmp_path)
            self.assertEqual(status, 404)
            self.assertIn("error", payload)


if __name__ == "__main__":
    unittest.main()