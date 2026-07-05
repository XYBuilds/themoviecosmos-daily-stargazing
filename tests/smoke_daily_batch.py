"""smoke_daily_batch.py · Phase 7.3 集成冒烟测试.

用真实 Guardian API key 跑一次小批量 daily_batch，验证端到端产出。

不是 pytest 用例（依赖真实网络 + LLM 调用，成本较高），是独立脚本：

用法：
  python tests/smoke_daily_batch.py
  python tests/smoke_daily_batch.py --min-count 3 --personas 2
  python tests/smoke_daily_batch.py --date 2026-07-05 --resume

检查项：
  1. output/daily_batch/{date}/pool.json 存在，且每条含 score 字段。
  2. state/daily_batch_{date}.json 存在，且逐条打印每个 item 的 status。
  3. 至少 1 条 news 产出了完整的 briefing.md。
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from scripts.daily_batch import (  # noqa: E402
    DEFAULT_MIN_COUNT,
    batch_output_dir,
    item_dir,
    load_batch_state,
    run_daily_batch,
    state_path,
)
from scripts.lib.run_options import RunOptions  # noqa: E402


def _today_iso() -> str:
    from datetime import UTC, datetime

    return datetime.now(UTC).strftime("%Y-%m-%d")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Phase 7.3 集成冒烟测试：用真实 API key 跑一次小批量 daily_batch。",
    )
    parser.add_argument("--date", help="批次日期覆盖（默认今天，UTC，YYYY-MM-DD）")
    parser.add_argument(
        "--min-count",
        type=int,
        default=3,
        metavar="N",
        help=f"热度池最小条数（默认 3；生产默认 {DEFAULT_MIN_COUNT}）",
    )
    parser.add_argument(
        "--personas",
        type=int,
        default=2,
        metavar="N",
        help="每条 news 只跑前 N 个 persona（默认 2，控制成本）",
    )
    parser.add_argument("--resume", action="store_true", help="从既有 state 断点续跑")
    parser.add_argument("--skip-expand", action="store_true", help="跳过 P-Expand 阶段")
    parser.add_argument(
        "--provider",
        choices=["mimo", "deepseek"],
        help="LLM provider 覆盖（默认 DEFAULT_LLM_PROVIDER from .env）",
    )
    return parser


def _check_pool(date: str) -> tuple[bool, str]:
    """检查 pool.json 存在且每条含 score 字段。"""
    pool_path = batch_output_dir(date) / "pool.json"
    if not pool_path.is_file():
        return False, f"pool.json 不存在: {pool_path}"

    pool = json.loads(pool_path.read_text(encoding="utf-8"))
    if not isinstance(pool, list) or not pool:
        return False, f"pool.json 为空或格式错误: {pool_path}"

    missing_score = [item.get("url") for item in pool if "score" not in item]
    if missing_score:
        return False, f"以下条目缺少 score 字段: {missing_score}"

    return True, f"pool.json OK，共 {len(pool)} 条，均含 score 字段"


def _check_state(date: str) -> tuple[bool, str, list[dict[str, str]]]:
    """检查 state 文件存在，逐条列出 item 的 status。"""
    path = state_path(date)
    if not path.is_file():
        return False, f"state 文件不存在: {path}", []

    batch_state = load_batch_state(path)
    if not batch_state.items:
        return False, f"state 文件中 items 为空: {path}", []

    rows = [
        {"index": str(it.index), "title": it.title, "status": it.status}
        for it in batch_state.items
    ]
    all_done = all(it.status == "done" for it in batch_state.items)
    summary = f"state.json OK，共 {len(batch_state.items)} 条 item，全部 done: {all_done}"
    return True, summary, rows


def _check_briefings(date: str) -> tuple[bool, str]:
    """检查至少 1 条 news 有 briefing.md。"""
    path = state_path(date)
    if not path.is_file():
        return False, f"state 文件不存在，无法定位 item 目录: {path}"

    batch_state = load_batch_state(path)
    found: list[str] = []
    for it in batch_state.items:
        briefing_path = item_dir(date, it.index, it.slug) / "briefing.md"
        if briefing_path.is_file() and briefing_path.stat().st_size > 0:
            found.append(str(briefing_path))

    if not found:
        return False, "没有任何 item 产出非空 briefing.md"

    return True, f"共 {len(found)} 条 briefing.md 已产出，例如: {found[0]}"


def run_smoke(args: argparse.Namespace) -> int:
    date = args.date or _today_iso()
    run_options = RunOptions(persona_limit=args.personas, skip_expand=args.skip_expand)

    print(f"=== Phase 7.3 冒烟测试 · date={date} min_count={args.min_count} personas={args.personas} ===")
    try:
        asyncio.run(
            run_daily_batch(
                date=date,
                resume=args.resume,
                min_count=args.min_count,
                run_options=run_options,
                provider=args.provider,
            )
        )
    except Exception as exc:  # noqa: BLE001 — 冒烟脚本需要捕获所有异常并报告，而非崩溃退出
        print(f"\n[FAIL] run_daily_batch 抛出异常: {exc!r}", file=sys.stderr)
        return 1

    print("\n--- 产出检查 ---")
    checks: list[tuple[bool, str]] = []

    ok, msg = _check_pool(date)
    checks.append((ok, msg))
    print(f"[{'PASS' if ok else 'FAIL'}] pool.json — {msg}")

    ok, msg, rows = _check_state(date)
    checks.append((ok, msg))
    print(f"[{'PASS' if ok else 'FAIL'}] state.json — {msg}")
    for row in rows:
        print(f"    - #{row['index']} {row['title'][:50]!r} → {row['status']}")

    ok, msg = _check_briefings(date)
    checks.append((ok, msg))
    print(f"[{'PASS' if ok else 'FAIL'}] briefing.md — {msg}")

    print("\n=== 总结 ===")
    passed = sum(1 for ok, _ in checks if ok)
    total = len(checks)
    print(f"{passed}/{total} 项检查通过")

    if passed == total:
        print("[PASS] 冒烟测试全部通过")
        return 0

    print("[FAIL] 冒烟测试未全部通过，请检查上方日志")
    return 1


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return run_smoke(args)


if __name__ == "__main__":
    raise SystemExit(main())