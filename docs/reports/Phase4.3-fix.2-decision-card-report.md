# Phase 4.3-fix.2 - 选片决策卡重构交付报告

## 1. 改动范围 (Scope)
- 更新 `prompts/compose_review.md`：从旧 C1 审核稿改为非创作选片决策卡 prompt。
- 更新 `scripts/compose.py`：review 阶段改为 judge 投影 + DB 投影 + 新闻原文链接 + causal_test/rationale 双语并列。
- 新增 `tests/test_compose_decision_card.py`：覆盖决策卡输入/输出不含读者级创作字段、DB 投影、新闻原文链接、双语字段。
- 更新 `.cursor/plans/Phase4-copywriter-c1-c2.plan.md`：标记 4.3-fix.2 complete。
- 新增/删除依赖包：无。

## 2. 技术实现 (Implementation)
- 决策卡不再要求标题、读者文案、电影介绍、Hashtag；LLM 仅负责 `causal_test` / `rationale` 的 ZH 忠实直译，并保留 EN 原文。
- 每个候选从通路 B 按 `tmdb_id` 取得 DB 投影字段，包含导演、评分、热度等可用事实；缺失时回退候选自带 overview/genres/title。
- Markdown/JSON 输出均改为非创作结构：`db_projection`、`judge.causal_test.en/zh`、`judge.rationale.en/zh`、`movie_url`、`news_url`。

## 3. 本地验证结果 (Verification)
- `python -m pytest tests/test_compose_decision_card.py tests/test_movie_metadata.py tests/test_retrieve_multi_pseudo.py tests/test_retrieve_funnel.py`
  - 结果：`20 passed in 21.08s`

## 4. 潜在影响或技术债 (Technical Debt & Caveats)
- 本分支继承自 `feat/phase4.3-fix.1-db-fullcolumn-lookup`，因为 4.3-fix.1 PR 尚未合并入 `main`。
- CLI 名称仍是 `--stage review`，但语义已按 ADR-0012 收敛为“选片决策卡”；物理拆出 compose 之外属于 ADR-0012 D4 后续方向。
- 旧 golden 的创作字段不再适用；后续 4.3-fix.4 人工 GATE 应按新决策卡口径验收。