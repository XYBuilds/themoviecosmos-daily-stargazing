# Phase 4.2 - 审核稿落 Obsidian (MVP) 交付报告

## 1. 改动范围 (Scope)

改动文件：

- `scripts/copywriter.py`（修改）：新增 Obsidian Markdown 候选块渲染（`render_review_copy_block` / `result_to_markdown`）+ CLI `--md-out` 参数与落盘逻辑（`_resolve_md_out`）。
- `tests/test_copywriter_review.py`（修改）：新增 `TestMarkdownRendering`（5 条），覆盖必备字段、勾选位永不自动勾、缺年份占位、每候选一块、文案无 hashtag。
- `README.md`（修改）：MVP 执行顺序第 5 步补 C1 审核稿完整命令与示例路径（JSON + Markdown 双产物）。
- `.cursor/plans/Phase4-copywriter-c1-c2.plan.md`（修改）：4.2 标 complete + 勾选验收项。

依赖包：无新增。

分支：`feat/phase4.2-obsidian-review`（从最新 `main` 检出，4.1 已并入 main）。

## 2. 技术实现 (Implementation)

数据流向（在 4.1 review 管线产物之上追加渲染层，read-only）：

```
ReviewResult (review_copies[] + errors[])
        │
        ├─ result_to_payload  → output/copy_review.json（4.1 已有）
        └─ result_to_markdown → output/copy_review.md（4.2 新增）
                 │
                 └─ 每 ReviewCopy → render_review_copy_block：
                      ### 《片名》(年份)
                      - 触发视角 / 切面（可选参考）/ judge_score（有则附）
                      - 中文文案（审核稿，C1）
                      - 链接 / - [ ] ✅ 选用（永不自动勾）
```

模块职责（functional 风格，纯函数 + CLI 编排）：

- `render_review_copy_block`：单条候选 → 一个 Markdown 候选块；勾选位恒为 `- [ ] ✅ 选用`（不自动替总编选用）。
- `result_to_markdown`：文档头（新闻标题 / run_id / 候选数）+ 各候选块 + errors 段汇总。
- `_resolve_md_out`：Markdown 落点解析——`--md-out` 优先；否则在给定 `--out` 时默认同名 `.md`；纯 stdout 模式不落 Markdown。
- CLI：JSON 与 Markdown 双写，均 UTF-8 编码。

A1/oracle 不出现：渲染层只消费 `review_copies`，而 `a1_oracle` 在 4.1 阶段已被显式排除在候选之外，故 Markdown 天然不含 oracle。

## 3. 本地验证结果 (Verification)

- 定向单测：`python -m unittest tests.test_copywriter_review` → 20/20 pass（含新增 5 条 Markdown 渲染测试）。
- 真实产物离线核验（`01-grid-outage`，注入 fake LLM）：19 候选 → 19 Markdown 候选块，0 errors，勾选位在场且未预勾，oracle 不出现，文档头含新闻标题/run_id/候选数。
- 全量回归（离线，`HF_HUB_OFFLINE=1` / `TRANSFORMERS_OFFLINE=1`）：`python -m unittest discover -s tests -p "test*.py"` → 214 OK，skipped=1，无 regression。
- 临时核验产物 `output/_p42_smoke.md` 已清理。

## 4. 潜在影响或技术债 (Technical Debt & Caveats)

- 4.2 仅在 4.1 review 产物上追加渲染层，未改动 review 管线本身；4.3 将用一条真实新闻跑通 `agents → retrieve → C1` 并由总编在 Obsidian 肉眼审核（Go/No-Go gate）。
- Windows 控制台 `print` 直出 ✅ 字符会因 GBK 编码报错，但文件落盘全程 UTF-8，不受影响；命令行查看建议设 `PYTHONIOENCODING=utf-8`。
- C1 一次 prompt 含多部候选，token 随候选数增长；MVP ≤8 部通常可接受。
- 平台定稿（Stage 1）未解封，须等 4.3 MVP GATE 通过。