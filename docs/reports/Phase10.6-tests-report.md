# Phase 10.6 - 测试覆盖新链路 交付报告

## 1. 改动范围 (Scope)

- `tests/test_review_panel_serve.py`（+34 行）——补 `select-draft` 旧 selection 向后兼容测试。
- 无生产代码改动、无依赖变更。
- 分支：`feat/phase10.6-tests`（从最新 `main` 检出，10.5 已并入 main）。
- 代码提交：`d753ac0` `test(panel): p10.6-add-select-draft-legacy-selection-backward-compat-coverage`。

## 2. 技术实现 (Implementation)

10.6 的定位是**测试收口验收**，而非从零补测——本 Phase 采「每 TODO 增量补测」策略，
新链路的绝大部分测试已随 10.2/10.3/10.4 落地，10.6 负责核对 plan 验收清单、补最后缺口、跑全绿。

**逐项核对已落地覆盖**（plan §Todo 10.6 验收清单）：

| 验收项 | 落地位置 | 状态 |
| --- | --- | --- |
| `load_persona_perspective` 归一化 / 缺文件 / 不回落 card | `test_compose_publish.py::PersonaPerspectiveInjectionTests`（6 例） | ✅ 10.2 |
| `run_publish` 注入视角 + 空注入 golden-snapshot 逐字节等价 | 同上 `test_empty_persona_perspective_is_byte_identical_noop` / `test_run_publish_empty_perspective_matches_default` | ✅ 10.2 |
| drafts_adapter 全量扇出条数 == triggered_by 去重数 | `test_review_panel_drafts_adapter.py::FanoutTests`（4 例） | ✅ 10.3 |
| combine `--combine-mode A/B` 各产单条、`both` 产 `#A/#B` 两条 | `CombineTests::test_combine_mode_{a,b,both}_*`（3 例） | ✅ 10.3 |
| 路线 A 走 run_publish / 路线 B 走文本融合纯函数（不调 LLM） | 同上 + `CombineBodiesPureFunctionTests`（3 例） | ✅ 10.3 |
| combine>2 报错、append 语义、stub 注入 | `test_combine_more_than_two_raises` / `test_combine_preserves_existing_drafts` | ✅ 10.3 |
| `/api/generate-drafts`（成功 + 缺 selection 4xx + subprocess 失败 500） | `GenerateDraftsRouteTests`（4 例） | ✅ 10.4 |
| `/api/select-draft` 指针派生失效 humanized + 写 `selected_draft_id` | `SelectDraftRouteTests`（原 5 例） | ✅ 10.4 |
| `/api/combine-drafts` ≤2 append 单版 / >2 → 4xx 不启 subprocess | `CombineDraftsRouteTests`（3 例） | ✅ 10.4 |
| **向后兼容：旧 selection 无 `selected_draft_id`** | **本 TODO 新增** `test_legacy_selection_without_pointer_field_is_backward_compatible` | ✅ **10.6** |
| slug 兜底 | 三端点均只传 date、slug 经 `_resolve_selected` 回落（隐式覆盖） | ✅ 10.4 |

**本 TODO 唯一新增测试**——补 plan 明列但此前缺显式覆盖的一条：`handle_select_draft` 对
Phase 10 前发布产生的旧 `copies` 条目（有 `published`/`copy_path`/`humanized_path`、
**缺 `selected_draft_id`**）的向后兼容。验证：选中草稿后能正常补上 `selected_draft_id` 指针、
不因缺字段报错，且旧 humanized 稿随 body 变而失效（复用 9.8 D4 stale 清理不变量）。

## 3. 本地验证结果 (Verification)

plan §Todo 10.6 验收命令全绿：

```
$ python -m pytest tests/test_compose_publish.py tests/test_review_panel_drafts_adapter.py \
      tests/test_review_panel_serve.py tests/test_review_panel_publish_adapter.py -q
117 passed in 61.19s
```

相邻回归面（publish/regenerate/rewrite 无回归）：

```
$ python -m pytest tests/test_review_panel_regenerate_adapter.py \
      tests/test_review_panel_rewrite_adapter.py -q
15 passed in 7.16s
```

- 新增测试 `test_legacy_selection_without_pointer_field_is_backward_compatible` 通过。
- 既有 publish/regenerate/rewrite/copy 测试无回归（117 + 15 全绿）。

## 4. 潜在影响或技术债 (Technical Debt & Caveats)

- **纯测试 TODO，零生产代码改动**：不改变任何运行时行为，无新风险。
- **plan 文件名口径**：plan §Todo 10.6 写的 `tests/test_compose.py` 实际对应仓库既有的
  `tests/test_compose_publish.py`（C2 定稿测试的历史命名），persona 注入测试已在其中，
  无需新建同名文件。
- **前端无自动化测试**：草稿池 UI（10.5）仍为手动 / 服务端 DOM smoke test 覆盖，
  真实交互验收留待 **10.7 GATE 面板人工验收**——这是本 Phase 唯一的测试面缺口，
  受限于仓库无 JS 测试框架，属既有约束而非本 TODO 引入。
- **后续 Phase**：10.7 为 `[需人工验收]` GATE，将对真实批次 `2026-07-06` 做全量扇出 +
  面板端到端验收 + A/B 选型冻结 + 文档同步，需人工 Go/No-Go。