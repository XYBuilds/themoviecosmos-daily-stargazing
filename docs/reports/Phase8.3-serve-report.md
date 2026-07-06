# Phase 8.3 - serve.py 本地 HTTP 服务器 交付报告

## 1. 改动范围 (Scope)

新增文件：

- `review_panel/serve.py`（stdlib HTTP 服务器 + 4 个 JSON API + 静态托管 index.html）
- `tests/test_review_panel_serve.py`（11 个 unittest 用例）

未修改任何既有文件（含 8.1/8.2 产物）。零第三方依赖（仅标准库 + 复用 build_data）。

## 2. 技术实现 (Implementation)

**架构：路由逻辑与传输层解耦**

- 纯路由函数 `route(method, path, query, body, *, batch_root, index_html_path, publish_adapter_path, run_subprocess)`
  分发到 `handle_index` / `handle_dates` / `handle_data` / `handle_select` / `handle_publish`，
  均不摸 socket，输入输出为 `(status_code, payload)`，可直接单测。
- `make_handler_class(...)` 用闭包生成 `BaseHTTPRequestHandler` 子类（避免全局可变状态），
  只做「解析请求 → 调 route() → 序列化响应」的薄胶水。
- `serve()` 返回已 bind 未 `serve_forever()` 的实例，便于集成测试注入随机端口。

**4 个 API**（严格按契约）：

- `GET /api/dates` → `{dates:[...]}`（倒序）
- `GET /api/data?date=...` → panel dict（按需调 `build_panel_data` 重建；date 目录不存在映射 404）
- `POST /api/select` → 写 `selection.json`（幂等整份覆盖）
- `POST /api/publish` → 读 selection，subprocess 调 `publish_adapter.py`

**subprocess 调用形态**：

```python
subprocess.run(
    [sys.executable, str(publish_adapter_path),
     "--date", date, "--news-slug", str(news_slug), "--tmdb-id", str(tmdb_id)],
    capture_output=True, text=True,
)
```

产出路径优先从 adapter 的 stderr `Wrote <path>` 解析（正则），失败才兜底拼
`batch_root/date/{slug}_copy.md`——避免两处拼路径逻辑漂移。成功后回写 `selection.published=true` + `copy_path`。

**耦合边界**：仅 import 同目录 `build_data`；触发 publish 走 subprocess，不 import `scripts.compose`。

**安全**：仅绑 `127.0.0.1`，模块 docstring 与启动日志明确「无鉴权本地面板，不可暴露公网」。

## 3. 本地验证结果 (Verification)

```
python -m pytest tests/test_review_panel_serve.py -q
........... [100%]
11 passed in 4.24s
```

覆盖：dates 倒序、data 返回 panel、select 幂等覆盖、publish 成功分支（published=true + copy_path）、
publish 失败分支（ok:false + stderr）、未知路径 404。publish 测试 monkeypatch `subprocess.run` 不真调 adapter。

lint：无诊断错误。

## 4. 潜在影响或技术债 (Technical Debt & Caveats)

- `handle_data` 对 date 目录不存在捕获 `FileNotFoundError` 映射 404；`/api/select` 缺字段返回 400——
  均为契约未明确列出的兜底健壮性，不影响主契约。
- index.html 缺失时返回占位页（plan 允许占位或 404，选占位页），8.4 产出后即正常托管。
- `main()` CLI 支持 `--port`/`--batch-root`；8.4 前端与 8.5 冒烟将基于本服务器。
- 无鉴权本地面板的安全边界已在代码与本报告中明确，需在 8.4 README/前端也保持一致提示。