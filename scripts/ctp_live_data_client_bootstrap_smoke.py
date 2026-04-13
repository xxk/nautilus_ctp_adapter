from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
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


BASELINE = "live-data-client-bootstrap-smoke-v1"


def _emit_payload(payload: dict[str, object]) -> None:
    print(json.dumps(payload, ensure_ascii=False))


def _emit_exception(*, stage: str, exc: Exception) -> int:
    _emit_payload(
        {
            "baseline": BASELINE,
            "success": False,
            "failure_reason": "exception",
            "error_stage": stage,
            "error_type": type(exc).__name__,
            "error_message": str(exc),
        }
    )
    return 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Bootstrap the Nautilus CTP live data client from a live instrument query.")
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--symbol", required=True)
    parser.add_argument("--instrument-timeout-seconds", type=int, default=20)
    parser.add_argument("--flow-path", type=Path, default=None)
    parser.add_argument("--session-label")
    parser.add_argument("--evidence-root", type=Path)
    parser.add_argument("--output-json", type=Path)
    args = parser.parse_args()

    try:
        flow_mode = resolve_flow_mode(flow_path=args.flow_path)
        session_label = resolve_session_label(session_label=args.session_label, flow_path=args.flow_path)
        export_path = resolve_export_path(
            output_json=args.output_json,
            evidence_root=args.evidence_root,
            session_label=session_label,
            default_file_name="live_data_client_bootstrap.json",
        )
    except Exception as exc:
        return _emit_exception(stage="argument_validation", exc=exc)

    try:
        config = CtpAdapterConfig.from_json_file(args.config)
    except Exception as exc:
        return _emit_exception(stage="config_load", exc=exc)

    try:
        stack = build_ctp_stack(config)
        provider = stack["instrument_provider"]
        data_client = stack["data_client"]
        runtime_bridge = stack["runtime_bridge"]

        load_result = provider.run_live_instrument_smoke(
            symbol=args.symbol,
            timeout_seconds=args.instrument_timeout_seconds,
            flow_path=args.flow_path,
        )

        runtime_bridge.drain_submitted_commands()
        instrument_events = runtime_bridge.drain_events()

        bootstrap_result = data_client.bootstrap_live_data_client_mainline(load_result)
        bootstrap_commands = runtime_bridge.drain_submitted_commands()
    except Exception as exc:
        return _emit_exception(stage="run_smoke", exc=exc)

    failure_reason = None
    if not load_result.loaded:
        failure_reason = "instrument_not_loaded"
    elif load_result.instrument_count <= 0:
        failure_reason = "instrument_missing"
    elif args.symbol not in bootstrap_result.selected_symbols:
        failure_reason = "symbol_not_selected"
    elif not bootstrap_result.bootstrap_state.started:
        failure_reason = "bootstrap_not_started"
    elif bootstrap_result.bootstrap_state.connect_request_id is None:
        failure_reason = "connect_request_missing"
    elif not bootstrap_result.bootstrap_state.subscribe_request_ids:
        failure_reason = "subscribe_requests_missing"

    payload = {
        "baseline": BASELINE,
        "success": failure_reason is None,
        "failure_reason": failure_reason,
        "flow_mode": flow_mode,
        "session_label": session_label,
        "flow_path": None if args.flow_path is None else str(args.flow_path),
        "requested_symbol": args.symbol,
        "instrument_request_id": load_result.request_id,
        "instrument_loaded": load_result.loaded,
        "instrument_count": load_result.instrument_count,
        "instrument_symbols": [instrument.display_symbol for instrument in load_result.instruments[:5]],
        "selected_symbols": list(bootstrap_result.selected_symbols),
        "bootstrap_started": bootstrap_result.bootstrap_state.started,
        "connect_request_id": bootstrap_result.bootstrap_state.connect_request_id,
        "subscribe_request_ids": list(bootstrap_result.bootstrap_state.subscribe_request_ids),
        "bootstrap_command_kinds": [command.kind.value for command in bootstrap_commands],
        "bootstrap_subscribe_symbols": [
            command.venue_symbol
            for command in bootstrap_commands
            if command.venue_symbol
        ],
        "instrument_event_kinds_tail": [event.kind.value for event in instrument_events[-5:]],
        "export": build_export_metadata(
            export_path=export_path,
            evidence_root=args.evidence_root,
            session_label=session_label,
            explicit_path=args.output_json is not None,
        ),
    }

    if export_path is not None:
        try:
            write_json_payload(path=export_path, payload=payload)
        except Exception as exc:
            return _emit_exception(stage="export_payload", exc=exc)

    _emit_payload(payload)
    return 0 if failure_reason is None else 1


if __name__ == "__main__":
    raise SystemExit(main())
