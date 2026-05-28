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

# TODO(MVP-step-5): 实现 feedparser + sqlite 状态 + 标题相似度去重 + 手动 --url 旁路.
FEEDS: list[str] = [
    # 待填: 免费 RSS 源
]
