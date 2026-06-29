# compose 职责收敛：选片决策与发布稿创作分离、DB 全列经 by-id lookup 开放

**Status**: accepted（职责边界与方向拍板于 2026-06；**物理落地随 Phase 4 「4.3 No-Go 整改」循环实施**，见 [`.cursor/plans/Phase4-copywriter-c1-c2.plan.md`](../../.cursor/plans/Phase4-copywriter-c1-c2.plan.md)）

> **本 ADR 的性质**：职责边界治理。它 **部分 supersede [ADR-0011](0011-pipeline-stage-naming-and-legacy-purge.md) D1/D2** 中「`compose` = `review` + `publish` 两个对称 stage」「`C1` 审核稿」的语义假设——不推翻 0011 的英文动词命名宪法，只重新切分 `compose` 内部的职责。算法口径（双轴 judge / fragment ladder）全部沿用 [ADR-0009](0009-fragment-ladder-and-search-unit-architecture.md)、[ADR-0007](0007-logic-resonance-judge-prescreen-and-pov-focalization.md)。

## 背景

`compose`（原 `copywriter.py`）当前的 `--stage review` 把两类异质职责焊在同一个 prompt（`compose_review.md`）里：

- **面向总编的决策材料**：电影介绍（热度 vs 质量）、judge 评分理由中译——用于「选哪部」。
- **面向读者的内容初稿**：标题、文案、Hashtag——本质是发布稿的雏形。

由此产生三个结构问题：

1. **双受众焊死**：决策材料要客观可判断，读者文案要冷峻有共振，两种质量标准在一个 prompt 里互相拖累。
2. **数据流回溯**：`compose_publish.md` 要求「保留同一个『现实 ↔ 电影』的共振内核重写」，但上游从未把「内核」显式产出——它只产出了内核的中文成品（文案）。下游被迫从成稿里逆向考古内核。**而事实上该内核在更上游的 judge 已结构化存在**（`judge_resonance_type` / `causal_test` / `rationale`，见 `scripts/llm_judge.py`），却没被 `compose` 消费。
3. **为 N 部候选写读者级文案，最终只用 1 部**：审核期产出浪费在被淘汰的候选上；被选中的 1 部还要被 publish 推倒重写。

同时，电影元数据通道 `META_COLUMNS`（`scripts/build_index.py`，9 列白名单）把 `cleaned.csv` 的 28 列挡在索引外，导致发布稿想用 `director`/评分/热度等真实数据时只能拿到占位 `待补`（`scripts/compose.py`），或让 LLM 凭记忆杜撰「热度 vs 质量」。

## 决策

### D1 · `compose` 的职责按「投影 vs 创作」重新切分为两个非对称环节

废除「`review` 与 `publish` 是两个对称文案 stage」的旧假设。重新切分为：

| 环节 | 性质 | 受众 | 是否创作 | 输入 | 产物 |
| --- | --- | --- | --- | --- | --- |
| **选片决策卡**（原 `review`） | judge 产物 + DB 元数据的**投影 + 极轻翻译** | 总编 | **否**（禁止创作） | overview + 新闻原文 + `judge_score` / `resonance_type` / `causal_test` / `rationale` | 决策卡，供「选哪部 / 不发」 |
| **发布稿**（原 `publish`） | 唯一的**创作**环节 | 读者 | **是** | 选定电影 + DB 元数据（全列可得）+ judge 内核 + 新闻语境 | 社交发布稿（电影介绍为主体 + 共振钩子） |

- **共振内核不在 `compose` 内重新产出**：它在 judge（`scripts/llm_judge.py`）已结构化存在，两个环节都向上游消费，消除背景所述的数据流回溯。
- **决策卡不创作**：标题/读者文案/Hashtag 从决策卡移除，全部归入发布稿，且只对**选定的 1 部**精写。
- 本阶段**暂不做平台变体**：发布稿先产单一版本，平台分叉（原 4.4–4.7）维持后移。

### D2 · 选片决策卡的翻译口径：双语并列、逐句忠实、禁止文学加工

- judge 的 `causal_test` / `rationale` 当前为英文（证据见 `scripts/llm_judge.py` 输出 + `output/Eval/.../llm-judge-scores-thinking-enabled.json`）。
- 决策卡**同时保留原文（EN）+ 译文（ZH）**，成对并列排版（译文紧跟原文，减少编辑视线跳转）。
- 翻译**逐句忠实，禁止增删信息、禁止润色加工**——它是给编辑的工具，不是读者内容。双语并列使「翻译飞了」可被原文兜底。

### D3 · 电影元数据「全列开放」经 by-id lookup 通路，而非全塞进检索元数据

区分两条数据通路，禁止用 `META_COLUMNS` 单一白名单混用：

```text
通路 A · 检索伴随元数据 (meta.parquet)
  随 embeddings + 5.9万行一起进检索热路径；保持精简，按需微调展示列。
通路 B · by-id 明细 lookup  ← 全列开放归这里
  以 tmdb_id 点查，只对少数几部命中；cleaned.csv 全 28 列经此可得，不进检索热路径。
```

- 下游（决策卡 / 发布稿）按 `tmdb_id` 从通路 B 取任意字段，**要啥用啥，新增字段零基建改动**。
- **能力全开 ≠ 注入全开**：数据层全列可得是能力；具体喂给 LLM prompt 的字段子集由 prompt 设计按需选择，两层分离。`budget`/`revenue`/`imdb_id` 等敏感或无关列不无脑注入。

### D4 · 路 2（决策卡移出 `compose`）方向认定、落地押后

- **终态**：选片决策卡本质是 judge 之后的「人工评审 gate」投影，不属于 `compose`（创作）阶段；`compose` 应收敛为单一职责 = 发布稿创作。
- **时机**：物理拆分（动 SSOT 阶段划分 + 重命名环节）**押后到 Phase 4「4.3 No-Go 整改」循环内、Stage 1 启动时**实施，避免在未过 GATE 时引入跨阶段骨架重构（符合「Phase 顺序 + 人工阻断」纪律）。本 ADR 先认定方向并钉边界。

### D5 · 站内影片页文本不在本工作流（澄清，非决策）

站内页简介 = DB 的 `overview` 直出，**零 LLM**，与 `compose` 发布稿无生成路径共享。发布稿的「电影介绍」是 LLM 创作的社交主体，二者不复用、不耦合。

## 为什么

1. **切分轴从「框架 vs 微调」改为「投影 vs 创作」**，才对齐真实的受众边界与质量标准；旧切分让双受众在一个 prompt 内互相妥协。
2. **内核已在 judge 结构化存在**，让两环节各自向上游消费，比让 publish 从 review 成稿里逆向考古更短、更不失真。
3. **by-id lookup 满足「全列开放」诉求又不污染检索热路径**：全列可得是下游能力，检索精简是性能约束，两者经两条通路各得其所。

## 后果 / 已知局限

- **部分 supersede ADR-0011**：0011 D1/D2 中 `compose` 两 stage 的对称描述与 `C1/C2` 语义被本 ADR 重定义；0011 的英文动词命名宪法仍有效。SSOT（`news-to-film-pipeline.md`）需在 D4 落地时同步更新 `compose` 段。
- **过渡期 prompt 双态并存**：`compose_review.md` / `compose_publish.md` 在整改 TODO 落地前仍是旧形态；本 ADR 是边界声明，不是迁移工单。
- **数据回填为前置基建**：发布稿用真实 director/评分/热度依赖通路 B 落地；未落地前发布稿对这些字段**可选透传**（有则用、无则省略），不被阻塞。
- **全量 `cleaned.csv` 已确认含 28 列**（含 `director` / `vote_average` / `imdb_rating` / `popularity` 等），通路 B 为「加列穿透」级改动，非 API 工程。