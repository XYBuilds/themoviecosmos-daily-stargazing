# Phase 3.8.5 - English eval corpus + e2e smoke 交付报告

## 1. 改动范围 (Scope)

- `tests/eval_news/batch-manifest.json` — v2：声明 `language: en`、3.6/3.7/3.8 lineage、`news_unchanged_since: 3.6`
- `scripts/run_phase38_eval.py` — **新增** 全链 runner（news → A0 → P-Expand → persona neutral+toned → retrieve → CJK 校验）
- `scripts/run_persona_batch.py` — `--eval-phase 3.8`：读 phase3.8 decon+expansion，传 `expansion` 给 persona pipeline，无 A1
- `scripts/eval_batch_manifest.py` — 注释更新
- `tests/test_eval_english_corpus.py` — **新增** 英文语料 + CJK helper 单测

无新增依赖包。`tests/eval_news/*.json` 新闻正文自 3.6 起已为英文，本 TODO 未换新闻主题。

## 2. 技术实现 (Implementation)

- **语料**：10 条 `run_id` 语义不变（01..10）；manifest 记录与 phase3.6 中文 decon / phase3.7 并跑不可直接数值对照。
- **E2E**：`run_phase38_eval.py` 写入 `output/Eval/phase3.8/{run_id}/`；`find_cjk_violations` 扫描 decon/expansion/persona/retrieve JSON。
- **批跑衔接**：`run_persona_batch.py --eval-phase 3.8` 供 3.8.7 批量 persona（需先 `run_phase38_eval` 产 A0+扩展）。

## 3. 本地验证结果 (Verification)

```text
python -m unittest tests.test_eval_english_corpus tests.test_eval_batch_manifest tests.test_personas -v
# Ran 30 tests — OK (skipped=1)

python scripts/run_phase38_eval.py --run-id 01-grid-outage --personas The-Ruler --no-skip-existing
# Wrote output/Eval/phase3.8/01-grid-outage · agents=1 candidates=8 english_ok=True

python scripts/run_phase38_eval.py --run-id 01-grid-outage --verify-only
# OK: no CJK
```

Smoke 产物：`The-Ruler` 含 `n1`（channel_role=neutral）+ `p1`–`p3`（toned）；A0/P-Expand 全英文。

## 4. 潜在影响或技术债 (Technical Debt & Caveats)

- E2E smoke 仅 1 persona（The-Ruler）；12 persona 全链留给 3.8.6/3.8.7。
- `reality.md` / `run_eval` 模板仍为中文 UI 标签（非 pipeline 文本）；CJK 闸仅扫 JSON 正文。
- `output/Eval/phase3.8/` 为本地 eval 产物，未入库。
