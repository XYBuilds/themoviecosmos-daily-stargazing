# Phase 9.8.7 - GATE 真实重跑 + 面板验收 + 文档同步 交付报告

## 1. 改动范围 (Scope)

- `docs/SSOT/news-to-film-pipeline.md`：在 `compose` 阶段总表后补充 Phase 9.8 定稿面板三种定点操控说明，引用 ADR-0016。
- `docs/SSOT/电影宇宙「每日星轨观测」系统 PRD.md`：在 §7.3 文案定稿章节补充同一段能力说明，引用 ADR-0016。
- `docs/reports/Phase9.8.7-gate-doc-sync-report.md`：本报告。

本次文档同步 worker 任务范围仅限以上三个文件。`.cursor/plans/Phase9.8-panel-copy-regenerate-and-edit.plan.md` 的状态标记（`p9.8.7` → `complete`）不在本次任务范围内，需由主流程另行处理。

9.8.7 本身不含新功能代码。它是 Phase 9.8 的 GATE 收尾节点，工作内容是：真实端到端人工验收 + 上述文档同步。唯一一处代码改动是 GATE 验收过程中发现并修复的前端加载态一致性问题（提交 `cf93047`：把「去AI化」按钮纳入 `copyOpInFlight` 互斥锁），非本次文档同步任务的范围，已在此前提交完成。

## 2. 技术实现 (Implementation)

9.8.7 的职责是验收，不是实现——真正的实现分布在 9.8.1–9.8.6：`prompts/_shared/xiaohongshu_headline_contract.md`（headline 契约单一事实源）→ `scripts/compose.run_headline`（body-aware 标题重生成）→ `review_panel/regenerate_adapter.py`（`--target headline|body`，与 publish/rewrite adapter 同层）→ `review_panel/serve.py` 新增 `POST /api/regenerate`、`POST /api/edit-body` 两个路由 → 前端定稿区新增「重生成正文」「重生成标题」按钮与正文可编辑 textarea。9.8.7 把这条链路串起来跑一次真实请求，确认端到端可用。

文档同步方面：

- `news-to-film-pipeline.md` 的 `compose` 行原本只讲 `review.md`/`publish.md` 两个 stage 和 humanized 派生产物。新增一段紧跟其后，说明面板对 `publish` 产物新增的三种覆盖式操控（重生成正文/重生成标题/正文人工编辑），以及 body 变更即失效 `_humanized.md` 的不变量，引用 ADR-0016。
- PRD 的 §7.3「文案定稿」原本止于 ADR-0015 定义的平台 profile。新增一条列表项，衔接在 profile 说明之后，讲总编现在能在面板内做的三种定点操控，同样引用 ADR-0016，强调不新增版本层（沿用原版/去AI化版二档）。

三种操作的端到端数据流：

- **重生成正文**：面板点击 → `POST /api/regenerate {target: body}` → serve subprocess 调 `regenerate_adapter.py --target body` → 内部复用 `scripts.compose.run_publish`（携带 news + selected_movie + judge 全语境）→ 只取新 body，经 `render_copy_markdown` 写回 `_copy_{platform}.md`（headline/链接不动，丢弃这次顺带产出的新 headline）→ 删除 `_humanized.md`，清空 `selection.json.copies.{platform}.humanized_path`。
- **重生成标题**：`POST /api/regenerate {target: headline}` → adapter 读取当前 `_copy_{platform}.md` 的 body（可能已被人工编辑过）→ `run_headline(current_body)` → 只覆盖 headline，body/链接不动 → 不触碰 humanized。
- **正文人工编辑**：面板 textarea 保存 → `POST /api/edit-body {body}` → serve 无 LLM，直接调 `render_copy_markdown` 写回原稿 → 同样删除 `_humanized.md` 并清空对应 `humanized_path`。

## 3. 本地验证结果 (Verification)

**路由根因排查**：验收初期「重生成/编辑点击无反应」，定位到运行中的 `serve.py` 进程是旧版本二进制（缺 9.8.4 引入的 `/api/regenerate`、`/api/edit-body` 路由），端口被这个旧进程占住，热重启没能接管端口。杀掉残留进程、用最新代码重启后，两个路由从 404 变为正常的 400 参数校验响应，确认是运行环境陈旧进程问题，不是代码缺陷。

**真实端到端实测**（Python `urllib`，UTF-8，对活服务器发真实请求）：

- `POST /api/edit-body`：返回 HTTP 200。body 被精确替换，含中文哨兵字符串逐字相等比对通过（验证 UTF-8 写入链路无损），headline 与「## 链接」分区逐字保留未受影响，`_humanized.md` 被正确删除。
- `POST /api/regenerate`（`target=body`）：返回 HTTP 200 `ok:true`。新旧 body 实质不同（确认真的走了一次 LLM 重生成，不是空转），headline 保持不变，`_humanized.md` 被删除，adapter stderr 打印 `Wrote <path>`。
- 测试全程自带备份/还原：验收所用新闻的定稿数据（`_copy_xiaohongshu.md`、`_humanized.md`、`selection.json`）按 SHA256 校验，验收结束后已完整还原到测试前状态，未污染生产数据。

**PowerShell 伪影排查**：验收中途一度用 `Invoke-WebRequest` 测试同样的接口，出现「请求挂起 + 中文变问号」的异常现象。排查后定位为 PowerShell 工具本身的伪影——默认 GBK 代码页损坏了请求体编码，且未加 `-UseBasicParsing`，与服务器代码无关。换用 Python `urllib`（显式 UTF-8 编解码）后两个端点全部通过。浏览器端 `fetch` 走的是标准 UTF-8 编码，不受此问题影响。

此外，9.8.1–9.8.6 各 TODO 累计的 pytest 单测（`test_compose_publish.py` 的 golden-snapshot 断言、adapter/serve 相关测试）此前已全绿，本轮 GATE 未引入新的自动化测试，只做人工端到端验收。

## 4. 潜在影响或技术债 (Technical Debt & Caveats)

- `run_publish` 重生成 body 会顺带产出一个新 headline 并直接丢弃，存在小幅 token 浪费——这是 D2 明确的 YAGNI 取舍（不为 body-only 单独建 prompt），换来的是首发场景不用拆 monolithic prompt。
- 平台仅开放 `xiaohongshu`，X/discord 等仍是占位，未随本次改动扩展。
- 面板 `serve.py` 无鉴权，仅绑定 `127.0.0.1`，依赖本机访问边界，不适合直接暴露到公网。
- Windows 下用 PowerShell `Invoke-WebRequest` 测本地 API 有 UTF-8 编码与请求挂起的陷阱（见上），后续本地调试建议统一用 `urllib`/`requests` 等显式指定 UTF-8 的客户端，避免误判为服务端问题。
- 两套 publish 入口（`main.py` 生产管线 / `review_panel` 系列 adapter）并存的既有技术债延续，本次未合并，后续如需统一入口需单独立项。