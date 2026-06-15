from __future__ import annotations

from scripts.ctp025292_runtime_pack_candidate_approval_packet import (
    build_candidate_approval_packet,
)


def _candidate(path: str, md_hash: str, td_hash: str, classification: str = "candidate_untrusted") -> dict:
    return {
        "path": path,
        "classification": classification,
        "issues": ["trust_marker_missing"],
        "dlls": {
            "thostmduserapi_se.dll": {"sha256": md_hash, "length": 100},
            "thosttraderapi_se.dll": {"sha256": td_hash, "length": 200},
        },
        "trust_marker_present": False,
    }


def test_candidate_packet_groups_duplicate_vnpy_family_and_requires_operator_ack() -> None:
    discovery = {
        "candidates": [
            _candidate("D:/Nautilus/nautilus_ctp_adapter/output/vnpy_ctp_clone/vnpy_ctp/api", "A" * 64, "B" * 64),
            _candidate("D:/wt/main/.venv/Lib/site-packages/vnpy_ctp/api", "A" * 64, "B" * 64),
        ]
    }

    payload = build_candidate_approval_packet(discovery)

    assert payload["status"] == "blocked_waiting_operator_ack"
    assert payload["blocker_id"] == "ctp025292_candidate_family_operator_ack_missing"
    assert payload["family_count"] == 1
    assert payload["operator_ack_eligible_family_count"] == 1
    assert payload["auto_select_allowed"] is False
    assert len(payload["operator_ack_choices"]) == 2
    assert payload["negative_assertions"]["did_not_write_trust_marker"] is True


def test_candidate_packet_rejects_openctp_path_even_when_hash_unknown() -> None:
    discovery = {
        "candidates": [
            _candidate("D:/Nautilus/nautilus_ctp_adapter/output/openctp/ctpapi-python-win64", "C" * 64, "D" * 64),
        ]
    }

    payload = build_candidate_approval_packet(discovery)

    assert payload["status"] == "blocked_no_operator_ack_eligible_family"
    assert payload["operator_ack_eligible_family_count"] == 0
    assert payload["families"][0]["path_openctp_like"] is True
    assert "family_path_openctp_like_rejected" in payload["families"][0]["issues"]


def test_candidate_packet_flags_multiple_non_openctp_families_ambiguous() -> None:
    discovery = {
        "candidates": [
            _candidate("D:/vendor/a", "A" * 64, "B" * 64),
            _candidate("D:/vendor/b", "C" * 64, "D" * 64),
        ]
    }

    payload = build_candidate_approval_packet(discovery)

    assert payload["status"] == "blocked_ambiguous_operator_ack_family"
    assert payload["blocker_id"] == "ctp025292_candidate_family_ambiguous"
    assert payload["operator_ack_eligible_family_count"] == 2
