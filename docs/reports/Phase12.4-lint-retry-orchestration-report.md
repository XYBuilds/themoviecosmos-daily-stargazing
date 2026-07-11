# Phase 12.4 - 命中即带反馈重试编排 交付报告

## 1. 改动范围 (Scope)

- `scripts/compose.py`：`run_publish` 内接入正文质量闸门 + 带反馈重试编排；新增模块级纯函数 `_build_body_repair_context`。
- `tests/test_compose_publish.py`：新增 `BodyQualityGateTests`（4 例）。
- 无新增/删除依赖包（复用已在 main 的 `scripts.lib.body_lint` / `scripts.lib.body_judge`）。

## 2. 技术实现 (Implementation)

### 闸门挂载点（ADR-0019 D3）

闸门接在 `run_publish` 的 `clean_publish_body(body)` 之后、`render_movie_header` 前置**之前** —— 只校验 LLM 正文，不碰确定性抬头（守 ADR-0018 边界）。

### 检测器与编排分离

- `body_lint.scan(body)`：**无条件**每轮跑（确定性、零 IO、零 LLM 成本）。
- `judge_body_fabrication(body, overview, llm_call=judge_llm_call, director=director)`：仅当注入了 `judge_llm_call` 才跑。
- 两者只返回违规清单；重试/降级由 `run_publish` 编排，检测器不参与。

### 带反馈重试循环（复刻 rewrite.py）

```
raw = _generate(prompt) → parse → clean
while True:
    violations = body_lint.scan(body)
    findings = judge(...) if judge_llm_call else []
    if not violations and not findings: break        # 通过
    if attempt >= max_body_retries: break            # 耗尽，保留最后一版
    attempt += 1
    retry_prompt = prompt + "\n\n" + _build_body_repair_context(violations, findings)
    raw = _generate(retry_prompt) → parse → clean     # 复刻 rewrite.py 尾部追加
```

`_build_body_repair_context` 是纯函数，把 `Violation`（rule_id + snippet + description）与 `Finding`（kind + quote + reason）拼成中文反馈喂回 LLM。

### 新签名

`run_publish(..., llm_call=None, judge_llm_call: Any = None, max_body_retries: int = 1)`。

### 不硬失败（ADR-0019 D4）

重试耗尽仍命中 → 保留最后一版 body，返回 dict 加 `warnings`：

```python
{"body_lint": [rule_id, ...], "fabrication": [{"kind", "quote", "reason"}, ...]}
```

只放最后一轮残余命中，不抛异常、不阻断扇出。

## 3. 本地验证结果 (Verification)

```
python -m pytest tests/test_compose_publish.py tests/test_body_lint.py tests/test_body_judge.py \
                 tests/test_review_panel_drafts_adapter.py tests/test_review_panel_publish_adapter.py -q
98 passed in 123.40s
```

- 新增 4 例：重试通过清 warnings、重试耗尽挂 warnings、judge 命中触发重试、judge 默认关闭零调用（用抛异常的 judge stub 证明未被触达）。
- 现有 `test_compose_publish.py` 全部未改动即通过（含 golden-snapshot、真实 client system message 断言）。
- ReadLints：`compose.py` / `test_compose_publish.py` 无诊断。

## 4. 潜在影响或技术债 (Technical Debt & Caveats)

### 零回归设计（五条边界，逐条守住）

1. **judge 独立注入**：`judge_llm_call: Any = None` 默认关闭，与 `llm_call` 独立 —— 不复用创作 stub 去跑 judge，避免二次调用覆盖测试捕获的 prompt / system message。
2. **body_lint 无条件跑但零副作用**：现有测试正文均不命中红线 → 零违规 → 不进重试 → `llm_call` 仍只调一次。
3. **首轮 prompt 逐字节不变**：repair_context 只在**重试轮**追加，未碰 `render_c2_prompt` / 模板 → golden-snapshot 不变。
4. **warnings 仅残余时加键**：clean 正文 dict 结构仍是 `{tmdb_id, headline, body}` → drafts_adapter 序列化不回归。
5. **_generate 闭包统一两条路径**：注入 llm_call / 真实 client 都走同一闭包，重试自动复用当前路径。

### 待 12.5 处理

- **judge 尚未在 drafts_adapter 扇出侧接线**：`run_publish` 已支持 `judge_llm_call` 注入，但 `run_fanout` 目前未传入。12.5 真重放时决定是否为扇出接入真实 judge（成本：N persona × judge 调用）。
- **成本**：接入 judge 后单 persona 调用量约 1 创作 + 1 judge + ≤K 重试。K 默认 1，务必保持小值。
- **judge 质量依赖 LLM**：语义判据有假阴/假阳，12.5 人工眼验仍是最终闸门。