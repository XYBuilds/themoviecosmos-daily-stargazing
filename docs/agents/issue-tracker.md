# Issue tracker：GitHub

本仓库使用 GitHub Issues 跟踪 Matt Skills 创建的新需求与规格。所有操作通过 `gh` CLI 完成，仓库由当前目录的 Git remote 自动推断。

## 与既有 Phase 工作流的边界

- `.cursor/plans/Phase*.plan.md` 和 `docs/reports/` 保留原位，不迁移、不重新编号，也不批量转换为 Issues。
- GitHub Issues 是 Matt Skills 的需求与规格入口。
- 当已接受的 Phase TODO 进入实现时，其分支、验收、状态和交付仍遵循 `.cursor/rules/workflow-adapter.mdc`。
- Issue 可以链接到对应计划或报告，但不要在多个位置维护相互独立的 TODO 状态。

## 常用操作

- 创建：`gh issue create --title "..." --body "..."`
- 查看：`gh issue view <number> --comments`
- 列表：`gh issue list --state open --json number,title,body,labels,comments`
- 评论：`gh issue comment <number> --body "..."`
- 标签：`gh issue edit <number> --add-label "..."` 或 `--remove-label "..."`
- 关闭：`gh issue close <number> --comment "..."`

## Pull requests 是否作为需求入口

**否。** PR 只用于代码交付，不进入需求分流队列。

## Skill 语义

- 当 skill 要求“发布到 issue tracker”时，创建 GitHub Issue。
- 当 skill 要求“读取相关 ticket”时，使用 `gh issue view <number> --comments`。