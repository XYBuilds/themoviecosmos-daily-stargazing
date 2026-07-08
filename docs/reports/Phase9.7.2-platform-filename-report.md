# Phase 9.7.2 - 文件名平台化 + selection.json 升级 交付报告

## 1. 改动范围 (Scope)

- `review_panel/publish_adapter.py` — `run_adapter` 输出路径 `{slug}_copy.md` → `{slug}_copy_{platform}.md`；`platform` 透传进 `render_copy_markdown`。
- `review_panel/serve.py` — 新增 `_ACTIVE_PLATFORMS` 常量、`_delete_stale_copies()`、`_migrate_selection()`；`handle_select`/`handle_publish` selection.json 结构升级为 `copies` dict。
- `tests/test_review_panel_publish_adapter.py` / `tests/test_review_panel_serve.py` — 覆盖新文件名 + copies 结构 + 向后兼容迁移。
- `review_panel/build_data.py` — 确认不引用 copy 路径，**无改动**。
- 新增/删除依赖：无。

## 2. 技术实现 (Implementation)

**D3 文件名平台化**：`run_adapter` 写 `{slug}_copy_{platform}.md`（默认 xiaohongshu）。`serve.py` 引入 `_ACTIVE_PLATFORMS = ("xiaohongshu",)` 单一扩展点——改选时的陈旧稿清理 `_delete_stale_copies()` 按此清单逐平台删，未来加平台只改这一处。

**D4 selection.json copies dict**：
```json
{
  "date": "...", "selected": {...}, "selected_at": "...",
  "copies": { "xiaohongshu": {"published": true, "copy_path": "...", "humanized_path": null} }
}
```
- `handle_select` 写 `copies: {}`（改选即清空各平台发布态），不再写顶层 `published`/`copy_path`。
- `handle_publish` 成功后填 `copies[platform]`，保留可能已存在的 `humanized_path`（为 9.7.4 占位）。
- **向后兼容**：`_migrate_selection()` 在 `read_selection` 内即时把旧格式（顶层 `published`/`copy_path`）无损迁移为 `copies.xiaohongshu.*`，下游只认新形状。旧格式无 platform 维度，历史数据只可能是 xiaohongshu，映射安全。

`build_data.py` 全文只读 news/retrieve/judge/panel.json，从不引用 copy 路径，故按 plan「如引用则适配」判断 → 无需改动。

## 3. 本地验证结果 (Verification)

```
python -m pytest tests/test_review_panel_publish_adapter.py tests/test_review_panel_serve.py tests/test_review_panel_build_data.py -q
57 passed in 35.50s
```
含新增 `SelectionMigrationTests`（旧→新无损迁移 + 新格式 passthrough）。ReadLints 无告警。

## 4. 潜在影响或技术债 (Technical Debt & Caveats)

- 磁盘上暂无 selection.json（Glob 为空），迁移逻辑目前只由单测覆盖；9.7.7 真实重跑会产生首份新格式数据。
- `handle_publish` 的 `platform` 已支持 body 覆盖，但 UI（9.7.3/9.7.4）与 adapter CLI（`choices=["xiaohongshu"]`）当前只放行 xiaohongshu；扩展平台时三处需同步放开。
- 分支继承：`feat/phase9.7.2-platform-filename` 从集成分支检出（已含 9.7.1 合并结果）。