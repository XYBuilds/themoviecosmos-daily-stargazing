# Phase 5.4 - 抓取源改进 交付报告

## 1. 改动范围 (Scope)

改动文件：
- `scripts/fetch_news.py` — Guardian API 默认源、section 宽进黑名单、tone 格式感知抽取、tone DROP、--pick 降级
- `scripts/retrieve.py` — HF local_files_only 修复
- `scripts/run_eval.py` — 阶段进度日志
- `scripts/llm_judge.py` — judge 进度日志
- `scripts/compose.py` — compose 进度日志
- `tests/test_fetch_news.py` — tone DROP/section/抽取路由测试
- `tests/test_fetch_news_cli.py` — 适配默认 provider
- `docs/adr/0014-news-source-selection-and-automation-boundary.md` — ADR D1-D6
- `docs/SSOT/news-source-selection-design.md` — 设计 SSOT
- `.cursor/plans/Phase5-fetch-news.plan.md` — 5.4 描述重写

新增依赖：无

## 2. 技术实现 (Implementation)

核心设计详见 `docs/SSOT/news-source-selection-design.md`：
- **Guardian API 默认源**：CLI 默认 `--provider guardian-api`，请求带 `show-tags=all` 获取 tone 标签
- **Section 宽进黑名单制**（5 类）：meta/工具页、功能页、地方新闻、行业垂直、低事件旅行内容(travel)
- **Tone 格式感知抽取**：EXTRACTION_TABLE 数据表驱动查表；多 tone 按具体度仲裁；tone/features 走段长衰减启发式；无 tone 默认前 3 段
- **Tone DROP 黑名单**：minutebyminute/letters/competitions 整条丢弃（DROP 优先于多 tone 仲裁）
- **--pick 降级**：从生产默认入口降为调试/评测开关，新闻侧全自动
- **进度日志**：run_eval/judge/compose 加阶段+persona+candidate 进度输出（stderr, flush=True）
- **HF 修复**：retrieve.py `SentenceTransformer(MODEL_NAME, local_files_only=True)` 避免联网卡死

## 3. 本地验证结果 (Verification)

```
$ python -m pytest tests/test_fetch_news.py tests/test_fetch_news_cli.py tests/test_fetch_news_dedup.py -q
32 passed in ~8s
```

端到端 smoke test（1 条真实 Guardian 新闻 → A0 → 12 persona → retrieve → judge → C1 文案）：
- run_eval: 12 persona 串行完成，进度日志正常（每 persona ~25-28s）
- judge: 19 candidates scored in ~4.5min（workers=4 并发）
- compose review: 1 次 LLM，~48s，C1 审核卡正常产出
- 新闻文本质量：A0 解构出 14 个 element，下游无异常

## 4. 潜在影响或技术债 (Technical Debt & Caveats)

- **分支职责越界**：进度日志（run_eval/judge/compose）严格说属 Phase 6 编排职责；用户确认在 5.4 正式保留
- **热度排序 Post-MVP**（ADR-0014 D4）：新闻侧当前无选题闸门，全量进入 agents
- **Judge 未校准**（ADR-0014 D5）：smoke test 中 trust_status=不采信
- **共振偏表层**：smoke test 候选偏字面联想，属 persona/judge/召回层课题
- **tone/quizzes 未覆盖**：后续可补 DROP
- **本分支继承自** `fix/phase5.4-agents-prompt-path`