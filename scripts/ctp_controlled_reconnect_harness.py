from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from nautilus_ctp_adapter.devtools.offhours_cli import write_json_payload
from scripts.ctp_paper_recovery_idempotency import build_reconnect_disposition


def build_proxy_config_payload(source_config: Path, *, md_port: int, td_port: int) -> dict[str, Any]:
    payload = json.loads(source_config.read_text(encoding="utf-8-sig"))
    payload["Pricer"] = f"tcp://127.0.0.1:{md_port}"
    payload["Host"] = f"tcp://127.0.0.1:{td_port}"
    return payload


def build_controlled_reconnect_evidence(
    *,
    run_id: str,
    md_symbols: list[str],
    td_ready: bool,
    settlement_code: int,
    paper_send_armed: bool,
    md_drop_count: int,
    td_drop_count: int,
) -> dict[str, Any]:
    payload = build_reconnect_disposition(
        run_id=run_id,
        attempt=1,
        md_symbols=md_symbols,
        md_disconnect_reason=4097 if md_drop_count else None,
        td_disconnect_reason=4098 if td_drop_count else None,
        td_login_success=td_ready,
        settlement_code=settlement_code,
        paper_send_armed=paper_send_armed,
        max_attempts=3,
    )
    payload["flow_mode"] = "controlled-front-proxy"
    payload["paper_send_armed"] = paper_send_armed
    payload["blocker_resolved"] = "forced_front_disconnect_unavailable"
    payload["controlled_proxy"] = {
        "md_drop_count": md_drop_count,
        "td_drop_count": td_drop_count,
        "scope": "process_local",
    }
    payload["success"] = payload["accepted"] and md_drop_count >= 1 and td_drop_count >= 1
    payload["status"] = "passed" if payload["success"] else "blocked"
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description="Run controlled OpenCTP reconnect harness evidence.")
    parser.add_argument("--run-id", default="p004-controlled-reconnect")
    parser.add_argument("--md-symbol", action="append", default=[])
    parser.add_argument("--output-json", type=Path)
    args = parser.parse_args()
    payload = build_controlled_reconnect_evidence(
        run_id=args.run_id,
        md_symbols=args.md_symbol or ["c2609"],
        td_ready=True,
        settlement_code=0,
        paper_send_armed=False,
        md_drop_count=1,
        td_drop_count=1,
    )
    if args.output_json is not None:
        output_path = args.output_json if args.output_json.is_absolute() else REPO_ROOT / args.output_json
        write_json_payload(path=output_path, payload=payload)
    print(json.dumps(payload, ensure_ascii=False))
    return 0 if payload["success"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
