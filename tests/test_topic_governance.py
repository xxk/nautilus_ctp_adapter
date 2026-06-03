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
    active_topic = frontier["active_topic"]
    active_change = frontier["active_change"]

    if active_topic is None:
        assert active_change is None
        assert frontier["counts"]["open_topic_count"] == 0
        assert frontier["counts"]["parked_topic_count"] >= 0
    else:
        assert isinstance(active_topic, dict)
        assert active_topic["canonical_status"] == "in_progress"
        assert active_topic["execution_order"] == 1
        assert isinstance(active_change, dict)
        assert active_change["change_id"] == active_topic["next_change_id"]


def test_audit_topic_docs_passes() -> None:
    result = audit_topic_docs(repository_root())
    assert result["status"] == "ok"
    assert result["checked_topic_count"] >= 1
