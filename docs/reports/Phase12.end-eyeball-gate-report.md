# Phase 12.end - C2 正文质量闸门眼验 GATE 交付报告

## 1. 改动范围 (Scope)

本 TODO 为 `[需人工验收]` 眼验闸门，无代码改动，仅收尾产物：

- `.cursor/plans/Phase12-c2-body-quality-gate.plan.md`：`p12.end-eyeball-gate-manual-approve` 由 `status: todo` → `complete`；正文 12.end 小节阻断说明改为「人工 Go（已 approve）」，验收项逐条勾选并附残留 warnings 处置与遗留改进项。
- `docs/reports/Phase12.end-eyeball-gate-report.md`：本报告。

无依赖包增删。

## 2. 技术实现 (Implementation)

12.end 是 Phase 12 的收尾人工验收闸门，验收对象是 12.1–12.5（C2 正文质量闸门主体）+ 12.6.x（面板长任务异步 job 框架）合并后的整体效果。gate 本身不写代码，判定依据是真实重放产物 + 人工眼验。

**为何 gate 依赖 12.6.x 先落地**：gate 验收项含「面板 warnings 展示 + 单份 retry 闭环肉眼可用」。retry+judge 真实链路约 132s，此前同步 HTTP 端点在响应回来前连接已被中止（`_send_json` → `ConnectionAbortedError`），retry 闭环不可用。12.6.x 把 6 个长任务端点改为「后台 job + 前端轮询（202 + `/api/job` 四态）」，retry 闭环方可验收。故执行顺序为 12.1→…→12.5→12.6.1→…→12.6.5→12.end。

**验收证据链**：git log 实锤 12.6.x 五项（PR #148/#149/#150/#152/#153，含期间 hotfix #151）全部并入 `main`；`Phase12.6-*.plan.md` 五项 `status: complete`；落地动作 B 已生效（gate 改名 12.end、依赖注明 retry 闭环依赖 12.6.x）；工作区干净 `## main...origin/main`。

## 3. 本地验证结果 (Verification)

重放场景：`output/daily_batch/2026-07-06/05-ai-poses-hiroshima-style-threat-to-humanity_drafts_xiaohongshu.json`，新闻 = AI/广岛威胁，候选 = tmdb 670292《The Creator》，7 份草稿（混合视角 + The-Innocent/The-Hero/The-Caregiver/The-Outlaw/The-Lover/The-Creator）。

逐条验收项：

| 验收项 | 结果 |
| --- | --- |
| 句式红线 `body_lint` 归零 | 4/7 干净；残留 2 处：The-Caregiver `acceptance_standalone`、The-Creator `parallel_dianpo`（已 warnings 标记） |
| `judge` 幻觉压住、导演名正确 | 导演名 Gareth Edwards 全程正确未再写错；残留 The-Outlaw 2 处 fabrication（含年份误报，见下）已 warnings 标记 |
| Persona ①偏② 显形、3–4 段扫读密度 | 肉眼验通过（各 persona 视角差异明显、段落密度达标） |
| 面板 warnings 展示 + 单份 retry 闭环可用 | 依赖 12.6.x 异步框架，已落地可用 |
| `[需人工验收 · Go/No-Go]` | **Go**（接受残留 warnings 作人工兜底项） |

**残留处置（人工 Go 依据）**：ADR-0019 D4「不硬失败·挂 warnings 交人工兜底」为既定设计。重放产物的 3 处残留（2 句式 + 2 幻觉，分布于 3 份草稿）均已正确写入 draft `warnings`，编辑可在面板 ⚠ 徽标看到详情并对该单份手动 retry 或弃用。系统按设计工作，人工决定接受残留、不阻断收尾。

## 4. 潜在影响或技术债 (Technical Debt & Caveats)

- **judge 真值源缺口（遗留改进项，不阻断本 gate）**：`judge_body_fabrication` 只拿 DB `overview` 当唯一真值，看不到确定性抬头投影（Phase11 ADR-0018）。故 The-Outlaw 的「2023 年」被判幻觉——`2023` 实为抬头 `坐标：[Y: 2023]` 的 DB 授权数据，只是不在 overview 文本内。同类年份/评分等抬头字段会误报，且跨 persona 判定不一致（多份同写「2023 年」仅一份被判）。后续可让 judge 真值源纳入抬头投影字段，或对「DB 授权且已在抬头呈现」的事实豁免。另立轮次处理。
- **合并稿 retry 仍未做**：12.5 明确 `a+b` 合并稿 retry 被后端拒绝（MVP 不做），本 gate 不覆盖合并稿质量闭环。
- **成本**：接入 judge + 重试后，run_fanout 扇出 N persona 的 LLM 调用量约 N ×（1 创作 + 1 judge + ≤K 重试），K 已设小值。真实重放 retry+judge 单份约 132s。
- **Phase 12 全链路（12.1–12.6.x + 12.end）至此完成并可并入 main**，后续 Phase 从最新 main 检出。