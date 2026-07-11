# Phase 12.1 - 落地现有结构层基线 交付报告

## 1. 改动范围 (Scope)
- 改动的文件列表（三个文件已由 commit `e9f91cf`（`feat(adapter): add neutral default draft for fanout process and update tests to reflect changes`）直接提交进 `main`，本次收尾不再改动代码）：
  - `prompts/compose_publish_xiaohongshu.md`
  - `review_panel/drafts_adapter.py`
  - `tests/test_review_panel_drafts_adapter.py`
  - （同一 commit 还捎带了 `.cursor/plans/Phase12-c2-body-quality-gate.plan.md` 与 `docs/adr/0019-c2-body-quality-gate.md`，属于该 commit 的既有基线内容，非本次收尾新增）
- 新增/删除的依赖包：无

## 2. 技术实现 (Implementation)

### prompts/compose_publish_xiaohongshu.md：结构层去 AI 腔规则
- **剧情简述硬约束升级**：只能复述 DB overview 里真正写到的内容，不得增补 overview 没写的场景/镜头/角色/角色名/道具/台词/结局/制作花絮/票房，即便"认得"这部电影也不许脑补。
- **篇幅约束调整**：取消旧的"克制简短、不要写成长评"限制，现阶段不设上限、不求精简，但强调放开的是篇幅不是素材，长度只能靠新闻侧真实细节和处境铺展撑起来。
- 新增「正文：结构与分段（打散骨架 · 快速扫读）」整节，核心规则：
  - **禁止四拍骨架**：不得每条都按「新闻概述 → 剧情概述 → 接受度一句 → 处境收尾」的固定顺序写，换连接词不算合规，要换的是骨架本身。
  - **交错开场、别默认从新闻起笔**：可从电影 overview 真有的情境、新闻一句话、二者共有处境切入，但从电影切入时只能用 overview 里真实存在的情境，不许为画面感发明不存在的镜头/道具/角色。
  - **接受度只能揉进从句，禁止单独成句/单独成段**：不能让"看过多少人、口碑如何"孤零零占一句或一段。
  - **关系靠并置，不许用一句话"说破"**：封死"两者共享/都触及/指向同一种……"类盖章句，尤其点名封死两个最顽固的句式模板（"都 [停在/悬在/落在/指向/压着] 同一个……"、"无论是……还是……背后是/都是同一种……"），换词不换招同样违规。
  - **结尾各条不同**：不许每条都把"关系句"摆在最后一段当论点，落点要分散（画面/动作/提问/余味）。
  - **分段下限硬约束**：至少 3 段起步，不许整篇正文挤成不换行的一坨；段内该连贯就连贯，不搞一句一行。
- 反例区新增「脑补 DB 没有的电影细节」头号红线举例，以及「固定四拍骨架 + 套话连接词」反例（取代旧的"固定三段式模板"反例）。

### review_panel/drafts_adapter.py：池首中性默认稿设计
- 新增模块级常量 `_DEFAULT_DRAFT_ID = "混合视角"`。
- `run_fanout` 内部改造为 `_run_one(persona_perspective, draft_id)` 辅助函数，统一封装"调用 run_publish → 拼装电影抬头 → 生成 draft entry"的逻辑。
- 草稿池组装顺序调整为：**先跑一条 `persona_perspective=""`（不注入任何 persona 主视角）的中性默认稿，draft_id 固定为 `"混合视角"`，排在池首（index 0）**；随后再按 `triggered_by` 去重后的顺序，逐 persona 各出一版加了原型视角滤镜的备选，跟在中性默认稿后面。
- 因为 review panel（`review_panel/index.html`）默认预览 `drafts[0]`，池首的中性默认稿即编辑打开面板时看到的默认预览稿。
- docstring 同步更新，说明池首中性默认稿 + per-persona 备选的扇出结构；"整份覆盖"注释也更新为"重新扇出 = 显式重掷池首中性默认 + 全部 persona"。

### tests/test_review_panel_drafts_adapter.py：配套测试调整
- 所有断言草稿池长度/顺序的既有测试同步 +1（新增的中性默认稿占位），并在 `draft_id` 序列开头补上 `"混合视角"`。
- 新增专项测试 `test_fanout_prepends_neutral_default_draft_at_index_0`：验证池首第 0 条固定是 `draft_id == "混合视角"` 且对应调用的 `persona_perspective == ""`，其余顺序仍是 `triggered_by` 去重后的 persona 序列。
- `CombineTests` 中原本 4/5 条的池长度断言相应调整为 5/6 条（中性默认稿(1) + persona 版本 + 合并稿），并补充注释说明每处数字的构成。

## 3. 本地验证结果 (Verification)

运行命令：

```powershell
python -m pytest tests/test_review_panel_drafts_adapter.py -q
```

输出：

```
..............                                                           [100%]
14 passed in 9.84s
```

14 项测试全部通过，无失败、无 regression。

## 4. 潜在影响或技术债 (Technical Debt & Caveats)
- **仅基线锁存，非达标判定**：本次落地的是 prompt 结构规则与池首中性默认稿的代码/规则基线，prompt 侧的去 AI 腔效果尚未经过眼验校准，真正的达标判定要等 12.5 GATE 跑完扫描/评审后才能确认，此报告与 status 标记不代表结构层已经"验收通过"，不可误判为已完成。
- **流程偏差记录**：12.1 的代码实质没有走独立分支 + PR 的标准六步流水线，而是在上一会话中直接以 commit `e9f91cf` 合入了 `main`（非常规操作）。本次 `feat/phase12.1-report` 分支及本报告是对这一偏差的补做收尾治理：只补齐「状态标记 + 交付报告」两步，代码本身不再重复改动或重新提交。
- **分支继承关系**：本收尾工作在 `feat/phase12.1-report` 分支进行，该分支从最新 `main`（已包含 `e9f91cf`）检出。