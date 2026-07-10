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
    load_headline_contract,
    load_headline_template,
    load_persona_perspective,
    parse_publish_output,
    render_c2_prompt,
    render_headline_prompt,
    render_movie_header,
    run_headline,
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

    def test_render_movie_header_drops_cn_segment_for_non_english(self) -> None:
        header = render_movie_header(
            {
                "zh_title": "",
                "original_title": "Sueño en otro idioma",
                "title": "I Dream in Another Language",
                "original_language": "es",
                "director": "Ernesto Contreras",
                "release_date": "2017-07-28",
                "genres": ["Fantasy", "Drama"],
                "vote_average": 7.9,
                "runtime": 142,
            }
        )

        self.assertEqual(
            header,
            "Sueño en otro idioma / I Dream in Another Language\n"
            "Ernesto Contreras\n"
            "\n"
            "坐标：[Y: 2017, M: 07, D: 28]\n"
            "文明：ES 西班牙语\n"
            "类型：奇幻，剧情\n"
            "光度：7.9\n"
            "体积：142",
        )

    def test_render_movie_header_dedupes_english_titles(self) -> None:
        header = render_movie_header(
            {
                "zh_title": "",
                "original_title": "Interstellar",
                "title": "Interstellar",
                "original_language": "en",
                "release_date": "2014-11-05",
                "genres": "Adventure, Drama, Science Fiction",
                "vote_average": 8.5,
                "runtime": 169,
            }
        )

        self.assertEqual(
            header,
            "Interstellar\n"
            "\n"
            "坐标：[Y: 2014, M: 11, D: 05]\n"
            "文明：EN 英语\n"
            "类型：冒险，剧情，科幻\n"
            "光度：8.5\n"
            "体积：169",
        )

    def test_render_movie_header_keeps_three_title_segments_with_cn(self) -> None:
        header = render_movie_header(
            {
                "zh_title": "梦呓雨林",
                "original_title": "Sueño en otro idioma",
                "title": "I Dream in Another Language",
                "original_language": "es",
                "director": "Ernesto Contreras",
            }
        )

        self.assertEqual(
            header,
            "「梦呓雨林」 / Sueño en otro idioma / I Dream in Another Language\n"
            "Ernesto Contreras\n"
            "\n"
            "坐标：未知\n"
            "文明：ES 西班牙语",
        )

    def test_render_movie_header_omits_missing_director_and_falls_back_for_labels(self) -> None:
        header = render_movie_header(
            {
                "zh_title": "",
                "original_title": "Unknown Film",
                "title": "Unknown Film",
                "original_language": "xx",
                "release_date": "",
                "genres": ["Made Up Genre"],
                "vote_average": "",
                "runtime": None,
            }
        )

        self.assertEqual(
            header,
            "Unknown Film\n"
            "\n"
            "坐标：未知\n"
            "文明：XX\n"
            "类型：Made Up Genre",
        )

    def test_render_movie_header_handles_invalid_release_date(self) -> None:
        header = render_movie_header(
            {
                "zh_title": "",
                "original_title": "Unknown Film",
                "title": "Unknown Film",
                "original_language": "es",
                "release_date": "not-a-date",
            }
        )

        self.assertIn("坐标：未知", header)
        self.assertNotIn("[Y:", header)

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


class HeadlineContractInjectionTests(unittest.TestCase):
    """ADR-0016 D1：headline 硬规则单一事实源 + monolithic 注入无回归的 golden-snapshot。"""

    # 每条硬规则的关键短语，抽取前后都必须在渲染结果里出现（一条不丢）。
    _KEY_PHRASES = (
        "≤ 10 个中文字",
        "不用推荐 / 煽动词",
        "不容错过",
        "不剧透结局",
        "不裸露字面片名",
        "一句话，别写成两三句或带换行",
    )

    def test_load_headline_contract_reads_shared_file(self) -> None:
        contract = load_headline_contract()
        self.assertIn("≤ 10", contract)
        self.assertIn("不裸露", contract)
        self.assertIn("不剧透", contract)

    def test_monolithic_render_loses_no_headline_rule_text(self) -> None:
        # 用真实仓库 prompt 文件（默认 prompts_dir）渲染，证明抽取后规则文本未丢失。
        template = load_c2_template("xiaohongshu")
        contract = load_headline_contract()
        rendered = render_c2_prompt(
            template,
            "News",
            "Movie",
            "Judge",
            headline_contract=contract,
        )
        self.assertNotIn("{{headline_contract}}", rendered)
        for phrase in self._KEY_PHRASES:
            self.assertIn(phrase, rendered)

    def test_render_c2_prompt_backward_compatible_without_placeholder(self) -> None:
        # 模板缺 {{headline_contract}} 占位符时，新增参数不改变渲染结果（back-compat）。
        template = "{{news_context}}\n{{selected_movie}}\n{{judge_kernel}}"
        rendered_without = render_c2_prompt(template, "News", "Movie", "Judge")
        rendered_with = render_c2_prompt(
            template, "News", "Movie", "Judge", headline_contract="some rules"
        )
        self.assertEqual(rendered_without, rendered_with)
        self.assertEqual(rendered_without, "News\nMovie\nJudge")


class RunHeadlineTests(unittest.TestCase):
    """ADR-0016 D3：headline-only、body-aware 重生成。"""

    def test_run_headline_returns_headline_only_no_body_key(self) -> None:
        def fake_llm(prompt: str) -> str:
            return "【标题】穿越星海的思念"

        with patch("scripts.compose.get_movie_detail_by_tmdb_id", return_value=_DETAIL):
            result = run_headline(
                _CANDIDATE,
                {"title": "News", "description": "Summary"},
                "这是当前正文。",
                llm_call=fake_llm,
            )

        self.assertEqual(result, {"tmdb_id": 157336, "headline": "穿越星海的思念"})
        self.assertNotIn("body", result)

    def test_run_headline_prompt_is_body_aware_and_fully_rendered(self) -> None:
        captured: dict[str, str] = {}

        def fake_llm(prompt: str) -> str:
            captured["prompt"] = prompt
            return "【标题】标题"

        with patch("scripts.compose.get_movie_detail_by_tmdb_id", return_value=_DETAIL):
            run_headline(
                _CANDIDATE,
                {"title": "News", "description": "Summary"},
                "独一无二的当前正文标记ABC123",
                llm_call=fake_llm,
            )

        prompt = captured["prompt"]
        self.assertIn("独一无二的当前正文标记ABC123", prompt)
        self.assertNotIn("{{current_body}}", prompt)
        self.assertNotIn("{{headline_contract}}", prompt)
        self.assertNotIn("{{news_context}}", prompt)
        self.assertNotIn("{{selected_movie}}", prompt)

    def test_run_headline_multiline_takes_first_line_only(self) -> None:
        def fake_llm(prompt: str) -> str:
            return "【标题】只保留第一行\n多余的第二行"

        with patch("scripts.compose.get_movie_detail_by_tmdb_id", return_value=_DETAIL):
            result = run_headline(
                _CANDIDATE,
                {"title": "News", "description": "Summary"},
                "当前正文",
                llm_call=fake_llm,
            )

        self.assertEqual(result["headline"], "只保留第一行")

    def test_run_headline_does_not_leak_body_sentinel_if_llm_misbehaves(self) -> None:
        # headline-only 鲁棒性：即使被注入的 stub LLM 违反契约误吐了 【正文】 段，
        # run_headline 也只取 headline，不应把正文内容泄漏进返回值。
        def fake_llm(prompt: str) -> str:
            return "【标题】误吐正文的标题\n【正文】\n不该出现在结果里的正文内容"

        with patch("scripts.compose.get_movie_detail_by_tmdb_id", return_value=_DETAIL):
            result = run_headline(
                _CANDIDATE,
                {"title": "News", "description": "Summary"},
                "当前正文",
                llm_call=fake_llm,
            )

        self.assertEqual(result, {"tmdb_id": 157336, "headline": "误吐正文的标题"})
        self.assertNotIn("body", result)
        self.assertNotIn("【正文】", result["headline"])
        self.assertNotIn("不该出现在结果里的正文内容", result["headline"])

    def test_render_headline_prompt_embeds_shared_contract(self) -> None:
        template = load_headline_template()
        contract = load_headline_contract()
        rendered = render_headline_prompt(
            template, "News", "Movie", "Body", headline_contract=contract
        )
        self.assertIn("≤ 10", rendered)
        self.assertNotIn("{{headline_contract}}", rendered)


class PersonaPerspectiveInjectionTests(unittest.TestCase):
    """ADR-0017 D1/D2：persona 视角加载归一化 + C2 注入 + 空注入 golden-snapshot 等价。"""

    def test_load_persona_perspective_reads_distilled_file(self) -> None:
        # 真实仓库文件：读到中文视角、且不含任何检索侧行话。
        text = load_persona_perspective("The-Sage")
        self.assertIn("主视角", text)
        self.assertIn("求真", text)
        for jargon in ("decon", "P-Select", "objective-floor", "focalized", "alt-creator"):
            self.assertNotIn(jargon, text)

    def test_load_persona_perspective_normalizes_uppercase_hyphen(self) -> None:
        # triggered_by 的 THE-SAGE 大写连字符须归一到 The-Sage 目录，与首字母大写等价。
        upper = load_persona_perspective("THE-SAGE")
        title = load_persona_perspective("The-Sage")
        self.assertEqual(upper, title)

    def test_load_persona_perspective_missing_file_raises(self) -> None:
        with self.assertRaises(FileNotFoundError):
            load_persona_perspective("THE-NOSUCH")

    def test_load_persona_perspective_never_falls_back_to_card(self) -> None:
        # 缺 c2_perspective.md 时清晰报错，禁静默回退读 persona_card.md（行话泄漏防线）。
        with TemporaryDirectory() as tmp:
            base = Path(tmp)
            card_dir = base / "personas" / "The-Faux"
            card_dir.mkdir(parents=True)
            (card_dir / "persona_card.md").write_text("decon P-Select", encoding="utf-8")
            with self.assertRaises(FileNotFoundError):
                load_persona_perspective("The-Faux", prompts_dir=base)

    def test_render_c2_prompt_injects_persona_perspective(self) -> None:
        rendered = render_c2_prompt(
            "{{news_context}}\n{{persona_perspective}}\n{{judge_kernel}}",
            "News",
            "Movie",
            "Judge",
            persona_perspective="用求真的眼光看",
        )
        self.assertIn("用求真的眼光看", rendered)
        self.assertNotIn("{{persona_perspective}}", rendered)

    def test_empty_persona_perspective_is_byte_identical_noop(self) -> None:
        # 空注入 golden-snapshot：真实模板下 persona_perspective="" 与不传参逐字节等价，
        # 证首发 publish / 9.8 重生成路径零回归。
        template = load_c2_template("xiaohongshu")
        contract = load_headline_contract()
        without = render_c2_prompt(
            template, "News", "Movie", "Judge", headline_contract=contract
        )
        with_empty = render_c2_prompt(
            template,
            "News",
            "Movie",
            "Judge",
            headline_contract=contract,
            persona_perspective="",
        )
        self.assertEqual(without, with_empty)
        self.assertNotIn("{{persona_perspective}}", with_empty)

    def test_run_publish_passes_persona_perspective_into_prompt(self) -> None:
        captured: dict[str, str] = {}

        def fake_llm(prompt: str) -> str:
            captured["prompt"] = prompt
            return "【标题】t\n【正文】\n「Interstellar」(2014) Christopher Nolan\n正文。"

        with patch("scripts.compose.get_movie_detail_by_tmdb_id", return_value=_DETAIL):
            run_publish(
                _CANDIDATE,
                {"title": "News", "description": "Summary"},
                persona_perspective="以荒诞、玩味的眼光看",
                llm_call=fake_llm,
            )

        self.assertIn("以荒诞、玩味的眼光看", captured["prompt"])

    def test_run_publish_empty_perspective_matches_default(self) -> None:
        # run_publish 默认 persona_perspective="" 时，渲染 prompt 与显式空串一致。
        prompts: dict[str, str] = {}

        def make_llm(key: str):
            def _llm(prompt: str) -> str:
                prompts[key] = prompt
                return "【标题】t\n【正文】\n「x」(2025) d\n正文。"

            return _llm

        with patch("scripts.compose.get_movie_detail_by_tmdb_id", return_value=_DETAIL):
            run_publish(
                _CANDIDATE,
                {"title": "News", "description": "Summary"},
                llm_call=make_llm("default"),
            )
            run_publish(
                _CANDIDATE,
                {"title": "News", "description": "Summary"},
                persona_perspective="",
                llm_call=make_llm("explicit_empty"),
            )

        self.assertEqual(prompts["default"], prompts["explicit_empty"])
        self.assertNotIn("{{persona_perspective}}", prompts["default"])


if __name__ == "__main__":
    unittest.main()