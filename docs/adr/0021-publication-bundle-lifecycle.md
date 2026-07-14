# 发布包生命周期：独立工作区、显式准备与非破坏性审计

**Status**: accepted（Phase 13.1）

> 本 ADR 定义 `daily_batch` 与 publication bundle 的职责边界。它不引入自动发布；发布包只为人工审核后的文案与视觉资产提供可独立查看的工作区。

## 背景

现有 `output/daily_batch/{date}/` 同时保存新闻、检索、judge、persona 草稿池和最终文案路径。过程证据与可发布产物共用目录会造成三个问题：选择变更会误删旧稿、调用方需要猜测散落路径来恢复状态、面板无法独立呈现海报和星球图的生成状态。

Phase 13 需要把选择后的最终工作移到稳定的 bundle，同时保留 `daily_batch` 作为流水线证据和草稿池。面板仍是本地审核工具，不承担自动发布。

## 决策

### D1 · publication bundle 是可发布工作区的唯一边界

每一条选择映射到：

```text
output/publications/{date}/{tmdb_id}-{slug}/
├─ manifest.json
├─ copy/
│  ├─ xiaohongshu.md
│  └─ xiaohongshu-humanized.md
└─ assets/
   ├─ poster-original.jpg
   ├─ planet.png
   └─ planet.png.render.json
```

新增 [publication_bundle.py](../../review_panel/publication_bundle.py) 是唯一可构造 bundle ID、投影目录、读写和校验 `manifest.json` 的模块。服务层、适配器与前端接口不得自行拼接 `output/publications` 路径。

`bundle_id` 固定为 `{tmdb_id}-{slugify(title)}`。slug 仅保留 `[a-z0-9-]`；标题无法得到 ASCII slug 时回退为 `{tmdb_id}`，以保证确定性和 Windows 路径安全。

### D2 · selection 与 manifest 分别是选择和发布工作区的 SSOT

`selection.json` 只回答“选中了什么”：日期、新闻 slug、TMDB ID、标题和选择时间。它不保存 copy 指针、草稿 ID、资产路径或任务状态。

`manifest.json` 是发布包的 SSOT，至少保存：

- `schema_version` 与稳定的 `publication_id`；
- selection 快照；
- bundle 顶层状态；
- 草稿、海报、星球和每个平台当前稿的分项状态、相对路径、错误与来源。

所有 artifact 路径必须相对于 bundle 根目录。未知 schema、缺失字段、绝对路径、盘符路径和 `..` 越界路径均在读取或写入时快速失败。

### D3 · 显式准备，独立并行，按项失败

选择候选只写 `selection.json`，不触发 LLM、TMDB 下载或渲染。用户点击“准备发布包”后，编排层并行启动草稿池、海报和 Bloom ON 星球图；每项独立更新 manifest。任意一项失败不取消其他项。

顶层状态由纯函数归并：准备 artifact 仍有 `pending` 或 `running` 时为 `preparing`；存在失败且没有待执行项时为 `partial`；草稿、海报与星球全部就绪时为 `ready`。平台最终稿是编辑阶段状态，不阻塞发布包准备状态。

### D4 · 改选不删除，旧包标记 superseded

改选其他候选时，旧 bundle 只将 manifest 标为 `superseded`，文件和 artifact 全部保留。重复选择同一个候选是幂等操作，不清空已准备资产。重新选回旧电影时可重新读取该 bundle，由审核者决定是否重新准备。

这替代了删除旧 `_copy_*.md` 的清理策略，保留选型和文案演进的审计记录。

### D5 · 草稿池与最终文案分离

`daily_batch` 持续保存 persona 草稿池，例如 `{slug}_drafts_xiaohongshu.json`。选择主视角后，当前稿写入 bundle 的 `copy/xiaohongshu.md`；正文编辑、标题/正文重生成和去 AI 化稿也只更新 bundle。正文变化必须让 `xiaohongshu-humanized.md` 失效。

旧 `selection.json.copies` 和旧 `_copy_*.md` 保持只读兼容，不批量移动或删除历史产物。新流程不再回写旧 copies 结构。

### D6 · 视觉资产只准备一份 Bloom ON 星球图

海报通过通用 TMDB 下载器写入 `assets/poster-original.jpg`。星球图只调用一次 `render_planet(..., bloom=True)`，输出 `assets/planet.png` 与 render metadata。面板从 manifest 注册的路径读取 `poster` 或 `planet` 枚举，不接受任意原始文件路径。

## 后果与边界

- `manifest.json` 使用每 bundle 锁、临时文件和 `os.replace` 写入，避免并行任务造成丢失更新或半份 JSON。
- `daily_batch` 仍是过程证据；后续平台集成必须从 manifest 消费状态，不能扫描散落文件猜测状态。
- 本 ADR 不授权小红书、X 或 Reddit 自动发布，也不修改历史 output。
- 面板仍绑定 `127.0.0.1`；受限 asset API 不构成公网文件服务。