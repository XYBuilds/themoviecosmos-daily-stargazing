"""rewrite_adapter.py · Phase 9.7.4 · avoid-ai-writing 面板集成薄适配脚本.

D5 架构决策：与 ``publish_adapter.py`` 同层——``serve.py`` 通过 subprocess 调用本脚本，
不直接 import ``scripts.lib.llm``。耦合收敛在本单文件：只有这里 import ``scripts.lib.llm``
+ ``prompts/avoid_ai_writing_rewrite.md``，避免把 LLM 依赖拖进 serve.py 的路由薄传输层。

职责：读 ``{slug}_copy_{platform}.md`` → 提取 body → 调 LLM 按 avoid-ai-writing 规则改写
→ 写 ``{slug}_copy_{platform}_humanized.md``（headline + 链接原样保留，只改 body）。
原稿从不被本脚本写入，humanized 版本可反复重新生成（覆盖）。
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from review_panel.publish_adapter import _PLATFORM_LABELS
from review_panel.serve import parse_copy_markdown
from scripts.lib.env import default_llm_provider, load_env
from scripts.lib.llm import get_llm_client
from scripts.lib.paths import repo_root

# 与 scripts/compose.py 的 _MODEL_ENV 完全一致：provider → 模型名环境变量。
# 不 import compose.py 是有意的（D5 要求 rewrite_adapter 的耦合止于 scripts.lib.*），
# 这份小映射复制一次比引入 compose 全量重依赖更划算。
_MODEL_ENV: dict[str, str] = {
    "mimo": "MIMO_MODEL",
    "deepseek": "DEEPSEEK_MODEL",
}

_PROMPT_REL = "prompts/avoid_ai_writing_rewrite.md"
_PLACEHOLDER = "{{body}}"

_SYSTEM_MESSAGE = (
    "你是「每日星轨观测」的文案改写助理，严格按用户消息里的规则改写正文，"
    "只输出改写后的正文本身，不输出任何说明、标题或额外文字。"
)


def _default_batch_root() -> Path:
    return repo_root() / "output" / "daily_batch"


def _resolve_provider(explicit: str | None) -> str:
    if explicit is not None:
        return explicit.strip().lower()
    return default_llm_provider()


def _model_name(provider: str) -> str:
    """镜像 scripts.compose._model_name：从环境变量解析模型名，缺失即报错。"""
    load_env()
    env_key = _MODEL_ENV.get(provider)
    if not env_key:
        raise ValueError(f"Unknown provider {provider!r}")
    model = os.getenv(env_key, "").strip()
    if not model:
        raise RuntimeError(
            f"Missing {env_key} for provider {provider!r}. "
            "Copy .env.example to .env and set the model name."
        )
    return model


def render_rewrite_prompt(template: str, body: str) -> str:
    return template.replace(_PLACEHOLDER, body)


def _real_call_llm(prompt: str, *, provider: str | None) -> str:
    load_env()
    resolved = _resolve_provider(provider)
    client = get_llm_client(resolved)
    model = _model_name(resolved)
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": _SYSTEM_MESSAGE},
            {"role": "user", "content": prompt},
        ],
    )
    return str(response.choices[0].message.content or "").strip()


def locate_copy_path(date: str, slug: str, platform: str, batch_root: Path | None = None) -> Path:
    """定位 ``{batch_root}/{date}/{slug}_copy_{platform}.md``；缺失即清晰报错。"""
    root = batch_root or _default_batch_root()
    copy_path = root / date / f"{slug}_copy_{platform}.md"
    if not copy_path.is_file():
        raise ValueError(f"copy file not found: {copy_path}")
    return copy_path


def _extract_links_block(text: str) -> str:
    """从原稿里取出从 ``## 链接`` 开始到文末的原样文本（含该标题行），保底空串。

    直接复用原文本身，而不是重新拼 movie_url/news_url，避免和
    ``publish_adapter.render_copy_markdown`` 的链接渲染规则产生第二处漂移点。
    """
    idx = text.find("## 链接")
    if idx == -1:
        return ""
    return text[idx:].rstrip("\n")


def render_humanized_markdown(
    date: str,
    headline: str,
    humanized_body: str,
    links_block: str,
    *,
    platform: str = "xiaohongshu",
) -> str:
    """渲染 humanized 版：与 render_copy_markdown 同一套精简排版，只换 body。"""
    platform_label = _PLATFORM_LABELS.get(platform, platform)
    lines = [
        f"# 发布定稿 · {date} · {platform_label}",
        "",
        headline or "（无标题）",
        "",
        humanized_body or "（无正文）",
        "",
    ]
    if links_block:
        lines.append(links_block)
        lines.append("")
    return "\n".join(lines)


def run_adapter(
    date: str,
    slug: str,
    *,
    platform: str = "xiaohongshu",
    provider: str | None = None,
    batch_root: Path | None = None,
    copy_path: Path | None = None,
    humanized_path: Path | None = None,
    call_llm: Any = None,
) -> Path:
    """读当前稿，生成 humanized 稿。

    新发布包流程显式传入 ``copy_path`` 与 ``humanized_path``；省略时使用旧
    daily_batch 路径，以保持历史脚本和产物的可读性。
    """
    root = batch_root or _default_batch_root()
    resolved_copy_path = copy_path or locate_copy_path(date, slug, platform, batch_root=root)
    original_text = resolved_copy_path.read_text(encoding="utf-8")
    parsed = parse_copy_markdown(original_text)
    body = parsed["body"]
    if not body:
        raise ValueError(f"copy file has empty body, nothing to rewrite: {resolved_copy_path}")

    template = (repo_root() / _PROMPT_REL).read_text(encoding="utf-8")
    prompt = render_rewrite_prompt(template, body)

    if call_llm is not None:
        humanized_body = str(call_llm(prompt) or "").strip()
    else:
        humanized_body = _real_call_llm(prompt, provider=provider)

    if not humanized_body:
        raise ValueError("LLM returned empty humanized body")

    links_block = _extract_links_block(original_text)
    resolved_humanized_path = humanized_path or (
        resolved_copy_path.parent / f"{slug}_copy_{platform}_humanized.md"
    )
    resolved_humanized_path.parent.mkdir(parents=True, exist_ok=True)
    resolved_humanized_path.write_text(
        render_humanized_markdown(
            date, parsed["headline"], humanized_body, links_block, platform=platform
        ),
        encoding="utf-8",
    )
    return resolved_humanized_path


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Rewrite a daily_batch copy draft via avoid-ai-writing, "
        "writing {slug}_copy_{platform}_humanized.md.",
    )
    parser.add_argument("--date", required=True, help="日期，如 2026-07-06")
    parser.add_argument("--slug", required=True, help="新闻目录 slug")
    parser.add_argument("--platform", default="xiaohongshu", help="发布平台（默认 xiaohongshu）")
    parser.add_argument("--provider", choices=["mimo", "deepseek"], default=None)
    parser.add_argument("--copy-path", type=Path, default=None)
    parser.add_argument("--humanized-path", type=Path, default=None)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    try:
        humanized_path = run_adapter(
            args.date,
            args.slug,
            platform=args.platform,
            provider=args.provider,
            copy_path=args.copy_path,
            humanized_path=args.humanized_path,
        )
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        print("interrupted", file=sys.stderr)
        return 130
    print(f"Wrote {humanized_path.resolve()}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())