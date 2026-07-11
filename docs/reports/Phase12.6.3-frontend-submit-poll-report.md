# Phase 12.6.3 - 前端 submitJob + pollJob + 6 回调切换 交付报告

## 1. 改动范围 (Scope)

- **改** `review_panel/index.html`（唯一改动文件，原生 JS 无框架无构建）：新增 `submitJob`/`pollJob` + 轮询上限常量；6 处长任务 `apiPost` 调用切换为 `submitJob`。
- 无 `.py` / 计划 / 依赖改动。

## 2. 技术实现 (Implementation)

- **`submitJob(url, payload, kind)`**：`apiPost` 拿 `202+job_id` → 交 `pollJob` 轮询。提交阶段失败（非 202 / `body.ok=false` / 缺 `job_id`，如连到旧版 serve 拿 404）→ 原样把 `submitRes` 传下去，走调用方既有 `else`/`apiErrorText`。
- **`pollJob(jobId)`**：`setTimeout` 循环 `apiGet('/api/job?job_id=')`，把终态**还原成与 `apiPost` 一致的 `{status, ok, body}`**：
  - running → 续轮询；`attempts >= JOB_POLL_MAX_ATTEMPTS` → reject 超时错误（走 `.catch`）。
  - done → `{status: result.http_status, ok: 2xx?, body: result.payload}` resolve，使调用方 `res.ok && res.body.ok` 与同步时代完全等价。
  - error → `{status:500, ok:false, body:{ok:false, stderr}}` resolve（走 `else`，`apiErrorText` 读到 stderr）。
  - 404/网络瞬断 → reject（走 `.catch`）。
- **轮询上限**：`JOB_POLL_MAX_ATTEMPTS=200` × `JOB_POLL_INTERVAL_MS=1500ms` = 300s（5 分钟），依据 retry+judge 实测最长 ~132s，留约 2.3 倍余量覆盖偶发慢请求/LLM 抖动。
- **6 处切换**（`.then/.catch/复位` 三段保持原样）：

| 回调 | url | kind |
|---|---|---|
| onRegenerateBody | /api/regenerate | regenerate |
| onRegenerateHeadline | /api/regenerate | regenerate |
| rewrite/去AI化 | /api/rewrite | rewrite |
| onRetryDraft | /api/retry-draft | retry-draft |
| onGenerateDrafts | /api/generate-drafts | generate-drafts |
| onCombineDrafts | /api/combine-drafts | combine-drafts |

- **快端点保持同步不变**：`/api/select`、`/api/select-draft`、`/api/edit-body`、所有 GET（`/api/data`/`/api/dates`/`/api/copy`/`/api/drafts`/`/api/selection`）。

## 3. 本地验证结果 (Verification)

- **JS 语法校验**（提取 `<script>` 段 `node --check`）：`JS syntax OK, script blocks: 1`。
- **grep 自检**：`apiPost("/api/(regenerate|rewrite|retry-draft|generate-drafts|combine-drafts)"` → 0 处残留；`submitJob`/`pollJob`/`JOB_POLL_MAX_ATTEMPTS` 均已定义，6 处调用点全命中 `submitJob`（L1707/1746/1823/2096/2238/2278）。
- 无前端测试框架，故以静态语法校验 + grep 结构核对为验证手段（面板端到端交互留 12.6.5 GATE 真实重跑肉眼验收）。

## 4. 潜在影响或技术债 (Technical Debt & Caveats)

- **plan 措辞修正**：plan 原写「publish/rewrite/regenerate 三处」，实测前端**无 `/api/publish` 消费者**（后端该端点保留，前端从未调用），实际长任务调用是 6 处（regenerate×2 + rewrite + retry-draft + generate-drafts + combine-drafts）。已在 plan todo content 注明。
- **`kind` 参数**目前仅作调用签名占位透传，未在 UI 按 kind 区分轮询提示——未来可扩展。
- **端到端行为**依赖 12.6.2 后端契约（已在 main）；真实闭环验证在 12.6.5 GATE。
- 分支继承：从最新 `main` 检出 `feat/phase12.6.3-frontend-submit-poll`（12.6.2 已并入 main）。