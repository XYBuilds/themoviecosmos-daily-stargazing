# Phase 9.7.4 - avoid-ai-writing 集成 交付报告

## 1. 改动范围 (Scope)

- `prompts/avoid_ai_writing_rewrite.md` [新] — 蒸馏 avoid-ai-writing rewrite 规则的改写 prompt（`{{body}}` 占位）。
- `review_panel/rewrite_adapter.py` [新] — subprocess 改写适配脚本（与 publish_adapter 同层）。
- `review_panel/serve.py` — 新增 `handle_rewrite` + `POST /api/rewrite` + `_default_rewrite_adapter_path`，`rewrite_adapter_path` 全链路穿透。
- `review_panel/index.html` — `#copy-humanize-toggle-slot` 内「去AI化/重新生成」按钮 + 原版/去AI化版可逆 toggle。
- `tests/test_review_panel_serve.py`（`RewriteRouteTests`）+ `tests/test_review_panel_rewrite_adapter.py` [新]。
- 新增/删除依赖：无。

## 2. 技术实现 (Implementation)

**D5 subprocess 架构（决策已定）**：`serve.py → subprocess → rewrite_adapter.py → scripts.lib.llm`。serve.py 不 import LLM 模块，与 publish 链路对称。

- **prompt**：硬约束首行归属行逐字保留、不引入小红书禁词、不编造事实、只输出正文；去 AI 味清单（句长单调 / 空洞套话 / 滤镜强调词 / 三项式排比 / 转折词滥用 / 抽象泛谈 / 机械对称）+ 保留项（信息量 / 调性 / 字数量级 / 已自然的句子不动）。
- **rewrite_adapter.py**：`run_adapter(date, slug, *, platform, provider, batch_root, call_llm)`——读原稿 → `parse_copy_markdown` 抽 body → 渲染 prompt → LLM → 写 `_humanized.md`。`call_llm` 可注入（默认 `_real_call_llm`），测试用 stub 免网络。链接段用 `_extract_links_block` 直接摘原文，不重拼 URL（避免第二处渲染漂移）。`_model_name`/`_MODEL_ENV` 小范围复制自 compose（耦合止于 `scripts.lib.*`，与 publish_adapter 注释理由一致）。`Wrote <path>` → stderr。
- **`POST /api/rewrite` 契约**：body `{date, slug?, platform?}`；缺 date→400；缺 slug 从 selection `selected.news_slug` 兜底；子进程失败→500；成功→解析 `Wrote`、读回 humanized body、更新 `selection.copies[platform].humanized_path`（保留 published/copy_path），返回 200 `{ok, humanized_path, humanized_body, stderr}`。
- **前端**：仅当有 humanized 数据时显示 toggle；点击去AI化 POST → spinner → 成功切到去AI化视图；`loadCopy()` 从 `/api/copy` 的 `has_humanized/humanized_body` 预置态（刷新不丢）；再点即覆盖重生，原版 `state.originalBody` 不变。

## 3. 本地验证结果 (Verification)

```
python -m pytest tests/test_review_panel_serve.py tests/test_review_panel_rewrite_adapter.py -q
34 passed in 8.99s
```
子代理另跑全量 `pytest tests/ -q` → 406 passed, 1 skipped（既有 skip 无关本改动）。ReadLints 无告警。

## 4. 潜在影响或技术债 (Technical Debt & Caveats)

- 真实 LLM 改写质量未在单测覆盖（stub 免网络）——由 9.7.7 GATE 真实重跑肉眼验收 toggle 与改写效果。
- `_model_name`/`_MODEL_ENV` 现在在 compose.py 与 rewrite_adapter.py 两处存在（有意的耦合边界代价）；若第三处再复制应考虑抽到 `scripts/lib/`。
- humanized 稿的链接段依赖原稿存在 `## 链接`；原稿格式变动需同步 `_extract_links_block`。
- 分支继承：`feat/phase9.7.4-avoid-ai-rewrite` 从集成分支检出（已含 9.7.1–9.7.3 合并结果）。