"""fetch_news.py · RSS 抓取与候选新闻挑选 (MVP 半自动).

MVP 决策:
  - 用免费 RSS 源 (清单待定, 放本文件 FEEDS 常量).
  - "热度": 多源同事件计数 + 时间近端加权 (暂粗糙).
  - 去重:
      a) URL 规范化 (剥 utm_*) 后查 state/seen_news.sqlite, 跑过则跳过
      b) 标题相似度: 与过去 14 天选过的标题做 difflib.SequenceMatcher, >=0.7 跳过
  - 允许人工指定 url 绕过整段抓取 (CLI: --url <url>).
  - 不爬全文, 仅用 RSS 自带 title + description + pub_time + source_name.

输出: 一个 dict
  {
    "title": str,
    "description": str,
    "pub_time": str | None,
    "source_name": str | None,
    "url": str,
  }
"""

from __future__ import annotations

from contextlib import closing
from datetime import datetime, timedelta, timezone
import difflib
import html
import logging
from pathlib import Path
import re
import sqlite3
from typing import Any
from urllib.parse import parse_qsl, urlencode, urlparse, urlsplit, urlunsplit

import feedparser

from scripts.lib.paths import seen_news_db

logger = logging.getLogger(__name__)

FEEDS: list[str] = [
    "https://feeds.bbci.co.uk/news/world/rss.xml",
    "https://www.npr.org/rss/rss.php?id=1001",
    "https://www.aljazeera.com/xml/rss/all.xml",
]


_TAG_RE = re.compile(r"<[^>]+>")
_WHITESPACE_RE = re.compile(r"\s+")
_TRACKING_QUERY_KEYS = {"fbclid", "gclid", "dclid", "msclkid", "mc_cid", "mc_eid", "igshid"}


def _db_path(db_path: Path | None = None) -> Path:
    """Resolve the dedup SQLite path; tests can inject a temp file."""

    return seen_news_db() if db_path is None else Path(db_path)


def _ensure_schema(conn: sqlite3.Connection) -> None:
    """Create RSS dedup tables if this is the first database access."""

    conn.execute(
        "CREATE TABLE IF NOT EXISTS seen_urls (url_norm TEXT PRIMARY KEY, seen_at TEXT)"
    )
    conn.execute("CREATE TABLE IF NOT EXISTS seen_titles (title TEXT, seen_at TEXT)")
    conn.commit()


def _connect(db_path: Path | None = None) -> sqlite3.Connection:
    """Open the dedup database and ensure URL/title state tables exist."""

    resolved = _db_path(db_path)
    resolved.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(resolved)
    _ensure_schema(conn)
    return conn


def _utc_now(now: datetime | None = None) -> datetime:
    if now is None:
        return datetime.now(timezone.utc)
    if now.tzinfo is None:
        return now.replace(tzinfo=timezone.utc)
    return now.astimezone(timezone.utc)


def _iso_now(now: datetime | None = None) -> str:
    return _utc_now(now).isoformat()


def normalize_url(url: str) -> str:
    """Normalize an RSS article URL for deterministic URL-level deduplication.

    Tracking query parameters are removed, scheme/host are lower-cased, fragments are
    discarded, and normal query parameters are preserved. Path case is intentionally
    unchanged because URL paths can be case-sensitive.
    """

    split = urlsplit(url.strip())
    query_pairs = []
    for key, value in parse_qsl(split.query, keep_blank_values=True):
        key_lower = key.lower()
        if key_lower.startswith("utm_") or key_lower in _TRACKING_QUERY_KEYS:
            continue
        query_pairs.append((key, value))

    # 数据流向：RSS 原始 URL -> 去营销参数/fragment -> 规范化 URL -> seen_urls 主键。
    return urlunsplit(
        (
            split.scheme.lower(),
            split.netloc.lower(),
            split.path,
            urlencode(query_pairs, doseq=True),
            "",
        )
    )


def is_url_seen(url: str, db_path: Path | None = None) -> bool:
    """Return True when the normalized URL already exists in seen_urls."""

    url_norm = normalize_url(url)
    with closing(_connect(db_path)) as conn:
        row = conn.execute(
            "SELECT 1 FROM seen_urls WHERE url_norm = ? LIMIT 1", (url_norm,)
        ).fetchone()
    return row is not None


def mark_url_seen(
    url: str, db_path: Path | None = None, seen_at: str | None = None
) -> None:
    """Persist a normalized selected URL in seen_urls.

    This write belongs to the selection stage (5.3), not the RSS fetch/filter stage.
    """

    with closing(_connect(db_path)) as conn:
        conn.execute(
            "INSERT OR IGNORE INTO seen_urls (url_norm, seen_at) VALUES (?, ?)",
            (normalize_url(url), seen_at or _iso_now()),
        )
        conn.commit()


def _normalize_title(title: str) -> str:
    return _WHITESPACE_RE.sub(" ", title.strip().lower())


def is_title_similar(
    title: str,
    db_path: Path | None = None,
    *,
    threshold: float = 0.7,
    within_days: int = 14,
    now: datetime | None = None,
) -> bool:
    """Return True if title resembles a selected title within the recent window.

    标题相似度只供 5.3 选用阶段标注/展示；抓取阶段的 filter_new_entries
    不会因为标题相似而丢弃候选。
    """

    cutoff = _utc_now(now) - timedelta(days=within_days)
    candidate = _normalize_title(title)
    with closing(_connect(db_path)) as conn:
        rows = conn.execute(
            "SELECT title FROM seen_titles WHERE seen_at >= ?", (cutoff.isoformat(),)
        ).fetchall()

    for (seen_title,) in rows:
        ratio = difflib.SequenceMatcher(
            None, candidate, _normalize_title(str(seen_title))
        ).ratio()
        if ratio >= threshold:
            return True
    return False


def mark_title_seen(
    title: str, db_path: Path | None = None, seen_at: str | None = None
) -> None:
    """Persist a selected title for later 14-day similarity checks."""

    with closing(_connect(db_path)) as conn:
        conn.execute(
            "INSERT INTO seen_titles (title, seen_at) VALUES (?, ?)",
            (title.strip(), seen_at or _iso_now()),
        )
        conn.commit()


def filter_new_entries(
    entries: list[dict],
    db_path: Path | None = None,
    *,
    title_threshold: float = 0.7,
    within_days: int = 14,
    now: datetime | None = None,
) -> list[dict]:
    """Filter RSS candidates by URL seen state only, preserving input order.

    抓取阶段语义边界：这里只读 seen_urls，不写库，也不按标题相似度过滤。
    title_threshold/within_days/now 预留给 5.3 选用阶段 UI 标注，不参与本函数判定。
    """

    del title_threshold, within_days, now
    new_entries: list[dict] = []
    for entry in entries:
        url = entry.get("url")
        if not isinstance(url, str) or not url.strip():
            new_entries.append(entry)
            continue
        if not is_url_seen(url, db_path):
            new_entries.append(entry)
    return new_entries


def mark_selected(
    entry: dict, db_path: Path | None = None, now: datetime | None = None
) -> None:
    """Mark a picked news payload as seen by both URL and title for 5.3."""

    seen_at = _iso_now(now)
    url = entry.get("url")
    title = entry.get("title")
    # 数据流向：用户选中的 payload -> 同一时间戳写入 URL 去重 + 标题相似度状态。
    if isinstance(url, str) and url.strip():
        mark_url_seen(url, db_path, seen_at=seen_at)
    if isinstance(title, str) and title.strip():
        mark_title_seen(title, db_path, seen_at=seen_at)


def _get_value(obj: Any, key: str, default: Any = None) -> Any:
    """同时兼容 feedparser 对象、SimpleNamespace 与 dict 的字段读取。"""

    if isinstance(obj, dict):
        return obj.get(key, default)
    return getattr(obj, key, default)


def _strip_html(text: str) -> str:
    """移除 RSS 摘要里的轻量 HTML，并压平多余空白。"""

    unescaped = html.unescape(text)
    without_tags = _TAG_RE.sub("", unescaped)
    return _WHITESPACE_RE.sub(" ", without_tags).strip()


def _published_to_iso(published_parsed: Any) -> str | None:
    """将 feedparser 的 published_parsed 转成 UTC ISO8601 字符串。"""

    if not published_parsed:
        return None

    try:
        return datetime(*published_parsed[:6], tzinfo=timezone.utc).isoformat()
    except (TypeError, ValueError):
        logger.warning("Invalid published_parsed value: %r", published_parsed)
        return None


def _source_name(parsed_feed: Any, feed_url: str) -> str | None:
    """优先使用 RSS 自带源名；缺失时回退到 feed URL 域名。"""

    feed_meta = _get_value(parsed_feed, "feed", {}) or {}
    title = _get_value(feed_meta, "title")
    if isinstance(title, str) and title.strip():
        return title.strip()

    hostname = urlparse(feed_url).hostname
    return hostname or None


def _entry_to_payload(entry: Any, source_name: str | None) -> dict[str, str | None] | None:
    """把单条 RSS entry 规范化为 news payload；缺必填字段则返回 None。"""

    title = _get_value(entry, "title")
    raw_description = _get_value(entry, "summary") or _get_value(entry, "description")
    url = _get_value(entry, "link")

    # 数据流向：RSS entry -> 必填字段校验 -> HTML 清洗 -> payload dict。
    if not isinstance(title, str) or not title.strip():
        return None
    if not isinstance(raw_description, str) or not raw_description.strip():
        return None
    if not isinstance(url, str) or not url.strip():
        return None

    description = _strip_html(raw_description)
    if not description:
        return None

    return {
        "title": title.strip(),
        "description": description,
        "pub_time": _published_to_iso(_get_value(entry, "published_parsed")),
        "source_name": source_name,
        "url": url.strip(),
    }


def fetch_feed(feed_url: str) -> list[dict]:
    """解析单个 RSS feed，返回符合 news payload schema 的条目列表。

    网络、解析异常或 bozo 失败不会向外抛出；调用方只会拿到空列表。
    """

    try:
        parsed_feed = feedparser.parse(feed_url)
    except Exception as exc:  # noqa: BLE001 - 抓取层必须隔离单源异常
        logger.warning("Failed to parse RSS feed %s: %s", feed_url, exc)
        return []

    if _get_value(parsed_feed, "bozo", False):
        logger.warning(
            "RSS feed parsed with bozo flag %s: %s",
            feed_url,
            _get_value(parsed_feed, "bozo_exception", "unknown parse error"),
        )
        return []

    source = _source_name(parsed_feed, feed_url)
    payloads: list[dict] = []

    # 数据流向：feed entries -> 单条规范化 -> 丢弃不完整条目 -> 合并返回。
    for entry in _get_value(parsed_feed, "entries", []) or []:
        payload = _entry_to_payload(entry, source)
        if payload is not None:
            payloads.append(payload)

    return payloads


def fetch_all_entries(feeds: list[str] | None = None) -> list[dict]:
    """合并多个 RSS feed 的规范化 news payload，单源失败不影响整批。"""

    selected_feeds = FEEDS if feeds is None else feeds
    entries: list[dict] = []

    for feed_url in selected_feeds:
        try:
            entries.extend(fetch_feed(feed_url))
        except Exception as exc:  # noqa: BLE001 - 保护整批抓取不被单源拖垮
            logger.warning("Skipping RSS feed %s after unexpected error: %s", feed_url, exc)

    return entries
