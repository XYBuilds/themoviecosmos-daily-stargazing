# Phase 9.8.6 - 覆盖新链路测试 交付报告

## 1. 改动范围 (Scope)

- `tests/test_compose_publish.py`：+1 测试（`run_headline` headline-only 鲁棒性）
- `tests/test_review_panel_serve.py`：+1 测试（`replace_body_in_copy_markdown` 边界）
- 无新增/删除第三方依赖。

分支：`feat/phase9.8.6-tests`，从相位分支 `feat/phase9.8-panel-copy-regenerate-and-edit` 检出（已含 9.8.1–9.8.5）。

## 2. 技术实现 (Implementation)

9.8.6 是「新链路测试覆盖 + 无回归」的收敛 TODO。9.8.2–9.8.4 已随各自实现增量写入测试，故本 TODO 先做 criterion→test 审计，仅对**真实 gap** 补测（不填充）。

### criterion → test 覆盖映射

| 验收标准 | 覆盖测试 |
| --- | --- |
| `run_headline` body-aware + headline-only 解析 | `RunHeadlineTests` 4 例 + **新增** `test_run_headline_does_not_leak_body_sentinel_if_llm_misbehaves` |
| `regenerate_adapter --target body\|headline` 覆盖 + humanized 失效 | `RegenerateBodyTests`（body 覆盖保留 headline + 删 humanized、空 body raise）、`RegenerateHeadlineTests`（headline 覆盖保留 body、传 current_body、humanized 保留、空 body 提前 raise）、`ErrorPathTests`、`MainCliTests` |
| `/api/regenerate` + `/api/edit-body` + humanized 失效 + slug 兜底 + 向后兼容 | `RegenerateRouteTests`（target=body 清 humanized_path + 返回新 body/保留旧 headline；target=headline 保留 humanized_path；invalid 400；missing selection 400；subprocess 失败 500）、`EditBodyRouteTests`（成功改 body 保留 headline/链接 + 失效 humanized；空 body 400；缺 copy 404；slug 兜底）、`ReplaceBodyInCopyMarkdownTests` 3 例 + **新增** links-lookalike 例 |
| monolithic prompt golden-snapshot | `HeadlineContractInjectionTests.test_monolithic_render_loses_no_headline_rule_text`、`test_render_c2_prompt_backward_compatible_without_placeholder`、`test_load_headline_contract_reads_shared_file` |

### 新增 2 测试（真实 gap）

1. `tests/test_compose_publish.py::RunHeadlineTests::test_run_headline_does_not_leak_body_sentinel_if_llm_misbehaves`
   - 原有测试都假设 stub LLM 遵守契约（只吐 `【标题】`）。本例注入一个**违约**的 stub（额外吐 `【正文】` 段 + 正文内容），断言 `run_headline` 仍只返回 `{tmdb_id, headline}`，`headline` 不含 `【正文】`/正文文本、结果无 `body` 键 —— 锁死 headline-only 的防泄漏行为。

2. `tests/test_review_panel_serve.py::ReplaceBodyInCopyMarkdownTests::test_new_body_containing_h1_and_links_heading_lookalikes_preserved_verbatim`
   - 新正文含字面 `# ...`（一级标题）或 `## 链接` 词时，断言 `replace_body_in_copy_markdown` 仍按**原文件结构**定位链接分区、逐字保留原链接（`## 链接` 在结果中恰好出现 2 次，body 逐字回填、headline 前缀不变）—— 锁死「替换只重扫原文件、不被新 body 里的 lookalike 误吞」。

第 3 条候选 gap（`/api/regenerate` target=body 的 body=新/headline=旧断言）确认已被 `test_target_body_clears_humanized_path` 覆盖，未补测。

## 3. 本地验证结果 (Verification)

```
python -m pytest tests/test_compose_publish.py tests/test_review_panel_regenerate_adapter.py \
  tests/test_review_panel_serve.py tests/test_review_panel_publish_adapter.py -q
→ 90 passed in 50.50s
```

回归检查：`pytest tests/test_compose_publish.py tests/test_review_panel_rewrite_adapter.py -q → 28 passed`（publish/rewrite 无回归）。

（注：导入 `scripts.compose` 会触发 torch/sentence-transformers 加载，聚合耗时约 50–70s，但不触真实 LLM，全部注入 stub。）

## 4. 潜在影响或技术债 (Technical Debt & Caveats)

- 三种操作的浏览器端到端真实验收（含真实 LLM 重生成）留待 9.8.7 GATE 人工走查。
- 测试均离线（注入 `llm_call` / `run_publish` / `run_headline` / `run_subprocess` stub，serve 直调 `route()` 不起真实端口），CI 友好、无网络/密钥依赖。
- plan 文本提到的 `tests/test_compose.py` 实为 `tests/test_compose_publish.py`（run_headline 与 golden-snapshot 均在此），已按实际文件对齐。