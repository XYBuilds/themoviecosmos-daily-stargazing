# Phase 6.3 - publish 子命令 交付报告

## 1. 改动范围 (Scope)

| 文件 | 类型 | 说明 |
| --- | --- | --- |
| `scripts/main.py` | 修改 | 新增 `publish` 子命令：`resolve_candidates_path` / `resolve_copy_path` / `_parse_news_from_briefing_md` / `load_news_context_for_publish` / `find_candidate_by_tmdb_id` / `build_copy_markdown` / `_run_publish_cli` / `build_publish_parser`；`main()` 顶部新增 `argv[0] == "publish"` 分发分支 |
| `tests/test_main_publish.py` | 新增 | 覆盖 news 上下文解析、候选定位（成功/未匹配/文件缺失）、`_copy.md` 渲染、CLI 端到端（含 mock `compose.run_publish`） |
| `.cursor/plans/Phase6-main-integration.plan.md` | 修改 | `p6-publish` status: pending → completed |

- 新增/删除依赖包：无。

## 2. 技术实现 (Implementation)

### 2.1 CLI 设计

`main.py` 原有 CLI 是单一 `argparse.ArgumentParser`（无 subparsers）。为不改动既有解析结构、同时不引入 subparsers 的复杂度，`publish` 以「顶层命令分发」方式接入：`main(argv)` 先检查 `argv[0] == "publish"`，若命中则用独立的 `build_publish_parser()` 解析剩余参数并调用 `_run_publish_cli`；否则走原有日报管线解析逻辑。这是与现有风格（单文件、函数式、无框架依赖）一致的最小改动路径。

最终 CLI：

```text
python scripts/main.py publish --date 2026-07-04 --tmdb-id 157336 [--provider mimo|deepseek]
```

### 2.2 `--selected-file` / `--selected-copy` 的设计决策：简化为不实现

**决策：简化，只支持 `--tmdb-id`（必需）定位 candidate，不实现 `--selected-file` / `--selected-copy`。**

理由：
- 读完 `compose.run_publish(candidate, news, *, provider=None, judge=None, prompts_dir=None, llm_call=None) -> dict[str, Any]` 的真实实现（`scripts/compose.py:404-428`）后确认，它只需要 `candidate` + `news` 两个输入就能产出完整 C2 正文（`{"tmdb_id": ..., "body": ...}`）。`candidate` 由 `--tmdb-id` 从 `{date}_candidates.json` 定位即可拿到，不需要额外的手写文案旁路输入。
- 计划文档里 `--selected-file`/`--selected-copy` 语义本身就写着「不完全清楚」，且没有任何既有测试（`test_compose_publish.py`）、ADR（0012/0013）或 SSOT 文档提及这两个参数与 `run_publish` 有关联；它们更像是计划草拟阶段设想的「总编手写文案覆盖」旁路，但 C2 的定位就是「唯一创作环节」，总编的输入通道是「勾选 tmdb_id」而不是「手写替代文案」——若真要支持总编手改文案，合理的位置是 C2 产出之后再让总编编辑 `_copy.md` 本身，而不是在 CLI 层加两个不明确语义的参数。
- 生造这两个参数会引入未被消费、未被测试覆盖的死代码，违反「不要为了对齐计划文档而生造无意义参数」的要求。

### 2.3 `run_publish` 真实返回结构

```python
{
    "tmdb_id": <int|str>,   # candidate.get("tmdb_id")
    "body": <str>,          # clean_publish_body(raw) —— LLM 产出的纯中文正文
}
```

- **无骨架**：不含《片名》(年份) 标题行、不含电影链接（这两项由下游程序按 DB 投影拼接，`clean_publish_body` 会剥除 LLM 误吐的这两项）。
- **单语言**：`body` 只是中文创作正文，没有对应的英文翻译字段（C2 prompt 契约本身要求纯中文散文，2–4 段）。
- 报告任务描述中提到的「`没有 copy_text` 字段」的说法准确——但要注意 `copy_text` 是 **C1**（`ReviewCopy` 数据类）曾经在计划早期设想过的字段名，实际代码里 `ReviewCopy` 从未有过 `copy_text`（`main.py` 里 `_review_copies_payload` 的 docstring 已记录这段历史）；`run_publish`（C2）的产物字段是 `body`，与 C1 的 `ReviewCopy` 无关，两者不要混淆。

### 2.4 news 上下文的获取方式

`run_publish` 内部只消费 `news.get("title")` / `news.get("description")` / `news.get("url")`（经 `compose.build_news_context`），不需要完整的 `NewsItem` 对象或原始 retrieve_result。因此 `publish` 子命令**不重跑管线、不重新拉新闻源**，而是从已产出的 `{date}.md` 里的「## 现实波澜」小节（`render_briefing._format_reality_body` 写入的 `- **title**:` / `- **summary**:` / `- news_url:` 三行）用正则回填出这三个字段，构成 `run_publish` 需要的 `news` dict。这样 `publish` 严格是「日报管线产物的下游消费者」，不依赖任何额外输入源，也不需要重新持有 `NewsItem`。

### 2.5 candidate 定位

从 `{date}_candidates.json` 顶层 `candidates` 数组按 `str(tmdb_id)` 比较查找（兼容 JSON 里数字/字符串两种存储形式）。未匹配时报错并列出该日所有可用 `tmdb_id`，便于总编排查输错 id。

### 2.6 `_copy.md` 产物格式

`_copy.md` 含以下几节：`# 发布定稿 · {date} · 《片名》(年份)` → `## 中文发布正文`（C2 正文）→ `## 新闻原文（English source）`（原始英文新闻标题+摘要）→ `## 链接`（电影链接 + 新闻链接）。

**关于计划「含中英文两节」验收标准的落地方式**：C2 本身按 ADR-0012/ADR-0013 设计为**纯中文单语言创作**（`compose_publish.md` 明确要求「输出发布稿正文」，2–4 段中文散文，不产多语言变体），`run_publish` 不产出英文版本的正文。因此「中英文两节」在本次实现里理解为「中文创作正文 + 英文新闻原始语境」的并置（而非把中文正文机器翻译成英文），这与 C1 决策卡的「EN 原文 + ZH 译文」模式（面向总编、可回溯判断依据）不是同一种双语契约——C2 面向读者，是纯创作单语言产物。若总编期望的是「正文本身有英文译文供跨语言发布」，需要新增翻译环节（超出本 TODO 范围），已记录在技术债中。

真实产出示例（真实 API 跑通，`--date 2026-07-05 --tmdb-id 429918`，验证后已清理未提交）：

```markdown
# 发布定稿 · 2026-07-05 · 《Survival Family》(2017)

## 中文发布正文

这部电影描绘了一个当电力毫无征兆地从世界消失的场景。东京的便利生活瞬间停滞，一个普通家庭不得不踏上从都市向乡村逃难的旅程。……

影片在看过的人那里收获了稳定的好评，它的构思引起了许多人的兴趣。不过，它似乎也没有成为一部被广泛谈论或引用的作品……

## 新闻原文（English source）

**Regional grid operator warns of rolling outages after heat wave strains power plants**

Officials said several fossil-fuel units tripped offline during record demand, ……

## 链接

- 电影: https://themoviecosmos.com/movie/429918
- 新闻: https://example.com/article/1
```

## 3. 本地验证结果 (Verification)

- 新测试文件 `tests/test_main_publish.py`：`python -m pytest tests/test_main_publish.py -q` → **9 passed**。覆盖：
  - news 上下文解析成功 / 缺失 `{date}.md` 报错
  - candidate 定位成功 / tmdb_id 未匹配报错（错误信息含请求 id 与可用 id 列表）/ `{date}_candidates.json` 缺失报错
  - `_copy.md` markdown 渲染内容正确性
  - CLI 端到端成功路径（mock `compose.run_publish`）、tmdb_id 未匹配退出码非 0、candidates.json 缺失退出码非 0
- **真实端到端跑通**（有真实 API key，走真实 LLM 调用，非 mock）：
  ```
  python scripts/main.py publish --date 2026-07-05 --tmdb-id 429918
  Wrote .../output/Daily_Briefing/2026-07-05_copy.md
  ```
  消费的是既有 6.2 测试残留产物 `output/Daily_Briefing/2026-07-05.md` + `2026-07-05_candidates.json`（未新跑主流程，因其已存在且结构符合预期）。产出内容见上方示例，符合 C2 平视调性契约（无评分裸数字、无内部术语、无标题行/链接回显）。验证后已删除 `2026-07-05_copy.md`（临时产物，未提交）。
- 全量回归：`python -m pytest tests/ -q` → **288 passed, 8 failed, 1 skipped**。8 个失败均为已知基线（`tests/test_copywriter_review.py` 里 `ReviewCopy.copy_text` 相关的历史遗留断言，与本次改动无关，6.2 报告已记录同一基线）。**无新增失败**。

## 4. 潜在影响或技术债 (Technical Debt & Caveats)

- **`--selected-file` / `--selected-copy` 简化决策**：本次判定这两个参数在当前架构下无必要性并未实现（见 §2.2）。如果未来产品需求变成「总编手写文案覆盖 C2 输出」，建议的落地方式是：`publish` 产出 `_copy.md` 后，允许总编直接编辑该文件（人工流程），或新增独立的 `--override-body` 参数直接跳过 LLM 调用写入指定正文——而不是重新引入语义不明的 `--selected-file`/`--selected-copy`。
- **「中英文两节」验收口径的解释性偏差**：本次实现将其理解为「中文正文 + 英文新闻原始语境并置」，而非「正文本身双语」。若总编验收时期望的是后者（正文附带英文翻译供海外发布），需要新增一个翻译步骤（可复用 C1 的 EN/ZH 并列模式，但那是给总编看的忠实翻译，不是创作），这是一个需要人工确认的产品决策，非本 TODO 技术缺陷。
- **不重跑管线**：`publish` 完全依赖 `{date}.md`/`{date}_candidates.json` 已存在，不重新调用 `resolve_news`/deconstruct/retrieve。若总编需要针对同一天的不同新闻/不同 run 反复 publish 不同 tmdb_id，此设计工作良好；但若 `{date}.md` 被覆盖（如用 `--force` 重跑主流程），旧的 tmdb_id 候选可能已不在新的 candidates.json 中，`publish` 会给出清晰的「未找到候选」报错而不是静默使用旧数据，这是有意为之的安全行为。
- **正则解析 `{date}.md` 的耦合**：`_parse_news_from_briefing_md` 依赖 `render_briefing._format_reality_body` 固定的 Markdown 格式（`- **title**:` / `- **summary**:` / `- news_url:`）。若未来该渲染函数格式变化，需要同步更新此解析逻辑；更稳健的替代方案是让主管线额外把 `news_dict` 落一份 JSON（类似 `_candidates.json`），但这超出本 TODO 最小改动范围，留作后续技术债。
- **对 6.4（文档）有帮助的发现**：真实端到端使用流程验证为：
  1. `python scripts/main.py --pick N`（或 `--news-file`）产出 `{date}.md` + `{date}_candidates.json`
  2. 总编在 Obsidian 里肉眼审核 `{date}.md` 候选星轨部分，确定选用哪个 `tmdb_id`
  3. `python scripts/main.py publish --date {date} --tmdb-id {id}` 产出 `{date}_copy.md`，供总编直接复制发布
  该三步流程与 README 已记录的「fetch_news → 手挑 → main.py → Obsidian 勾选 → main.py publish」端到端工作流完全一致，本次实现未偏离既有文档预期。

## 附：分支与合并纪录（自动化流水线执行中的意外与恢复）

执行第 3 步（Commit）时，由于工作区与 Phase 6.4 subagent 共享同一份本地 git checkout（非独立 worktree），提交瞬间 `HEAD` 实际处于 `main`（被并行 subagent 的 `git checkout main` 切换），导致 `feat(main): p6.3-add-publish-subcommand` 一度落在本地 `main` 分支而非 `feat/phase6.3-publish`。发现后立即通过以下非破坏性操作恢复：
1. `git branch -f main origin/main`：把本地 `main` 指针拨回远端已知状态（未使用 `reset --hard`，未丢失任何提交，本地 `main` 上从未有它独有的未推送提交）。
2. `git merge --ff-only 100b541`（在 `feat/phase6.3-publish` 上，该分支此时仍在 6.2 合并点 `09ddf39`，未分叉）：快进合入误落地的提交。
3. 验证 `git diff main..feat/phase6.3-publish --stat` 只包含预期的 `scripts/main.py` + `tests/test_main_publish.py` 改动，工作区 `git status --short` 为空。

全程未使用 `reset --hard` / 强推 / 交互式命令，未丢失任何提交历史。