# Phase 9.8.5 - 面板前端：正文编辑 + 重生成按钮 交付报告

## 1. 改动范围 (Scope)

- `review_panel/index.html`（单文件原生 JS 面板，无框架无构建）
  - 定稿区（copy view）新增总编三种「定点操控」能力的前端交互。
- 无新增/删除第三方依赖（零依赖约束不变）。

分支继承关系：本 TODO 分支 `feat/phase9.8.5-frontend-edit-regenerate` 从相位分支 `feat/phase9.8-panel-copy-regenerate-and-edit` 检出，已继承 9.8.1–9.8.4（headline 契约 SSOT、`run_headline`、`regenerate_adapter.py`、serve `/api/regenerate` + `/api/edit-body`）。

## 2. 技术实现 (Implementation)

### 状态模型（沿用 9.7.4 二档，不加版本层）
`state` 新增字段：
- `headline`：定稿标题移入 state 驱动，`renderCopyHeadline()` 重渲染；「重生成标题」只需改 `state.headline` 再重渲染。
- `editingBody`：正文展示态 ↔ 编辑态开关。
- `copyOpInFlight`：编辑/重生成正文/重生成标题/去AI化的互斥锁，禁止并发 LLM 操作。

### DOM
- 静态：`#copy-actions-slot`（置于 `#copy-content` 内、`#copy-body` 之后）。
- 动态（非编辑态）：`#edit-body-btn` `#regen-body-btn` `#regen-headline-btn` + `#copy-op-result`。
- 动态（编辑态）：`#save-body-btn` `#cancel-body-btn` + `#copy-op-result`，`#copy-body` 内渲染 `#copy-body-editor`（textarea，prefill `state.originalBody`）。

### 新增/修改函数
- 新增：`renderCopyHeadline` / `renderCopyActions` / `setCopyOpButtonsDisabled` / `clearCopyOpResult` / `showCopyOpResult` / `onEditBodyClick` / `onCancelEditBody` / `onSaveBody` / `onRegenerateBody` / `onRegenerateHeadline`。
- 修改 `showCopyContent`：改为 `state.headline = headline; renderCopyHeadline()`，并追加 `renderCopyActions()`。
- 修改 `renderCopyBody`：编辑态渲染 textarea；否则按 `humanizeView` 显示原版/去AI化正文。
- 修改 `loadCopy`：成功回调补 `state.headline = body.headline || ""`。

### 语义落地（对齐 plan D4/D5）
- **编辑正文（D5）**：点「编辑正文」先强制 `humanizeView="original"`（编辑只作用原稿），保存走 `POST /api/edit-body`，无 LLM。
- **重生成正文（D2）**：`POST /api/regenerate {target:"body"}`，只覆盖 body。
- **重生成标题（D3）**：`POST /api/regenerate {target:"headline"}`，body-aware，仅覆盖 headline。
- **覆盖 + humanized 失效（D4）**：保存/重生成正文成功后 `humanizedBody=null` + `humanizeView="original"` + 重渲染 `renderHumanizeSlot()`/`renderCopyBody()`，去AI化 toggle 自动隐藏、按钮回落「去AI化」；**重生成标题不触碰 humanized**。
- 交互护栏：LLM 进行中按钮显示 spinner 并禁用整组；结果/失败提示复用 `.humanize-result` / `.humanize-result.fail` 样式；控制类文案用中文字面量（与既有「写推文」「去AI化」一致，不接入 `textFor()`）。

### CSS
新增 `.copy-body-editor`(+`:focus`)、`.copy-actions-slot`、`.copy-action-btn`(+`:hover:not(:disabled)`/`:disabled`)、`.copy-action-btn.primary`(+hover)，沿用 `--accent`/`--ink`/`--line`/`--bg-card`/`--mono` 等既有变量与暗色调风格。

## 3. 本地验证结果 (Verification)

- JS 语法自检：提取 `<script>` 内嵌 JS 到临时文件 `node --check` → `SYNTAX_OK`（临时文件已删除）。
- 后端回归：`python -m pytest tests/test_review_panel_serve.py -q` → **45 passed in 6.34s**（前端改动不触及后端契约，无回归）。
- API 契约核对：`/api/edit-body` 返回 `{ok, headline, body}`、`/api/regenerate` 返回 `{ok, target, headline, body, stderr}`，前端读取字段一致；tmdb_id 由服务端从 selection.json 取，前端不发送。

## 4. 潜在影响或技术债 (Technical Debt & Caveats)

- 前端视觉与真实 LLM 端到端交互（三种操作的浏览器实测）留到 9.8.7 GATE 人工验收统一走查。
- 重生成为耗时 LLM 操作，当前仅用按钮 spinner + 互斥锁提示；未做超时/取消（与既有 `/api/rewrite` 去AI化按钮口径一致，暂不扩展）。
- 平台范围仍仅 xiaohongshu；X/Reddit tab 灰置，编辑/重生成按钮只在有定稿的 `#copy-content` 中出现。