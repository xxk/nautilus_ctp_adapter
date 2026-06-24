from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from nautilus_ctp_adapter.diagnostics.p077_market_freshness import (  # noqa: E402
    BASELINE,
    DEFAULT_CONFIG,
    DEFAULT_OUTPUT,
    FORBIDDEN_TRUTH_SOURCES,
    OWNER,
    UPSTREAM_BLOCKER_ID,
    attach_checksum,
    build_market_freshness_artifact,
    build_typed_blocker_artifact,
    exchange_timestamp_warnings,
    market_freshness_issues,
    redacted_config_identity,
    run_probe,
    run_probe_with_watchdog,
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


__all__ = [
    "BASELINE",
    "DEFAULT_CONFIG",
    "DEFAULT_OUTPUT",
    "FORBIDDEN_TRUTH_SOURCES",
    "OWNER",
    "UPSTREAM_BLOCKER_ID",
    "attach_checksum",
    "build_market_freshness_artifact",
    "build_typed_blocker_artifact",
    "exchange_timestamp_warnings",
    "market_freshness_issues",
    "redacted_config_identity",
    "run_probe",
    "run_probe_with_watchdog",
]


if __name__ == "__main__":
    raise SystemExit(main())
