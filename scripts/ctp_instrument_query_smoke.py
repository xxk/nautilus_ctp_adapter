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


BASELINE = "instrument-query-smoke-v1"


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


def _instrument_matches_requested_symbol(*, requested_symbol: str, venue_symbol: str, display_symbol: str) -> bool:
    requested = requested_symbol.strip().lower()
    if not requested:
        return False
    candidates = {
        venue_symbol.strip().lower(),
        display_symbol.strip().lower(),
        display_symbol.split(".", 1)[0].strip().lower(),
    }
    return requested in candidates


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the repository-owned instrument query smoke.")
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--symbol", required=True)
    parser.add_argument("--timeout-seconds", type=int, default=20)
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
            default_file_name="instrument_query.json",
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
        bridge = stack["runtime_bridge"]
        result = provider.run_live_instrument_smoke(
            symbol=args.symbol,
            timeout_seconds=args.timeout_seconds,
            flow_path=args.flow_path,
        )
        events = bridge.drain_events()
        commands = bridge.drain_submitted_commands()
    except Exception as exc:
        return _emit_exception(stage="run_smoke", exc=exc)

    matched_symbols = [
        item.display_symbol
        for item in result.instruments
        if _instrument_matches_requested_symbol(
            requested_symbol=args.symbol,
            venue_symbol=item.venue_symbol,
            display_symbol=item.display_symbol,
        )
    ]
    exact_symbol_found = len(matched_symbols) > 0

    failure_reason = None
    if not result.loaded:
        failure_reason = "instrument_query_incomplete"
    elif result.instrument_count == 0:
        failure_reason = "instrument_missing"
    elif not exact_symbol_found:
        failure_reason = "instrument_symbol_mismatch"

    payload = {
        "baseline": BASELINE,
        "success": failure_reason is None,
        "failure_reason": failure_reason,
        "flow_path": None if args.flow_path is None else str(args.flow_path),
        "flow_mode": flow_mode,
        "session_label": session_label,
        "requested_symbol": args.symbol,
        "request_id": result.request_id,
        "loaded": result.loaded,
        "instrument_count": result.instrument_count,
        "symbols": [item.display_symbol for item in result.instruments],
        "matched_symbols": matched_symbols,
        "exact_symbol_found": exact_symbol_found,
        "export": build_export_metadata(
            export_path=export_path,
            evidence_root=args.evidence_root,
            session_label=session_label,
            explicit_path=args.output_json is not None,
        ),
        "bridge_command_kinds": [command.kind.value for command in commands],
        "bridge_event_kinds": [event.kind.value for event in events],
        "first_instrument": None
        if not result.instruments
        else {
            "display_symbol": result.instruments[0].display_symbol,
            "underlying": result.instruments[0].underlying,
            "contract_month": result.instruments[0].contract_month,
            "product_kind": result.instruments[0].product_kind.value,
            "price_tick": result.instruments[0].price_tick,
            "volume_multiple": result.instruments[0].volume_multiple,
        },
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
