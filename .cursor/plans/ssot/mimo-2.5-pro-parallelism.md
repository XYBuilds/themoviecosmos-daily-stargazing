# Mimo 2.5 Pro 并行参数 / 策略 SSOT

> 适用范围：Phase 7.3 / 7.4 的并行设计、调优、冒烟验证与恢复策略。
> 约束边界：不改 `heat_pool` 语义，不改 prompt，不改 `retrieve` 排序。

## 1. 模型约束

- 上下文窗口：`1M context`
- 输出上限：`128K output`
- 请求速率：`RPM 100`
- 令牌速率：`TPM 10M`
- 限制粒度：**账号级限制**，不是单任务独立限额
- 风险：高并发/长输出下更易出现 `429`、`timeout`
- 设计原则：所有并行与重试都必须在账号级预算内收敛

## 2. 推荐拓扑

- `heat_pool`：串行，只负责选题 / 池化 / 富化，不并发展开
- `daily_batch item scheduler`：按 item 维度调度，负责 item 间分发
- `persona`：item 内并发，承担主要吞吐
- `global LLM limiter`：全局统一限流，所有 LLM 调用进入同一预算池

## 3. 默认参数

```text
item_concurrency=2
persona_concurrency=4
global_llm_concurrency=3
global_rpm_budget=80
global_tpm_budget=8_000_000
retry_attempts=4
backoff=exponential+jitter
```

## 4. 状态机

```text
pending -> deconstruct -> expand -> persona -> retrieve -> compose -> done
```

- 状态推进以 stage 为主
- persona 阶段允许按 persona 粒度续跑
- `resume` 必须可从最近一次稳定 checkpoint 继续

## 5. 错误定位字段

统一记录以下字段，便于定位 429、超时和恢复失败：

- `date`
- `item_index`
- `item_slug`
- `stage`
- `persona_id`
- `attempt`
- `model`
- `elapsed_ms`
- `error_class`
- `retryable`

## 6. 自动降级顺序

1. 降 `persona_concurrency`
2. 降 `item_concurrency`
3. 降 `global_llm_concurrency`
4. 降 `global_rpm_budget`
5. 回退到串行 item

> 降级只改变调度强度，不改业务语义与产物结构。

## 7. 测试矩阵与命令

| 场景 | item 并发 | persona 并发 | 目的 |
|------|-----------|--------------|------|
| p2 / i1 | 1 | 2 | 低并发基线，验证端到端与 resume |
| p4 / i2 | 2 | 4 | 默认基线，验证吞吐与稳定性 |
| p6 / i3 | 3 | 6 | 压力边界，观察 429 / timeout / retry |
| full tune | 动态 | 动态 | 按日志和失败率做参数收敛 |

```powershell
python scripts/daily_batch.py --date 2026-07-05 --min-count 3 --personas 2
python scripts/daily_batch.py --date 2026-07-05 --min-count 3 --personas 4
python scripts/daily_batch.py --date 2026-07-05 --min-count 3 --personas 6
python scripts/daily_batch.py --date 2026-07-05 --resume
```

## 8. 判定阈值

- `success = 100%`
- `429 < 1%`
- `retry < 2%`
- `hard failure = 0`
- `state json valid`
- `resume works`

## 9. 记录要求

- 每次 smoke/tuning 保留：参数组合、失败样例、恢复是否成功、最终状态 JSON
- 若触发自动降级，记录降级前后的并发/预算值
- 仅在 7.3 / 后续调优中使用，不回写到采集语义或 prompt 设计
