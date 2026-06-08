from __future__ import annotations

import argparse
import hashlib
import json
import multiprocessing as mp
import sys
import time
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from nautilus_ctp_adapter.adapters.ctp.config import CtpAdapterConfig
from nautilus_ctp_adapter.adapters.ctp.factory import build_ctp_stack
from nautilus_ctp_adapter.devtools.offhours_cli import (
    build_export_metadata,
    resolve_export_path,
    resolve_flow_mode,
    resolve_session_label,
    write_json_payload,
)

from scripts.ctp_paper_session_preflight import paper_config_issues


BASELINE = "ctp-paper-readonly-snapshot-v1"
DEFAULT_CONFIG = REPO_ROOT / "cfgs" / "local" / "ctp.openctp.tts.7x24.local.json"
OPENCTP_TTS_7X24_PROFILE = "openctp-tts-7x24-simulation"


def _fingerprint(value: str | None) -> str:
    text = str(value or "").strip()
    if not text:
        return ""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]


def _path_text(path: Path | None) -> str | None:
    return None if path is None else str(path)


def _emit_payload(payload: dict[str, Any]) -> None:
    print(json.dumps(payload, ensure_ascii=False))


def snapshot_schema_metadata(*, run_id: str, flow_path: Path | None, session_label: str) -> dict[str, Any]:
    return {
        "run_id": run_id,
        "flow_path": _path_text(flow_path),
        "session_label": session_label,
        "account_profile": OPENCTP_TTS_7X24_PROFILE,
        "evidence_class": "openctp-tts-7x24-simulation",
        "reconciliation_role": "pre_or_post_order_snapshot",
        "schema_version": BASELINE,
    }


def redacted_account_identity(account_id: str | None) -> dict[str, Any]:
    return {
        "account_id_present": bool(account_id),
        "account_id_fingerprint": _fingerprint(account_id),
    }


def classify_positions_disposition(
    *, query_code: int, completed: bool, timed_out: bool, no_positions: bool
) -> dict[str, Any]:
    if query_code != 0:
        return {
            "status": "blocked",
            "disposition": "query_failed",
            "failure_reason": "positions_query_failed",
        }
    if timed_out:
        return {
            "status": "blocked",
            "disposition": "timeout",
            "failure_reason": "positions_timed_out",
        }
    if not completed:
        return {
            "status": "blocked",
            "disposition": "incomplete",
            "failure_reason": "positions_incomplete",
        }
    if no_positions:
        return {
            "status": "passed",
            "disposition": "valid_empty",
            "failure_reason": None,
        }
    return {
        "status": "passed",
        "disposition": "positions_present",
        "failure_reason": None,
    }


def classify_account_disposition(
    *, query_code: int, completed: bool, timed_out: bool, account_present: bool
) -> dict[str, Any]:
    if query_code != 0:
        return {
            "status": "blocked",
            "disposition": "query_failed",
            "failure_reason": "account_query_failed",
        }
    if timed_out:
        return {
            "status": "blocked",
            "disposition": "timeout",
            "failure_reason": "account_timed_out",
        }
    if not completed:
        return {
            "status": "blocked",
            "disposition": "incomplete",
            "failure_reason": "account_incomplete",
        }
    if not account_present:
        return {
            "status": "blocked",
            "disposition": "missing",
            "failure_reason": "account_missing",
        }
    return {
        "status": "passed",
        "disposition": "account_present",
        "failure_reason": None,
    }


def position_contract_issues(position: Any) -> list[str]:
    issues: list[str] = []
    if str(position.direction or "").strip().lower() not in {"long", "short", "buy", "sell", "2", "3"}:
        issues.append("direction")
    for field_name in ("position_qty", "yd_position_qty", "td_position_qty"):
        value = getattr(position, field_name)
        if value is None or value < 0:
            issues.append(field_name)
    return issues


def instrument_contract_issues(instrument: Any) -> list[str]:
    issues: list[str] = []
    if not getattr(instrument, "display_symbol", ""):
        issues.append("display_symbol")
    if not getattr(instrument, "venue_symbol", ""):
        issues.append("venue_symbol")
    if not getattr(instrument, "exchange_id", ""):
        issues.append("exchange_id")
    if getattr(instrument, "price_tick", None) in {None, 0}:
        issues.append("price_tick")
    if getattr(instrument, "volume_multiple", None) in {None, 0}:
        issues.append("volume_multiple")
    return issues


def build_config_only_snapshot(
    *,
    config: CtpAdapterConfig,
    config_path: Path,
    run_id: str,
    flow_path: Path | None,
    session_label: str,
) -> dict[str, Any]:
    issues = paper_config_issues(config)
    payload: dict[str, Any] = {
        "baseline": BASELINE,
        "success": not issues,
        "status": "passed" if not issues else "blocked",
        "failure_reason": None if not issues else "config_validation_failed",
        "blocker_type": None if not issues else "paper-resource",
        "action_mode": "request_only",
        "connect_requested": False,
        "schema": snapshot_schema_metadata(
            run_id=run_id,
            flow_path=flow_path,
            session_label=session_label,
        ),
        "config_path": str(config_path),
        "issues": issues,
        "account": {
            "identity": redacted_account_identity(config.user_id),
            "disposition": {
                "status": "not_run",
                "disposition": "request_only",
                "failure_reason": None,
            },
        },
        "positions": {
            "disposition": {
                "status": "not_run",
                "disposition": "request_only",
                "failure_reason": None,
            },
            "position_count": None,
            "no_positions": None,
            "records": [],
        },
        "instruments": {
            "requested_symbols": list(config.instruments),
            "loaded": None,
            "instrument_count": None,
            "records": [],
            "contract_issues": [],
        },
        "order_trade": {
            "disposition": "not_run",
            "observed_order_event_count": None,
            "observed_trade_event_count": None,
        },
    }
    return payload


def build_connected_snapshot(
    *,
    config: CtpAdapterConfig,
    config_path: Path,
    run_id: str,
    flow_path: Path | None,
    session_label: str,
    timeout_seconds: int,
    completion_grace_seconds: float,
    observation_grace_seconds: float,
) -> dict[str, Any]:
    payload = build_config_only_snapshot(
        config=config,
        config_path=config_path,
        run_id=run_id,
        flow_path=flow_path,
        session_label=session_label,
    )
    payload["action_mode"] = "paper_connect"
    payload["connect_requested"] = True
    if payload["issues"]:
        return payload

    try:
        stack = build_ctp_stack(config)
        query_adapter = stack["query_adapter"]
        instrument_provider = stack["instrument_provider"]
        execution_client = stack["execution_client"]
        runtime_bridge = stack["runtime_bridge"]

        snapshot = query_adapter.query_snapshot_mainline(
            timeout_seconds=timeout_seconds,
            flow_path=flow_path,
            completion_grace_seconds=completion_grace_seconds,
        )
        instrument_result = None
        if config.instruments:
            instrument_result = instrument_provider.run_live_instrument_smoke(
                symbol=config.instruments[0],
                timeout_seconds=timeout_seconds,
                flow_path=flow_path,
            )
        order_trade = execution_client.capture_td_order_trade_snapshot_mainline(
            timeout_seconds=timeout_seconds,
            flow_path=flow_path,
            observation_grace_seconds=observation_grace_seconds,
        )
        events = runtime_bridge.drain_events()
        commands = runtime_bridge.drain_submitted_commands()
    except Exception as exc:
        payload["success"] = False
        payload["status"] = "blocked"
        payload["failure_reason"] = "paper_snapshot_exception"
        payload["blocker_type"] = "paper-resource"
        payload["issues"] = [type(exc).__name__]
        payload["exception"] = {"type": type(exc).__name__, "message": str(exc)}
        return payload

    positions_disposition = classify_positions_disposition(
        query_code=snapshot.positions.query_code,
        completed=snapshot.positions.completed,
        timed_out=snapshot.positions.timed_out,
        no_positions=snapshot.positions.no_positions,
    )
    account_present = snapshot.account.account is not None
    account_disposition = classify_account_disposition(
        query_code=snapshot.account.query_code,
        completed=snapshot.account.completed,
        timed_out=snapshot.account.timed_out,
        account_present=account_present,
    )

    position_contract_findings = [
        {"venue_symbol": position.venue_symbol, "issues": position_contract_issues(position)}
        for position in snapshot.positions.positions
        if position_contract_issues(position)
    ]
    instrument_records: list[dict[str, Any]] = []
    instrument_contract_findings: list[dict[str, Any]] = []
    if instrument_result is not None:
        for instrument in instrument_result.instruments:
            instrument_records.append(
                {
                    "venue_symbol": instrument.venue_symbol,
                    "display_symbol": instrument.display_symbol,
                    "exchange_id": instrument.exchange_id,
                    "product_kind": instrument.product_kind.value,
                    "price_tick": instrument.price_tick,
                    "volume_multiple": instrument.volume_multiple,
                }
            )
            issues = instrument_contract_issues(instrument)
            if issues:
                instrument_contract_findings.append(
                    {"display_symbol": instrument.display_symbol, "issues": issues}
                )

    payload["account"] = {
        "identity": redacted_account_identity(
            None if snapshot.account.account is None else snapshot.account.account.account_id
        ),
        "disposition": account_disposition,
        "request_id": snapshot.account.request_id,
        "query_code": snapshot.account.query_code,
        "completed": snapshot.account.completed,
        "timed_out": snapshot.account.timed_out,
        "balance_present": bool(snapshot.account.account and snapshot.account.account.balance is not None),
        "available_present": bool(snapshot.account.account and snapshot.account.account.available is not None),
        "margin_present": bool(snapshot.account.account and snapshot.account.account.margin is not None),
    }
    payload["positions"] = {
        "disposition": positions_disposition,
        "request_id": snapshot.positions.request_id,
        "query_code": snapshot.positions.query_code,
        "completed": snapshot.positions.completed,
        "timed_out": snapshot.positions.timed_out,
        "no_positions": snapshot.positions.no_positions,
        "position_count": snapshot.positions.position_count,
        "contract_issues": position_contract_findings,
        "records": [
            {
                "venue_symbol": position.venue_symbol,
                "exchange_id": position.exchange_id,
                "direction": position.direction,
                "position_qty": position.position_qty,
                "yd_position_qty": position.yd_position_qty,
                "td_position_qty": position.td_position_qty,
                "position_cost": position.position_cost,
            }
            for position in snapshot.positions.positions
        ],
    }
    payload["instruments"] = {
        "requested_symbols": list(config.instruments),
        "loaded": None if instrument_result is None else instrument_result.loaded,
        "instrument_count": None if instrument_result is None else instrument_result.instrument_count,
        "records": instrument_records,
        "contract_issues": instrument_contract_findings,
    }
    payload["order_trade"] = {
        "disposition": order_trade.disposition,
        "observed_order_event_count": order_trade.observed_order_event_count,
        "observed_trade_event_count": order_trade.observed_trade_event_count,
        "no_order_events": order_trade.no_order_events,
        "no_trade_events": order_trade.no_trade_events,
        "historical_order_count": order_trade.historical_order_count,
        "historical_trade_count": order_trade.historical_trade_count,
        "current_session_order_count": order_trade.current_session_order_count,
        "current_session_trade_count": order_trade.current_session_trade_count,
        "manual_review_codes": [
            finding.code for finding in order_trade.findings if finding.action == "manual_review_required"
        ],
        "boundary_codes": [
            finding.code for finding in order_trade.findings if finding.action == "boundary_required"
        ],
        "evidence_only_codes": [
            finding.code for finding in order_trade.findings if finding.action == "evidence_only"
        ],
    }
    payload["bridge_command_kinds"] = [command.kind.value for command in commands]
    payload["bridge_event_kinds"] = [event.kind.value for event in events]

    failure_reasons = [
        item["failure_reason"]
        for item in (positions_disposition, account_disposition)
        if item["failure_reason"]
    ]
    if position_contract_findings:
        failure_reasons.append("position_contract_issues")
    if instrument_contract_findings:
        failure_reasons.append("instrument_contract_issues")
    if instrument_result is not None and not instrument_result.loaded:
        failure_reasons.append("instrument_query_incomplete")

    payload["success"] = not failure_reasons
    payload["status"] = "passed" if not failure_reasons else "blocked"
    payload["failure_reason"] = None if not failure_reasons else failure_reasons[0]
    payload["blocker_type"] = None if not failure_reasons else "paper-resource"
    payload["issues"] = failure_reasons
    return payload


def build_connect_process_blocker_snapshot(
    *,
    config: CtpAdapterConfig,
    config_path: Path,
    run_id: str,
    flow_path: Path | None,
    session_label: str,
    process_timeout_seconds: float,
    failure_reason: str,
    error_stage: str = "paper_connect",
    error_type: str | None = None,
) -> dict[str, Any]:
    payload = build_config_only_snapshot(
        config=config,
        config_path=config_path,
        run_id=run_id,
        flow_path=flow_path,
        session_label=session_label,
    )
    payload.update(
        {
            "success": False,
            "status": "blocked",
            "failure_reason": failure_reason,
            "blocker_type": "paper-resource",
            "action_mode": "paper_connect",
            "connect_requested": True,
            "snapshot_complete": False,
            "process_timeout_seconds": process_timeout_seconds,
            "error_stage": error_stage,
            "error_type": error_type,
            "issues": [failure_reason],
            "completion": {
                "status": "blocked",
                "disposition": failure_reason,
                "failure_reason": failure_reason,
            },
        }
    )
    return payload


def _connected_snapshot_worker(
    queue: Any,
    config: CtpAdapterConfig,
    config_path: Path,
    run_id: str,
    flow_path: Path | None,
    session_label: str,
    timeout_seconds: int,
    completion_grace_seconds: float,
    observation_grace_seconds: float,
) -> None:
    try:
        payload = build_connected_snapshot(
            config=config,
            config_path=config_path,
            run_id=run_id,
            flow_path=flow_path,
            session_label=session_label,
            timeout_seconds=timeout_seconds,
            completion_grace_seconds=completion_grace_seconds,
            observation_grace_seconds=observation_grace_seconds,
        )
    except Exception as exc:
        queue.put(
            {
                "kind": "exception",
                "error_stage": "paper_connect",
                "error_type": type(exc).__name__,
            }
        )
        return
    queue.put({"kind": "payload", "payload": payload})


def build_connected_snapshot_with_watchdog(
    *,
    config: CtpAdapterConfig,
    config_path: Path,
    run_id: str,
    flow_path: Path | None,
    session_label: str,
    timeout_seconds: int,
    completion_grace_seconds: float,
    observation_grace_seconds: float,
    process_timeout_seconds: float,
) -> dict[str, Any]:
    ctx = mp.get_context("spawn")
    queue = ctx.Queue(maxsize=1)
    process = ctx.Process(
        target=_connected_snapshot_worker,
        args=(
            queue,
            config,
            config_path,
            run_id,
            flow_path,
            session_label,
            timeout_seconds,
            completion_grace_seconds,
            observation_grace_seconds,
        ),
    )
    process.start()
    process.join(max(process_timeout_seconds, 0.0))
    if process.is_alive():
        process.terminate()
        process.join(timeout=5)
        return build_connect_process_blocker_snapshot(
            config=config,
            config_path=config_path,
            run_id=run_id,
            flow_path=flow_path,
            session_label=session_label,
            process_timeout_seconds=process_timeout_seconds,
            failure_reason="connect_process_timeout",
        )

    if not queue.empty():
        result = queue.get()
        if result.get("kind") == "payload":
            return result["payload"]
        return build_connect_process_blocker_snapshot(
            config=config,
            config_path=config_path,
            run_id=run_id,
            flow_path=flow_path,
            session_label=session_label,
            process_timeout_seconds=process_timeout_seconds,
            failure_reason="connect_process_exception",
            error_type=result.get("error_type"),
        )

    return build_connect_process_blocker_snapshot(
        config=config,
        config_path=config_path,
        run_id=run_id,
        flow_path=flow_path,
        session_label=session_label,
        process_timeout_seconds=process_timeout_seconds,
        failure_reason="connect_process_no_payload",
    )


def _emit_exception(*, stage: str, exc: Exception) -> int:
    _emit_payload(
        {
            "baseline": BASELINE,
            "success": False,
            "status": "blocked",
            "failure_reason": "exception",
            "blocker_type": "paper-resource",
            "error_stage": stage,
            "error_type": type(exc).__name__,
            "error_message": str(exc),
        }
    )
    return 1


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build a redacted OpenCTP paper read-only account/position/order/trade/instrument snapshot."
    )
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--connect-paper", action="store_true")
    parser.add_argument("--timeout-seconds", type=int, default=20)
    parser.add_argument("--process-timeout-seconds", type=float, default=None)
    parser.add_argument("--completion-grace-seconds", type=float, default=1.0)
    parser.add_argument("--observation-grace-seconds", type=float, default=1.5)
    parser.add_argument("--flow-path", type=Path, default=None)
    parser.add_argument("--session-label")
    parser.add_argument("--evidence-root", type=Path)
    parser.add_argument("--output-json", type=Path)
    args = parser.parse_args()

    try:
        session_label = resolve_session_label(session_label=args.session_label, flow_path=args.flow_path)
        export_path = resolve_export_path(
            output_json=args.output_json,
            evidence_root=args.evidence_root,
            session_label=session_label,
            default_file_name="paper_readonly_snapshot.json",
        )
    except Exception as exc:
        return _emit_exception(stage="argument_validation", exc=exc)

    config_path = args.config if args.config.is_absolute() else REPO_ROOT / args.config
    try:
        config = CtpAdapterConfig.from_json_file(config_path)
    except Exception as exc:
        return _emit_exception(stage="config_load", exc=exc)

    run_id = f"paper-readonly-{int(time.time() * 1000)}"
    if args.connect_paper:
        process_timeout_seconds = (
            float(args.process_timeout_seconds)
            if args.process_timeout_seconds is not None
            else max(float(args.timeout_seconds) + 15.0, 30.0)
        )
        payload = build_connected_snapshot_with_watchdog(
            config=config,
            config_path=config_path,
            run_id=run_id,
            flow_path=args.flow_path,
            session_label=session_label,
            timeout_seconds=args.timeout_seconds,
            completion_grace_seconds=args.completion_grace_seconds,
            observation_grace_seconds=args.observation_grace_seconds,
            process_timeout_seconds=process_timeout_seconds,
        )
    else:
        payload = build_config_only_snapshot(
            config=config,
            config_path=config_path,
            run_id=run_id,
            flow_path=args.flow_path,
            session_label=session_label,
        )
    payload["flow_mode"] = resolve_flow_mode(flow_path=args.flow_path)
    payload["export"] = build_export_metadata(
        export_path=export_path,
        evidence_root=args.evidence_root,
        session_label=session_label,
        explicit_path=args.output_json is not None,
    )

    if export_path is not None:
        try:
            write_json_payload(path=export_path, payload=payload)
        except Exception as exc:
            return _emit_exception(stage="export_payload", exc=exc)

    _emit_payload(payload)
    return 0 if payload["success"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
