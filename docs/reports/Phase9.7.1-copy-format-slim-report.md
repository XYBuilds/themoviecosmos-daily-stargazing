# Phase 9.7.1 - 产出格式精简 + headline ≤10 中文字约束 交付报告

## 1. 改动范围 (Scope)

- `review_panel/publish_adapter.py` — `render_copy_markdown()` 重写为精简模板；新增 `_PLATFORM_LABELS` dict、`_count_chinese_chars()` helper、`platform` 关键字参数、超限 `logger.warning`。
- `prompts/compose_publish_xiaohongshu.md` — `## headline` 小节新增硬约束 bullet「≤ 10 个中文字（不含标点）」。
- `tests/test_review_panel_publish_adapter.py` — 更新旧格式断言为新格式；新增 headline 独立成行 / 超长不截断两个用例。
- 新增/删除依赖：无。

## 2. 技术实现 (Implementation)

prompt + 渲染层双保证（plan D2）：
- **prompt 层**（主保证）：headline 约束加「≤ 10 个中文字（不含标点）」，由 LLM 生成时约束。
- **渲染层**（兜底观测）：`render_copy_markdown` 用 `_count_chinese_chars`（`\u4e00`–`\u9fff` 计数，不含标点）统计，超 10 只 `logger.warning`、**不截断**——避免破坏 LLM 已生成的语义完整标题，是否调 prompt 交由 9.7.7 GATE 人工判断。

精简模板（plan D1 目标态）：
```
# 发布定稿 · {date} · {platform_label}

{headline}          ← 独立成行，无 "## 小红书标题（headline）" 标签

{body}              ← 无 "## 中文发布正文" 标签

## 链接
- 电影: {movie_url}
- 新闻: {news_url}
```
去掉了三段：`## 小红书标题（headline）`、`## 中文发布正文`、整个 `## 新闻原文（English source）` section。`platform` 参数经 `_PLATFORM_LABELS` 映射为中文标签（xiaohongshu→小红书），为 9.7.2 多平台命名预留。

## 3. 本地验证结果 (Verification)

```
python -m pytest tests/test_review_panel_publish_adapter.py tests/test_compose_publish.py -q
28 passed in 45.69s
```
`test_review_panel_publish_adapter.py` 16 passed（含新增 3 项断言 + 2 个新用例）；`test_compose_publish.py` 12 passed（prompt 改动无回归）。ReadLints 无告警。

## 4. 潜在影响或技术债 (Technical Debt & Caveats)

- `run_adapter` 当前仍以 `{slug}_copy.md` 写盘且未把 `platform` 透传给 `render_copy_markdown`（渲染层 `platform` 默认 xiaohongshu 即可正确工作）——文件名平台化 + platform 透传是 **9.7.2** 的职责，本 TODO 有意不动。
- headline 10 字为软兜底（仅 warning 不截断），真实 LLM 偶发超限需 9.7.7 GATE 肉眼确认。
- 分支继承：本分支 `feat/phase9.7.1-copy-format-slim` 从集成分支 `feat/phase9.7-copy-output-and-panel-integration` 检出（Phase 9.1–9.6 已开发未合并入 main，全部栈在该集成分支上）。