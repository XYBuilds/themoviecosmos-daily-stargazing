# Phase 3.1 - run_eval 评测管线 交付报告

## 1. 改动范围 (Scope)

- `scripts/run_eval.py` — 新增评测管线 CLI 与 Markdown 渲染
- `.cursor/plans/Phase3-validation-gate-the-bet.plan.md` — Todo 3.1 标记 complete

无新增 Python 依赖。

## 2. 技术实现 (Implementation)

- **CLI**：`--news-file`（必填）、`--run-id`（默认 title slug 或 UTC 时间戳）、`--out`（默认 `output/Eval/{run_id}.md`）、`--provider`
- **管线**：`asyncio.run(run_all(news))` → `agent_to_dict` 列表 → `retrieve_from_agents(agents, errors)`（库内 import，无 subprocess）
- **Markdown**：元信息、现实波澜、伪剧情（A2/A4/A7/A1，A1 带 `[baseline]`）、errors、divergence（`<details>` 折叠 JSON）、候选星轨（`triggered_by` 仅创作视角；仅基线为 `[baseline only]`；每条含共振分 HTML 注释占位）
- **辅助**：`slugify()` / `default_run_id()` 从标题生成 ASCII-safe run_id

## 3. 本地验证结果 (Verification)

```powershell
cd t:\themoviecosmos-daily-stargazing
python scripts/run_eval.py --news-file tests/sample_news.json --out output/Eval/sample.md
```

- exit **0**；写入 `output/Eval/sample.md`
- 四段 pseudo（A2、A4、A7、A1 `[baseline]`）；`errors` 为「（无）」
- **8** 部候选，每条含 `- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->`
- LLM（`.env`）与 sentence-transformers 索引均可用；首次运行会下载/加载 embedding 模型（约 60s）

## 4. 潜在影响或技术债 (Technical Debt & Caveats)

- `output/Eval/*.md` 为运行时产物，未纳入 git
- Phase 3.2 `summarize_eval.py` 将依赖本 Markdown 格式解析共振分
- 每次 `run_eval` 加载 embedding 模型与 59k 索引，评测批量时注意内存与耗时
- 后续 Phase 6 可抽离 `render_briefing.py` 与 `run_eval` 共用渲染逻辑
