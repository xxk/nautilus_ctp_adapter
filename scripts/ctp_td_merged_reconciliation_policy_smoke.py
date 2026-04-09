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


BASELINE = "td-merged-reconciliation-policy-v1"


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
    parser = argparse.ArgumentParser(description="Run the TD merged reconciliation policy live smoke.")
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--timeout-seconds", type=int, default=20)
    parser.add_argument("--flow-path", type=Path, default=None)
    parser.add_argument("--observation-grace-seconds", type=float, default=1.5)
    parser.add_argument("--completion-grace-seconds", type=float, default=1.0)
    args = parser.parse_args()

    try:
        config = CtpAdapterConfig.from_json_file(args.config)
    except Exception as exc:
        return _emit_exception(stage="config_load", exc=exc)

    try:
        stack = build_ctp_stack(config)
        adapter = stack["truth_merge_adapter"]
        runtime_bridge = stack["runtime_bridge"]

        result = adapter.capture_merged_reconciliation_policy_mainline(
            timeout_seconds=args.timeout_seconds,
            flow_path=args.flow_path,
            observation_grace_seconds=args.observation_grace_seconds,
            completion_grace_seconds=args.completion_grace_seconds,
        )
        events = runtime_bridge.drain_events()
        commands = runtime_bridge.drain_submitted_commands()
    except Exception as exc:
        return _emit_exception(stage="run_smoke", exc=exc)

    failure_reason = None
    if result.snapshot.account.account is None:
        failure_reason = "account_missing"
    elif result.disposition not in {"clear", "manual_review_required", "boundary_required", "evidence_only"}:
        failure_reason = "unexpected_disposition"

    payload = {
        "baseline": BASELINE,
        "success": failure_reason is None,
        "failure_reason": failure_reason,
        "account_id": result.snapshot.order_truth.account_id,
        "disposition": result.disposition,
        "position_count": result.snapshot.positions.position_count,
        "observed_callback_count": result.snapshot.order_truth.observed_callback_count,
        "historical_callback_count": result.snapshot.order_truth.historical_callback_count,
        "current_session_callback_count": result.snapshot.order_truth.current_session_callback_count,
        "available_ratio": result.available_ratio,
        "margin_ratio": result.margin_ratio,
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
        "bridge_command_kinds": [command.kind.value for command in commands],
        "bridge_event_kinds": [event.kind.value for event in events],
    }
    _emit_payload(payload)
    return 0 if failure_reason is None else 1


if __name__ == "__main__":
    raise SystemExit(main())
