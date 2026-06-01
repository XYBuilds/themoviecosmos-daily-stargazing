# Phase 3.5.2 - 现实解构 agent 交付报告

## 1. 改动范围 (Scope)

- **新增** `prompts/A0_reality_deconstructor.md` — A0 身份、铁律、印度热浪 few-shot、新闻占位符注入
- **新增** `scripts/deconstruct.py` — CLI、MiMo/DeepSeek 调用、JSON 抽取与归一化、契约校验、双写产物
- **更新** `.cursor/plans/Phase3.5-pivot-reality-deconstruction.plan.md` — todo `f35b1c2d-0001-4000-8035-000000000002` 标 complete
- **无** 新增 Python 依赖

## 2. 技术实现 (Implementation)

- **Prompt**：严格对齐 `docs/SSOT/reality-deconstruction-contract.md` §0–§1；附录 A 热浪样例作 few-shot；禁止 skeleton/load_bearing/共振等字段。
- **管线**：`load_news_from_file` → 渲染 `{{title}}` 等占位符 → `get_llm_client`（默认 `mimo` / MiMo 2.5 Pro）→ 从回复抽取 JSON（支持 ```json 围栏）→ `normalize_deconstructed`（标量 list 化）→ `validate_deconstructed` → 写入目录。
- **产物**（`--out-dir`）：
  - `reality-deconstructed.json` — 契约本体
  - `reality-deconstructed.md` — Anchor/When/Where/Who/Why/How/Result 分段，总编可扫
  - `deconstruct-errors.json` — 仅在有校验/解析错误时写入
- **MVP 宽松**：解析或 schema 问题记入 `errors` 并打 stderr warning，**CLI 仍 exit 0**（与「不阻断」一致）。

## 3. 本地验证结果 (Verification)

```powershell
python scripts/deconstruct.py --news-file tests/eval_news/01-grid-outage.json --out-dir output/deconstruct-verify/01-grid-outage --provider mimo
python scripts/deconstruct.py --news-file tests/eval_news/05-climate-disaster.json --out-dir output/deconstruct-verify/05-climate-disaster --provider mimo
python scripts/deconstruct.py --news-file tests/eval_news/08-sports-underdog.json --out-dir output/deconstruct-verify/08-sports-underdog --provider mimo
```

| 样本 | 结果 | 备注 |
|------|------|------|
| `01-grid-outage` | JSON + MD，无 errors | Visayas 电网：专名、950 MW、230-kV 保留；`scene_archetype`/`role` 为 list |
| `05-climate-disaster` | JSON + MD，无 errors | 幼发拉底洪灾：Deir Ezzor/Raqqa 分条 where；无 forbidden 键 |
| `08-sports-underdog` | JSON + MD，无 errors | NHL 横扫：时序 how 带 step；未出现「underdog/favorite」等叙事框定 |

三条均无 `skeleton` / `load_bearing` / `resonance`；多值字段均为数组。肉眼扫 MD：无权力定性、无反讽/戏剧 beat 标签。

## 4. 潜在影响或技术债 (Technical Debt & Caveats)

- **3.5.3** 须改 `agents.py` / A1–A7 prompt：输入从原始新闻改为 `reality-deconstructed.json` 全量注入。
- **`run_eval.py`** 尚未串联 deconstruct；评测仍走旧管线，待 3.5.3+ 集成。
- **role_in_event 用语**：模型偶用英文 `cause`/`decision-making` 而非契约示例中文「发起·决策」——客观但可后续在 prompt 中收紧枚举。
- **验证产物** `output/deconstruct-verify/` 为本地试跑目录，未纳入提交。
