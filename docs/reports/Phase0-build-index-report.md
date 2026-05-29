# Phase 0 - build_index 交付报告

## 1. 改动范围 (Scope)

- `scripts/build_index.py` — 完整实现 `--reuse` 默认流程与 `--rebuild-embed` stub
- 本地生成（gitignore）：`data/index/meta.parquet`、`data/index/embeddings.npy`
- 无新增依赖包

## 2. 技术实现 (Implementation)

- 默认从 `data/output/cleaned.csv` 读取 9 列 meta 字段，保持 CSV 行序写入 `meta.parquet`
- 使用 `shutil.copy2` 将 `data/output/text_embeddings.npy` 同步到 `INDEX_DIR/embeddings.npy`
- 断言 `len(meta) == embeddings.shape[0] == 59341` 且 shape `(59341, 384)`，失败 `sys.exit(1)`
- `--reuse` 路径不加载 `sentence-transformers`；`--rebuild-embed` 打印未实现并退出

## 3. 本地验证结果 (Verification)

```text
python scripts/build_index.py
python -c "import numpy as np, pandas as pd; e=np.load('data/index/embeddings.npy'); m=pd.read_parquet('data/index/meta.parquet'); assert len(m)==59341 and e.shape==(59341,384); print('OK', m.columns.tolist())"
# OK ['id', 'title', 'original_title', 'overview', 'tagline', 'genres', 'original_language', 'release_date', 'poster_path']
```

## 4. 潜在影响或技术债 (Technical Debt & Caveats)

- `build_index.py` 内路径解析与 Phase 0.2 的 `scripts/lib/paths.py` 尚未统一；0.2 完成后应改为从 `paths` 导入
- 克隆仓库后需运行 `python scripts/build_index.py` 生成 index 产物（`data/index/` 在 gitignore 中）
