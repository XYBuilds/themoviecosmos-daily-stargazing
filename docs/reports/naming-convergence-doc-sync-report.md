# 命名收敛重构 #6（文档产物名同步 · SSOT / CONTEXT）交付报告

## 1. 改动范围 (Scope)

本轮为纯文档收敛，把两份现状文档里描述**当前代码实际产物**的旧产物名对齐到已落地 `main`（merge commit `1747a7a`）的规范名。零代码改动。

**三条产物名映射（旧 → 新）：**
- `reality-deconstructed.json` / `.md` → `facts.json` / `.md`（extract 解构产物）
- `reality-expanded.json` → `bridges.json`（expand / P-Expand 客观扩展产物）
- `retrieve.json` → `candidates.json`（retrieve 召回候选池产物）

**改动文件与处数（共 10 处，+10/-10）：**
- `docs/SSOT/news-to-film-pipeline.md`（8 处）：
  - §0.1 阶段总表 extract 行：`当前实际：reality-deconstructed.json` → `facts.json`，产出列 `reality-deconstructed.json / .md` → `facts.json / .md`（同行 2 处）
  - §0.1 阶段总表 expand 行：`当前实际：reality-expanded.json` → `bridges.json`
  - §0.1 阶段总表 retrieve 行：`当前实际：retrieve.json` → `candidates.json`
  - §2.1 element：来源 `reality-deconstructed.json` → `facts.json`
  - §3.3 extract 层产物块：`reality-deconstructed.json` / `.md` → `facts.json` / `.md`
  - §3.3 落地物偏差注：`当前实际：reality-deconstructed.json` → `facts.json`
  - §11 推荐最小产物集合：`reality-deconstructed.json` → `facts.json`
- `CONTEXT.md`（2 处）：
  - 现实解构 agent 段：产出 `reality-deconstructed.json` → `facts.json`，hypernym 梯 `reality-expanded.json` → `bridges.json`（同句 2 处）
  - pseudo命中分段：`retrieve.json` 的 `hit_sources` → `candidates.json`

无新增 / 删除依赖。

## 2. 技术实现 (Implementation)

**判定「改 / 不改」的边界**：只对描述**当前代码实际产物**（落地态、读写真实文件名）的串做对齐；历史记录、目标态/未实现标注、阶段名/脚本名、已废弃约束一律保持。

**保持未改的点（有意保留）：**
- **SSOT §12「不建议再保留的旧约束」** 中「独立 reality-expanded / hypernym 层」：这是被废弃的旧约束概念描述，不是当前产物引用，保留原样。
- **queries.json / search-units 目标态**：SSOT §0.1 rewrite 行 `queries.json（当前实际：search-units.json / personas/*）` 未动 —— Stage 4 物化暂缓未落地，保持其目标态/未实现标注。
- **intake 未实现标注**：§0.1 intake 行 `news.json（当前实际：未实现）` 保持。
- **orchestrate 未实现标注**：§0.1 orchestrate 行 `Daily_Briefing/YYYY-MM-DD.md（当前实际：未实现）` 保持。
- **阶段名 / 脚本名**：`retrieve` 阶段名、`retrieve.py` 脚本名未触碰，只改指向产物文件名的 `retrieve.json`。
- **历史存档**：`docs/reports/`、`output/Eval/**`、`docs/adr/`（含 0011 及更早）、`.cursor/plans/` 一律未动，保持历史真实（dead link 可接受，项目既定约定）。
- 未顺手重写任何句子或调整结构，最小化只做产物名字符串对齐。

## 3. 本地验证结果 (Verification)

- **纯文档零代码改动**，无需跑测试，无 regression 风险。
- **改后复跑 Grep 确认**：对两文档以 `reality-deconstructed|reality-expanded|retrieve\.json` 复查：
  - `CONTEXT.md`：0 命中（已全部对齐）。
  - `docs/SSOT/news-to-film-pipeline.md`：仅剩 1 处（§12 L1134「独立 reality-expanded / hypernym 层」），为有意保留的废弃约束概念，非当前产物引用。
  - 结论：两文档内已无残留的、指向当前实际产物的旧名。

## 4. 潜在影响或技术债 (Technical Debt & Caveats)

- **历史存档按约定未回改**：`docs/reports/`（本轮新报告除外）、`docs/adr/`、`.cursor/plans/`、`output/Eval/**` 中的旧产物名保留不动，保持历史可复现性，dead link 可接受。
- **queries.json 仍为目标态**：Stage 4（`queries.json` / `search-units` 物化）尚未落地，文档保持其目标态/未实现标注，未改成已实现口吻。
- **后续项不在本轮**：Stage 4 物化、`main.py` 主链组装、Phase 4.3 等后续工作不在本轮范围。
- **SSOT §12 废弃约束串**：保留「reality-expanded」字样是有意为之（描述被废弃的旧约束），非疏漏。