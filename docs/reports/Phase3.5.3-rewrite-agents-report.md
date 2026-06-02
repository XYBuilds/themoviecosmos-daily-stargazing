# Phase 3.5.3 - 改写编剧链 交付报告

## 分支继承

- **开发分支**：`feat/phase3.5-rewrite-agents`
- **检出来源**：`feat/phase3.5-deconstruct-agent`（3.5.2 已开发、PR 未合并入 `main`）

## 1. 改动范围 (Scope)

| 区域 | 文件 |
|------|------|
| 编剧 prompts | `prompts/A1_reality_recorder.md`, `A2_sociologist.md`, `A4_mythologist.md`, `A7_chaos_theorist.md` |
| 共享契约 | `prompts/_shared/deentification_rules.md`, `multi_pseudo_output_contract.md`（新建） |
| 运行时 | `scripts/agents.py`, `scripts/run_eval.py` |
| 离线夹具 / 测试 | `tests/fixtures/01-grid-outage-deconstructed.json`, `india-heatwave-deconstructed.json`, `tests/test_agents_p35.py` |
| 计划 | `.cursor/plans/Phase3.5-pivot-reality-deconstruction.plan.md` |

无新增 Python 依赖。

## 2. 技术实现 (Implementation)

- **输入**：`--deconstruction-file` 加载 A0 产物（或 raw `deconstruction` 对象）；`annotate_fragment_ids()` 为 `why`/`how`/`result` 注入稳定 id。
- **Prompt**：`{{deconstruction_json}}` 替代原 `{{title}}`/`{{description}}` 新闻占位；每 agent 产 **3** 段 pseudo（`p1`–`p3`），`source.fragments` 溯源。
- **输出 JSON**：`agents[].pseudos: [{id, text, source, warnings}]`；保留 `text` = 首段 pseudo（供 3.5.4 前 `retrieve.py` 兼容）。
- **LLM**：`response_format=json_object`（不支持时回退）；解析 + 碎片合法性 / `how-*` 连续性校验。
- **de-entification**：规则 2/4 放宽为默认抽象、承重可保留专名/数字（ADR-0002）；启发式不再对普通人名大写报警。
- **run_eval**：缺 `reality-deconstructed.json` 时自动跑 A0；Eval 目录双写解构产物；agent markdown 展示 3 pseudos。

## 3. 本地验证结果 (Verification)

```bash
python tests/test_agents_p35.py
python -m py_compile scripts/agents.py scripts/run_eval.py
```

**LLM（需 `.env`）**

```bash
python scripts/agents.py \
  --deconstruction-file tests/fixtures/01-grid-outage-deconstructed.json \
  --news-file tests/eval_news/01-grid-outage.json \
  --agents A1 --out output/test-p35-agents-a1.json

python scripts/agents.py \
  --deconstruction-file tests/fixtures/01-grid-outage-deconstructed.json \
  --agents A2 --out output/test-p35-agents-a2-retry.json

python scripts/agents.py \
  --deconstruction-file tests/fixtures/india-heatwave-deconstructed.json \
  --out output/test-p35-agents-all-india.json
```

| 运行 | 结果 |
|------|------|
| A1 @ grid-outage | 3 pseudos，含 `Visayan Islands` / `950 megawatts` 等承重专名与数字 |
| A2 @ grid-outage（json_object 后） | 3 pseudos，明显权力/结构镜头（非事实换说法） |
| 全 agent @ india | A2/A7 成功 3 pseudos；A1/A4 偶发 `fragments` 误填 `when/where/who` → 已收紧 prompt 契约 |

## 4. 潜在影响或技术债 (Technical Debt & Caveats)

- **3.5.4 阻塞项**：`retrieve.py` 仍只检索每 agent 的 legacy `text`（首段 pseudo），未遍历 `pseudos` × Top-2，候选爆炸控制未做。
- **JSON 遵从**：创意 agent 在无 `response_format` 时可能返回纯文本；已用 `json_object` 缓解，偶发仍需重试。
- **短文本**：A1 常触发 `short_output`（<40 词），属模型未吃满 60–120 词，可后续在 prompt 或后处理加压。
- **run_eval 全链路**：未在本 TODO 跑通 retrieve（依赖 3.5.4）；可用 `run_eval.py --deconstruction-file` 跳过 A0。

## 交给 3.5.4

- 扩展 `retrieve_from_agents` 遍历 `pseudos`，每段 Top-2，`tmdb_id` 聚合 + `source` 挂候选。
- 移除或废弃顶层 `agents[].text` 单路检索。
