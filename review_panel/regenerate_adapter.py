"""regenerate_adapter.py · Phase 9.8.3 · 单条定稿的「重生成」薄适配脚本.

与 ``publish_adapter.py`` / ``rewrite_adapter.py`` 同层：本文件是唯一 import
``scripts.compose`` 的重生成入口，耦合收敛在这一处，``serve.py``（后续 TODO）通过
subprocess/直接 import 调用本模块，不需要自己拼装 news/candidate/judge。

职责边界（ADR-0016 D2/D3/D4）：
- 只做**覆盖语义**——改写既有 ``{slug}_copy_{platform}.md`` 的 headline 或 body，
  不产出新版本文件、不建版本目录。总编只有「一份原稿」，重生成即覆盖它。
- ``target=body``（D2）：复用 ``compose.run_publish``（与首次发布同一条创作管线），
  但**只取它的 body**，丢弃它顺带产出的 headline——因为 run_publish 是「从零创作」
  的入口，它给出的 headline 是给「首次发布」用的；重生成 body 时总编通常只想换正文、
  保留已经定下来的标题，若采用新 headline 会在总编不知情的情况下悄悄换掉标题。
- ``target=headline``（D3）：复用 ``compose.run_headline``，它是 body-aware 的——
  贴合**当前正文**重新出一句标题，而不是另起一篇。
- humanized 失效范围只在 body（D4）：``{slug}_copy_{platform}_humanized.md`` 是对
  原稿 body 的去 AI 化改写产物，body 变了它就是对着旧正文改写的过期缓存，必须删除
  逼下游重新触发 rewrite_adapter；headline 变化不影响 body，humanized 原样保留。
  selection.json 里的 ``humanized_path`` 字段清理是 serve 层（9.8.4）的职责，本文件
  只管文件系统，不摸 selection.json。

为什么两种 target 都强制要 tmdb_id：无论是重出 body 还是重出 headline，
``compose.run_publish``/``compose.run_headline`` 都要靠 candidate（经
``format_selected_movie_block``）把「选中的是哪部电影」喂给 prompt——headline
本身贴合的是「新闻 + 选中电影 + 当前正文」三者的关系，不是纯文本改写，没有
candidate 就没法保证新标题依然贴着这部电影。serve 层（后续 TODO）会从
selection.json 里读出已选定的 tmdb_id 再调用本模块；本模块本身保持「参数的
纯函数」，不耦合 selection.json 的读写。
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from scripts import compose
from review_panel.publish_adapter import (
    _default_batch_root,
    find_candidate,
    load_judge_entry,
    load_news,
    locate_news_dir,
    render_copy_markdown,
)
from review_panel.serve import _delete_copy_if_exists, parse_copy_markdown


def run_adapter(
    date: str,
    slug: str,
    tmdb_id: int | str,
    target: str,
    *,
    provider: str | None = None,
    platform: str = "xiaohongshu",
    batch_root: Path | None = None,
    run_publish: Any = compose.run_publish,
    run_headline: Any = compose.run_headline,
) -> Path:
    """薄适配 orchestrator：覆盖重生成既有 ``{slug}_copy_{platform}.md`` 的一半内容。

    ``run_publish``/``run_headline`` 可注入（默认 ``compose`` 真实函数），测试用 stub
    替换，避免真调 LLM。``target`` 只能是 ``"headline"`` 或 ``"body"``，其他值不做
    校验直接留给调用方的编程错误（内部调用点，不是面向不可信输入的 CLI 层）。
    """
    root = batch_root or _default_batch_root()
    news_dir = locate_news_dir(date, slug, batch_root=root)
    news = load_news(news_dir)
    candidate = find_candidate(news_dir, tmdb_id)
    judge = load_judge_entry(news_dir, tmdb_id)

    copy_path = news_dir.parent / f"{slug}_copy_{platform}.md"
    if not copy_path.is_file():
        raise ValueError(f"copy file not found: {copy_path}")

    parsed = parse_copy_markdown(copy_path.read_text(encoding="utf-8"))

    if target == "body":
        draft = run_publish(candidate, news, provider=provider, judge=judge, platform=platform)
        new_body = str(draft.get("body") or "").strip()
        if not new_body:
            raise ValueError("run_publish returned empty body, nothing to regenerate")
        # 丢弃 draft 里顺带产出的 headline（见模块 docstring）：本次只换 body。
        merged = {"headline": parsed["headline"], "body": new_body}
        copy_path.write_text(
            render_copy_markdown(date, candidate, news, merged, platform=platform),
            encoding="utf-8",
        )
        # D4：body 变了，humanized 是对旧 body 的改写缓存，必须失效。
        _delete_copy_if_exists(copy_path.parent / f"{slug}_copy_{platform}_humanized.md")
    elif target == "headline":
        current_body = parsed["body"]
        if not current_body:
            raise ValueError("copy file has empty body, cannot regenerate headline")
        result = run_headline(
            candidate, news, current_body, provider=provider, judge=judge, platform=platform
        )
        new_headline = str(result.get("headline") or "").strip()
        if not new_headline:
            raise ValueError("run_headline returned empty headline")
        merged = {"headline": new_headline, "body": current_body}
        copy_path.write_text(
            render_copy_markdown(date, candidate, news, merged, platform=platform),
            encoding="utf-8",
        )
        # headline 变化不动 body，humanized（对 body 的改写）无需失效，故意不删。
    else:
        raise ValueError(f"unknown target {target!r}, expected 'headline' or 'body'")

    return copy_path


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Regenerate the headline or body of an existing "
        "{slug}_copy_{platform}.md in place (overwrite semantics).",
    )
    parser.add_argument("--date", required=True, help="日期，如 2026-07-06")
    parser.add_argument("--slug", required=True, help="新闻目录 slug")
    parser.add_argument("--tmdb-id", dest="tmdb_id", required=True, help="选定候选的 tmdb_id")
    parser.add_argument(
        "--platform",
        choices=["xiaohongshu"],
        default="xiaohongshu",
        help="发布平台（默认 xiaohongshu）。",
    )
    parser.add_argument(
        "--target",
        required=True,
        choices=["headline", "body"],
        help="重生成目标：headline 或 body。",
    )
    parser.add_argument("--provider", choices=["mimo", "deepseek"], default=None)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    try:
        copy_path = run_adapter(
            args.date,
            args.slug,
            args.tmdb_id,
            args.target,
            provider=args.provider,
            platform=args.platform,
        )
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        print("interrupted", file=sys.stderr)
        return 130
    print(f"Wrote {copy_path.resolve()}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())