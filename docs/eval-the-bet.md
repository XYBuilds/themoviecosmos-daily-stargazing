# 验证闸门 · The Bet（Phase 3）

> **目的**：在投入 Phase 4 中文文案（C1/C2）之前，用 **N=10** 条手挑新闻验证「多 Agent 伪剧情 → 向量召回 → 人类结构性共振评分」这条链是否值得继续。
>
> **总编角色**：你是唯一裁决者——手挑新闻、填 **共振分 0/1/2**、记录闸门结论。系统不做自动打分。

详细术语见 [`CONTEXT.md`](../CONTEXT.md)；闸门指标定义与 Phase 3 plan 一致（[`.cursor/plans/Phase3-validation-gate-the-bet.plan.md`](../.cursor/plans/Phase3-validation-gate-the-bet.plan.md)）。

---

## 1. 前置条件

在启动本评测前，确认以下 Phase 已验收：

| Phase | 验收要点 |
|-------|----------|
| **Phase 0** | `.env` 已配置 LLM；`python scripts/smoke_llm.py` 通过 |
| **Phase 1** | `python scripts/agents.py --news-file tests/sample_news.json` 产出 4 段英文 pseudo（A2/A4/A7 + 基线 A1） |
| **Phase 2** | 全量索引已构建（`data/index/embeddings.npy` + `meta.parquet`）；`retrieve.py` 可召回候选 |

**环境**：从仓库根目录运行；虚拟环境已激活；首次 `run_eval` 会加载 sentence-transformers 模型与 59,341 行索引（注意内存与首次下载耗时）。

---

## 2. 准备 N=10 条新闻 JSON

评测批次固定 **N=10**。每条新闻一个 JSON 文件，格式与 `tests/sample_news.json` 相同：

```json
{
  "title": "...",
  "description": "...",
  "pub_time": "2026-05-29T12:00:00Z",
  "source_name": "Example Wire",
  "url": "https://example.com/article/1"
}
```

**必填**：`title`、`description`。**推荐**：`pub_time`、`source_name`、`url`（写入评测 Markdown 元信息）。

### 新闻来源

| 阶段 | 做法 |
|------|------|
| **评测早期**（Phase 5 RSS 未接） | 总编手写或改编 10 条 JSON，放入 `tests/eval_news/`（见该目录 README 占位文件名） |
| **Phase 5 之后** | 从 `fetch_news.py` 抓取的 RSS 池中**手挑** 10 条，导出为上述 JSON 格式 |

**挑选原则（建议，非硬规则）**：

- 题材多样（政治、灾难、商业、文化等），避免 10 条全是同一类头条
- 含足够「关联潜力」（权力博弈、命运转折、主题张力等可共振骨架），而非纯数据通报
- 避免过于本地化专名堆叠——agents 会去实体化，但极端生僻事件可解释性较差

### Phase 3.7 · 观察集 / 留出集（N=10）

与 [ADR-0004](adr/0004-persona-emotional-diffusion.md) §评测留出集纪律一致（`run_id` 见 `tests/eval_news/batch-manifest.json`）：

| 集合 | news | 用途 |
| --- | --- | --- |
| **观察集** | `01`–`04` | 开发、pilot、契约迭代；共振分可选 |
| **留出集** | `05`–`10` | **3.7.4/3.7.5 闸门与 P-Abstain 仅在此填分**；多轮迭代时每轮至少评 **2 条**留出新闻 |

Phase 3.5/3.6 历史批次仍用全 N=10 填分；自 Phase 3.7 起闸门统计须区分集合，勿在观察集上自证 persona 增量。

---

## 3. 评测循环（10 次）

对每条新闻执行一次 `run_eval`，在 `output/Eval/{run_id}/` 下生成一组文档（见 §3.3）。

### 3.1 运行命令

```powershell
# 单条（默认 output/Eval/{run_id}/）
python scripts/run_eval.py --news-file tests/eval_news/01-grid-outage.json

# 指定 run_id（与 eval_news 文件名对齐）
python scripts/run_eval.py --news-file tests/eval_news/01-grid-outage.json --run-id 01-grid-outage

# 指定输出目录
python scripts/run_eval.py --news-file tests/sample_news.json --out output/Eval/sample-run

# 切换 LLM 提供商（默认读 .env 的 DEFAULT_LLM_PROVIDER）
python scripts/run_eval.py --news-file tests/sample_news.json --provider deepseek
```

**CLI 参数（`scripts/run_eval.py`）**：

| 参数 | 必填 | 说明 |
|------|------|------|
| `--news-file` | 是 | 新闻 JSON 路径 |
| `--run-id` | 否 | 评测 slug；默认从 title 生成 ASCII slug，失败则用 UTC 时间戳 |
| `--out` | 否 | 输出目录；默认 `output/Eval/{run_id}/` |
| `--provider` | 否 | `mimo` 或 `deepseek` |

**管线**：`agents.run_all` → `retrieve.from_agents` → 写入 Eval 目录（与正式 `Daily_Briefing` 分离）。

### 3.3 产出目录结构

```text
output/Eval/{run_id}/
├── run.md                    # 索引（Obsidian 入口）
├── reality.json              # 新闻快照
├── reality.md                # 现实波澜
├── reality-deconstructed.json / .md   # Phase 3.5 解构产物
├── retrieve.json             # 完整 retrieve（含 hit_sources）
├── errors.md
├── candidates.md             # 聚合候选 + 共振分/类型（总编填分）
└── agents/
    ├── A2.md        # 伪剧情 + 本视角 Top-K
    ├── A4.md
    ├── A7.md
    └── A1.md        # 基线
```

**成本提示**：每条新闻 ≈ **1 次解构 + 4×3 段 pseudo** LLM + 多段向量检索；10 条 ≈ 10× 上述开销。

### 3.1.1 Phase 3.6.5 并行批量（`run_eval_batch.ps1`）

Phase 3.6 重跑须写入 **`output/Eval/phase3.6/{run_id}/`**（勿用默认 `output/Eval/{run_id}/`，以免覆盖 3.5.6 对照）。推荐用批量脚本（PowerShell 7+）：

```powershell
pwsh -NoProfile -File scripts/run_eval_batch.ps1 -WhatIf   # 预览（需 PowerShell 7+）
pwsh -NoProfile -File scripts/run_eval_batch.ps1             # 正式 N=10
```

| 项 | 说明 |
| --- | --- |
| 并行度 | `ForEach-Object -Parallel`，默认 **ThrottleLimit 3** |
| 抖动 | 每任务开始前随机 sleep **5–15s**（减轻 429） |
| 日志 | `output/Eval/phase3.6/_logs/{run_id}.log` |
| 命中分 | 仅当 **10/10 成功** 后自动：`score_eval_candidates.py --dir output/Eval/phase3.6 --review-out output/Eval/phase3.6/high-hit-score-review.md` |
| 重试 | `-RetryFailed`：读 `_logs/batch-summary.json` 中失败项，**K=4**；或 `-RunIds 02-corporate-layoff,05-climate-disaster` |

**环境**：`.env`（`DEFAULT_LLM_PROVIDER`、对应 API key）、`python scripts/smoke_llm.py`、Phase 2 索引就绪（§1）。详见 `output/Eval/README.md`。

### 3.4 Pseudo 命中分（审阅辅助，非闸门）

闸门前可用脚本把 `retrieve.json` 的碎片命中写成 `candidates.md` 内的 **命中分** / **pseudo命中分合计**，并生成全批次 `high-hit-score-review.md`（默认阈值 ≥5）：

```powershell
python scripts/score_eval_candidates.py
```

详见 `output/Eval/README.md`。命中分**不替代** `共振分`；`summarize_eval.py` 仍只读共振分。Phase 3.5 书面结论见 `output/Eval/GATE_RESULT.md`（当前 **GATE_FAIL · 发布**）。

### 3.2 在 Obsidian 中填分

1. 用 Obsidian 打开 `output/Eval/{run_id}/`（从 **`run.md`** 或 **`candidates.md`** 进入）。
2. 通读：**`reality.md`** → **`agents/A2.md`** … **`agents/A1.md`** → **`candidates.md`**。
3. 仅在 **`candidates.md`** 中，对每个 `### 电影标题 (年份) [A2, A4]` 候选块，找到：

   ```markdown
   - **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
   ```

4. 将占位改为 **`0`**、**`1`** 或 **`2`**（保留该行格式，例如 `- **共振分**: 2`）。

**阅读顺序建议**：

- 先看创作视角 pseudo（A2/A4/A7），再看 A1 `[baseline]` 对照
- 点开 **跳转** 链接或 TMDB overview，判断的是「新闻骨架 ↔ 电影骨架」，不是字面题材
- `[A2, A4]` 表示多创作视角撞车（中性展示）；`[baseline only]` / `also_baseline: true` 表示仅基线命中

重复本步骤，直到 **10 个** `{run_id}/candidates.md` 全部填完共振分。

---

## 4. 共振分 Rubric（0 / 1 / 2）

共振有**两层**，本 rubric **同时拥抱**二者（与 [`CONTEXT.md`](../CONTEXT.md) 中 **共振 (Resonance)** 一致）。**验收目标统一为「关联 / 共振」**——不单独追求讽刺、反讽或荒诞作为产品指标；后者仅可作为底层逻辑或双重共振的**子类**出现。

- **第一轴 · 表层元素 (Surface)**：候选与新闻共享**具体、可命名且承重**的元素——地点 / 人物类型 / 事件类型 / 设定 / 题材。关键在「**承重**」：换一条无关新闻**无法**复用该元素。**抽象权力角色配对（权威↔受害者、领袖↔团队）不算表层元素，归底层逻辑轴**。
- **第二轴 · 底层逻辑 (Underlying logic)**：新闻与电影**实例化同一个因果-赌注引擎**，且该引擎在 **POV / 尺度变换下不变**——一句 **「X 在约束 Z 下驱动 Y」**（如*系统性稀缺把普通人逼入求生*），机构尺度↔个人尺度也算。**可证伪反测**：写不出一句两边都成立的因果句 ⇒ 不算逻辑共振，退回 0/1。**逻辑 0 分守门**：若该因果句对无关新闻配上同一部电影仍字面成立 ⇒ 第二轴 = 无 ⇒ 不可给「深层共振（仅逻辑，无表层）」。**0/1 不确定时优先 0**。

按两轴定分（**先判承重表层元素，再判 POV/尺度不变因果引擎**）：

| 表层元素 | 底层逻辑 | 分 | 共振类型 |
|---|---|---|---|
| 无 | 否 | **0** | 无共振（偶然词面重叠） |
| 无 | 是 | **1** | 深层共振（仅逻辑，无表层） |
| 有 | 否 | **1** | 表层沾边 |
| 有 | 是 | **2** | 强共振（表层 + 逻辑） |

> **0 分守门**：别让「拥抱表层」滑成「什么都给分」。**纯偶然、非承重的表层重叠仍判 0**——判据不变：「换一条无关新闻同样能解释这部片」= 0。

**共振类型标注（总编打分时填，最小体温计）**：`共振分` 与 `共振类型` **必须**按上表一致；打 1 / 2 分时标对应类型，0 分留空。用于诊断「创作视角的强共振 vs 仅逻辑 / 仅表层」（直接喂 §5.1 第 2 条；见 ADR-0002 / ADR-0007）。LLM judge 同样输出 `score` + `resonance_type` + `causal_test`（因果反测句），校验同一矩阵。

**可选子标签 · POV变换**（ADR-0007 D7）：仅当 `共振分 = 2` 时可标 `是`，表示该强共振**靠视角/尺度变换才看得出来**（机构新闻 ↔ 个人电影等 Gap A 模式）。不改变 2×2 `共振类型`；judge JSON 字段为 `pov_transform: true|false`。

```markdown
- **共振分**: 2
- **共振类型**: 强共振（表层 + 逻辑）    <!-- 0 分留空；1→深层共振（仅逻辑，无表层）|表层沾边；2→强共振（表层 + 逻辑） -->
- **POV变换**: 是    <!-- 可选；仅 score 2 -->
```

**归属规则**（汇总脚本与闸门统计均按此）：

- 每个 `(新闻, tmdb_id)` 候选打**一次**分
- 该分同时计入所有在 `triggered_by` 中召回它的**创作视角**桶（A2 / A4 / A7）
- 若候选**仅**被 A1 基线召回（`[baseline only]`），分计入 **baseline** 桶，**不计入**创作撞车展示

---

## 5. 闸门汇总：`summarize_eval.py`

全部 10 份 md 填分完成后，运行汇总（接口以 `python scripts/summarize_eval.py --help` 为准）：

```powershell
# 扫描整个目录（推荐）
python scripts/summarize_eval.py --dir output/Eval

# 或显式列出 candidates.md / run 目录
python scripts/summarize_eval.py output/Eval/01-grid-outage/candidates.md
python scripts/summarize_eval.py output/Eval/01-grid-outage
```

**解析规则**：在每个 `### ` 候选块内，读取 `- **共振分**:` 后第一个 `0` / `1` / `2`；未填则报 `missing`，该 run 不参与通过率计算。

**脚本输出（stdout 或 `--out report.json`）应包含**：

- 每个 run：是否存在 ≥1 个 **2 分** 候选
- 全局：**批次通过率** = 至少有一个 2 分的 run 数 ÷ 总 run 数
- **baseline_2_rate**（仅 A1 桶）vs **creative_2_rate**（A2+A4+A7 合并桶）
- 最终打印 **`GATE_PASS`** 或 **`GATE_FAIL`** 及简要原因

### 5.1 通过线（N=10）

同时满足以下两条方为 **GATE_PASS**；**判别重心在第 2 条**（产品已转向，见 [ADR-0002](adr/0002-pivot-to-event-logic-resonance.md)）：

1. **批次通过率 ≥ 60%（必要下限，证明力弱）**：10 条新闻中至少 **6 条** 各自存在 **≥1 个** 共振分为 **2** 的候选。
   - ⚠️ 转向后表层 2 分合法、A1 白描也能刷出 2 分，本条**容易过**，仅作下限，几乎不证明重构成效。
2. **关联增量优于基线（验收核心）**：**A1 中性基线**候选集的 **2 分率** **<** **创作侧**（Phase 3.6 为 A2+A4+A7；Phase 3.7 起为 12 persona，见 [ADR-0004](adr/0004-persona-emotional-diffusion.md) 闸门 2）合并候选集的 **2 分率**。
   - 这是唯一回答「情绪化扩散 / 创作视角是否比白描多带来**关联与共振**、多 agent 编剧室是否值得」的测试（不以「讽刺/反讽命中率」为独立目标）。
   - **口径**：优先比 `共振类型 ∈ {深层共振（仅逻辑，无表层）, 强共振（表层 + 逻辑）}` 的（score≥1）率，或单独比 `强共振（表层 + 逻辑）` 的 2 分率（才看得见创作的**骨架**增量）；`共振类型` 未填时退回比总 2 分率（判别力被表层稀释，仅参考）。
   - 不过 → 结论是「现实解构 + 碎片化 + A1 白描已够，创作视角是过度设计」，回到 prompt / 流程，别往下走。

未通过任一条 → **GATE_FAIL**。

### 5.2 记录结论（人工）

将书面结论写入 **`output/Eval/GATE_RESULT.md`**（Phase 3.5 已维护；含脚本快照 + 总编/product 裁决），例如：

```markdown
# Phase 3 闸门结论

- 日期：2026-05-29
- 批次：N=10（tests/eval_news/01–10）
- summarize_eval 输出：GATE_PASS / GATE_FAIL
- 批次通过率：6/10（60%）
- baseline_2_rate：… vs creative_2_rate：…
- 总编备注：…
```

---

## 6. 未通过时的回流路径

**GATE_FAIL** 时 **不要** 启动 Phase 4 `copywriter.py`（C1/C2）。按失败形态回流：

| 现象 | 优先回流 |
|------|----------|
| pseudo 质量差：未去实体化、口吻趋同、骨架模糊 | **Phase 1** — 改 `prompts/_shared/` 或 A2/A4/A7 Persona |
| pseudo 可读但候选普遍 0/1 分、与骨架无关 | **Phase 2** — 查 `retrieve.py` 模板、top-k、索引字段；确认 pseudo 套 `Overview: {pseudo}` |
| 创作与基线 2 分率倒挂（A1 ≥ 创作） | **Phase 1** — 强化创作视角的隐喻/结构注入；对照 A1 是否「过于幸运」 |
| 个别 run 全失败 / errors 非空 | 查 LLM 配置、单条 `--news-file` 重跑；必要时缩减 description 长度 |
| 批次通过率略低于 60%（如 5/10） | 可增至 N=15 重测（手册约定：增 N 时需**同比例重算**通过线，如 15 条需 9 条有 2 分） |

回流后从 **§3 评测循环** 重跑受影响的 news JSON，重新填分并 `summarize_eval`，更新 `GATE_RESULT.md`。

---

## 7. 通过后的下一步

| 结果 | 动作 |
|------|------|
| **GATE_PASS** | 启动 Phase 4 `copywriter.py`（中文审核文案 C1） |
| **GATE_FAIL** | 继续 Phase 1/2 迭代，不开 Copy |

评测 Markdown 格式可供 Phase 6 `main.py` 复用渲染逻辑；闸门指标定义供产品记录与 prompt 迭代参考。

---

## 8. 快速检查清单

- [ ] Phase 0–2 本地验收通过
- [ ] `tests/eval_news/` 内 10 条 JSON 就绪
- [ ] 10 次 `python scripts/run_eval.py --news-file ...` 均 exit 0
- [ ] `output/Eval/*/candidates.md` 共振分已填（无 `missing`）
- [ ] `python scripts/summarize_eval.py --dir output/Eval` → `GATE_PASS` 或已知原因下的 `GATE_FAIL`
- [ ] `output/Eval/GATE_RESULT.md` 已写书面结论

---

## 附录 · 人类工作流（一览）

```text
手挑 10 条（RSS 池或手写 JSON）
    → run_eval × 10（output/Eval/{run_id}/）
    → Obsidian 填 candidates.md 共振分 0/1/2
    → summarize_eval --dir output/Eval
    → 记录 GATE 于 output/Eval/GATE_RESULT.md
    → PASS → Phase 4；FAIL → Phase 1/2
```
