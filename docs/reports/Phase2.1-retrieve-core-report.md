# Phase 2.1 - 召回核心 交付报告

## 1. 改动范围 (Scope)

- `scripts/retrieve.py` — 索引加载、`SentenceTransformer` 查询编码、余弦 Top-K
- 无新增 pip 依赖

## 2. 技术实现 (Implementation)

- 经 `scripts.lib.paths` 加载 `embeddings.npy`（59341×384）与 `meta.parquet`，校验行对齐
- 查询模板 `Overview: {pseudo}`（ADR-0001），`normalize_embeddings=True`
- `scores = query @ embeddings.T`，`np.argpartition` 取 Top-2，再按分数降序
- 单条调试：`retrieve_top_k()` / CLI `--pseudo` + `--agent-id`

## 3. 本地验证结果 (Verification)

```powershell
python scripts/retrieve.py --pseudo "A prophet of technology proclaims..." --agent-id A2
```

- exit 0；2 hits；similarity 0.5346 / 0.5558（∈ [-1, 1]）
- 样例片名：Alien Code、Pulse 3

## 4. 潜在影响或技术债 (Technical Debt & Caveats)

- 首次运行需下载 MiniLM 权重（约数分钟）
- 未对 `embeddings.npy` 做 reorder / re-normalize
