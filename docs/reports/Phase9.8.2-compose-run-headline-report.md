# Phase 9.8.2 - run_headline + body 重生成路径 交付报告

## 1. 改动范围 (Scope)

编辑文件：
- `scripts/compose.py` — 新增 headline-only 重生成链路（+88 行，未删改任何现有函数）
- `tests/test_compose_publish.py` — 新增 `RunHeadlineTests`（+67 行）

依赖变更：无。

## 2. 技术实现 (Implementation)

**D2/D3 决策落地：headline 与 body 走两条不对称路径，只为 headline 建新函数。**

正文重生成（D2）刻意**不建独立 body prompt/函数**——下游 adapter 直接复用 `run_publish` 全语境创作，只取返回的 `body` 字段，丢弃顺带产出的 headline（YAGNI）。故本 TODO 只落 headline-only 路径。

新增的 headline-only 链路（与 monolithic publish 链路对称但独立选取模板）：

```
run_headline(candidate, news, current_body, *, provider, judge, platform, prompts_dir, llm_call)
  ├── load_headline_template(platform)        # compose_publish_{platform}_headline.md（9.8.1 产物）
  ├── build_news_context(news, "")            # 复用
  ├── format_selected_movie_block(candidate)  # 复用
  ├── load_headline_contract(prompts_dir)     # 9.8.1 的共享契约 SSOT
  ├── render_headline_prompt(...)             # 注入 news/movie/current_body/headline_contract
  ├── LLM（_HEADLINE_SYSTEM_MESSAGE，只产标题）│ 与 run_publish 同形，可注入 llm_call 离线测
  └── parse_publish_output(raw)[0]            # 复用 headline 分支，只取首行 → 丢 body
  → return {"tmdb_id", "headline"}
```

关键签名：
- `run_headline(candidate, news, current_body, *, provider=None, judge=None, platform="xiaohongshu", prompts_dir=None, llm_call=None) -> dict`
- `load_headline_template(platform="xiaohongshu", prompts_dir=None) -> str`
- `render_headline_prompt(template, news_context, selected_movie, current_body, headline_contract="") -> str`

设计要点：
- **复用 `parse_publish_output` 的 headline 分支**，不为 headline-only 另写解析逻辑；即使模型误吐多行，也只取首行（鲁棒性）。
- **`judge` 参数保留但不注入**：headline prompt 是有意的 judge-free 设计，参数仅为与 `run_publish` 签名对齐，已加注释。
- **专用 `_HEADLINE_SYSTEM_MESSAGE`**：明确「只产一句标题、不产正文」，避免复用 `_PUBLISH_SYSTEM_MESSAGE`（要求同时产标题+正文）导致模型误吐正文块。

## 3. 本地验证结果 (Verification)

```
python -m pytest tests/test_compose_publish.py tests/test_main_publish.py tests/test_review_panel_publish_adapter.py -q
.............................................                            [100%]
45 passed in 46.18s
```

`RunHeadlineTests` 四项：
- headline-only 返回 `{tmdb_id, headline}`（无 body key，sentinel 已剥）
- body-aware：`current_body` 文本进入渲染 prompt，四个占位符全部解析（无残留）
- 多行鲁棒：模型误吐多行时只保留首行标题
- 共享契约嵌入：`render_headline_prompt` 注入契约后含 ≤10 字硬规则

`run_publish` 路径无回归（既有 publish/main/adapter 测试全绿）。

## 4. 潜在影响或技术债 (Technical Debt & Caveats)

- **对后续 Phase 的依赖**：9.8.3 的 `regenerate_adapter.py` 将 `--target headline` 调 `run_headline`、`--target body` 调 `run_publish` 取 body。本 TODO 是 adapter 的直接上游。
- **body/headline 不自动联动**（D2）：`run_headline` 只吃 `current_body`，不反向重写 body；headline↔body 对齐由总编显式操作，避免隐式连锁。
- **环境说明**：验证使用系统 Python 3.14.3（仓库无 `.venv`），功能验证不受影响。
- **无人工验收阻断**：本 TODO 非 `[需人工验收]`，按标准流水线进入合并。