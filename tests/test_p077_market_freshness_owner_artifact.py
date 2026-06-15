from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta
from pathlib import Path

from nautilus_ctp_adapter.adapters.ctp.config import CtpAdapterConfig
from nautilus_ctp_adapter.adapters.ctp.data_client import CtpMdSmokeResult

from scripts.ctp_p077_market_freshness_probe import (
    BASELINE,
    OWNER,
    UPSTREAM_BLOCKER_ID,
    attach_checksum,
    build_market_freshness_artifact,
    build_typed_blocker_artifact,
    run_probe_with_watchdog,
)


def _config() -> CtpAdapterConfig:
    return CtpAdapterConfig.from_dict(
        {
            "BrokerID": "9999",
            "UserID": "PAPER_USER_19053",
            "Password": "secret-password",
            "Pricer": "tcp://trading.openctp.cn:30011",
            "Host": "tcp://trading.openctp.cn:30001",
            "Instruments": ["rb2610"],
        }
    )


def _smoke(
    *,
    ts_epoch_us: int,
    symbol: str = "rb2610",
    received_at_epoch_us: int | None = None,
) -> CtpMdSmokeResult:
    return CtpMdSmokeResult(
        init_code=0,
        login_request_code=0,
        subscribe_code=0,
        login_success=True,
        login_error_id=0,
        login_error_message="",
        first_tick_symbol=symbol,
        first_tick_last=3137.0,
        first_tick_bid=3136.0,
        first_tick_ask=3138.0,
        first_tick_ts_epoch_us=ts_epoch_us,
        first_tick_received_at_epoch_us=received_at_epoch_us,
    )


def test_pass_artifact_is_owner_scoped_source_backed_and_checksummed(tmp_path: Path) -> None:
    now = datetime(2026, 6, 13, 14, 0, 0, tzinfo=UTC)
    tick_ts = int((now - timedelta(seconds=2)).timestamp() * 1_000_000)

    artifact = build_market_freshness_artifact(
        config=_config(),
        config_path=tmp_path / "paper.json",
        route_id="ctp-paper-19053",
        account_alias="19053",
        result=_smoke(ts_epoch_us=tick_ts),
        collected_at_utc=now,
        freshness_threshold_seconds=10,
    )

    assert artifact["baseline"] == BASELINE
    assert artifact["owner"] == OWNER
    assert artifact["upstream_blocker_id"] == UPSTREAM_BLOCKER_ID
    assert artifact["status"] == "passed"
    assert artifact["success"] is True
    assert artifact["md"]["first_tick_age_seconds"] == 2.0
    assert artifact["checksum"].startswith("sha256:")
    assert "CtpDataClient.run_live_md_smoke" in artifact["accepted_truth_sources"]


def test_artifact_redacts_account_and_password(tmp_path: Path) -> None:
    now = datetime(2026, 6, 13, 14, 0, 0, tzinfo=UTC)
    tick_ts = int((now - timedelta(seconds=1)).timestamp() * 1_000_000)

    artifact = build_market_freshness_artifact(
        config=_config(),
        config_path=tmp_path / "paper.json",
        route_id="ctp-paper-19053",
        account_alias="19053",
        result=_smoke(ts_epoch_us=tick_ts),
        collected_at_utc=now,
        freshness_threshold_seconds=10,
    )
    serialized = json.dumps(artifact, ensure_ascii=False)

    assert "PAPER_USER_19053" not in serialized
    assert "secret-password" not in serialized
    assert artifact["config_identity"]["user_id_present"] is True
    assert artifact["config_identity"]["user_id_fingerprint"]


def test_stale_tick_becomes_typed_market_freshness_blocker(tmp_path: Path) -> None:
    now = datetime(2026, 6, 13, 14, 0, 0, tzinfo=UTC)
    tick_ts = int((now - timedelta(seconds=90)).timestamp() * 1_000_000)

    artifact = build_market_freshness_artifact(
        config=_config(),
        config_path=tmp_path / "paper.json",
        route_id="ctp-paper-19053",
        account_alias="19053",
        result=_smoke(ts_epoch_us=tick_ts),
        collected_at_utc=now,
        freshness_threshold_seconds=30,
    )

    assert artifact["status"] == "blocked"
    assert artifact["blocker_type"] == "market-freshness"
    assert artifact["failure_reason"] == "first_tick_stale"
    assert "first_tick_stale" in artifact["issues"]


def test_received_at_basis_passes_with_stale_exchange_timestamp_warning(tmp_path: Path) -> None:
    now = datetime(2026, 6, 13, 14, 0, 0, tzinfo=UTC)
    exchange_tick_ts = int((now - timedelta(seconds=90)).timestamp() * 1_000_000)
    received_at_ts = int((now - timedelta(seconds=2)).timestamp() * 1_000_000)

    artifact = build_market_freshness_artifact(
        config=_config(),
        config_path=tmp_path / "paper.json",
        route_id="ctp-paper-19053",
        account_alias="19053",
        result=_smoke(ts_epoch_us=exchange_tick_ts, received_at_epoch_us=received_at_ts),
        collected_at_utc=now,
        freshness_threshold_seconds=30,
        freshness_basis="received_at",
    )

    assert artifact["status"] == "passed"
    assert artifact["freshness_basis"] == "received_at"
    assert artifact["md"]["first_tick_received_age_seconds"] == 2.0
    assert artifact["md"]["first_tick_age_seconds"] == 90.0
    assert artifact["warnings"] == ["first_tick_exchange_timestamp_stale"]


def test_unexpected_tick_symbol_becomes_blocker(tmp_path: Path) -> None:
    now = datetime(2026, 6, 13, 14, 0, 0, tzinfo=UTC)
    tick_ts = int((now - timedelta(seconds=2)).timestamp() * 1_000_000)

    artifact = build_market_freshness_artifact(
        config=_config(),
        config_path=tmp_path / "paper.json",
        route_id="ctp-paper-19053",
        account_alias="19053",
        result=_smoke(ts_epoch_us=tick_ts, symbol="zn2610"),
        collected_at_utc=now,
        freshness_threshold_seconds=10,
    )

    assert artifact["status"] == "blocked"
    assert artifact["failure_reason"] == "unexpected_tick_symbol"


def test_missing_config_probe_returns_owner_blocker(tmp_path: Path) -> None:
    artifact = run_probe_with_watchdog(
        config_path=tmp_path / "missing.json",
        route_id="ctp-paper-19053",
        account_alias="19053",
        timeout_seconds=1,
        freshness_threshold_seconds=10,
        flow_path=None,
        process_timeout_seconds=5,
    )

    assert artifact["status"] == "blocked"
    assert artifact["owner"] == OWNER
    assert artifact["blocker_type"] == "market-resource"
    assert artifact["failure_reason"] == "missing_config"
    assert artifact["checksum"].startswith("sha256:")


def test_watchdog_timeout_returns_owner_blocker(tmp_path: Path) -> None:
    config_path = tmp_path / "paper.json"
    config_path.write_text(json.dumps({"UserID": "PAPER_USER_19053"}), encoding="utf-8")

    artifact = run_probe_with_watchdog(
        config_path=config_path,
        route_id="ctp-paper-19053",
        account_alias="19053",
        timeout_seconds=20,
        freshness_threshold_seconds=10,
        flow_path=None,
        process_timeout_seconds=0,
    )

    assert artifact["status"] == "blocked"
    assert artifact["owner"] == OWNER
    assert artifact["failure_reason"] == "market_freshness_probe_timeout"
    assert "process_timeout" in artifact["issues"]


def test_checksum_is_canonical_and_changes_when_payload_changes() -> None:
    payload = build_typed_blocker_artifact(
        route_id="ctp-paper-19053",
        account_alias="19053",
        failure_reason="missing_config",
        blocker_type="market-resource",
        collected_at_utc=datetime(2026, 6, 13, 14, 0, 0, tzinfo=UTC),
        issues=["config_path_missing"],
    )
    changed = dict(payload)
    changed["failure_reason"] = "different"

    assert payload["checksum"] == attach_checksum(payload)["checksum"]
    assert payload["checksum"] != attach_checksum(changed)["checksum"]
