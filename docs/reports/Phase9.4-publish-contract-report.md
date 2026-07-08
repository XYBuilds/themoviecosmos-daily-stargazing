# Phase 9.4 · --platform + publish system message + run_publish headline — 交付报告

## 改动范围（Scope）

- `scripts/compose.py`：CLI `--platform`、`load_c2_template` 平台化、`_PUBLISH_SYSTEM_MESSAGE`、`_sync_llm_call` 加参、`parse_publish_output`、`run_publish` 返回结构扩容。
- 删除 `prompts/compose_publish.md`（loader 平台化后为死文件）。
- `tests/test_compose_publish.py`：headline+body 契约、sentinel 解析、平台选 prompt、publish system message 覆盖。

**分支继承**：`feat/phase9.4-publish-contract` 从 `feat/phase9.3-xhs-prompt` 检出（未合并、PR #110）。链：9.1→9.2→9.3→9.4。

## 技术实现（Implementation）

- **平台化（D1）**：`_C2_PROMPT_FILENAME = "compose_publish_{platform}.md"`、`_DEFAULT_PLATFORM="xiaohongshu"`、`_PLATFORMS=("xiaohongshu",)`。`load_c2_template(platform, prompts_dir)` 按平台选文件。CLI 新增 `--platform`（`choices=["xiaohongshu"]`, default xiaohongshu），stage 名不变。
- **publish 专用 system message**：`_PUBLISH_SYSTEM_MESSAGE` 要求产「标题+正文」、守平视调性、遵 sentinel 契约。`_sync_llm_call` 加 `system_message` 形参（默认仍 `_SYSTEM_MESSAGE`，C1 不变），`run_publish` 真实路径传 `_PUBLISH_SYSTEM_MESSAGE`。**解决了硬坑**：决策卡 message 的「不要输出标题」会压制 headline。
- **产物契约（D4）**：`run_publish` 返回 `{tmdb_id, headline, body}`。`parse_publish_output(raw)` 按 `【标题】`/`【正文】` sentinel 解析；缺 `【正文】` 时退化（有 `【标题】` → 首行标题+余下正文；两 sentinel 全缺 → headline 空、整段作 body）。body 仍走 `clean_publish_body`。headline 只取首行。
- **兜底**：sentinel 缺失不静默出半稿——body 为空时 CLI 退出码 1（`_run_publish_cli` 原有 `body` 空判失败逻辑保留）。
- **旧 prompt 去留（交代 9.3 遗留项）**：`compose_publish.md` 删除；无代码再引用它（grep 确认仅 `load_c2_template` 曾引用，已改）。

## 本地验证结果（Verification）

```
python -m pytest tests/test_compose_publish.py -q            → 12 passed
python -m pytest tests/test_compose_decision_card.py tests/test_main_publish.py -q  → (随 23-passed 批次)绿
python -m pytest tests/test_review_panel_publish_adapter.py -q → 14 passed（9.4 未动 adapter，无 ripple）
python scripts/compose.py --stage publish --platform badplat …
  → error: argument --platform: invalid choice: 'badplat' (choose from xiaohongshu)
```

- `run_publish` 返回含 `headline` 与 `body`；sentinel 已剥离。✅
- 归属行「」保留、《》(年) 行与裸链接仍剥除。✅
- publish 真实路径发 `_PUBLISH_SYSTEM_MESSAGE`（≠ `_SYSTEM_MESSAGE`）——mock client 断言。✅
- 缺 `--platform` 默认 xiaohongshu；未知平台 CLI 报错、`load_c2_template` 抛 `FileNotFoundError`。✅
- CLI `--platform xiaohongshu --tmdb-id 1379520` 全链跑通（需真实 LLM）→ 归 9.8 GATE 验证。

## 潜在影响或技术债（Technical Debt & Caveats）

- **main.py 旧 publish 路径**：`scripts/main.py` 的 Phase 6 单条 publish 仍调 `compose.run_publish(candidate, news, provider=...)`（不传 platform/judge），默认平台 xiaohongshu，现也走小红书 prompt 并返回 headline（该路径不消费 headline，无害）。未在本 Phase 为其加 `--platform`（超出 scope）。
- **headline 空非硬失败**：仅 body 空判失败（ADR-0015 D4「先试后调」+ G6 人工兜底）。GATE 人工检查 headline 非空。
- **sentinel 依赖 LLM 守约**：`parse_publish_output` 有退化路径，但若 LLM 完全无视 sentinel，headline 会退化为空、归属行落入 body——GATE 人工兜底。
