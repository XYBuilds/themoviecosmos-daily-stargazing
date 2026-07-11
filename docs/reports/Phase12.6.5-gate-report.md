# Phase 12.6.5 - GATE 真实重跑面板异步闭环交付报告

## 1. 改动范围 (Scope)
- `review_panel/index.html`
  - 修复 retry job 成功后预览刷新被 `draftOpInFlight` 锁挡住的问题。
  - 同步修正 `generate-drafts` 成功后内部预览和「进入微调」按钮状态恢复。
- `tests/test_review_panel_frontend_state.py`
  - 新增前端状态静态回归测试，锁定 retry / generate-drafts 成功态刷新语义。
- `.cursor/plans/Phase12.6-panel-async-job-framework.plan.md`
  - 将 `p12.6.5-gate` 状态标记为 `complete`。
- 新增/删除依赖包：无。

## 2. 技术实现 (Implementation)
- 根因确认：`onRetryDraft` 在 job 成功后仍处于 `state.draftOpInFlight = true`，旧实现调用受保护的 `onPreviewDraft(id)`，该函数入口命中 in-flight guard 后直接返回，导致正文与 warnings 未重新渲染，旧的「重掷中，稍候…」残留。
- 修复方式：抽出内部预览函数 `previewDraft(draftId, options)`。
  - 用户手动切换草稿仍走 `onPreviewDraft(draftId)`，继续受 `draftOpInFlight` 保护。
  - retry / generate-drafts 成功后的程序内部终态刷新显式传入 `allowDuringInFlight`，允许在收尾清锁前刷新正文、warnings 和预览状态。
- 额外修正：generate-drafts 成功后恢复「进入微调」按钮 disabled 状态，避免同类 in-flight 收尾造成 UI 状态残留。

## 3. 本地验证结果 (Verification)
- 子流程复核：确认根因和修复方向正确，未发现需要继续修复的问题。
- 浏览器 mock 验证：点击「重试这一条」后，轮询完成，正文刷新为新正文，旧「重掷中，稍候…」消失，warnings 清空，进入微调按钮可用。
- `node --check _index_script_tmp.js`
  - 结果：通过。
- `python -m pytest tests/test_review_panel_frontend_state.py -q`
  - 结果：`3 passed`。
- `python -m pytest tests/test_review_panel_frontend_state.py tests/test_review_panel_serve.py tests/test_job_store.py -q`
  - 结果：`80 passed`。
- `python -m pytest -q`
  - 结果：exit code 0，全量回归通过。
- 人工验收：用户已回复 `approve`。

## 4. 潜在影响或技术债 (Technical Debt & Caveats)
- 本次只修复前端状态机在 job 成功收尾阶段的刷新路径，不改后端 job 框架契约。
- `draftOpInFlight` 仍是前端同类操作互斥的核心锁；后续新增长任务回调时，应区分「用户交互入口」和「程序内部终态刷新」，避免再次让内部刷新走受保护入口。
- Phase 12.6 已完成；后续 Phase 12.end gate 可基于异步 job 框架继续验收 C2 正文质量闭环。