# Phase 3.5 - 现实解构 agent (3.5.2) 交付报告

## 1. 改动范围 (Scope)

- `prompts/A0_reality_deconstructor.md` — A0 身份、铁律、印度热浪 few-shot、新闻占位符注入
- `scripts/deconstruct.py` — CLI、MiMo 2.5 Pro（`MIMO_MODEL_PRO` 优先）、JSON 抽取/校验、双写产物
- `.cursor/plans/Phase3.5-pivot-reality-deconstruction.plan.md` — 3.5.1 / 3.5.2 todo 标 complete
- 无新增 Python 依赖

**分支：** `feat/phase3.5-deconstruct-agent`（自 `main` 检出；`main` 已含 3.5.1 契约 `docs/SSOT/reality-deconstruction-contract.md`）

## 2. 技术实现 (Implementation)

- **Prompt**：整份 `A0_reality_deconstructor.md` 作为 user message（与 Phase 1 agents 相同模式），替换 `{{title}}` / `{{description}}` / `{{pub_time}}` / `{{source_name}}`。
- **LLM**：`DEFAULT_LLM_PROVIDER`（默认 mimo）；mimo 时优先 `MIMO_MODEL_PRO`，否则 `MIMO_MODEL`。
- **解析**：支持裸 JSON 或 markdown fence；失败记入 `errors[].type=parse_error`。
- **校验**：禁止 `skeleton` / `load_bearing` / `seeds` / `共振类型` 等键；`when.*` / `where.scene_archetype` / `who.role_in_event` 等必须为 list；主观措辞启发式 → `validation_warnings`（不阻断）。
- **输出契约**（`reality-deconstructed.json`）：`news` + `deconstruction` + `errors` + `validation_warnings` + provider/model 元数据。
- **人类视图**：`reality-deconstructed.md`（Anchor / When / Where / Who / Why·How·Result 分节，Obsidian 可扫）。
- **CLI**：`python scripts/deconstruct.py --news-file <json> [--run-id] [--out-dir] [--provider]`

## 3. 本地验证结果 (Verification)

```text
python scripts/deconstruct.py --news-file tests/eval_news/01-grid-outage.json --run-id 01-grid-outage
python scripts/deconstruct.py --news-file tests/eval_news/05-climate-disaster.json --run-id 05-climate-disaster
python scripts/deconstruct.py --news-file tests/eval_news/04-celebrity-scandal.json --run-id 04-celebrity-scandal
```

| 样本 | exit | `errors` | 契约校验 | 禁止字段 |
|------|------|----------|----------|----------|
| 01-grid-outage | 0 | 0 | pass | none |
| 05-climate-disaster | 0 | 0 | pass | none |
| 04-celebrity-scandal | 0 | 0 | pass | none |

产物目录：`output/deconstruct/{run-id}/`（未纳入 git；本地验证用）。

肉眼抽查：三份 JSON 无 skeleton/load_bearing/共振类型；`scene_archetype` / `role_in_event` 均为数组；因果与专名保留，未出现权力/反讽框定类字段。

## 4. 潜在影响或技术债 (Technical Debt & Caveats)

- **3.5.3 依赖**：`agents.py` 需改为读 `reality-deconstructed.json` 的 `deconstruction` 字段，并扩展为多段 `pseudos`；`run_eval.py` 宜在管线中插入 deconstruct 步骤。
- **校验为 MVP**：主观措辞仅 warning；非法 JSON 仍 exit 0（与 agents errors 策略一致）。
- **语言混排**：模型对英文新闻有时输出中英混排标签（可接受于 MVP，后续可在 prompt 约束或后处理）。
- **未合并 PR**：待 review 后 merge commit 入 `main`。
