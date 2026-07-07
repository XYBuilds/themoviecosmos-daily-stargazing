# Phase 8.6 - Review Panel i18n + UX 增强 交付报告

## 1. 改动范围 (Scope)
- `.cursor/plans/Phase8-review-panel.plan.md`
  - 新增并完成 `p8.6-i18n-ux` TODO。
  - 补充 8.6 设计说明、验收口径、空态策略与技术债。
- `scripts/daily_batch.py`
  - 在中文 briefing 渲染路径补充 `news_title` 翻译缓存写入。
- `review_panel/build_data.py`
  - 读取 `briefing.zh.translations.json` 并 join 中译字段。
  - 过滤 `judge_score in (None, 0)` 的 candidates。
  - 按 `judge_score` 降序稳定排序。
  - 移除 `causal_test` 输出。
- `review_panel/index.html`
  - 新增 EN/ZH 切换。
  - candidates 改为卡片网格布局；卡片加宽并自适应屏幕。
  - candidate 头部拆成标题行 / 元信息行 / genres 行，修复窄卡片错位。
  - candidate 内部字段顺序改为 overview 在前、rationale 在后。
  - 为空 candidates 增加 EN/ZH 空态提示。
  - 移除 candidate 标题书名号与 `causal_test` 展示。
- `review_panel/publish_adapter.py`
  - 发布定稿标题去掉候选电影书名号。
- `tests/test_review_panel_build_data.py`
  - 覆盖翻译 join、judge=0/None 过滤、降序排序、同分稳定序、`causal_test` 移除、缓存缺失/畸形容错。
- `tests/test_review_panel_publish_adapter.py`
  - 更新定稿标题断言，匹配去书名号后的输出。

新增/删除依赖包：无。

## 2. 技术实现 (Implementation)
- 翻译职责收敛在 `daily_batch.py`：复用既有 `_translate_texts_to_zh_safe` 缓存机制，仅新增 `news_title` kind；`build_data.py` 继续保持纯聚合，无 LLM 副作用。
- `panel.json` 新增字段：
  - `news.title_zh`
  - `news.description_zh`
  - `candidate.overview_zh`
  - `candidate.judge_rationale_zh`
- `panel.json` 移除字段：
  - `candidate.causal_test`
- candidate 数据口径：只保留 `judge_score not in (None, 0)` 的候选；候选按 judge 分数从高到低展示。
- 前端语言切换为纯客户端状态：`textFor(en, zh)` 在 zh 缺失时回退英文，不重新请求 `/api/data`。
- candidate 卡片布局使用 CSS grid：`repeat(auto-fill, minmax(480px, 1fr))`；窄屏回落单列；主容器扩展到 `1600px`，避免宽屏两侧大量留白。
- 对候选全被过滤的新闻保留 news 展示，并显示空态：「无共振候选 · 全部候选被 judge 判为 0 分」。

## 3. 本地验证结果 (Verification)
```powershell
python -m pytest tests/test_review_panel_build_data.py tests/test_review_panel_publish_adapter.py -v
# 39 passed

python -m pytest tests/test_daily_batch.py -v
# 19 passed

node -e "const fs=require('fs');const h=fs.readFileSync('review_panel/index.html','utf8');const m=h.match(/<script>([\\s\\S]*?)<\\/script>/);fs.writeFileSync('_chk.js',m[1]);require('child_process').execSync('node --check _chk.js');fs.unlinkSync('_chk.js');console.log('JS syntax OK');"
# JS syntax OK
```

人工验收：用户已在浏览器验收卡片宽度、卡片头部排版、空态、EN/ZH 展示与字段顺序，并输入 `approve`。

## 4. 潜在影响或技术债 (Technical Debt & Caveats)
- 历史日期的 `briefing.zh.translations.json` 可能没有 `news_title` 分组；未补缓存前，news title 在 ZH 模式会回退英文。重跑中文 briefing 渲染即可补齐。
- `description_zh` 当前按 `news.description` 做缓存 key。现有 `news.json` 仅有 description 字段，安全；若未来 news.json 引入 `excerpt` / `body` 并改变 daily_batch 的翻译源，需要同步 build_data 的 key 选择策略。
- `causal_test` 被判定为 judge 内部审计工件，不进入主面板。若未来需要调试视图，应以默认折叠的 debug 区域承载，而不是主审稿流。