from __future__ import annotations

from pathlib import Path

from nautilus_ctp_adapter.devtools.topic_governance import (
    audit_topic_docs,
    collect_current_frontier,
    sync_topic_index,
)


def repository_root() -> Path:
    return Path(__file__).resolve().parents[1]


def test_sync_topic_index_check_passes() -> None:
    path = sync_topic_index(repository_root(), check=True)
    assert path.name == "README.md"


def test_collect_current_frontier_returns_consistent_active_state() -> None:
    frontier = collect_current_frontier(repository_root())
    active_change = frontier["active_change"]

    assert frontier["frontier_source"] == "docs/changes/*/plan.md"
    assert frontier["active_topic"] is None

    if active_change is None:
        assert frontier["counts"]["active_change_count"] == 0
        assert frontier["counts"]["queued_change_count"] >= 0
    else:
        assert isinstance(active_change, dict)
        assert active_change["status"] == "in_progress"
        assert active_change["plan_path"].endswith("/plan.md")


def test_audit_topic_docs_passes() -> None:
    result = audit_topic_docs(repository_root())
    assert result["status"] == "ok"
    assert result["checked_topic_count"] >= 1
