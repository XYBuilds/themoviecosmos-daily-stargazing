# Phase 8.1 - build_data.py 数据聚合瘦身 交付报告

## 1. 改动范围 (Scope)

新增文件：

- `review_panel/__init__.py`（空包标记，使 `review_panel` 可作为 Python 包被 import）
- `review_panel/build_data.py`（数据聚合瘦身模块 + argparse CLI）
- `tests/test_review_panel_build_data.py`（13 个 unittest 用例）

未修改任何既有文件。无新增/删除第三方依赖（纯标准库 + 复用 `scripts.lib.paths`）。

## 2. 技术实现 (Implementation)

模块职责：从 `output/daily_batch/{date}/{NN}-{slug}/` 下的 `news.json` / `retrieve.json` /
`llm-judge-scores.json` 聚合出前端只读的 `panel.json`，只保留展示所需字段（瘦身）。

公开/半公开 API（严格照 plan 签名）：

- `build_panel_data(date, batch_root=None) -> dict`：顶层入口，返回 panel dict。
- `write_panel_json(date, batch_root=None) -> Path`：落盘 `panel.json`。
- `list_available_dates(batch_root=None) -> list[str]`：扫描日期目录，倒序返回。
- `_join_judge_scores(candidates, judge_scores) -> list[dict]`：按 tmdb_id join judge 字段并瘦身。
- `_extract_resonance_agents(hit_sources) -> list[str]`：去重且保序提取共振 agent。

核心设计要点：

- **tmdb_id int/str 归一化**：`retrieve.json` 的 `candidate.tmdb_id` 是 `int`，
  `llm-judge-scores.json` 的 `scores[].tmdb_id` 是 `str`（两者来自不同管线）。
  join 时统一 `str(tmdb_id)` 作 key 建索引与查找，输出仍保留 candidate 原始 int 类型。
- **judge 容错**：judge 文件整体缺失、或某 tmdb_id 未被 judge 覆盖，都是正常业务状态，
  容错为空值而不抛异常。
- **字段瘦身**：candidate 只保留 schema 声明的 13 个字段，丢弃 `triggered_by`/`hit_sources`/`also_baseline` 等。
- **排序**：news_items 按 slug 前缀 `NN` 升序；前缀解析失败退回目录枚举序。

FP 风格、纯函数优先，副作用（读写文件）集中在明确的 IO 函数。

## 3. 本地验证结果 (Verification)

```
python -m pytest tests/test_review_panel_build_data.py -v
............. [100%]
13 passed in 4.09s
```

真实数据 CLI 干跑：

```
python review_panel/build_data.py --date 2026-07-06 --dry-run
news_items=10 candidates=190
```

lint：无诊断错误。

## 4. 潜在影响或技术债 (Technical Debt & Caveats)

- 无对后续 Phase 的破坏性影响；8.2/8.3 将依赖本模块产出的 `panel.json` 契约。
- CLI 增加了 plan 示例未列出的 `--batch-root` 参数（非破坏性增量，便于测试与自定义根目录），plan 中两条验收命令原样可跑。
- 全量回归 `pytest tests/ -q` 中 `test_copywriter_review.py` 有 8 个失败，经核实为 pre-existing（终端中文编码问题，与本次改动无关，本次未触碰该模块）。