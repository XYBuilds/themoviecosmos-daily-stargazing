# Phase 10.1 - 蒸馏 persona 视角 + ADR-0017 交付报告

## 1. 改动范围 (Scope)

- **新增** `prompts/personas/{Persona}/c2_perspective.md` × 12（The-Sage / The-Innocent / The-Everyman / The-Hero / The-Caregiver / The-Creator / The-Explorer / The-Jester / The-Lover / The-Magician / The-Outlaw / The-Ruler）
- **修改** `prompts/compose_publish_xiaohongshu.md`：新增「本条创作的主视角」段，注入 `{{persona_perspective}}` 占位符
- **新增** `docs/adr/0017-persona-perspective-c2-draft-pool.md`
- 依赖包：无新增

## 2. 技术实现 (Implementation)

### 2.1 c2_perspective.md 蒸馏（D1）

每份 persona 的 C2 侧视角指引采用统一三要素结构，压缩为一句话：

```
**主视角：<English · 中文名>**

<核心眼光——用什么角度切入> ; <关注张力——在意哪对矛盾> ; <调性——什么笔触>
```

蒸馏原则：从 `persona_card.md`（检索侧资产）抽取「创作可用内核」（核心情感 / 价值倾向 / 镜头方向），**剥离全部检索侧行话**（decon / P-Select / objective-floor / focalized / fit / 正极负极 / alt-creator lens）。12 份互相可区分，示例：

| persona | 核心眼光 | 关注张力 |
| --- | --- | --- |
| The-Sage | 求真、理性、辨识 | 被验证的事实 vs 被制造的扭曲 |
| The-Hero | 需跨越的难关、挺身而出 | 勇气担当 vs 压力下的退缩 |
| The-Outlaw | 质疑秩序、不甘规训 | 挑战权威 vs 被规则压制 |
| The-Ruler | 全局与秩序的高度 | 维系稳定 vs 动摇根基 |

### 2.2 C2 prompt 注入点（D2）

`compose_publish_xiaohongshu.md` 在「正例」段与「当前任务」段之间插入常量框架段，写清 **persona 视角（用什么眼光写）与 judge 内核（为什么共振）的分工**，并声明视角**绝不覆盖**去实体化 / 平视不排名 / 数字文字化 / 来源纪律等硬规则。变量部分为单一 `{{persona_perspective}}` 占位符——完全复刻 `{{headline_contract}}` 的 no-op 模式：模板此占位符在 10.2 由 `render_c2_prompt` 的新 `replace` 调用填充，空串注入时渲染与注入前等价。

### 2.3 ADR-0017

记录 D0–D7：**显式推翻 ADR-0016 D4 的「严格二档」字面约束**（并划清边界——新增的是只读来源层而非可编辑版本，可编辑面未变宽）、草稿池只读来源层 + 指针派生模型、C2 侧 / 检索侧 SSOT 分层、A/B 合并路线开发期离线对照 + 生产冻结单版。

## 3. 本地验证结果 (Verification)

```
$ python -m pytest tests/test_compose_publish.py -q
....................                                                     [100%]
20 passed in 5.93s
```

现有 golden-snapshot（`test_monolithic_render_loses_no_headline_rule_text` / `test_render_c2_prompt_backward_compatible_without_placeholder`）全绿——新增 prompt 段不破坏 headline 契约注入，且新占位符未影响向后兼容断言。

## 4. 潜在影响或技术债 (Technical Debt & Caveats)

- **占位符渲染的临时缺口**：10.1 仅在模板加入 `{{persona_perspective}}` 占位符，`render_c2_prompt` 的对应 `replace` 由 10.2 补上。在 10.1 合并到 10.2 合并之间，若跑真实 publish，模板会残留字面占位符文本。因 10.2 紧随其后且此窗口无生产运行，可接受；10.2 落地即闭合。
- **蒸馏质量是 10.7 GATE 核心验收点**：12 份视角的「可辨识性」须人读逐份确认；若同质，扇出 N 版即失去意义（风险已记入 plan「风险与约束」）。
- **禁注入原始 card 是硬纪律**：C2 加载路径（10.2 的 `load_persona_perspective`）必须只认 `c2_perspective.md`，永不读 `persona_card.md`。