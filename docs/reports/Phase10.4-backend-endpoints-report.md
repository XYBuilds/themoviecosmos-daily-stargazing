# Phase 10.4 - serve 草稿池后端端点 交付报告

## 1. 改动范围 (Scope)

- `review_panel/serve.py`：新增三个 POST 端点及其纯路由处理函数、草稿池只读读取 + 派生当前稿的纯胶水、`drafts_adapter_path` 注入链路。
- `tests/test_review_panel_serve.py`：新增三组测试类覆盖三端点（生成/选中/合并）+ 边界与失效不变量。
- 无新增/删除依赖包（仍是 stdlib http.server + subprocess）。

## 2. 技术实现 (Implementation)

### 端点与职责边界（ADR-0017 D3/D4/D5/D6）

三个端点严格沿用 9.8 既有形态，`route()` → `handle_*` 纯函数（输入 method/path/query/body，输出 `(status, dict)`），HTTP 传输层不变：

- **`POST /api/generate-drafts`**（`{date, slug?, platform?}`）→ subprocess 调 `drafts_adapter.py` 全量扇出，同 `handle_publish`/`handle_regenerate` 的 subprocess 隔离 LLM 模式。slug/tmdb_id 从 selection.json 兜底；成功后解析 stderr 的 `Wrote <path>` 读回只读草稿池数组一并返回。**本端点不动 selection.json**——「产池」与「选中」分离。
- **`POST /api/select-draft`**（`{date, slug?, platform?, draft_id}`）→ **无 LLM**，serve 直接读池 + 派生当前稿。指针语义：读 `{slug}_drafts_{platform}.json` 取 `draft_id` → 本地渲染 `{slug}_copy_{platform}.md` → 失效 humanized（删 `_humanized.md` + 清 `humanized_path`）→ 写 `selected_draft_id`（可变指针）。草稿池只读，选中不消费/删除任何草稿。
- **`POST /api/combine-drafts`**（`{date, slug?, platform?, draft_ids}`）→ subprocess `--combine a,b`，**恒调单版**（不传 `--combine-mode`，由 adapter 默认生产路线决定）；>2 目标由 serve 层直接 4xx 拦掉（不启动 subprocess），恰好 2 的硬约束单一收敛在 adapter。成功后读回池返回，**不自动切指针**。

### 耦合边界（关键设计约束）

`serve.py` 必须保持薄传输层、**不可 import `scripts.compose`**（`publish_adapter` 也不行——它经 compose 拖入检索/persona 重依赖）。因此：

- **generate/combine** 走 subprocess（LLM 隔离在 adapter 进程）。
- **select-draft** 无 LLM，但派生当前稿需渲染「## 链接」分区，而草稿池只存 `{draft_id, headline, body}` 不含链接。故新增两个本地纯函数，与既有 `parse_copy_markdown`/`replace_body_in_copy_markdown` 同因（自带轻量实现避免拖重依赖）：
  - `_load_copy_links(batch_root, date, slug, tmdb_id)`：直接读 `news.json`（news_url）+ `retrieve.json`（按 tmdb_id 定位 candidate.movie_url），文件/字段缺失容错空串。
  - `render_copy_markdown_from_draft(...)`：逐字对齐 `publish_adapter.render_copy_markdown` 的产出排版，保证派生稿能被既有 `parse_copy_markdown` / `/api/copy` 无差别消费。

### 注入链路

新增 `_default_drafts_adapter_path()` + `_MAX_COMBINE=2` + `_PLATFORM_LABELS`（渲染标题的平台中文名）。`drafts_adapter_path` 沿 `route()` → `make_handler_class()` → `serve()` 全链路可注入，与既有 publish/rewrite/regenerate adapter 注入模式一致。三端点共用 `_resolve_selected()` 兜底解 `(slug, tmdb_id, selection)`（同 handle_regenerate 兜底口径）。

### `selected_draft_id` 向后兼容

selection.json 的 `copies[platform]` 条目扩 `selected_draft_id`（D4）。旧条目无此字段视为 None；只有 select-draft 写入非 None 值，其它 handler（publish/rewrite/regenerate/edit-body）重建 copies 条目时不带该字段（语义正确：那些动作使当前稿脱离池指针，重置为 None 是干净的）。

## 3. 本地验证结果 (Verification)

```
python -m pytest tests/test_review_panel_serve.py -q
..........................................................               [100%]
58 passed in 4.52s

python -m pytest tests/test_review_panel_drafts_adapter.py tests/test_review_panel_publish_adapter.py -q
..............................                                           [100%]
30 passed in 25.50s
```

新增测试覆盖：generate-drafts 成功（断言 subprocess 命令行 + 无 `--combine`）/缺 selection 4xx/缺 date 4xx/subprocess 失败 500；select-draft 派生当前稿 + 写 `selected_draft_id`（断言链接分区含 movie_url）/改选失效 humanized/未知 draft_id 4xx/缺池 404/缺 draft_id 4xx；combine-drafts 合并两条 append 单版（断言不传 `--combine-mode both`）/>2 不启动 subprocess 直接 4xx/非 list 4xx。既有 publish/regenerate/rewrite/edit-body/copy/select 全部无回归。

## 4. 潜在影响或技术债 (Technical Debt & Caveats)

- **前端未接入（10.5）**：三端点已可用，但 index.html 尚无草稿池 UI；10.5 才把「生成草稿池/选主视角/合并 ≤2」接上，选中后流入既有 publish/去AI化工作流。
- **`render_copy_markdown_from_draft` 与 `publish_adapter.render_copy_markdown` 是两份**：为守 serve 薄传输层耦合边界刻意复制（同 parse/replace 先例）。二者排版必须逐字一致，否则派生稿与 publish 产出会漂移——测试已断言 select-draft 产出含标准「## 链接 + movie_url」结构兜底。未来若 render 排版变更需两处同步。
- **combine `--combine-mode` 生产默认**：serve 恒调单版，具体走 A 还是 B 由 `drafts_adapter` 的 `--combine-mode` 默认值决定（当前 `A`）。10.7 GATE 选型冻结后若改默认路线，只需改 adapter 默认，serve 无需动。
- **select-draft 无 selection.json 时**：若 body 显式带 slug+tmdb_id 但无 selection，当前稿会写出但 `selected_draft_id` 不落盘（无 selection 对象可更新）。实际面板恒先 /api/select 建 selection，不触发此路径。