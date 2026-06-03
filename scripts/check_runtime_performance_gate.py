from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def _ensure_src_path() -> None:
    src = REPO_ROOT / "src"
    if str(src) not in sys.path:
        sys.path.insert(0, str(src))


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the repo-local P001 runtime bridge performance gate.",
    )
    parser.add_argument("--events", type=int, default=5000, help="Number of synthetic runtime events to drain.")
    parser.add_argument("--limit", type=int, default=1000, help="Batch drain limit.")
    parser.add_argument(
        "--min-events-per-sec",
        type=float,
        default=1000.0,
        help="Minimum accepted synthetic events drained per second.",
    )
    parser.add_argument(
        "--output-json",
        type=Path,
        default=REPO_ROOT
        / "output"
        / "reports"
        / "p001-ADR001-native-first-runtime-rollout"
        / "runtime_performance_gate.json",
        help="JSON report path.",
    )
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    if args.events <= 0:
        raise SystemExit("--events must be > 0")
    if args.limit <= 0:
        raise SystemExit("--limit must be > 0")
    if args.min_events_per_sec <= 0:
        raise SystemExit("--min-events-per-sec must be > 0")

    _ensure_src_path()

    from nautilus_ctp_adapter.runtime import CtpRuntimeBridge, CtpRuntimeEvent, CtpRuntimeEventKind

    bridge = CtpRuntimeBridge()
    for index in range(args.events):
        bridge.push_event(
            CtpRuntimeEvent(
                kind=CtpRuntimeEventKind.TICK,
                venue_symbol=f"rb{index % 12:04d}",
                exchange_id="SHFE",
                payload={"last": str(index)},
            )
        )

    drained = 0
    started = time.perf_counter()
    while True:
        batch = bridge.drain_events(args.limit)
        if not batch:
            break
        drained += len(batch)
    elapsed_sec = max(time.perf_counter() - started, 1e-9)
    events_per_sec = drained / elapsed_sec
    passed = drained == args.events and events_per_sec >= args.min_events_per_sec

    report = {
        "proposal_id": "p001-ADR001-native-first-runtime-rollout",
        "gate": "runtime_bridge_batch_drain",
        "events": args.events,
        "limit": args.limit,
        "drained": drained,
        "elapsed_sec": elapsed_sec,
        "events_per_sec": events_per_sec,
        "min_events_per_sec": args.min_events_per_sec,
        "passed": passed,
        "daemon_trigger_policy": "daemon proposal remains forbidden unless this gate is replaced by a live/formal benchmark showing the in-process batch bridge is the bottleneck",
    }

    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")

    status = "RUNTIME_PERFORMANCE_GATE_OK" if passed else "RUNTIME_PERFORMANCE_GATE_FAIL"
    print(
        f"{status}: drained={drained}/{args.events} "
        f"events_per_sec={events_per_sec:.2f} threshold={args.min_events_per_sec:.2f} "
        f"report={args.output_json}"
    )
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
