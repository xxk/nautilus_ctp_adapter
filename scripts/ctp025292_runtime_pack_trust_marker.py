from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

RUNTIME_PACK_ID = "ctp-live-025292-md"
TRUST_MARKER = "_ctp025292_runtime_pack.json"
REQUIRED_DLLS = ("thostmduserapi_se.dll", "thosttraderapi_se.dll")
KNOWN_OPENCTP_TTS_DLL_SHA256 = {
    "thostmduserapi_se.dll": "66BACF7E33AD901534DA4B08662F08FC9F6169760B2AA0EEA85766C93FB6501E",
    "thosttraderapi_se.dll": "543ECE8B55C6FBC671B251E8CC0EE909708EE0F3C5ADC4FD2FD542E3B4C8D4E1",
}


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def _dlls(source_bin: Path) -> dict[str, dict[str, Any]]:
    payload: dict[str, dict[str, Any]] = {}
    for filename in REQUIRED_DLLS:
        path = source_bin / filename
        if not path.exists():
            payload[filename] = {
                "exists": False,
                "sha256": None,
                "length": None,
            }
            continue
        payload[filename] = {
            "exists": True,
            "sha256": _file_sha256(path),
            "length": path.stat().st_size,
        }
    return payload


def _issues(dlls: dict[str, dict[str, Any]]) -> list[str]:
    issues: list[str] = []
    for filename, metadata in dlls.items():
        if not metadata["exists"]:
            issues.append(f"source_dll_missing:{filename}")
            continue
        if str(metadata["sha256"]).upper() == KNOWN_OPENCTP_TTS_DLL_SHA256[filename]:
            issues.append(f"source_dll_known_openctp_tts:{filename}")
    return issues


def build_trust_marker_preview(
    *,
    source_bin: Path,
    operator_ack: bool = False,
    write: bool = False,
) -> dict[str, Any]:
    source_bin = source_bin.resolve()
    dll_payload = _dlls(source_bin)
    issues = _issues(dll_payload)
    if not operator_ack:
        issues.append("operator_ack_missing")
    if write and issues:
        issues.append("write_rejected_due_to_marker_issues")

    marker_payload = {
        "schema_version": "ctp025292.runtime_pack_trust_marker.v1",
        "runtime_pack_id": RUNTIME_PACK_ID,
        "source_kind": "operator_trusted_025292",
        "source_bin": str(source_bin),
        "dlls": {
            filename: {"sha256": metadata["sha256"], "length": metadata["length"]}
            for filename, metadata in dll_payload.items()
            if metadata["exists"]
        },
        "loader_isolation": "fresh_worker_process_per_runtime_pack",
        "negative_assertions": {
            "not_broker_order_permission": True,
            "not_market_data_ready_evidence": True,
            "not_live_or_paper_ready_evidence": True,
        },
    }

    marker_path = source_bin / TRUST_MARKER
    wrote_marker = False
    if write and not issues:
        marker_path.write_text(json.dumps(marker_payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        wrote_marker = True

    return {
        "baseline": "ctp025292-runtime-pack-trust-marker-v1",
        "runtime_pack_id": RUNTIME_PACK_ID,
        "route_scenario": "ctp025292_marketdata_sandbox_paper_simulated_001",
        "market_source": "CTP 025292 official market data only",
        "market_data_account_id": "025292",
        "broker_order_submission": False,
        "trading_adapter": "disabled",
        "source_bin": str(source_bin),
        "operator_ack": operator_ack,
        "write_requested": write,
        "success": wrote_marker,
        "status": "marker_written" if wrote_marker else "blocked",
        "blocker_id": None if wrote_marker else "ctp025292_runtime_pack_trust_marker_unready",
        "issues": issues,
        "marker_path": str(marker_path),
        "marker_preview": marker_payload,
        "negative_assertions": {
            "did_not_open_trading_channel": True,
            "did_not_submit_broker_order": True,
            "did_not_generate_or_consume_paper_request": True,
            "did_not_claim_market_data_ready": True,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Preview or write a trust marker for an operator-approved CTP 025292 DLL source directory."
    )
    parser.add_argument("--source-bin", type=Path, required=True)
    parser.add_argument("--operator-ack", action="store_true")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--output-json", type=Path, default=None)
    args = parser.parse_args()

    payload = build_trust_marker_preview(
        source_bin=args.source_bin,
        operator_ack=args.operator_ack,
        write=args.write,
    )
    print(json.dumps(payload, ensure_ascii=False))

    if args.output_json is not None:
        args.output_json.parent.mkdir(parents=True, exist_ok=True)
        args.output_json.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    return 0 if payload["success"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
