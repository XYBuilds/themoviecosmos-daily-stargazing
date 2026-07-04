# Phase 6.1 - render_briefing 抽离 交付报告

## 1. 改动范围 (Scope)

改动的文件列表：

- 新增 `scripts/lib/render_briefing.py`（渲染函数模块，从 `scripts/run_eval.py` 迁入）
- 修改 `scripts/run_eval.py`：删除内联的渲染函数实现，改为从 `scripts.lib.render_briefing` import；`write_eval_bundle` 调用 `_format_run_index` 时新增 `persona_ids` 参数传递（动态 persona 链接，见第 2 节）
- 修改 `.cursor/plans/Phase6-main-integration.plan.md`：`p6-render-module` 状态 `pending` → `completed`
- 新增 `docs/reports/Phase6.1-render-briefing-report.md`（本报告）

新增/删除的依赖包：无（本 todo 未改动 `pyproject.toml`/`requirements.txt`，全部为标准库 + 项目内既有模块）。

## 2. 技术实现 (Implementation)

### 核心设计思路

`run_eval.py` 原本内联了一组 `_format_*` / `_agents_from_hit_sources` / `_sort_candidates_for_display` 等纯格式化函数（无副作用，输入输出均为 dict/list/str），本 todo 将它们原样迁移到 `scripts/lib/render_briefing.py`，`run_eval.py` 改为 import 调用。迁移遵循「逐字复制，仅补充必要的模块化封装」原则：

- 所有函数体与迁移前逐字节一致（已用真实基线数据验证，见第 3 节）。
- `run_eval.py` 中被其他脚本（`score_eval_candidates.py`、`run_phase38_eval.py`、`scripts/eval/run_phase5_judge.py`、`tests/test_run_eval_candidates.py`）通过 `from scripts.run_eval import _format_candidates_markdown` 等方式直接引用的私有函数，在 `run_eval.py` 顶部改为从 `render_briefing` re-export（`from scripts.lib.render_briefing import (...)`），确保这些下游模块无需改动即可继续工作（已用 pytest 验证，见第 3 节）。
- `run_eval.py` 里仍保留、未迁移的函数：`_agent_outputs_by_id`（依赖 `AgentOutput` 对象，属管道装配逻辑而非纯格式化）、`_resolve_deconstruction`、`write_eval_bundle`、`_resolve_expansion`、`_persona_result_to_agent`、`_persona_result_to_output`、`run_eval_pipeline`、`_run_cli`、`main` 等管道/IO 函数——它们不属于"渲染"范畴，保留在 `run_eval.py` 是合理的模块边界（管道装配 vs 纯渲染分离）。

### `scripts/lib/render_briefing.py` 导出函数真实签名（供 Phase 6.2 直接参考）

```python
def _format_reality_body(run_id: str, news) -> str: ...
def _format_errors(errors: list[dict]) -> str: ...
def _hit_heading(hit: dict[str, Any]) -> str: ...
def _format_hit_lines(hit: dict[str, Any]) -> list[str]: ...
def _agents_from_hit_sources(cand: dict[str, Any]) -> list[str]: ...
def _pseudo_hit_total(cand: dict[str, Any]) -> int: ...
def _sort_candidates_for_display(candidates: list[dict[str, Any]]) -> list[dict[str, Any]]: ...
def _candidate_heading(cand: dict[str, Any]) -> str: ...
def _candidate_auto_score_lines(cand: dict[str, Any]) -> list[str]: ...

def _candidate_copy_text(
    cand: dict[str, Any],
    copies: dict[Any, Any] | list[dict] | None,
) -> str | None: ...

def _format_candidate_block(
    cand: dict[str, Any],
    *,
    include_score: bool,
    copies: dict[Any, Any] | list[dict] | None = None,
) -> list[str]: ...

def _format_agent_markdown(
    run_id: str,
    agent_id: str,
    output,
    per_agent_entry: dict[str, Any] | None,
) -> str: ...

def _format_candidates_markdown(
    run_id: str,
    candidates: list[dict[str, Any]],
    *,
    copies: dict[Any, Any] | list[dict] | None = None,
) -> str: ...

def _format_run_index(
    run_id: str,
    errors: list[dict],
    *,
    persona_ids: list[str] | None = None,
) -> str: ...
```

关键调用说明（给 Phase 6.2）：

- `_format_candidates_markdown(run_id, candidates, copies=None)`：eval 模式不传 `copies`（保持 `None`，行为与迁移前完全一致）。Prod 模式（main.py）将来把 C1（`compose.run_review`）产出的 `review_copies` 转换为 `dict[tmdb_id, str]` 或 `list[{"tmdb_id":…, "copy":…}]` 后传入即可；`_candidate_copy_text` 已同时支持这两种形状（dict 键查找 / list 线性查找 + `entry.get("copy"/"text"/"draft")`），因为 6.2 尚未落地、`compose.run_review` 真实返回形状未在本 todo 验证，采用防御式双形状支持以避免 6.2 时二次改签名。
- `_format_run_index(run_id, errors, persona_ids=None)`：**默认值从"硬编码 4 行死链"改为"不传参数则不渲染任何 persona 行"**（详见第 4 节死链说明）。`run_eval.py` 的实际调用已改为 `persona_ids=run_persona_ids`，取自 `persona_payloads.keys()`（有的话）或 `[o.agent_id for o in outputs]`（回退）。main.py（6.2）应同样传入真实 persona_id 列表。

### 未采用计划里的组合入口函数 `render_daily_briefing(mode=..., copies=...)`

计划草案里提到的 `render_daily_briefing(news, retrieve_payload, *, review_copies=None, mode: Literal["prod","eval"]="prod", run_id="")` 组合函数**本次未实现**。原因见第 4 节"潜在影响或技术债"。

## 3. 本地验证结果 (Verification)

### 3.1 纯格式化逻辑等价性验证（主要验收方式）

由于 A0/persona pipeline 涉及真实 LLM 调用（内容有随机性），采用计划里建议的更可靠方式：复用 `output/Eval/phase6-baseline/`（2026-07-04 已保存的真实基线产物，12 persona 全部成功）里的 `reality.json` + `candidates.json` 作为固定输入，在迁移前后分别调用渲染函数比对输出字符串。

具体做法：临时脚本 `_verify_render_equiv.py`（验证后已删除）在文件内逐字复制了迁移前 `run_eval.py` 的 `_format_reality_body` / `_format_errors` / `_format_candidates_markdown`（及其依赖的 `_sort_candidates_for_display` / `_candidate_heading` / `_candidate_auto_score_lines` / `_format_candidate_block` / `_agents_from_hit_sources` / `_pseudo_hit_total`）作为 OLD 版本，用真实基线的 `reality.json`（转为 `SimpleNamespace` 模拟 `NewsItem`）和 `candidates.json` 的 `candidates` 字段驱动 OLD 与 NEW（`scripts.lib.render_briefing`）两侧渲染，`==` 比较输出字符串。

结果：

```
[PASS] reality_body
[PASS] errors
[PASS] candidates_markdown (copies=None)
FINAL: ALL PURE-FORMATTING FUNCTIONS BIT-IDENTICAL
```

`_format_run_index` 单独处理（见第 4 节，预期行为已改变，非 bug）：OLD 输出硬编码 `[[agents/A2]] [[agents/A4]] [[agents/A7]] [[agents/A1]]` 四行死链；NEW 默认（不传 `persona_ids`）不渲染任何 persona 行；NEW 传入真实基线 12 persona 目录名（`The-Caregiver` … `The-Sage`）后正确生成 12 行动态链接。此差异是本 todo 明确要求的"顺带修复"，非漂移。

### 3.2 端到端真实管线运行验证

```powershell
python scripts/run_eval.py --news-file tests/sample_news.json --run-id phase6.1-verify --personas 2 --skip-expand --force
```

运行成功（exit 0），`output/Eval/phase6.1-verify/run.md` 实际内容：

```
| [[agents/The-Innocent]] | The-Innocent |
| [[agents/The-Everyman]] | The-Everyman |
```

（而非旧的 A2/A4/A7/A1），证明新模块在真实管线中被正确调用且死链修复生效。验证完毕后已删除该临时运行目录 `output/Eval/phase6.1-verify/`。

未做"迁移前 vs 迁移后重新跑一次全量真实 LLM pipeline 再 diff 产物"这一步——因为 A0/persona 环节调用真实 LLM，两次运行的候选内容/文案本身就会有非确定性差异（与代码改动无关），这类 diff 无法证明代码等价性反而会引入噪音；3.1 的固定输入等价性验证是更可靠、已执行的方案，与计划文档"优先采用"的建议一致。

### 3.3 回归测试套件

```powershell
python -m pytest tests/ -q
```

结果：`8 failed, 269 passed, 1 skipped`。8 个失败与预期一致，全部集中在 `tests/test_copywriter_review.py`（`TestCandidateBlock` / `TestRunReview` / `TestMarkdownRendering`），失败原因是该文件内部的中文字符串断言编码问题（`AssertionError`/`AttributeError: 'ReviewCopy' object has no attribute 'copy_text'`），与 `compose.py`/`ReviewCopy` 有关，**与本次 render_briefing 迁移无关**，且失败数量（8）与任务描述中"已知既有失败"数量一致，确认无新增 regression。

`tests/test_run_eval_candidates.py`（直接从 `scripts.run_eval` import 迁移前的私有函数）全部通过，证明 re-export 机制生效。

## 4. 潜在影响或技术债 (Technical Debt & Caveats)

### run index 死链问题：真实存在，已修复

`output/Eval/phase6-baseline/run.md`（真实基线产物）证实死链问题确实存在：硬编码 `[[agents/A2]] [[agents/A4]] [[agents/A7]] [[agents/A1]]`，而该基线运行的 `personas/` 目录下实际有 12 个真实 persona（The-Hero、The-Innocent 等），`agents/` 目录下也是 12 个 `.md` 文件，指向 A2/A4/A7/A1 的四行链接在 Obsidian 里点击后目标不存在。已修复为 `_format_run_index(run_id, errors, *, persona_ids: list[str] | None = None)`，`run_eval.py` 调用时传入 `persona_payloads.keys()`（persona pipeline 跑过时）或 `[o.agent_id for o in outputs]`（回退）。

**注意默认值语义变化**：迁移前 `_format_run_index(run_id, errors)` 总是渲染四行死链；迁移后 `_format_run_index(run_id, errors)`（不传 `persona_ids`）渲染**零行** persona 链接，而不是恢复死链。这是有意选择——恢复死链没有意义，`run_eval.py` 的真实调用点已经总是传入 `persona_ids`，因此这个"空列表默认值"只在直接单测该函数、不传参数时才可见。Phase 6.2 的 main.py 若复用此函数也必须传入真实 persona_ids，否则 run 索引里会完全缺失 persona 链接段（不会退化成旧死链，但也不会隐式补全）。

### 计划里的 `render_daily_briefing(mode="prod"/"eval", copies=...)` 组合入口：未实现，理由与 6.2 对接建议

计划草案设想了一个统一入口 `render_daily_briefing(news, retrieve_payload, *, review_copies=None, mode="prod", run_id="")`，试图让 eval 和 main 共用同一个"拼出整份文档"的函数。本 todo **没有落地这个组合函数**，原因：

1. `run_eval.py` 的真实产物结构是"多个独立文件"（`reality.md` / `candidates.md` / `errors.md` / `run.md` / `agents/*.md` 各自独立写盘），而不是"一份合并的 Markdown 文档"。计划草案里的 `render_daily_briefing` 签名暗示返回单个字符串（对应 main.py 未来产出的单份 `Daily_Briefing/{date}.md`），这与 eval 模式的多文件产物结构本质不同，强行统一会让 `mode` 参数变成一个巨大的 if/else 分叉，反而降低两边的可读性和可测试性。
2. eval 侧目前没有"整份文档"的需求（Obsidian 靠 `[[wikilink]]` 互相跳转，本来就是多文件设计），若现在建一个 `render_daily_briefing` 但 eval 侧不用，只是给 main.py 单独用，那它本质上就是"main.py 专用的模板拼装函数"，不应该冒充"共享组合入口"的语义。

**给 Phase 6.2 的建议**：main.py 直接复用 `render_briefing.py` 里现成的这些细粒度函数（`_format_reality_body`、`_format_candidates_markdown(..., copies=review_copies)`、`_format_errors`），在 main.py 自己的模块里按照计划文档里描述的"Markdown 输出模板"（现实波澜 / 候选星轨 / errors / A1 oracle 附录 / 脚注）组装成单份 `Daily_Briefing/{date}.md` 字符串，不必也不建议在 `render_briefing.py` 里再造一个 `mode` 分叉的组合函数。如果 6.2 认为确有必要一个 `assemble_daily_briefing(...)` 之类的 prod-only 组合函数，可以新建在 `scripts/main.py` 或 `scripts/lib/render_briefing.py` 里作为纯 prod 用途的新函数（不带 `mode` 参数，不服务 eval），签名和位置留给 6.2 subagent 视 main.py 实际数据流决定。

### `copies` 参数槽位：已开好，形状待 6.2 定案

`_format_candidates_markdown` / `_format_candidate_block` 新增的 `copies: dict[Any, Any] | list[dict] | None = None` 参数槷位为 `None` 时行为与迁移前完全一致（已在 3.1 验证）。`_candidate_copy_text` 助手函数同时兼容 `dict[tmdb_id, str]`、`dict[tmdb_id, {"copy"/"text"/"draft": str}]`、`list[{"tmdb_id":…, "copy"/"text"/"draft":…}]` 三种形状，因为 `compose.run_review` 的真实返回结构（`ReviewCopy` dataclass，参见 `test_copywriter_review.py` 里 `ReviewCopy` 对象但字段名疑似正在变动中，测试文件里出现了 `copy_text` 属性缺失的既有失败）在本 todo 未被读取验证。**Phase 6.2 对接时务必先读取 `scripts/compose.py` 里 `ReviewCopy`/`ReviewResult` 的真实字段定义**，确认 tmdb_id 和文案字段名后，可能需要在调用处做一次 `{c.tmdb_id: c.<真实文案字段名> for c in result.review_copies}` 的转换，再传给 `copies=`。

### `_PSEUDO_ORDER` 常量的历史包袱

`render_briefing.py` 里保留了 `_PSEUDO_ORDER = RUN_ORDER`（即 `("A2","A4","A7","A1")`，来自已 DEAD FLOW 的 `scripts/agents.py`），用于 `_agents_from_hit_sources` 的排序优先级和 `run_eval.py` 里 `_agent_outputs_by_id` 排序（后者仍留在 `run_eval.py`，未迁移）。当前 12-persona 生产管线的 `persona_id`（如 `The-Hero`）不在这个元组里，排序会落到 `order.get(aid, 99)` 兜底（按 hit_sources 出现顺序）。这是**迁移前既有行为**，本 todo 未改变、仅原样迁移并加注释说明；是否要把这个排序键换成真正对齐 12-persona 的顺序，属于独立的技术债，建议留给未来单独 todo（不在本次范围内处理，未做改动）。

### 对 6.2 有帮助的关键发现（管线数据流）

- `run_eval.py` 的真实执行顺序（`_run_cli` → `run_eval_pipeline`）：`load_news_from_file` → `_resolve_deconstruction`（A0，`run_deconstruct(news, provider=...)` 或读取缓存 `facts.json`）→ `run_eval_pipeline(news, provider=, deconstruction=, run_dir=, run_options=)` 内部依次：`_resolve_expansion(deconstruction, run_dir, provider=)`（P-Expand，可 `--skip-expand` 跳过）→ 遍历 `list_persona_ids()`（来自 `scripts/rewrite.py`，读 `docs/SSOT/personas-12.md`，返回 12 个 `The-Xxx` persona_id）逐个调用 `run_persona_pipeline(persona_id, deconstruction, provider=, expansion=)` → 收集 `outputs`/`agents_list`/`persona_payloads` → `retrieve_from_agents(agents_list, errors, top_k=options.judge_topk)`（`scripts/retrieve.py`）。
- `retrieve_from_agents` 返回的 dict 顶层键（从 `scripts/retrieve.py` 第 1154-1174 行实测）：`per_agent`、`candidates`、`human_candidates`、`audit_pool`、`funnel`（即 `funnel["meta"]`，漏斗统计元信息）、`a1_oracle`、`oracle_comparison`、`divergence`、`meta`（`meta` 里嵌套展开了 `funnel["meta"]` 的字段，还有 `query_count`/`raw_hit_count`/`candidate_count`/`max_candidates`/`human_budget`/`quality_floor`/`oracle_query_count`/`judge_query_count`）。`run_eval.py` 目前只用了 `retrieve_result.get("candidates", [])` 和 `retrieve_result.get("per_agent", [])`；`human_candidates`/`audit_pool`/`funnel`/`a1_oracle`/`oracle_comparison`/`divergence`/`meta` 均未被 `run_eval.py` 使用，说明计划里提到的 `render_funnel`/`render_oracle_appendix`/`render_meta_footer` 目标函数**在当前代码里根本不存在对应的调用点**——`run_eval.py` 里没有渲染 funnel/oracle/meta 的逻辑，因此本 todo 没有迁移这三类函数（迁移前不存在，不能凭空发明签名）。Phase 6.2 若要在 main.py 里渲染 A1 oracle 附录/funnel 统计，需要**新建**这些渲染函数（可以放进 `render_briefing.py`），数据源就是 `retrieve_result["a1_oracle"]`、`retrieve_result["oracle_comparison"]`、`retrieve_result["funnel"]`/`retrieve_result["meta"]`，字段结构定义参见 `scripts/retrieve.py` 里 `_build_a1_oracle_payload`（第 421 行起）和 `apply_candidate_funnel`（第 723 行起）。
- candidate dict 的真实字段（从 `_format_candidate_block` 消费的字段推断，均已在 render_briefing.py 里保留）：`title`、`release_year`、`tmdb_id`、`quality_candidate`、`quality_reason`、`convergence_persona_count`/`persona_count`、`convergent_score`、`match_diagnostics`（含 `surface_match`/`event_match`/`persona_semantic_match`/`search_unit_kinds`/`center_dimensions`）、`also_baseline`、`similarity`、`genres`、`language`、`overview`、`movie_url`、`hit_sources`（list，每项含 `agent_id`/`pseudo_id`/`fragments`/`similarity`/`search_unit_kind`/`center_element`）。`movie_url` 直接来自 retrieve 输出，main.py 不应手拼（符合计划里的"关键约束"）。
- C1 入口 `compose.run_review(retrieve, news, *, provider=None, judge_index=None, run_id="", min_judge=None, prompts_dir=None, llm_call=None) -> ReviewResult`（`scripts/compose.py` 第 744 行起），C2 入口 `compose.run_publish(candidate, news, *, provider=None, judge=None, prompts_dir=None, llm_call=None) -> dict[str, Any]`（第 404 行起）。两者均在本 todo 范围外未被读取内部实现，6.2 需自行确认 `ReviewResult.review_copies` 里每个 `ReviewCopy` 的真实字段名（`test_copywriter_review.py` 显示测试期望 `copy_text` 属性但当前实测该属性不存在——这是既有失败，6.2 对接时需要先解决或绕开）。