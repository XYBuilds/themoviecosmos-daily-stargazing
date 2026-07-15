"""Unit tests for Phase 8.3 review_panel/serve.py.

优先测纯路由函数 route()（不起真实端口），符合 serve.py 里「传输层与路由逻辑
解耦」的设计：造临时 batch_root + mini 数据，直接调 route() 验证行为。
"""

from __future__ import annotations

import json
import shutil
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace

from review_panel.job_store import JobStore, _inline_executor
from review_panel.publication_bundle import manifest_path, new_manifest, read_manifest, write_manifest
from review_panel.serve import (
    parse_copy_markdown,
    read_selection,
    replace_body_in_copy_markdown,
    route,
)


class _InlineJobStore(JobStore):
    """测试专用：submit 默认用 inline executor，让 job 在 submit() 内同步跑完。

    生产代码零改动——只在测试里覆写 executor 的默认值，使这 6 个已异步化的端点
    在单测里表现为「提交即完成」，可以立即用 GET /api/job 查到 status="done"。
    """

    def submit(self, work, kind, *, executor=_inline_executor):  # noqa: ANN001
        return super().submit(work, kind, executor=executor)


def _run_job_and_get_result(tmp_path, job_store, job_id):
    """两段式断言辅助：轮询 /api/job 直到读出终态，返回 (job_http_status, job_payload)。"""
    status, payload = route(
        "GET", "/api/job", {"job_id": job_id}, None, batch_root=tmp_path, job_store=job_store
    )
    return status, payload


def _submit_async(tmp_path, path, body, *, expected_kind, run_subprocess=None):
    """六个异步端点的公共两段式调用：提交 job（断言 202+kind）→ inline 跑完 → 取回 result。

    返回 ``(result_http_status, result_payload)``，正是原来同步端点的 (status, payload)
    形状，供各测试用例直接沿用改造前的断言语句，只需把 ``route(...)`` 换成
    ``_submit_async(...)`` 即可。
    """
    job_store = _InlineJobStore()
    kwargs = {"batch_root": tmp_path, "job_store": job_store}
    if run_subprocess is not None:
        kwargs["run_subprocess"] = run_subprocess
    submit_status, submit_payload = route("POST", path, {}, body, **kwargs)
    assert submit_status == 202, f"expected 202, got {submit_status}: {submit_payload}"
    assert submit_payload["ok"] is True
    assert submit_payload["kind"] == expected_kind
    job_id = submit_payload["job_id"]
    job_status, job_payload = _run_job_and_get_result(tmp_path, job_store, job_id)
    assert job_status == 200
    assert job_payload["status"] == "done"
    result = job_payload["result"]
    return result["http_status"], result["payload"]


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


def _prepare_bundle_for_selection(batch_root: Path, date: str) -> Path:
    selection = read_selection(batch_root, date)
    assert selection is not None
    selected = selection["selected"]
    assert isinstance(selected, dict)
    path = manifest_path(batch_root, date, selected["tmdb_id"], selected["title"])
    expected_selection = {
        "date": date,
        "news_slug": selected["news_slug"],
        "tmdb_id": selected["tmdb_id"],
        "title": selected["title"],
        "selected_at": selection["selected_at"],
    }
    if path.is_file() and read_manifest(path)["selection"] != expected_selection:
        shutil.rmtree(path.parent)
    if not path.is_file():
        write_manifest(path, new_manifest(expected_selection))
    return path


def _bundle_copy_paths(batch_root: Path, date: str) -> tuple[Path, Path, Path]:
    manifest_file = _prepare_bundle_for_selection(batch_root, date)
    bundle_root = manifest_file.parent
    return manifest_file, bundle_root / "copy" / "xiaohongshu.md", bundle_root / "copy" / "xiaohongshu-humanized.md"


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
            self.assertEqual(set(selection), {"date", "selected", "selected_at"})
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

            _, expected_copy_path, _ = _bundle_copy_paths(tmp_path, "2026-07-06")

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

            job_store = _InlineJobStore()
            status, payload = route(
                "POST",
                "/api/publish",
                {},
                {"date": "2026-07-06"},
                batch_root=tmp_path,
                run_subprocess=fake_run_subprocess,
                job_store=job_store,
            )
            self.assertEqual(status, 202)
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["kind"], "publish")
            job_id = payload["job_id"]

            job_status, job_payload = _run_job_and_get_result(tmp_path, job_store, job_id)
            self.assertEqual(job_status, 200)
            self.assertEqual(job_payload["status"], "done")
            result = job_payload["result"]
            self.assertEqual(result["http_status"], 200)
            payload = result["payload"]
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["copy_path"], str(expected_copy_path))

            manifest = read_manifest(_prepare_bundle_for_selection(tmp_path, "2026-07-06"))
            entry = manifest["artifacts"]["copies"]["xiaohongshu"]
            self.assertEqual(entry["status"], "ready")
            self.assertEqual(entry["copy_path"], "copy/xiaohongshu.md")
            self.assertIsNone(entry["selected_draft_id"])

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
            _prepare_bundle_for_selection(tmp_path, "2026-07-06")

            def fake_run_subprocess(cmd, capture_output, text):  # noqa: ANN001
                return SimpleNamespace(returncode=2, stdout="", stderr="error: tmdb_id not found")

            job_store = _InlineJobStore()
            status, payload = route(
                "POST",
                "/api/publish",
                {},
                {"date": "2026-07-06"},
                batch_root=tmp_path,
                run_subprocess=fake_run_subprocess,
                job_store=job_store,
            )
            self.assertEqual(status, 202)
            job_id = payload["job_id"]

            job_status, job_payload = _run_job_and_get_result(tmp_path, job_store, job_id)
            self.assertEqual(job_status, 200)
            self.assertEqual(job_payload["status"], "done")
            result = job_payload["result"]
            # handle_publish 内部返回 500 是正常返回不是抛异常，job 仍是 done。
            self.assertEqual(result["http_status"], 500)
            payload = result["payload"]
            self.assertFalse(payload["ok"])
            self.assertIsNone(payload["copy_path"])
            self.assertEqual(payload["stderr"], "error: tmdb_id not found")

            selection = read_selection(tmp_path, "2026-07-06")
            self.assertEqual(set(selection), {"date", "selected", "selected_at"})

    def test_missing_selection_returns_400(self) -> None:
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            _make_batch(tmp_path, "2026-07-06", "09-slug")

            job_store = _InlineJobStore()
            status, payload = route(
                "POST",
                "/api/publish",
                {},
                {"date": "2026-07-06"},
                batch_root=tmp_path,
                job_store=job_store,
            )
            self.assertEqual(status, 202)
            job_id = payload["job_id"]

            job_status, job_payload = _run_job_and_get_result(tmp_path, job_store, job_id)
            self.assertEqual(job_payload["status"], "done")
            result = job_payload["result"]
            self.assertEqual(result["http_status"], 400)
            self.assertFalse(result["payload"]["ok"])


class SelectSupersededBundleTests(unittest.TestCase):
    """Phase 13：改选仅标记旧 bundle 为 superseded，不删除任何历史产物。"""

    def _select(self, tmp_path: Path, slug: str, tmdb_id: int) -> None:
        route(
            "POST",
            "/api/select",
            {},
            {"date": "2026-07-06", "news_slug": slug, "tmdb_id": tmdb_id, "title": slug},
            batch_root=tmp_path,
        )

    def test_reselect_other_candidate_supersedes_and_preserves_previous_bundle(self) -> None:
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            _make_batch(tmp_path, "2026-07-06", "09-slug")
            _make_batch(tmp_path, "2026-07-06", "10-slug", tmdb_id=99)

            self._select(tmp_path, "09-slug", 429918)
            manifest_file = _prepare_bundle_for_selection(tmp_path, "2026-07-06")
            copy_path = manifest_file.parent / "copy" / "xiaohongshu.md"
            copy_path.parent.mkdir(parents=True, exist_ok=True)
            copy_path.write_text("审计保留", encoding="utf-8")

            self._select(tmp_path, "10-slug", 99)

            self.assertTrue(copy_path.is_file())
            self.assertEqual(read_manifest(manifest_file)["status"], "superseded")
            selection = read_selection(tmp_path, "2026-07-06")
            self.assertEqual(selection["selected"]["news_slug"], "10-slug")
            self.assertEqual(set(selection), {"date", "selected", "selected_at"})

    def test_reselect_same_candidate_is_idempotent_and_keeps_bundle(self) -> None:
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            _make_batch(tmp_path, "2026-07-06", "09-slug")

            self._select(tmp_path, "09-slug", 429918)
            manifest_file = _prepare_bundle_for_selection(tmp_path, "2026-07-06")
            copy_path = manifest_file.parent / "copy" / "xiaohongshu.md"
            copy_path.parent.mkdir(parents=True, exist_ok=True)
            copy_path.write_text("已出稿", encoding="utf-8")

            self._select(tmp_path, "09-slug", 429918)

            self.assertTrue(copy_path.is_file())
            self.assertNotEqual(read_manifest(manifest_file)["status"], "superseded")

    def test_select_without_existing_bundle_is_idempotent(self) -> None:
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


class DraftsGetRouteTests(unittest.TestCase):
    """10.5.1 · GET /api/drafts：刷新后把只读草稿池读回前端，恢复 pick（选型）阶段。"""

    def test_missing_params_returns_400(self) -> None:
        with TemporaryDirectory() as tmp:
            status, payload = route(
                "GET", "/api/drafts", {"date": "2026-07-06"}, None, batch_root=Path(tmp)
            )
            self.assertEqual(status, 400)
            self.assertIn("error", payload)

    def test_no_pool_file_returns_200_empty(self) -> None:
        # 「还没产池」是正常态：200 + 空数组（前端据此留在选片视图），而非 404。
        with TemporaryDirectory() as tmp:
            status, payload = route(
                "GET",
                "/api/drafts",
                {"date": "2026-07-06", "slug": "09-slug"},
                None,
                batch_root=Path(tmp),
            )
            self.assertEqual(status, 200)
            self.assertEqual(payload["drafts"], [])

    def test_existing_pool_returned(self) -> None:
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            date = "2026-07-06"
            pool = [
                {"draft_id": "The-Sage", "headline": "理性之眼", "body": "以求真视角。"},
                {"draft_id": "The-Hero", "headline": "抗争之路", "body": "以抗争视角。"},
            ]
            pool_path = tmp_path / date / "09-slug_drafts_xiaohongshu.json"
            pool_path.parent.mkdir(parents=True)
            pool_path.write_text(
                json.dumps(pool, ensure_ascii=False, indent=2), encoding="utf-8"
            )
            status, payload = route(
                "GET",
                "/api/drafts",
                {"date": date, "slug": "09-slug"},
                None,
                batch_root=tmp_path,
            )
            self.assertEqual(status, 200)
            self.assertEqual(len(payload["drafts"]), 2)
            self.assertEqual(payload["drafts"][0]["draft_id"], "The-Sage")
            self.assertEqual(payload["platform"], "xiaohongshu")


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

    def test_missing_date_or_slug_returns_4xx(self) -> None:
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
            self.assertEqual(status, 404)
            self.assertIn("error", payload)

    def test_has_humanized_true_when_bundle_humanized_file_present(self) -> None:
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
            _, copy_path, humanized_path = _bundle_copy_paths(tmp_path, "2026-07-06")
            copy_path.parent.mkdir(parents=True, exist_ok=True)
            copy_path.write_text(
                "# 发布定稿 · 2026-07-06 · 小红书\n\n"
                "原版标题\n\n"
                "原版正文。\n\n"
                "## 链接\n\n"
                "- 电影: https://example.com/movie/1\n",
                encoding="utf-8",
            )
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
                {"date": "2026-07-06"},
                None,
                batch_root=tmp_path,
            )

            self.assertEqual(status, 200)
            self.assertTrue(payload["has_humanized"])
            self.assertEqual(payload["humanized_body"], "去AI化正文。")
            self.assertEqual(payload["body"], "原版正文。")


class RewriteRouteTests(unittest.TestCase):
    """9.7.4：/api/rewrite 通过注入的 run_subprocess stub 验证，不调真实 LLM。"""

    def _write_copy_md(self, tmp_path: Path, date: str, slug: str, platform: str = "xiaohongshu") -> Path:
        _, copy_path, _ = _bundle_copy_paths(tmp_path, date)
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

            _, _, humanized_path = _bundle_copy_paths(tmp_path, "2026-07-06")

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

            status, payload = _submit_async(
                tmp_path,
                "/api/rewrite",
                {"date": "2026-07-06", "slug": "09-slug", "platform": "xiaohongshu"},
                expected_kind="rewrite",
                run_subprocess=fake_run_subprocess,
            )

            self.assertEqual(status, 200)
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["humanized_path"], str(humanized_path))
            self.assertIn("去AI化正文", payload["humanized_body"])

            manifest = read_manifest(_prepare_bundle_for_selection(tmp_path, "2026-07-06"))
            entry = manifest["artifacts"]["copies"]["xiaohongshu"]
            self.assertEqual(entry["status"], "ready")
            self.assertEqual(entry["humanized_path"], "copy/xiaohongshu-humanized.md")
            self.assertEqual(entry["copy_path"], "copy/xiaohongshu.md")

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

            status, payload = _submit_async(
                tmp_path,
                "/api/rewrite",
                {"date": "2026-07-06", "slug": "09-slug"},
                expected_kind="rewrite",
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
            _, _, humanized_path = _bundle_copy_paths(tmp_path, "2026-07-06")

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
            status, payload = _submit_async(
                tmp_path,
                "/api/rewrite",
                {"date": "2026-07-06"},
                expected_kind="rewrite",
                run_subprocess=fake_run_subprocess,
            )

            self.assertEqual(status, 200)
            self.assertTrue(payload["ok"])


class PublishThenRewriteE2ETests(unittest.TestCase):
    """Phase 13：select → bundle current copy → humanized 只写 manifest。"""

    def test_publish_then_rewrite_updates_manifest_paths(self) -> None:
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
            _, copy_path, humanized_path = _bundle_copy_paths(tmp_path, "2026-07-06")

            def fake_publish_subprocess(cmd, capture_output, text):  # noqa: ANN001
                copy_path.parent.mkdir(parents=True, exist_ok=True)
                copy_path.write_text(
                    "# 发布定稿 · 2026-07-06 · 小红书\n\n一句标题\n\n原版正文。\n\n"
                    "## 链接\n\n- 电影: https://example.com/movie/1\n",
                    encoding="utf-8",
                )
                return SimpleNamespace(returncode=0, stdout="", stderr=f"Wrote {copy_path}\n")

            status, _ = _submit_async(
                tmp_path,
                "/api/publish",
                {"date": "2026-07-06"},
                expected_kind="publish",
                run_subprocess=fake_publish_subprocess,
            )
            self.assertEqual(status, 200)

            def fake_rewrite_subprocess(cmd, capture_output, text):  # noqa: ANN001
                humanized_path.write_text(
                    "# 发布定稿 · 2026-07-06 · 小红书\n\n一句标题\n\n去AI化正文。\n\n"
                    "## 链接\n\n- 电影: https://example.com/movie/1\n",
                    encoding="utf-8",
                )
                return SimpleNamespace(returncode=0, stdout="", stderr=f"Wrote {humanized_path}\n")

            status, _ = _submit_async(
                tmp_path,
                "/api/rewrite",
                {"date": "2026-07-06"},
                expected_kind="rewrite",
                run_subprocess=fake_rewrite_subprocess,
            )
            self.assertEqual(status, 200)

            manifest = read_manifest(_prepare_bundle_for_selection(tmp_path, "2026-07-06"))
            entry = manifest["artifacts"]["copies"]["xiaohongshu"]
            self.assertEqual(entry["status"], "ready")
            self.assertEqual(entry["copy_path"], "copy/xiaohongshu.md")
            self.assertEqual(entry["humanized_path"], "copy/xiaohongshu-humanized.md")
            self.assertEqual(set(read_selection(tmp_path, "2026-07-06")), {"date", "selected", "selected_at"})


class PublishMigratesOldFormatSelectionTests(unittest.TestCase):
    """旧 selection 可读，但当前稿只允许写入显式准备的 publication bundle。"""

    def test_legacy_selection_can_prepare_bundle_then_publish(self) -> None:
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
            _, expected_copy_path, _ = _bundle_copy_paths(tmp_path, date)

            def fake_run_subprocess(cmd, capture_output, text):  # noqa: ANN001
                return SimpleNamespace(returncode=0, stdout="", stderr=f"Wrote {expected_copy_path}\n")

            status, payload = _submit_async(
                tmp_path,
                "/api/publish",
                {"date": date},
                expected_kind="publish",
                run_subprocess=fake_run_subprocess,
            )

            self.assertEqual(status, 200)
            self.assertTrue(payload["ok"])
            manifest = read_manifest(_prepare_bundle_for_selection(tmp_path, date))
            self.assertEqual(manifest["artifacts"]["copies"]["xiaohongshu"]["status"], "ready")
            self.assertEqual(manifest["artifacts"]["copies"]["xiaohongshu"]["copy_path"], "copy/xiaohongshu.md")
            self.assertEqual(json.loads(selection_path.read_text(encoding="utf-8")), legacy_payload)


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
        _, copy_path, _ = _bundle_copy_paths(tmp_path, date)
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
            copy_path = self._write_copy_md(tmp_path, date, "09-slug")
            _, _, humanized_path = _bundle_copy_paths(tmp_path, date)
            humanized_path.write_text("旧 humanized 稿", encoding="utf-8")

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

            on_disk = copy_path.read_text(encoding="utf-8")
            self.assertIn("- 电影: https://example.com/movie/1", on_disk)
            self.assertIn("- 新闻: https://example.com/news/1", on_disk)

            self.assertFalse(humanized_path.exists())
            manifest = read_manifest(_prepare_bundle_for_selection(tmp_path, date))
            entry = manifest["artifacts"]["copies"]["xiaohongshu"]
            self.assertEqual(entry["status"], "ready")
            self.assertEqual(entry["humanized_path"], "copy/xiaohongshu-humanized.md")

    def test_empty_body_returns_400(self) -> None:
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            date = "2026-07-06"

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
            date = "2026-07-06"
            _make_batch(tmp_path, date, "09-slug")
            route(
                "POST",
                "/api/select",
                {},
                {"date": date, "news_slug": "09-slug", "tmdb_id": 429918, "title": "Survival Family"},
                batch_root=tmp_path,
            )
            _prepare_bundle_for_selection(tmp_path, date)
            status, payload = route(
                "POST",
                "/api/edit-body",
                {},
                {"date": date, "slug": "09-slug", "body": "新正文"},
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
        _, copy_path, _ = _bundle_copy_paths(tmp_path, date)
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

            _, _, humanized_path = _bundle_copy_paths(tmp_path, date)
            humanized_path.write_text("旧 humanized", encoding="utf-8")

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

            status, payload = _submit_async(
                tmp_path,
                "/api/regenerate",
                {"date": date, "slug": "09-slug", "platform": "xiaohongshu", "target": "body"},
                expected_kind="regenerate",
                run_subprocess=fake_run_subprocess,
            )

            self.assertEqual(status, 200)
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["target"], "body")
            self.assertEqual(payload["body"], "新的正文。")
            self.assertEqual(payload["headline"], "原版标题")

            self.assertFalse(humanized_path.exists())
            manifest = read_manifest(_prepare_bundle_for_selection(tmp_path, date))
            self.assertEqual(manifest["artifacts"]["copies"]["xiaohongshu"]["status"], "ready")

    def test_target_headline_does_not_clear_humanized_path(self) -> None:
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            date = "2026-07-06"
            self._select(tmp_path, date)
            copy_path = self._write_copy_md(tmp_path, date, "09-slug")

            _, _, humanized_path = _bundle_copy_paths(tmp_path, date)
            humanized_path.write_text("旧 humanized", encoding="utf-8")

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

            status, payload = _submit_async(
                tmp_path,
                "/api/regenerate",
                {"date": date, "slug": "09-slug", "platform": "xiaohongshu", "target": "headline"},
                expected_kind="regenerate",
                run_subprocess=fake_run_subprocess,
            )

            self.assertEqual(status, 200)
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["headline"], "新的标题")
            self.assertEqual(payload["body"], "原版正文。")

            self.assertTrue(humanized_path.exists())
            self.assertEqual(read_manifest(_prepare_bundle_for_selection(tmp_path, date))["artifacts"]["copies"]["xiaohongshu"]["humanized_path"], "copy/xiaohongshu-humanized.md")

    def test_invalid_target_returns_400(self) -> None:
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            date = "2026-07-06"
            self._select(tmp_path, date)

            status, payload = _submit_async(
                tmp_path,
                "/api/regenerate",
                {"date": date, "slug": "09-slug", "target": "nope"},
                expected_kind="regenerate",
            )
            self.assertEqual(status, 400)
            self.assertFalse(payload["ok"])

    def test_missing_selection_returns_400(self) -> None:
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            date = "2026-07-06"
            _make_batch(tmp_path, date, "09-slug")

            status, payload = _submit_async(
                tmp_path,
                "/api/regenerate",
                {"date": date, "target": "body"},
                expected_kind="regenerate",
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

            status, payload = _submit_async(
                tmp_path,
                "/api/regenerate",
                {"date": date, "slug": "09-slug", "target": "body"},
                expected_kind="regenerate",
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

            status, payload = _submit_async(
                tmp_path,
                "/api/generate-drafts",
                {"date": date},
                expected_kind="generate-drafts",
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

            status, payload = _submit_async(
                tmp_path, "/api/generate-drafts", {"date": "2026-07-06"}, expected_kind="generate-drafts"
            )
            self.assertEqual(status, 400)
            self.assertFalse(payload["ok"])

    def test_missing_date_returns_400(self) -> None:
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            status, payload = _submit_async(
                tmp_path, "/api/generate-drafts", {}, expected_kind="generate-drafts"
            )
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

            status, payload = _submit_async(
                tmp_path,
                "/api/generate-drafts",
                {"date": date},
                expected_kind="generate-drafts",
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
        _prepare_bundle_for_selection(tmp_path, date)
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

            _, copy_path, _ = _bundle_copy_paths(tmp_path, date)
            self.assertTrue(copy_path.is_file())
            on_disk = copy_path.read_text(encoding="utf-8")
            # 派生当前稿逐字对齐 publish 产出：headline + body + 链接分区（movie_url 来自 retrieve.json）。
            self.assertIn("抗争之路", on_disk)
            self.assertIn("## 链接", on_disk)
            self.assertIn("https://themoviecosmos.com/movie/429918", on_disk)

            manifest = read_manifest(_prepare_bundle_for_selection(tmp_path, date))
            entry = manifest["artifacts"]["copies"]["xiaohongshu"]
            self.assertEqual(entry["selected_draft_id"], "The-Hero")
            self.assertEqual(entry["status"], "ready")
            self.assertEqual(entry["copy_path"], "copy/xiaohongshu.md")
            self.assertEqual(entry["humanized_path"], "copy/xiaohongshu-humanized.md")

    def test_reselect_invalidates_humanized(self) -> None:
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            date = "2026-07-06"
            self._setup_pool(tmp_path, date)
            route("POST", "/api/select-draft", {}, {"date": date, "draft_id": "The-Sage"}, batch_root=tmp_path)

            _, _, humanized_path = _bundle_copy_paths(tmp_path, date)
            humanized_path.write_text("旧去AI化稿", encoding="utf-8")

            # 改选另一张卡：body 变 ⇒ humanized 必须失效。
            status, payload = route(
                "POST", "/api/select-draft", {}, {"date": date, "draft_id": "The-Hero"}, batch_root=tmp_path
            )
            self.assertEqual(status, 200)
            self.assertFalse(humanized_path.exists())
            entry = read_manifest(_prepare_bundle_for_selection(tmp_path, date))["artifacts"]["copies"]["xiaohongshu"]
            self.assertEqual(entry["selected_draft_id"], "The-Hero")

    def test_select_draft_requires_explicit_bundle_prepare(self) -> None:
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
            unprepared_manifest = manifest_path(tmp_path, date, 429918, "Survival Family")
            shutil.rmtree(unprepared_manifest.parent, ignore_errors=True)
            pool_path = tmp_path / date / "09-slug_drafts_xiaohongshu.json"
            pool_path.write_text(
                json.dumps([{"draft_id": "The-Sage", "headline": "理性之眼", "body": "正文"}], ensure_ascii=False),
                encoding="utf-8",
            )

            status, payload = route(
                "POST", "/api/select-draft", {}, {"date": date, "draft_id": "The-Sage"}, batch_root=tmp_path
            )

            self.assertEqual(status, 400)
            self.assertIn("publication bundle is not prepared", payload["error"])

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

            status, payload = _submit_async(
                tmp_path,
                "/api/combine-drafts",
                {"date": date, "draft_ids": ["The-Sage", "The-Hero"]},
                expected_kind="combine-drafts",
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

            status, payload = _submit_async(
                tmp_path,
                "/api/combine-drafts",
                {"date": date, "draft_ids": ["The-Sage", "The-Hero", "The-Lover"]},
                expected_kind="combine-drafts",
                run_subprocess=fake_run_subprocess,
            )
            self.assertEqual(status, 400)
            self.assertFalse(payload["ok"])
            # >2 应在 handle_combine_drafts 里直接拦下，绝不启动 subprocess
            # （拦截逻辑本身零改动，只是现在跑在 job 里而非同步 route() 内）。
            self.assertEqual(called["n"], 0)

    def test_non_list_draft_ids_returns_400(self) -> None:
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            date = "2026-07-06"
            self._setup(tmp_path, date)
            status, payload = _submit_async(
                tmp_path,
                "/api/combine-drafts",
                {"date": date, "draft_ids": "The-Sage"},
                expected_kind="combine-drafts",
            )
            self.assertEqual(status, 400)
            self.assertFalse(payload["ok"])


class RetryDraftRouteTests(unittest.TestCase):
    """12.5：POST /api/retry-draft 通过注入 run_subprocess stub 验证 --retry 单份重掷。"""

    def _write_pool(self, tmp_path: Path, date: str, slug: str, pool: list, platform: str = "xiaohongshu") -> Path:
        path = tmp_path / date / f"{slug}_drafts_{platform}.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(pool, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return path

    def _select(self, tmp_path: Path, date: str) -> None:
        _make_batch(tmp_path, date, "09-slug")
        route(
            "POST",
            "/api/select",
            {},
            {"date": date, "news_slug": "09-slug", "tmdb_id": 429918, "title": "Survival Family"},
            batch_root=tmp_path,
        )

    def test_success_passes_retry_and_judge_flags_and_returns_pool(self) -> None:
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            date = "2026-07-06"
            self._select(tmp_path, date)
            pool = [
                {"draft_id": "混合视角", "headline": "中性", "body": "中性正文。"},
                {"draft_id": "The-Sage", "headline": "理性之眼", "body": "求真正文。"},
            ]
            pool_path = self._write_pool(tmp_path, date, "09-slug", pool)

            def fake_run_subprocess(cmd, capture_output, text):  # noqa: ANN001
                self.assertIn("--retry", cmd)
                self.assertIn("The-Sage", cmd)
                # 面板重试恒带 judge 闸门。
                self.assertIn("--judge", cmd)
                # 单份重试绝不夹带 --combine。
                self.assertNotIn("--combine", cmd)
                return SimpleNamespace(returncode=0, stdout="", stderr=f"Wrote {pool_path}\n")

            status, payload = _submit_async(
                tmp_path,
                "/api/retry-draft",
                {"date": date, "draft_id": "The-Sage"},
                expected_kind="retry-draft",
                run_subprocess=fake_run_subprocess,
            )

            self.assertEqual(status, 200)
            self.assertTrue(payload["ok"])
            self.assertEqual(len(payload["drafts"]), 2)

    def test_missing_draft_id_returns_400(self) -> None:
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            date = "2026-07-06"
            self._select(tmp_path, date)
            status, payload = _submit_async(
                tmp_path, "/api/retry-draft", {"date": date}, expected_kind="retry-draft"
            )
            self.assertEqual(status, 400)
            self.assertFalse(payload["ok"])

    def test_missing_date_returns_400(self) -> None:
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            status, payload = _submit_async(
                tmp_path, "/api/retry-draft", {"draft_id": "The-Sage"}, expected_kind="retry-draft"
            )
            self.assertEqual(status, 400)
            self.assertFalse(payload["ok"])

    def test_subprocess_failure_returns_500(self) -> None:
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            date = "2026-07-06"
            self._select(tmp_path, date)

            def fake_run_subprocess(cmd, capture_output, text):  # noqa: ANN001
                return SimpleNamespace(returncode=2, stdout="", stderr="error: 合并稿单份 retry 暂不支持")

            status, payload = _submit_async(
                tmp_path,
                "/api/retry-draft",
                {"date": date, "draft_id": "The-Sage+The-Hero"},
                expected_kind="retry-draft",
                run_subprocess=fake_run_subprocess,
            )
            self.assertEqual(status, 500)
            self.assertFalse(payload["ok"])
            self.assertIn("合并稿", payload["stderr"])


class JobRouteTests(unittest.TestCase):
    """直接测 GET /api/job 经 route() 的四态（Phase 12.6.4 验收点）。"""

    def test_unknown_job_id_returns_404(self) -> None:
        """未知 job_id（store 里查不到）→ 404 + ok:False + error 字段。"""
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            status, payload = route(
                "GET",
                "/api/job",
                {"job_id": "does-not-exist"},
                None,
                batch_root=tmp_path,
                job_store=JobStore(),
            )
            self.assertEqual(status, 404)
            self.assertFalse(payload["ok"])
            self.assertIn("error", payload)

    def test_missing_job_id_param_returns_404(self) -> None:
        """query 里完全没有 job_id（rec 落在 None 分支）→ 同样 404。"""
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            status, payload = route(
                "GET",
                "/api/job",
                {},
                None,
                batch_root=tmp_path,
                job_store=JobStore(),
            )
            self.assertEqual(status, 404)
            self.assertFalse(payload["ok"])
            self.assertIn("error", payload)

    def test_running_job_returns_200_running_without_result(self) -> None:
        """job 还没跑完（executor 只捕获不执行）→ 200 + status:running，无 result 字段。"""
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            store = JobStore()
            job_id = store.submit(
                lambda: (200, {"ok": True}), kind="test", executor=lambda fn: None
            )
            status, payload = route(
                "GET",
                "/api/job",
                {"job_id": job_id},
                None,
                batch_root=tmp_path,
                job_store=store,
            )
            self.assertEqual(status, 200)
            self.assertEqual(payload, {"ok": True, "status": "running"})

    def test_done_job_returns_200_done_with_result(self) -> None:
        """job 用 inline executor 立即跑完 → 200 + status:done + result:{http_status,payload}。"""
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            store = JobStore()
            job_id = store.submit(
                lambda: (202, {"ok": True, "kind": "x"}),
                kind="test",
                executor=_inline_executor,
            )
            status, payload = route(
                "GET",
                "/api/job",
                {"job_id": job_id},
                None,
                batch_root=tmp_path,
                job_store=store,
            )
            self.assertEqual(status, 200)
            self.assertEqual(payload["status"], "done")
            self.assertEqual(
                payload["result"], {"http_status": 202, "payload": {"ok": True, "kind": "x"}}
            )

    def test_error_job_returns_200_error_with_stderr_traceback(self) -> None:
        """work 抛异常，inline executor 立即落 error → 200 + status:error + stderr 含 traceback。"""
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            store = JobStore()

            def _work() -> tuple[int, dict]:
                raise ValueError("boom")

            job_id = store.submit(_work, kind="test", executor=_inline_executor)
            status, payload = route(
                "GET",
                "/api/job",
                {"job_id": job_id},
                None,
                batch_root=tmp_path,
                job_store=store,
            )
            self.assertEqual(status, 200)
            self.assertEqual(payload["status"], "error")
            self.assertIn("ValueError: boom", payload["stderr"])
            self.assertIn("Traceback", payload["stderr"])


class UnknownRouteTests(unittest.TestCase):
    def test_unknown_path_returns_404(self) -> None:
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            status, payload = route("GET", "/api/nope", {}, None, batch_root=tmp_path)
            self.assertEqual(status, 404)
            self.assertIn("error", payload)


if __name__ == "__main__":
    unittest.main()