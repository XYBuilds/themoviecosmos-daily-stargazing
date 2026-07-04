# Phase 6.2 - main.py 日报管线 交付报告

## 1. 改动范围 (Scope)

- 改动的文件列表：
  - `scripts/main.py`（modified，原 16 行空壳 → 完整实现，408 行）
  - `tests/test_main_pipeline.py`（新增，10 个单元测试）
  - `.cursor/plans/Phase6-main-integration.plan.md`（`p6-main-pipeline` 状态 `pending` → `completed`）
  - `docs/reports/Phase6.2-main-pipeline-report.md`（本报告，新增）
- 新增/删除的依赖包：无。全部复用 6.0（`RunOptions`）、6.1（`render_briefing.py`）及已有模块（`extract.py`/`expand.py`/`rewrite.py`/`retrieve.py`/`compose.py`/`fetch_news.py`）。
- `output/Daily_Briefing/` 下的运行产物（`2026-07-05.md`、`2026-07-05_candidates.json`）为本地 e2e 验证的真实产出示例，未纳入本次提交（该目录被 `.gitignore` 的 `output/` 规则排除，git 中仅追踪 `.gitkeep`）。

## 2. 技术实现 (Implementation)

### CLI 参数全集

```text
python scripts/main.py --news-file <path>          # 三者互斥，任选其一（必需其一）
python scripts/main.py --url <url> [--title T] [--description D]
python scripts/main.py --pick N                     # 1-based，从 fetch_news.fetch_guardian_api() 结果中选取
python scripts/main.py ... --date YYYY-MM-DD         # 默认今天（UTC）
python scripts/main.py ... --provider {mimo,deepseek}
python scripts/main.py ... --no-copy                 # 跳过 C1
python scripts/main.py ... --personas N              # 复用 RunOptions.persona_limit
python scripts/main.py ... --skip-expand             # 复用 RunOptions.skip_expand
python scripts/main.py ... --judge-topk K            # 复用 RunOptions.judge_topk，默认 2
python scripts/main.py ... --force                   # 复用 RunOptions.force，覆盖同日已存在的日报
```

无参数直接运行：`build_parser().print_usage()` 输出用法到 stderr，exit code 2。

### 管线调用顺序（`run_daily_pipeline` + `_run_cli`）

```
resolve_news(args)                                  # --news-file / --url(+fallback) / --pick N
  └─ --pick N → fetch_news.fetch_guardian_api() 取候选列表，1-based 索引，越界报错；
                 fetch_news.mark_selected(payload) 标记已选；再走 _news_from_dict 转 NewsItem
  └─ --url    → fetch_news.build_url_news_payload(url, title=, description=) → mark_selected → _news_from_dict
  └─ --news-file → agents.load_news_from_file(path)

[同日覆盖保护] briefing_path = output/Daily_Briefing/{date}.md
  若已存在且非 --force → print error, exit 2（对齐 run_eval.py 覆盖保护语义）

[stage 1/4] extract.run_deconstruct(news, provider=)         # A0
[stage 2/4] expand.run_expansion(deconstruction, provider=)  # 可 --skip-expand 跳过，expansion=None
[stage 3/4] for persona_id in rewrite.list_persona_ids()[:persona_limit]:
                rewrite.run_persona_pipeline(persona_id, deconstruction, provider=, expansion=)
             → 收集 agents_list（_persona_result_to_agent，镜像 run_eval._persona_result_to_agent）
[stage 4/4] retrieve.retrieve_from_agents(agents_list, errors, top_k=judge_topk)

[stage 5/5，若非 --no-copy] compose.run_review(retrieve_result, news_dict, provider=)
             → ReviewResult.review_copies → _review_copies_payload() 转 [{"tmdb_id":, "copy":}, ...]

build_daily_briefing(date, news_dict, errors, retrieve_result, review_copies=)
             → 组装 Markdown 字符串，写 output/Daily_Briefing/{date}.md
             → 同目录写 output/Daily_Briefing/{date}_candidates.json（整份 retrieve_result 落盘）
```

### Markdown 组装（`build_daily_briefing`）

复用 `render_briefing.py`（6.1 产物）的三个纯函数：
- `_format_reality_body(date, news)` → 现实波澜
- `_format_candidates_markdown(date, candidates, copies=review_copies)` → 候选星轨。`candidates` 显式来自 `retrieve_result.get("candidates")`（生产池），不是 `human_candidates`、`audit_pool`，也不是 `a1_oracle`
- `_format_errors(errors)` → errors 区块

main.py 新写了两个 prod 专属 helper（未加入 `render_briefing.py`）：
- `_format_oracle_appendix(retrieve_result)` — A1 held-out oracle 附录，只读 `retrieve_result["a1_oracle"]` / `["oracle_comparison"]`
- `_format_footer(retrieve_result)` — meta 脚注，只读 `retrieve_result["meta"]`

**放在 main.py 而非 render_briefing.py 的取舍**：oracle 附录和脚注是 main.py（prod 管线）专属语义 —— `run_eval.py`（eval 管线）目前没有消费 `a1_oracle`/`oracle_comparison` 渲染为附录的需求，也没有对应的 CLI 输出位置。把这两个函数放进共享的 `render_briefing.py` 会让该模块承载 prod-only 的组装逻辑，违反 6.1 report 确立的原则（细粒度、可复用的渲染函数留在 `render_briefing.py`；调用方专属的整体组装留在各自入口文件）。如果未来 `run_eval.py` 也需要渲染 oracle 附录，再按需上提为共享函数。

### `output/Daily_Briefing/{date}.md` + `{date}_candidates.json` 落盘设计

- `{date}.md`：单份日报 Markdown，结构为 `# 每日星轨观测 · {date}` → 现实波澜 → 候选星轨（共 N 部）→ errors → 附录 · A1 Reality Recorder → 脚注。
- `{date}_candidates.json`：**完整的 `retrieve_result` dict**（`per_agent`/`candidates`/`human_candidates`/`audit_pool`/`funnel`/`a1_oracle`/`oracle_comparison`/`divergence`/`meta`），`json.dumps(..., ensure_ascii=False, indent=2)`。
  - 决策：落盘整份 retrieve_result 而非仅 `candidates` 子集，理由是 6.3（publish 子命令）需要按 `tmdb_id` 反查 candidate 的完整字段（`title`/`release_year`/`movie_url`/`overview`/`genres`/`match_diagnostics` 等），落盘全量结果避免 6.3 还要重新跑一次 retrieve。
  - 6.3 实现时应从该文件的顶层 `candidates` 列表按 `tmdb_id` 过滤，**不要**误用 `a1_oracle`（该键在无命中时为 `null`，需要做 falsy 检查）或 `human_candidates`（人工审阅池，字段与 `candidates` 高度重叠但语义不同，是否等价需 6.3 自行核实，本次未做该判断）。

### `ReviewResult` / `ReviewCopy` 真实字段确认

读取 `scripts/compose.py` 第 113-148 行源码确认：

```python
@dataclass
class ReviewCopy:
    tmdb_id: int | str
    title: str
    year: int | None
    triggered_by: list[str]
    center_dimensions: list[str]
    db_projection: dict[str, Any] = field(default_factory=dict)
    movie_url: str = ""
    news_url: str = ""
    judge_score: int | None = None
    judge_rationale_en: str = ""
    judge_causal_test_en: str = ""
    judge_resonance_type: str = ""
    judge_rationale_zh: str = ""
    judge_causal_test_zh: str = ""

@dataclass
class ReviewResult:
    review_copies: list[ReviewCopy] = field(default_factory=list)
    errors: list[dict[str, Any]] = field(default_factory=list)
    dropped_candidates: list[dict[str, Any]] = field(default_factory=list)
    min_judge: int | None = None
```

**结论**：`ReviewCopy` 没有 `copy_text` 属性。`_review_copies_payload()` 用 `copy.judge_rationale_zh or copy.judge_causal_test_zh` 合成中文文案文本，因为这是卡片上唯一已由 LLM 授权的中文叙述字段（compose.py 的设计是"事实来自 DB 投影，判据来自 judge，LLM 只负责英文判据的忠实中译"，本身不产出独立的营销文案）。`tests/test_copywriter_review.py` 中依赖 `copy.copy_text` 属性（以及若干 mojibake 断言字符串）的 8 个失败用例是既有测试对不存在字段的历史遗留误判，与本次 main.py 改动无关；本次改动前后该 8 个失败数量不变，未新增、未修复。

## 3. 本地验证结果 (Verification)

### 单元测试

`python -m pytest tests/ -q`：

```
8 failed, 279 passed, 1 skipped in 47.09s
```

失败集合（8 个，均在 `tests/test_copywriter_review.py`，与既有基线一致，本次改动未新增/未减少）：
```
FAILED tests/test_copywriter_review.py::TestCandidateBlock::test_block_has_soft_hints_genres_and_judge_rationale
FAILED tests/test_copywriter_review.py::TestCandidateBlock::test_missing_year_renders_dash
FAILED tests/test_copywriter_review.py::TestRunReview::test_n_candidates_yield_n_copies
FAILED tests/test_copywriter_review.py::TestRunReview::test_payload_shape
FAILED tests/test_copywriter_review.py::TestMarkdownRendering::test_block_has_required_fields
FAILED tests/test_copywriter_review.py::TestMarkdownRendering::test_copy_text_carries_no_hashtag
FAILED tests/test_copywriter_review.py::TestMarkdownRendering::test_document_has_one_block_per_candidate
FAILED tests/test_copywriter_review.py::TestMarkdownRendering::test_missing_year_renders_dash
```
`tests/test_main_pipeline.py`（本次新增的 10 个测试）不在失败列表中，全部通过。

### e2e 真实产出验证

```powershell
python scripts/main.py --news-file tests/sample_news.json --no-copy --personas 2 --date 2026-07-05
python scripts/main.py --news-file tests/sample_news.json --personas 2 --date 2026-07-05 --force
```

- 第一次（`--no-copy`）：exit 0，产出 `output/Daily_Briefing/2026-07-05.md`，结构核对：`# 每日星轨观测 · 2026-07-05` → 现实波澜（title/source/pub_time/summary 均从 `_format_reality_body` 正确取值）→ 候选星轨（共 12 部，每条含 tmdb_id、自动打分、相似度、genres/language、overview、`movie_url` 直取 retrieve 字段未手拼、命中视角/碎片）→ errors（无）→ 附录（无 A1 oracle 数据，因 baseline 查询未产生命中）→ 脚注。
- 第二次（含 C1，`--force` 覆盖）：exit 0，产出同一 `.md`（含 C1 文案）+ `2026-07-05_candidates.json`（61697 字节，完整 retrieve_result）。
- 读取 `2026-07-05_candidates.json` 复核 A1 隔离：顶层键 `candidates`（12 条，含 `429918 Survival Family` 等）、`human_candidates`（同规模池）、`audit_pool: []`、`funnel`、`a1_oracle: null`、`oracle_comparison: null`（本次 run 的 baseline 查询无命中）、`divergence`、`meta`（`query_count: 10`、`raw_hit_count: 20`、`candidate_count: 12`）。确认 `candidates`/`human_candidates` 列表中未出现任何 a1_oracle 特有字段（如 `raw_hit_count`/`hit_tmdb_ids` 均只出现在 `a1_oracle` 键下，而该键本身为 `null`），A1 与生产池物理隔离。

## 4. 潜在影响或技术债 (Technical Debt & Caveats)

- **A1 隔离验证的局限**：本次 e2e 实跑的样例新闻恰好触发 `a1_oracle: null`（baseline 查询无命中），因此未能在真实产出中直接肉眼验证"a1_oracle 有数据时附录正确渲染、且不泄入候选"的完整路径；该路径已通过 `tests/test_main_pipeline.py` 中构造的假 retrieve_payload（含非空 a1_oracle）单元测试覆盖并断言候选区块不含 A1 特有内容，但建议 6.3/6.4 阶段用一次真实产生 a1_oracle 命中的新闻样例再做一次 e2e 复核。
- **`human_candidates` 与 `candidates` 的语义边界未澄清**：两者在样例产出中字段高度重叠，本次未深入核实其差异（是否为同一份数据的不同视图，或存在过滤差异）。6.3 若需要用 `human_candidates` 而非 `candidates` 做发布查找，需要先自行确认 `retrieve_from_agents` 的语义。
- **oracle 附录/脚注渲染函数留在 main.py**：如 6.4 文档阶段或未来 eval 侧也需要类似附录，需要评估是否上提到 `render_briefing.py`，避免逻辑漂移到两处维护。
- **`test_copywriter_review.py` 的 8 个既有失败未修复**：本报告只是确认与本次改动无关，未做修复；若后续 phase 需要该测试文件全绿，需要单独排期修复 `copy_text` 属性缺失和 mojibake 断言字符串问题。
- **6.3 关键依赖**：`{date}_candidates.json` 是 6.3 publish 子命令按 `tmdb_id` 查找 candidate 的唯一数据源，其 schema（顶层 9 个键，`candidates` 列表内字段）已在本报告固化，6.3 实现前应视为契约。