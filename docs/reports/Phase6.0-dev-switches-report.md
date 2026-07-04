# Phase 6.0 - 开发快捷开关 交付报告

## 1. 改动范围 (Scope)

- 新增：
  - `scripts/lib/run_options.py` — `RunOptions` 纯数据 `@dataclass(frozen=True)`
  - `tests/test_run_options.py` — `RunOptions` 单元测试 + `run_eval.py` CLI 开关接线测试
- 改动：
  - `scripts/run_eval.py` — 新增 CLI 参数 `--personas` / `--skip-expand` / `--judge-topk` / `--force`；`run_eval_pipeline()` 新增可选 `run_options` 参数（默认 `None` → 等价于 `RunOptions()`，不改变既有行为）；`_run_cli()` 解析参数构造 `RunOptions` 并做同日输出覆盖保护
  - `.cursor/plans/Phase6-main-integration.plan.md` — `p6-debt-dev-switch` 状态 `pending` → `completed`
- 未改动：`scripts/main.py`（原因见第 4 节）
- 依赖：无新增/删除（未引入新的第三方包）

## 2. 技术实现 (Implementation)

`RunOptions` 是纯数据容器，字段与计划一致：

```python
@dataclass(frozen=True)
class RunOptions:
    persona_limit: int | None = None
    skip_expand: bool = False
    judge_topk: int = 2
    force: bool = False
```

设计上严格遵守"不改变现有函数签名"原则：

- `list_persona_ids()` / `run_persona_pipeline()` / `run_expansion()` / `retrieve_from_agents()` 的签名全部保持不变
- 所有开关逻辑只在调用方 `run_eval_pipeline()` / `_run_cli()` 内部实现：
  - `--personas N` → `persona_ids = list_persona_ids()[:persona_limit]`
  - `--skip-expand` → 跳过 `_resolve_expansion()` 调用，`expansion=None`，写入 `bridges.json` 时带 `"skipped": true` 标记，persona pipeline 仍正常调用（`expansion=None` 是 `run_persona_pipeline` 已支持的合法值）
  - `--judge-topk K` → `retrieve_from_agents(agents_list, errors, top_k=options.judge_topk)`（`top_k` 是该函数已有的具名参数，默认值 2，与计划口径一致）
  - `--force` → 若 `run_dir` 已存在且非空且未传 `--force`，`_run_cli` 提前返回 exit code 2 并打印错误，避免静默覆盖同日产物

`run_eval_pipeline()` 新增的 `run_options: RunOptions | None = None` 是尾部具名可选参数，旧调用方（若有）无需改动即可继续工作。

## 3. 本地验证结果 (Verification)

**新增单测**：
```
python -m pytest tests/test_run_options.py -v
# 5 passed in 17.03s
```
覆盖：`RunOptions` 默认值 / frozen 不可变 / 自定义值 roundtrip；`run_eval.py` CLI 在 `--personas 2 --skip-expand --judge-topk 5` 与默认（无开关）两种场景下，`run_eval_pipeline` 收到的 `RunOptions` 字段是否符合预期（mock 掉 LLM/IO 相关函数，纯参数流转测试）。

**全量回归**：
```
python -m pytest tests/ -q
# 8 failed, 269 passed, 1 skipped in 36.12s
```
失败的 8 个用例均在 `tests/test_copywriter_review.py`，与本次改动无关。已在 `main` 分支（未应用任何本次改动）单独复核：
```
git checkout main
python -m pytest tests/test_copywriter_review.py -q
# 8 failed, 18 passed in 7.62s
```
同样的 8 个测试在 `main` 上原样失败（`ReviewCopy` 缺少 `copy_text` 属性 + 若干中文断言字符串因源文件编码/BOM 问题被 pytest 读成 `�` 替换符），属于既有测试债务，与本 TODO 无关，未做修复（超出本 TODO 范围）。本分支上除这 8 个既有失败外，其余 269 passed / 1 skipped 与 main 基线一致，无新增 regression。

**验收命令（计划要求的真实命令）**：
```powershell
python scripts/run_eval.py --news-file tests/sample_news.json --personas 2 --skip-expand --run-id phase6-smoke-test
```
实跑结果（真实 LLM API 调用，非 mock）：
- exit code 0
- 日志确认 `[stage 3/6] expand skipped (--skip-expand)`
- 日志确认 `[stage 4/6] persona start total=2`（而非默认 12），仅跑了 `The-Innocent` / `The-Everyman`
- 产物目录 `output/Eval/phase6-smoke-test/agents/` 下只有 2 个 persona md 文件，`bridges.json` 内容为 `{"expansion": null, "errors": [], "warnings": [], "skipped": true}`
- 额外验证 `--force` 保护：不带 `--force` 二次跑同一 `--run-id` 返回 exit code 2 并报错 `run dir already has output: ... (use --force to overwrite)`
- 验证完成后已删除 `output/Eval/phase6-smoke-test/` 临时产物，不遗留在仓库中

无法验证项：`--force` 覆盖已有输出后重新生成产物的完整路径未单独重跑一次完整 pipeline（因单次全量 persona 跑耗时较长且消耗真实 LLM 配额），但代码逻辑上 `force=True` 时跳过覆盖保护分支、直接进入既有的 `write_eval_bundle`（原有 `mkdir(parents=True, exist_ok=True)` + 逐文件覆盖写入逻辑未变），行为等价于 Phase 5 之前的默认行为，风险低。

## 4. 潜在影响或技术债 (Technical Debt & Caveats)

- **main.py 现状判断**：读取确认 `scripts/main.py` 目前只有 16 行，纯 docstring + 一行 `# TODO(MVP-step-6): 串联所有模块...` 注释，无任何 CLI 骨架、无 `argparse`、无可执行逻辑，是彻底的空壳。按计划要求（"main.py 当前是空壳...本 todo 不需要改 main.py"），本次未接入 `RunOptions`，留给 6.2 处理。6.2 实现 main.py 管线时需要重复计划里的接线：解析 CLI → 构造 `RunOptions` → 传入 persona/expand/retrieve 调用点，可直接参考本次 `run_eval.py` 里 `_run_cli()` 的写法。
- **retrieve_from_agents 参数细节（供 6.1/6.2 参考）**：签名为 `retrieve_from_agents(agents, errors, *, top_k=DEFAULT_TOP_K, max_candidates=..., human_budget=None, quality_floor=..., judge_scores=None, min_judge_score=...)`，`DEFAULT_TOP_K = 2`，与计划里 `--judge-topk` 默认值一致，直接传 `top_k=` 即可，无需额外改造。
- **run_persona_pipeline 签名细节**：`async def run_persona_pipeline(persona_id, deconstruction, provider=None, *, expansion=None, prompts_dir=None, client=None, model=None)`，`expansion` 是具名可选参数，`skip_expand` 场景下传 `None` 是合法路径，未触发任何隐藏依赖 expansion 非空的断言。
- **list_persona_ids 细节**：无参数版本从 `personas-12.md` SSOT 解析，强制校验必须恰好 12 个 persona_id（否则抛 `ValueError`），`persona_limit` 是在拿到全量 12 个之后做 Python 切片 `[:N]`，不影响该校验时机。
- **`--force` 覆盖保护是新增行为**：Phase 5 及之前的 `run_eval.py` 对同日重复跑没有任何保护，会静默覆盖。本次新增的检查（`run_dir` 非空且未 `--force` 时报错退出）是一个**行为变化**，如果后续有自动化脚本/CI 依赖"重复跑会静默覆盖"的旧行为，需要显式加 `--force`。已在 6.1/6.2 依赖清单中标注此点，避免后续 subagent 误踩。
- **既有测试债务未处理**：`tests/test_copywriter_review.py` 的 8 个失败（`ReviewCopy.copy_text` 属性缺失 + 中文字符串编码问题）与本 TODO 无关，建议后续单开一个 TODO 修复，不阻塞 Phase 6.0/6.1/6.2 推进。
- **judge 分布重对齐占位**：计划里提到的 `--judge-profile` 占位参数本 TODO 未实现（计划标注"不实装逻辑"），如后续需要请在对应 TODO 中另行设计。