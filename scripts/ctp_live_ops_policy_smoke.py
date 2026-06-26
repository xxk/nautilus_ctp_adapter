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


BASELINE = "live-ops-policy-v1"


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
    parser = argparse.ArgumentParser(description="Run the live ops policy baseline smoke.")
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--timeout-seconds", type=int, default=20)
    parser.add_argument("--observation-grace-seconds", type=float, default=1.5)
    parser.add_argument("--completion-grace-seconds", type=float, default=1.0)
    parser.add_argument("--session-label")
    parser.add_argument("--evidence-root", type=Path)
    parser.add_argument("--output-json", type=Path)
    parser.add_argument("--td-shared-flow-path", type=Path, default=None)
    parser.add_argument("--td-isolated-flow-path", type=Path, default=None)
    parser.add_argument("--md-flow-path", type=Path, default=None)
    parser.add_argument("--td-flow-path", type=Path, default=None)
    parser.add_argument("--query-flow-path", type=Path, default=None)
    args = parser.parse_args()

    effective_flow_path = (
        args.td_isolated_flow_path
        or args.md_flow_path
        or args.td_flow_path
        or args.query_flow_path
        or args.td_shared_flow_path
    )

    try:
        flow_mode = resolve_flow_mode(flow_path=effective_flow_path)
        session_label = resolve_session_label(session_label=args.session_label, flow_path=effective_flow_path)
        export_path = resolve_export_path(
            output_json=args.output_json,
            evidence_root=args.evidence_root,
            session_label=session_label,
            default_file_name="live_ops_policy.json",
        )
    except Exception as exc:
        return _emit_exception(stage="argument_validation", exc=exc)

    try:
        config = CtpAdapterConfig.from_json_file(args.config)
    except Exception as exc:
        return _emit_exception(stage="config_load", exc=exc)

    try:
        stack = build_ctp_stack(config)
        adapter = stack["live_ops_snapshot_adapter"]
        runtime_bridge = stack["runtime_bridge"]

        result = adapter.capture_live_ops_policy_mainline(
            timeout_seconds=args.timeout_seconds,
            td_shared_flow_path=args.td_shared_flow_path,
            td_isolated_flow_path=args.td_isolated_flow_path,
            md_flow_path=args.md_flow_path,
            td_flow_path=args.td_flow_path,
            query_flow_path=args.query_flow_path,
            observation_grace_seconds=args.observation_grace_seconds,
            completion_grace_seconds=args.completion_grace_seconds,
        )
        events = runtime_bridge.drain_events()
        commands = runtime_bridge.drain_submitted_commands()
    except Exception as exc:
        return _emit_exception(stage="run_smoke", exc=exc)

    failure_reason = None
    if result.summary.account_id is None:
        failure_reason = "account_id_missing"
    elif result.summary.symbol is None:
        failure_reason = "symbol_missing"
    elif result.disposition not in {
        "clear",
        "manual_review_required",
        "rebuild_required",
        "restore_required",
        "boundary_required",
        "evidence_only",
    }:
        failure_reason = "unexpected_disposition"

    payload = {
        "baseline": BASELINE,
        "success": failure_reason is None,
        "failure_reason": failure_reason,
        "flow_mode": flow_mode,
        "session_label": session_label,
        "account_id": result.summary.account_id,
        "symbol": result.summary.symbol,
        "disposition": result.disposition,
        "requires_manual_review": result.disposition == "manual_review_required",
        "finding_count": len(result.findings),
        "startup_disposition": result.summary.startup_disposition,
        "md_disposition": result.summary.md_disposition,
        "td_disposition": result.summary.td_disposition,
        "reconciliation_disposition": result.summary.reconciliation_disposition,
        "manual_review_codes": list(result.summary.manual_review_codes),
        "rebuild_required_codes": list(result.summary.rebuild_required_codes),
        "restore_required_codes": list(result.summary.restore_required_codes),
        "boundary_codes": list(result.summary.boundary_codes),
        "evidence_only_codes": list(result.summary.evidence_only_codes),
        "findings": [
            {
                "code": finding.code,
                "severity": finding.severity,
                "action": finding.action,
                "metric": finding.metric,
                "metric_value": finding.metric_value,
                "threshold": finding.threshold,
                "message": finding.message,
            }
            for finding in result.findings
        ],
        "export": build_export_metadata(
            export_path=export_path,
            evidence_root=args.evidence_root,
            session_label=session_label,
            explicit_path=args.output_json is not None,
        ),
        "bridge_command_kinds": [command.kind.value for command in commands],
        "bridge_event_kinds": [event.kind.value for event in events],
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

