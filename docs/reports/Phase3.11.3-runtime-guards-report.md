# Phase 3.11.3 - 运行时守卫 交付报告

## 1. 改动范围 (Scope)

- `scripts/personas.py` — ADR-0008 运行时守卫模块与接线
- `tests/test_personas.py` — `PersonaAdr8RuntimeGuardTests`（8 项守卫单测）
- `.cursor/plans/Phase3.11-pov-focalization-additive.plan.md` — `p311-3` 标 complete

无新增依赖。

## 2. 技术实现 (Implementation)

- **`validate_adr8_runtime_guards`**：统一入口，校验 center ∈ decon ids、支撑 fragments 2–4、focal ∈ `who-*`、事实守卫、hypernym 锚、双地板。
- **`validate_adr8_fact_guard`**：拒绝内心戏/内省措辞、虚构因果、novel event/outcome、未蕴含专有名词。
- **`collect_entailed_vocabulary`**：从 decon + alt-pool + expansion 构建事实词表。
- **接线**：`parse_adr8_pseudos_response`（解析期，含 fact/dual-floor）、`assemble_adr8_channel_pseudos`（装配期含 hypernym）；`run_screenwriter` 传入 decon/overlay；`run_persona_pipeline` 既有单次 repair retry 在守卫硬失败时携错误重问。

## 3. 本地验证结果 (Verification)

```text
python -m unittest tests.test_personas -v
Ran 62 tests in ~19s — OK
```

守卫相关：`PersonaAdr8RuntimeGuardTests` 8/8；`PersonaAdr8CompositionTests` 12/12；`PersonaRepairTests` 3/3（含 parse/assembly retry）。

## 4. 潜在影响或技术债 (Technical Debt & Caveats)

- 事实守卫为启发式（regex + 词表），pilot 审计（3.11.6）可能需收紧/放宽模式。
- 解析期未传 decon 时仅做结构 + 双地板校验（向后兼容）；完整守卫在 ADR-0008 管线中始终启用。
