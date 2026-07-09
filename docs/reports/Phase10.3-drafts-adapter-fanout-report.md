# Phase 10.3 - drafts_adapter 全量扇出 + 合并 交付报告

## 1. 改动范围 (Scope)

- **新增** `review_panel/drafts_adapter.py`（与 publish/rewrite/regenerate adapter 同层）
- **新增** `tests/test_review_panel_drafts_adapter.py`（13 例）
- 依赖包：无新增

## 2. 技术实现 (Implementation)

### 2.1 数据流（ADR-0017 D3/D5）

```
run_fanout(date, slug, tmdb_id)
    │  locate_news_dir / load_news / find_candidate / load_judge_entry（复用 publish_adapter）
    ▼
personas = dedupe(candidate.triggered_by)          # 去重且保序，无上限
    │  for persona in personas:
    │      normalized = THE-SAGE → The-Sage
    │      perspective = load_persona_perspective(persona)
    │      draft = run_publish(..., persona_perspective=perspective)
    │      pool.append({draft_id: normalized, headline, body})
    ▼
{slug}_drafts_{platform}.json                      # 整份覆盖（重掷全部 persona）
```

```
run_combine(date, slug, tmdb_id, [a, b], combine_mode)
    │  校验 len(ids)==2，否则 ValueError（≤2 硬约束）
    │  读池 → by_id 查找；缺失 → ValueError
    ▼
    ├─ mode=A：composite = 视角a\n\n视角b → run_publish → append {draft_id:"a+b"}
    ├─ mode=B：combine_bodies(body_a, body_b) 纯函数 → append {draft_id:"a+b"}（不调 LLM）
    └─ mode=both：append "a+b#A"（走 A）+ "a+b#B"（走 B）   # 仅 GATE 离线对照
    ▼
    append-only 写回（读→append→写，不动其它草稿）
```

### 2.2 combine_bodies 纯函数（路线 B）

独立可测（两份 body → 融合 body），保守策略：保留 a 归属行（ADR-0015 D3 首行），去掉 b 重复归属行防片名 / 年 / 导演出现两次，其余正文空行拼接。不重排、不改写——把接缝 / 调性判断权留给 GATE 肉眼对照（路线 B 已知局限）。

### 2.3 耦合与注入

- 唯一 import `scripts.compose`（经 publish_adapter 转 import 其 locate/load/find/judge 工具，无重复造轮子）。
- `run_publish` / `load_persona_perspective` 均可注入（默认 `compose` 真实函数），测试 stub 免真调 LLM。
- CLI：`--date/--news-slug/--tmdb-id/--platform/--combine/--combine-mode`；`--combine-mode` 默认 `A`（生产默认单版）；stderr 打 `Wrote <path>`。
- **本层不碰 selection.json、不派生当前稿、不失效 humanized**——那些是「选中」语义，属 serve（10.4）的 `/api/select-draft`。本层纯粹「产只读来源池」。

## 3. 本地验证结果 (Verification)

```
$ python -m pytest tests/test_review_panel_drafts_adapter.py -q
.............                                                            [100%]
13 passed in 5.31s
```

覆盖：扇出条数 == 去重 triggered_by 数、去重保序、空 triggered_by 报错、整份覆盖、combine A 走 run_publish（复合视角含两份）、combine B 纯函数不调 LLM、combine both 产 #A/#B 两条、combine>2 报错、未知 draft_id 报错、append 保留原草稿、combine_bodies 归属行去重 / 空值兜底。

CLI 冒烟（错误路径）：

```
$ python -m review_panel.drafts_adapter --date 1999-01-01 --news-slug nosuch --tmdb-id 1
error: news dir not found: ...\output\daily_batch\1999-01-01\nosuch
exit=2
```

publish_adapter / regenerate_adapter / compose_publish 既有测试全绿，无回归。

## 4. 潜在影响或技术债 (Technical Debt & Caveats)

- **combine 恰好 2 而非 ≤2**：语义上「合并」至少要 2 份，故 `run_combine` 强制 `len==2`（比 plan 的「≤2」更严）。>2 与 <2 都报错，覆盖 plan 的「传 3 个 → 非零退出」验收。
- **路线 B 融合策略保守**：当前只做无损拼接 + 归属行去重，接缝可能生硬。这是 D5 明列的路线 B 已知局限，GATE（10.7）离线对照后若选 B 可迭代 `combine_bodies`（已隔离为纯函数，改动面小）。
- **serve 端点尚未接入**：10.4 将新增 `/api/generate-drafts`（subprocess 调本模块扇出）+ `/api/combine-drafts`（恒单版，不传 both）+ `/api/select-draft`（指针派生，本模块不负责）。
- **combine 的 headline（路线 B）取 a 的既有 headline**：融合只处理 body，headline 沿用第一份，符合「文本融合不重新创作标题」的路线 B 定位。