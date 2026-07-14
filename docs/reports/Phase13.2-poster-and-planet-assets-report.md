# Phase 13.2 · 海报下载与 Bloom ON 星球资产报告

- **TODO**: `p13.2-poster-and-planet-assets`
- **状态**: complete
- **分支**: `feat/phase13.2-poster-planet-assets`

## 交付

- 新增 `scripts/lib/poster_downloader.py`：统一下载 TMDB original poster，校验 JPEG/PNG magic、非空内容、超时与原子落盘；返回源 URL、内容类型和文件大小。
- `scripts/publish_discord.py` 改为复用该下载器，保留原有 Discord 输出目录和命名。
- 新增 `review_panel/publication_assets.py`：通过 publication bundle 路径投影生成 `assets/poster-original.jpg` 与 `assets/planet.png`，并且只调用一次 `render_planet(..., bloom=True)`。

## 验证

```text
python -m pytest tests/test_poster_downloader.py tests/test_publication_assets.py tests/test_planet_renderer.py
17 passed in 10.65s
```

覆盖成功下载、404、超时、空响应、错误 magic、Discord 复用、bundle 路径投影，以及单 Bloom ON 星球渲染调用。