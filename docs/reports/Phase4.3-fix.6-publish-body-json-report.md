# Phase 4.3-fix.6 - 发布稿产物契约改为 JSON（仅电影 id + 正文）交付报告

## 0. 分支继承关系

- 本分支 `feat/phase4.3-fix.6-publish-body-json` **继承自** `feat/phase4.3-fix.5-image-equality-tone`（对应 TODO 4.3-fix.5，确立「影像平权」创作宪法）。
- 检出原因：fix.5 已开发完毕但**尚未合并入 `main`**，按「Phase 依赖与顺序执行」规则从前置最新开发分支检出，以不阻塞 fix.6 调性后续调整。
- 继承了 fix.5 的平视调性基线（compose_publish.md 身份/边界/共振钩子/正例/反例），本次在其之上仅做产物契约调整，未回退调性内容。

## 1. 改动范围 (Scope)

| 文件 | 类型 | 说明 |
| --- | --- | --- |
| `prompts/compose_publish.md` | 修改 | 生成规则改为「仅产正文」契约：去掉《片名》(年份) 标题行与电影链接的输出要求 |
| `scripts/compose.py` | 修改 | `run_publish` 返回 JSON dict；删除骨架拼接逻辑；新增正文清洗 |
| `tests/test_compose_publish.py` | 修改 | 同步新契约断言（tmdb_id + body），保留正文清洗用例 |
| `output/phase4.3-fix.4-verify/publish_draft_v11.json` | 新增 | 本次最终验证产物（JSON 形态示例） |

- 新增/删除依赖包：无（纯逻辑 + prompt 改动）。
- 提交：`75f53bb feat(compose): p4.3-fix.6-emit-publish-body-json-defer-skeleton-to-platform`（4 files changed, 78 insertions, 30 deletions）。
- 未纳入提交：`output/phase4.3-fix.4-verify/` 下 fix.3~fix.5 历史草稿（v2~v10、decision_card、READ_FIRST）保持未跟踪，属既往 GATE 审核材料，与本 TODO 无关，不卷入。

## 2. 技术实现 (Implementation)

### 2.1 职责调整动机
C2 是链路「唯一创作环节」，其本分应是**产正文**。骨架（片名/年份/链接）与 DB 投影属**呈现层**，而不同社媒平台呈现规则不同（小红书话题标签、X 短链、Discord embed）。上一轮（同分支前序）让程序确定性拼骨架，本质是把呈现层职责前置到创作环节，构成复杂度扩散。本次将其下沉到下游平台适配阶段（4.4+），C2 回归纯创作。

### 2.2 数据流演变

```
旧（同分支前序）：
  run_publish → assemble_publish_draft(candidate, body)
                  └─ 程序用 DB 拼《片名》(年份) + 正文 + 链接 → str（Markdown）

新（本次 fix.6）：
  run_publish → { "tmdb_id": <id>, "body": <纯正文> }   ← 结构化 JSON 产物
                  └─ clean_publish_body：仅剥除 LLM 误吐的标题行/链接
  下游平台适配器（4.4+）← 各自消费 DB 投影 + body，按平台规则拼骨架
```

### 2.3 API 变更
- `run_publish` 返回类型 `str → dict[str, Any]`，结构 `{tmdb_id, body}`。
- **删除** `resolve_publish_skeleton` / `assemble_publish_draft`（骨架解析与拼接，C2 不再需要）。
- **新增** `clean_publish_body(body) -> str`：保留对 LLM 误吐《片名》(年份) 标题行与 `themoviecosmos.com/movie/` 链接的防御性正文清洗。
- CLI `_run_publish_cli` 输出从 Markdown 文本改为 `json.dumps(..., ensure_ascii=False, indent=2)`。
- `format_selected_movie_block`（喂给 LLM 的**输入**块）保留 DB 投影与片名/年份——这是创作所需事实依据，与产物契约无关，未受影响。

## 3. 本地验证结果 (Verification)

- 单元测试：`python -m unittest tests.test_compose_publish -v` → **5 passed, OK**。
  - 含新增 `test_run_publish_strips_llm_emitted_skeleton`（LLM 误吐标题/链接时正文清洗剥除）。
  - `test_run_publish_feeds_db_and_judge_to_llm` 改为断言 `{tmdb_id, body}` 契约。
- 实跑（真实新闻 01-grid-outage，tmdb_id 429918）→ `publish_draft_v11.json`：

```json
{
  "tmdb_id": 429918,
  "body": "当全球的电力突然中断，东京的日常生活在顷刻间静止。…（纯正文，无标题行、无链接）"
}
```

- Lint：`scripts/compose.py` / `tests/test_compose_publish.py` 无新增诊断。

## 4. 潜在影响或技术债 (Technical Debt & Caveats)

- **对后续 Phase 的影响（正向）**：4.4+ 平台适配阶段现需自行用 DB 投影拼骨架。建议在平台 profile 抽象中明确「骨架拼接」为平台层职责，复用 DB 全列查询（ADR-0012）。各平台可对 `body` 自由包裹，互不耦合。
- **消费方契约变更**：任何下游读取 C2 产物的代码需从「读 Markdown 文本」改为「读 JSON 的 `body` 字段」。当前链路 C2 为末端，无既有消费方受影响。
- **fix.4 GATE 待重判**：本次为 fix.4 No-Go 后的整改项之一。GATE 节点（4.3-fix.4）仍为 `todo`，需总编对新 JSON 产物形态做 Go/No-Go 人工判定。
- 历史草稿目录 `output/phase4.3-fix.4-verify/` 仍未跟踪且混杂多版本，建议后续统一清理或归档，避免审核现场歧义。