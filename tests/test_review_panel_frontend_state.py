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


def test_generate_drafts_success_previews_first_draft_while_operation_is_in_flight() -> None:
    """generate-drafts 成功后也处于 in-flight 收尾期，进入 pick 时必须允许内部预览。"""
    html = _read_index_html()
    generate_fn = _slice_between(html, "function onGenerateDrafts", "function onCombineDrafts")
    enter_pick_fn = _slice_between(html, "function enterPickStage", "function loadRefineCopy")

    assert "enterPickStage({ allowPreviewDuringInFlight: true });" in generate_fn
    assert "if (els.enterRefineBtn) { els.enterRefineBtn.disabled = !state.previewDraftId; }" in generate_fn
    assert "function enterPickStage(options)" in enter_pick_fn
    assert "allowPreviewDuringInFlight" in enter_pick_fn
    assert "previewDraft(" in enter_pick_fn
    assert "onPreviewDraft(" not in enter_pick_fn


def test_preview_draft_keeps_user_click_guard_but_allows_internal_refresh() -> None:
    """用户点击切草稿仍受 in-flight 保护；程序内部终态刷新可显式绕过。"""
    html = _read_index_html()
    preview_fn = _slice_between(html, "function previewDraft", "function onEnterRefine")

    assert "function previewDraft(draftId, options)" in preview_fn
    assert "options = options || {};" in preview_fn
    assert "if (state.draftOpInFlight && !options.allowDuringInFlight) return;" in preview_fn
    assert "function onPreviewDraft(draftId)" in preview_fn
    assert "previewDraft(draftId);" in preview_fn