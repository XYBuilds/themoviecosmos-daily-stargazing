"""serve.py · Phase 8.3 · 每日审核面板本地 stdlib HTTP 服务器.

安全边界（重要）：本服务器**无鉴权**，仅设计给审核者在本机浏览器访问，
默认且只允许绑定 ``127.0.0.1``（loopback）。**不可**改绑 ``0.0.0.0`` 或任何
公网可达地址对外暴露，否则任意能访问该端口的人都能读取 daily_batch 数据、
写 selection.json、甚至触发 publish 子进程。

架构：把「路由处理逻辑」与「HTTP 传输层」拆开——``route()`` 及其下的
``handle_*`` 都是纯函数（输入 method/path/query/body，输出
``(status_code, payload)``），不摸 socket，因此单测可以直接调用它们而不必
起真实端口；``ReviewPanelHandler``（``BaseHTTPRequestHandler`` 子类）只做
「解析请求 → 调 route() → 序列化响应」的薄传输层胶水。

耦合边界：仅 import 同目录 ``build_data``（按需重建 panel.json）；触发下游
「写推文」定稿通过 **subprocess** 调 ``publish_adapter.py``，不 import
``scripts.compose`` 等项目内部重模块，避免 serve.py 拖入项目全部依赖。
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import UTC, datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlsplit

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from review_panel.build_data import build_panel_data, list_available_dates  # noqa: E402
from scripts.lib.paths import repo_root  # noqa: E402

# 子进程调 publish_adapter.py 时用 stderr 里这一行定位「Wrote <path>」的产出路径，
# 比自己拼 {slug}_copy.md 更可靠：adapter 内部用的是 news_dir.parent 拼路径，
# 这里直接信它自己汇报的路径，避免两处拼路径逻辑长期漂移不一致。
_WROTE_LINE_RE = re.compile(r"^Wrote (.+)$", re.MULTILINE)


def _default_batch_root() -> Path:
    return repo_root() / "output" / "daily_batch"


def _default_publish_adapter_path() -> Path:
    return Path(__file__).resolve().parent / "publish_adapter.py"


def _default_index_html_path() -> Path:
    return Path(__file__).resolve().parent / "index.html"


# ---------------------------------------------------------------------------
# selection.json 读写（决策单一事实来源）
# ---------------------------------------------------------------------------


def _selection_path(batch_root: Path, date: str) -> Path:
    return batch_root / date / "selection.json"


def read_selection(batch_root: Path, date: str) -> dict[str, Any] | None:
    """读 selection.json；不存在返回 None（正常状态：审核者尚未做出选择）。"""
    path = _selection_path(batch_root, date)
    if not path.is_file():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def write_selection(batch_root: Path, date: str, payload: dict[str, Any]) -> Path:
    """写 selection.json，直接整份覆盖（幂等：最后一次选择/更新生效）。"""
    path = _selection_path(batch_root, date)
    # 日期目录理应已由 daily_batch 产物创建，但 mkdir 兜底避免测试用临时目录时因
    # 目录未预先建好而抛出无关的 FileNotFoundError。
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def _parse_wrote_path(stderr: str) -> str | None:
    match = _WROTE_LINE_RE.search(stderr or "")
    return match.group(1).strip() if match else None


# ---------------------------------------------------------------------------
# 纯路由处理函数（不摸 socket，可直接单测）
# ---------------------------------------------------------------------------


def handle_index(index_html_path: Path) -> tuple[int, str]:
    """静态托管 index.html；文件不存在（8.4 未产出前）返回占位页而非崩溃。"""
    if index_html_path.is_file():
        return 200, index_html_path.read_text(encoding="utf-8")
    placeholder = (
        "<!doctype html><html><head><meta charset=\"utf-8\">"
        "<title>Review Panel</title></head><body>"
        "<h1>Review Panel</h1>"
        "<p>index.html 尚未产出（Phase 8.4）。API 已可用："
        "/api/dates, /api/data, /api/select, /api/publish。</p>"
        "</body></html>"
    )
    return 200, placeholder


def handle_dates(batch_root: Path) -> tuple[int, dict[str, Any]]:
    return 200, {"dates": list_available_dates(batch_root=batch_root)}


def handle_data(batch_root: Path, query: dict[str, str]) -> tuple[int, dict[str, Any]]:
    date = (query or {}).get("date")
    if not date:
        return 400, {"error": "missing required query param 'date'"}
    try:
        panel = build_panel_data(date, batch_root=batch_root)
    except FileNotFoundError:
        # date 目录不存在是正常的用户输入错误（比如切到还没跑批的日期），
        # 不是服务器内部错误，用 404 而不是让异常冒泡成 500。
        return 404, {"error": f"no daily_batch data for date {date!r}"}
    return 200, panel


def handle_select(batch_root: Path, body: dict[str, Any] | None) -> tuple[int, dict[str, Any]]:
    body = body or {}
    date = body.get("date")
    news_slug = body.get("news_slug")
    tmdb_id = body.get("tmdb_id")
    title = body.get("title")
    if not date or not news_slug or tmdb_id is None:
        return 400, {"ok": False, "error": "missing required fields: date/news_slug/tmdb_id"}

    payload = {
        "date": date,
        "selected": {"news_slug": news_slug, "tmdb_id": tmdb_id, "title": title},
        "selected_at": datetime.now(UTC).isoformat(),
        "published": False,
        "copy_path": None,
    }
    path = write_selection(batch_root, date, payload)
    return 200, {"ok": True, "path": str(path), "selection": payload}


def handle_publish(
    batch_root: Path,
    body: dict[str, Any] | None,
    *,
    publish_adapter_path: Path,
    run_subprocess: Any = subprocess.run,
) -> tuple[int, dict[str, Any]]:
    body = body or {}
    date = body.get("date")
    if not date:
        return 400, {"ok": False, "copy_path": None, "stderr": "missing required field: date"}

    selection = read_selection(batch_root, date)
    if selection is None:
        return 400, {
            "ok": False,
            "copy_path": None,
            "stderr": f"no selection.json for date {date!r}; call /api/select first",
        }

    selected = selection.get("selected") or {}
    news_slug = selected.get("news_slug")
    tmdb_id = selected.get("tmdb_id")
    if not news_slug or tmdb_id is None:
        return 400, {
            "ok": False,
            "copy_path": None,
            "stderr": "selection.json missing news_slug/tmdb_id",
        }

    result = run_subprocess(
        [
            sys.executable,
            str(publish_adapter_path),
            "--date",
            date,
            "--news-slug",
            str(news_slug),
            "--tmdb-id",
            str(tmdb_id),
        ],
        capture_output=True,
        text=True,
    )

    if result.returncode == 0:
        # 优先信 adapter 自己汇报的 "Wrote <path>"（stderr），推导路径只作兜底，
        # 避免两处拼路径规则长期漂移不一致。
        copy_path = _parse_wrote_path(result.stderr) or str(
            batch_root / date / f"{news_slug}_copy.md"
        )
        selection["published"] = True
        selection["copy_path"] = copy_path
        write_selection(batch_root, date, selection)
        return 200, {"ok": True, "copy_path": copy_path, "stderr": result.stderr}

    return 500, {"ok": False, "copy_path": None, "stderr": result.stderr}


def route(
    method: str,
    path: str,
    query: dict[str, str] | None,
    body: dict[str, Any] | None,
    *,
    batch_root: Path,
    index_html_path: Path | None = None,
    publish_adapter_path: Path | None = None,
    run_subprocess: Any = subprocess.run,
) -> tuple[int, dict[str, Any] | str]:
    """纯路由分发：无 socket 依赖，单测与真实服务器共用同一份逻辑。"""
    query = query or {}

    if method == "GET" and path in ("/", "/index.html"):
        return handle_index(index_html_path or _default_index_html_path())
    if method == "GET" and path == "/api/dates":
        return handle_dates(batch_root)
    if method == "GET" and path == "/api/data":
        return handle_data(batch_root, query)
    if method == "POST" and path == "/api/select":
        return handle_select(batch_root, body)
    if method == "POST" and path == "/api/publish":
        return handle_publish(
            batch_root,
            body,
            publish_adapter_path=publish_adapter_path or _default_publish_adapter_path(),
            run_subprocess=run_subprocess,
        )
    return 404, {"error": f"not found: {method} {path}"}


# ---------------------------------------------------------------------------
# HTTP 传输层（薄胶水：解析请求 → route() → 序列化响应）
# ---------------------------------------------------------------------------


def make_handler_class(
    *,
    batch_root: Path,
    index_html_path: Path,
    publish_adapter_path: Path,
) -> type[BaseHTTPRequestHandler]:
    """按注入的 batch_root/路径生成一个 handler 类（闭包避免用全局可变状态）。"""

    class ReviewPanelHandler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:  # noqa: N802 (stdlib method naming)
            self._dispatch("GET")

        def do_POST(self) -> None:  # noqa: N802
            self._dispatch("POST")

        def _dispatch(self, method: str) -> None:
            parsed = urlsplit(self.path)
            query = {k: v[0] for k, v in parse_qs(parsed.query).items()}

            body: dict[str, Any] | None = None
            if method == "POST":
                length = int(self.headers.get("Content-Length") or 0)
                raw = self.rfile.read(length) if length else b""
                try:
                    body = json.loads(raw.decode("utf-8")) if raw else {}
                except (json.JSONDecodeError, UnicodeDecodeError):
                    self._send_json(400, {"ok": False, "error": "invalid JSON body"})
                    return

            status, payload = route(
                method,
                parsed.path,
                query,
                body,
                batch_root=batch_root,
                index_html_path=index_html_path,
                publish_adapter_path=publish_adapter_path,
            )
            if isinstance(payload, str):
                self._send_html(status, payload)
            else:
                self._send_json(status, payload)

        def _send_json(self, status: int, payload: dict[str, Any]) -> None:
            data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def _send_html(self, status: int, html: str) -> None:
            data = html.encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def log_message(self, format: str, *args: Any) -> None:  # noqa: A002
            # 静默默认访问日志；启动/关键事件由 main() 自行 print，避免噪声。
            pass

    return ReviewPanelHandler


def serve(
    *,
    port: int,
    batch_root: Path | None = None,
    index_html_path: Path | None = None,
    publish_adapter_path: Path | None = None,
) -> ThreadingHTTPServer:
    """构建并返回一个已 bind 但尚未 serve_forever 的服务器实例（便于测试注入）。"""
    root = batch_root or _default_batch_root()
    handler_cls = make_handler_class(
        batch_root=root,
        index_html_path=index_html_path or _default_index_html_path(),
        publish_adapter_path=publish_adapter_path or _default_publish_adapter_path(),
    )
    # 只绑 127.0.0.1（loopback）：这是无鉴权本地面板，绝不能改绑 0.0.0.0 对外暴露。
    return ThreadingHTTPServer(("127.0.0.1", port), handler_cls)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Serve the local review panel (stdlib http.server, loopback only, no auth).",
    )
    parser.add_argument("--port", type=int, default=8770)
    parser.add_argument("--batch-root", type=Path, default=None)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    server = serve(port=args.port, batch_root=args.batch_root)
    print(
        f"Serving review panel on http://127.0.0.1:{args.port} (local only, no auth)",
        file=sys.stderr,
    )
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("interrupted", file=sys.stderr)
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())