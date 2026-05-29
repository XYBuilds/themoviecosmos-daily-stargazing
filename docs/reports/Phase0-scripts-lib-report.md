# Phase 0 - scripts/lib 交付报告

## 1. 改动范围 (Scope)

- `scripts/lib/paths.py` — `repo_root`, `cleaned_csv`, `index_dir`, `embeddings_npy`, `meta_parquet`, `embeddings_source_npy`
- `scripts/lib/env.py` — `load_env`, `default_llm_provider`
- `scripts/lib/llm.py` — `get_llm_client`（MiMo / DeepSeek，缺 key 时 `RuntimeError`）
- `scripts/lib/__init__.py` — 已有导出（与上述模块对齐）
- `scripts/__init__.py` — 包说明（本分支先前提交）
- `.env.example` — `CLEANED_CSV`, `EMBEDDINGS_SOURCE`, `INDEX_DIR`；`TMDB_CSV` 注释为 subsample only
- 无新增依赖包（沿用 `requirements.txt` 中的 `openai`, `python-dotenv`）

## 2. 技术实现 (Implementation)

- `paths.py` 以 `scripts/lib` 上溯两级定位 `REPO_ROOT`；相对路径经 `CLEANED_CSV` / `EMBEDDINGS_SOURCE` / `INDEX_DIR` 覆盖，与 `build_index.py` 默认布局一致
- `env.py` 从仓库根加载 `.env`（单次 `load_dotenv`）
- `llm.py` 按 provider 读取 `MIMO_*` / `DEEPSEEK_*`，返回 `openai.OpenAI(api_key=..., base_url=...)`

## 3. 本地验证结果 (Verification)

```text
python -c "from scripts.lib.paths import cleaned_csv, embeddings_npy; from scripts.lib.llm import get_llm_client; print(cleaned_csv(), embeddings_npy())"
# \\192.168.1.110\Hermes_Workspace\themoviecosmos-daily-stargazing\data\output\cleaned.csv
# \\192.168.1.110\Hermes_Workspace\themoviecosmos-daily-stargazing\data\index\embeddings.npy
```

（需已安装 `requirements.txt` 中的 `python-dotenv` 与 `openai`；未调用 `get_llm_client()`，故无需 API key。）

## 4. 潜在影响或技术债 (Technical Debt & Caveats)

- `build_index.py` 仍内联路径解析；后续可改为从 `scripts.lib.paths` 导入以去重
- Phase 0.3 `smoke_llm.py` 依赖本模块的 `get_llm_client`
- 克隆后需本地 `pip install -r requirements.txt` 方可导入 `scripts.lib`
