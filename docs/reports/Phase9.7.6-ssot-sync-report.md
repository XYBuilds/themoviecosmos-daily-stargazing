# Phase 9.7.6 - SSOT / PRD 同步 交付报告

## 1. 改动范围 (Scope)

- `docs/SSOT/news-to-film-pipeline.md` — §0.1 阶段总表 `compose` 行的 publish 口径 + 产物列更新。
- `docs/SSOT/电影宇宙「每日星轨观测」系统 PRD.md` — §7.3 文案定稿段同步 + 平台起步顺序修正。
- 新增/删除依赖：无。纯文档，无代码/测试改动。

## 2. 技术实现 (Implementation)

**SSOT compose 行**：publish stage 补充「按 ADR-0015 每平台一个创作步骤（`--platform`），小红书首发，产出正文 + headline（≤10 中文字）+ 归属行 `「片名」(YYYY) 导演名`，正文只守必含元素清单（新闻侧/关系侧/电影侧），不规定顺序或段数」；产物列补 `publish.md（小红书：{tmdb_id, headline, body}）`。保留原表格格式与「落地物偏差」约定，仅改 compose 一行。

**PRD §7.3**：定稿段改为「按 ADR-0015 生成平台发布版本：每平台一个创作步骤（`compose --stage publish --platform xiaohongshu`），MVP 小红书首发，X/Reddit 预留；正文（三类必含元素，顺序自由）+ headline + 归属行」。旧的 `prompts/C2_copywriter_multiplatform.md`（编号式命名，已被 ADR-0011 收敛废弃）替换为 `compose --stage publish --platform` 口径。

**平台顺序修正**：PRD 原「discord → 小红书 → X」与 ADR-0015「小红书首发」D1 矛盾，改为「小红书 → X → discord」。

## 3. 本地验证结果 (Verification)

文档无自动化测试，做一致性 grep：
- `暂不分平台`/`不分平台`（C2/发布稿/定稿上下文）→ 0 处残留。
- `分平台` 全库仅剩 PRD §5.4「不带 hashtag、不分平台」——描述的是 **C1 审核稿**（审核稿保持平台中性是既定设计，平台化只在下游 C2/publish 发生），与 ADR-0015 不矛盾，未改。
- ADR-0015 引用已加入 SSOT compose 行 + PRD §7.3；headline/归属行/元素清单/小红书首发 四要素均在 SSOT compose 段出现。

## 4. 潜在影响或技术债 (Technical Debt & Caveats)

- SSOT/PRD 中承载脚本名仍按目标态标注（`compose.py` 目标名），与 ADR-0011 命名收敛「不改代码、磁盘仍旧名」的偏差约定一致，非本 TODO 引入。
- C1 审核稿的「不分平台」是有意设计（非残留矛盾），后续若审核稿也要分平台需另开决策，不在本 Phase 范围。
- 分支继承：`feat/phase9.7.6-ssot-sync` 从集成分支检出（已含 9.7.1–9.7.5 合并结果）。