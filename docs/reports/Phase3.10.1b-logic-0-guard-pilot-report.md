# Phase 3.10.1b - Logic 0-guard pilot 交付报告

## 1. 改动范围 (Scope)

- `prompts/_shared/resonance_definition_v2.md` — Axis 2 logic 0-guard 措辞（无关新闻仍成立 → 底层逻辑=NO）
- `scripts/llm_judge.py` — `_JUDGE_SYSTEM` / `_JUDGE_RUBRIC` 同步 logic 0-guard + prefer 0
- `docs/eval-the-bet.md` — §4 双轴 rubric 同步 logic 0-guard 一句
- `scripts/run_phase39_judge_batch.py` — `--run-ids` 子集 CLI、`--prompt-version` 默认 `3.10.1b-logic-0-guard`
- `scripts/judge_batch_parallel.py` — 新增并行 (news, movie) pair scorer
- `tests/test_llm_judge.py` — `test_logic_zero_guard_in_rubric_and_system`
- `output/Eval/phase3.10-visible/llm-judge-scores-rerun-05-06.json` / `.md` / `.json.bak` — pilot 重打分输出
- `output/Eval/phase3.10-visible/judge-rerun-05-06-comparison.md` — before/after 对比与 2→0/1 回归清单
- `output/Eval/phase3.10-visible/high-hit-score-review.md` — 可见集 judge 注入（含 pilot rationale）
- `.cursor/plans/Phase3.10-logic-resonance-and-judge-prescreen.plan.md` — p310-1b 标 complete
- 新增/删除的依赖包：无

**分支：** `feat/phase3.10.1b-logic-0-guard-pilot`（基于 `main` @ 3.10.6 merge，`8792ae9`）

## 2. 技术实现 (Implementation)

### Logic 0-guard rubric patch

在 3.10.1 双轴 rubric 上，Axis 2（底层逻辑）追加 **logic 0-guard**：

- Judge 须写出 bidirectional `X under constraint Z drives Y` 因果反测句；
- 若该句对「同一电影 + 无关新闻」仍字面成立 → 底层逻辑 = NO；
- 不确定 0 vs 1 时 **prefer 0**。

权威源 `resonance_definition_v2.md` 与 `llm_judge.py` 逐字传播；`prompt_version` 升为 `3.10.1b-logic-0-guard`。

### `--run-ids` CLI + pilot rerun

```text
python scripts/run_phase39_judge_batch.py \
  --eval-dir output/Eval/phase3.10-visible \
  --run-ids 05-climate-disaster,06-tech-monopoly \
  --out-json output/Eval/phase3.10-visible/llm-judge-scores-rerun-05-06.json \
  --fresh
```

Pilot 仅重跑 holdout runs 05/06（obs-style visible 目录），保留 `.bak` 作 holdout baseline 对比。

### Pilot 分布变化（judge 0/1/2）

| run | before | after |
| --- | --- | --- |
| 05-climate-disaster | {0: 3, 1: 7, 2: 7} | {0: 9, 1: 4, 2: 4} |
| 06-tech-monopoly | {0: 4, 1: 15} | {0: 17, 1: 2} |

Transition 摘要：1→0 **18**；2→0 **1**；2→1 **3**；2→2 **3**。

**4 例 prior judge=2 回归**（待 spot-check，未改 human 标签）：

- Raining Cats and Frogs (05): 2→1
- Water Wrackets (05): 2→0
- Tidal Wave (05): 2→1
- Dry (2022) (05): 2→1

## 3. 本地验证结果 (Verification)

```text
python -m unittest tests.test_llm_judge -v
# → Ran 25 tests in ... OK
```

Pilot 对比报告：`output/Eval/phase3.10-visible/judge-rerun-05-06-comparison.md`

User approved pilot after reviewing comparison → cleared for merge; **full holdout rerun 不在本 PR 范围**。

## 4. 潜在影响或技术债 (Technical Debt & Caveats)

- **全量 holdout rerun 待做** — 3.10.7 须在用户 spot-check 4 例 2→0/1 回归后，用同一 `prompt_version` 对 05–10 一次性重打分。
- **混合 prompt_version corpus** — 直至全量 rerun 完成，`phase3.10` holdout JSON 仍混有 3.10.6 冻结版与 3.10.1b pilot 子集；合并分析前须统一版本或标注来源。
- **logic 0-guard 收紧过猛风险** — pilot 大量 1→0（尤其 06 泛化 regulatory 句）；若 spot-check 认为过宽，可微调 wording（comparison 报告已建议）。
- **human 标签未动** — `high-hit-score-review.md` 中 human 分保持鲜标；仅 judge 列更新。

**Go/No-Go:** User approved pilot → merged; proceed to **3.10.7** holdout prescreen when ready for full rerun.
