# Phase 8.4 - index.html 前端面板 交付报告

## 1. 改动范围 (Scope)

新增文件：

- `review_panel/index.html`（单文件原生 JS 审核面板，791 行，内联 CSS+JS）
- `review_panel/README.md`（面板说明、启动方式、API 表、数据流、安全边界、关键元素 id 清单）

零第三方依赖（无框架、无构建、无 CDN），由 `serve.py` 在 `GET /` 托管。

## 2. 技术实现 (Implementation)

**设计方向**：编辑部深色报刊风——暗炭底 + 暖纸白正文 + 琥珀强调色，等宽字体点缀数据
（similarity/日期/tmdb_id），judge_score 用色块分层（2=绿 / 1=中性米 / 0/null=灰），
让审核者快速扫过 10 条新闻上百候选时一眼定位高分候选。用 CSS 变量组织配色。

**布局**：顶部工具条（标题 + 日期下拉 + 写推文主按钮）+ 主区按新闻分组卡片。每张新闻卡含
新闻头（index/title/source/pub_time/url/description）+ 候选列表（片名年份、language、genres、
similarity、共振 agent 徽章、judge 分数色块、resonance_type/rationale/causal_test 判空隐藏、
overview、movie_url 跳转、单选控件）。

**全天唯一单选**：所有候选 radio 共享固定 `name="daily-pick"`，靠浏览器原生 radio group 语义
天然互斥，无需额外 JS。

**交互**：选中即 `POST /api/select`（幂等覆盖）→ 顶部显示已选状态 + 启用写推文按钮；
写推文 → loading（禁用 + spinner）→ `POST /api/publish {date}` → 成功显示 copy_path、失败显示 stderr。

**健壮性**：`apiGet`/`apiPost` 封装区分传输层错误（非 JSON）与业务错误（ok:false）；网络错误、
404、500 都在 `#error-banner` / `#publish-result` 显示；空数据有 `#empty-state` 友好提示；
可能为 null/空的字段用 `hasText()`/`safeText()` 判空，不渲染成 "null"/"undefined"。

**关键元素 id/class**（README 列全）：`#date-select` `#publish-btn` `#selection-status`
`#error-banner` `#publish-result` `#news-list` `.news-card` `.candidate`（`.is-selected`）
`.candidate-select` `.score-badge`（`.score-2/1/0`）`.agent-badge` `#loading-state` `#empty-state`。

## 3. 本地验证结果 (Verification)

契约逐字核对（与 serve.py 一致）：`/api/select` body = `{date, news_slug, tmdb_id, title}`、
`/api/publish` body = `{date}`、URL/method 正确。

真实服务器联通烟测（`serve.py --port 8771` + 探针脚本）：

```
dates: ['2026-07-06-smoke', '2026-07-06', ...]   # /api/dates 返回 7 个日期
news_items: 10                                    # /api/data 返回 10 条新闻
first candidates: 19
cand keys: [causal_test, genres, judge_rationale, judge_resonance_type, judge_score,
            language, movie_url, overview, poster_path, release_year, resonance_agents,
            similarity, title, tmdb_id]           # 与 panel.json schema 完全一致
html contains id="date-select" / id="publish-btn" / id="news-list" / /api/select / /api/publish : all True
```

JS 语法：Node `--check` 提取内联 JS 通过；HTML 标签配平校验通过；lint 无报错。
真实浏览器交互留待 8.5 人工验收。探针脚本已清理，服务器已停止。

## 4. 潜在影响或技术债 (Technical Debt & Caveats)

- 按「禁止外部 CDN」约束，`poster_path` 字段保留但不渲染海报图（避免加载 TMDB 外部图片），
  候选信息全部以文字呈现。
- 前端真实交互（点选、写推文触发真实 LLM 定稿）属 8.5 人工验收范围。
- 安全边界：无鉴权本地面板，仅绑 127.0.0.1，前端页脚与 README 均已明确「勿公网暴露」。