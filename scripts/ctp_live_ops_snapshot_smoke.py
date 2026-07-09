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
from nautilus_ctp_adapter.diagnostics.evidence_payloads import (
    LIVE_OPS_SNAPSHOT_BASELINE,
    build_live_ops_snapshot_payload,
)
from nautilus_ctp_adapter.devtools.offhours_cli import (
    build_export_metadata,
    resolve_export_path,
    resolve_flow_mode,
    resolve_session_label,
    write_json_payload,
)


BASELINE = LIVE_OPS_SNAPSHOT_BASELINE


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
    parser = argparse.ArgumentParser(description="Run the live ops snapshot baseline smoke.")
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
            default_file_name="live_ops_snapshot.json",
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

        snapshot = adapter.capture_live_ops_snapshot_mainline(
            timeout_seconds=args.timeout_seconds,
            td_shared_flow_path=args.td_shared_flow_path,
            td_isolated_flow_path=args.td_isolated_flow_path,
            md_flow_path=args.md_flow_path,
            td_flow_path=args.td_flow_path,
            query_flow_path=args.query_flow_path,
            observation_grace_seconds=args.observation_grace_seconds,
            completion_grace_seconds=args.completion_grace_seconds,
        )
        summary = adapter.summarize_live_ops_snapshot(snapshot)
        policy_result = adapter.evaluate_live_ops_policy(summary)
        events = runtime_bridge.drain_events()
        commands = runtime_bridge.drain_submitted_commands()
    except Exception as exc:
        return _emit_exception(stage="run_smoke", exc=exc)

    payload = build_live_ops_snapshot_payload(
        snapshot=snapshot,
        summary=summary,
        policy_result=policy_result,
        flow_mode=flow_mode,
        session_label=session_label,
        export=build_export_metadata(
            export_path=export_path,
            evidence_root=args.evidence_root,
            session_label=session_label,
            explicit_path=args.output_json is not None,
        ),
        bridge_commands=commands,
        bridge_events=events,
    )

    if export_path is not None:
        try:
            write_json_payload(path=export_path, payload=payload)
        except Exception as exc:
            return _emit_exception(stage="export_payload", exc=exc)

    _emit_payload(payload)

    return 0 if payload["failure_reason"] is None else 1


if __name__ == "__main__":
    raise SystemExit(main())
