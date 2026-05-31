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
- 含足够「结构骨架」（权力博弈、命运转折、反讽落差），而非纯数据通报
- 避免过于本地化专名堆叠——agents 会去实体化，但极端生僻事件可解释性较差

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
├── run.md           # 索引（Obsidian 入口）
├── reality.json     # 新闻快照（JSON，与 reality.md 同源）
├── reality.md       # 现实波澜（人类可读）
├── retrieve.json    # 完整 retrieve（per_agent + candidates + divergence）
├── errors.md        # Agent 失败（若有）
├── candidates.md    # 聚合候选 + 共振分（总编唯一填分处）
└── agents/
    ├── A2.md        # 伪剧情 + 本视角 Top-K
    ├── A4.md
    ├── A7.md
    └── A1.md        # 基线
```

**成本提示**：每条新闻 ≈ 4 次 LLM 调用 + 1 次全量向量检索；10 条 ≈ 10× 上述开销。

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

共振有**两层**，本 rubric **同时拥抱**二者（与 [`CONTEXT.md`](../CONTEXT.md) 中 **共振 (Resonance)** 一致）：

- **表层共振 (Surface)**：候选与新闻共享**具体且承重**的元素——地点 / 人物类型 / 事件类型 / 设定 / 题材。关键在「**承重**」：该共享元素必须是两边故事的核心驱动，而非碰巧同一个布景。
- **结构性共振 (Structural)**：抽象骨架同构——权力关系 / 命运结构 / 反讽落差。

按两轴定分：

| | 骨架**不**同构 | 骨架同构 |
|---|---|---|
| **无**承重表层锚点 | **0** · 无共振：仅偶然词面重叠，换一条无关新闻同样能「解释」这部片 | **2** · 深层共振：说不出共享布景，但能清晰说出同构骨架——如「中心权威在资源稀缺下被迫牺牲边缘群体」「个人命运被体制齿轮碾过」「公开 rhetoric 与 private 动机反讽撕裂」（跨界，最「绝妙」） |
| **有**承重表层锚点 | **1** · 表层沾边：共享一个承重元素（同地点 / 同事件类型），但权力 / 命运 / 反讽骨架对不上（如同一座城市：悲剧新闻 vs 轻喜剧电影） | **2** · 强共振：既有承重的具体锚点，又骨架同构（最理想） |

> **0 分守门**：别让「拥抱表层」滑成「什么都给分」。**纯偶然、非承重的表层重叠仍判 0**——判据不变：「换一条无关新闻同样能解释这部片」= 0。

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

同时满足以下两条方为 **GATE_PASS**：

1. **批次通过率 ≥ 60%**：10 条新闻中至少 **6 条** 各自存在 **≥1 个** 共振分为 **2** 的候选
2. **创作优于基线**：**A1 基线**候选集的 **2 分率** **<** **A2+A4+A7 创作**合并候选集的 **2 分率**
   - ⚠️ 注意：新 rubric 把**表层共振**也纳入 2 分，而 A1 基线（题材平面）最擅长表层匹配，其 2 分率会被抬高；解读本条时心里有数——必要时人工分辨某个 2 分是靠表层还是靠骨架。

未通过任一条 → **GATE_FAIL**。

### 5.2 记录结论（人工）

将书面结论写入 **`output/Eval/GATE_RESULT.md`**（人工维护，不纳入 git 亦可），例如：

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
