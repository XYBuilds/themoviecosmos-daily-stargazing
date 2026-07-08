from __future__ import annotations

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from scripts.compose import (
    JudgeEntry,
    format_judge_kernel,
    format_selected_movie_block,
    load_c2_template,
    parse_publish_output,
    render_c2_prompt,
    run_publish,
)


_CANDIDATE = {
    "tmdb_id": 157336,
    "title": "Interstellar",
    "overview": "A team travels through a wormhole.",
    "genres": "Adventure, Drama, Science Fiction",
    "release_year": 2014,
    "movie_url": "https://themoviecosmos.com/movie/157336",
}

_DETAIL = {
    "id": 157336,
    "title": "Interstellar",
    "overview": "A team travels through a wormhole.",
    "genres": "Adventure, Drama, Science Fiction",
    "release_date": "2014-11-05",
    "runtime": 169,
    "director": "Christopher Nolan",
    "vote_average": 8.5,
    "vote_count": 37000,
    "popularity": 154.2,
    "imdb_rating": 8.7,
    "imdb_votes": 2300000,
}


class ComposePublishTests(unittest.TestCase):
    def test_selected_movie_block_exposes_real_numbers(self) -> None:
        with patch("scripts.compose.get_movie_detail_by_tmdb_id", return_value=_DETAIL):
            block = format_selected_movie_block(_CANDIDATE)

        self.assertIn("vote_average: 8.5", block)
        self.assertIn("vote_count: 37000", block)
        self.assertIn("popularity: 154.2", block)
        self.assertIn("director: Christopher Nolan", block)
        self.assertIn("https://themoviecosmos.com/movie/157336", block)

    def test_judge_kernel_uses_upstream_judge_fields(self) -> None:
        kernel = format_judge_kernel(JudgeEntry(2, "same engine", "X drives Y", "strong"))
        self.assertIn("resonance_type: strong", kernel)
        self.assertIn("causal_test: X drives Y", kernel)
        self.assertIn("rationale: same engine", kernel)

    def test_publish_prompt_is_single_draft_not_platform_variants(self) -> None:
        prompt = render_c2_prompt(
            "{{news_context}}\n{{selected_movie}}\n{{judge_kernel}}",
            "News",
            "Movie",
            "Judge",
        )
        self.assertEqual(prompt, "News\nMovie\nJudge")

    def test_run_publish_feeds_db_and_judge_and_returns_headline_body(self) -> None:
        # ADR-0015 D4：sentinel 契约输出 → run_publish 返回 {tmdb_id, headline, body}。
        captured: dict[str, str] = {}

        def fake_llm(prompt: str) -> str:
            captured["prompt"] = prompt
            return (
                "【标题】当风向不站在她们这边\n"
                "【正文】\n"
                "「Interstellar」(2014) Christopher Nolan\n"
                "这是一段正文。"
            )

        with patch("scripts.compose.get_movie_detail_by_tmdb_id", return_value=_DETAIL):
            draft = run_publish(
                _CANDIDATE,
                {"title": "News", "description": "Summary"},
                judge=JudgeEntry(2, "same engine", "X drives Y", "strong"),
                llm_call=fake_llm,
            )

        self.assertIn("vote_average: 8.5", captured["prompt"])
        self.assertIn("causal_test: X drives Y", captured["prompt"])
        # 产物三字段；sentinel 已剥离。
        self.assertEqual(draft["tmdb_id"], 157336)
        self.assertEqual(draft["headline"], "当风向不站在她们这边")
        self.assertNotIn("【标题】", draft["headline"])
        self.assertNotIn("【正文】", draft["body"])
        # 归属行用「」——不得被 clean_publish_body 剥除（只剥《》(年)）。
        self.assertIn("「Interstellar」(2014) Christopher Nolan", draft["body"])
        self.assertIn("这是一段正文。", draft["body"])
        self.assertNotIn("https://themoviecosmos.com/movie/", draft["body"])
        self.assertNotIn("#", draft["body"])

    def test_run_publish_strips_llm_emitted_book_title_and_link(self) -> None:
        # 归属行「」保留，但 LLM 误吐的《片名》(年份) 行与裸链接仍被剥除。
        def fake_llm(prompt: str) -> str:
            return (
                "【标题】一句标题\n"
                "【正文】\n"
                "「Interstellar」(2014) Christopher Nolan\n"
                "《Interstellar》(2014)\n"
                "这是正文。\n\n"
                "https://themoviecosmos.com/movie/157336"
            )

        with patch("scripts.compose.get_movie_detail_by_tmdb_id", return_value=_DETAIL):
            draft = run_publish(
                _CANDIDATE,
                {"title": "News", "description": "Summary"},
                judge=JudgeEntry(2, "same engine", "X drives Y", "strong"),
                llm_call=fake_llm,
            )

        self.assertEqual(draft["headline"], "一句标题")
        self.assertIn("「Interstellar」(2014) Christopher Nolan", draft["body"])
        self.assertIn("这是正文。", draft["body"])
        self.assertNotIn("《Interstellar》(2014)", draft["body"])
        self.assertNotIn("https://themoviecosmos.com/movie/157336", draft["body"])

    def test_run_publish_body_empty_when_no_content(self) -> None:
        # 兜底：LLM 只吐标题无正文 → body 为空（上层据此判失败，不静默出半稿）。
        def fake_llm(prompt: str) -> str:
            return "【标题】只有标题\n【正文】\n"

        with patch("scripts.compose.get_movie_detail_by_tmdb_id", return_value=_DETAIL):
            draft = run_publish(
                _CANDIDATE,
                {"title": "News", "description": "Summary"},
                llm_call=fake_llm,
            )

        self.assertEqual(draft["headline"], "只有标题")
        self.assertEqual(draft["body"], "")


class PublishSystemMessageTests(unittest.TestCase):
    def test_real_path_uses_publish_system_message_not_decision_card(self) -> None:
        # run_publish 走真实 client 路径时须发 publish 专用 system message，
        # 不再复用决策卡 message（其明写「不要输出标题」，与 headline 冲突）。
        from scripts import compose

        captured: dict[str, str] = {}

        class _FakeMsg:
            content = "【标题】t\n【正文】\n「x」(2025) d\n正文"

        class _FakeChoice:
            message = _FakeMsg()

        class _FakeResp:
            choices = [_FakeChoice()]

        class _FakeCompletions:
            def create(self, *, model, messages):  # noqa: ANN001
                captured["system"] = messages[0]["content"]
                return _FakeResp()

        class _FakeChat:
            completions = _FakeCompletions()

        class _FakeClient:
            chat = _FakeChat()

        with TemporaryDirectory() as tmp:
            base = Path(tmp)
            (base / "compose_publish_xiaohongshu.md").write_text(
                "{{news_context}}{{selected_movie}}{{judge_kernel}}", encoding="utf-8"
            )
            with (
                patch("scripts.compose.load_env", lambda: None),
                patch("scripts.compose.get_llm_client", lambda _p: _FakeClient()),
                patch("scripts.compose._model_name", lambda _p: "m"),
                patch("scripts.compose.get_movie_detail_by_tmdb_id", return_value=_DETAIL),
            ):
                draft = compose.run_publish(
                    _CANDIDATE,
                    {"title": "News", "description": "Summary"},
                    provider="mimo",
                    prompts_dir=base,
                )

        self.assertEqual(captured["system"], compose._PUBLISH_SYSTEM_MESSAGE)
        self.assertNotEqual(captured["system"], compose._SYSTEM_MESSAGE)
        self.assertEqual(draft["headline"], "t")


class ParsePublishOutputTests(unittest.TestCase):
    def test_full_sentinel_contract(self) -> None:
        headline, body = parse_publish_output(
            "【标题】标题句\n【正文】\n「片名」(2025) 导演\n正文段。"
        )
        self.assertEqual(headline, "标题句")
        self.assertEqual(body, "「片名」(2025) 导演\n正文段。")

    def test_headline_only_multiline_takes_first_line(self) -> None:
        headline, body = parse_publish_output("【标题】第一行\n第二行\n正文")
        self.assertEqual(headline, "第一行")
        self.assertEqual(body, "第二行\n正文")

    def test_no_sentinel_falls_back_to_body(self) -> None:
        headline, body = parse_publish_output("整段没有 sentinel 的正文")
        self.assertEqual(headline, "")
        self.assertEqual(body, "整段没有 sentinel 的正文")


class LoadC2TemplateTests(unittest.TestCase):
    def test_platform_selects_prompt_file(self) -> None:
        with TemporaryDirectory() as tmp:
            base = Path(tmp)
            (base / "compose_publish_xiaohongshu.md").write_text(
                "XHS: {{news_context}}", encoding="utf-8"
            )
            template = load_c2_template("xiaohongshu", prompts_dir=base)
            self.assertIn("XHS:", template)

    def test_unknown_platform_raises(self) -> None:
        with TemporaryDirectory() as tmp:
            with self.assertRaises(FileNotFoundError):
                load_c2_template("nosuch", prompts_dir=Path(tmp))


if __name__ == "__main__":
    unittest.main()