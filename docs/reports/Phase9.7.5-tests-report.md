# Phase 9.7.5 - 测试覆盖新功能 交付报告

## 1. 改动范围 (Scope)

- `tests/test_review_panel_publish_adapter.py` — 新增 headline >10 字触发 WARNING log 用例。
- `tests/test_review_panel_rewrite_adapter.py` — 新增 headline+链接逐字保留、二次生成覆盖 humanized 且原稿不变两个用例。
- `tests/test_review_panel_serve.py` — 新增 `PublishThenRewriteE2ETests`、`PublishMigratesOldFormatSelectionTests` 两个类。
- 新增/删除依赖：无。仅测试文件，无生产代码改动。

## 2. 技术实现 (Implementation)

本 TODO 为覆盖率 gap 审计 + 填补——9.7.1–9.7.4 各自已带测试，此处只补真实缺口、不重复：

- **gap1 e2e**：`publish → rewrite` 串跑同一份 selection.json，断言 `copies.xiaohongshu` 三字段正确且 `published`/`copy_path` 在 rewrite 后被保留（隔离测试未覆盖跨调用保留）。
- **gap2 迁移穿透 handle_publish**：磁盘放旧格式 selection.json，走 `handle_publish`，断言结果为 copies dict 形状、无顶层字段泄漏（此前只单测 `read_selection` 迁移）。
- **gap3 保留 vs 原稿**：`rewrite_adapter.run_adapter` 后断言 humanized 稿 headline 行 + `## 链接` 段与原稿逐字一致、仅 body 变（此前只隔离测 render）。
- **gap4 重生成幂等**：两次不同 stub 输出跑 run_adapter，断言 humanized 取第二次、原 `_copy_xiaohongshu.md` 字节不变。
- **gap5 warning**：`assertLogs` 断言 `review_panel.publish_adapter` logger 在 headline >10 中文字时发 WARNING（此前只断言不截断）。
- **gap6 parse 边界**：判定已被 `ParseCopyMarkdownTests` 覆盖 → 跳过（不冗余）。

## 3. 本地验证结果 (Verification)

```
python -m pytest tests/test_review_panel_publish_adapter.py tests/test_review_panel_serve.py tests/test_review_panel_rewrite_adapter.py tests/test_review_panel_build_data.py -q
80 passed in 82.79s
```
子代理另跑三件套 `-v` → 55 passed。全绿，无 regression。

## 4. 潜在影响或技术债 (Technical Debt & Caveats)

- 未发现生产 bug——新增断言均符合 9.7.1–9.7.4 现有行为。
- 所有新测试均用注入 stub（run_publish/run_subprocess/call_llm）+ TemporaryDirectory，无真实 LLM / subprocess / 网络依赖，CI 安全。
- 分支继承：`feat/phase9.7.5-tests` 从集成分支检出（已含 9.7.1–9.7.4 合并结果）。