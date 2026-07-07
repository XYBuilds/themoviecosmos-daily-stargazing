# Phase 9.5 · publish_adapter / clean_publish_body 适配 — 交付报告

## 改动范围（Scope）

- `review_panel/publish_adapter.py`：`render_copy_markdown` 消费 headline、去机械标题行；`run_adapter` + CLI 加 `--platform` 透传。
- `scripts/compose.py`：`clean_publish_body` docstring 明确「」归属行有意保留（无功能改动）。
- `tests/test_review_panel_publish_adapter.py`：stub 返回 headline / 接受 platform；断言更新。

**分支继承**：`feat/phase9.5-downstream-adapter` 从 `feat/phase9.4-publish-contract` 检出（未合并、PR #111）。链：9.1→…→9.5。

## 技术实现（Implementation）

- **消费 headline（D4）**：`render_copy_markdown` 新增「## 小红书标题（headline）」段展示 `draft["headline"]`；H1 改为 `# 发布定稿 · {date} · 小红书`，**移除** `{title}({year})` 机械标题行——电影真名由正文首行 `「片名」(YYYY) 导演名` 归属行承载，避免重复（D3）。
- **归属行保留（D3）**：`clean_publish_body` 逻辑本已只剥《》(年) 行与裸链接、保留「」行（`_TITLE_LINE_RE` 仅匹配《》）。本 todo 仅把这一「有意保留」写进 docstring，无行为变化。归属行随 body 原样进 `_copy.md`。
- **平台透传（D1）**：`run_adapter(..., platform="xiaohongshu")` → `run_publish(..., platform=platform)`；adapter CLI 加 `--platform`（choices xiaohongshu, default xiaohongshu）。`serve.py handle_publish` 保持最简（不传 platform，adapter 默认 xiaohongshu）——本期唯一平台，符合 plan「可最简处理」。

## 本地验证结果（Verification）

```
python -m pytest tests/test_review_panel_publish_adapter.py tests/test_compose_publish.py -q
26 passed
```

- `_copy.md` 顶部展示 headline（「## 小红书标题（headline）」段）。✅
- 正文含 `「Survival Family」(2017) 矢口史靖` 归属行、未被剥除。✅
- 无机械标题行：`Survival Family(2017)` 与 `《Survival Family》` 均不出现。✅
- 电影/新闻链接仍在链接段。✅

## 潜在影响或技术债（Technical Debt & Caveats）

- **serve.py 未显式传 platform**：本期唯一平台，adapter 默认 xiaohongshu 即可；未来加 X/Discord 时需让面板选择平台并经 `handle_publish` 透传（架构已留 `--platform` 口子）。
- **headline 空的降级**：`draft["headline"]` 为空时渲染「（无标题）」占位——不静默丢失信号，GATE 人工可见。
- **`_copy.md` 结构变更**：H1 不再含片名/年份；下游若有脚本按旧 H1 正则解析片名会失配（当前无此类消费者；面板只读文件全文）。
