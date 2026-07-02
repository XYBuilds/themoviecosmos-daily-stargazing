# Phase 4.4 + 4.5 - Discord 首发平台选定与发布脚本 交付报告

## 1. 改动范围 (Scope)
- 新增 `scripts/publish_discord.py` — Discord 发布资产生成脚本
- 新增 `docs/templates/discord_template.md` — Discord 发布稿模板示例
- 修改 `.cursor/plans/Phase4-copywriter-c1-c2.plan.md` — 4.4/4.5 标 complete + 表述更新
- 修改 `.gitignore` — 忽略 `output/` 生成产物
- 依赖：无新增外部依赖（使用已有 `scripts/lib/llm`、`scripts/movie_metadata`）

## 2. 技术实现 (Implementation)
- **架构决策**：采用独立 per-platform 脚本（`publish_discord.py`）而非扩展 `copywriter.py` 子命令。理由：各平台输出形态差异大，独立脚本内聚性更好。
- **数据流**：C2 发布稿（纯文本 markdown）→ 提取 tmdb_id → DB 全列查询 → LLM 翻译片名/导演 → 组装 discord markdown + 下载 TMDB 海报
- **图片策略**：当前使用 TMDB 原始海报作为占位资产；未来视觉生成层将替换为定制图片
- **平台选择**：discord（零门槛、纯文本结构最简）；X 因依赖新闻源 URL（Phase 5）暂不做

## 3. 本地验证结果 (Verification)
- 成功生成 `output/discord/2026-07-02-discord-429918.md`（生存家族）
- 成功下载海报 `output/discord/2026-07-02-discord-429918-poster.jpg`
- 产出经总编确认符合要求

## 4. 潜在影响或技术债 (Technical Debt & Caveats)
- 4.6 小红书扩展时需新建 `publish_xiaohongshu.py`，不需要提前做 profile 抽象
- TMDB 海报为临时占位，视觉生成层 Phase 将替换
- X 平台阻塞于 Phase 5 fetch_news 的新闻源 URL 字段