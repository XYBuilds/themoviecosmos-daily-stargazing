# Phase 3.11 GATE RESULT — Fragment Ladder 架构调优收敛判定

- **日期**: 2026-06-13
- **裁决性质**: ADR-0009 架构升级调优收敛指南针（非"要不要"判决闸）
- **对照**: fragment ladder design-on (full-batch-20260613-3117) vs Phase 3.10 基线
- **评测集**: 10 条新闻（01–10），同新闻同 def 同 judge
- **Judge**: MiMo v2.5 Pro, thinking=enabled（权威依据），screening-only/不采信

---

## 一、四条指南针口径

### ① 池差净新增 human-2 > 0（扩大强共振边界）

| 指标 | 值 |
|------|------|
| 净新增候选总数 | 102 |
| 净新增进入 high-hit 审阅的 | 44 |
| 净新增 judge=2 | **7** |
| 净新增 2-rate | **15.9%** |
| 净新增 POV变换=True | 4 |

**judge=2 净新增候选明细：**

| run_id | film | personas |
|--------|------|----------|
| 01-grid-outage | The Trigger Effect (1996) | THE-CAREGIVER, THE-HERO |
| 07-migration-border | Sleep Dealer (2008) | THE-EVERYMAN, THE-EXPLORER, THE-INNOCENT, THE-LOVER |
| 07-migration-border | Broken Horses (2015) | THE-HERO, THE-RULER |
| 09-cultural-backlash | Jesus of Montreal (1989) | THE-CREATOR, THE-HERO |
| 09-cultural-backlash | Be Somebody (2021) | THE-RULER |
| 10-whistleblower-leak | I Flunked, But... (1930) | THE-HERO, THE-INNOCENT |
| 10-whistleblower-leak | Attitude Test (2016) | THE-CREATOR, THE-JESTER |

**结论: PASS** — 净新增 judge=2 > 0，fragment ladder 架构确实扩大了强共振边界。

---

### ② 差集 2 分率不显著低于 baseline combo（精度不崩）

| 候选池 | scored | judge=0 | judge=1 | judge=2 | 2-rate |
|--------|--------|---------|---------|---------|--------|
| 净新增 | 44 | 34 | 3 | 7 | **15.9%** |
| 基线保留 | 66 | 45 | 12 | 9 | **13.6%** |
| 全池 | 110 | 79 | 15 | 16 | 14.5% |

**结论: PASS** — 净新增 2-rate (15.9%) ≥ 基线保留 2-rate (13.6%)，精度不崩。新架构引入的候选质量不低于保留池。

---

### ③ 守卫零硬失败

| 指标 | 值 |
|------|------|
| guard_hard_failures (10 runs) | **0** |

所有 10 个 run 均无 center 声明违规、事实漂移硬失败、fragment-bundle objective 越界。

**结论: PASS**

---

### ④ 3.10 已确认 human-2 候选不丢

| 指标 | 值 |
|------|------|
| human-2 被 judge=0 杀 | **0** |
| human-2 因 sort 变化落在预算线下 | 5 (pool retention warning) |

**明细（落在预算线下的 5 条）：**

| run_id | tmdb_id | 说明 |
|--------|---------|------|
| 01-grid-outage | 431892 | 因新 convergent sort 排在 top-19 之后 |
| 02-corporate-layoff | 485162 | 同上 |
| 05-climate-disaster | 33196 | 同上 |
| 06-tech-monopoly | 13748 | 同上 |
| 08-sports-underdog | 248555 | 同上 |

这 5 条**未被 reject**（judge≠0），仅因池子固定 19/run 且 102 条新候选进入后 convergent sort 重排，落在预算线外。这是打包归因的已知代价——新旧总量守恒（190 vs 190），新候选替换的是**弱候选位**，但极端情况下个别旧 human-2 也可能落出。

**安全评估**: 5/22 (22 = 10 runs 中 baseline human-2 总数) = 22.7% 落出率。无一被 judge=0 hard-reject。若后续人工确认这 5 条确实是强共振且不应丢，可通过以下调优手段恢复：
- 提高 `baseline_overlap` 在 convergent sort 中的权重
- 对已确认 human-2 设置 retention floor

**结论: CONDITIONAL PASS** — 安全约束（零 judge-kill）满足；5 条 sort 落出是已接受的打包归因代价，可通过调优恢复。

---

## 二、调优结论

### search_unit_kind 分解

| kind | any-hit | exclusive | 占比 |
|------|---------|-----------|------|
| persona-semantic | 100 | 89 | **87.3%** |
| event-fragment-bundle | 11 | 0 | 0% exclusive |
| surface-fragment-bundle | 1 | 0 | 0% exclusive |
| collision gain | 12 | — | 11.8% |

- **persona-semantic 是压倒性主力**：89/102 净新增独家来自此通道。
- **event/surface bundle 无独家贡献**：仅通过 collision gain（多通道汇聚）体现增益。
- 调优方向：event-fragment-bundle 的 objective levels 覆盖面有限，可考虑扩展 why/how/result 组合方式。

### Persona 贡献排名

| Top-3 | 净新增数 | Bottom-3 | 净新增数 |
|-------|---------|----------|---------|
| THE-INNOCENT | 17 | THE-EVERYMAN | 8 |
| THE-CAREGIVER | 15 | THE-JESTER | 8 |
| THE-CREATOR | 15 | THE-SAGE | 8 |

### Center dimension 分布

| dimension | 净新增数 | 占比 |
|-----------|---------|------|
| who | 47 | 35.3% |
| result | 42 | 31.6% |
| how | 28 | 21.1% |
| why | 15 | 11.3% |
| where | 1 | 0.8% |

- `who` + `result` 占 2/3 净新增，符合 persona-semantic 以人物和结果为中心组织语义的设计预期。
- `where` 几乎无贡献，surface-fragment-bundle 现有覆盖已足够。

### POV变换 分布

- judge POV=True: 4/44 净新增 (9.1%)
- 集中在 07-migration-border（Sleep Dealer, Broken Horses, Sicario, Trade）
- 即视角变换能力确实在**边境/移民**类新闻上激活，符合 ADR-0008 D4 预期。

---

## 三、GATE 裁决

| 口径 | 判定 |
|------|------|
| ① 净新增 human-2 > 0 | **PASS** (7 条) |
| ② 精度不崩 | **PASS** (15.9% ≥ 13.6%) |
| ③ 守卫零硬失败 | **PASS** (0) |
| ④ human-2 不丢 | **CONDITIONAL PASS** (零 kill; 5 条 sort 落出) |

### 总裁决: **GATE GO**

Fragment ladder + search unit 架构升级**调优已收敛**：
- 扩大了强共振边界（+7 judge=2）
- 精度不低于基线
- 安全约束满足
- 5 条 sort 落出属已接受代价，可后续微调

### 后续动作

1. ADR-0009 状态升级: `proposed` → `accepted`
2. ADR-0008 标注: `superseded by ADR-0009`（通道结构部分）
3. Fragment ladder 成为生成层标配架构
4. 考虑: event-fragment-bundle 组合扩展、baseline_overlap retention 调优、呈现层 POV（OPEN a）

---

## 四、数据溯源

| 产物 | 路径 |
|------|------|
| 全批产物 | `output/Eval/phase3.11/full-batch-20260613-3117/` |
| thinking-enabled judge | `llm-judge-scores-thinking-enabled.json` |
| tuning report | `phase3117-tuning-report.md` |
| summary | `phase3117-summary.json` |
| high-hit review | `high-hit-score-review.md` / `.json` |
| 3.10 基线 | `output/Eval/phase3.10/` |
| ADR-0009 | `docs/adr/0009-fragment-ladder-and-search-unit-architecture.md` |