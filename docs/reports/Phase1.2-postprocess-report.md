# Phase 1.2 - 后处理与去实体化告警 交付报告

## 1. 改动范围 (Scope)

- `scripts/agents.py` — `post_process_output()`、长度截断、专名/八股启发式、`refusal` 检测
- `.cursor/plans/Phase1-agents-pseudo-overview.plan.md` — Todo 1.2 标记 complete

## 2. 技术实现 (Implementation)

- **60–120 words**：超过 120 词在最近句号处截断并 `truncated_over_length`；少于 40 词 `short_output`（不丢弃）
- **去实体化**：连续大写词组、品牌词表、新闻八股 → `deentify_warning: ...`（保留 text）
- **拒绝话术**：命中则清空 text、`error=model refusal detected`，由 `run_all` 写入顶层 `errors`
- 在 `_run_one_agent` 成功路径于 `minimal_clean` 之后调用 `post_process_output`

## 3. 本地验证结果 (Verification)

```text
python -c "… post_process_output unit tests …"
postprocess unit OK
```

（CLI 端到端在 Todo 1.3 验收。）

## 4. 潜在影响或技术债 (Technical Debt & Caveats)

- 启发式可能误报/漏报专名；MVP 仅打标
- Todo 1.3 将提供 `--news-file` 与进程退出码（全部失败才非零）
