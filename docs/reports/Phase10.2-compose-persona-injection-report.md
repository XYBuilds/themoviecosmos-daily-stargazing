# Phase 10.2 - compose 侧 persona 视角注入 交付报告

## 1. 改动范围 (Scope)

- **修改** `scripts/compose.py`：
  - 新增常量 `_C2_PERSPECTIVE_FILENAME = "c2_perspective.md"`
  - 新增 `load_persona_perspective(persona_id, prompts_dir=None)`
  - `render_c2_prompt` 加可选参数 `persona_perspective: str = ""` + `{{persona_perspective}}` 占位符 replace
  - `run_publish` 加可选参数 `persona_perspective: str = ""`，透传给 `render_c2_prompt`
- **修改** `tests/test_compose_publish.py`：新增 `PersonaPerspectiveInjectionTests`（7 例）
- 依赖包：无新增

## 2. 技术实现 (Implementation)

### 2.1 load_persona_perspective 归一化（D1）

```
persona_id = "THE-SAGE"
    │  "-".join(part.capitalize() for part in id.split("-"))
    ▼
normalized = "The-Sage"                       # title-case per hyphen 段
    │  prompts_dir/personas/The-Sage/c2_perspective.md（优先）
    │  → repo_root()/prompts/personas/The-Sage/c2_perspective.md（回退）
    ▼
读取 .strip() 后的中文视角文本；缺文件 → FileNotFoundError（清晰报错）
```

**只认 c2_perspective.md**：查找两处都是 `c2_perspective.md`，**永不回退读 `persona_card.md`**——这是防检索侧行话泄漏进 C2 中文创作的架构防线（ADR-0017 D1）。测试 `test_load_persona_perspective_never_falls_back_to_card` 用只放 `persona_card.md` 的伪 persona 目录证明其必然报错。

### 2.2 no-op 占位符注入（D2）

`render_c2_prompt` 新增的 `persona_perspective` 参数完全复刻既有 `headline_contract` 模式：

```
rendered = rendered.replace("{{persona_perspective}}", persona_perspective or "")
```

- 模板无占位符 → `replace` 为 no-op
- 传空串 → 占位符被替换为空，其余字节不动
- `run_publish(persona_perspective="")`（默认值）= 现有行为，首发 publish / 9.8 重生成路径零回归

### 2.3 参数流

```
run_publish(candidate, news, persona_perspective="...")
    │  透传
    ▼
render_c2_prompt(template, news_ctx, movie, judge, headline_contract, persona_perspective)
    │  replace {{persona_perspective}}
    ▼
prompt → LLM
```

上游 adapter（10.3）负责调 `load_persona_perspective(persona)` 得到文本再传入 `run_publish`；compose 层不感知 persona 目录扇出逻辑，只接收已蒸馏文本。

## 3. 本地验证结果 (Verification)

```
$ python -m pytest tests/test_compose_publish.py -q
............................                                             [100%]
28 passed in 6.23s

$ python -m pytest tests/test_compose_publish.py tests/test_review_panel_publish_adapter.py tests/test_review_panel_regenerate_adapter.py -q
（exit code 0，全绿）
```

关键断言：
- `test_empty_persona_perspective_is_byte_identical_noop`：真实模板下 `persona_perspective=""` 与不传参**逐字节等价**
- `test_run_publish_empty_perspective_matches_default`：`run_publish` 默认与显式空串渲染 prompt 一致
- `test_load_persona_perspective_normalizes_uppercase_hyphen`：`THE-SAGE` 与 `The-Sage` 加载结果相等
- `test_load_persona_perspective_reads_distilled_file`：读到中文视角、断言无 decon/P-Select/objective-floor/focalized/alt-creator 行话

## 4. 潜在影响或技术债 (Technical Debt & Caveats)

- **闭合 10.1 的临时缺口**：10.1 已在模板植入 `{{persona_perspective}}` 占位符，本 TODO 补上 `render_c2_prompt` 的 replace 逻辑，占位符不再会残留进真实 prompt。
- **compose 层与目录扇出解耦**：`load_persona_perspective` 只做「persona_id → 文本」映射，不知道 `triggered_by` 全集；全量扇出编排是 10.3 drafts_adapter 的职责。
- **归一化仅覆盖 hyphen 分段 title-case**：若未来出现非 `THE-X-Y` 形态的 persona_id（如带下划线），需扩展归一化规则；当前 12 persona 全为 `The-X` / `The-X-Y` 形态，无风险。