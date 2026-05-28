"""main.py · 串起每日星轨观测的端到端管线.

链路 (MVP):
  fetch_news  ->  agents (3 Persona 并发)  ->  retrieve (Top-2 each)
  ->  render Markdown -> 写入 output/Daily_Briefing/YYYY-MM-DD.md

CLI:
  python scripts/main.py                       # 自动抓 RSS 选 Top1
  python scripts/main.py --url <news_url>      # 手动指定新闻
  python scripts/main.py --news-file path.json # 手喂一条 JSON 新闻 (调试用)
"""

from __future__ import annotations

# TODO(MVP-step-6): 串联所有模块, 渲染 Markdown 模板, 写入 Obsidian Vault.
