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
import shutil
import subprocess
import sys
from dataclasses import dataclass
from datetime import UTC, datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlsplit

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from review_panel.build_data import build_panel_data, list_available_dates  # noqa: E402
from review_panel.job_store import JobStore, job_store as _DEFAULT_JOB_STORE  # noqa: E402
from review_panel.publication_bundle import manifest_path, read_manifest  # noqa: E402
from scripts.lib.paths import repo_root  # noqa: E402

# 子进程调 publish_adapter.py 时用 stderr 里这一行定位「Wrote <path>」的产出路径，
# 比自己拼 {slug}_copy_{platform}.md 更可靠：adapter 内部用的是 news_dir.parent 拼路径，
# 这里直接信它自己汇报的路径，避免两处拼路径逻辑长期漂移不一致。
_WROTE_LINE_RE = re.compile(r"^Wrote (.+)$", re.MULTILINE)

# 当前已实现的发布平台清单（D3）。新增平台时只需在此追加一项，改选时的陈旧稿清理、
# selection.json 的 copies dict 初始化等下游逻辑无需改动即可覆盖新平台。
_ACTIVE_PLATFORMS: tuple[str, ...] = ("xiaohongshu",)

# Phase 10.4：复数视角合并上限（ADR-0017 D5）。serve 只对「>2」这一显式客户端错误做快速
# 4xx 兜底；「恰好 2」的业务硬约束单一收敛在 drafts_adapter.run_combine，不在 serve 复刻。
_MAX_COMBINE = 2


@dataclass(frozen=True)
class PublicationAssetResponse:
    """An already-authorized bundle file for the HTTP transport layer to stream."""

    path: Path
    content_type: str


# 派生当前稿「# 发布定稿 · {date} · {label}」标题的平台中文名，与
# publish_adapter._PLATFORM_LABELS 保持一致（select-draft 本地渲染需逐字对齐 publish 产出）。
_PLATFORM_LABELS: dict[str, str] = {
    "xiaohongshu": "小红书",
    "x": "X (Twitter)",
    "reddit": "Reddit",
}


def _default_batch_root() -> Path:
    return repo_root() / "output" / "daily_batch"


def _default_publish_adapter_path() -> Path:
    return Path(__file__).resolve().parent / "publish_adapter.py"


def _default_rewrite_adapter_path() -> Path:
    return Path(__file__).resolve().parent / "rewrite_adapter.py"


def _default_regenerate_adapter_path() -> Path:
    return Path(__file__).resolve().parent / "regenerate_adapter.py"


def _default_drafts_adapter_path() -> Path:
    return Path(__file__).resolve().parent / "drafts_adapter.py"


def _default_publication_adapter_path() -> Path:
    return Path(__file__).resolve().parent / "publication_adapter.py"


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
# Phase 10.4 · 草稿池只读来源层（ADR-0017 D3/D4）：读池 + 派生当前稿的纯胶水
# ---------------------------------------------------------------------------


def _drafts_pool_path(batch_root: Path, date: str, slug: str, platform: str) -> Path:
    """草稿池文件：与 drafts_adapter._drafts_path 同一命名（{slug}_drafts_{platform}.json）。"""
    return batch_root / date / f"{slug}_drafts_{platform}.json"


def _read_drafts_pool(path: Path) -> list[dict[str, Any]]:
    """读只读草稿池；不存在或非数组 → 空列表（前端据此显示「尚未生成草稿池」）。"""
    if not path.is_file():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    return data if isinstance(data, list) else []


def _load_copy_links(batch_root: Path, date: str, slug: str, tmdb_id: int | str) -> dict[str, str]:
    """从 daily_batch 产物取派生当前稿所需的链接（movie_url / news_url）。

    select-draft 无 LLM、serve 直接读池写稿，但草稿池只存 {draft_id, headline, body}，
    不含链接；渲染当前稿的「## 链接」分区需要 movie_url（retrieve.json 按 tmdb_id 定位候选）
    与 news_url（news.json）。这里直接读 JSON，不 import publish_adapter（那会经 scripts.compose
    拖入检索/persona 重依赖，违反 serve.py 薄传输层耦合边界）——与本文件自带 parse/replace
    纯函数同因。文件缺失或字段缺失都容错返回空串（渲染层用「（无）」占位，不崩溃）。
    """
    news_dir = batch_root / date / slug
    movie_url = ""
    news_url = ""
    news_path = news_dir / "news.json"
    if news_path.is_file():
        try:
            news_url = str((json.loads(news_path.read_text(encoding="utf-8")) or {}).get("url") or "")
        except (json.JSONDecodeError, OSError):
            news_url = ""
    retrieve_path = news_dir / "retrieve.json"
    if retrieve_path.is_file():
        try:
            retrieve = json.loads(retrieve_path.read_text(encoding="utf-8")) or {}
            target = str(tmdb_id)
            for cand in retrieve.get("candidates") or []:
                if isinstance(cand, dict) and str(cand.get("tmdb_id")) == target:
                    movie_url = str(cand.get("movie_url") or "")
                    break
        except (json.JSONDecodeError, OSError):
            movie_url = ""
    return {"movie_url": movie_url, "news_url": news_url}


def render_copy_markdown_from_draft(
    date: str,
    draft: dict[str, Any],
    links: dict[str, str],
    *,
    platform: str = "xiaohongshu",
) -> str:
    """本地渲染派生当前稿，逐字对齐 publish_adapter.render_copy_markdown 的产出形状。

    存在的意义与 parse/replace 纯函数同：select-draft 无 LLM、须避免 import
    publish_adapter（经 scripts.compose 拖入重依赖）；故自带一份风格等价的轻量渲染。
    产物排版必须与 publish 产出一致，才能被既有 parse_copy_markdown / /api/copy 无差别消费。
    """
    headline = str(draft.get("headline") or "").strip()
    body = str(draft.get("body") or "").strip()
    movie_url = str(links.get("movie_url") or "")
    news_url = str(links.get("news_url") or "")
    platform_label = _PLATFORM_LABELS.get(platform, platform)
    lines = [
        f"# 发布定稿 · {date} · {platform_label}",
        "",
        headline or "（无标题）",
        "",
        body or "（无正文）",
        "",
        "## 链接",
        "",
        f"- 电影: {movie_url or '（无）'}",
        f"- 新闻: {news_url or '（无）'}",
        "",
    ]
    return "\n".join(lines)


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


def _resolve_selected(
    batch_root: Path, date: str, body: dict[str, Any]
) -> tuple[str | None, Any, dict[str, Any] | None]:
    """从 body 或 selection.json 兜底解出 (slug, tmdb_id, selection)。

    面板通常只传 date/platform，slug/tmdb_id 从 selection.json 的 selected 兜底——
    这是三个新端点共用的定位逻辑（同 handle_regenerate 的兜底口径）。返回的 selection
    已过 D4 迁移；任一缺失由各 handler 自行按其响应形状报 4xx。
    """
    slug = body.get("slug") or body.get("news_slug")
    tmdb_id = body.get("tmdb_id")
    selection = read_selection(batch_root, date)
    if selection is not None:
        selected = selection.get("selected") or {}
        if not slug:
            slug = selected.get("news_slug")
        if tmdb_id is None:
            tmdb_id = selected.get("tmdb_id")
    return slug, tmdb_id, selection


def handle_generate_drafts(
    batch_root: Path,
    body: dict[str, Any] | None,
    *,
    drafts_adapter_path: Path,
    run_subprocess: Any = subprocess.run,
) -> tuple[int, dict[str, Any]]:
    """POST /api/generate-drafts（ADR-0017 D3）：subprocess 调 drafts_adapter 全量扇出。

    slug/tmdb_id 从 selection.json 兜底（drafts_adapter 定位 candidate.triggered_by 的唯一
    途径）；成功后读回只读草稿池数组一并返回。本端点不动 selection.json——「产池」与「选中」
    分离，选中是 /api/select-draft 的职责。
    """
    body = body or {}
    date = body.get("date")
    platform = body.get("platform") or "xiaohongshu"
    if not date:
        return 400, {"ok": False, "drafts": [], "stderr": "missing required field: date"}

    slug, tmdb_id, selection = _resolve_selected(batch_root, date, body)
    if selection is None and not (slug and tmdb_id is not None):
        return 400, {
            "ok": False,
            "drafts": [],
            "stderr": f"no selection.json for date {date!r}; call /api/select first",
        }
    if not slug or tmdb_id is None:
        return 400, {"ok": False, "drafts": [], "stderr": "selection.json missing news_slug/tmdb_id"}

    result = run_subprocess(
        [
            sys.executable,
            str(drafts_adapter_path),
            "--date",
            date,
            "--news-slug",
            str(slug),
            "--tmdb-id",
            str(tmdb_id),
            "--platform",
            platform,
        ],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        return 500, {"ok": False, "drafts": [], "stderr": result.stderr}

    pool_path_str = _parse_wrote_path(result.stderr) or str(
        _drafts_pool_path(batch_root, date, slug, platform)
    )
    drafts = _read_drafts_pool(Path(pool_path_str))
    return 200, {
        "ok": True,
        "drafts_path": pool_path_str,
        "drafts": drafts,
        "platform": platform,
        "stderr": result.stderr,
    }


def handle_select_draft(batch_root: Path, body: dict[str, Any] | None) -> tuple[int, dict[str, Any]]:
    """POST /api/select-draft（ADR-0017 D4）：可变指针派生当前稿，无 LLM。

    读 {slug}_drafts_{platform}.json 取指定 draft_id → 本地渲染派生 {slug}_copy_{platform}.md →
    失效 humanized（删 _humanized.md + 清 humanized_path，body 变即旧去AI化稿过期，复用 9.8 D4
    不变量）→ 写 selected_draft_id（可变指针）。「选中」不消费/删除任何草稿——池永远只读。
    """
    body = body or {}
    date = body.get("date")
    platform = body.get("platform") or "xiaohongshu"
    draft_id = body.get("draft_id")
    if not date:
        return 400, {"ok": False, "error": "missing required field: date"}
    if not draft_id:
        return 400, {"ok": False, "error": "missing required field: draft_id"}

    slug, tmdb_id, selection = _resolve_selected(batch_root, date, body)
    if not slug:
        return 400, {"ok": False, "error": f"no news_slug for date {date!r}; call /api/select first"}
    if tmdb_id is None:
        return 400, {"ok": False, "error": "selection.json missing tmdb_id"}

    pool_path = _drafts_pool_path(batch_root, date, slug, platform)
    pool = _read_drafts_pool(pool_path)
    if not pool:
        return 404, {"ok": False, "error": f"draft pool not found: {pool_path}"}
    match = next((d for d in pool if isinstance(d, dict) and str(d.get("draft_id")) == str(draft_id)), None)
    if match is None:
        available = ", ".join(str(d.get("draft_id")) for d in pool if isinstance(d, dict))
        return 400, {"ok": False, "error": f"draft_id {draft_id!r} not in pool; available: {available or '（空池）'}"}

    links = _load_copy_links(batch_root, date, slug, tmdb_id)
    copy_path = batch_root / date / f"{slug}_copy_{platform}.md"
    new_text = render_copy_markdown_from_draft(date, match, links, platform=platform)
    copy_path.parent.mkdir(parents=True, exist_ok=True)
    copy_path.write_text(new_text, encoding="utf-8")

    _delete_copy_if_exists(batch_root / date / f"{slug}_copy_{platform}_humanized.md")

    if selection is not None:
        existing_entry = selection.get("copies", {}).get(platform) or {}
        selection.setdefault("copies", {})[platform] = {
            "published": True,
            "copy_path": str(copy_path),
            "humanized_path": None,
            "selected_draft_id": str(draft_id),
        }
        write_selection(batch_root, date, selection)

    parsed = parse_copy_markdown(new_text)
    return 200, {
        "ok": True,
        "headline": parsed["headline"],
        "body": parsed["body"],
        "copy_path": str(copy_path),
        "selected_draft_id": str(draft_id),
        "platform": platform,
    }


def handle_combine_drafts(
    batch_root: Path,
    body: dict[str, Any] | None,
    *,
    drafts_adapter_path: Path,
    run_subprocess: Any = subprocess.run,
) -> tuple[int, dict[str, Any]]:
    """POST /api/combine-drafts（ADR-0017 D5）：subprocess `--combine` 合并 ≤2 草稿 append 进池。

    serve **恒调单版**（不传 --combine-mode，由 adapter 默认的生产路线决定）；A/B 双版对照
    是开发期 CLI 的事，面板永不产双版。成功后读回池一并返回，但**不自动切指针**——切主视角
    仍需前端显式再调 /api/select-draft。>2 目标由 serve 直接 4xx 拦掉（恰好 2 由 adapter 兜底）。
    """
    body = body or {}
    date = body.get("date")
    platform = body.get("platform") or "xiaohongshu"
    draft_ids = body.get("draft_ids")
    if not date:
        return 400, {"ok": False, "drafts": [], "stderr": "missing required field: date"}
    if not isinstance(draft_ids, list) or not all(isinstance(i, str) for i in draft_ids):
        return 400, {"ok": False, "drafts": [], "stderr": "draft_ids must be a list of strings"}
    ids = [i.strip() for i in draft_ids if i and i.strip()]
    if len(ids) > _MAX_COMBINE:
        return 400, {"ok": False, "drafts": [], "stderr": f"combine accepts at most {_MAX_COMBINE} draft_ids, got {len(ids)}"}

    slug, tmdb_id, selection = _resolve_selected(batch_root, date, body)
    if selection is None and not (slug and tmdb_id is not None):
        return 400, {
            "ok": False,
            "drafts": [],
            "stderr": f"no selection.json for date {date!r}; call /api/select first",
        }
    if not slug or tmdb_id is None:
        return 400, {"ok": False, "drafts": [], "stderr": "selection.json missing news_slug/tmdb_id"}

    result = run_subprocess(
        [
            sys.executable,
            str(drafts_adapter_path),
            "--date",
            date,
            "--news-slug",
            str(slug),
            "--tmdb-id",
            str(tmdb_id),
            "--platform",
            platform,
            "--combine",
            ",".join(ids),
        ],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        return 500, {"ok": False, "drafts": [], "stderr": result.stderr}

    pool_path_str = _parse_wrote_path(result.stderr) or str(
        _drafts_pool_path(batch_root, date, slug, platform)
    )
    drafts = _read_drafts_pool(Path(pool_path_str))
    return 200, {
        "ok": True,
        "drafts_path": pool_path_str,
        "drafts": drafts,
        "platform": platform,
        "stderr": result.stderr,
    }


def handle_retry_draft(
    batch_root: Path,
    body: dict[str, Any] | None,
    *,
    drafts_adapter_path: Path,
    run_subprocess: Any = subprocess.run,
) -> tuple[int, dict[str, Any]]:
    """POST /api/retry-draft（Phase 12.5）：subprocess 调 drafts_adapter ``--retry`` 单份重掷。

    编辑在面板对某挂 warnings 的草稿点「重试」→ 本端点带 ``--judge`` 只重掷那一条
    （in-place 换池内那条，其它草稿零改动）。slug/tmdb_id 从 selection.json 兜底，与
    /api/generate-drafts 同源。成功后读回整份池返回，供前端刷新徽标与预览。本端点不动
    selection.json——「重掷来源池」与「选中」分离。
    """
    body = body or {}
    date = body.get("date")
    platform = body.get("platform") or "xiaohongshu"
    draft_id = body.get("draft_id")
    if not date:
        return 400, {"ok": False, "drafts": [], "stderr": "missing required field: date"}
    if not draft_id or not str(draft_id).strip():
        return 400, {"ok": False, "drafts": [], "stderr": "missing required field: draft_id"}

    slug, tmdb_id, selection = _resolve_selected(batch_root, date, body)
    if selection is None and not (slug and tmdb_id is not None):
        return 400, {
            "ok": False,
            "drafts": [],
            "stderr": f"no selection.json for date {date!r}; call /api/select first",
        }
    if not slug or tmdb_id is None:
        return 400, {"ok": False, "drafts": [], "stderr": "selection.json missing news_slug/tmdb_id"}

    result = run_subprocess(
        [
            sys.executable,
            str(drafts_adapter_path),
            "--date",
            date,
            "--news-slug",
            str(slug),
            "--tmdb-id",
            str(tmdb_id),
            "--platform",
            platform,
            "--retry",
            str(draft_id),
            "--judge",
        ],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        return 500, {"ok": False, "drafts": [], "stderr": result.stderr}

    pool_path_str = _parse_wrote_path(result.stderr) or str(
        _drafts_pool_path(batch_root, date, slug, platform)
    )
    drafts = _read_drafts_pool(Path(pool_path_str))
    return 200, {
        "ok": True,
        "drafts_path": pool_path_str,
        "drafts": drafts,
        "platform": platform,
        "stderr": result.stderr,
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


def handle_drafts(batch_root: Path, query: dict[str, str] | None) -> tuple[int, dict[str, Any]]:
    """GET /api/drafts：把只读草稿池读回前端，供刷新后恢复 pick（选型）阶段。

    pick 升格为可刷新恢复的真实阶段后，前端需要一个事实来源重建 persona tab 行；但草稿池
    只落盘、不驻留 serve 内存（process 内存里没有池），刷新后前端据 selection.selected.news_slug
    调本端点把池读回。「还没产池」是正常态：返回 200 + ``drafts: []``（前端据此留在选片视图），
    与 handle_selection 的 ``selection: null`` 同风格，而非 404——刷新恢复不应把「未产池」当错误。
    """
    query = query or {}
    date = query.get("date")
    slug = query.get("slug")
    platform = query.get("platform") or "xiaohongshu"
    if not date or not slug:
        return 400, {"error": "missing required query params: date/slug"}
    pool_path = _drafts_pool_path(batch_root, date, slug, platform)
    drafts = _read_drafts_pool(pool_path)
    return 200, {"drafts": drafts, "drafts_path": str(pool_path), "platform": platform}


def _publication_manifest_for_date(batch_root: Path, date: str) -> tuple[Path, dict[str, Any]]:
    """Resolve the selected movie's manifest through the bundle domain boundary."""
    selection = read_selection(batch_root, date)
    if selection is None:
        raise ValueError(f"no selection.json for date {date!r}; call /api/select first")
    selected = selection.get("selected") or {}
    tmdb_id = selected.get("tmdb_id")
    title = selected.get("title")
    if tmdb_id is None or not title:
        raise ValueError("selection.json missing tmdb_id/title")
    path = manifest_path(batch_root, date, tmdb_id, str(title))
    return path, dict(read_manifest(path))


def handle_publication(batch_root: Path, query: dict[str, str] | None) -> tuple[int, dict[str, Any]]:
    query = query or {}
    date = query.get("date")
    if not date:
        return 400, {"error": "missing required query param 'date'"}
    try:
        _, manifest = _publication_manifest_for_date(batch_root, date)
    except ValueError as exc:
        return 404, {"error": str(exc)}
    return 200, {"manifest": manifest}


def handle_prepare_publication(
    batch_root: Path,
    body: dict[str, Any] | None,
    *,
    publication_adapter_path: Path,
    run_subprocess: Any = subprocess.run,
) -> tuple[int, dict[str, Any]]:
    body = body or {}
    date = body.get("date")
    if not date:
        return 400, {"ok": False, "stderr": "missing required field: date"}
    if read_selection(batch_root, str(date)) is None:
        return 400, {
            "ok": False,
            "stderr": f"no selection.json for date {date!r}; call /api/select first",
        }

    result = run_subprocess(
        [
            sys.executable,
            str(publication_adapter_path),
            "--date",
            str(date),
            "--batch-root",
            str(batch_root),
        ],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return 500, {"ok": False, "stderr": result.stderr}
    return 200, {"ok": True, "stderr": result.stderr}


def handle_retry_publication_artifact(
    batch_root: Path,
    body: dict[str, Any] | None,
    *,
    publication_adapter_path: Path,
    run_subprocess: Any = subprocess.run,
) -> tuple[int, dict[str, Any]]:
    body = body or {}
    date = body.get("date")
    artifact = body.get("artifact")
    if not date or not artifact:
        return 400, {"ok": False, "stderr": "missing required fields: date/artifact"}
    if artifact not in {"drafts", "poster", "planet"}:
        return 400, {"ok": False, "stderr": f"unknown publication artifact: {artifact!r}"}
    if read_selection(batch_root, str(date)) is None:
        return 400, {
            "ok": False,
            "stderr": f"no selection.json for date {date!r}; call /api/select first",
        }

    result = run_subprocess(
        [
            sys.executable,
            str(publication_adapter_path),
            "--date",
            str(date),
            "--batch-root",
            str(batch_root),
            "--targets",
            str(artifact),
        ],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return 500, {"ok": False, "stderr": result.stderr}
    return 200, {"ok": True, "artifact": artifact, "stderr": result.stderr}


def handle_publication_asset(
    batch_root: Path, query: dict[str, str] | None
) -> tuple[int, dict[str, Any] | PublicationAssetResponse]:
    """Resolve only manifest-registered visual assets and reject raw file paths."""
    query = query or {}
    date = query.get("date")
    asset = query.get("asset")
    if not date or not asset:
        return 400, {"error": "missing required query params: date/asset"}
    if asset not in {"poster", "planet"}:
        return 400, {"error": f"unknown publication asset: {asset!r}"}
    try:
        manifest_file, manifest = _publication_manifest_for_date(batch_root, date)
    except ValueError as exc:
        return 404, {"error": str(exc)}

    artifact = (manifest.get("artifacts") or {}).get(asset)
    relative_path = artifact.get("path") if isinstance(artifact, dict) else None
    if not isinstance(relative_path, str):
        return 404, {"error": f"publication asset {asset!r} is not registered"}
    bundle_root = manifest_file.parent.resolve()
    candidate = (bundle_root / relative_path).resolve()
    try:
        candidate.relative_to(bundle_root)
    except ValueError:
        return 403, {"error": "publication asset path escapes its bundle"}
    if not candidate.is_file():
        return 404, {"error": f"publication asset {asset!r} is not ready"}
    content_type = "image/jpeg" if asset == "poster" else "image/png"
    return 200, PublicationAssetResponse(path=candidate, content_type=content_type)


def handle_job(job_store: JobStore, query: dict[str, str] | None) -> tuple[int, dict[str, Any]]:
    """GET /api/job（Phase 12.6.2 D4）：轮询后台 job 的四态。

    ``rec is None``（未知 job_id）→ 404；``running`` → 200 无 result；``done`` →
    200 + ``result: {http_status, payload}``（原 handle_* 的同步返回形状原样透出）；
    ``error``（work 抛异常）→ 200 + ``stderr``（traceback 文本，字段名对齐既有
    handle_* 失败时的 ``stderr`` 习惯，供前端复用同一套错误展示逻辑）。
    """
    query = query or {}
    job_id = query.get("job_id")
    rec = job_store.get(job_id) if job_id else None
    if rec is None:
        return 404, {"ok": False, "error": f"unknown job_id: {job_id}"}
    if rec.status == "running":
        return 200, {"ok": True, "status": "running"}
    if rec.status == "done":
        return 200, {
            "ok": True,
            "status": "done",
            "result": {"http_status": rec.http_status, "payload": rec.payload},
        }
    return 200, {"ok": True, "status": "error", "stderr": rec.error}


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
    drafts_adapter_path: Path | None = None,
    publication_adapter_path: Path | None = None,
    run_subprocess: Any = subprocess.run,
    job_store: JobStore = _DEFAULT_JOB_STORE,
) -> tuple[int, dict[str, Any] | str | PublicationAssetResponse]:
    """纯路由分发：无 socket 依赖，单测与真实服务器共用同一份逻辑。

    Phase 12.6.2：6 个长 LLM 任务端点（publish/rewrite/regenerate/generate-drafts/
    combine-drafts/retry-draft）不再同步阻塞到跑完，而是提交后台 job 立即返回 202；
    真正的结果需轮询 ``GET /api/job?job_id=...`` 取回（四态：unknown/running/done/error）。
    handle_* 函数本身零改动——它们返回的 ``(status, payload)`` 正是 job work 的返回形状。
    """
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
    if method == "GET" and path == "/api/drafts":
        return handle_drafts(batch_root, query)
    if method == "GET" and path == "/api/publication":
        return handle_publication(batch_root, query)
    if method == "GET" and path == "/api/publication-asset":
        return handle_publication_asset(batch_root, query)
    if method == "POST" and path == "/api/select":
        return handle_select(batch_root, body)
    if method == "GET" and path == "/api/job":
        return handle_job(job_store, query)
    if method == "POST" and path == "/api/prepare-publication":
        _publication_adapter_path = publication_adapter_path or _default_publication_adapter_path()
        job_id = job_store.submit(
            lambda: handle_prepare_publication(
                batch_root,
                body,
                publication_adapter_path=_publication_adapter_path,
                run_subprocess=run_subprocess,
            ),
            kind="prepare-publication",
        )
        return 202, {"ok": True, "job_id": job_id, "kind": "prepare-publication"}
    if method == "POST" and path == "/api/retry-publication-artifact":
        _publication_adapter_path = publication_adapter_path or _default_publication_adapter_path()
        job_id = job_store.submit(
            lambda: handle_retry_publication_artifact(
                batch_root,
                body,
                publication_adapter_path=_publication_adapter_path,
                run_subprocess=run_subprocess,
            ),
            kind="retry-publication-artifact",
        )
        return 202, {"ok": True, "job_id": job_id, "kind": "retry-publication-artifact"}
    if method == "POST" and path == "/api/publish":
        _publish_adapter_path = publish_adapter_path or _default_publish_adapter_path()
        job_id = job_store.submit(
            lambda: handle_publish(
                batch_root,
                body,
                publish_adapter_path=_publish_adapter_path,
                run_subprocess=run_subprocess,
            ),
            kind="publish",
        )
        return 202, {"ok": True, "job_id": job_id, "kind": "publish"}
    if method == "POST" and path == "/api/rewrite":
        _rewrite_adapter_path = rewrite_adapter_path or _default_rewrite_adapter_path()
        job_id = job_store.submit(
            lambda: handle_rewrite(
                batch_root,
                body,
                rewrite_adapter_path=_rewrite_adapter_path,
                run_subprocess=run_subprocess,
            ),
            kind="rewrite",
        )
        return 202, {"ok": True, "job_id": job_id, "kind": "rewrite"}
    if method == "POST" and path == "/api/regenerate":
        _regenerate_adapter_path = regenerate_adapter_path or _default_regenerate_adapter_path()
        job_id = job_store.submit(
            lambda: handle_regenerate(
                batch_root,
                body,
                regenerate_adapter_path=_regenerate_adapter_path,
                run_subprocess=run_subprocess,
            ),
            kind="regenerate",
        )
        return 202, {"ok": True, "job_id": job_id, "kind": "regenerate"}
    if method == "POST" and path == "/api/edit-body":
        return handle_edit_body(batch_root, body)
    if method == "POST" and path == "/api/generate-drafts":
        _drafts_adapter_path = drafts_adapter_path or _default_drafts_adapter_path()
        job_id = job_store.submit(
            lambda: handle_generate_drafts(
                batch_root,
                body,
                drafts_adapter_path=_drafts_adapter_path,
                run_subprocess=run_subprocess,
            ),
            kind="generate-drafts",
        )
        return 202, {"ok": True, "job_id": job_id, "kind": "generate-drafts"}
    if method == "POST" and path == "/api/select-draft":
        return handle_select_draft(batch_root, body)
    if method == "POST" and path == "/api/combine-drafts":
        _drafts_adapter_path = drafts_adapter_path or _default_drafts_adapter_path()
        job_id = job_store.submit(
            lambda: handle_combine_drafts(
                batch_root,
                body,
                drafts_adapter_path=_drafts_adapter_path,
                run_subprocess=run_subprocess,
            ),
            kind="combine-drafts",
        )
        return 202, {"ok": True, "job_id": job_id, "kind": "combine-drafts"}
    if method == "POST" and path == "/api/retry-draft":
        _drafts_adapter_path = drafts_adapter_path or _default_drafts_adapter_path()
        job_id = job_store.submit(
            lambda: handle_retry_draft(
                batch_root,
                body,
                drafts_adapter_path=_drafts_adapter_path,
                run_subprocess=run_subprocess,
            ),
            kind="retry-draft",
        )
        return 202, {"ok": True, "job_id": job_id, "kind": "retry-draft"}
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
    drafts_adapter_path: Path,
    publication_adapter_path: Path,
    job_store: JobStore = _DEFAULT_JOB_STORE,
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
                drafts_adapter_path=drafts_adapter_path,
                publication_adapter_path=publication_adapter_path,
                job_store=job_store,
            )
            if isinstance(payload, str):
                self._send_html(status, payload)
            elif isinstance(payload, PublicationAssetResponse):
                self._send_file(status, payload)
            else:
                self._send_json(status, payload)

        def _send_json(self, status: int, payload: dict[str, Any]) -> None:
            data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            try:
                self.send_response(status)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)
            except (ConnectionAbortedError, BrokenPipeError, ConnectionResetError):
                # 客户端断开（比如前端页面被关掉/刷新中断了长轮询请求）不是服务器错误，
                # 静默 return，不打 traceback 噪声。
                return

        def _send_html(self, status: int, html: str) -> None:
            data = html.encode("utf-8")
            try:
                self.send_response(status)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)
            except (ConnectionAbortedError, BrokenPipeError, ConnectionResetError):
                return

        def _send_file(self, status: int, asset: PublicationAssetResponse) -> None:
            try:
                self.send_response(status)
                self.send_header("Content-Type", asset.content_type)
                self.send_header("Content-Length", str(asset.path.stat().st_size))
                self.end_headers()
                with asset.path.open("rb") as source:
                    shutil.copyfileobj(source, self.wfile)
            except (ConnectionAbortedError, BrokenPipeError, ConnectionResetError):
                return

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
    drafts_adapter_path: Path | None = None,
    publication_adapter_path: Path | None = None,
    job_store: JobStore = _DEFAULT_JOB_STORE,
) -> ThreadingHTTPServer:
    """构建并返回一个已 bind 但尚未 serve_forever 的服务器实例（便于测试注入）。"""
    root = batch_root or _default_batch_root()
    handler_cls = make_handler_class(
        batch_root=root,
        index_html_path=index_html_path or _default_index_html_path(),
        publish_adapter_path=publish_adapter_path or _default_publish_adapter_path(),
        rewrite_adapter_path=rewrite_adapter_path or _default_rewrite_adapter_path(),
        regenerate_adapter_path=regenerate_adapter_path or _default_regenerate_adapter_path(),
        drafts_adapter_path=drafts_adapter_path or _default_drafts_adapter_path(),
        publication_adapter_path=publication_adapter_path or _default_publication_adapter_path(),
        job_store=job_store,
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