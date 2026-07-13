# Phase 36.7 — Daily publish 星球导出集成报告

## 交付

- `scripts/main.py publish` 在候选电影定位完成后、C2 文案生成前，默认依次调用 `render_planet()` 导出 Bloom off 与 Bloom on 两张 PNG。
- 图片命名固定为 `{date}_{tmdb_id}_planet_bloom-{off|on}.png`；Chronicle CLI 同步生成同名 `.render.json` metadata。
- 新增 `--no-planet-image`，仅在显式指定时跳过两次图片导出。
- 星球导出失败会以退出码 `1` 中止 `publish`，不会调用 `compose.run_publish()`，避免出现文案已生成而图片缺失的半完成发布。

## 验证

```text
python -m pytest tests/test_main_publish.py tests/test_planet_renderer.py
19 passed
```

测试覆盖默认双图调用及路径、跳过开关、导出失败短路 C2，并保留 36.6 的适配器契约测试。