"""Offline tests for compose --stage review (C1) helper functions.

Covers persona-semantic selection (never A1/oracle), news-context build,
multi-paragraph parsing (title/year + positional fallback + missing-paragraph
errors), judge-score backfill, run_review empty/error handling, and the judge
floor filter. The LLM call is injected, so no network or API key is needed.

Note (Phase 9.6): the old copywriter「审核稿」contract tests (ReviewCopy.copy_text /
.director / row["card"] / `# 审核稿候选` / `### 《片名》(年) | headline` blocks) were
removed here — that contract was replaced by the decision-card format (ADR-0012),
and those assertions had been red on `main` since that refactor. The DB-projection /
decision-card render + payload shape are covered by ``test_compose_decision_card.py``.
The live helpers exercised below are covered ONLY here, so the file is retained
(trimmed) rather than deleted.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from scripts.compose import (
    JudgeEntry,
    build_news_context,
    filter_candidates_by_judge,
    load_judge_scores,
    map_paragraphs_to_candidates,
    representative_persona_semantic,
    result_to_payload,
    run_review,
    split_into_paragraphs,
)


def _card(title, year, headline="短语", copy="文案句。", intro="介绍。", tags="#标签", rzh="理由中译。"):
    """Build a structured C1 card block string matching the DSL contract."""
    return (
        f"《{title}》({year})\n"
        f"标题: {headline}\n"
        f"文案: {copy}\n"
        f"电影介绍: {intro}\n"
        f"Hashtag: {tags}\n"
        f"评分理由中译: {rzh}"
    )


def _candidate(tmdb_id, title, year, triggered, dims, overview="An overview.", genres="Drama"):
    return {
        "tmdb_id": tmdb_id,
        "title": title,
        "overview": overview,
        "genres": genres,
        "release_year": year,
        "movie_url": f"https://themoviecosmos.com/movie/{tmdb_id}",
        "triggered_by": triggered,
        "match_diagnostics": {
            "center_dimensions": dims,
            "search_unit_kinds": ["persona-semantic"],
        },
    }


def _retrieve(candidates, per_agent=None, news=None):
    payload = {"candidates": candidates}
    if per_agent is not None:
        payload["per_agent"] = per_agent
    if news is not None:
        payload["news"] = news
    return payload


class TestPersonaSemantic(unittest.TestCase):
    def test_picks_highest_similarity_persona_semantic(self) -> None:
        per_agent = [
            {
                "agent_id": "THE-INNOCENT",
                "pseudos": [
                    {
                        "pseudo": "surface bundle text",
                        "source": {"search_unit_kind": "surface-fragment-bundle"},
                        "hits": [{"similarity": 0.9}],
                    },
                    {
                        "pseudo": "low semantic",
                        "source": {"search_unit_kind": "persona-semantic"},
                        "hits": [{"similarity": 0.4}],
                    },
                ],
            },
            {
                "agent_id": "THE-SAGE",
                "pseudos": [
                    {
                        "pseudo": "high semantic",
                        "source": {"search_unit_kind": "persona-semantic"},
                        "hits": [{"similarity": 0.8}],
                    }
                ],
            },
        ]
        text = representative_persona_semantic(_retrieve([], per_agent))
        self.assertEqual(text, "high semantic")

    def test_ignores_non_persona_semantic(self) -> None:
        per_agent = [
            {
                "agent_id": "A1",
                "pseudos": [
                    {
                        "pseudo": "surface only",
                        "source": {"search_unit_kind": "surface-fragment-bundle"},
                        "hits": [{"similarity": 0.99}],
                    }
                ],
            }
        ]
        self.assertEqual(representative_persona_semantic(_retrieve([], per_agent)), "")


class TestNewsContext(unittest.TestCase):
    def test_includes_title_description_and_semantic(self) -> None:
        ctx = build_news_context(
            {"title": "T", "description": "D"}, "rep semantic fragment"
        )
        self.assertIn("标题: T", ctx)
        self.assertIn("摘要: D", ctx)
        self.assertIn("persona-semantic", ctx)


class TestParsing(unittest.TestCase):
    def test_split_paragraphs_by_title_leader(self) -> None:
        raw = "《甲》(2001)\n第一段。\n\n《乙》(1999)\n第二段。"
        blocks = split_into_paragraphs(raw)
        self.assertEqual(len(blocks), 2)
        self.assertEqual(blocks[0][0], "甲")
        self.assertEqual(blocks[0][1], 2001)
        self.assertIn("第一段", blocks[0][2])

    def test_title_match_mapping(self) -> None:
        cands = [
            _candidate(1, "Alpha", 2001, ["THE-HERO"], ["who"]),
            _candidate(2, "Beta", 1999, ["THE-SAGE"], ["why"]),
        ]
        blocks = [("Beta", 1999, "《Beta》(1999)\nB"), ("Alpha", 2001, "《Alpha》(2001)\nA")]
        pairs, errors = map_paragraphs_to_candidates(blocks, cands)
        self.assertEqual(errors, [])
        self.assertEqual(pairs[0][0]["tmdb_id"], 1)
        self.assertIn("A", pairs[0][1])
        self.assertIn("B", pairs[1][1])

    def test_positional_fallback_when_titles_differ(self) -> None:
        cands = [
            _candidate(1, "Alpha", 2001, [], []),
            _candidate(2, "Beta", 1999, [], []),
        ]
        # LLM translated titles, no title match possible, equal counts.
        blocks = [("甲", 2001, "《甲》(2001)\nA-zh"), ("乙", 1999, "《乙》(1999)\nB-zh")]
        pairs, errors = map_paragraphs_to_candidates(blocks, cands)
        self.assertEqual(errors, [])
        self.assertIn("A-zh", pairs[0][1])
        self.assertIn("B-zh", pairs[1][1])

    def test_missing_paragraph_recorded_as_error(self) -> None:
        cands = [
            _candidate(1, "Alpha", 2001, [], []),
            _candidate(2, "Beta", 1999, [], []),
            _candidate(3, "Gamma", 2010, [], []),
        ]
        # Only two blocks for three candidates, counts differ → no positional fallback.
        blocks = [
            ("Alpha", 2001, "《Alpha》(2001)\nA"),
            ("Beta", 1999, "《Beta》(1999)\nB"),
        ]
        pairs, errors = map_paragraphs_to_candidates(blocks, cands)
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0]["tmdb_id"], 3)


class TestJudgeBackfill(unittest.TestCase):
    def test_load_judge_scores_indexes_by_run_and_tmdb(self) -> None:
        import json
        import tempfile

        data = {
            "scores": [
                {
                    "run_id": "01-grid-outage",
                    "tmdb_id": "429918",
                    "judge_score": 2,
                    "rationale": "Both center on outages.",
                    "causal_test": "Power loss drives crisis.",
                    "judge_resonance_type": "强共振",
                },
                {"run_id": "01-grid-outage", "tmdb_id": "33495", "judge_score": 1},
            ]
        }
        with tempfile.NamedTemporaryFile(
            "w", suffix=".json", delete=False, encoding="utf-8"
        ) as fh:
            json.dump(data, fh)
            path = Path(fh.name)
        index = load_judge_scores(path)
        entry = index[("01-grid-outage", "429918")]
        self.assertEqual(entry.score, 2)
        self.assertEqual(entry.rationale, "Both center on outages.")
        self.assertEqual(entry.causal_test, "Power loss drives crisis.")
        self.assertEqual(entry.resonance_type, "强共振")
        path.unlink()

    def test_missing_file_returns_empty(self) -> None:
        self.assertEqual(load_judge_scores(Path("does-not-exist.json")), {})


class TestRunReview(unittest.TestCase):
    def _prompts_dir(self) -> Path:
        return _REPO / "prompts"

    def test_empty_candidates_returns_empty(self) -> None:
        result = run_review(
            _retrieve([]),
            {"title": "", "description": ""},
            prompts_dir=self._prompts_dir(),
            llm_call=lambda _p: "",
        )
        self.assertEqual(result.review_copies, [])
        self.assertEqual(result.errors, [])

    def test_llm_error_recorded_not_raised(self) -> None:
        def boom(_prompt):
            raise RuntimeError("api down")

        result = run_review(
            _retrieve([_candidate(1, "Alpha", 2001, [], [])]),
            {"title": "T", "description": "D"},
            prompts_dir=self._prompts_dir(),
            llm_call=boom,
        )
        self.assertEqual(result.review_copies, [])
        self.assertEqual(result.errors[0]["type"], "llm_error")


class TestJudgeFilter(unittest.TestCase):
    def _pool(self):
        return [
            _candidate(1, "Keep2", 2001, [], []),
            _candidate(2, "Keep1", 2002, [], []),
            _candidate(3, "DropZero", 2003, [], []),
            _candidate(4, "DropNone", 2004, [], []),
        ]

    def _index(self):
        # tmdb 1→2, 2→1, 3→0, 4 absent (None)
        return {
            ("r", "1"): JudgeEntry(score=2),
            ("r", "2"): JudgeEntry(score=1),
            ("r", "3"): JudgeEntry(score=0),
        }

    def test_min_judge_none_keeps_all(self) -> None:
        kept, dropped = filter_candidates_by_judge(
            self._pool(), self._index(), "r", None
        )
        self.assertEqual(len(kept), 4)
        self.assertEqual(dropped, [])

    def test_min_judge_one_drops_zero_and_none(self) -> None:
        kept, dropped = filter_candidates_by_judge(
            self._pool(), self._index(), "r", 1
        )
        self.assertEqual([c["tmdb_id"] for c in kept], [1, 2])
        reasons = {d["tmdb_id"]: d["reason"] for d in dropped}
        self.assertEqual(reasons[3], "below_min_judge")
        self.assertEqual(reasons[4], "no_judge_score")

    def test_min_judge_two_keeps_only_two(self) -> None:
        kept, _ = filter_candidates_by_judge(self._pool(), self._index(), "r", 2)
        self.assertEqual([c["tmdb_id"] for c in kept], [1])

    def test_run_review_filters_before_llm(self) -> None:
        seen: dict[str, str] = {}

        def capture(prompt):
            seen["prompt"] = prompt
            return _card("Keep2", 2001) + "\n\n" + _card("Keep1", 2002)

        result = run_review(
            _retrieve(self._pool()),
            {"title": "T", "description": "D"},
            judge_index=self._index(),
            run_id="r",
            min_judge=1,
            prompts_dir=_REPO / "prompts",
            llm_call=capture,
        )
        self.assertEqual(len(result.review_copies), 2)
        self.assertEqual(len(result.dropped_candidates), 2)
        # Dropped candidates must never reach the LLM prompt.
        self.assertNotIn("DropZero", seen["prompt"])
        self.assertNotIn("DropNone", seen["prompt"])

    def test_payload_carries_filter_summary(self) -> None:
        result = run_review(
            _retrieve(self._pool()),
            {"title": "T", "description": "D"},
            judge_index=self._index(),
            run_id="r",
            min_judge=1,
            prompts_dir=_REPO / "prompts",
            llm_call=lambda _p: _card("Keep2", 2001) + "\n\n" + _card("Keep1", 2002),
        )
        payload = result_to_payload(result)
        self.assertEqual(payload["filter"]["min_judge"], 1)
        self.assertEqual(payload["filter"]["dropped_count"], 2)

    def test_no_filter_summary_when_disabled(self) -> None:
        result = run_review(
            _retrieve(self._pool()),
            {"title": "T", "description": "D"},
            judge_index=self._index(),
            run_id="r",
            min_judge=None,
            prompts_dir=_REPO / "prompts",
            llm_call=lambda _p: (
                _card("Keep2", 2001)
                + "\n\n"
                + _card("Keep1", 2002)
                + "\n\n"
                + _card("DropZero", 2003)
                + "\n\n"
                + _card("DropNone", 2004)
            ),
        )
        self.assertNotIn("filter", result_to_payload(result))


if __name__ == "__main__":
    unittest.main()
