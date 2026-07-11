# Phase 12.2 - body_lint 确定性句式校验器 交付报告

## 1. 改动范围 (Scope)
- 新增 `scripts/lib/body_lint.py`：C2 正文句式红线检测器（纯函数 + DSL 红线表）。
- 新增 `tests/test_body_lint.py`：每条红线正/反例单测 + 纯函数契约 + DSL 结构断言。
- 新增/删除的依赖包：无（仅用标准库 `re` / `typing`）。

## 2. 技术实现 (Implementation)

### 设计对齐（ADR-0019 D0/D1）
- **能力边界**：只抓句式类红线，不碰语义幻觉（那是 12.3 LLM-judge 的职责）；`scan` 是检测器不做编排——只返回违规清单，不改文本、不调 LLM、零 IO。
- **FP 哲学**：复刻 `compose.py::render_movie_header` 的纯函数 + 模块级常量表风格。红线以 DSL 声明式组织：新增/调整红线 = 往 `RULES` 表加一行 `(rule_id, pattern, description)`，不动 `scan` 遍历逻辑。

### 数据结构
- `Violation`（`typing.NamedTuple`，不可变）：`rule_id` / `snippet`（命中原文片段，供 12.4 拼 repair_context）/ `description`（意图说明）。
- `RULES: list[tuple[rule_id, re.Pattern, description]]`：模块级红线表。
- `scan(body) -> list[Violation]`：遍历 RULES，对每条用 `finditer` 找全部命中，同规则多处命中各记一条（不去重），让上游看到实际违规次数与每处片段。

### 四条红线
| rule_id | 抓什么 | 正则要点 |
|---|---|---|
| `hard_transition` | 「而这部/而这恰/而这正…电影」硬转场 | `而这(部\|恰\|正)[^。！？]{0,40}?电影`，限句内且不超 40 字，避免误伤普通含「而」句 |
| `parallel_dianpo` | 「无论是…（还是…）都…」并列点破 | `无论是.{0,150}?都`，锚「无论是」+「都」收束（真实样本「还是」非必现，故不强制） |
| `verdict_stamp` | 「…同一种/同一个…」论点盖章 | `同一(种\|个)`，故意只抓两个强词、不要求前置「都/背后是」 |
| `acceptance_standalone` | 接受度单独成句 | 零宽断言锚句首（串首或紧跟 `。！？\n`）+ 「这部电影/影片/电影」+ 评价类词 + 句号收尾；从而放过揉进从句中段的合规写法 |

## 3. 本地验证结果 (Verification)

```powershell
python -m pytest tests/test_body_lint.py tests/test_compose_publish.py -q
# 52 passed in 7.55s
```

- `test_body_lint.py` 17 项：4 条红线各正例（真实 05 场景草稿句）+ 反例，另加纯函数不改入参、确定性、DSL 结构、Violation 不可变断言。
- 合并跑 `test_compose_publish.py` 确认既有链路零回归。

## 4. 潜在影响或技术债 (Technical Debt & Caveats)
- **初版红线不完备（预期演进，非缺陷）**：ADR-0019 已明确「新样式靠往 RULES 表加行迭代」。目前有意收窄以避免误伤：
  - `acceptance_standalone` 只抓句首为「这部电影/影片/电影」的强锚定模式；接受度以其他主语开头单独成句会漏检。
  - `verdict_stamp` 只抓「同一种/同一个」，未纳入「两者都在问」等弱信号。
  - `parallel_dianpo` 锚点放宽为「无论是…都」（真实样本 1 无「还是」），未见误伤反例。
- **能力边界**：body_lint 抓不住语义幻觉（编造画面/写错导演名），必须由 12.3 LLM-judge 补齐，否则漏网。
- **尚未接入链路**：本 TODO 只产检测器 + 单测，接进 `run_publish` 的重试编排是 12.4；本报告不代表闸门已在生产链路生效。
- 分支：`feat/phase12.2-body-lint-syntax-gate`，从最新 `main`（含 PR #143）检出。