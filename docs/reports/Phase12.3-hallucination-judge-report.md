# Phase 12.3 - LLM-judge 幻觉校验器 交付报告

## 1. 改动范围 (Scope)

- 新增 `scripts/lib/body_judge.py`：语义幻觉检测器（纯函数 + `llm_call` 依赖注入）。
- 新增 `prompts/_shared/body_fabrication_judge.md`：judge 用的核查提示词（非创作提示词）。
- 新增 `tests/test_body_judge.py`：11 条 stub 注入单测，不真联网。
- 无新增/删除依赖包（仅用标准库 `json` / `re` + 项目内 `scripts.lib.paths.repo_root`）。

## 2. 技术实现 (Implementation)

### 检测器与编排分离（ADR-0019 D0/D2）

`body_judge` 与 `body_lint` 并列为**检测器**：只返回违规清单，不改文本、不调真实 LLM 客户端、不决定重试。是否重试 / 如何拼反馈由上游 `run_publish` 承担（留给 12.4）。

- `Finding(NamedTuple)`：`kind`（`"fabricated_detail"` / `"wrong_director"`）+ `quote`（body 原文片段，供 12.4 拼 `repair_context`）+ `reason`（简短中文判据）。与 `body_lint.Violation` 同为不可变 NamedTuple，风格对齐。
- 主函数签名：

```python
def judge_body_fabrication(
    body: str, overview: str, *, llm_call: Callable[[str], Any], director: str | None = None
) -> list[Finding]:
```

- `llm_call` 设为**必填关键字参数**（非 `Any = None`）。理由：ADR-0019 D2 明确要求本模块「不 import openai、不建 client」，若默认走真实 LLM 就必须在模块内构造客户端，与该约束冲突。真实客户端的构造留给 12.4 的调用方（`run_publish`）注入。这是与 `run_publish` 的 `llm_call: Any = None` 唯一有意的差异。

### 唯一真值纪律

- `overview`（DB 剧情简述）是判定「编造」的唯一授权真值：body 出现 overview 没写的画面/角色/道具/结局 → `fabricated_detail`（即便真实电影确有其事）。
- `director`（DB 导演原名，可选）是判定「写错导演名」的唯一真值；未提供则跳过该检查。
- prompt 单列「只核查电影事实，不核查新闻」一节，防止把新闻侧专名/数字误判为幻觉。

### 解析容错（不硬失败）

`_parse_findings` 纯函数：先抓 ` ```json fence ` 内数组，抓不到则把整段当裸 JSON。非法 JSON / 空串 / 非数组 → 返回 `[]`，不抛异常。语义判据宁可漏判交人工，也不让一次 LLM 格式抖动砸掉整条 `run_publish` 编排。

## 3. 本地验证结果 (Verification)

```
python -m pytest tests/test_body_judge.py tests/test_body_lint.py tests/test_compose_publish.py -q
...............................................................          [100%]
63 passed in 9.96s
```

- `test_body_judge.py` 11 例：正例（fabricated_detail + wrong_director 用 05 场景真实句子 +《The Creator》真实 overview）、反例（空数组）、`_parse_findings` 四种容错分支、不改 body、stub 记录调用证明走注入、director 缺省、prompt 含 overview+body、Finding 不可变。
- 与 `body_lint` / `compose_publish` 合并跑无 regression。
- ReadLints：`body_judge.py` / `test_body_judge.py` 无诊断。

## 4. 潜在影响或技术债 (Technical Debt & Caveats)

- **12.4 接入契约**：`run_publish` 调用 `judge_body_fabrication` 时须传入真实 `llm_call`；`llm_call=None` 时构造真实客户端的逻辑放在**调用方**，不放 judge 内部（保 judge 零 IO 依赖）。
- **prompt 模板文件 IO**：`_load_prompt_template` 读 `prompts/_shared/body_fabrication_judge.md`，是渲染 prompt 所必需，不违反「检测器不做编排」（不改文本/不重试/不建 client）。这是 judge 相对 body_lint（纯正则零 IO）多出的一步文件读取。
- **judge 质量本身依赖 LLM**：语义判据有假阴/假阳，12.5 人工眼验仍是最终闸门。