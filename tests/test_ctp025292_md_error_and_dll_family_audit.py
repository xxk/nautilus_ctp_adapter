from __future__ import annotations

import json
from pathlib import Path

from scripts.ctp025292_md_error_and_dll_family_audit import build_audit


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def test_error_return_analysis_classifies_disconnect_without_ctp_error(tmp_path: Path) -> None:
    summary = tmp_path / "summary.json"
    capture = tmp_path / "capture.json"
    runtime = tmp_path / "runtime" / "bin"
    runtime.mkdir(parents=True)
    (runtime / "thostmduserapi_se.dll").write_bytes(b"THOST UserAPI v1.0\nv6.7.11_20250617")
    (runtime / "thosttraderapi_se.dll").write_bytes(b"THOST UserAPI v1.0\nv6.7.11_20250617")
    (runtime / "_synced_from.txt").write_text(
        "runtime_pack_id=ctp-live-025292-md\nctp_api=vendor-x\n",
        encoding="utf-8",
    )

    _write_json(
        summary,
        {
            "return_codes": [0],
            "disconnect_reasons": [0],
            "login_response_count": 0,
            "rsp_error_count": 0,
            "heartbeat_warning_count": 0,
            "native_close_detail": {"last_login_return_codes": [0]},
        },
    )
    _write_json(
        capture,
        {
            "console_capture": {
                "summary": {
                    "non_json_console_line_count": 0,
                    "matched_line_counts": {
                        "native_session_disconnect": 0,
                        "front_disconnect": 0,
                        "login_response": 0,
                        "rsp_error": 0,
                        "tick": 0,
                    },
                }
            },
            "smoke_result": {"login_error_id": -1, "login_error_message": ""},
        },
    )

    payload = build_audit(
        lifecycle_summary=summary,
        console_capture=capture,
        dll_roots=[runtime],
        historical_refs=[],
        created_at="2026-06-16T14:35:00+08:00",
    )

    analysis = payload["error_return_analysis"]
    assert analysis["classification"] == "no_ctp_login_error_payload_observed_before_front_disconnect"
    assert analysis["req_user_login_return_codes"] == [0]
    assert analysis["disconnect_reasons"] == [0]
    assert analysis["login_response_count"] == 0
    assert analysis["rsp_error_count"] == 0
    assert analysis["login_error_id"] == -1

    family = payload["dll_family_audit"]["families"][0]
    assert family["has_required_se_pair"] is True
    assert family["synced_manifest_summary"]["runtime_pack_id"] == "ctp-live-025292-md"
    assert "v6.7.11_20250617" in family["files"]["thostmduserapi_se.dll"]["version_markers"]
    assert payload["negative_assertions"]["did_not_generate_or_consume_paper_request"] is True


def test_same_name_dll_families_are_distinguished_by_hash_and_marker(tmp_path: Path) -> None:
    summary = tmp_path / "summary.json"
    capture = tmp_path / "capture.json"
    current = tmp_path / "current"
    historical = tmp_path / "historical"
    current.mkdir()
    historical.mkdir()
    _write_json(
        summary,
        {
            "return_codes": [0],
            "disconnect_reasons": [0],
            "login_response_count": 0,
            "rsp_error_count": 0,
            "heartbeat_warning_count": 0,
        },
    )
    _write_json(capture, {"console_capture": {"summary": {}}, "smoke_result": {}})

    (current / "thostmduserapi_se.dll").write_bytes(b"current-md-v6.7.11")
    (current / "thosttraderapi_se.dll").write_bytes(b"current-td-v6.7.11")
    (current / "_ctp025292_runtime_pack.json").write_text(
        json.dumps(
            {
                "runtime_pack_id": "ctp-live-025292-md",
                "source_kind": "operator_trusted_025292",
                "source_bin": str(current),
            }
        ),
        encoding="utf-8",
    )
    (historical / "thostmduserapi_se.dll").write_bytes(b"openctp-tts v6.6.9 historical-md")
    (historical / "thosttraderapi_se.dll").write_bytes(b"openctp-tts v6.6.9 historical-td")

    payload = build_audit(
        lifecycle_summary=summary,
        console_capture=capture,
        dll_roots=[current, historical],
        historical_refs=[],
        current_runtime_family=current,
        current_runtime_source=current,
        historical_success_family=historical,
        created_at="2026-06-16T14:35:00+08:00",
    )

    families = payload["dll_family_audit"]["families"]
    current_family = families[0]
    historical_family = families[1]
    assert current_family["trust_marker_summary"]["source_kind"] == "operator_trusted_025292"
    assert current_family["files"]["thostmduserapi_se.dll"]["sha256"] != historical_family["files"][
        "thostmduserapi_se.dll"
    ]["sha256"]
    assert historical_family["files"]["thostmduserapi_se.dll"]["version_markers"] == [
        "openctp-tts v6.6.9"
    ]
    assert historical_family["classification"] == "rejected_openctp_tts_paper_family"
    assert payload["status"] == "blocked"
    assert "DLL-family lineage" in payload["next_action"]
    assert "Do not materialize OpenCTP/TTS" in payload["next_action"]
