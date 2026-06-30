# Phase 4.3-fix.3 - 发布稿重构交付报告

## 1. 改动范围 (Scope)
- 更新 `prompts/compose_publish.md`：从多平台改写 prompt 改为单一发布稿创作 prompt。
- 更新 `scripts/compose.py`：新增 `publish` stage、选定单片输入组装、DB 数字投影、judge 内核透传。
- 新增 `tests/test_compose_publish.py`：覆盖真实评分/热度数字注入、judge 内核消费、单稿非平台变体约束。
- 更新 `.cursor/plans/Phase4-copywriter-c1-c2.plan.md`：标记 4.3-fix.3 complete；未触碰 4.3-fix.4。
- 新增/删除依赖包：无。

## 2. 技术实现 (Implementation)
- `compose --stage publish` 现在只接受选定 `--tmdb-id` 的 1 部电影，不再生成多平台变体。
- 发布稿 prompt 明确以电影介绍为主体，要求用通路 B 的真实数字（如 `vote_average`、`vote_count`、`popularity`、`imdb_rating`）支撑“热度 vs 质量”。
- `run_publish()` 将选定片 DB 投影、新闻语境、judge 内核（score/type/causal_test/rationale）一起送入 LLM；director/runtime/cast/writers 等字段有则用，无则自然省略。

## 3. 本地验证结果 (Verification)
- `python -m pytest tests/test_compose_publish.py tests/test_compose_decision_card.py tests/test_movie_metadata.py tests/test_retrieve_multi_pseudo.py tests/test_retrieve_funnel.py`
  - 结果：`24 passed in 22.48s`
- `python scripts/compose.py --help; python -m pytest tests/test_compose_publish.py tests/test_compose_decision_card.py tests/test_movie_metadata.py tests/test_retrieve_multi_pseudo.py tests/test_retrieve_funnel.py`
  - 结果：CLI help 正常展示 `--stage {review,publish}`；`24 passed in 21.60s`
- 期间 CLI smoke 首次暴露 `main` 定义被误移除，已修复并复测通过。

## 4. 潜在影响或技术债 (Technical Debt & Caveats)
- 本分支继承自 `feat/phase4.3-fix.2-decision-card`，因为 4.3-fix.2 PR 尚未合并入 `main`。
- 发布稿当前仍通过同一个 `compose.py` 承载；选片决策卡物理拆出 compose 的终态重构仍按 ADR-0012 D4 后置。
- 本 TODO 不执行 4.3-fix.4 Go/No-Go；人工验收重跑链路需在后续 GATE 中单独进行。