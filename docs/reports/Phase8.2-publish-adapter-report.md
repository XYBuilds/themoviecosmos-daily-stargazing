# Phase 8.2 - publish_adapter.py 薄适配脚本 交付报告

## 1. 改动范围 (Scope)

新增文件：

- `review_panel/publish_adapter.py`（daily_batch → C2 定稿薄适配脚本 + CLI）
- `tests/test_review_panel_publish_adapter.py`（14 个 unittest 用例）

未修改任何既有文件。无新增第三方依赖（复用 `scripts.compose.run_publish`）。

## 2. 技术实现 (Implementation)

解决决策冲突：`scripts/main.py publish` 消费 Phase6 单条产物（`Daily_Briefing/{date}.md` +
`{date}_candidates.json`），而 daily_batch 产物在 `output/daily_batch/{date}/{slug}/`，结构不同、
无法直接复用其定位函数。本脚本直接从日批目录取 news + candidate + judge，调用稳定的
`compose.run_publish` 产出 `{slug}_copy.md`。

可测函数拆分：

- `locate_news_dir(date, slug, batch_root)`：定位日批新闻目录，缺失清晰报错。
- `load_news(news_dir)`：读 `news.json`，瘦身出 run_publish 需要的字段。
- `find_candidate(news_dir, tmdb_id)`：按 `str()` 归一化在 candidates 定位候选。
- `load_judge_entry(news_dir, tmdb_id) -> JudgeEntry | None`：读 judge 分数构造 `JudgeEntry`，缺失容错 None。
- `render_copy_markdown(...)`：轻量渲染 `_copy.md`（四段：标题 / 中文正文 / 新闻原文 / 链接）。
- `run_adapter(...)`：orchestrator，`run_publish` 作为可注入依赖便于测试。

**耦合收敛**：本文件是全 Phase 唯一 import `scripts.compose` 的耦合点。`compose` 只依赖
openai/movie_metadata，是安全耦合点；刻意**不** import `scripts.main.build_copy_markdown`，
因为 `scripts.main` 顶层会连带拉入 extract/retrieve/rewrite/fetch_news 等重模块，违背
plan「耦合收敛在本单文件」约束。故自带一份风格等价的轻量渲染函数（已在 docstring 注明理由）。

**tmdb_id int/str 归一化**：CLI 传入可能 int/str，`retrieve.json` 的 candidate.tmdb_id 是 int，
`llm-judge-scores.json` 的 scores[].tmdb_id 是 str；`find_candidate` / `load_judge_entry` 统一
`str()` 后比较。

## 3. 本地验证结果 (Verification)

```
python -m pytest tests/test_review_panel_publish_adapter.py -q
.............. [100%]
14 passed in 29.74s
```

覆盖点：candidate int/str 定位、judge 作为 JudgeEntry 传入 run_publish、`{slug}_copy.md` 产出、
找不到 tmdb_id / slug 目录的非零退出、judge 文件缺失时 judge=None 仍产出。

lint：无诊断错误。

## 4. 潜在影响或技术债 (Technical Debt & Caveats)

- 与 `main.py publish` 并存两套 publish 入口的技术债（plan 已注明）：长期可考虑
  `main.py publish --from-daily-batch` 统一，本 Phase 不做。
- `main()` CLI 未暴露 `--batch-root`（`run_adapter` 支持该参数）；测试通过 monkeypatch
  `_default_batch_root` 隔离真实 repo 路径。若后续 serve.py 需要自定义 batch-root 可再补 CLI 参数。
- 后续 8.3 `serve.py` 将以 subprocess 调用本脚本，不 import 项目内部模块。