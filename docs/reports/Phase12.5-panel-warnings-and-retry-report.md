# Phase 12.5 - 面板化 warnings 展示与单份 retry 交付报告

## 1. 改动范围 (Scope)

- `review_panel/drafts_adapter.py`：新增 `run_retry` + `_resolve_retry_perspective` + `_normalize_persona`；`run_fanout` 归一化改为复用 `_normalize_persona`；CLI 加 `--retry <draft_id>`（与 `--combine` 互斥）。
- `review_panel/serve.py`：新增 `handle_retry_draft` + 路由 `POST /api/retry-draft`。
- `review_panel/index.html`：标签 ⚠ 徽标、预览区 warnings 详情块、「重试这一条」按钮、`onRetryDraft`、`renderDraftWarnings`、`hasWarnings`/`isRetryable` 辅助、rule_id→人话标签映射、事件委托、CSS。
- `tests/test_review_panel_drafts_adapter.py`：新增 `RetryTests`（5 例）。
- `tests/test_review_panel_serve.py`：新增 `RetryDraftRouteTests`（4 例）。
- `.cursor/plans/Phase12-c2-body-quality-gate.plan.md`：重构 —— 旧 GATE 移末尾成 12.6（搁置），新 12.5 = 面板化。
- 依赖包：无新增。

## 2. 技术实现 (Implementation)

### 数据流：warnings 从产出到人工兜底闭环

```
run_publish 双闸门耗尽 → draft["warnings"]={body_lint:[rule_id], fabrication:[{kind,quote,reason}]}
  → _draft_entry 保留非空 warnings → 池 JSON → serve 原样透传 → state.drafts[i].warnings
  → ① 展示：标签 ⚠ + 预览区详情块  ② 兜底：点「重试这一条」→ /api/retry-draft
```

A1（dd1952a）已打通数据面（judge 透传 + warnings 保留）。本 TODO 补齐**展示面**与**单份重试**。

### run_retry 反查（命门）

`_resolve_retry_perspective(draft_id, candidate, load_persona_perspective)`：
- `混合视角`（`_DEFAULT_DRAFT_ID`）→ `""`（不注入主视角，与 `run_fanout` 池首同源）。
- 含 `+` 的合并稿 → `ValueError` 拒绝（MVP 不支持合并视角重掷）。
- 单 persona → 在 `_candidate_personas` 里找「归一化后 == draft_id」的原始 id → 注入其蒸馏视角。

归一化单一收敛于 `_normalize_persona`，`run_fanout`（产池）与 `run_retry`（反查）共用同一函数，杜绝口径漂移。

`run_retry` 读池 → 定位 `draft_id` 索引（找不到 `ValueError`）→ 反查视角 → 带 `judge_llm_call`/`max_body_retries` 重跑一版 → `_attach_movie_header` → **in-place** 按索引替换那一条 → 写回。其它草稿零改动（成本从全量再扇出的 N× 降到 1×）。重跑后 warnings 归零则 `_draft_entry` 自动不带该键 → 前端徽标随之消失。

### serve / 前端

- `/api/retry-draft`：subprocess 调 `--retry <draft_id> --judge`，对齐 `handle_generate_drafts` 形状（slug/tmdb_id 从 selection.json 兜底，成功读回整池返回）。面板重试恒带 judge 闸门。
- 前端 `renderDraftWarnings` 列出 body_lint 句式红线（rule_id 经 `_BODY_LINT_LABELS` 翻成人话，表外 id 兜底显原值）+ judge 幻觉 quote/reason；合并稿隐藏重试按钮。`onRetryDraft` 成功后用回传池刷新并重新预览该条。

## 3. 本地验证结果 (Verification)

- 受影响文件：`pytest tests/test_review_panel_drafts_adapter.py tests/test_review_panel_serve.py tests/test_compose_publish.py tests/test_body_lint.py tests/test_body_judge.py -q` → **156 passed in 19.30s**。
- 全量：`pytest -q` → **337 passed, 1 xfailed**（xfailed 为既有预期失败，非本次引入）。两次重跑均稳定通过。
- Lint：改动文件无诊断。

## 4. 潜在影响或技术债 (Technical Debt & Caveats)

- **合并稿 retry 未做**（MVP 边界）：`a+b` 单份重掷需拆号重组复合视角，后端明确 `ValueError` 拒绝、前端隐藏按钮。留后续。
- **12.6 GATE 仍搁置**：旧眼验闸门移到 12.6，当前不给 Go/No-Go 结论 —— 面板化本身是 gate 验收内容的一部分，需真跑面板肉眼验 warnings 展示与 retry 闭环后再回到 gate。
- **retry 成本**：单份重试带 judge，每次约 1×（创作 + judge + ≤K 重试），远低于全量再扇出。
- **分支继承**：本 TODO 在 `feat/phase12.5-gate` 上续做（A1 judge 透传 dd1952a 是其数据面前置），非从 main 新检出。