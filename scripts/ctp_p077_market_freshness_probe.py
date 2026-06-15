from __future__ import annotations

import argparse
import hashlib
import json
import multiprocessing as mp
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from nautilus_ctp_adapter.adapters.ctp.config import CtpAdapterConfig
from nautilus_ctp_adapter.adapters.ctp.data_client import CtpMdSmokeResult
from nautilus_ctp_adapter.adapters.ctp.factory import build_ctp_stack


BASELINE = "p077-ctp-market-freshness-owner-artifact-v1"
OWNER = "owner://ctp_market_owner"
UPSTREAM_BLOCKER_ID = "p077-t6-ctp-market-freshness-owner-artifact-missing"
DEFAULT_CONFIG = REPO_ROOT / "cfgs" / "local" / "ctp.openctp.tts.7x24.local.json"
DEFAULT_OUTPUT = REPO_ROOT / "output" / "reports" / "p077-market-freshness" / "p077_t6_ctp_market_freshness.json"
FORBIDDEN_TRUTH_SOURCES = [
    "route config as tick evidence",
    "stdout/log text as tick evidence",
    "latest/debug path discovery",
    "UI screenshot or browser state",
    "process/window state",
    "DB rows without owner checksum",
]


def _fingerprint(value: str | None) -> str:
    text = str(value or "").strip()
    if not text:
        return ""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]


def _repo_relative(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def _utc_now() -> datetime:
    return datetime.now(UTC)


def _iso_utc(value: datetime) -> str:
    return value.astimezone(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _tick_utc(ts_epoch_us: int | None) -> str | None:
    if ts_epoch_us is None or ts_epoch_us <= 0:
        return None
    return _iso_utc(datetime.fromtimestamp(ts_epoch_us / 1_000_000, tz=UTC))


def _timestamp_age_seconds(*, ts_epoch_us: int | None, collected_at_utc: datetime) -> float | None:
    if ts_epoch_us is None or ts_epoch_us <= 0:
        return None
    ts_dt = datetime.fromtimestamp(ts_epoch_us / 1_000_000, tz=UTC)
    return round((collected_at_utc - ts_dt).total_seconds(), 3)


def _canonical_payload(payload: dict[str, Any]) -> bytes:
    without_checksum = {key: value for key, value in payload.items() if key != "checksum"}
    return json.dumps(without_checksum, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def attach_checksum(payload: dict[str, Any]) -> dict[str, Any]:
    result = dict(payload)
    result["checksum"] = "sha256:" + hashlib.sha256(_canonical_payload(result)).hexdigest()
    return result


def redacted_config_identity(config: CtpAdapterConfig, *, config_path: Path) -> dict[str, Any]:
    return {
        "config_path": _repo_relative(config_path),
        "broker_id": config.broker_id,
        "user_id_present": bool(config.user_id),
        "user_id_fingerprint": _fingerprint(config.user_id),
        "md_front": config.md_front,
        "instruments": list(config.instruments),
    }


def market_freshness_issues(
    result: CtpMdSmokeResult,
    *,
    expected_symbol: str | None,
    collected_at_utc: datetime,
    freshness_threshold_seconds: int,
    max_future_skew_seconds: int,
    freshness_basis: str = "exchange_timestamp",
) -> list[str]:
    issues: list[str] = []
    if result.login_success is not True:
        issues.append("md_login_failed")
    if result.subscribe_code != 0:
        issues.append("md_subscribe_failed")
    if result.first_tick_symbol is None:
        issues.append("first_tick_missing")
    elif expected_symbol and result.first_tick_symbol != expected_symbol:
        issues.append("unexpected_tick_symbol")

    if freshness_basis == "received_at":
        basis_ts_epoch_us = result.first_tick_received_at_epoch_us
        missing_issue = "first_tick_received_at_missing"
        stale_issue = "first_tick_received_at_stale"
        future_issue = "first_tick_received_at_in_future"
    else:
        basis_ts_epoch_us = result.first_tick_ts_epoch_us
        missing_issue = "first_tick_timestamp_missing"
        stale_issue = "first_tick_stale"
        future_issue = "first_tick_timestamp_in_future"

    if basis_ts_epoch_us is None or basis_ts_epoch_us <= 0:
        issues.append(missing_issue)
        return issues

    tick_time = datetime.fromtimestamp(basis_ts_epoch_us / 1_000_000, tz=UTC)
    age_seconds = (collected_at_utc - tick_time).total_seconds()
    if age_seconds > freshness_threshold_seconds:
        issues.append(stale_issue)
    if age_seconds < -max_future_skew_seconds:
        issues.append(future_issue)
    return issues


def exchange_timestamp_warnings(
    result: CtpMdSmokeResult,
    *,
    collected_at_utc: datetime,
    freshness_threshold_seconds: int,
    max_future_skew_seconds: int,
) -> list[str]:
    warnings: list[str] = []
    if result.first_tick_ts_epoch_us is None or result.first_tick_ts_epoch_us <= 0:
        warnings.append("first_tick_exchange_timestamp_missing")
        return warnings

    tick_time = datetime.fromtimestamp(result.first_tick_ts_epoch_us / 1_000_000, tz=UTC)
    age_seconds = (collected_at_utc - tick_time).total_seconds()
    if age_seconds > freshness_threshold_seconds:
        warnings.append("first_tick_exchange_timestamp_stale")
    if age_seconds < -max_future_skew_seconds:
        warnings.append("first_tick_exchange_timestamp_in_future")
    return warnings


def build_market_freshness_artifact(
    *,
    config: CtpAdapterConfig,
    config_path: Path,
    route_id: str,
    account_alias: str,
    result: CtpMdSmokeResult,
    collected_at_utc: datetime,
    freshness_threshold_seconds: int,
    max_future_skew_seconds: int = 5,
    freshness_basis: str = "exchange_timestamp",
) -> dict[str, Any]:
    expected_symbol = config.instruments[0] if config.instruments else None
    issues = market_freshness_issues(
        result,
        expected_symbol=expected_symbol,
        collected_at_utc=collected_at_utc,
        freshness_threshold_seconds=freshness_threshold_seconds,
        max_future_skew_seconds=max_future_skew_seconds,
        freshness_basis=freshness_basis,
    )
    warnings = (
        exchange_timestamp_warnings(
            result,
            collected_at_utc=collected_at_utc,
            freshness_threshold_seconds=freshness_threshold_seconds,
            max_future_skew_seconds=max_future_skew_seconds,
        )
        if freshness_basis == "received_at"
        else []
    )
    status = "passed" if not issues else "blocked"
    tick_time = _tick_utc(result.first_tick_ts_epoch_us)
    age_seconds = _timestamp_age_seconds(ts_epoch_us=result.first_tick_ts_epoch_us, collected_at_utc=collected_at_utc)
    received_time = _tick_utc(result.first_tick_received_at_epoch_us)
    received_age_seconds = _timestamp_age_seconds(
        ts_epoch_us=result.first_tick_received_at_epoch_us,
        collected_at_utc=collected_at_utc,
    )

    payload: dict[str, Any] = {
        "baseline": BASELINE,
        "schema_version": BASELINE,
        "status": status,
        "success": status == "passed",
        "owner": OWNER,
        "upstream_blocker_id": UPSTREAM_BLOCKER_ID,
        "blocker_type": None if status == "passed" else "market-freshness",
        "failure_reason": None if status == "passed" else issues[0],
        "route_id": route_id,
        "account_alias": account_alias,
        "action_mode": "md_only_market_freshness_probe",
        "collected_at_utc": _iso_utc(collected_at_utc),
        "freshness_basis": freshness_basis,
        "freshness_threshold_seconds": freshness_threshold_seconds,
        "max_future_skew_seconds": max_future_skew_seconds,
        "config_identity": redacted_config_identity(config, config_path=config_path),
        "accepted_truth_sources": [
            "CtpDataClient.run_live_md_smoke",
            "CtpMdSmokeResult.first_tick_*",
        ],
        "forbidden_truth_sources": list(FORBIDDEN_TRUTH_SOURCES),
        "issues": issues,
        "warnings": warnings,
        "md": {
            "init_code": result.init_code,
            "login_request_code": result.login_request_code,
            "subscribe_code": result.subscribe_code,
            "login_success": result.login_success,
            "login_error_id": result.login_error_id,
            "login_error_message": result.login_error_message,
            "first_tick_symbol": result.first_tick_symbol,
            "first_tick_last": result.first_tick_last,
            "first_tick_bid": result.first_tick_bid,
            "first_tick_ask": result.first_tick_ask,
            "first_tick_ts_epoch_us": result.first_tick_ts_epoch_us,
            "first_tick_utc": tick_time,
            "first_tick_age_seconds": age_seconds,
            "first_tick_received_at_epoch_us": result.first_tick_received_at_epoch_us,
            "first_tick_received_at_utc": received_time,
            "first_tick_received_age_seconds": received_age_seconds,
        },
    }
    return attach_checksum(payload)


def build_typed_blocker_artifact(
    *,
    route_id: str,
    account_alias: str,
    failure_reason: str,
    blocker_type: str,
    collected_at_utc: datetime,
    issues: list[str],
    config_path: Path | None = None,
    config: CtpAdapterConfig | None = None,
    error_type: str | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "baseline": BASELINE,
        "schema_version": BASELINE,
        "status": "blocked",
        "success": False,
        "owner": OWNER,
        "upstream_blocker_id": UPSTREAM_BLOCKER_ID,
        "blocker_type": blocker_type,
        "failure_reason": failure_reason,
        "route_id": route_id,
        "account_alias": account_alias,
        "action_mode": "md_only_market_freshness_probe",
        "collected_at_utc": _iso_utc(collected_at_utc),
        "accepted_truth_sources": [
            "CtpDataClient.run_live_md_smoke",
            "CtpMdSmokeResult.first_tick_*",
        ],
        "forbidden_truth_sources": list(FORBIDDEN_TRUTH_SOURCES),
        "issues": issues,
        "error_type": error_type,
        "config_identity": (
            redacted_config_identity(config, config_path=config_path)
            if config is not None and config_path is not None
            else None
        ),
        "md": None,
    }
    return attach_checksum(payload)


def run_probe(
    *,
    config_path: Path,
    route_id: str,
    account_alias: str,
    timeout_seconds: int,
    freshness_threshold_seconds: int,
    freshness_basis: str = "exchange_timestamp",
    flow_path: Path | None = None,
) -> dict[str, Any]:
    collected_at_utc = _utc_now()
    resolved_config = config_path if config_path.is_absolute() else REPO_ROOT / config_path
    if not resolved_config.exists():
        return build_typed_blocker_artifact(
            route_id=route_id,
            account_alias=account_alias,
            failure_reason="missing_config",
            blocker_type="market-resource",
            collected_at_utc=collected_at_utc,
            issues=["config_path_missing"],
            config_path=resolved_config,
        )

    try:
        config = CtpAdapterConfig.from_json_file(resolved_config)
    except Exception as exc:
        return build_typed_blocker_artifact(
            route_id=route_id,
            account_alias=account_alias,
            failure_reason="config_load_failed",
            blocker_type="market-resource",
            collected_at_utc=collected_at_utc,
            issues=[type(exc).__name__],
            config_path=resolved_config,
            error_type=type(exc).__name__,
        )

    missing = config.validate()
    if missing:
        return build_typed_blocker_artifact(
            route_id=route_id,
            account_alias=account_alias,
            failure_reason="config_validation_failed",
            blocker_type="market-resource",
            collected_at_utc=collected_at_utc,
            issues=missing,
            config_path=resolved_config,
            config=config,
        )

    try:
        stack = build_ctp_stack(config)
        data_client = stack["data_client"]
        result = data_client.run_live_md_smoke(timeout_seconds=timeout_seconds, flow_path=flow_path)
    except Exception as exc:
        return build_typed_blocker_artifact(
            route_id=route_id,
            account_alias=account_alias,
            failure_reason="market_freshness_probe_exception",
            blocker_type="market-resource",
            collected_at_utc=collected_at_utc,
            issues=[type(exc).__name__],
            config_path=resolved_config,
            config=config,
            error_type=type(exc).__name__,
        )

    return build_market_freshness_artifact(
        config=config,
        config_path=resolved_config,
        route_id=route_id,
        account_alias=account_alias,
        result=result,
        collected_at_utc=_utc_now(),
        freshness_threshold_seconds=freshness_threshold_seconds,
        freshness_basis=freshness_basis,
    )


def _probe_worker(queue: Any, kwargs: dict[str, Any]) -> None:
    try:
        queue.put({"kind": "payload", "payload": run_probe(**kwargs)})
    except Exception as exc:
        queue.put({"kind": "exception", "error_type": type(exc).__name__, "error_message": str(exc)})


def run_probe_with_watchdog(
    *,
    process_timeout_seconds: float,
    **kwargs: Any,
) -> dict[str, Any]:
    ctx = mp.get_context("spawn")
    queue = ctx.Queue(maxsize=1)
    process = ctx.Process(target=_probe_worker, args=(queue, kwargs))
    process.start()
    process.join(max(process_timeout_seconds, 0.0))
    if process.is_alive():
        process.terminate()
        process.join(timeout=5)
        return build_typed_blocker_artifact(
            route_id=kwargs["route_id"],
            account_alias=kwargs["account_alias"],
            failure_reason="market_freshness_probe_timeout",
            blocker_type="market-resource",
            collected_at_utc=_utc_now(),
            issues=["process_timeout"],
            config_path=kwargs.get("config_path"),
        )
    if queue.empty():
        return build_typed_blocker_artifact(
            route_id=kwargs["route_id"],
            account_alias=kwargs["account_alias"],
            failure_reason="market_freshness_probe_no_payload",
            blocker_type="market-resource",
            collected_at_utc=_utc_now(),
            issues=["process_no_payload"],
            config_path=kwargs.get("config_path"),
        )
    result = queue.get()
    if result.get("kind") == "payload":
        return result["payload"]
    return build_typed_blocker_artifact(
        route_id=kwargs["route_id"],
        account_alias=kwargs["account_alias"],
        failure_reason="market_freshness_probe_worker_exception",
        blocker_type="market-resource",
        collected_at_utc=_utc_now(),
        issues=[result.get("error_type") or "worker_exception"],
        config_path=kwargs.get("config_path"),
        error_type=result.get("error_type"),
    )


def _emit_payload(payload: dict[str, Any]) -> None:
    data = (json.dumps(payload, ensure_ascii=False) + "\n").encode("utf-8")
    stdout_buffer = getattr(sys.stdout, "buffer", None)
    if stdout_buffer is not None:
        stdout_buffer.write(data)
        stdout_buffer.flush()
        return
    sys.stdout.write(data.decode(sys.stdout.encoding or "utf-8", errors="backslashreplace"))
    sys.stdout.flush()


def _write_payload(path: Path, payload: dict[str, Any]) -> None:
    resolved = path if path.is_absolute() else REPO_ROOT / path
    resolved.parent.mkdir(parents=True, exist_ok=True)
    resolved.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Emit the P077 CTP market freshness owner artifact or typed blocker.")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--route-id", default="ctp-paper-19053")
    parser.add_argument("--account-alias", default="19053")
    parser.add_argument("--timeout-seconds", type=int, default=20)
    parser.add_argument("--freshness-threshold-seconds", type=int, default=60)
    parser.add_argument("--freshness-basis", choices=("exchange_timestamp", "received_at"), default="exchange_timestamp")
    parser.add_argument("--process-timeout-seconds", type=float, default=None)
    parser.add_argument("--flow-path", type=Path, default=None)
    parser.add_argument("--output-json", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    process_timeout_seconds = (
        args.process_timeout_seconds
        if args.process_timeout_seconds is not None
        else max(float(args.timeout_seconds) + 15.0, 30.0)
    )
    payload = run_probe_with_watchdog(
        config_path=args.config,
        route_id=args.route_id,
        account_alias=args.account_alias,
        timeout_seconds=args.timeout_seconds,
        freshness_threshold_seconds=args.freshness_threshold_seconds,
        freshness_basis=args.freshness_basis,
        flow_path=args.flow_path,
        process_timeout_seconds=process_timeout_seconds,
    )
    if args.output_json is not None:
        _write_payload(args.output_json, payload)
    _emit_payload(payload)
    return 0 if payload.get("success") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
