from __future__ import annotations

import json
from pathlib import Path

from scripts.ctp025292_csharp_runtime_parity_audit import build_audit


def _write_trust_marker(root: Path) -> None:
    (root / "_ctp025292_runtime_pack.json").write_text(
        json.dumps(
            {
                "runtime_pack_id": "ctp-live-025292-md",
                "source_kind": "operator_trusted_025292",
                "source_bin": str(root),
            }
        ),
        encoding="utf-8",
    )


def _write_source_trust_marker(source: Path, *, md_bytes: bytes, td_bytes: bytes) -> None:
    source.mkdir()
    (source / "thostmduserapi_se.dll").write_bytes(md_bytes)
    (source / "thosttraderapi_se.dll").write_bytes(td_bytes)
    _write_trust_marker(source)
    marker = json.loads((source / "_ctp025292_runtime_pack.json").read_text(encoding="utf-8"))
    import hashlib

    marker["dlls"] = {
        "thostmduserapi_se.dll": {
            "sha256": hashlib.sha256(md_bytes).hexdigest().upper(),
            "length": len(md_bytes),
        },
        "thosttraderapi_se.dll": {
            "sha256": hashlib.sha256(td_bytes).hexdigest().upper(),
            "length": len(td_bytes),
        },
    }
    (source / "_ctp025292_runtime_pack.json").write_text(json.dumps(marker), encoding="utf-8")


def test_csharp_v6315_candidate_is_not_auto_route_trusted(tmp_path: Path) -> None:
    current = tmp_path / "current"
    csharp = tmp_path / "csharp"
    current.mkdir()
    csharp.mkdir()
    (current / "thostmduserapi_se.dll").write_bytes(b"THOST UserAPI v1.0\nv6.7.11_20250617")
    (current / "thosttraderapi_se.dll").write_bytes(b"THOST UserAPI v1.0\nv6.7.11_20250617")
    _write_trust_marker(current)

    (csharp / "thostmduserapi_se.dll").write_bytes(b"THOST UserAPI v1.0\nv6.3.15_20190220")
    (csharp / "thosttraderapi_se.dll").write_bytes(b"THOST UserAPI v1.0\nv6.3.15_20190220")

    source = tmp_path / "NMdSpi.cpp"
    source.write_text(
        "void OnFrontConnected(){ ReqUserLogin(&m_logonField, 0); }\n"
        "void OnRspUserLogin(){ SubscribeMarketData(c_inst, 1); }\n",
        encoding="utf-8",
    )

    payload = build_audit(
        current_runtime_bin=current,
        candidate_roots=[csharp],
        source_refs=[source],
        desktop_csvs=[],
        created_at="2026-06-16T14:52:00+08:00",
    )

    assert payload["success"] is False
    assert payload["status"] == "blocked"
    assert payload["current_runtime_pack"]["classification"] == "operator_trusted_025292_non_openctp_family"
    assert payload["candidate_runtime_families"][0]["classification"] == (
        "csharp_reference_v6315_se_candidate_untrusted_for_route"
    )
    assert payload["parity_against_current_runtime"][0]["same_required_se_pair_as_current"] is False
    assert payload["findings"]["subscription_not_primary_blocker"] is True
    assert payload["safety_decision"]["materialize_csharp_dll_family_into_route_runtime_now"] is False
    assert payload["safety_decision"]["bridge_rebuild_required_if_sdk_family_changes"] is True
    assert payload["negative_assertions"]["did_not_copy_or_materialize_external_dlls"] is True
    assert payload["source_refs"][0]["findings"]["req_user_login_request_id_zero"]["present"] is True
    assert payload["source_refs"][0]["findings"]["subscribe_after_login_path"]["present"] is True


def test_materialized_bin_is_trusted_when_synced_manifest_points_to_matching_marker(tmp_path: Path) -> None:
    source = tmp_path / "operator-source"
    current = tmp_path / "pack" / "bin"
    current.mkdir(parents=True)
    md_bytes = b"THOST UserAPI v1.0\nv6.7.11_20250617"
    td_bytes = b"THOST UserAPI v1.0\nv6.7.11_20250617 td"
    _write_source_trust_marker(source, md_bytes=md_bytes, td_bytes=td_bytes)
    (current / "thostmduserapi_se.dll").write_bytes(md_bytes)
    (current / "thosttraderapi_se.dll").write_bytes(td_bytes)
    (current / "_synced_from.txt").write_text(
        f"runtime_pack_id=ctp-live-025292-md\nctp_api={source}\n",
        encoding="utf-8",
    )

    payload = build_audit(
        current_runtime_bin=current,
        candidate_roots=[],
        source_refs=[],
        desktop_csvs=[],
        created_at="2026-06-16T14:52:00+08:00",
    )

    assert payload["current_runtime_pack"]["classification"] == "operator_trusted_025292_non_openctp_family"
    assert payload["current_runtime_pack"]["source_trust_marker"]["matches_runtime_bin_dlls"] is True
    assert payload["findings"]["current_runtime_is_operator_trusted"] is True


def test_openctp_tts_candidate_is_rejected_even_with_required_names(tmp_path: Path) -> None:
    current = tmp_path / "current"
    openctp = tmp_path / "openctp"
    current.mkdir()
    openctp.mkdir()
    (current / "thostmduserapi_se.dll").write_bytes(b"THOST UserAPI v1.0\nv6.7.11_20250617")
    (current / "thosttraderapi_se.dll").write_bytes(b"THOST UserAPI v1.0\nv6.7.11_20250617")
    _write_trust_marker(current)

    (openctp / "thostmduserapi_se.dll").write_bytes(b"openctp-tts v6.6.9 md")
    (openctp / "thosttraderapi_se.dll").write_bytes(b"openctp-tts v6.6.9 td")

    payload = build_audit(
        current_runtime_bin=current,
        candidate_roots=[openctp],
        source_refs=[],
        desktop_csvs=[],
        created_at="2026-06-16T14:52:00+08:00",
    )

    candidate = payload["candidate_runtime_families"][0]
    assert candidate["classification"] == "rejected_openctp_tts_paper_family"
    assert payload["findings"]["openctp_tts_candidates_rejected"] == 1
    assert "Do not use OpenCTP/TTS" in payload["blocker"]["next_action"]
    assert payload["negative_assertions"]["did_not_launch_legacy_csharp_provider"] is True
