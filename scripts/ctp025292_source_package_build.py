from __future__ import annotations

import argparse
import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
ACCOUNT_CONSOLE_ROOT = REPO_ROOT.parent / "nautilus_account_console"

BASELINE = "ctp025292-source-package-build-v1"
RUNTIME_PACK_ID = "ctp-live-025292-md"
REQUIRED_DLLS = ("thostmduserapi_se.dll", "thosttraderapi_se.dll")
KNOWN_OPENCTP_TTS_DLL_SHA256 = {
    "thostmduserapi_se.dll": "66BACF7E33AD901534DA4B08662F08FC9F6169760B2AA0EEA85766C93FB6501E",
    "thosttraderapi_se.dll": "543ECE8B55C6FBC671B251E8CC0EE909708EE0F3C5ADC4FD2FD542E3B4C8D4E1",
}
DEFAULT_RUNTIME_BIN = REPO_ROOT / "output" / "runtime_packs" / RUNTIME_PACK_ID / "bin"
DEFAULT_SOURCE_PACKAGE = (
    ACCOUNT_CONSOLE_ROOT
    / "output"
    / "account_capability"
    / "ctp-live-025292"
    / "source-package.json"
)


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def _read_manifest(runtime_bin: Path) -> dict[str, str]:
    manifest_path = runtime_bin / "_synced_from.txt"
    if not manifest_path.exists():
        return {}
    values: dict[str, str] = {}
    for line in manifest_path.read_text(encoding="utf-8-sig").splitlines():
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip()
    return values


def _dlls(runtime_bin: Path) -> dict[str, dict[str, Any]]:
    payload: dict[str, dict[str, Any]] = {}
    for filename in REQUIRED_DLLS:
        path = runtime_bin / filename
        if not path.exists():
            payload[filename] = {
                "exists": False,
                "sha256": None,
                "length": None,
                "ref": str(path),
            }
            continue
        payload[filename] = {
            "exists": True,
            "sha256": _file_sha256(path),
            "length": path.stat().st_size,
            "ref": str(path),
        }
    return payload


def _issues(runtime_bin: Path, manifest: dict[str, str], dlls: dict[str, dict[str, Any]]) -> list[str]:
    issues: list[str] = []
    if not runtime_bin.exists():
        issues.append("runtime_pack_bin_missing")
    if not (runtime_bin / "_synced_from.txt").exists():
        issues.append("runtime_pack_manifest_missing")
    runtime_pack_id = manifest.get("runtime_pack_id") or manifest.get("pack_id") or ""
    if runtime_pack_id != RUNTIME_PACK_ID:
        issues.append("runtime_pack_id_not_ctp_live_025292_md")
    profile = (manifest.get("profile") or "").lower()
    if profile in {"", "auto"}:
        issues.append("runtime_pack_profile_auto_or_missing")
    if manifest.get("loader_isolation") != "fresh_worker_process_per_runtime_pack":
        issues.append("runtime_pack_loader_isolation_missing")
    for filename, metadata in dlls.items():
        if not metadata["exists"]:
            issues.append(f"runtime_dll_missing:{filename}")
            continue
        digest = str(metadata["sha256"] or "").upper()
        if digest == KNOWN_OPENCTP_TTS_DLL_SHA256[filename]:
            issues.append(f"runtime_dll_known_openctp_tts:{filename}")
        manifest_digest = str(manifest.get(f"{filename}.sha256") or "").upper()
        if not manifest_digest:
            issues.append(f"runtime_manifest_dll_hash_missing:{filename}")
        elif manifest_digest != digest:
            issues.append(f"runtime_manifest_dll_hash_mismatch:{filename}")
    return issues


def _package_payload(
    *,
    runtime_bin: Path,
    manifest: dict[str, str],
    dlls: dict[str, dict[str, Any]],
    observed_at: str,
    lineage_ready: bool,
) -> dict[str, Any]:
    return {
        "schema_version": "ctp025292.source_package.v1",
        "artifact_id": f"source.ctp.live.025292.{observed_at.replace(':', '').replace('-', '')}",
        "account_id": "acct.ctp.live.025292",
        "display_alias": "025292",
        "source_owner": "nautilus_ctp_adapter",
        "source_kind": "ctp_marketdata_runtime_pack",
        "source_mode": "runtime_lineage",
        "account_domain": "stage2_market_data_only",
        "market_source": "CTP 025292 official market data only",
        "market_data_account_id": "025292",
        "broker_order_submission": False,
        "trading_adapter": "disabled",
        "route_scenario": "ctp025292_marketdata_sandbox_paper_simulated_001",
        "runtime_pack": {
            "runtime_pack_id": RUNTIME_PACK_ID,
            "ref": str(runtime_bin),
            "manifest_ref": str(runtime_bin / "_synced_from.txt"),
            "source_ref": manifest.get("ctp_api"),
            "loader_isolation": manifest.get("loader_isolation"),
            "dlls": {
                filename: {
                    "sha256": metadata["sha256"],
                    "length": metadata["length"],
                    "ref": metadata["ref"],
                }
                for filename, metadata in dlls.items()
            },
        },
        "source_health": {
            "state": "runtime_lineage_ready" if lineage_ready else "runtime_lineage_unready_preview",
            "observation_mode": "runtime_pack_manifest",
            "event_stream": "not_implemented",
        },
        "negative_assertions": {
            "not_account_balance_truth": True,
            "not_position_truth": True,
            "not_order_or_fill_truth": True,
            "not_market_data_ready_evidence": True,
            "not_broker_order_permission": True,
            "not_live_or_paper_ready_evidence": True,
        },
        "observed_at": observed_at,
    }


def build_source_package_summary(
    *,
    runtime_bin: Path = DEFAULT_RUNTIME_BIN,
    output_path: Path = DEFAULT_SOURCE_PACKAGE,
    write: bool = False,
    observed_at: str | None = None,
) -> dict[str, Any]:
    runtime_bin = runtime_bin if runtime_bin.is_absolute() else REPO_ROOT / runtime_bin
    output_path = output_path if output_path.is_absolute() else REPO_ROOT / output_path
    observed_at = observed_at or datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    manifest = _read_manifest(runtime_bin)
    dll_payload = _dlls(runtime_bin)
    issues = _issues(runtime_bin, manifest, dll_payload)
    package_payload = _package_payload(
        runtime_bin=runtime_bin,
        manifest=manifest,
        dlls=dll_payload,
        observed_at=observed_at,
        lineage_ready=not issues,
    )
    wrote_package = False
    package_sha256: str | None = None
    if write and not issues:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(package_payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        wrote_package = True
        package_sha256 = _file_sha256(output_path)
    elif write and issues:
        issues.append("write_rejected_due_to_source_package_issues")

    return {
        "baseline": BASELINE,
        "route_scenario": "ctp025292_marketdata_sandbox_paper_simulated_001",
        "runtime_pack_id": RUNTIME_PACK_ID,
        "market_source": "CTP 025292 official market data only",
        "market_data_account_id": "025292",
        "broker_order_submission": False,
        "trading_adapter": "disabled",
        "runtime_bin": str(runtime_bin),
        "output_path": str(output_path),
        "write_requested": write,
        "success": wrote_package,
        "status": "source_package_written" if wrote_package else "blocked",
        "blocker_id": None if wrote_package else "ctp025292_source_package_runtime_pack_unready",
        "issues": issues,
        "runtime_manifest": {
            "exists": (runtime_bin / "_synced_from.txt").exists(),
            "values": manifest,
        },
        "runtime_dlls": dll_payload,
        "source_package_sha256": package_sha256,
        "source_package_preview": package_payload,
        "negative_assertions": {
            "did_not_open_trading_channel": True,
            "did_not_submit_broker_order": True,
            "did_not_generate_or_consume_paper_request": True,
            "did_not_claim_market_data_ready": True,
        },
        "next_action": (
            "Run ctp025292_source_lineage_gate.py against the generated source package."
            if wrote_package
            else "Materialize a trusted ctp-live-025292-md runtime pack first, then rerun this builder with --write."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build the Account Console 025292 source-package only from a trusted materialized runtime pack."
    )
    parser.add_argument("--runtime-bin", type=Path, default=DEFAULT_RUNTIME_BIN)
    parser.add_argument("--output-path", type=Path, default=DEFAULT_SOURCE_PACKAGE)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--observed-at", default=None)
    parser.add_argument("--output-json", type=Path, default=None)
    args = parser.parse_args()

    payload = build_source_package_summary(
        runtime_bin=args.runtime_bin,
        output_path=args.output_path,
        write=args.write,
        observed_at=args.observed_at,
    )
    print(json.dumps(payload, ensure_ascii=False))

    if args.output_json is not None:
        args.output_json.parent.mkdir(parents=True, exist_ok=True)
        args.output_json.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    return 0 if payload["success"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
