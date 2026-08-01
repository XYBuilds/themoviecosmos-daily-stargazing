# Domain docs

本文件规定 Matt Skills 在探索与修改 Daily Stargazing 时如何读取领域文档。

## 开始探索前

按任务范围读取：

1. 根级 `CONTEXT.md`：项目术语表及明确禁用的旧称。
2. `docs/SSOT/` 中与任务相关的当前产品或数据契约。
3. `docs/adr/` 中与任务相关的决策，包含 `Status`、修订与 `supersedes` 链。
4. 仅在执行已接受的 Phase TODO 时，读取对应 `.cursor/plans/Phase*.plan.md`；历史计划和报告只作证据，不作当前设计权威。

不要为了补齐形式而预先创建新的 `CONTEXT.md` 或 ADR。只有领域术语或长期决策真正被确认后，才通过 domain-modeling 流程更新。

## 文件结构

本仓库采用 single-context 布局：

```text
/
├─ CONTEXT.md
├─ docs/
│  ├─ SSOT/
│  ├─ adr/
│  └─ reports/
└─ .cursor/
   └─ plans/
```

不创建 `CONTEXT-MAP.md` 或子上下文，除非仓库以后真实拆分为多个独立业务上下文。

## 术语

Issue 标题、规格、重构提案、测试名和文档应使用 `CONTEXT.md` 已定义的术语。若需要的新概念尚未定义，先判断它是错误同义词还是实际领域缺口；实际缺口交由 domain-modeling 流程确认。

## 文档冲突

- 显式标记为 `accepted` 的 ADR 及其 `supersedes` / revised 链，优先于被取代的旧 ADR、历史计划和历史报告。
- `docs/SSOT/` 表达当前产品与契约，`CONTEXT.md` 表达当前领域词汇；两者不应被历史计划或报告反向覆盖。
- 若当前 SSOT、现行 ADR、`CONTEXT.md` 或运行行为互相冲突，必须列出具体文件和冲突内容，向用户确认应修正哪一侧。不得静默选择、批量归一化或借 setup 改写旧文档。
- 运行行为用于确认系统实际做了什么；它可以证明文档已过期，但不能自行改写产品意图。

若输出将违反现行 ADR，应明确标注，例如：

> 与 ADR-0007 D1 冲突；需要先确认是否重开该决策。