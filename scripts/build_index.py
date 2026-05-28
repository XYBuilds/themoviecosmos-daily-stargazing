"""build_index.py · 构建"纯文本搜索专用库"。

输入: data/subsample/TMDB_all_movies_random20.csv  (MVP) 或 data/full/...
输出:
  - data/index/embeddings.npy   (float32, L2 归一化, shape=(N, 384))
  - data/index/meta.parquet     (检索/渲染必需字段)

设计原则:
  - 与原 3D 宇宙项目对齐: 仅 tagline + overview, 不翻译, 不拼接 genres/language.
  - 6 万级走 NumPy, 不引入 FAISS.
  - 脚本对 subsample 与 full 同构, 只换 --csv 参数.

用法:
  python scripts/build_index.py --csv data/subsample/TMDB_all_movies_random20.csv
  python scripts/build_index.py --csv data/full/TMDB_all_movies.csv
"""

from __future__ import annotations

# TODO(MVP-step-1): 实现以下流程
#   1. 读取 CSV (pandas)
#   2. 清洗 tagline/overview: strip / 去 HTML 残片 / 引号统一
#   3. 缺失值规则:
#        - tagline 缺 -> 接受, overview-only
#        - overview 缺 -> 用 title (+ original_title) 回填
#        - 仍无 -> 剔除
#   4. 拼接 text_for_embedding = (tagline + ". " if tagline else "") + (overview or title)
#   5. 加载 sentence-transformers: paraphrase-multilingual-MiniLM-L12-v2
#   6. encode(..., normalize_embeddings=True), float32
#   7. 保存 embeddings.npy 与 meta.parquet
#      meta 字段: id, title, original_title, overview, tagline, genres,
#                original_language, release_date, poster_path
