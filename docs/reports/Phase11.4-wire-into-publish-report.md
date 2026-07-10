# Phase 11.4 - wire-into-publish 交付报告

## 1. 改动范围 (Scope)
- `scripts/compose.py`
- `prompts/compose_publish_xiaohongshu.md`
- `tests/test_compose_publish.py`
- `.cursor/plans/Phase11-deterministic-movie-header-projection.plan.md`

新增/删除依赖：无。

## 2. 技术实现 (Implementation)
- 在 `run_publish` 中，LLM 产出的正文先经过 `clean_publish_body`，再由代码把 `render_movie_header(build_header_projection(candidate))` 前置到正文首块；抬头不再依赖 LLM。
- `compose_publish_xiaohongshu.md` 删除了原本要求模型写归属行的内容，改为明确禁止输出任何电影信息抬头 / 元信息行，并与“不要自吐链接”并列。
- `clean_publish_body` 新增小而稳的兜底规则：保留正常正文段落，剥除 LLM 误吐的《片名》(年份) 行、抬头样式行，以及坐标 / 文明 / 类型 / 光度 / 体积等元信息前缀行；同时继续保留既有的裸链接剥除逻辑。
- 测试补齐了三类关键回归：`run_publish` 输出确实以前置头部开头、prompt 不再引导模型写抬头、`clean_publish_body` 能清掉误吐抬头且不影响正常正文；同时保留既有链接清洗回归。

## 3. 本地验证结果 (Verification)
- 运行命令：`py -m pytest tests/test_compose_publish.py`
- 结果：`35 passed in 6.36s`
- 说明：环境里直接调用 `pytest` 不可用，因此使用 `py -m pytest` 完成验证。

## 4. 潜在影响或技术债 (Technical Debt & Caveats)
- 这一步把抬头接回 `run_publish`，但其他下游适配器若仍自行渲染正文，后续 11.5 需要同步收口。
- `clean_publish_body` 目前偏保守，遇到更复杂的正文格式时可能还需要补更精细的规则。
- 目前中文片名段仍是留空退化路径，完整中文译名增强仍在后续 TODO-B / 后续 Phase。