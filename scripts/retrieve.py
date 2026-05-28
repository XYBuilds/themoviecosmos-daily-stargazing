"""retrieve.py · 跨类型纯文本召回.

输入: 各 Agent 的 pseudo-overview 文本.
索引: data/index/embeddings.npy + data/index/meta.parquet.
模型: paraphrase-multilingual-MiniLM-L12-v2 (与 build_index 严格同模型).

输出: 每个 Agent 一组 Top-K (MVP K=2), 同时给一个聚合视图 (跨 Agent 撞车标识为强信号).

不做:
  - 相似度阈值过滤
  - 评分 / 年代 / 成人内容过滤
  - 历史去重
"""

from __future__ import annotations

# TODO(MVP-step-4): 实现
#   1. 加载 embeddings.npy 到内存; meta.parquet 到 DataFrame
#   2. 加载同款 sentence-transformer 模型
#   3. encode(pseudo_overviews, normalize_embeddings=True) -> (M, 384)
#   4. similarity = pseudo @ embeddings.T  (cosine, 已归一化)
#   5. np.argpartition 取 Top-K per agent
#   6. 聚合视图: 按 tmdb_id 计数, 标记被多少 Agent 召回
