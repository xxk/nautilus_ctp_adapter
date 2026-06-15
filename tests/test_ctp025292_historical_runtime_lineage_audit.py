from __future__ import annotations

from pathlib import Path

from scripts.ctp025292_historical_runtime_lineage_audit import (
    audit_historical_runtime_lineage,
)


def test_historical_success_without_runtime_hash_does_not_auto_trust(tmp_path: Path) -> None:
    evidence = tmp_path / "td_startup_truth_20260403.log"
    evidence.write_text(
        '{"baseline":"td-startup-truth-v1","ready":true,"login_success":true}\n'
        "TD Auto-auth: 0155/025292\n",
        encoding="utf-8",
    )

    payload = audit_historical_runtime_lineage([tmp_path])

    assert payload["success"] is False
    assert payload["candidate_auto_trust_allowed"] is False
    assert payload["historical_success_ref_count"] == 1
    assert "historical_success_runtime_hash_missing" in payload["issues"]


def test_trusted_runtime_hash_ref_allows_historical_lineage(tmp_path: Path) -> None:
    evidence = tmp_path / "025292_runtime_hash.json"
    evidence.write_text(
        '{'
        '"runtime_pack_id":"ctp-live-025292-md",'
        '"thostmduserapi_se.dll":"AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",'
        '"thosttraderapi_se.dll":"BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB",'
        '"login_success":true,'
        '"account_id":"025292"'
        '}',
        encoding="utf-8",
    )

    payload = audit_historical_runtime_lineage([tmp_path])

    assert payload["success"] is True
    assert payload["candidate_auto_trust_allowed"] is True
    assert payload["trusted_runtime_hash_ref_count"] == 1


def test_missing_historical_config_is_reported_separately(tmp_path: Path) -> None:
    evidence = tmp_path / "td_order_truth_20260402.log"
    evidence.write_text(
        '{"ready":true,"login_success":true}\nTD Auto-auth: 0155/025292\n',
        encoding="utf-8",
    )

    payload = audit_historical_runtime_lineage(
        [tmp_path],
        historical_config=tmp_path / "cfgs" / "local" / "ctp.live.025292.rb2610.10675.json",
    )

    assert payload["success"] is False
    assert "historical_success_config_missing" in payload["issues"]
    assert payload["historical_config"]["exists"] is False
