from __future__ import annotations

from pathlib import Path


INDEX_HTML = Path(__file__).resolve().parents[1] / "review_panel" / "index.html"


def _read_index_html() -> str:
    return INDEX_HTML.read_text(encoding="utf-8")


def _slice_between(text: str, start: str, end: str) -> str:
    start_idx = text.index(start)
    end_idx = text.index(end, start_idx)
    return text[start_idx:end_idx]


def test_retry_success_refreshes_preview_even_while_draft_operation_is_in_flight() -> None:
    """12.6.5 gate 回归：retry job 成功时不能被 onPreviewDraft 的互斥锁挡住。

    用户点击「重试这一条」后，onRetryDraft 会先把 state.draftOpInFlight 置 true。
    旧实现成功返回后直接调用 onPreviewDraft(id)，但 onPreviewDraft 第一行看到 in-flight
    就 return，导致正文不刷新、warnings 区旧的「重掷中，稍候…」残留。
    """
    html = _read_index_html()
    retry_fn = _slice_between(html, "function onRetryDraft", "function renderDraftPool")

    assert "previewDraft(id, { allowDuringInFlight: true });" in retry_fn
    assert "onPreviewDraft(id);" not in retry_fn


def test_prepare_publication_is_the_only_draft_generation_trigger() -> None:
    """13.5：选片只落 selection；草稿、海报、星球只能经显式准备动作并行启动。"""
    html = _read_index_html()
    prepare_fn = _slice_between(html, "function onPreparePublication", "function onRetryPublicationArtifact")
    select_fn = _slice_between(html, "function onSelectCandidate", "// ---------------------------------------------------------------------\n      // 事件绑定")

    assert 'submitJob("/api/prepare-publication"' in prepare_fn
    assert "onPublicationJobRunning" in prepare_fn
    assert "showCopyLoading" in prepare_fn
    assert "/api/generate-drafts" not in html
    assert "/api/prepare-publication" not in select_fn
    assert 'apiPost("/api/select"' in select_fn


def test_publication_manifest_drives_asset_workbench_and_retries() -> None:
    """manifest 是视觉资产状态唯一来源；图片请求和重试都经受限 API。"""
    html = _read_index_html()
    card_fn = _slice_between(html, "function renderAssetCard", "function renderVisualAssets")
    retry_fn = _slice_between(html, "function onRetryPublicationArtifact", "// ---------------------------------------------------------------------\n      // 10.5")

    assert 'id="visual-assets"' in html
    assert '"/api/publication-asset?date="' in html
    assert '"/api/retry-publication-artifact"' in retry_fn
    assert "data-retry-artifact" in card_fn
    assert "console.log(\"[publication] manifest\"" in html


def test_asset_workbench_follows_pick_and_refine_stages() -> None:
    """候选页不展示资产栏；pick/refine 使用同一个 manifest 投影，窄屏布局仍先展示资产。"""
    html = _read_index_html()
    switch_fn = _slice_between(html, "function switchStage", "function updateCopyHead")

    assert 'stage === "pick" || stage === "refine"' in switch_fn
    assert "renderVisualAssets();" in switch_fn
    assert ".publication-workbench" in html
    assert "@media (max-width: 820px)" in html
    assert "grid-template-columns: 1fr;" in html

def test_preview_draft_keeps_user_click_guard_but_allows_internal_refresh() -> None:
    """用户点击切草稿仍受 in-flight 保护；程序内部终态刷新可显式绕过。"""
    html = _read_index_html()
    preview_fn = _slice_between(html, "function previewDraft", "function onEnterRefine")

    assert "function previewDraft(draftId, options)" in preview_fn
    assert "options = options || {};" in preview_fn
    assert "if (state.draftOpInFlight && !options.allowDuringInFlight) return;" in preview_fn
    assert "function onPreviewDraft(draftId)" in preview_fn
    assert "previewDraft(draftId);" in preview_fn