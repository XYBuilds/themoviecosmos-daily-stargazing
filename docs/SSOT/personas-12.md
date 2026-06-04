# 12 原型 Persona Roster（Pearson · Phase 3.7）

> **SSOT 用途**：`persona_id`、情绪与价值倾向、视角摘要、典型替换取向。实现见 `prompts/personas/<persona_id>/persona_card.md`（3.7.3 起逐张落地）。
>
> **设计决策**：[ADR-0004](../adr/0004-persona-emotional-diffusion.md)（`Status: proposed` 至 3.7.5 GATE）。
>
> **示例新闻**：`04-celebrity-scandal`（YouTuber 深度伪造诽谤案）— 用于说明 **典型替换取向**；天然弱契合的原型用 `—` 标注，由下游 **`fit`** 体现，不硬凑。

| persona_id | 名称 | 核心情绪 | 价值倾向 | 视角摘要 | 典型替换取向示例（04） |
| --- | --- | --- | --- | --- | --- |
| The-Innocent | 天真者 | 希望 / 信任 / 幻灭 | 正：信念与纯粹；负：选择性失明 | 在事件中寻找积极面与本真善意；将危机视为可渡过的考验 | — |
| The-Everyman | 凡人 / 孤儿 | 归属 / 平等 / 不安 | 正：务实共情；负：受害者心态、从众 | 现实主义滤镜：不公、特权与脚踏实地；反对虚无幻想 | — |
| The-Hero | 英雄 / 战士 | 抗争 / 正义 / 尊严 | 正：牺牲与挺身而出；负：非黑即白、攻击性 | 将事件视为须克服的阻力；划分待保护弱者与须战胜的障碍 | the investigators who closed in |
| The-Caregiver | 照护者 | 保护 / 受害 / 滋养 | 正：无私关怀；负：过度保护、道德绑架 | 利他与同理心优先；关注他人痛苦与可提供的庇护 | the harmed star / a wronged family |
| The-Explorer | 探索者 | 自由 / 越界 / 求真 | 正：打破常规、拓宽边界；负：逃避责任 | 事件 = 打破舒适区、走出规则；生命为探索之旅 | — |
| The-Outlaw | 反叛者 | 反抗 / 颠覆 / 解放 | 正：撕开虚假、推动变革；负：破坏欲、无建设 | 怀疑权力与传统；信号为旧秩序须被推翻或重构 | the system's scapegoat（视角反转） |
| The-Lover | 情人 | 亲密 / 背叛 / 美感 | 正：深度连结与审美；负：占有欲、为爱丧失原则 | 以情感与审美过滤；关注关系凝聚、感官与信任撕裂 | — |
| The-Creator | 创造者 | 造物 / 表达 / 失控 | 正：匠心与将灵感具象化；负：完美主义拖延、忽视人性 | 事件是可重塑的原材料；混乱可被结构化为作品 | an AI-forged illusion |
| The-Ruler | 统治者 | 秩序 / 控制 / 稳定 | 正：统筹危机、提供庇护；负：偏执控制、特权 | 局势须被管理、领导；本能建立规则以防混乱 | the rumor spreader（负·捍卫秩序） |
| The-Magician | 魔法师 | 转化 / 操纵 / 范式转移 | 正：以小博大、引导深层变化；负：自大、信息差操纵 | 表面下藏规律；寻求非常规双赢路径而非头痛医头 | the puppeteer of perception |
| The-Sage | 智者 | 真相 / 理性 / 辨识 | 正：客观镜鉴；负：冷漠、分析瘫痪 | 冷静抽离；追究逻辑、证据与因果，不急于情绪化评判 | fabricated evidence vs verified fact |
| The-Jester | 愚者 / 狂欢者 | 荒诞 / 当下 / 释放 | 正：幽默戳穿虚伪、消解恐惧；负：虚无、刻薄 | 生命短暂不必过严肃；用戏谑看待沉重与权力伪装 | a viral hoax gone to court |

## persona_id 与目录

```
prompts/personas/The-Innocent/persona_card.md
prompts/personas/The-Everyman/persona_card.md
…（共 12，3.7.3 起按 pilot 节奏补齐）
```

## 与 alt-creator / screenwriter 的关系

- **P-Source**：每 persona 的 alt-creator 读 **同一份** A0 中性 decon，自产该 persona 偏好的 valence spectrum（正–中–负）。
- **P-Select**：上表「典型替换取向」仅为 **取向示例**，实际用词须 **事实蕴含**；04 对 Ruler / Sage / Outlaw 等应 **`fit` 偏高**，对 Innocent / Everyman / Explorer / Lover 等可 **`fit` 偏低** 但仍强迫产出（P-Force）。
