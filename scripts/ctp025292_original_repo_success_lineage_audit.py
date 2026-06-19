from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.ctp025292_historical_runtime_lineage_audit import audit_historical_runtime_lineage
from scripts.ctp025292_runtime_pack_discover import discover_runtime_packs

BASELINE = "ctp025292-original-repo-success-lineage-audit-v1"
RUNTIME_PACK_ID = "ctp-live-025292-md"
KNOWN_OPENCTP_TTS_DLL_SHA256 = {
    "thostmduserapi_se.dll": "66BACF7E33AD901534DA4B08662F08FC9F6169760B2AA0EEA85766C93FB6501E",
    "thosttraderapi_se.dll": "543ECE8B55C6FBC671B251E8CC0EE909708EE0F3C5ADC4FD2FD542E3B4C8D4E1",
}
REQUIRED_DLLS = tuple(KNOWN_OPENCTP_TTS_DLL_SHA256)
SENSITIVE_CONFIG_KEYS = {"password", "authcode", "auth_code", "appid", "app_id"}


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def _load_json(path: Path) -> dict[str, Any] | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception:
        return None
    return payload if isinstance(payload, dict) else None


def _config_summary(path: Path) -> dict[str, Any]:
    payload = _load_json(path)
    summary: dict[str, Any] = {
        "artifact_ref": str(path),
        "exists": path.exists(),
        "sha256": _file_sha256(path) if path.exists() else None,
        "json_valid": payload is not None,
        "user_id": None,
        "broker_id": None,
        "app_id_present": False,
        "auth_code_present": False,
        "password_present": False,
        "fronts_present": {},
        "native_pack_dir_present": False,
        "native_pack_dir_non_empty": False,
        "native_pack_dir_value_recorded": False,
        "instruments": [],
    }
    if payload is None:
        return summary

    normalized = {str(key).lower(): value for key, value in payload.items()}
    summary["user_id"] = normalized.get("userid")
    summary["broker_id"] = normalized.get("brokerid")
    summary["app_id_present"] = bool(normalized.get("appid"))
    summary["auth_code_present"] = bool(normalized.get("authcode"))
    summary["password_present"] = bool(normalized.get("password"))
    summary["fronts_present"] = {
        "host": bool(normalized.get("host")),
        "pricer": bool(normalized.get("pricer")),
        "md_front": bool(normalized.get("mdfront")),
        "td_front": bool(normalized.get("tdfront")),
    }
    native_pack_dir = normalized.get("nativepackdir")
    summary["native_pack_dir_present"] = "nativepackdir" in normalized
    summary["native_pack_dir_non_empty"] = bool(str(native_pack_dir or "").strip())
    instruments = normalized.get("instruments") or normalized.get("instrument") or []
    if isinstance(instruments, str):
        instruments = [instruments]
    summary["instruments"] = [str(item) for item in instruments] if isinstance(instruments, list) else []
    summary["redaction"] = {
        "sensitive_keys_redacted": sorted(SENSITIVE_CONFIG_KEYS),
        "front_values_recorded": False,
    }
    return summary


def _manifest_values(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.exists():
        return values
    for line in path.read_text(encoding="utf-8-sig", errors="replace").splitlines():
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip()
    return values


def _dll_summary(bin_dir: Path) -> dict[str, dict[str, Any]]:
    summary: dict[str, dict[str, Any]] = {}
    for filename in REQUIRED_DLLS:
        path = bin_dir / filename
        summary[filename] = {
            "exists": path.exists(),
            "sha256": _file_sha256(path) if path.exists() else None,
            "length": path.stat().st_size if path.exists() else None,
            "known_openctp_tts": (
                path.exists()
                and _file_sha256(path) == KNOWN_OPENCTP_TTS_DLL_SHA256[filename]
            ),
        }
    return summary


def _vendor_runtime_summary(original_root: Path) -> dict[str, Any]:
    vendor_bin = original_root / "vendor" / "ctp" / "bin"
    manifest_path = vendor_bin / "_synced_from.txt"
    manifest = _manifest_values(manifest_path)
    dlls = _dll_summary(vendor_bin)
    return {
        "bin_ref": str(vendor_bin),
        "manifest_ref": str(manifest_path),
        "manifest_exists": manifest_path.exists(),
        "manifest_sha256": _file_sha256(manifest_path) if manifest_path.exists() else None,
        "manifest": manifest,
        "dlls": dlls,
        "all_required_dlls_present": all(item["exists"] for item in dlls.values()),
        "all_required_dlls_known_openctp_tts": all(item["known_openctp_tts"] for item in dlls.values()),
    }


def audit_original_repo_success_lineage(original_root: Path) -> dict[str, Any]:
    original_root = original_root.resolve()
    current_config = original_root / "cfgs" / "local" / "ctp.live.025292.local.json"
    historical_config = original_root / "cfgs" / "local" / "ctp.live.025292.rb2610.10675.json"
    config = _config_summary(current_config)
    vendor = _vendor_runtime_summary(original_root)
    historical = audit_historical_runtime_lineage(
        [original_root / "output", original_root / "docs"],
        historical_config=historical_config,
    )
    discovery = discover_runtime_packs(
        [
            original_root / "vendor" / "ctp" / "bin",
            original_root / "output",
            Path("D:/wt/main/.venv/Lib/site-packages/vnpy_ctp/api"),
        ]
    )

    issues: list[str] = []
    if not config["exists"]:
        issues.append("original_current_025292_config_missing")
    if config["user_id"] != "025292":
        issues.append("original_current_config_user_id_not_025292")
    if not config["native_pack_dir_non_empty"]:
        issues.append("original_current_config_native_pack_dir_empty")
    if vendor["manifest"].get("ctp_api", "").lower().find("openctp") >= 0:
        issues.append("original_vendor_manifest_points_openctp")
    if vendor["all_required_dlls_known_openctp_tts"]:
        issues.append("original_vendor_required_dlls_known_openctp_tts")
    if historical["trusted_runtime_hash_ref_count"] == 0:
        issues.append("original_historical_success_runtime_hash_missing")
    if discovery["trusted_candidate_count"] != 1:
        issues.append("operator_trusted_025292_candidate_not_unique")

    success = not issues
    return {
        "baseline": BASELINE,
        "route_scenario": "ctp025292_marketdata_sandbox_paper_simulated_001",
        "runtime_pack_id": RUNTIME_PACK_ID,
        "market_source": "CTP 025292 official market data only",
        "market_data_account_id": "025292",
        "broker_order_submission": False,
        "trading_adapter": "disabled",
        "original_root": str(original_root),
        "success": success,
        "status": "passed" if success else "blocked",
        "blocker_id": None if success else "ctp025292_original_repo_success_lineage_unready",
        "issues": issues,
        "current_config_summary": config,
        "current_vendor_runtime_summary": vendor,
        "historical_audit_summary": {
            "historical_success_ref_count": historical["historical_success_ref_count"],
            "runtime_lineage_ref_count": historical["runtime_lineage_ref_count"],
            "trusted_runtime_hash_ref_count": historical["trusted_runtime_hash_ref_count"],
            "historical_config_exists": historical["historical_config"]["exists"]
            if historical.get("historical_config")
            else None,
            "issues": historical["issues"],
        },
        "runtime_pack_discovery_summary": {
            "candidate_count": discovery["candidate_count"],
            "trusted_candidate_count": discovery["trusted_candidate_count"],
            "candidate_classifications": {
                classification: sum(
                    1 for item in discovery["candidates"] if item.get("classification") == classification
                )
                for classification in sorted(
                    {str(item.get("classification")) for item in discovery["candidates"]}
                )
            },
        },
        "auto_trust_allowed": success,
        "negative_assertions": {
            "did_not_open_trading_channel": True,
            "did_not_submit_broker_order": True,
            "did_not_use_025292_as_trading_account": True,
            "did_not_write_trust_marker": True,
            "did_not_materialize_runtime_pack": True,
            "did_not_write_account_console_source_package": True,
            "did_not_generate_or_consume_paper_request": True,
            "did_not_claim_market_data_ready": True,
        },
        "next_action": (
            "Run ctp025292_runtime_lineage_recover.py --write, then read-only MD smoke."
            if success
            else "Provide or restore exactly one operator_trusted_025292 marker/source package bound to non-OpenCTP/TTS DLL hashes before materializing ctp-live-025292-md."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Audit whether the original nautilus_ctp_adapter repo can auto-restore 025292 runtime lineage."
    )
    parser.add_argument("--original-root", type=Path, default=Path("D:/Nautilus/nautilus_ctp_adapter"))
    parser.add_argument("--output-json", type=Path, default=None)
    args = parser.parse_args()

    payload = audit_original_repo_success_lineage(args.original_root)
    print(json.dumps(payload, ensure_ascii=False))
    if args.output_json is not None:
        args.output_json.parent.mkdir(parents=True, exist_ok=True)
        args.output_json.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return 0 if payload["success"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
