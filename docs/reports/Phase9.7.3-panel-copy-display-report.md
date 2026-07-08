# Phase 9.7.3 - 面板定稿展示区 交付报告

## 1. 改动范围 (Scope)

- `review_panel/serve.py` — 新增纯函数 `parse_copy_markdown()` + `handle_copy()` + `GET /api/copy` 路由。
- `review_panel/index.html` — 新增定稿展示区 `#copy-panel`（platform tabs + headline/body 渲染 + 空态），`loadCopy()` 拉取逻辑。
- `tests/test_review_panel_serve.py` — `ParseCopyMarkdownTests` + `CopyRouteTests`。
- 新增/删除依赖：无（serve.py 纯 stdlib，index.html 零依赖）。

## 2. 技术实现 (Implementation)

**`parse_copy_markdown(text) -> {headline, body}`（纯函数）**：对齐 `render_copy_markdown` 的 D1 排版——跳过前导空行 + `# 发布定稿…` H1，其后第一个非空行为 headline，body 取到（不含）`## 链接` 前的全部内容并 strip。缺 H1/headline/链接分区均容错返回空串，可脱离 IO 单测。

**`GET /api/copy?date=&slug=&platform=`（默认 xiaohongshu）契约**：
- 缺 date/slug → 400 `{error}`
- `{slug}_copy_{platform}.md` 不存在 → 404 `{error}`（前端渲染空态）
- 成功 → 200 `{headline, body, humanized_body, has_humanized, platform}`

humanized 文件解析是 **9.7.4 的前瞻只读兼容**：本 TODO 不写它，仅在其已存在时顺带解析出 `humanized_body`，让 9.7.4 无需再改此 handler。

**前端**：`#copy-panel` 含 `#copy-platform-tabs`（`ACTIVE_COPY_PLATFORMS=["xiaohongshu"]` 驱动，x/reddit 渲染为 disabled「coming soon」），`#copy-content` 内含 `#copy-humanize-toggle-slot` 空容器预留给 9.7.4 的去AI化 toggle。body 用 `white-space: pre-wrap` 保留换行。`loadCopy()` 在选片 / publish 成功 / tab 切换时触发；切日期时重置隐藏旧定稿。

## 3. 本地验证结果 (Verification)

```
python -m pytest tests/test_review_panel_serve.py -q
25 passed in 5.71s
```
（含 `ParseCopyMarkdownTests` 4 项 + `CopyRouteTests` 5 项）。ReadLints 无告警。

## 4. 潜在影响或技术债 (Technical Debt & Caveats)

- `parse_copy_markdown` 依赖 D1 固定排版（H1 → headline → body → `## 链接`）；若 render 模板再变，解析规则需同步（两处形状耦合，已在 docstring 标注对齐关系）。
- 「去AI化」toggle 按钮尚未实现，仅预留 `#copy-humanize-toggle-slot` 容器 + `handle_copy` 已返回 `humanized_body/has_humanized` → 9.7.4 只需填充前端 toggle + 写 rewrite 链路。
- 分支继承：`feat/phase9.7.3-panel-copy-display` 从集成分支检出（已含 9.7.1/9.7.2 合并结果）。