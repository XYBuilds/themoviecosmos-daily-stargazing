# Phase 1.3 - CLI 与 fixtures 交付报告

## 1. 改动范围 (Scope)

- `scripts/agents.py` — CLI：`--news-file`、`--out`、`--provider`、`--agents`；JSON 契约输出
- `tests/sample_news.json` — 样本新闻 fixture
- `README.md` — MVP 步骤 1–2 更新（全量索引 + Agent 命令）
- `.cursor/plans/Phase1-agents-pseudo-overview.plan.md` — Todo 1.3 complete

## 2. 技术实现 (Implementation)

- `load_news_from_file` / `build_result_payload` / `news_to_dict` / `agent_to_dict`
- stdout UTF-8 JSON；`--out` 写文件并 stderr 打印路径
- 退出码：全部 agent 失败 → 1；参数/文件错误 → 2
- `sys.path` 引导与 Phase 0 smoke 一致，仓库根目录直接 `python scripts/agents.py`

## 3. 本地验证结果 (Verification)

```text
python scripts/agents.py --help
python -c "load_news_from_file(tests/sample_news.json)"  # news OK
python scripts/agents.py --news-file tests/sample_news.json --out output/agents_cli_test.json
# exit=1 (no API keys); JSON: 4 agents + errors — structure OK
python -c "assert len(d['agents'])==4"  # json OK ['A2','A4','A7','A1']
```

有 `.env` 时运行：`python scripts/agents.py --news-file tests/sample_news.json` 应 exit 0 且至少 3 路非空 `text`。

## 4. 潜在影响或技术债 (Technical Debt & Caveats)

- Phase 1 整体验收需用户本地 MiMo/DeepSeek 连通性
- `output/` 测试产物未提交（应在 gitignore）
