---
name: Phase11-deterministic-movie-header-projection
overview: |
  把「电影信息抬头行」从 LLM 手里彻底收回，改为代码确定性投影——根治现状里
  草稿正文片名忽用英文 title、忽用西语 original_title 的不一致（根因：抬头行由
  LLM 在 compose_publish prompt 里自由生成，prompt 只说「片名」从未指定用哪个字段）。
  架构主张：抬头行 = 确定性数据投影（代码 f-string 拼装），正文 = persona 创作（LLM）；
  完全类比现有「movie_url 由代码追加、prompt 禁 LLM 自吐链接」的既有先例。
  本 Phase 仅做 **TODO-A：零外部依赖的确定性骨架**——抬头 7 项里 6 项全走 DB
  （original_title/title/release_date/genres/original_language + by-id 补 director/
  vote_average/runtime），静态映射表（类型 EN→中、ISO639-1 语言码→中文语言名）纯代码零联网。
  唯一需要外部 TMDB 在线的「中文片名译名」作为**可插拔增强插槽**留待后续 TODO-B（独立 Phase）：
  本 Phase 恒缺中文段 → 按已定 drop_cn_seg 规则退化。冻结格式模板见 D0。仅 xiaohongshu。
todos:
  - id: p11.1-static-maps-and-adr
    content: 11.1 · [asset] 静态映射表（genres EN→中 + ISO639-1 语言码→中文语言名，纯代码零联网）+ 抬头行格式契约 prompts/_shared/xiaohongshu_movie_header_contract.md + 写 ADR-0018（确定性抬头投影：从 LLM 收回抬头行、类比 movie_url 由代码追加；中文译名作可插拔增强层留 TODO-B）
    status: complete
  - id: p11.2-render-header-pure-fn
    content: 11.2 · [compose] render_movie_header(proj) 纯函数（零 IO 可单测）：三段片名 + original_language!=en 去重规则 + release_date 拆 [Y/M/D] + 文明码.upper()+语言名 + 类型映射 + 光度/体积 + 中文片名缺失→drop_cn_seg 退化
    status: complete
  - id: p11.3-build-projection-byid
    content: 11.3 · [compose] build_header_projection(candidate)：retrieve candidate + get_movie_detail_by_tmdb_id 补 director/vote_average/runtime（ADR-0012 通路B）+ 静态映射；取数与渲染解耦、可注入 stub；cleaned.csv 缺失清晰降级
    status: complete
  - id: p11.4-wire-into-publish
    content: 11.4 · [compose+prompt] 抬头由代码追加进 run_publish 产物（类比 movie_url）+ 改 compose_publish_xiaohongshu.md 归属行段（禁 LLM 生成片名/抬头行）+ clean_publish_body 兜底剥除 LLM 误吐抬头
    status: complete
  - id: p11.5-adapter-fanout-header
    content: 11.5 · [adapter] drafts_adapter 全量扇出每份草稿装配确定性抬头 + publish_adapter 同步；复用既有 locate/load/find；golden-snapshot 证既有链路无回归
    status: todo
  - id: p11.6-tests
    content: 11.6 · [测试] render_movie_header 各分支（英语片去重/非英语三段/缺中文退化/缺 director/映射命中与 fallback/release_date 异常）+ build_header_projection stub 注入 + 集成 drafts/publish 抬头装配
    status: todo
  - id: p11.7-gate
    content: 11.7 · [GATE] 真实重跑扇出对比新旧抬头 + 人工验收渲染格式（对齐冻结模板）+ 确认 title/original 混用病根消除 + 文档同步 [需人工验收]
    status: todo
isProject: true
---

# Phase 11 · 确定性电影抬头行投影（从 LLM 收回抬头，代码纯拼装）

## 前置条件

| Phase | 状态 | 判定依据 |
| --- | --- | --- |
| 10（10.1–10.7 全子计划） | complete 且已并入 `main` | `git log --oneline -15` 见 PR #135 合并（`d5e563c`）、p10.7 收尾 `c788a74`/`82aaadc` 在 main；`git status -sb` = `## main...origin/main`（工作区干净，无未合并 `feat/phase10*`） |
| 当前分支 | 从最新 `main` 检出 | 规则2：前置已并入 main → 从 main 检出，无 stacked 继承 |

> 说明：本 Phase 的关注点（抬头行确定性投影）与 Phase10（persona 视角草稿池）正交，但**产物同链路**（都改 `run_publish` / `drafts_adapter`），故必须在 Phase10 合并后开工，从最新 main 检出。

## 背景

现状：草稿池 JSON 与 C2 定稿的**抬头行由 LLM 自由生成**，不是代码拼的。`prompts/compose_publish_xiaohongshu.md`「归属行」段只规定「`「片名」(YYYY) 导演名`」并只给英文例子，**从未指定该用 `title` 还是 `original_title`**；而传给 LLM 的候选投影块两个字段都在，LLM 每次随机挑一个 →

```
同一部片 tmdb=xxx 在不同 persona 草稿里：
    The-Innocent → 「I Dream in Another Language」   (英文 title)
    The-Everyman → 「Sueño en otro idioma」          (西语 original_title)
    ……                                              ← 不一致的直接根因
```

**既有先例**：电影链接 `https://themoviecosmos.com/movie/{id}` 现在就是**代码 f-string 拼**的（`review_panel/publish_adapter.py` / `scripts/compose.py`），且 prompt 明确「不要让 LLM 自己吐链接，由下游程序处理」。抬头行本质同类——确定性数据投影，不该让 LLM 碰。

**目标数据流演变**：

```
现状（一次 LLM 生成，抬头+正文混在一起）:
    candidate 投影(含 title+original_title) ──▶ LLM 又填表又创作 ──▶ 抬头不稳定

目标（职责分离）:
    candidate ──▶ build_header_projection ──┐
                  (+ by-id 补 director/       ├──▶ render_movie_header(纯代码) ──┐
                     vote_average/runtime)     │                                  ├──▶ 成品
    news/judge/persona ──▶ LLM 只写正文 ───────┘   (prompt 禁 LLM 碰片名/抬头/链接) ─┘
```

## 设计决策

### D0 · 冻结格式模板（Round1–5 需求讨论逐版收敛，最终拍板）

以本片（tmdb `I Dream in Another Language` / `Sueño en otro idioma`）真实数据渲染为唯一目标：

```
「梦呓雨林」/ Sueño en otro idioma / I Dream in Another Language
Ernesto Contreras

坐标：[Y: 2017, M: 07, D: 28]
文明：ES 西班牙语
类型：奇幻，剧情
光度：7.9
体积：142
```

**两块分组**（Round3 定）：上半 = **身份**（片名 + 导演，作者归属贴一起）；下半 = **星轨读数**（坐标/文明/类型/光度/体积），中间一处空行分隔。

| 行 | 内容 | 数据源 | 规则 |
| --- | --- | --- | --- |
| 片名 | `「中译」/ original_title / title` | 中译=TMDB在线(TODO-B，本 Phase 恒缺)；后两者=DB | 三段斜杠分隔；见 D1 去重与退化 |
| 导演 | `Ernesto Contreras` | DB `director`（by-id 补） | **仅原名**，不做中译（Round5 定 original_only） |
| 坐标 | `[Y: 2017, M: 07, D: 28]` | DB `release_date` 拆解 | 天文坐标味（Round4 定）；`YYYY-MM-DD` split |
| 文明 | `ES 西班牙语` | DB `original_language` | `码.upper()` + 静态语言名；语种轴非产地（Round5 定） |
| 类型 | `奇幻，中文用「，」分隔` | DB `genres` + 静态 EN→中表 | 不联网；表外类型退化保留英文 |
| 光度 | `7.9` | DB `vote_average`（by-id 补） | 术语沿用 |
| 体积 | `142` | DB `runtime`（by-id 补） | 术语沿用 |

### D1 · 片名三段 + original_language 去重 + 中文缺失退化

- **三段**：`「中译」/ {original_title} / {title}`。
- **英语片去重**：`original_language == "en"` 时 original_title==title 会重复 → 退化两段 `「中译」/ {title}`。
- **中文片名缺失（本 Phase 恒发生，TODO-B 未做）→ `drop_cn_seg`**（Round5 定）：丢中文段，只 `{original_title} / {title}`（英语片再去重为单个 `{title}`）。
- 中译位设计成**可插拔插槽**：`proj["zh_title"]` 为空即触发 drop_cn_seg；TODO-B 填上该字段后中文段自动亮起，render 函数无需改。

### D2 · render_movie_header = 纯函数（零 IO，最大化可测）

- `render_movie_header(proj: dict) -> str`：只吃一个已就绪的投影 dict，出多行字符串。**不读文件、不查库、不调 LLM** → 每个分支纯单测覆盖（D1 的去重/退化、release_date 异常、映射 fallback）。
- 静态映射表（genres EN→中、ISO639-1→中文语言名）作模块级常量注入，render 内只查表。

### D3 · build_header_projection = 取数装配（与 render 解耦）

- `build_header_projection(candidate, movie_detail_loader=...) -> dict`：合并 retrieve candidate（有 title/original_title/genres/release_date/original_language）+ `get_movie_detail_by_tmdb_id`（ADR-0012 通路B，补 director/vote_average/runtime）→ 拼成 render 所需 proj。
- **取数可注入**：`movie_detail_loader` 默认 `get_movie_detail_by_tmdb_id`，测试传 stub 免读 `cleaned.csv`（该文件 gitignore、CI/他机可能无）。
- `cleaned.csv` 缺失或某片查不到 → director/光度/体积清晰降级（该行省略或标注），不抛崩溃。

### D4 · 抬头由代码追加进产物（prompt 禁 LLM 生成）· 类比 movie_url

- 抬头行**不进 LLM prompt 生成范围**：`run_publish` 产出正文后，由代码把 `render_movie_header(proj)` 拼在正文首（与现有 `movie_url` 追加同一模式）。
- 改 `prompts/compose_publish_xiaohongshu.md` 归属行段：从「LLM 写 `「片名」(YYYY) 导演名`」改为「**不要输出任何片名行/抬头/元信息行**（片名、年份、导演、类型、评分、时长），这些由下游程序拼装」——与既有「不要自吐链接」并列。
- `clean_publish_body` 加兜底：剥除 LLM 若仍误吐的抬头样式行（复用既有裸链接剥除的清洗惯例）。

### D5 · ADR-0018

新开 `docs/adr/0018-deterministic-movie-header-projection.md`，记录：抬头行从 LLM 收回为代码确定性投影的理由（title/original 混用根因）、类比 ADR-0012 通路B 与 movie_url 代码追加先例、冻结格式模板（D0）、三段+去重+drop_cn_seg 退化（D1）、render/projection 解耦（D2/D3）、中文译名作独立增强层留 TODO-B（明确本 Phase 不引入 TMDB 在线依赖、守住「纯本地库」不变）。引用 ADR-0012 / 0013 / 0015 / 0017。

---

## Todo 11.1 · [asset] 静态映射表 + 抬头格式契约 + ADR-0018

**依赖：** 无（可先做）

**改动：**
- `scripts/`（或 `scripts/lib/`）新增静态映射常量：`GENRE_EN_TO_ZH`（TMDB ~19 类型）、`LANG_CODE_TO_ZH`（ISO639-1→中文语言名，至少覆盖库内出现语种）。表外键 fallback：类型保留英文、语言名只显大写码。
- `prompts/_shared/xiaohongshu_movie_header_contract.md`：[新] 用文字固化 D0 冻结模板与字段规则（作契约文档，非注入 LLM 的生成指令）。
- `docs/adr/0018-deterministic-movie-header-projection.md`：[新] 记录 D0–D5。

### 验收
- [ ] 两张映射表齐全，键覆盖 subsample 样本出现的全部 genres/original_language
- [ ] 契约文档逐字段对齐 D0 冻结模板
- [ ] ADR-0018 落地并被本 plan 引用；明确「本 Phase 不引入 TMDB 在线依赖，中文译名留 TODO-B」

---

## Todo 11.2 · [compose] render_movie_header 纯函数

**依赖：** 11.1

**改动：**
- `scripts/compose.py`：新 `render_movie_header(proj: dict) -> str`——按 D0/D1 拼多行字符串：
  - 片名三段 + `original_language=="en"` 去重 + `zh_title` 空→drop_cn_seg 退化；
  - 导演仅原名（缺失省略该行）；
  - `坐标`：`release_date` split `YYYY-MM-DD`→`[Y: , M: , D: ]`（异常/缺失清晰退化）；
  - `文明`：`original_language.upper()` + `LANG_CODE_TO_ZH` 查表；
  - `类型`：`genres` 拆分 + `GENRE_EN_TO_ZH` 逐项映射，中文「，」join；
  - `光度`/`体积`：`vote_average`/`runtime` 直出（缺失省略）。
- 纯函数：不读文件、不查库、不调 LLM。

### 验收
- [ ] 非英语片（es）→ 三段（本 Phase zh_title 空 → 两段 `original / title`）
- [ ] 英语片（en）→ 去重后单个 title（zh 空时）
- [ ] release_date 为空/非法 → 坐标行清晰退化不崩
- [ ] genres/language 表外键 → 各自 fallback（英文/纯码）

---

## Todo 11.3 · [compose] build_header_projection（by-id 补字段，取数/渲染解耦）

**依赖：** 11.2

**改动：**
- `scripts/compose.py`：新 `build_header_projection(candidate, movie_detail_loader=get_movie_detail_by_tmdb_id) -> dict`：
  - 从 candidate 取 title/original_title/genres/release_date/original_language；
  - 经 loader 按 tmdb_id 补 director/vote_average/runtime（ADR-0012 通路B）；
  - `zh_title` 恒置空（TODO-B 插槽）；
  - 组装成 `render_movie_header` 所需 proj dict。
- loader 可注入；`cleaned.csv` 缺失 / 片查不到 → 缺字段降级（不崩）。

### 验收
- [ ] 注入 stub loader 时不读真实 `cleaned.csv` 即可产出完整 proj
- [ ] 真跑一条真实候选，proj 含 director/vote_average/runtime
- [ ] loader 抛错/查空 → proj 缺字段但可 render（对应行退化）

---

## Todo 11.4 · [compose+prompt] 抬头代码追加进 run_publish + prompt 禁 LLM 生成

**依赖：** 11.3

**改动：**
- `scripts/compose.py::run_publish`：正文生成后，代码把 `render_movie_header(build_header_projection(candidate))` 追加为正文首块（类比 movie_url 追加）。
- `prompts/compose_publish_xiaohongshu.md`：归属行段改为「禁止 LLM 输出任何片名/抬头/元信息行」（并列既有「禁自吐链接」）。
- `clean_publish_body`：加兜底剥除 LLM 误吐的抬头样式行。

### 验收
- [ ] run_publish 产物抬头行逐字节 == render_movie_header 输出（LLM 不再参与）
- [ ] prompt 不再引导 LLM 写片名行；golden-snapshot 更新并说明差异来源
- [ ] LLM 误吐抬头 → clean_publish_body 剥除

---

## Todo 11.5 · [adapter] drafts/publish 扇出装配确定性抬头

**依赖：** 11.4

**改动：**
- `review_panel/drafts_adapter.py`：全量扇出每份 persona 草稿装配同一确定性抬头（同片同抬头，仅正文因 persona 而异）。
- `review_panel/publish_adapter.py`：C2 定稿同步走同一抬头装配。
- 复用既有 `locate_news_dir/load_news/find_candidate/render_copy_markdown`。

### 验收
- [ ] 同一候选的 N 份 persona 草稿抬头**完全一致**（混用病根消除）
- [ ] publish 定稿抬头与草稿池一致
- [ ] 既有 publish/drafts 链路 golden-snapshot 无回归

---

## Todo 11.6 · [测试] 覆盖新链路

**依赖：** 11.5

**改动：**
- `tests/test_compose.py`：`render_movie_header` 各分支（英语去重/非英语/缺中文退化/缺 director/映射 fallback/release_date 异常）；`build_header_projection` stub 注入。
- `tests/test_review_panel_drafts_adapter.py` / `..._publish_adapter.py`：抬头装配集成、同片抬头一致、向后兼容无回归。

### 验收
- [ ] `pytest tests/test_compose.py tests/test_review_panel_drafts_adapter.py tests/test_review_panel_publish_adapter.py` 全绿
- [ ] 既有测试无回归

---

## Todo 11.7 · [GATE] 真实重跑 + 格式验收 + 文档同步 [需人工验收]

**依赖：** 11.1–11.6 全部

**执行顺序：**
1. 真实重跑扇出，导出新旧抬头对比（不写 report、不合并）。
2. 人工验收渲染格式对齐 D0 冻结模板、确认 title/original 混用消除。
3. 等待人工 Go/No-Go；No-Go 回对应 TODO 修正。
4. Go 后同步 SSOT/PRD 相关段并引用 ADR-0018。

**验收项：**
- [ ] 真实候选抬头逐行对齐 D0 冻结模板
- [ ] 同片跨 persona 抬头一致、无 title/original 混用
- [ ] 中文段按 drop_cn_seg 退化（TODO-B 未做，符合预期）
- [ ] Go 后文档同步、引用 ADR-0018
- [ ] `[需人工验收 · Go/No-Go]`

---

## 风险与约束

- **范围纪律**：本 Phase 只做**确定性骨架（TODO-A）**，**不引入 TMDB 在线依赖**、不动中文译名——守住项目「纯本地静态库」不变量。中文译名 = 独立 TODO-B（另起 Phase，含 TMDB key + `data/index/zh_titles_cache.json` 提交 git + 独立 ADR）。
- **正文质量不在本 Phase**：用户提的「正文生硬+过短」是 persona/compose prompt 的事，与抬头行两套逻辑，留独立轮次，勿混入。
- **取数解耦是可测性命门**：`cleaned.csv` gitignore，render 必须纯函数、projection 的 loader 必须可注入，否则 CI/他机跑不了单测。
- **向后兼容**：prompt 改动会变 golden-snapshot；须在 11.4 明确「差异来源 = 抬头行改由代码产出」，并保证首发 publish / Phase10 扇出路径逻辑不回归。
- **zh_title 插槽契约**：render 依赖 `proj["zh_title"]` 空↔非空切换中文段；TODO-B 落地时只填字段、不改 render——此契约须在 ADR-0018 写死，避免 TODO-B 重构 render。
- **同片同抬头**：抬头是候选的确定性投影，与 persona 无关；N 份草稿共享同一抬头，仅正文因视角而异。