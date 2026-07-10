# Phase 11.1 - p11.1-static-maps-and-adr 交付报告

## 1. 改动范围 (Scope)
- 新增 `scripts/lib/movie_labels.py`，提供 `GENRE_EN_TO_ZH` 与 `LANG_CODE_TO_ZH` 两张纯本地静态映射表。
- 更新 `scripts/lib/__init__.py`，将两张映射表导出为后续 `scripts/compose.py` 可直接 import 的公共常量。
- 新增 `prompts/_shared/xiaohongshu_movie_header_contract.md`，固化 Phase 11 D0 抬头模板与字段退化规则。
- 新增 `docs/adr/0018-deterministic-movie-header-projection.md`，记录确定性抬头投影的决策背景、边界与后果。
- 新增 `tests/test_movie_labels.py`，覆盖映射表非空、核心 genre 键、常见语言码键。

## 2. 技术实现 (Implementation)
- 采用“静态常量 + 纯 import”方式实现映射表，避免任何 TMDB 在线依赖。
- genre 表覆盖 TMDB 常见 19 类并提供中文译名；语言表覆盖 subsample/仓内高频语种，并保留后续扩展空间。
- 契约文档把抬头模板、字段来源、drop_cn_seg 退化逻辑写死，作为下游 render/projection 的单一格式依据。
- ADR-0018 明确抬头行应由代码确定性投影，正文仍由 LLM 创作，中文译名留 TODO-B 插槽。

## 3. 本地验证结果 (Verification)
- 运行命令：`py -3 -m pytest tests/test_movie_labels.py`
- 结果：`3 passed in 4.54s`
- 说明：`pytest` 直接命令在当前 PowerShell 环境未注册，但 Python launcher 方式验证通过。

## 4. 潜在影响或技术债 (Technical Debt & Caveats)
- 目前仅完成静态映射与契约/ADR，尚未接入 `scripts/compose.py` 的实际投影/渲染逻辑；后续 11.2/11.3 才会消费这些常量。
- `LANG_CODE_TO_ZH` 仍是面向仓内常见语种的覆盖集，若后续数据出现更冷门语种，需要补表。
- 中文片名译名仍为空插槽，按 Phase 11 约束留给 TODO-B / 后续独立 Phase 处理。