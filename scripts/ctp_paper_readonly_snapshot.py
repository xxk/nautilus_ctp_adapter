from __future__ import annotations

import argparse
import json
import multiprocessing as mp
import queue as queue_mod
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
from nautilus_ctp_adapter.diagnostics.paper_readonly_snapshot import (
    BASELINE,
    DEFAULT_CONFIG,
    build_config_only_snapshot,
    build_connect_process_blocker_snapshot,
    build_exception_payload,
    populate_connected_snapshot_payload,
)
from nautilus_ctp_adapter.devtools.offhours_cli import (
    build_export_metadata,
    resolve_export_path,
    resolve_flow_mode,
    resolve_session_label,
    write_json_payload,
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

    return populate_connected_snapshot_payload(
        payload=payload,
        config=config,
        snapshot=snapshot,
        instrument_result=instrument_result,
        order_trade=order_trade,
        commands=commands,
        events=events,
    )


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
    result_queue = ctx.Queue(maxsize=1)
    process = ctx.Process(
        target=_connected_snapshot_worker,
        args=(
            result_queue,
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
            process_exitcode=process.exitcode,
        )

    try:
        result = result_queue.get(timeout=2.0)
    except queue_mod.Empty:
        result = None

    if result is not None:
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
            process_exitcode=process.exitcode,
        )

    return build_connect_process_blocker_snapshot(
        config=config,
        config_path=config_path,
        run_id=run_id,
        flow_path=flow_path,
        session_label=session_label,
        process_timeout_seconds=process_timeout_seconds,
        failure_reason="connect_process_no_payload",
        process_exitcode=process.exitcode,
    )


def _emit_exception(*, stage: str, exc: Exception) -> int:
    _emit_payload(build_exception_payload(stage=stage, exc=exc))
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
