# Phase 6.4 - README/文档对齐 交付报告

## 1. 改动范围 (Scope)

- 改动的文件列表：
  - `README.md`（修改）：
    - 「MVP 执行顺序」步骤 6~8 改写为真实 `main.py` CLI（`--pick` / `--news-file` / `--url`）与 `main.py publish` 用法；
    - 新增「`run_eval.py` vs `main.py`」小节；
    - 新增「plumbing 说明：索引/小规模脚本仅用于测通」小节；
    - 「新闻抓取与手挑（fetch_news）」小节改写，纠正“必须手挑才能继续”的旧表述。
  - `.cursor/plans/Phase6-main-integration.plan.md`（修改）：`id: p6-docs` 状态 `pending` → `completed`。
  - `docs/reports/Phase6.4-docs-report.md`（新增，本报告）。
- 新增/删除的依赖包：无。
- 未修改任何 `scripts/*.py` 源码（本 todo 边界内无代码改动）。

## 2. 技术实现 (Implementation)

### 核实结论

1. **`run_eval.py` 已使用 `render_briefing` 模块**（6.1 承诺项）：确认 `scripts/run_eval.py` 顶部从 `scripts.lib.render_briefing` import `_agents_from_hit_sources` / `_candidate_auto_score_lines` / `_candidate_heading` / `_format_agent_markdown` / `_format_candidate_block` / `_format_candidates_markdown` / `_format_errors` / `_format_hit_lines` / `_format_reality_body` / `_format_run_index` / `_hit_heading` / `_pseudo_hit_total` / `_sort_candidates_for_display`，run_eval.py 内未再内联维护这些渲染函数。核实完成，未做代码改动。
2. **run index 死链修复已完成**：`scripts/lib/render_briefing.py::_format_run_index` 的 docstring 明确记录了历史死链问题（硬编码 `[[agents/A2]] [[agents/A4]] [[agents/A7]] [[agents/A1]]`），并已改为按调用方传入的 `persona_ids` 参数动态生成 persona 链接行；未传入时输出空列表而非重新硬编码死链。`run_eval.py` 调用处（第 191 行）传入 `run_persona_ids = list(persona_payloads.keys())`，确认走的是动态路径。无冲突，未触发暂停规则。
3. **`fetch_news.py` 真实 CLI 参数**（通过 `python -m scripts.fetch_news --help` 核实）：`--limit` / `--out` / `--out-json` / `--provider {rss,guardian-api}`（默认 `guardian-api`）/ `--sections` / `--order-by` / `--tag` / `--pick`（与 `--url` 互斥）/ `--title` / `--description` / `--source-name` / `--pub-time`。默认 provider 为 `guardian-api`，且其 section 列表（`GUARDIAN_API_SECTIONS`，29 个宽泛 section，经黑名单过滤掉 about/help/weather/travel 等非事件类栏目）是自动全放行的，`--pick` 是可选的调试期手工干预参数，不是强制手挑关卡。README 已按此口径改写。
4. **`main.py` 真实 CLI 参数**（通过 `python scripts/main.py --help` 核实）：`--news-file` / `--url` / `--pick N`（三者互斥）/ `--title` / `--description` / `--date` / `--provider {mimo,deepseek}` / `--no-copy` / `--personas N` / `--skip-expand` / `--judge-topk K`（默认 2）/ `--force`。**`main.py publish` 子命令在本次核实时尚不存在**（6.3 仍在并行开发中，检出时 main 上只有 6.2 的产物，`main.py` 无 subparser 机制，是纯 flat argparse），README 中 publish 示例按计划文档 Todo 6.3 的设计意图书写（`main.py publish --date ... --tmdb-id ...`），并在文中加了一句提醒：以 6.3 实际合并后的 `--help` 输出为准。
5. **`run_eval.py` 真实 CLI 参数**：`--news-file`（必填）/ `--run-id` / `--out` / `--provider` / `--deconstruction-file` / `--personas` / `--skip-expand` / `--judge-topk` / `--force`。产物目录固定 `output/Eval/{run_id}/`，与 `main.py` 的 `output/Daily_Briefing/{date}.md` 形成对照，已写入 README 新增小节。
6. **plumbing 脚本清单**（搜索确认，非臆造）：`scripts/build_index.py`（构建索引，一次性/低频）、`scripts/smoke_llm.py`（LLM 连通性测试）、`scripts/agents.py`（旧 4-persona 路径，ADR-0011 D3 判定 DEAD FLOW）、`scripts/retrieve.py --pseudo ...` 单条 CLI 调用（手工验证用，生产走 `retrieve_from_agents()` 函数调用而非 CLI）。未发现名为 `build_index` 之外的其他专职索引脚本。

### README 改动摘要

- 「MVP 执行顺序」步骤 6：改为「接 RSS / Guardian API」，说明默认 provider 与自动放行。
- 步骤 7：改为 `main.py --pick N` / `--news-file` / `--url` 三种入口，写出真实管线顺序（`resolve_news → deconstruct(A0) → expand → persona_pipeline×N → retrieve → (可选)C1 → build_daily_briefing`），产物路径与 `--date`/`--force` 语义。
- 步骤 8：改为 `main.py publish --date ... --tmdb-id ...`（按计划设计意图书写，标注 6.3 待核实）。
- 新增「`run_eval.py` vs `main.py`」小节：产物目录对比 + 共享 `render_briefing.py` 事实说明 + 共享的四个 Phase 6.0 开发开关。
- 新增「plumbing 说明」小节：逐条列出索引/连通性/旧路径/单条 CLI 四类非生产脚本及原因。
- 「新闻抓取与手挑（fetch_news）」小节开头新增一段，纠正“先手挑才能进入主链路”的旧表述，明确 `--pick` 是调试期手工干预开关。

## 3. 本地验证结果 (Verification)

- `python scripts/main.py --help`：核对 12 个参数名与 README 描述逐条一致。
- `python -m scripts.fetch_news --help`（`fetch_news.py` 内部用 `from scripts.lib.paths import ...` 绝对导入，直接 `python scripts/fetch_news.py --help` 会报 `ModuleNotFoundError: No module named 'scripts'`；用 `-m` 方式在仓库根目录跑通）：核对 12 个参数名一致。
- Grep 核实 `run_eval.py` import 语句、`_format_run_index` docstring 与调用处传参，确认 6.1 承诺的两项工作（模块化 + 死链修复）均已完成，无需暂停。
- `python -m pytest tests/ -q`：`8 failed, 279 passed, 1 skipped`（47.89s）。失败集合与 Phase 6.2 报告记录的既有基线 8 个失败（均在 `tests/test_copywriter_review.py`，`copy_text` 属性缺失 + mojibake 断言字符串的历史遗留问题）完全一致，本次改动前后失败数量不变，未新增回归。本 todo 未修改任何 Python 源码，此次测试仅用于确认改动分支未破坏现状。

## 4. 潜在影响或技术债 (Technical Debt & Caveats)

### 计划草稿 CLI 示例 vs 真实代码差异清单

| 计划草稿（`.cursor/plans/Phase6-main-integration.plan.md` Todo 6.4） | 真实代码 | 处理方式 |
|---|---|---|
| `main.py --pick N` | 真实为 `--pick N`（int，1-based，与 `--news-file`/`--url` 三者互斥组），参数名一致，行为一致 | 无需改写，按原样写入 README |
| 未提及 `--title`/`--description` 是 `--url` 的必要 fallback（当链接自动解析失败时） | 真实 `--url` 解析失败必须同时补 `--title` 与 `--description` | README 已在 `--url` 示例中带上 `--title`/`--description` |
| `main.py publish --date ... --tmdb-id ...` | **本次核实时该子命令在 main 分支尚不存在**（main.py 是 flat argparse，无 subcommand 机制），6.3 仍在并行分支开发中 | 按计划设计意图写入 README，并加提醒句：以 6.3 实际合并后的 `--help` 为准；这是本次已知、非本 todo 范围内的差异，非"6.1 声称完成但未完成"级别的冲突，未触发暂停规则 |
| 未提及 `fetch_news.py` 默认 provider 及 Guardian section 宽泛自动放行策略 | `fetch_news.py` 默认 `--provider guardian-api`，`GUARDIAN_API_SECTIONS`（29 个）经黑名单过滤后自动放行，`--pick` 降级为调试开关（Phase 5.4 变更） | README 新增说明，纠正"必须手挑"的旧印象 |

### 6.3 合并后可能需要的后续小修提醒

- README 里 `main.py publish --date 2026-07-04 --tmdb-id 157336` 这条命令示例是基于计划文档 Todo 6.3 的设计意图书写的，**尚未用真实 `--help` 输出核实**（6.3 检出时未合并，且当时 main.py 无 publish 子命令）。6.3 合并后建议做一次轻量核对：跑 `python scripts/main.py publish --help`（或等价方式），确认参数名（尤其是是否真的是 `--tmdb-id` 而非其他命名，以及是否存在 `--selected-file`/`--selected-copy` 等 Phase 6.3 设计草稿里提到的额外参数）与 README 描述一致，不一致则小修 README，不需要重开完整 todo 流水线。
- 若 6.3 最终把 publish 逻辑接到了 `compose.py --stage publish`（已存在的 `--stage publish --tmdb-id` 参数）而非在 `main.py` 里新增独立 subcommand，README 里的产物路径描述（`{date}_copy.md`）预期不受影响，但调用命令本身需要核对。

### 其他

- 本 todo 未发现 6.1 声称完成但实际未完成的问题，未触发暂停规则，全流程可以推进到合并。