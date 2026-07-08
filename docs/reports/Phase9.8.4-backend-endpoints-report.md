# Phase 9.8.4 - serve /api/regenerate + /api/edit-body 交付报告

## 1. 改动范围 (Scope)

编辑文件：
- `review_panel/serve.py` — 新增两个端点 handler + 一个纯函数 + 传输层参数透传
- `tests/test_review_panel_serve.py` — 新增 3 个测试类（12 用例）

依赖变更：无。

分支继承关系：本分支 `feat/phase9.8.4-backend-endpoints` 从 phase 分支
`feat/phase9.8-panel-copy-regenerate-and-edit`（含已并入的 9.8.1/9.8.2/9.8.3）检出，未并入 main。

## 2. 技术实现 (Implementation)

**ADR-0016 D5/D6 落地：serve 新增「定点重生成」与「无 LLM 正文直改」两条入口，
严守 serve.py「薄传输层」耦合边界（不 import compose / publish_adapter / regenerate_adapter）。**

新增函数：
- `_default_regenerate_adapter_path()` — 镜像 `_default_rewrite_adapter_path()`
- `replace_body_in_copy_markdown(text, new_body) -> str` — **纯函数**，原地替换 body、逐字保留 header/headline/`## 链接` 分区
- `handle_regenerate(batch_root, body, *, regenerate_adapter_path, run_subprocess)`
- `handle_edit_body(batch_root, body)` — 无 `run_subprocess` 参数（无 LLM）

修改函数：`route()` / `make_handler_class()` / `serve()` 均新增 `regenerate_adapter_path` 参数并层层透传。

**`POST /api/regenerate`（D2/D3/D4）**：
```
handle_regenerate
  ├── 校验 date + target ∈ {headline, body}
  ├── slug 兜底自 selection.selected.news_slug
  ├── tmdb_id 从 selection.selected.tmdb_id 读出（面板不传，adapter 定位 candidate 必需）
  ├── subprocess: regenerate_adapter.py --date/--slug/--tmdb-id/--platform/--target
  ├── returncode≠0 → 500 echo stderr
  └── 成功 → parse_copy_markdown(Wrote 路径)
        target=body：adapter 已删 humanized 文件 → serve 同步清 selection.copies[p].humanized_path=None
        target=headline：不动 humanized / selection
      返回 {ok, target, headline, body, copy_path, stderr}
```

**`POST /api/edit-body`（D5，无 LLM）**：
```
handle_edit_body
  ├── 校验 date + body 非空 + slug 兜底
  ├── 定位 {slug}_copy_{platform}.md（缺 → 404）
  ├── replace_body_in_copy_markdown 纯文本拼接写回（headline/链接逐字不变）
  ├── D4 失效：_delete_copy_if_exists(_humanized.md) + 清 selection humanized_path
  └── 返回 {ok, headline, body, platform}
```

**关键架构决策（对 plan 文本的合理偏离，已确认符合其意图）**：
plan 9.8.4 描述「edit-body 经 `render_copy_markdown` 写回」。但 `serve.py` 有明确核心不变量
——它是**薄传输层，绝不 import `scripts.compose`**（保证测试导入快、依赖足迹小），而
`publish_adapter.render_copy_markdown` 会**传递性拉入 compose**。因此 edit-body 改为
**serve 内纯文本 splice**（`replace_body_in_copy_markdown`，与既有 `parse_copy_markdown` 同层对称，
serve 本就拥有该文件格式的读契约）。这同时更好地满足了 plan 自己的验收标准「headline/链接不变」
——逐字保留而非重新渲染，天然字节级不变。已用 import 断言守护该不变量（见验证）。

## 3. 本地验证结果 (Verification)

```
python -m pytest tests/test_review_panel_serve.py -q
.............................................                            [100%]
45 passed in 4.40s
---IMPORT CHECK---
serve import OK, compose NOT loaded
```

新增 3 个测试类（12 用例）：
- `ReplaceBodyInCopyMarkdownTests`：normal / 多段 body / 无链接分区三种形态
- `EditBodyRouteTests`：成功（body 换、headline+链接不变、humanized 文件删除 + selection humanized_path 归 None）、空 body 400、缺 copy 404、slug 兜底
- `RegenerateRouteTests`：target=body（覆盖 body、清 humanized_path）、target=headline（覆盖 headline、humanized 保留）、target 非法 400、缺 tmdb_id 400、subprocess 失败 500

导入断言 `assert 'scripts.compose' not in sys.modules`：确认 serve 导入时 compose 未被拉入，薄传输层不变量成立。既有 33 个用例无回归。

## 4. 潜在影响或技术债 (Technical Debt & Caveats)

- **对后续 Phase 的依赖**：9.8.5 前端将调这两个端点（正文可编辑 textarea → `/api/edit-body`；「重生成正文/标题」按钮 → `/api/regenerate`），并据 `target=body` 后 humanized 已失效来复位去AI化 toggle。
- **`replace_body_in_copy_markdown` 与 `render_copy_markdown` 的格式耦合**：两者对 `# 发布定稿` / `## 链接` 排版契约必须保持一致；若未来 D1 排版变更，需同步这两处（已在 docstring 标注意图）。当前通过纯函数测试断言其输出可被 `parse_copy_markdown` 正确回读来间接锁定契约。
- **tmdb_id 来源**：regenerate 依赖 selection.json 里已落盘的 tmdb_id；未选片（无 selection）直接 400，符合「先选片再操作」的面板流程。
- **环境说明**：验证使用系统 Python（仓库无 `.venv`）。
- **无人工验收阻断**：本 TODO 非 `[需人工验收]`，按标准流水线进入合并（PR base 为 phase 分支）。