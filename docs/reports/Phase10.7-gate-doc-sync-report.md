# Phase 10.7 - GATE 验收 · A/B 选型冻结 · 文档同步 交付报告

## 1. 改动范围 (Scope)

- `docs/adr/0017-persona-perspective-c2-draft-pool.md`（+9 行）——D5 补「10.7 GATE 选型冻结结论」段。
- `docs/SSOT/news-to-film-pipeline.md`（+2 行）——`compose` 阶段补 Phase 10 草稿池说明，引用 ADR-0017。
- `docs/SSOT/电影宇宙「每日星轨观测」系统 PRD.md`（+2 行）——§7.3 定稿段补 Phase 10 草稿池说明，引用 ADR-0017。
- 无生产代码改动、无依赖变更（冻结为纯文档，见 §2）。
- 代码提交：`82aaadc` `docs(compose): p10.7-freeze-combine-route-a-and-sync-ssot`。

### 分支继承说明

- **本 TODO 分支**：`feat/phase10.5.1-draft-pool-ux-primary-cta`。
- **继承来源**：从最新 `main` 检出（10.1–10.6 各 PR #129–#134 均已并入 main，末位 `4321947`）。
- **说明**：10.5.1 分支原为 10.7 GATE 人工验收期间的 **UX 迭代分支**（见 §2「10.5.x UX 迭代」），
  GATE Go 后 10.7 的文档冻结改动直接叠加在此分支上一并合并，未再另开分支——
  因 UX 迭代与 GATE 冻结同属「10.7 验收闭环」的产物，合并拓扑上归为一个 PR 更内聚。

## 2. 技术实现 (Implementation)

10.7 是本 Phase 唯一 `[需人工验收]` GATE，定位是**端到端验收 + A/B 选型冻结 + 文档收尾**，
不含新功能开发。三件事：

### (a) GATE 人工验收（Go）

真实批次 `output/daily_batch/2026-07-06/`（news `02-learning-another-language-appears-to-slow`，
tmdb 355196，`triggered_by` = 9 persona）全量扇出 + 面板端到端：

- **persona 可辨识性**（本 Phase 最大质量前提，ADR-0017 D1）：逐份人读 9-persona 池 +
  另一批次 6-persona 池，各 persona 视角与其核心情感对齐、互相可区分，**非 judge rationale 回声** → **强通过**。
- **面板三阶段工作流**（候选选片 → pick 选型 → refine 微调）：状态机切换无 JS 崩溃、
  Console 零错误、流程顺畅；池浏览 / 选主视角指针 / 合并≤2 / 派生当前稿 / 失效 humanized 均正常。

### (b) A/B 合并路线选型冻结 → **路线 A**

- 对 `The-Sage + The-Outlaw` 离线跑 `--combine-mode both`（真实 LLM，~37s），产 `#A`/`#B` 两版肉眼对比。
- **判定冻结路线 A（重跑 C2 合并视角）为生产默认**：A 出稿浑然一体、篇幅适配小红书、
  Sage 理性辨识与 Outlaw 抗争坠落两种镜头真正交织；B（文本拼接）出现片名重复 2 次、
  开头重复、关键数据重复、篇幅近乎翻倍，实证 D5 对 B「接缝与调性一致性存疑」的先验判断。
- **零代码改动即冻结**：`drafts_adapter._build_parser()` 的 `--combine-mode` argparse 默认本就是 `"A"`，
  且 `serve.handle_combine_drafts` 的 subprocess **不传 `--combine-mode`**（落 adapter 默认）。
  因此「路线 A = 生产默认 + serve 恒单版」在既有代码里已然成立 → 冻结 = 文档记录，无需改代码。
- **生产模式复跑实证**：清理对照稿后不带 `--combine-mode` 复跑，池仅 append 一条 `The-Sage+The-Outlaw`
  （**无 `#` 后缀**），确认双版逻辑不外泄生产。

### (c) 10.5.x UX 迭代（GATE 期间）

GATE 人工验收暴露的 UX 问题在 `feat/phase10.5.1` 上迭代修复（前端为主）：

- **Option A · 草稿池为唯一主入口**：移除「写推文」topbar，`#generate-drafts-btn` 升为 accent 主 CTA，
  移除废弃的 `#publish-result` CSS/DOM 与 `onPublish`（`/api/publish` 端点仍保留在 serve.py，仅前端不再直连）。
- **修复「未知错误」**：根因是浏览器命中旧 serve.py 冻结路由表返回无 `stderr` 的 404，前端只提 stderr 吞掉了它；
  修法是 shape-agnostic 的 `apiErrorText(res)` 贯穿 7 条错误分支。
- **草稿池卡片 → persona 标签页**：`#draft-pool-grid` → `#draft-pool-tabs`（flex-wrap pill 行），原生 `<button>` 键盘可达。
- **三阶段工作流重构**：`#copy-view` 内互斥的 `#pick-stage` / `#refine-stage`；`switchStage` 三态机
  （切换为纯视图操作、无后端副作用）；`loadCopy` 三态分诊（磁盘产物为单一事实源）；
  `onEnterRefine` 是唯一持久化点（调 `/api/select-draft`）；back 两级回退；新增 `GET /api/drafts` 补刷新恢复缺口。

## 3. 本地验证结果 (Verification)

全量验收测试全绿（本 TODO 提交前）：

```
$ python -m pytest -q
479 passed, 1 skipped in 171.69s
```

Phase 10 核心链路相关面：

```
$ python -m pytest tests/test_compose_publish.py tests/test_review_panel_drafts_adapter.py \
      tests/test_review_panel_serve.py tests/test_review_panel_regenerate_adapter.py -q
110 passed in 14.16s
```

- 冻结为纯文档改动，`git diff --numstat` 仅 3 个文档文件（+9/+2/+2），无 ghost CRLF 变更、无生产代码 diff。
- GATE 人工验收：persona 可辨识性强通过、三阶段工作流零 Console 错误、生产模式复跑单版实证通过。

## 4. 潜在影响或技术债 (Technical Debt & Caveats)

- **冻结零代码改动**：路线 A 生产默认在既有代码里已成立，本 TODO 不改运行时行为，无新风险。
- **`/api/publish` 端点保留**：前端不再直连，但 serve.py 端点仍在（未来若需回退旧直发路径可用）；属有意保留，非死代码遗漏。
- **前端无自动化测试**：草稿池三阶段 UI 仍靠服务端 DOM smoke test + 人工验收覆盖，受限于仓库无 JS 测试框架，属既有约束。
- **tab 命中区**：`.draft-tab` pill 的 padding 区不可点（点击绑定在内层 `.draft-tab-select`），
  经用户裁定「维持现状」——minor UX，不阻塞。
- **combine 生产上限 2**：D5 约束不变；`both` 仅开发期 CLI，不进面板 / 产物。
- **Phase 10 收官**：10.1–10.7 全部 complete 并入 main 后，本 Phase 关闭；persona 视角已真正进入 C2 定稿链路。