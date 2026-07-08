# Phase 9.8.3 - regenerate_adapter.py 交付报告

## 1. 改动范围 (Scope)

新增文件：
- `review_panel/regenerate_adapter.py` — 单条定稿「重生成」薄适配脚本（165 行）
- `tests/test_review_panel_regenerate_adapter.py` — 单元测试（287 行，7 个用例）

依赖变更：无。

分支继承关系：本分支 `feat/phase9.8.3-regenerate-adapter` 从 phase 分支
`feat/phase9.8-panel-copy-regenerate-and-edit`（tip `cb0d99e`，含已并入的 9.8.1/9.8.2）检出，
未并入 main。

## 2. 技术实现 (Implementation)

**ADR-0016 D2/D3/D4 落地：与 `publish_adapter.py` / `rewrite_adapter.py` 同层的第三个薄适配器，
是重生成链路唯一 import `scripts.compose` 的入口，耦合收敛在此。**

顶层入口 `run_adapter(date, slug, tmdb_id, target, *, provider, platform, batch_root, run_publish, run_headline) -> Path`，
两种 `target` 走不对称的覆盖语义：

```
run_adapter(..., target)
  ├── locate_news_dir / load_news / find_candidate / load_judge_entry  # 复用 publish_adapter
  ├── parse_copy_markdown(现有 _copy_{platform}.md)                     # 复用 serve
  │
  ├─ target=body (D2):
  │     run_publish(candidate, news, ...) → 只取 body，丢弃顺带的 headline
  │     merged = {headline: 原 headline, body: 新 body}
  │     render_copy_markdown 覆盖回写
  │     _delete_copy_if_exists(_humanized.md)   # D4：body 变 → humanized 陈旧 → 删
  │
  └─ target=headline (D3):
        run_headline(candidate, news, current_body, ...) → body-aware 只出一句标题
        merged = {headline: 新 headline, body: 原 body}
        render_copy_markdown 覆盖回写
        # 不删 humanized（headline 不参与 body 的去 AI 化派生）
```

设计要点：
- **覆盖语义、不建版本层**：只改写既有 `{slug}_copy_{platform}.md` 的一半内容，不产出新文件，
  严守「原版 / 去AI化版」二档模型（D4）。
- **`run_publish`/`run_headline` 可注入**（默认绑 `compose` 真实函数），测试用 stub 替换，全程不触真 LLM。
- **humanized 失效边界只在 body**：body 变才删 `_humanized.md`；headline 变故意保留。
- **selection.json 不在本层碰**：adapter 保持「参数纯函数」，`humanized_path` 字段清理是 serve 层（9.8.4）职责。
- **tmdb_id 强制必填**：headline 也是 body-aware + movie-aware，需 candidate 经 `format_selected_movie_block` 喂给 prompt。
- CLI 错误路径经 `ValueError` → 非零退出（missing copy / empty body / unknown target），stderr 打印 `Wrote <path>` 供 serve 解析。

## 3. 本地验证结果 (Verification)

```
python -m pytest tests/test_review_panel_regenerate_adapter.py tests/test_review_panel_publish_adapter.py -q
........................                                                  [100%]
24 passed in 85.68s (0:01:25)
```

7 个新增用例覆盖：
- `target=body` 覆盖 body、保留原 headline、保留链接分区、删除 `_humanized.md`
- `target=body` 空 body → `ValueError`
- `target=headline` 覆盖 headline、保留 body、`current_body` 正确传入 `run_headline`、**不删** humanized
- `target=headline` 原稿 body 为空 → 在调 `run_headline` 前就 `ValueError`（不浪费 LLM 调用）
- 缺 copy 文件 → `ValueError`；CLI 层 → 退出码 2
- main CLI 端到端：参数解析 → 调用 → 打印 `Wrote <path>` → 返回 0

`publish_adapter` 既有测试无回归。测试耗时主要来自 `scripts.compose` 的 torch/sentence-transformers import，非真实网络/LLM 调用。

## 4. 潜在影响或技术债 (Technical Debt & Caveats)

- **对后续 Phase 的依赖**：9.8.4 的 `serve.py` 将新增 `POST /api/regenerate`，subprocess 调本 adapter，
  并从 selection.json 读出 tmdb_id 传入、成功后清 `humanized_path`。本 adapter 是其直接上游。
- **默认参数早绑定**：`run_adapter` 的 `run_publish`/`run_headline` 默认值在模块加载时绑定，
  事后 `patch("compose.run_headline")` 不会回填到已绑定的默认参数（Python 经典坑，`publish_adapter.py`
  同款设计亦如此）。测试策略已规避（main CLI 用例改为直接 patch `run_adapter`）；生产不受影响
  ——serve 层以真实默认函数调用，默认绑定的就是真实 `compose` 函数。
- **环境说明**：验证使用系统 Python（仓库无 `.venv`），功能验证不受影响。
- **无人工验收阻断**：本 TODO 非 `[需人工验收]`，按标准流水线进入合并（PR base 为 phase 分支）。