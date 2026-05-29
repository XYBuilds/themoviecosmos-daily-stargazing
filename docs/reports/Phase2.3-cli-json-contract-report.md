# Phase 2.3 - CLI 与 JSON 契约 交付报告

## 1. 改动范围 (Scope)

- `scripts/retrieve.py` — CLI、`from_agents_json()` 公共 API
- `README.md` — MVP 步骤 3 联调命令
- `.cursor/plans/Phase2-retrieve-candidates.plan.md` — Todo 2.1–2.3 complete

## 2. 技术实现 (Implementation)

- CLI：`--agents-json`、`--out`、`--top-k`、`--pseudo` + `--agent-id`、`--help`
- 跳过 `errors[]` 中 agent 与空 `text`
- 输出契约：`per_agent`、`candidates`、`divergence`
- `from_agents_json(path|dict)` 供 Phase 3 / `main.py` 调用

## 3. 本地验证结果 (Verification)

```powershell
python scripts/retrieve.py --agents-json output/phase1_agents.json --out output/phase2_retrieve.json
python -c "import json; d=json.load(open('output/phase2_retrieve.json')); print(len(d['candidates']), 'candidates')"
```

- exit 0；`8 candidates`
- 分支：`feat/phase2.1-retrieve-core`（自 `main` 检出）

## 4. 潜在影响或技术债 (Technical Debt & Caveats)

- Phase 2 整体验收仍留一项人工：候选与 pseudo 表层相关性（计划 checklist）
- `output/phase2_retrieve.json` 未纳入 git（运行时产物）
