# Phase 11.2 - p11.2-render-header-pure-fn 交付报告

## 1. 改动范围 (Scope)
- `scripts/compose.py`
- `tests/test_compose_publish.py`
- `.cursor/plans/Phase11-deterministic-movie-header-projection.plan.md`
- `docs/reports/Phase11.2-render-header-pure-fn-report.md`
- 依赖复用：`scripts/lib/movie_labels.py` 中的 `GENRE_EN_TO_ZH`、`LANG_CODE_TO_ZH`

## 2. 技术实现 (Implementation)
- 新增 `render_movie_header(proj: dict) -> str`，把电影抬头按 Phase11 D0/D1 确定性拼成多行字符串。
- 处理了片名三段、英语片去重、中文片名缺失退化、导演缺失省略、release_date 非法退化、语言码/类型映射 fallback，以及光度/体积直出。
- 保持函数零 IO、零 DB、零 LLM，仅做字符串投影；辅助逻辑收进了几个私有小函数，方便单测覆盖。
- 新增单测覆盖：非英语退化、英语去重、三段中文片名、缺 director、映射 fallback、release_date 异常。

## 3. 本地验证结果 (Verification)
- 运行命令：`python -m pytest tests/test_compose_publish.py -q`
- 结果：`32 passed in 6.00s`
- 先前一次直接跑 `pytest` 因环境里未暴露命令而失败，改用 `python -m pytest` 后通过。

## 4. 潜在影响或技术债 (Technical Debt & Caveats)
- 当前只落了纯渲染层，尚未把抬头装配接入后续 `build_header_projection` / `run_publish` / adapters。
- `release_date` 异常时采用 `坐标：未知` 的稳定退化策略，后续若计划更严格的格式契约，可再统一收敛。
- 语言和类型 fallback 目前偏保守：表外语言只保留大写码，表外类型保留原英文名。