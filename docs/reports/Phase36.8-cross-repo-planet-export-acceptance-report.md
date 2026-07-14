# Phase 36.8 — 跨仓库星球导出最终验收报告

## 结论

跨仓库调用已通过真实数据验证。Daily 不接触 Three.js 或 GLSL，只通过 Chronicle CLI、PNG 与 `.render.json` 文件协议工作。

最终发布尺寸口径固定为三次方根：Daily 调用显式传递 `--size-root 3`，Chronicle CLI 同时以 `3` 作为默认值，避免两仓库的尺寸映射漂移。

## 真实调用结果

- 电影：`tmdb_id=157336`。
- 数据版本：`2026.05.11.h3`。
- 产物：
  - `output/Daily_Briefing/phase-36.8_157336_planet_bloom-off.png`
  - `output/Daily_Briefing/phase-36.8_157336_planet_bloom-on.png`
  - 两张图对应的 `.render.json`。
- 两个 PNG 均为 `3000×3000` RGBA；适配器已校验 CLI stdout、PNG 签名与 scanline、alpha bounds 以及 metadata 的电影 ID、分辨率、留白和 Bloom。

## 验证

```text
python -m pytest tests/test_planet_renderer.py tests/test_main_publish.py
20 passed
```

测试覆盖 Windows 下的 `npm.cmd` 参数数组、静默 CLI 调用、离线 `MOVIE_COSMOS_GALAXY_DATA_FILE` 覆盖与 `--size-root 3` 透传。