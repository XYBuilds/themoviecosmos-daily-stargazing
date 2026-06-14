# Phase 4.1 - C1 审核稿 (MVP) 交付报告

## 1. 改动范围 (Scope)

改动文件：

- `scripts/copywriter.py`（新增）：copywriter 入口脚本，本 TODO 实现 `--stage review`（C1）。
- `tests/test_copywriter_review.py`（新增）：C1 review stage 离线单测，15 条。
- `prompts/C1_copywriter_review.md`（修改）：`{{candidates}}` 变量字段说明补一行 `center_dimensions` 切面可选参考提示（仅字段描述，写作措辞不变）。

依赖包：无新增。复用既有 `scripts/lib/llm`、`scripts/lib/env`、`scripts/lib/paths`、`unittest`。

分支：`feat/phase4.1-c1-review`（从最新 `main` 检出，Phase 3 与 Phase 4 plan 均已并入 main）。
提交：`7b92d5d feat(copywriter): p4.1-implement-c1-review-stage`。

## 2. 技术实现 (Implementation)

数据流向（read-only 消费 Phase 3.11 全批产物，不重跑链路）：

```
retrieve.json
  ├─ candidates[]      → 每条提取 title/year/overview/triggered_by/movie_url
  │                      + match_diagnostics 内的 center_dimensions（软提示）
  ├─ per_agent[]       → 取相似度最高的一条 persona-semantic 文本入新闻语境
  └─ a1_oracle         → 显式忽略，不入候选
reality.json           → news_context（title + description）
llm-judge-scores-thinking-enabled.json
                       → 按 tmdb_id(+run_id) 建索引回填 judge_score（缺失视为空）
        │
        ▼
  组装 C1 prompt（{{news_context}} + {{candidates}}）
        │
        ▼
  LLM（MiMo 主 / DeepSeek 兜底）
        │
        ▼
  解析多段纯文本（段首《片名》(年份)）→ 映射回 tmdb_id → review_copies[]
```

模块职责（functional 风格，纯函数 + 一个 orchestration）：

- `load_retrieve` / `load_news` / `load_judge_scores`：产物加载与 judge 索引构建。
- 候选字段提取 + persona_id 自然语言化 + 软提示透传（`center_dimensions` / `POV变换`，措辞标注「可参考、非强制」）。
- `run_review`：编排单次 review（组装 → 调用 LLM → 解析），单路失败记入 `errors` 不阻断。
- `result_to_payload`：序列化为 plan 约定的 `{review_copies[], errors[]}` JSON 形状。
- CLI：`--stage review --retrieve-json ... --out ...`，`--provider` 透传。

关键契约修正（已对齐 3.11 真实产物）：`center_dimensions` / `search_unit_kinds` 嵌在 `candidate["match_diagnostics"]` 内，非顶层；`judge_score` 不在 `retrieve.json`，从批次根 judge 文件按 `tmdb_id` 回填。

## 3. 本地验证结果 (Verification)

- 定向单测：`python -m unittest tests.test_copywriter_review` → 15/15 pass。覆盖 N 候选→N review_copies、中文/无 hashtag、A1/oracle 不出现、软提示透传、多段解析边界。
- 真实产物离线核验（`01-grid-outage`，注入 fake LLM）：19 候选 → 19 review_copies，0 errors，judge_score 回填 10/19（screening-only 可空，符合预期），`triggered_by` / `center_dimensions` 软提示正确透传，无 oracle。
- 全量回归（离线，`HF_HUB_OFFLINE=1` / `TRANSFORMERS_OFFLINE=1`）：`python -m unittest` → 209 OK，skipped=1，无 regression。
- 临时日志 `output/_phase41_test.log` 已清理。

## 4. 潜在影响或技术债 (Technical Debt & Caveats)

- 4.1 仅实现 `--stage review` 的核心数据加载、组装、解析；落 Obsidian Markdown 候选块与 README 在 4.2。
- C1 一次 prompt 含多部候选，token 随候选数增长；MVP ≤8 部通常可接受，本次 19 候选属离线核验场景。
- OPEN a 软提示只透传不强制，规避生成层 POV 的事实漂移风险。
- prompt 正文措辞迭代属产品调整，与本代码 PR 分开。