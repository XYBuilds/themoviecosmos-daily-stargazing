# 管线阶段唯一命名（英文动词体系）、编号全废、诊断死流移出生产主链

**Status**: accepted（命名与收敛口径拍板；命名与 5 维阶段契约已并入 [`docs/SSOT/news-to-film-pipeline.md`](../SSOT/news-to-film-pipeline.md)）

> **本 ADR 的性质**：命名与边界治理。它不改变任何一个步骤的内部算法（fragment ladder / search unit / 双轴评审等口径全部沿用 [ADR-0009](0009-fragment-ladder-and-search-unit-architecture.md) 与 [`docs/SSOT/news-to-film-pipeline.md`](../SSOT/news-to-film-pipeline.md)），只解决一个长期遗留问题：**同一个步骤有 2–4 套并行叫法，且没有任何一套是权威主名**。本 ADR 钉死「一步一名」。
>
> 架构主线见 ADR-0009；执行纪律见 [ADR-0010](0010-pseudo-drop-granularity-and-pipeline-first-derisking.md)；本 ADR 只覆盖**命名权威**与**生产/诊断职责边界**。

## 背景

经过 ADR-0005 → 0009 的五轮概念演进，单个管线步骤累积了多套互不统一的称呼，阅读与开发成本主要来自此处，而非算法本身：

- **三套并行词汇指向同一批步骤**：
  - 代码文件名：`deconstruct.py` / `fragment_ladder.py` / `personas.py` / `copywriter.py`
  - Agent / Pass 编号：`A0` / `A1` / `A2` / `A4` / `A7` / `P-Extract` / `P-Expand` / `C1` / `C2`
  - 设计概念名（SSOT）：现实解构层 / fragment ladder 层 / search unit 生成层
  - 数据流图标签（drawio）：新闻拆解层 / 搜索说法扩展层 / 找电影层
- **编号体系本身不自洽**：A0/A1/A2/A4/A7 不连续；`A1` 单独背着「基线 / held-out oracle / baseline / 现实记录员」四个身份。
- **大量已降级为 `diagnostic-only` 的概念仍占据生产数据结构**：撞车票、neutral channel (`n1`)、three-bucket、`neutral_hit_rate`、`quality_candidate` 等，已不影响任何生产结果，却仍在主链产物里输出，并在 `CONTEXT.md` 中各挂一条 `_Avoid_`。
- **生产管线脚本与一次性评测脚手架混在同一个 `scripts/` 目录**：7 个核心管线脚本淹没在 30+ 个 `run_phase3x_*` / `apply_*_phase310` / `promote_*` / `merge_*` 中。

总编据此决定做一次命名与边界收敛：先确定每步边界，再给每步唯一主名，让 **文件名 = 阶段名 = 主产物名** 三者对齐。

## 决策

### D1 · 六阶段唯一主名采用英文动词体系，编号体系整体废除

管线收敛为 6 个生产阶段 + 1 个编排入口。每个阶段有**唯一英文动词主名**（用于代码、文件、产物）与**唯一中文别名**（用于文档与交流），一一固定映射。除此之外的旧叫法一律降为「历史别名」，不再在新代码、新文档中作为主称呼。

| 阶段主名 | 中文别名 | 承载脚本（现状） | 主产物（建议统一名） |
| --- | --- | --- | --- |
| `intake` | 选材 | `fetch_news.py` | `news.json` |
| `extract` | 解构 | `deconstruct.py` | `facts.json` |
| `expand` | 扩展 | `fragment_ladder.py` | `bridges.json` |
| `rewrite` | 改写 | `personas.py` | `queries.json` |
| `retrieve` | 召回 | `retrieve.py` | `candidates.json` |
| `compose` | 文案 | `copywriter.py` | `review.md` / `publish.md` |
| `orchestrate` | 编排 | `main.py` | `Daily_Briefing/YYYY-MM-DD.md` |

> 产物文件名（`facts.json` / `bridges.json` / `queries.json` 等）为**目标统一名**，是否即刻重命名现有产物（`reality-deconstructed.json` / `reality-expanded.json` 等）留待 SSOT 阶段契约落地时统一决定，不在本 ADR 强制。

### D2 · 编号与 Pass 名的废除口径

| 旧称 | 处置 |
| --- | --- |
| `A0`（现实解构） | 废除。对外只称 `extract` / 解构。 |
| `P-Extract` / `P-Expand` / `P-Select` / `P-Tone` | 废除。能力分别归入 `extract` / `expand` / `rewrite`。 |
| `C1`（审核稿）/ `C2`（定稿） | 废除为独立编号；降为 `compose` 的两个 stage：`compose --stage review` / `compose --stage publish`。 |
| 创作视角编号 `A2` / `A4` / `A7` | **对外不再暴露编号**，统一用视角名（社会学家 / 神话学者 / 混沌理论家）。注：`scripts/agents.py` 的旧 pseudos 生成路径在 `PERSONA_FILENAMES` 中硬编码引用 `prompts/A2_sociologist.md` / `A4_*` / `A7_*`，而这些 prompt 文件**磁盘上并不存在**；该路径已被 `personas.py` 的 search_units 取代，属 D3 待清理死流程，连同其对不存在 prompt 的硬编码引用留待后续轮次随 `agents.py` 一并处理，本轮不改其代码逻辑。 |
| `A1`（基线 / held-out oracle / baseline / 现实记录员） | 四名收一：对外统一称「基线 oracle」。它**不属于 6 生产阶段**，是 `retrieve` 旁挂的评测专用神谕（见 D3）。 |

### D3 · 诊断死流移出生产主链，仅在评测侧保留

以下产物/概念已被 ADR-0006/0009 降级为 `diagnostic-only`，对生产结果零影响。本 ADR 钉死：它们**不得出现在生产主链产物中**；评测确需者，迁至评测侧单独保留。

| 死流 | 现状 | 处置 |
| --- | --- | --- |
| `agents.py` 的 `pseudos[]` / `text` 旧生成路径 | 与 `personas.py` 的 `search_units` 并存；`retrieve.py` 兼容三套输入 | `rewrite` 仅保留 `search_units`；`retrieve` 仅吃单一输入口径 |
| 撞车票 / `quality_candidate` | 不进排序、不进截断、不进 Go/No-Go | 移出 `candidates.json`，仅评测产物可留 |
| neutral channel (`n1`) / `neutral_hit_rate` | 已非判据 | 移出 `rewrite` 主产物 |
| three-bucket 分桶 | 已非 Go/No-Go、非 D5 判据 | 移出生产主链 |
| 基线 oracle（原 A1） | 评测用召回/质量神谕 | **保留但归评测侧**，永不进 `retrieve` 的 `candidates` |
| `scripts/` 下 `run_phase3x_*` / `apply_*` / `promote_*` / `merge_*` 等一次性评测脚手架 | 与 7 个管线脚本混目录 | 迁至 `scripts/eval/`，与生产管线脚本物理隔离 |

> 本 ADR 只钉「应移出」的边界口径；**具体删改属代码重构，不在本轮范围**，待 SSOT 阶段契约落地后另行实施。

### D4 · 已知偏差与待决项（显式登记，不在本 ADR 决断）

- **SSOT 与代码存在偏差**：[`news-to-film-pipeline.md`](../SSOT/news-to-film-pipeline.md) §12 声明「删除独立 `reality-expanded` / hypernym 层」，但当前 `fragment_ladder.py` 仍产出 `reality-expanded.json`。SSOT 描述的是 ADR-0009 **目标态**，代码停在**中间态**。该偏差登记为已知事实。
- **契约落地处已定**：命名与 5 维阶段契约**并入** [`docs/SSOT/news-to-film-pipeline.md`](../SSOT/news-to-film-pipeline.md)（由 `simplified-news-to-film-workflow.md` 更名而来），**不再单独建 `pipeline-stages-contract.md`**。该文件同时是阶段命名权威与工作流设计 SSOT，概念维度按目标态书写、落地物维度暂标偏差。
- **产物重命名未执行**：D1 的统一产物名为目标名，现有产物文件是否即刻改名待定。
- **【文件更名映射】（技术债）**：`simplified-news-to-film-workflow.md` → `news-to-film-pipeline.md`。历史记录（`docs/reports/Phase3.12.7-doc-backfill-report.md`、`.cursor/plans/Phase3.11-pov-focalization-additive.plan.md`、`.cursor/plans/Phase3.12-code-doc-sync.plan.md`）中对旧文件名的引用为**已知死链，遵循历史不回改原则，不予回改**，更名映射由本 ADR 统一登记。
- **【落地物清理债】（技术债）**：未来重构代码时，需把承载脚本名（`deconstruct.py`→`extract.py`、`fragment_ladder.py`→`expand.py`、`personas.py`→`rewrite.py`、`copywriter.py`→`compose.py` 等）、产物名（`reality-deconstructed.json`→`facts.json`、`reality-expanded.json`→`bridges.json`、`search-units.json`→`queries.json`、`retrieve.json`→`candidates.json` 等）、prompts 名一并落地；落地后须**同步清除 `news-to-film-pipeline.md` 表与正文中的「当前实际」偏差标注**，使该文档收敛为纯目标态。

## 为什么

1. **一步一名是阅读成本的根因解**：算法已由 ADR-0009 收敛得足够清晰，剩余的认知负担几乎全部来自「同一步骤多套叫法、且无主名」。固定 `文件名 = 阶段名 = 产物名` 后，新开发者读任一处都能直接定位步骤身份，不必跨三套词汇拼图。
2. **编号体系已无法承载语义**：不连续编号 + `A1` 的四重身份，使编号从「索引」退化为「歧义源」。改用英文动词主名后，名字即职责。
3. **生产与诊断必须物理隔离**：`diagnostic-only` 流仍混在生产产物里，会让每个下游消费者被迫理解一批不影响结果的字段。移出主链是降低复杂度扩散的直接手段。

## 后果 / 已知局限

- **过渡期双名并存**：代码文件名与 prompts 文件名（`deconstruct.py`、`A2_sociologist.md`）短期内仍是旧名，与新主名暂不一致；本 ADR 接受这一过渡态，重命名属后续重构。
- **本 ADR 是命名/边界宪法，不是迁移工单**：D3 的死流移出、D1 的产物改名均为口径声明；落地改动需在 SSOT 阶段契约确定「以哪态为准」后，再拆分为可执行的重构 TODO。
- **SSOT 偏差需尽快定调**：D4 登记的偏差若长期不决，`news-to-film-pipeline.md` SSOT 会持续描述一个代码未达的世界，命名收敛的收益会被偏差重新稀释。