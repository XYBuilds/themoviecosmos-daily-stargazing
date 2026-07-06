# 每日审核面板（review_panel）

## 是什么，解决什么问题

每日日批（`daily_batch`）跑完后，会产出当天全部新闻及其候选电影（含相似度、共振
agent、LLM judge 打分等信息）。此前审核者只能靠肉眼翻 `briefing.md`/`briefing.zh.md`
逐条比对，效率低、容易漏看高分候选。

`review_panel` 是一个独立、零框架、零构建的本地 Web 小工具：审核者在浏览器里看到
当天全部新闻卡片和各自的候选电影列表（含 judge 分数高亮、共振 agent 徽章、
rationale/causal_test 等原文），**从全天所有候选中选定 1 部电影**（全天唯一单选），
点「写推文」触发下游 C2 定稿，产出 `{slug}_copy.md`。取代原来看 md 文件的人肉审阅方式。

## 如何启动

```powershell
python review_panel/serve.py --port 8770
```

然后浏览器打开：

```
http://127.0.0.1:8770
```

默认扫描 `output/daily_batch/`；可用 `--batch-root <path>` 覆盖根目录（主要用于测试）。

## API 简表

| Method | Path | 入参 | 返回 | 说明 |
| --- | --- | --- | --- | --- |
| GET | `/api/dates` | 无 | `{"dates": ["2026-07-06", ...]}`（倒序） | 扫描 `daily_batch/*/` 目录名 |
| GET | `/api/data?date=YYYY-MM-DD` | query `date` | panel dict（见下方 schema）；无数据返回 404 + `{"error": "..."}` | 服务器按需重建 panel.json |
| POST | `/api/select` | body `{date, news_slug, tmdb_id, title}` | 200 `{ok:true, path, selection}`；缺字段 400 `{ok:false, error}` | 写 `selection.json`，幂等覆盖 |
| POST | `/api/publish` | body `{date}` | 200 `{ok:true, copy_path, stderr}`；失败 400/500 `{ok:false, copy_path:null, stderr}` | subprocess 调 `publish_adapter.py` |

## 数据流

```
daily_batch 产物 (news.json / retrieve.json / llm-judge-scores.json)
        │
        ▼
  build_data.py  ──────────────────────► panel.json（瘦身聚合）
        │                                       │
        ▼                                       ▼
  GET /api/data  ◄──────────────────────  serve.py 按需重建
        │
        ▼
  index.html 前端渲染新闻卡片 + 候选电影列表
        │
        │ 审核者选定 1 部电影
        ▼
  POST /api/select  ──►  selection.json（决策单一事实来源，幂等覆盖）
        │
        │ 点击「写推文」
        ▼
  POST /api/publish ──►  subprocess publish_adapter.py
        │                     │
        │                     └─► scripts.compose.run_publish
        ▼
  {slug}_copy.md（定稿产出，路径回显给前端）
```

## 安全边界

**本面板无鉴权**，`serve.py` 仅绑定 `127.0.0.1`（loopback）。任何能访问该端口的人
都能读取 daily_batch 数据、写 `selection.json`、甚至触发 publish 子进程——**请勿**
改绑 `0.0.0.0` 或任何公网可达地址对外暴露，也不要放到共享/多用户主机上不受限访问。
前端页脚也印了同一句提示：「本地面板 · 无鉴权 · 勿公网暴露」。

## 前端关键元素 id / class 清单（供测试/调试）

| 选择器 | 说明 |
| --- | --- |
| `#date-select` | 日期下拉 |
| `#publish-btn` | 「写推文」主按钮（未选定候选时 disabled） |
| `#selection-status` | 顶部当前选择状态展示 |
| `#error-banner` | 全局错误提示条（API 失败时展示，`.visible` 时可见） |
| `#publish-result` | publish 结果展示条（`.ok`/`.fail` 区分成功/失败） |
| `#news-list` | 新闻卡片列表容器 |
| `.news-card` | 单条新闻卡片 |
| `.candidate` | 单个候选电影行（`.is-selected` 标记当前选中项） |
| `.candidate-select` | 候选的单选 radio input（全天共享同一个 `name="daily-pick"`） |
| `.score-badge` | judge 分数徽章（`.score-2`/`.score-1`/`.score-0`） |
| `.agent-badge` | 共振 agent 徽章 |
| `#loading-state` / `#empty-state` | 加载中 / 空状态提示 |

## 全天唯一单选的实现方式

所有候选的 `<input type="radio" class="candidate-select">` 都使用**同一个固定
`name="daily-pick"`**（不随新闻 slug 或候选 tmdb_id 变化），由浏览器原生 radio
group 语义保证：勾选任意一个会自动取消同一 name 下的其它所有勾选，天然实现「全天
（跨新闻）唯一单选」，不需要额外的 JS 互斥逻辑。选中后立即 `POST /api/select`
落盘 `selection.json`；切换选择时会带上新的 `news_slug`/`tmdb_id`/`title` 再次
POST，服务端整份覆盖写入，天然幂等。