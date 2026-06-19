from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]

BASELINE = "ctp025292-runtime-pack-materialize-v1"
RUNTIME_PACK_ID = "ctp-live-025292-md"
REQUIRED_DLLS = ("thostmduserapi_se.dll", "thosttraderapi_se.dll")
KNOWN_OPENCTP_TTS_DLL_SHA256 = {
    "thostmduserapi_se.dll": "66BACF7E33AD901534DA4B08662F08FC9F6169760B2AA0EEA85766C93FB6501E",
    "thosttraderapi_se.dll": "543ECE8B55C6FBC671B251E8CC0EE909708EE0F3C5ADC4FD2FD542E3B4C8D4E1",
}
DEFAULT_TARGET_BIN = REPO_ROOT / "output" / "runtime_packs" / RUNTIME_PACK_ID / "bin"


def _safe_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def _dll_summary(source_bin: Path) -> dict[str, dict[str, Any]]:
    summary: dict[str, dict[str, Any]] = {}
    for filename in REQUIRED_DLLS:
        path = source_bin / filename
        if not path.exists():
            summary[filename] = {
                "exists": False,
                "sha256": None,
                "length": None,
                "path": _safe_path(path),
            }
            continue
        summary[filename] = {
            "exists": True,
            "sha256": _file_sha256(path),
            "length": path.stat().st_size,
            "path": _safe_path(path),
        }
    return summary


def _issues_for_source(
    source_bin: Path,
    dlls: dict[str, dict[str, Any]],
    *,
    source_kind: str,
) -> list[str]:
    issues: list[str] = []
    if not source_bin.exists():
        issues.append("source_bin_missing")
    for filename, metadata in dlls.items():
        if not metadata["exists"]:
            issues.append(f"source_dll_missing:{filename}")
            continue
        if str(metadata["sha256"]).upper() == KNOWN_OPENCTP_TTS_DLL_SHA256[filename]:
            issues.append(f"source_dll_known_openctp_tts:{filename}")
    if source_kind != "operator_trusted_025292":
        issues.append("runtime_source_not_operator_trusted_for_025292")
    return issues


def _write_manifest(target_bin: Path, *, source_bin: Path, dlls: dict[str, dict[str, Any]]) -> Path:
    manifest_path = target_bin / "_synced_from.txt"
    lines = [
        "profile=ctp-live-025292-md",
        "pack_kind=runtime",
        f"runtime_pack_id={RUNTIME_PACK_ID}",
        f"ctp_api={source_bin}",
        "loader_isolation=fresh_worker_process_per_runtime_pack",
    ]
    for filename in REQUIRED_DLLS:
        lines.append(f"{filename}.sha256={dlls[filename]['sha256']}")
    manifest_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return manifest_path


def build_runtime_pack_summary(
    *,
    source_bin: Path,
    target_bin: Path = DEFAULT_TARGET_BIN,
    source_kind: str = "candidate_untrusted",
    materialize: bool = False,
) -> dict[str, Any]:
    source_bin = source_bin if source_bin.is_absolute() else REPO_ROOT / source_bin
    target_bin = target_bin if target_bin.is_absolute() else REPO_ROOT / target_bin
    dlls = _dll_summary(source_bin)
    issues = _issues_for_source(source_bin, dlls, source_kind=source_kind)
    copied: list[str] = []
    manifest_path: Path | None = None

    if materialize and not issues:
        target_bin.mkdir(parents=True, exist_ok=True)
        for filename in REQUIRED_DLLS:
            shutil.copy2(source_bin / filename, target_bin / filename)
            copied.append(filename)
        manifest_path = _write_manifest(target_bin, source_bin=source_bin, dlls=dlls)
    elif materialize and issues:
        issues.append("materialize_rejected_due_to_source_issues")

    payload: dict[str, Any] = {
        "baseline": BASELINE,
        "runtime_pack_id": RUNTIME_PACK_ID,
        "route_scenario": "ctp025292_marketdata_sandbox_paper_simulated_001",
        "market_source": "CTP 025292 official market data only",
        "market_data_account_id": "025292",
        "broker_order_submission": False,
        "trading_adapter": "disabled",
        "source_kind": source_kind,
        "materialize_requested": materialize,
        "success": not issues and materialize,
        "status": "materialized" if materialize and not issues else "blocked",
        "blocker_id": None if materialize and not issues else "ctp025292_runtime_pack_source_unready",
        "issues": issues,
        "paths": {
            "source_bin": _safe_path(source_bin),
            "target_bin": _safe_path(target_bin),
            "manifest": _safe_path(manifest_path) if manifest_path is not None else None,
        },
        "source_dlls": dlls,
        "copied": copied,
        "loader_isolation": {
            "required_mode": "fresh_worker_process_per_runtime_pack",
            "reason": "Windows caches same-name DLLs by module name; 025292 must not reuse a shared 19053/OpenCTP vendor/bin process.",
        },
        "negative_assertions": {
            "did_not_open_trading_channel": True,
            "did_not_submit_broker_order": True,
            "did_not_generate_or_consume_paper_request": True,
            "did_not_claim_market_data_ready": True,
        },
    }
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Materialize a route-bound CTP 025292 runtime pack only from an explicit trusted source directory."
    )
    parser.add_argument("--source-bin", type=Path, required=True)
    parser.add_argument("--target-bin", type=Path, default=DEFAULT_TARGET_BIN)
    parser.add_argument(
        "--source-kind",
        choices=("candidate_untrusted", "operator_trusted_025292"),
        default="candidate_untrusted",
    )
    parser.add_argument("--materialize", action="store_true")
    parser.add_argument("--output-json", type=Path, default=None)
    args = parser.parse_args()

    payload = build_runtime_pack_summary(
        source_bin=args.source_bin,
        target_bin=args.target_bin,
        source_kind=args.source_kind,
        materialize=args.materialize,
    )
    print(json.dumps(payload, ensure_ascii=False))

    if args.output_json is not None:
        output_path = args.output_json if args.output_json.is_absolute() else REPO_ROOT / args.output_json
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    return 0 if payload["success"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
