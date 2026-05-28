"""agents.py · 多智能体编剧室.

加载 prompts/AX_*.md (跳过 _shared/), 异步并发请求 LLM (MiMo 2.5, 备选 DeepSeek),
为每个 Persona 产出一段去实体化的 pseudo-overview.

MVP:
  - 只跑 A2 / A4 / A7 三个 Persona (差异度最大, 先验证人格服从度).
  - 输出契约: 纯文本单段, 不做 JSON 强约束.
  - 失败/超时 -> 跳过该 Agent, 记录到 errors, 主流程继续.

LLM 客户端: 以 OpenAI 兼容协议为基线接 MiMo / DeepSeek.
"""

from __future__ import annotations

# TODO(MVP-step-3): 实现
#   1. load_personas(prompts_dir) -> list[Persona]
#   2. render_prompt(persona, news) -> str   (注入 title / description / pub_time / source_name)
#   3. async call_llm(prompt, model) -> str  (httpx / aiohttp 直调 OpenAI 兼容 endpoint)
#   4. async run_all(personas, news) -> list[AgentOutput]
#   5. 基础校验: 长度截断, 去前言后语, 检测明显违规实体名 -> errors
