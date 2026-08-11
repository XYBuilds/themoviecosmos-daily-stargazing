# 复用 3D 宇宙的文本向量,而非按 PRD §3 自建索引

**Status**: accepted

## 决策

MVP 不自己 encode 索引,而是**直接复用** 3D 宇宙项目(`chronicle_v3_3d_galaxy`)产出的两份产物作为检索基建:

- `data/output/cleaned.csv`(策展片单；行数随 Chronicle release 变化，不以冻结常数为权威)
- `data/output/text_embeddings.npy`(`(N, 384)`,float32,行级 L2 归一化,与 cleaned.csv 行序一一对齐)

两者用同一模型 `paraphrase-multilingual-MiniLM-L12-v2` 生成,只用 `tagline + overview`、不拼 genres/language、不翻译,正是 PRD §2 想要的"纯文本搜索库"。`build_index.py` 的从 CSV 重算逻辑降级为 Post-MVP 备用。

## 为什么(关键约束)

1. **深链硬约束**:引流的全部价值是点进 `themoviecosmos.com/movie/{id}` 落地。站点只收录当前 Chronicle Galaxy Roster。**每个发布/检索到的 Daily 电影 id 必须属于当次所选 Chronicle 片单**——片单外的电影 = 死链。Daily 索引可以是 Chronicle 片单的子集；不以冻结行数或精确相等闸门为权威。这条直接排除了"用 119 万行 Kaggle 原始表重算"。
2. **零成本对齐**:复用产物天然与线上 id 集合同源,且省掉全量 encode；发布时再以 manifest 所选 galaxy 产物做成员资格校验。

## 后果 / 已知局限

- **查询模板必须对齐**:索引侧电影按 `Tagline: {tagline}\nOverview: {overview}`(无 tagline 时 `Overview: {overview}`)编码。`retrieve.py` 必须把每段 pseudo-overview 套成 `Overview: {pseudo}` 再 encode,否则查询与索引不同分布、余弦相似度系统性退化。PRD §3.2 的裸拼接公式作废。
- **片单受票数门槛过滤**:cleaned.csv 经过"按发行年份动态 vote_count 阈值"清洗,**冷门佳片即使共振更妙也不在片单内,本系统够不到**。这是 3D 宇宙策展策略的继承,非本项目可改。
- 若未来要追求 PRD 原始的"无前缀、无 title 回填"口径,需在本项目侧用 cleaned.csv 自行重 encode(模型不变),并重跑全部评分。
