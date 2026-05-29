# Phase 0 - smoke_llm 交付报告

## 1. 改动范围 (Scope)

- `scripts/smoke_llm.py` — LLM 连通性 smoke CLI（`--provider mimo|deepseek`，默认读 `DEFAULT_LLM_PROVIDER`）
- `.cursor/plans/Phase0-index-and-llm-foundation.plan.md` — Todo 0.3 标记为 complete
- 无新增依赖包（复用 `openai`、`python-dotenv` via `scripts.lib`）

## 2. 技术实现 (Implementation)

- 启动时将仓库根目录加入 `sys.path`，保证 `python scripts/smoke_llm.py` 可导入 `scripts.lib`
- 通过 `load_env()` + `get_llm_client(provider)` 获取 OpenAI 兼容客户端
- 单轮 user message：`Reply with exactly: pong`；打印 provider、model（优先 API 返回的 `response.model`）、回复前 200 字符
- 失败（缺 key、缺 model、网络/API 错误）打印 `error: …` 到 stderr 并以退出码 1 结束

## 3. 本地验证结果 (Verification)

```text
python scripts/smoke_llm.py --help
# OK — usage 与 --provider {mimo,deepseek} 选项正常

python scripts/smoke_llm.py --provider mimo
# error: Missing MIMO_API_KEY for provider 'mimo'. …
# exit code 1（本机无 .env / 未配置密钥，符合预期）
```

**说明：** 本 CI/agent 环境未配置用户 `.env` 与 API 密钥，未执行真实 MiMo 调用。用户本地配置 `MIMO_API_KEY`、`MIMO_BASE_URL`、`MIMO_MODEL` 后应看到 `provider` / `model` / `reply` 三行输出且退出码 0。

## 4. 潜在影响或技术债 (Technical Debt & Caveats)

- `sys.path` 引导与 Phase 1 `agents.py` 的「从仓库根运行」约定一致；后续可统一为 `python -m scripts.*` 并去掉各脚本内联 path 插入
- DeepSeek smoke 需本地配置 `DEEPSEEK_*`；行为与 MiMo 相同
- 不校验回复内容是否字面等于 `pong`（仅验证 API 可达）
