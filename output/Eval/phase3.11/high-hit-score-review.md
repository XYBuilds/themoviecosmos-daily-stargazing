# Phase 3.11.6 Pilot — High Pseudo Hit Score · Human Review

## Criteria

### Pseudo 命中分（二级审阅键 · 非质量闸）

**High-hit review** lists candidates with **pseudo命中分合计 ≥ 5**
or **pure-neutral** hits (`neutral_hits≥1` and `distinct_agents=0`, ADR-0006 D4).
Inclusion is **not** a quality gate; D1 `quality_candidate` is from retrieve.

For each hit line under **命中视角/碎片**, count entries in `fragments=[...]`
— **each fragment id = 1 point** for that pseudo.

- **Candidate 总分** (`pseudo命中分合计`) = sum of pseudo 命中分 across all hit lines.
- Shown inline per line, e.g. `HERO/p1: fragments=[...] · sim=... · **命中分=3**`.

### Pilot scope（本稿与 3.10 全集审阅的差异）

| 项 | Phase 3.10 `high-hit-score-review.md` | 本稿（3.11.6 pilot） |
|----|--------------------------------------|----------------------|
| 新闻条数 | 01–10 全批 | **仅 `01-grid-outage`** |
| 设计臂 | 3.10 基线（valence 光谱 + 旧 pseudo） | **ADR-0008 design-on**（元素中心构图 + POV focalized） |
| 对照臂 | — | `output/Eval/phase3.10/01-grid-outage/` |
| 自动化闸 | 无 | **防火墙六维审计** + Go/No-Go 建议 |
| 人工任务 | 共振分 / 共振类型 / 打分备注 | 同上 + **守卫签核清单**（见文末） |

### Sources

- **Design-on run:** `output/Eval/phase3.11/pilot-20260611-062203/01-grid-outage/`
- **3.10 baseline:** `output/Eval/phase3.10/01-grid-outage/`
- **Primary hits:** `retrieve.json` → `hit_sources`（含 `channel_role`: neutral / toned / focalized）
- **Persona legs:** `personas/*/persona-pipeline.json`
- **Pool diff / audit:** `pool-diff.json`, `audit.json`, `pilot-audit.md`
- **Gap A SSOT:** `pilot-manifest.json` → `gap_a_targets`
- **Editor fields:** 共振分 / 共振类型 / 打分备注 are placeholders only (not filled by this script).

- **Generation date:** 2026-06-11
- **Pilot run id:** `pilot-20260611-062203`
- **Automated Go/No-Go:** **No-Go**（6 runtime guard hard failures）
- **Human candidates (design-on):** 19（与 baseline 同预算）
- **Personas attempted:** 12 · **pipeline 成功:** 6 · **guard / pipeline 失败:** 6

---

## Executive summary · 如何读本文

本稿是 **Phase 3.11.6 单点 pilot** 的总编人工审阅包：在 `01-grid-outage`（Visayas 电网限电）上，用 **ADR-0008 整包新设计** 对照 **Phase 3.10 基线**，供 Go/No-Go 决策。

**自动化结论（须人工覆核）：No-Go。** 6 个 persona 在生成阶段硬失败（事实守卫 / 支撑元素上限 / 双地板），导致这些 persona **无 toned 腿、无完整 pseudo 集**，并连带 **10 部 baseline 命中片从漏斗消失**。成功 persona（Caregiver / Creator / Explorer / Hero / Magician / Sage）的中心声明自动审计通过，但 **4/6 成功 persona 的 focalized 腿** 被标为「center 未实例化 card vantage seat」。

**池差快照：** 候选数同为 19；重叠 9；净新增 10；丢失 10。**Gap A 靶片 Survival Family (429918) 仍在重叠池内（human 漏斗 #1）**，但未出现在 design-on 独家净新增中；judge 预筛口径仍为「表层沾边」。

**建议阅读顺序：**

1. 下文 **Per-persona 流水线** — 看清谁成功、谁因何 guard fail。
2. **池差表** — baseline vs design-on 的净增/丢失片名。
3. **Gap A** — POV-resonance 靶片是否保住。
4. **防火墙六维** — 自动 PASS/FAIL + 人工 eyeball 项。
5. **High-hit 候选** — 按 3.10 同款 pseudo 命中分格式抽审顶部片（非 JSON dump）。
6. **Human sign-off checklist** — 签核后方可 approve → 3.11.7。

---

## 01-grid-outage

# 现实波澜 · 01-grid-outage

## 元信息
- date: 2026-05-29
- news_url: https://mb.com.ph/2026/05/29/rotational-blackout-risks-rise-in-visayas-amid-power-crunch
- run_id: 01-grid-outage
- pilot_output: `pilot-20260611-062203`

## 现实波澜
- **title**: Rotational blackout risks rise in Visayas amid power crunch
- **source** / **pub_time**: Manila Bulletin / 2026-05-29T18:00:00+08:00
- **summary**: The Philippines grid operator placed the Visayas under red alert after Kepco SPC Power's Unit 2 tripped offline, leaving more than 950 megawatts unavailable alongside other long-running plant outages. Eleven generators have failed since May began, while seasonal heat drove demand into a thin operating margin. Officials ordered emergency load shedding to keep a critical 230-kilovolt transmission line from overloading.

---

## Per-persona 流水线（success vs guard fail）

| Persona | Pipeline | 双地板 | 事实漂移 | 中心真实性 | Focalized 派生 | 通道 / 中心（成功时） |
|---------|----------|--------|----------|------------|----------------|----------------------|
| The-Caregiver | ✅ | ✅ n1+2 toned +1 focal | ✅ | ✅ | ⚠️ p3 focal who-0 未匹配 card seat | toned: result-0, who-3 · focal: who-0 |
| The-Creator | ✅ | ✅ | ✅ | ✅ | ⚠️ p3 center why-0 却 focal who-0 | toned: how-1, how-2 · focal: why-0→who-0 |
| The-Explorer | ✅ | ✅ | ✅ | ✅ | ✅ | toned: how-2, result-0 · focal: who-0 |
| The-Hero | ✅ | ✅ | ✅ | ✅ | ⚠️ p3 focal who-2 未匹配 card seat | toned: result-0, how-2 · focal: who-2 |
| The-Magician | ✅ | ✅ | ✅ | ✅ | ✅ | toned: how-1, why-2 · focal: who-0 |
| The-Sage | ✅ | ✅ | ✅ | ✅ | ⚠️ p3 focal who-0 未匹配 card seat | toned: result-0, why-0 · focal: who-0 |
| The-Everyman | ❌ | ❌ | ❌ p1 内心戏 | — | — | pipeline 中断 |
| The-Innocent | ❌ | ❌ | ❌ p1 新专名 "In May" | — | — | pipeline 中断 |
| The-Jester | ❌ | ❌ | ❌ p1 内心戏 | — | — | pipeline 中断 |
| The-Lover | ❌ | ❌ | ❌ p1 支撑元素 5>4 | — | — | pipeline 中断 |
| The-Outlaw | ❌ | ❌ | ❌ p3 支撑元素 5>4 | — | — | pipeline 中断 |
| The-Ruler | ❌ | ❌ | ❌ p1 支撑元素 5>4 | — | — | pipeline 中断 |

### 成功 persona · pseudo 摘录（供人工读 prose）

**The-Explorer · p1 toned**（center=`how-2`）
> Officials navigated the crisis by ordering load shedding, a grid stabilization action designed to protect a critical 230-kilovolt transmission line from overloading…

**The-Explorer · p3 focalized**（center=`who-0`, focal=`who-0` · 自动审计 PASS）
> The power system operator watches as the consequences of a power outage ripple across the grid… From this vantage, the operator sees the direct outcome: a capacity loss leaving the island group short of over 950 megawatts…

**The-Caregiver · p3 focalized**（center=`who-0` · 自动审计 WARN）
> From the perspective of the Philippines grid operator, the duty to protect the grid's stability was paramount… implementing grid stabilization measures to prevent a broader collapse.

**The-Sage · p3 focalized**（center=`who-0` · 含第一人称 · 自动审计 WARN）
> As the system overseer, my duty is to maintain the grid… I authorized a calculated grid protection measure—an emergency load management action…

### 失败 persona · 硬失败原因（须回 3.11.2/3.11.3 收紧）

| Persona | 错误 |
|---------|------|
| The-Everyman | `pseudo p1: fact guard — invented inner monologue or interiority` |
| The-Innocent | `pseudo p1: fact guard — novel proper noun 'In May'` |
| The-Jester | `pseudo p1: fact guard — invented inner monologue or interiority` |
| The-Lover | `pseudo p1: supporting elements must be 2–4, got 5` |
| The-Outlaw | `pseudo p3: supporting elements must be 2–4, got 5` |
| The-Ruler | `pseudo p1: supporting elements must be 2–4, got 5` |

失败 persona **无 toned 腿产出** → 双地板硬性不满足；n1 对 Everyman / Innocent / Jester / Lover / Outlaw / Ruler **未能与 baseline 逐字对齐校验**（design 侧缺失）。

### OPEN d · weak-fit cohort 观察

| Persona | 质量 | 备注 |
|---------|------|------|
| The-Creator | acceptable | fit 0.70–0.85；3 腿齐全（2 toned + 1 focalized） |
| The-Innocent | **failed** | pipeline error |
| The-Jester | **failed** | pipeline error |
| The-Lover | **failed** | pipeline error |

---

## 候选池 · baseline vs design-on

| 指标 | 3.10 baseline | ADR-0008 design-on |
|------|---------------|-------------------|
| human_candidates | 19 | 19 |
| overlap | — | **9** |
| net-new | — | **10** |
| lost vs baseline | — | **10** |

### 重叠 9 部（两臂均进漏斗）

| tmdb_id | Title |
|---------|-------|
| 33495 | 2061 - Un anno eccezionale |
| 33787 | Get Smart, Again! |
| 266727 | Peasants |
| 274855 | Geostorm |
| 418879 | The Current War |
| 429918 | **Survival Family** |
| 475946 | Blade Runner: Black Out 2022 |
| 533885 | Kaappaan |
| 841793 | Stranded |

### 净新增 10 部（design-on ∖ baseline）· 按通道

| tmdb_id | Title | sim | 通道 | 触发 persona |
|---------|-------|-----|------|--------------|
| 2154 | The Dark Side of the Moon | 0.471 | toned | THE-SAGE p1 |
| 6499 | Turbo: A Power Rangers Movie | 0.518 | **focalized** | THE-HERO p3 |
| 14161 | 2012 | 0.444 | toned | THE-CREATOR p1 |
| 43552 | Vanishing on 7th Street | 0.496 | toned | THE-CAREGIVER p1 |
| 58770 | The Trigger Effect | 0.457 | toned | THE-SAGE p2 |
| 63333 | Gog | 0.480 | **focalized** | THE-CREATOR p3 |
| 158091 | Metro Manila | 0.508 | toned | THE-EXPLORER p1 |
| 720321 | Breathe | 0.451 | neutral (n1 撞车) | THE-HERO / THE-SAGE n1 |
| 949698 | Flashover | 0.459 | **focalized** | THE-EXPLORER p3 |
| 969686 | 4 Horsemen: Apocalypse | 0.537 | **focalized** | THE-MAGICIAN p3 |

**通道分解：** focalized 独家 4 · toned 独家 5 · neutral 独家 1（Breathe 经 n1 中性通道进入，非 POV 增益）。

### 丢失 10 部（baseline ∖ design-on）

| tmdb_id | Title | 备注 |
|---------|-------|------|
| 46221 | The Tunnel | 原 baseline 单 agent 命中 |
| 100063 | Blackout | |
| 111750 | The Real Glory | 原 优质·多agent |
| 190738 | Assembling a Generator | |
| 194834 | Re-Generator | |
| 210219 | Jet Stream | |
| 280492 | From What Is Before | 原 优质·多agent |
| 370097 | Stormageddon | |
| 431892 | Trapped | |
| 1223272 | Contagion of Fear | |

> **双地板警示：** 丢失片与 6 个失败 persona 高度相关（这些 persona 的 pseudo 未进入 retrieve）。人工需判断：丢失是「可接受的漏斗置换」还是「匹配地板塌方」。

### Design-on 漏斗 Top-12（人工预算内排序 · 供 ⑤ 签核）

| # | Title | sim | quality | agents | 备注 |
|---|-------|-----|---------|--------|------|
| 1 | Survival Family | 0.602 | ✅ | 5 | Gap A 靶片 · 仍在池内 |
| 2 | Stranded | 0.484 | ✅ | 2 | |
| 3 | Geostorm | 0.568 | — | 4 | |
| 4 | Breathe | 0.451 | — | 0 | 纯 neutral 撞车 |
| 5 | 4 Horsemen: Apocalypse | 0.537 | — | 1 | focalized 净新增 |
| 6 | 2061 - Un anno eccezionale | 0.532 | — | 1 | |
| 7 | Turbo: A Power Rangers Movie | 0.518 | — | 1 | focalized 净新增 |
| 8 | The Current War | 0.517 | — | 1 | |
| 9 | Metro Manila | 0.508 | — | 1 | toned 净新增 |
| 10 | Vanishing on 7th Street | 0.496 | — | 1 | toned 净新增 |
| 11 | Blade Runner: Black Out 2022 | 0.489 | — | 1 | |
| 12 | Gog | 0.480 | — | 1 | focalized 净新增 |

自动化漏斗问题：`human_candidates not monotonic by convergence/sort key` — 排序键需人工判断是否合理。

---

## Gap A 靶片状态

**Manifest 定义（`pilot-manifest.json`）：**

| tmdb_id | Title | human_score | judge | judge 共振类型 |
|---------|-------|-------------|-------|----------------|
| 429918 | Survival Family | **2** | 1 | 表层沾边 |

**本 run 结果：**

| 检查项 | 状态 |
|--------|------|
| 在 design-on human_candidates 内 | ✅ **#1**（sim 0.602, quality_candidate=true, 5 agents） |
| 在 net-new（design 独家） | ❌ 在 **overlap**（baseline 亦有） |
| gap_a_targets_in_net_new | `[]` |
| gap_a_targets_in_baseline_only | Survival Family 列为此（指未靠新通道独家召回） |

**人工判读提示：** Gap A 关心的是 POV/视角变换才看得见的共振。Survival Family 仍被多条 **neutral n1 + toned** 腿命中，但 **focalized 独家通道未将其净新增入池**；且 3.10 中其 pseudo 命中分极高（全批 #1）。请人工确认：design-on 是否**保住**了 2 分共振逻辑，还是仅余表层电网停电同场。

---

## 防火墙审计 · 六维（review-friendly）

| # | 维度 | 自动 | 人工 eyeball |
|---|------|------|--------------|
| ① | 事实漂移（无内心戏 / 新事件 / 新专名） | **FAIL** · 6 hard failures | 读 focalized 腿（尤其 Sage p3 第一人称）是否编造内心 |
| ② | 中心声明真实性（声明 A 实写 A） | **PASS** · 成功 persona 无 stuffing | 确认中心元素在 prose 中负载荷 |
| ③ | Focalized 按 card Who 原型派生 | **FAIL** · Caregiver/Creator/Hero/Sage | focal∈who-* 已满足；**seat 实例化** 4 条 WARN |
| ④ | 双地板（n1 零改动 + ≥1 非 focal toned + baseline hits） | **FAIL** · 6 persona 无 toned；**10 片丢失** |  spot-check 成功 persona n1 字数 vs baseline |
| ⑤ | 漏斗去重 / 汇聚排序 | **FAIL** · 排序非单调 | 审 Top-19 顺序是否可交付总编 |
| ⑥ | OPEN d weak-fit valence 可选化 | **FAIL** · 3/4 weak-fit pipeline 失败 | Creator 可读；Innocent/Jester/Lover 无产出 |

**Center granularity（OPEN c 携带）：**

- 中心元素分布：`result-0×4, who-0×4, how-2×3, how-1×2, why-0×2, who-3×1, who-2×1, why-2×1`
- 通道：`toned×12, focalized×6`（仅成功 6 persona）
- Focal who-*：`who-0×5, who-2×1`

---

### 多 agents 命中

**Count:** 2 candidate(s) with quality_candidate · ≥2 agents in pilot funnel

<!-- run_id: 01-grid-outage · design-on pilot -->
<!-- pseudo命中分合计: 约 28+（较 3.10 全 12 persona 的 159 大幅收缩） -->
### Survival Family (2017) [THE-HERO, THE-CAREGIVER, THE-EXPLORER, THE-MAGICIAN, THE-SAGE] [优质·多agent]
- **tmdb_id**: 429918
- **quality_candidate**: true
- **distinct_agents**: 5（pilot 仅 6 persona 成功；baseline 为 12）
- **相似度**: 0.6017
- **genres** / **language**: Comedy, Drama, Adventure / ja
- **overview**: A world wide electrical outage occurs. Everything that requires electricity comes to a stop. Tokyo is nearly ruined. Yoshiyuki Suzuki decides to escape from Tokyo with his family.
- **跳转**: https://themoviecosmos.com/movie/429918
- **also_baseline**: true（overlap）
- **Gap A**: human-2 · judge-1 表层沾边
- **命中视角/碎片**（节选 · 含 channel_role）:
  - THE-HERO/n1 · **neutral**: fragments=[result-0, how-2, who-2, why-0, how-1] · sim=0.4875 · **命中分=5**
  - THE-CAREGIVER/n1 · **neutral**: fragments=[result-0, who-1, who-3, why-0, how-2] · sim=0.4896 · **命中分=5**
  - THE-CAREGIVER/p1 · **toned**: fragments=[why-0, how-2, result-0] · sim=0.5758 · **命中分=3**
  - THE-EXPLORER/p1 · **toned**: fragments=[how-2, result-0] · sim=0.5217 · **命中分=2**
  - THE-HERO/p1 · **toned**: fragments=[result-0, how-2, why-0] · sim=0.5288 · **命中分=3**
  - THE-SAGE/p1 · **toned**: fragments=[why-0, how-1, how-2, result-0] · sim=0.4796 · **命中分=4**
- **pseudo命中分合计**: （人工可加总 · pilot 腿数少于 baseline）
- **共振分**: ___  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**: ___  <!-- 0 留空；1→深层共振；2→强共振 -->
- **打分备注**: Gap A 靶片 · 请对照是否仍达 human-2

<!-- run_id: 01-grid-outage -->
### Stranded (2021) [THE-MAGICIAN, THE-SAGE] [优质·多agent]
- **tmdb_id**: 841793
- **quality_candidate**: true
- **distinct_agents**: 2
- **相似度**: 0.4838
- **overview**: After a catastrophic solar flare destroys all electrical power, a father must protect his family from the ensuing chaos.
- **跳转**: https://themoviecosmos.com/movie/841793
- **also_baseline**: true
- **命中视角/碎片**（节选）:
  - THE-MAGICIAN/n1 · **neutral**: fragments=[how-1, how-2, why-0, who-0, result-0] · **命中分=5**
  - THE-SAGE/n1 · **neutral**: fragments=[result-0, why-0, why-1, why-2, how-0] · **命中分=5**
- **共振分**: ___
- **共振类型**: ___

### 单 agent 命中 · focalized 净新增（POV 通道样本）

**4 Horsemen: Apocalypse (969686)** · THE-MAGICIAN **p3 focalized**
- fragments=[why-2, how-1, how-2] · sim=0.5372 · **命中分=3**
- **共振分**: ___ · **共振类型**: ___ · **POV变换**: ___ 

**Turbo: A Power Rangers Movie (6499)** · THE-HERO **p3 focalized**
- fragments=[why-0, how-1, how-2, why-2] · sim=0.5184 · **命中分=4**
- 自动审计：center who-2 未实例化 card vantage seat — 人工判断是否仍可用

**Flashover (949698)** · THE-EXPLORER **p3 focalized**
- fragments=[why-0, how-1, result-0] · sim=0.4588 · **命中分=3**

**Gog (63333)** · THE-CREATOR **p3 focalized**
- fragments=[why-0, why-1, why-2, result-0] · sim=0.4800 · **命中分=4**
- 自动审计：center why-0 与 focal who-0 不一致 — 人工读 prose

---

## Human sign-off checklist（签核后方可 Go → 3.11.7）

> 自动化建议 **No-Go**。以下六项须总编逐项签核；全部通过且接受风险后方可 `approve` 进入全批 A/B。

- [ ] **①** No invented inner monologue, events, causality, or outcomes in focalized/toned legs.
- [ ] **②** Each pseudo's declared center element is genuinely load-bearing (no keyword stuffing).
- [ ] **③** Focalized channels match card Who vantage prototypes; focal ∈ who-*.
- [ ] **④** Neutral n1 unchanged vs 3.10 for **successful** personas; ≥1 non-focal toned per persona; acceptable loss of 10 baseline-only titles.
- [ ] **⑤** Funnel dedup and convergent sort look reasonable for human review budget.
- [ ] **⑥** Weak-fit personas produce honest, fact-entailed prose without forced valence coverage (or document acceptable pipeline failure rate).

**签核人:** _______________ **日期:** _______________

**决定:** [ ] Go → 3.11.7 全批 A/B　[ ] No-Go → 回 3.11.2/3.11.3 收紧　[ ] 有条件 Go（备注: _________）

---

_Generated for Phase 3.11.6 pilot human gate · sources: `pilot-20260611-062203`, `phase3.10/01-grid-outage` · 2026-06-11_
