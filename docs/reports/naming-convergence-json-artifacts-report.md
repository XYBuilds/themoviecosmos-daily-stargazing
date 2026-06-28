# 命名收敛重构 #1（JSON 产物改名 · facts / bridges / candidates）交付报告

## 1. 改动范围 (Scope)

本轮把管线三条 JSON 产物的默认文件名收敛为规范名，写点与读取方一并更新。

**三条改名映射：**
- `reality-deconstructed.json` / `.md` → `facts.json` / `.md`（A0 解构产物）
- `reality-expanded.json` → `bridges.json`（P-Expand 客观扩展产物）
- `retrieve.json` → `candidates.json`（召回候选池产物）

**14 个脚本（scripts/，共 +59/-59，纯字符串改名，无逻辑变更）：**
- `extract.py`、`expand.py`、`agents.py`、`rewrite.py`（写点 / 描述 / CLI help）
- `compose.py`、`score_eval_candidates.py`、`verify_phase312_equivalence.py`、`extract_multi_agent_hits.py`、`eval/persona_batch_lib.py`（candidates 读取方）
- `run_eval.py`、`run_persona_pilot.py`、`run_persona_batch.py`、`run_phase38_batch.py`、`run_phase38_eval.py`（写点 + 读取方，含多条产物名）

**3 个测试夹具（tests/，纯 rename，0 增删）：**
- `tests/eval_fixtures/score_eval_review/mini-batch/01-alpha/retrieve.json → candidates.json`
- `tests/eval_fixtures/score_eval_review/mini-batch/02-beta/retrieve.json → candidates.json`
- `tests/eval_fixtures/score_eval_review/neutral-only-batch/03-neutral-only/retrieve.json → candidates.json`

无新增 / 删除依赖。

## 2. 技术实现 (Implementation)

**逐条映射的写点与读取方：**
- **facts**：`extract.py` 的 `write_outputs` 落 `facts.json` + `facts.md`；`run_eval.py` 的 `write_eval_bundle` 与缓存解析、`run_persona_batch.py` / `run_phase38_eval.py` / `run_phase38_batch.py` 的解构读取与完成判定、`agents.py` / `rewrite.py` 的 CLI help 描述同步改名。
- **bridges**：`expand.py` 的 `write_outputs` 落 `bridges.json`，并更新内嵌 P-Expand 契约描述；`run_persona_batch.py` 的 `_load_expansion_from_run`、`run_phase38_eval.py` 的扩展产物读取同步改名。
- **candidates**：`run_eval.py` / `run_persona_pilot.py` / `run_persona_batch.py` / `run_phase38_*` 的召回结果写点改为 `candidates.json`；`compose.py`（`--retrieve-json` 喂入的候选池）、`score_eval_candidates.py`、`verify_phase312_equivalence.py`、`extract_multi_agent_hits.py`、`persona_batch_lib.py` 的读取方与文档串同步改名。

**为何 fixture 跟随改名**：`score_eval_review` 下的 fixture 是**活测试夹具**，被 `score_eval_candidates` 相关测试按默认产物名 `candidates.json` 扫描读取，不是冻结归档。产物默认名改了，活夹具必须跟随，否则测试按新名找不到文件而失败。因此随代码同改名，保持测试与生产口径一致。

**为何 phase3.6 归档保留旧名**：phase3.6 是已冻结的历史评测归档（`output/Eval/phase3.6/`），按约定「归档不回改」。`run_persona_batch.py` 的 `_copy_phase38_static` 是 phase3.8 静态拷贝来源，已随本轮改为新名；而 phase3.6 静态读取路径有意保留旧名 `reality-deconstructed.json`，不在本轮触碰——这是对冻结基线的正确保护，避免破坏历史可复现性。

**提交粒度选择**：原计划按产物拆 3 个代码 commit，但 `run_eval.py` / `run_persona_batch.py` / `run_phase38_eval.py` / `run_phase38_batch.py` 单文件内同时含多条产物改名（facts + bridges + candidates 交叉），无法干净拆到单一产物 commit。按「正确性优先于 commit 粒度」原则，14 个脚本合并为**一个**代码 commit（`refactor(pipeline): pNC5-rename-json-artifacts-facts-bridges-candidates`），fixture rename 单独一个 commit（`test(eval): pNC5-rename-fixture-retrieve-to-candidates-json`），避免给混合文件贴单一产物的误导性标签。

## 3. 本地验证结果 (Verification)

- **全量测试（提交前）**：`python -m pytest tests/ -q` → **228 passed / 1 skipped / 0 failed**。
- **全量测试（提交后）**：同命令复跑 → **228 passed / 1 skipped / 0 failed**，确认提交未遗漏文件。
- **golden 守护**：用 golden 留档输入（`output/Eval/phase3.11/full-batch-20260613-3117/01-grid-outage/retrieve.json` + `llm-judge-scores-thinking-enabled.json`，归档保留旧名不受默认产物名改动影响）经 `--retrieve-json` 显式喂入，跑 `scripts/compose.py --stage review --run-id 01-grid-outage`，与 `docs/temp/golden/copy_review.golden.json` 比对确定性字段：
  - 顶层 key 集、`filter` / `errors` 一致；
  - 候选块数 = **5 kept / 14 dropped**（与基准一致）；
  - 每条 `tmdb_id`（33495 / 58770 / 139329 / 429918 / 475946）、`triggered_by`、`center_dimensions`、`movie_url` 及 key 集**逐字一致**；
  - **无 `a1_oracle` / `oracle` 泄漏**。
  - 结论：**golden 端到端比对通过**，改名未破坏 retrieve→compose 链路产出。
- **import 冒烟**：`scripts.run_eval` / `scripts.compose` / `scripts.retrieve` / `scripts.rewrite` 均成功导入。

## 4. 潜在影响或技术债 (Technical Debt & Caveats)

- **Stage 4（queries.json 物化）本轮未做**：按用户决定单开一轮，与 `main.py` 主链组装一起规划，不在本轮范围。
- **文档同步单开一轮**：`docs/SSOT/`、`CONTEXT.md` 内仍可能引用旧产物名，本轮未动，留待文档同步轮次统一收敛。
- **历史归档保留旧名未回改**：`output/Eval/`（含 phase3.6 / phase3.11 等冻结基线）按约定保留旧名 `retrieve.json` / `reality-deconstructed.json` 等，未回改；phase3.6 静态读取路径在代码侧也有意保留旧名。
- **CLI 参数名保留未改**：`--retrieve-json`、`--deconstruction-file` 等参数名本轮保留未改，仅改默认产物文件名与 help 文本，避免破坏既有调用脚本 / golden 命令。
- **commit 粒度**：因混合文件无法干净拆分，代码改名合并为单 commit（详见第 2 节），与原计划「按产物 3 个 commit」有出入，属正确性优先的有意选择。