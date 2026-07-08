---
name: Phase9.7-copy-output-and-panel-integration
overview: |
  Phase 9.1–9.6 完成了 C2 平台化核心（prompt 元素化 + headline + 归属行 + --platform）。
  本子阶段处理「产出格式精简 + 多平台文件命名 + 审核面板定稿展示 + avoid-ai-writing 可逆改写 + SSOT 同步」。
  核心改动：
  ① render_copy_markdown 去掉冗余标签行和新闻原文 section，headline 加 ≤ 10 中文字硬约束；
  ② 文件名从 {slug}_copy.md → {slug}_copy_{platform}.md，为多平台定稿留扩展口；
  ③ 审核面板新增定稿展示区（带 platform tabs + 移动宽度预览），读 _copy_{platform}.md 呈现；
  ④ 面板集成 avoid-ai-writing：后端 /api/rewrite 调 LLM 改写，写 _copy_{platform}_humanized.md，前端 toggle 原版/去AI化版（可逆）；
  ⑤ GATE 通过后同步 docs/SSOT 与 PRD。
todos:
  - id: p9.7.1-copy-format-slim
    content: 9.7.1 · [渲染] render_copy_markdown 去掉标签行 + 新闻原文 section + headline ≤ 10 中文字约束（prompt + 渲染层双保证）
    status: complete
  - id: p9.7.2-platform-filename
    content: 9.7.2 · [命名] 文件名 {slug}_copy_{platform}.md + selection.json 结构升级为 copies dict + 下游适配
    status: complete
  - id: p9.7.3-panel-copy-display
    content: 9.7.3 · [面板] 审核面板新增定稿展示区：GET /api/copy + 前端 platform tabs + 渲染 headline/body
    status: complete
  - id: p9.7.4-avoid-ai-rewrite
    content: 9.7.4 · [面板] avoid-ai-writing 集成：POST /api/rewrite + _humanized.md 产出 + 前端 toggle 可逆切换
    status: complete
  - id: p9.7.5-tests
    content: 9.7.5 · [测试] 新增/更新 test_publish_adapter + test_serve 覆盖新格式/新文件名/新 API
    status: complete
  - id: p9.7.6-gate-doc-sync
    content: 9.7.6 · [GATE] Rule Breakers 真实重跑：验证新格式 + 面板定稿展示/移动宽度预览 + avoid-ai-writing toggle；Go 后同步 SSOT/PRD 并收尾 [需人工验收]
    status: complete
isProject: true
---

# Phase 9.7 · 定稿产出精简 + 面板定稿集成 + avoid-ai-writing

## 前置条件

| Phase    | 状态                                              | 依据                                                                                |
| -------- | ------------------------------------------------- | ----------------------------------------------------------------------------------- |
| 9.1–9.6  | complete                                          | `git log --oneline` 可见 p9.1–p9.6 全部提交；plan frontmatter 均 `status: complete` |
| 当前分支 | `feat/phase9.7-copy-output-and-panel-integration` | 从 9.6 检出，无额外 diff                                                            |

## 背景

Phase 9.1–9.6 落地了 C2 平台化核心能力（xiaohongshu prompt + headline + 归属行）。真实产出 `_copy.md` 含多余的 section 标签行和新闻原文段——这些是内部调试信息，不应出现在面向发布的成品中。同时，审核面板目前只能看到候选卡和触发 publish，无法直接阅读/编辑定稿。

本子阶段解决五个问题：
1. **产出格式精简**：去标签行、去新闻原文 section、headline ≤ 10 中文字
2. **多平台文件命名**：为未来 X / Reddit 等平台预留扩展，文件名带 platform 维度
3. **面板定稿展示**：总编在面板直接阅读定稿，并可用移动宽度预览检查小红书观感
4. **avoid-ai-writing 可逆改写**：面板内一键去 AI 写作痕迹，保留原版可回退
5. **GATE 后文档同步**：Rule Breakers 验收 Go 后再同步 SSOT / PRD 并收尾 9.7

## 设计决策

### D1 产出格式（目标态）

```markdown
# 发布定稿 · {date} · {platform_label}

{headline}                       ← ≤ 10 中文字（不含标点）

{body}                           ← 正文（含归属行）

## 链接
- 电影: {movie_url}
- 新闻: {news_url}
```

去掉的：`## 小红书标题（headline）` 标签行、`## 中文发布正文` 标签行、整个 `## 新闻原文（English source）` section。

### D2 headline ≤ 10 字

- prompt 层：在 compose_publish_xiaohongshu.md 的 headline 约束中加「≤ 10 个中文字（不含标点）」
- 渲染层：`render_copy_markdown` 不做截断（prompt 端保证），但可加 warning log

### D3 文件名平台化

```
当前:  {slug}_copy.md
目标:  {slug}_copy_{platform}.md
去AI:  {slug}_copy_{platform}_humanized.md

示例:
  10-overseas-education_copy_xiaohongshu.md
  10-overseas-education_copy_xiaohongshu_humanized.md
  10-overseas-education_copy_x.md          ← 未来
```

### D4 selection.json 结构升级

```json
{
  "date": "2026-07-06",
  "selected": { "news_slug": "...", "tmdb_id": 1379520, "title": "..." },
  "selected_at": "...",
  "copies": {
    "xiaohongshu": {
      "published": true,
      "copy_path": "...copy_xiaohongshu.md",
      "humanized_path": null
    }
  }
}
```

向后兼容：读 selection.json 时如果遇到旧格式（`published` / `copy_path` 在顶层），迁移为 copies dict。

### D5 avoid-ai-writing 方案

- 后端新增 `POST /api/rewrite`：读 `_copy_{platform}.md` 正文 → LLM（复用 DeepSeek/MIMO）按 avoid-ai-writing rewrite mode 规则改写 → 写 `_copy_{platform}_humanized.md`
- prompt 来源：从 `.cursor/rules/avoid-ai-writing.mdc` 提取核心 rewrite 规则为 `prompts/avoid_ai_writing_rewrite.md`
- 可逆性：原版 `_copy_{platform}.md` 不变；humanized 版可反复重新生成
- 前端 toggle：「原版 / 去AI化版」切换显示

**LLM 调用架构决策：subprocess + `review_panel/rewrite_adapter.py`**

与 publish_adapter.py 同模式——serve.py 通过 subprocess 调用独立 adapter 脚本，不直接 import LLM 模块。

选型理由：
1. **一致性**：publish 已用 subprocess adapter，rewrite 同模式 → 面板所有 LLM 调用统一为 `serve.py → subprocess → adapter → scripts.lib.llm`
2. **崩溃隔离**：LLM 超时/crash 不阻塞 serve.py 响应其他请求
3. **依赖解耦**：serve.py 保持纯路由，不直接 import `scripts.lib.llm`（保持和 publish 链路一致的薄传输层定位）
4. **延迟容忍**：subprocess spawn ~1s vs LLM API 3–10s，进程启动开销可忽略
5. **可测试性**：rewrite_adapter.py 可独立单测，serve.py 测试可注入 `run_subprocess` stub

`rewrite_adapter.py` 职责边界：
```
输入：--date / --slug / --platform
处理：读 _copy_{platform}.md → 提取 body → 调 LLM（avoid_ai_writing_rewrite prompt）→ 写 _copy_{platform}_humanized.md
输出：stderr 打印 "Wrote <path>"（供 serve.py 解析）
```

### D6 面板定稿展示

- `GET /api/copy?date=&slug=&platform=` → 返回 `{ headline, body, humanized_body, has_humanized }`
- 前端：定稿独立视图，带 platform tabs（当前只有 xiaohongshu 可用，其他灰置）
- 移动宽度预览：定稿正文容器支持桌面宽度 / 小红书移动宽度两档切换；只改变预览容器宽度，不改变产物内容
- 未 publish 时显示空态提示

---

## Todo 9.7.1 · [渲染] 产出格式精简 + headline 约束

**依赖：** 无

**改动：**
- `review_panel/publish_adapter.py` → `render_copy_markdown()`：重写模板，去掉标签行和新闻原文 section
- `prompts/compose_publish_xiaohongshu.md` → headline 约束加「≤ 10 个中文字（不含标点）」
- 可选：渲染层加 `len(headline) > 10` 时的 warning log

### 验收
- [ ] `_copy_*.md` 无 `## 小红书标题` / `## 中文发布正文` / `## 新闻原文` 标签
- [ ] headline 单独成行，≤ 10 中文字
- [ ] 链接 section 保留

---

## Todo 9.7.2 · [命名] 文件名平台化 + selection.json 升级

**依赖：** 9.7.1

**改动：**
- `publish_adapter.py`：`run_adapter` 输出路径 `{slug}_copy_{platform}.md`
- `serve.py`：
  - `handle_select`：删旧稿逻辑适配新文件名 `_copy_{platform}.md`
  - `handle_publish`：`copy_path` 使用新文件名
  - selection.json 读写升级为 `copies` dict 结构（D4）
  - 向后兼容读旧格式
- `build_data.py`：如果引用 copy 路径，适配新命名

### 验收
- [ ] publish 产出文件名为 `{slug}_copy_xiaohongshu.md`
- [ ] selection.json 使用 `copies` dict
- [ ] 改选时正确删除旧 `_copy_{platform}.md`
- [ ] 旧格式 selection.json 可被正确读取并迁移

---

## Todo 9.7.3 · [面板] 定稿展示区

**依赖：** 9.7.2

**改动：**
- `serve.py`：新增 `GET /api/copy` 路由（读 _copy_{platform}.md 解析返回 headline/body/humanized 状态）
- `index.html`：定稿独立视图（platform tabs + headline + body + 空态）
- `index.html`：增加移动宽度预览切换，用于模拟小红书发布后的窄屏阅读宽度

### 验收
- [ ] 面板可展示已 publish 的定稿内容
- [ ] 未 publish 时显示空态
- [ ] platform tab 切换有效（当前只有 xiaohongshu）
- [ ] 可切换桌面宽度 / 移动宽度预览，且不改变 copy 文件内容

---

## Todo 9.7.4 · [面板] avoid-ai-writing 集成

**依赖：** 9.7.3

**改动：**
- `prompts/avoid_ai_writing_rewrite.md`：[新文件] 从 avoid-ai-writing 规则提取 rewrite mode 核心
- `review_panel/rewrite_adapter.py`：[新文件] 独立 adapter 脚本（subprocess 模式，和 publish_adapter 同层）
  - 读 `_copy_{platform}.md` 提取 body
  - 调 `scripts.lib.llm` + avoid_ai_writing prompt
  - 写 `_copy_{platform}_humanized.md`
  - stderr 输出 "Wrote <path>"
- `serve.py`：新增 `POST /api/rewrite` 路由
  - subprocess 调 rewrite_adapter.py（和 handle_publish 调 publish_adapter 同模式）
  - 更新 selection.json 的 `copies.{platform}.humanized_path`
  - 返回 humanized body
- `index.html`：「去AI化」按钮 + toggle 原版/去AI化版

### 验收
- [ ] 点击「去AI化」后生成 humanized 文件
- [ ] toggle 可在原版和去AI化版之间切换
- [ ] 反复点击「去AI化」覆盖 humanized 版本，原版不变
- [ ] humanized_path 在 selection.json 正确记录

---

## Todo 9.7.5 · [测试] 覆盖新功能

**依赖：** 9.7.4

**改动：**
- `tests/test_review_panel_publish_adapter.py`：新格式渲染 + 新文件名
- `tests/test_review_panel_serve.py`：/api/copy + /api/rewrite + selection.json copies 结构 + 向后兼容

### 验收
- [ ] `pytest tests/test_review_panel_publish_adapter.py tests/test_review_panel_serve.py` 全绿

---

## Todo 9.7.6 · [GATE] Rule Breakers 真实重跑 + 面板验收 + 文档同步 [需人工验收]

**依赖：** 9.7.1–9.7.5 全部

**执行顺序：**
1. 先做 Rule Breakers 真实重跑与面板验收。
2. 等待人工 Go/No-Go；No-Go 则回到对应实现 TODO 修正。
3. Go 后再同步 docs/SSOT 与 PRD，并按 9.7 收尾。

**验收项：**
- [ ] 用 2026-07-06 / Rule Breakers 重跑 publish → `_copy_xiaohongshu.md` 格式正确
- [ ] headline ≤ 10 中文字
- [ ] 面板定稿区正常展示
- [ ] 定稿区可切换桌面宽度 / 移动宽度预览
- [ ] avoid-ai-writing toggle 工作正常
- [ ] Go 后同步 `docs/SSOT/news-to-film-pipeline.md` compose 段与 PRD 平台化/元素化描述，引用 ADR-0015
- [ ] `[需人工验收 · Go/No-Go]`

---

## 风险与约束

- **headline 10 字是硬限**：LLM 偶发超限时渲染层 log warning 但不截断——由 GATE 人工判断是否需要调 prompt
- **selection.json 向后兼容**：旧格式（published/copy_path 在顶层）必须能被无损读取并迁移，否则已有的 2026-07-06 数据会坏
- **/api/rewrite 引入 LLM 依赖到 serve.py**：通过 subprocess 调独立脚本（类似 publish_adapter 模式），不让 serve.py 直接 import 重模块
- **多平台 tab 未来扩展**：当前只实现 xiaohongshu，其他 platform 的 tab 灰置 + "coming soon"