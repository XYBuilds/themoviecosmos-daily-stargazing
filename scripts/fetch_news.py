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

from datetime import datetime, timezone
import html
import logging
import re
from typing import Any
from urllib.parse import urlparse

import feedparser

logger = logging.getLogger(__name__)

FEEDS: list[str] = [
    "https://feeds.bbci.co.uk/news/world/rss.xml",
    "https://www.npr.org/rss/rss.php?id=1001",
    "https://www.aljazeera.com/xml/rss/all.xml",
]


_TAG_RE = re.compile(r"<[^>]+>")
_WHITESPACE_RE = re.compile(r"\s+")


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
