# Phase 10.5 - 前端草稿池浏览 + 选主视角指针 + 合并≤2 交付报告

## 1. 改动范围 (Scope)

- `review_panel/index.html`（+351 行，1523→1874 行）——纯前端，无后端/无依赖变更。
- 分支：`feat/phase10.5-frontend-draft-pool`（从最新 `main` 检出，10.4 已并入 main）。
- 代码提交：`23630c6` `feat(panel): p10.5-add-draft-pool-browse-select-pointer-and-combine-ui`。

## 2. 技术实现 (Implementation)

草稿池 UI 全部落在**定稿视图（copy-view）内部**，寄居于 `copy-panel-body`、位于 `copy-content`
**上方**，与「当前稿」区共存——严守 D3/D4「只读草稿池 → 唯一可编辑当前稿 → 去AI化派生」三层，
草稿池纯上游浏览、不可编辑。

数据流（复刻 9.8 既有范式，不新增架构层）：

```
[生成草稿池]按钮 ──POST /api/generate-drafts──▶ state.drafts = 全量扇出草稿数组
                                                    │
                                             renderDraftPool()  # 每 persona 一张卡（名+headline+body 预览）
                                                    │
点某卡「选为主视角」──POST /api/select-draft──▶ selectedDraftId 指针更新（可变、非搬运）
                                                    │
                                             派生当前稿 → 复用既有 /api/copy 渲染 + publish/去AI化工作流
                                                    │
勾选 ≤2 张 +「合并生成」──POST /api/combine-drafts──▶ 池追加一张合并卡（a+b，恒单版）
```

关键设计点：

- **视图归属**：草稿池区 `#draft-pool-section` 内含 `#draft-pool-grid`（卡片网格）+ `#draft-pool-result`
  （结果/失败提示）；「生成草稿池」按钮 `#generate-drafts-btn` 置于 topbar「写推文」旁，二者均以
  「已选中候选」为启用门槛（gated on selection）。
- **指针语义（D4）**：选中卡片 = 主视角指针高亮，非消费/搬运；改选即改当前稿，回看其它草稿池不丢失
  （池只读）。`selectedDraftId` 作为可变状态字段，`renderDraftPool` 据此高亮当前指向卡。
- **合并护栏（D5）**：checkbox 选择，超过 2 张即禁用「合并生成」按钮；合并恒走生产单版
  （`/api/combine-drafts` 不传 `--combine-mode both`），A/B 对照复杂度留在开发期 CLI，不外泄 UI。
- **事件委托**：`draft-pool-grid` 采用委托式 `click`（选主视角）+ `change`（合并勾选）监听，
  避免每次 `renderDraftPool` 重建 DOM 后逐卡重绑（同 `#news-list` 范式）。
- **loading 锁复用**：所有异步按钮沿用 9.8 的 `copyOpInFlight` 锁与结果提示语义；池随候选切换而 reset。
- **函数声明提升**：新增 render/handler 函数插在 `renderSelectionStatus` 前，IIFE 内函数声明提升，插入顺序无副作用。

## 3. 本地验证结果 (Verification)

前端为纯 DOM / 手动验证（仓库无 JS 测试框架），采用「后端回归 + 服务端 smoke test」双保险：

- **后端回归**：`python -m pytest tests/test_review_panel_serve.py -q` → **58 passed**（10.4 端点无回归）。
- **服务端 smoke test**：后台启 `python review_panel/serve.py --port 8791`，`Invoke-WebRequest http://127.0.0.1:8791/`
  → **HTTP 200**，且 `generate-drafts-btn` / `draft-pool-grid` / `combine-drafts-btn` 三处新 DOM 均 `match=True`，
  确认更新后的 index.html 被正确 serve。
- **接线核验**：grep 确认 39 处关键锚点全部就位——DOM 元素、els 缓存（`generateDraftsBtn`/`draftPoolSection`/
  `draftPoolGrid`/`draftPoolResult`/`combineDraftsBtn`）、`renderDraftPool`、三 handler
  （`onGenerateDrafts`/`onSelectDraft`/`onCombineDrafts`）、事件绑定（生成/合并按钮 + grid 委托 click/change）。
- **Lint**：`review_panel/index.html` 零诊断。

## 4. 潜在影响或技术债 (Technical Debt & Caveats)

- **无自动化前端测试**：仓库无 JS 测试框架，草稿池交互（指针高亮切换、合并勾选禁用、卡片渲染）
  仅经服务端 DOM 存在性 smoke test + 人工目检覆盖；真实交互验收留待 **10.7 GATE 面板人工验收**。
- **依赖 10.4 端点契约**：前端严格按 10.4 三端点（generate/select/combine）的请求/响应形状对接；
  端点若变形需同步前端。
- **A/B 双版不进 UI**：`--combine-mode both` 仅开发期 CLI 离线用；面板恒走生产单版——本 TODO 未在
  UI 暴露双版逻辑，符合 D5「选型冻结即生产纪律」。
- **对后续 Phase 影响**：10.6 需补测覆盖新链路（后端为主）；10.7 GATE 将对真实批次做全量扇出 +
  面板浏览/选主视角/改选回看/合并≤2/派生当前稿/失效 humanized 的端到端人工验收。