# Phase 1.1 - agents.py 核心交付报告

## 1. 改动范围 (Scope)

- `scripts/agents.py` — 替换 TODO 空壳：数据模型、Persona 加载、模板渲染、异步并发 LLM、最小清洗、`run_all` API
- `.cursor/plans/Phase1-agents-pseudo-overview.plan.md` — Todo 1.1 标记为 complete
- 无新增依赖包（复用 `openai`、`python-dotenv` via `scripts.lib`）
- 未修改 `prompts/*.md`、未实现 CLI（1.3）与完整后处理（1.2）

## 2. 技术实现 (Implementation)

- **数据模型**：`NewsItem`（title/description/pub_time/source_name/url）、`AgentOutput`（含 `warnings` / `error`）、内部 `Persona`
- **Persona 加载**：显式列表 `A1`/`A2`/`A4`/`A7` 四个 `.md`；`agent_id` 自文件名前缀；`persona_name` 自 Markdown 标题行；A1 `role=baseline`，其余 `creative`
- **模板渲染**：替换 `{{title}}` / `{{description}}` / `{{pub_time}}` / `{{source_name}}`；空字段为 `—` 或 `unknown`；整份 persona 送入模型，不拼接 `_shared`
- **异步 LLM**：`asyncio.gather` + `asyncio.to_thread` 包装同步 `chat.completions.create`；默认 timeout 120s（`AGENT_LLM_TIMEOUT`）；单路失败写入 `AgentOutput.error` 与顶层 `errors`，不阻断其余
- **最小清洗**：去首尾空白、换行合并为单段、简单前言剥离（Sure / Here is 等）
- **公共 API**：`async def run_all(news, provider=None, agent_ids=None) -> tuple[list[AgentOutput], list[dict]]`；默认运行顺序 A2 → A4 → A7 → A1
- **sys.path**：与 `smoke_llm.py` 相同，仓库根入 path，支持 `from scripts.agents import ...`

## 3. 本地验证结果 (Verification)

```text
python -c "from scripts.agents import NewsItem, run_all; import inspect; print('import OK', inspect.iscoroutinefunction(run_all))"
# import OK True

python -c "… load_personas / render_prompt / minimal_clean …"
# unit checks OK
```

**Live LLM：** 本机未配置 `MIMO_API_KEY` / `DEEPSEEK_API_KEY`，跳过单 agent 实网调用。配置 `.env` 后可：

```powershell
python -c "import asyncio; from scripts.agents import NewsItem, run_all; … asyncio.run(run_all(news))"
```

## 4. 潜在影响或技术债 (Technical Debt & Caveats)

- 1.2 将补充截断、去实体化告警与更完整的前言/拒绝话术处理
- 1.3 将提供 CLI、`tests/sample_news.json` 与 stdout JSON 契约
- 同步 OpenAI 客户端经 `to_thread` 并发；若 rate limit 成为问题可换 `AsyncOpenAI`
- `AGENT_LLM_TIMEOUT` 未写入 `.env.example`（可选后续文档化）
