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
# 比自己拼 {slug}_copy_{platform}.md 更可靠：adapter 内部用的是 news_dir.parent 拼路径，
# 这里直接信它自己汇报的路径，避免两处拼路径逻辑长期漂移不一致。
_WROTE_LINE_RE = re.compile(r"^Wrote (.+)$", re.MULTILINE)

# 当前已实现的发布平台清单（D3）。新增平台时只需在此追加一项，改选时的陈旧稿清理、
# selection.json 的 copies dict 初始化等下游逻辑无需改动即可覆盖新平台。
_ACTIVE_PLATFORMS: tuple[str, ...] = ("xiaohongshu",)


def _default_batch_root() -> Path:
    return repo_root() / "output" / "daily_batch"


def _default_publish_adapter_path() -> Path:
    return Path(__file__).resolve().parent / "publish_adapter.py"


def _default_rewrite_adapter_path() -> Path:
    return Path(__file__).resolve().parent / "rewrite_adapter.py"


def _default_regenerate_adapter_path() -> Path:
    return Path(__file__).resolve().parent / "regenerate_adapter.py"


def _default_index_html_path() -> Path:
    return Path(__file__).resolve().parent / "index.html"


# ---------------------------------------------------------------------------
# selection.json 读写（决策单一事实来源）
# ---------------------------------------------------------------------------


def _selection_path(batch_root: Path, date: str) -> Path:
    return batch_root / date / "selection.json"


def _migrate_selection(selection: dict[str, Any]) -> dict[str, Any]:
    """D4 向后兼容：旧格式（顶层 published/copy_path）无损迁移为 copies dict。

    旧格式没有 platform 维度，历史数据只可能是 xiaohongshu；迁移后不留旧字段，
    保证下游代码只需认识 ``copies`` 这一种形状。已是新格式（存在 ``copies``）时原样返回。
    """
    if "copies" in selection:
        return selection

    migrated = dict(selection)
    old_published = migrated.pop("published", False)
    old_copy_path = migrated.pop("copy_path", None)
    migrated["copies"] = {
        "xiaohongshu": {
            "published": bool(old_published),
            "copy_path": old_copy_path,
            "humanized_path": None,
        }
    }
    return migrated


def read_selection(batch_root: Path, date: str) -> dict[str, Any] | None:
    """读 selection.json；不存在返回 None（正常状态：审核者尚未做出选择）。

    读出后立即做 D4 迁移，让所有下游调用点只看到新的 ``copies`` dict 形状。
    """
    path = _selection_path(batch_root, date)
    if not path.is_file():
        return None
    raw = json.loads(path.read_text(encoding="utf-8"))
    return _migrate_selection(raw)


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


def _delete_copy_if_exists(path: Path) -> bool:
    """删一份 {slug}_copy_{platform}.md（存在才删），返回是否真的删了（幂等）。"""
    if path.is_file():
        path.unlink()
        return True
    return False


def _delete_stale_copies(batch_root: Path, date: str, slug: str) -> None:
    """按 _ACTIVE_PLATFORMS 逐平台删 {slug}_copy_{platform}.md（存在才删，幂等）。"""
    for platform in _ACTIVE_PLATFORMS:
        _delete_copy_if_exists(batch_root / date / f"{slug}_copy_{platform}.md")


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


def handle_selection(batch_root: Path, query: dict[str, str] | None) -> tuple[int, dict[str, Any]]:
    """读某日期已落盘的 selection.json（经 D4 迁移），供前端刷新后恢复选中态与视图。

    尚未选片是正常状态：返回 200 + ``selection: null``，而不是 404（前端据此留在选片视图）。
    这是修 refresh desync 的服务端支点——磁盘 selection 是刷新后恢复的唯一事实来源。
    """
    query = query or {}
    date = query.get("date")
    if not date:
        return 400, {"error": "missing required query param 'date'"}
    selection = read_selection(batch_root, date)
    return 200, {"selection": selection}


def handle_select(batch_root: Path, body: dict[str, Any] | None) -> tuple[int, dict[str, Any]]:
    body = body or {}
    date = body.get("date")
    news_slug = body.get("news_slug")
    tmdb_id = body.get("tmdb_id")
    title = body.get("title")
    if not date or not news_slug or tmdb_id is None:
        return 400, {"ok": False, "error": "missing required fields: date/news_slug/tmdb_id"}

    # G8 修复（变体 A）：改选时清掉上一次选片遗留的 {slug}_copy.md，恢复
    # 「selection.copy_path=null ⇔ 磁盘无对应 _copy.md」不变量。否则改选后新 selection
    # 被重置为 published:false / copy_path:null，但旧稿仍在盘上，导致陈旧稿（如 Rule
    # Breakers）与新选片（如 The Girl）对不上。删两处（存在才删，幂等）：
    #   ① 上一份 selection 指向的旧 slug 稿——可能是别的新闻，否则会变成孤儿稿；
    #   ② 本次 slug 稿——重复选同片时强制重新 publish（稿可再生，安全）。
    prev = read_selection(batch_root, date)
    if prev:
        prev_slug = (prev.get("selected") or {}).get("news_slug")
        if prev_slug:
            _delete_stale_copies(batch_root, date, prev_slug)
    _delete_stale_copies(batch_root, date, news_slug)

    payload = {
        "date": date,
        "selected": {"news_slug": news_slug, "tmdb_id": tmdb_id, "title": title},
        "selected_at": datetime.now(UTC).isoformat(),
        # D4：改选即清空所有平台的发布状态——新选片尚未对任何平台出稿。
        "copies": {},
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
    # 本期唯一实装平台；body 未传时默认 xiaohongshu，为未来平台留 body 覆盖口。
    platform = body.get("platform") or "xiaohongshu"
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
            "--platform",
            platform,
        ],
        capture_output=True,
        text=True,
    )

    if result.returncode == 0:
        # 优先信 adapter 自己汇报的 "Wrote <path>"（stderr），推导路径只作兜底，
        # 避免两处拼路径规则长期漂移不一致。
        copy_path = _parse_wrote_path(result.stderr) or str(
            batch_root / date / f"{news_slug}_copy_{platform}.md"
        )
        # D4：只更新本平台的 copies 条目，保留可能已存在的 humanized_path（9.7.4
        # 才会真正写入非 None 值，这里先占位保留字段结构）。
        existing_entry = selection.get("copies", {}).get(platform) or {}
        selection.setdefault("copies", {})[platform] = {
            "published": True,
            "copy_path": copy_path,
            "humanized_path": existing_entry.get("humanized_path"),
        }
        write_selection(batch_root, date, selection)
        return 200, {"ok": True, "copy_path": copy_path, "stderr": result.stderr}

    return 500, {"ok": False, "copy_path": None, "stderr": result.stderr}


def handle_rewrite(
    batch_root: Path,
    body: dict[str, Any] | None,
    *,
    rewrite_adapter_path: Path,
    run_subprocess: Any = subprocess.run,
) -> tuple[int, dict[str, Any]]:
    """D5：subprocess 调 rewrite_adapter.py，落 humanized 稿 + 更新 selection.json。

    slug 未传时从 selection.json 的 selected.news_slug 兜底（读 selection 已经过 D4
    迁移，只会看到 copies dict 形状）；platform 未传默认 xiaohongshu（当前唯一实装平台）。
    """
    body = body or {}
    date = body.get("date")
    platform = body.get("platform") or "xiaohongshu"
    if not date:
        return 400, {
            "ok": False,
            "humanized_path": None,
            "stderr": "missing required field: date",
        }

    slug = body.get("slug")
    selection: dict[str, Any] | None = None
    if not slug:
        selection = read_selection(batch_root, date)
        if selection is None:
            return 400, {
                "ok": False,
                "humanized_path": None,
                "stderr": f"no selection.json for date {date!r}; call /api/select first",
            }
        slug = (selection.get("selected") or {}).get("news_slug")
        if not slug:
            return 400, {
                "ok": False,
                "humanized_path": None,
                "stderr": "selection.json missing news_slug",
            }

    result = run_subprocess(
        [
            sys.executable,
            str(rewrite_adapter_path),
            "--date",
            date,
            "--slug",
            str(slug),
            "--platform",
            platform,
        ],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        return 500, {"ok": False, "humanized_path": None, "stderr": result.stderr}

    humanized_path_str = _parse_wrote_path(result.stderr) or str(
        batch_root / date / f"{slug}_copy_{platform}_humanized.md"
    )
    humanized_path = Path(humanized_path_str)
    humanized_body: str | None = None
    if humanized_path.is_file():
        humanized_body = parse_copy_markdown(
            humanized_path.read_text(encoding="utf-8")
        )["body"]

    # 读 selection（若上面因 slug 已传而未读过）以保留 published/copy_path，
    # 只更新本平台的 humanized_path 字段。
    if selection is None:
        selection = read_selection(batch_root, date)
    if selection is not None:
        existing_entry = selection.get("copies", {}).get(platform) or {}
        selection.setdefault("copies", {})[platform] = {
            "published": existing_entry.get("published", False),
            "copy_path": existing_entry.get("copy_path"),
            "humanized_path": humanized_path_str,
        }
        write_selection(batch_root, date, selection)

    return 200, {
        "ok": True,
        "humanized_path": humanized_path_str,
        "humanized_body": humanized_body,
        "stderr": result.stderr,
    }


def handle_regenerate(
    batch_root: Path,
    body: dict[str, Any] | None,
    *,
    regenerate_adapter_path: Path,
    run_subprocess: Any = subprocess.run,
) -> tuple[int, dict[str, Any]]:
    """9.8.4：subprocess 调 regenerate_adapter.py 覆盖重生成 headline 或 body。

    tmdb_id 面板不会随请求传来（面板只知道 date/slug/platform/target），必须从
    selection.json 兜底读出——这是 regenerate_adapter 定位 candidate 的唯一途径。
    body 目标成功后 adapter 已自行删掉 humanized 文件，这里只需同步清空
    selection.json 里的 humanized_path 字段，让磁盘与元数据保持一致。
    """
    body = body or {}
    date = body.get("date")
    platform = body.get("platform") or "xiaohongshu"
    target = body.get("target")

    if not date:
        return 400, {
            "ok": False,
            "headline": None,
            "body": None,
            "stderr": "missing required field: date",
        }
    if target not in ("headline", "body"):
        return 400, {
            "ok": False,
            "headline": None,
            "body": None,
            "stderr": "target must be 'headline' or 'body'",
        }

    slug = body.get("slug")
    selection = read_selection(batch_root, date)
    if not slug:
        if selection is None:
            return 400, {
                "ok": False,
                "headline": None,
                "body": None,
                "stderr": f"no selection.json for date {date!r}; call /api/select first",
            }
        slug = (selection.get("selected") or {}).get("news_slug")
        if not slug:
            return 400, {
                "ok": False,
                "headline": None,
                "body": None,
                "stderr": "selection.json missing news_slug",
            }

    if selection is None:
        return 400, {
            "ok": False,
            "headline": None,
            "body": None,
            "stderr": f"no selection.json for date {date!r}; call /api/select first",
        }
    tmdb_id = (selection.get("selected") or {}).get("tmdb_id")
    if tmdb_id is None:
        return 400, {
            "ok": False,
            "headline": None,
            "body": None,
            "stderr": "selection.json missing tmdb_id",
        }

    result = run_subprocess(
        [
            sys.executable,
            str(regenerate_adapter_path),
            "--date",
            date,
            "--slug",
            str(slug),
            "--tmdb-id",
            str(tmdb_id),
            "--platform",
            platform,
            "--target",
            target,
        ],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        return 500, {"ok": False, "headline": None, "body": None, "stderr": result.stderr}

    copy_path_str = _parse_wrote_path(result.stderr) or str(
        batch_root / date / f"{slug}_copy_{platform}.md"
    )
    copy_path = Path(copy_path_str)
    parsed = parse_copy_markdown(copy_path.read_text(encoding="utf-8"))

    if target == "body":
        # regenerate_adapter 已自行删掉 humanized 文件（D4），这里只需把
        # selection.json 的 humanized_path 同步清空，保留 published/copy_path。
        selection = read_selection(batch_root, date) or selection
        existing_entry = selection.get("copies", {}).get(platform) or {}
        selection.setdefault("copies", {})[platform] = {
            "published": existing_entry.get("published", False),
            "copy_path": existing_entry.get("copy_path"),
            "humanized_path": None,
        }
        write_selection(batch_root, date, selection)

    return 200, {
        "ok": True,
        "target": target,
        "headline": parsed["headline"],
        "body": parsed["body"],
        "copy_path": copy_path_str,
        "stderr": result.stderr,
    }


def handle_edit_body(batch_root: Path, body: dict[str, Any] | None) -> tuple[int, dict[str, Any]]:
    """9.8.4：/api/edit-body 无 LLM，纯 in-serve 文本拼接直改 body。

    与 handle_regenerate 的 body 分支一样要失效 humanized（D4），但这里没有
    adapter 子进程替我们删文件，需自己调 _delete_copy_if_exists。
    """
    body = body or {}
    date = body.get("date")
    platform = body.get("platform") or "xiaohongshu"
    new_body = body.get("body")

    if not date:
        return 400, {"ok": False, "error": "missing required field: date"}
    if new_body is None or str(new_body).strip() == "":
        return 400, {"ok": False, "error": "missing or empty body"}

    slug = body.get("slug")
    selection: dict[str, Any] | None = None
    if not slug:
        selection = read_selection(batch_root, date)
        if selection is None:
            return 400, {
                "ok": False,
                "error": f"no selection.json for date {date!r}; call /api/select first",
            }
        slug = (selection.get("selected") or {}).get("news_slug")
        if not slug:
            return 400, {"ok": False, "error": "selection.json missing news_slug"}

    copy_path = batch_root / date / f"{slug}_copy_{platform}.md"
    if not copy_path.is_file():
        return 404, {"ok": False, "error": f"copy not found: {copy_path}"}

    text = copy_path.read_text(encoding="utf-8")
    new_text = replace_body_in_copy_markdown(text, str(new_body))
    copy_path.write_text(new_text, encoding="utf-8")

    _delete_copy_if_exists(batch_root / date / f"{slug}_copy_{platform}_humanized.md")
    if selection is None:
        selection = read_selection(batch_root, date)
    if selection is not None and platform in selection.get("copies", {}):
        existing_entry = selection["copies"][platform]
        selection["copies"][platform] = {
            "published": existing_entry.get("published", False),
            "copy_path": existing_entry.get("copy_path"),
            "humanized_path": None,
        }
        write_selection(batch_root, date, selection)

    parsed = parse_copy_markdown(new_text)
    return 200, {
        "ok": True,
        "headline": parsed["headline"],
        "body": parsed["body"],
        "platform": platform,
    }


def parse_copy_markdown(text: str) -> dict[str, str]:
    """纯函数：解析 ``{slug}_copy_{platform}.md`` 的固定 D1 排版，抽出 headline/body。

    规则（对齐 publish_adapter.render_copy_markdown 的输出形状）：
    - 跳过开头的 ``# 发布定稿...`` H1 标题行（及其前的空行）；
    - H1 之后第一个非空行即 headline；
    - body 是 headline 之后、直到（不含）``## 链接`` 分区之前的所有内容，整体 strip；
    - 缺 H1 / 缺 headline / 缺链接分区都不报错，容错返回空串——供 handle_copy 对已知产出
      文件解析，也允许直接单测喂任意残缺文本。
    """
    lines = text.splitlines()
    n = len(lines)
    idx = 0

    while idx < n and not lines[idx].strip():
        idx += 1
    if idx < n and lines[idx].strip().startswith("# "):
        idx += 1

    while idx < n and not lines[idx].strip():
        idx += 1

    headline = lines[idx].strip() if idx < n else ""
    if idx < n:
        idx += 1

    body_lines: list[str] = []
    for line in lines[idx:]:
        if line.strip() == "## 链接":
            break
        body_lines.append(line)
    body = "\n".join(body_lines).strip()

    return {"headline": headline, "body": body}


def replace_body_in_copy_markdown(text: str, new_body: str) -> str:
    """纯函数：原地替换 body，逐字保留 header/headline/``## 链接`` 分区。

    存在的意义：/api/edit-body 是无 LLM 的直改，若复用 publish_adapter 的
    render_copy_markdown 重新拼装整份文件，就得 import compose 相关重模块，
    违反 serve.py「薄传输层」的耦合边界；同时逐字保留（而非重新渲染）headline
    与链接分区，天然满足「headline/链接不变」的验收标准，不必额外断言。
    """
    lines = text.splitlines()
    n = len(lines)
    idx = 0

    while idx < n and not lines[idx].strip():
        idx += 1
    if idx < n and lines[idx].strip().startswith("# "):
        idx += 1
    while idx < n and not lines[idx].strip():
        idx += 1

    headline_idx = idx
    links_idx: int | None = None
    for j in range(idx, n):
        if lines[j].strip() == "## 链接":
            links_idx = j
            break

    prefix_lines = lines[: headline_idx + 1]
    parts = ["\n".join(prefix_lines), "", new_body.strip()]
    if links_idx is not None:
        links_block = "\n".join(lines[links_idx:]).rstrip("\n")
        parts += ["", links_block]

    return "\n".join(parts).rstrip("\n") + "\n"


def handle_copy(batch_root: Path, query: dict[str, str] | None) -> tuple[int, dict[str, Any]]:
    """读 ``{slug}_copy_{platform}.md``（D6）：面板定稿展示区的数据源。

    humanized 文件的解析是 9.7.4 的前瞻只读兼容：本 TODO 不产出/不写它，只在它已存在时
    （未来 9.7.4 落地后）顺带解析出 humanized_body，避免 9.7.4 还要再改这个 handler。
    """
    query = query or {}
    date = query.get("date")
    slug = query.get("slug")
    platform = query.get("platform") or "xiaohongshu"
    if not date or not slug:
        return 400, {"error": "missing required query params: date/slug"}

    copy_path = batch_root / date / f"{slug}_copy_{platform}.md"
    if not copy_path.is_file():
        return 404, {"error": f"copy not found: {copy_path}"}

    parsed = parse_copy_markdown(copy_path.read_text(encoding="utf-8"))

    humanized_path = batch_root / date / f"{slug}_copy_{platform}_humanized.md"
    has_humanized = humanized_path.is_file()
    humanized_body: str | None = None
    if has_humanized:
        humanized_body = parse_copy_markdown(
            humanized_path.read_text(encoding="utf-8")
        )["body"]

    return 200, {
        "headline": parsed["headline"],
        "body": parsed["body"],
        "humanized_body": humanized_body,
        "has_humanized": has_humanized,
        "platform": platform,
    }


def route(
    method: str,
    path: str,
    query: dict[str, str] | None,
    body: dict[str, Any] | None,
    *,
    batch_root: Path,
    index_html_path: Path | None = None,
    publish_adapter_path: Path | None = None,
    rewrite_adapter_path: Path | None = None,
    regenerate_adapter_path: Path | None = None,
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
    if method == "GET" and path == "/api/copy":
        return handle_copy(batch_root, query)
    if method == "GET" and path == "/api/selection":
        return handle_selection(batch_root, query)
    if method == "POST" and path == "/api/select":
        return handle_select(batch_root, body)
    if method == "POST" and path == "/api/publish":
        return handle_publish(
            batch_root,
            body,
            publish_adapter_path=publish_adapter_path or _default_publish_adapter_path(),
            run_subprocess=run_subprocess,
        )
    if method == "POST" and path == "/api/rewrite":
        return handle_rewrite(
            batch_root,
            body,
            rewrite_adapter_path=rewrite_adapter_path or _default_rewrite_adapter_path(),
            run_subprocess=run_subprocess,
        )
    if method == "POST" and path == "/api/regenerate":
        return handle_regenerate(
            batch_root,
            body,
            regenerate_adapter_path=regenerate_adapter_path or _default_regenerate_adapter_path(),
            run_subprocess=run_subprocess,
        )
    if method == "POST" and path == "/api/edit-body":
        return handle_edit_body(batch_root, body)
    return 404, {"error": f"not found: {method} {path}"}


# ---------------------------------------------------------------------------
# HTTP 传输层（薄胶水：解析请求 → route() → 序列化响应）
# ---------------------------------------------------------------------------


def make_handler_class(
    *,
    batch_root: Path,
    index_html_path: Path,
    publish_adapter_path: Path,
    rewrite_adapter_path: Path,
    regenerate_adapter_path: Path,
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
                rewrite_adapter_path=rewrite_adapter_path,
                regenerate_adapter_path=regenerate_adapter_path,
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
    rewrite_adapter_path: Path | None = None,
    regenerate_adapter_path: Path | None = None,
) -> ThreadingHTTPServer:
    """构建并返回一个已 bind 但尚未 serve_forever 的服务器实例（便于测试注入）。"""
    root = batch_root or _default_batch_root()
    handler_cls = make_handler_class(
        batch_root=root,
        index_html_path=index_html_path or _default_index_html_path(),
        publish_adapter_path=publish_adapter_path or _default_publish_adapter_path(),
        rewrite_adapter_path=rewrite_adapter_path or _default_rewrite_adapter_path(),
        regenerate_adapter_path=regenerate_adapter_path or _default_regenerate_adapter_path(),
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