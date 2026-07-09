# Phase 9.8.1 - headline 契约 SSOT + body-aware headline prompt + ADR-0016 交付报告

## 1. 改动范围 (Scope)

新增文件：
- `prompts/_shared/xiaohongshu_headline_contract.md` — headline 硬规则单一事实源（SSOT）
- `prompts/compose_publish_xiaohongshu_headline.md` — body-aware、headline-only 重生成 prompt
- `docs/adr/0016-panel-editorial-regeneration-and-inline-edit.md` — 记录 Phase 9.8 的 D0–D7 决策

编辑文件：
- `prompts/compose_publish_xiaohongshu.md` — headline 段由内联规则改为 `{{headline_contract}}` 占位符注入
- `scripts/compose.py` — 新增 `load_headline_contract()` + 常量 `_HEADLINE_CONTRACT_REL`；`render_c2_prompt` 增加可选参数 `headline_contract`；`run_publish` 加载并注入契约
- `tests/test_compose_publish.py` — 新增 `HeadlineContractInjectionTests`（golden-snapshot 回归护栏）

依赖变更：无（纯标准库 + 现有 prompt 加载机制）。

## 2. 技术实现 (Implementation)

**D1 决策落地：injection 方案（非降级方案）。** golden-snapshot 证明抽取后 monolithic 渲染结果不丢任一 headline 硬规则文本，故采用架构更干净的注入路径，而非「内联保留 + 注释指向 SSOT」的降级。

数据流（headline 规则的单一事实源 + 双向复用）：

```
prompts/_shared/xiaohongshu_headline_contract.md   ← 唯一规则文本
        │  (被两处 prompt 各自的占位符引用)
        ├── compose_publish_xiaohongshu.md          {{headline_contract}}  (monolithic 首发稿)
        └── compose_publish_xiaohongshu_headline.md {{headline_contract}}  (headline-only 重生成，9.8.2 起用)
```

注入机制（保持 `render_c2_prompt` 的纯函数/DSL 风格）：

```
run_publish(...)
  headline_contract = load_headline_contract(prompts_dir)   # 查找顺序同 load_c2_template
  render_c2_prompt(template, news_context, selected_movie, judge_kernel, headline_contract)
    → .replace("{{headline_contract}}", headline_contract or "")   # 模板无占位符时为 no-op，向后兼容
```

关键签名：
- `render_c2_prompt(template, news_context, selected_movie, judge_kernel, headline_contract: str = "") -> str`
- `load_headline_contract(prompts_dir: Path | None = None) -> str`

**向后兼容不变量**：任何不含 `{{headline_contract}}` 占位符的模板，其渲染结果与本次改动前逐字节一致（新增的 `.replace` 对无占位符文本为 no-op）——由测试 (c) 断言。

## 3. 本地验证结果 (Verification)

```
python -m pytest tests/test_compose_publish.py tests/test_main_publish.py tests/test_review_panel_publish_adapter.py -q
.........................................                                [100%]
41 passed in 51.31s
```

新增 golden-snapshot 三项断言：
- (a) `load_headline_contract` 读到共享文件且含关键规则（≤10 中文字 / 不裸片名 / 不剧透）
- (b) 渲染真实 monolithic prompt 后：无 `{{headline_contract}}` 残留 + 每条 headline 硬规则文本均在
- (c) 无占位符模板经新参数渲染结果不变（向后兼容）

## 4. 潜在影响或技术债 (Technical Debt & Caveats)

- **对后续 Phase 的依赖**：9.8.2 的 `run_headline` 将复用 `load_headline_contract` + 新 headline prompt；9.8.3 adapter 依赖 9.8.2。本 TODO 是链路起点，不引入阻塞。
- **GATE 验过的首发 prompt 被触碰**：已用 golden-snapshot 兜底证明无回归；后续若调整 headline 硬规则（如放宽字数），只改 `_shared` 契约一处即可，两处 prompt 自动同步。
- **环境说明**：本仓库当前无 `.venv`，验证使用系统 Python 3.14.3，功能验证不受影响。
- **无人工验收阻断**：本 TODO 非 `[需人工验收]`，按标准流水线直接进入合并。