from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from nautilus_ctp_adapter.adapters.ctp.config import CtpAdapterConfig


BASELINE = "ctp025292-source-lineage-gate-v1"
DEFAULT_CONFIG = REPO_ROOT / "cfgs" / "local" / "ctp.live.025292.local.json"
DEFAULT_RUNTIME_BIN = REPO_ROOT / "vendor" / "ctp" / "bin"
REQUIRED_CTP_RUNTIME_DLLS = ("thostmduserapi_se.dll", "thosttraderapi_se.dll")
KNOWN_OPENCTP_TTS_DLL_SHA256 = {
    "thostmduserapi_se.dll": "66BACF7E33AD901534DA4B08662F08FC9F6169760B2AA0EEA85766C93FB6501E",
    "thosttraderapi_se.dll": "543ECE8B55C6FBC671B251E8CC0EE909708EE0F3C5ADC4FD2FD542E3B4C8D4E1",
}
DEFAULT_SOURCE_PACKAGE = (
    REPO_ROOT.parent
    / "nautilus_account_console"
    / "output"
    / "account_capability"
    / "ctp-live-025292"
    / "source-package.json"
)


def _fingerprint(value: str) -> str:
    text = str(value or "").strip()
    if not text:
        return ""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]


def _safe_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def _read_json(path: Path) -> dict[str, Any] | None:
    payload = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(payload, dict):
        raise ValueError("JSON payload must be an object")
    return payload


def _read_runtime_manifest(runtime_bin: Path) -> dict[str, str]:
    manifest_path = runtime_bin / "_synced_from.txt"
    if not manifest_path.exists():
        return {}
    manifest: dict[str, str] = {}
    for line in manifest_path.read_text(encoding="utf-8-sig").splitlines():
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        manifest[key.strip()] = value.strip()
    return manifest


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def _runtime_dll_summary(runtime_bin: Path) -> dict[str, dict[str, Any]]:
    summary: dict[str, dict[str, Any]] = {}
    for filename in REQUIRED_CTP_RUNTIME_DLLS:
        path = runtime_bin / filename
        if not path.exists():
            summary[filename] = {
                "exists": False,
                "sha256": None,
                "length": None,
                "path": _safe_path(path),
            }
            continue
        stat = path.stat()
        summary[filename] = {
            "exists": True,
            "sha256": _file_sha256(path),
            "length": stat.st_size,
            "path": _safe_path(path),
        }
    return summary


def _contains_openctp_tts(value: Any) -> bool:
    text = json.dumps(value, ensure_ascii=False).lower()
    return "openctp" in text or "tts-sdk" in text or "tts_6.6.9" in text


def _config_summary(config: CtpAdapterConfig) -> dict[str, Any]:
    return {
        "broker_id": config.broker_id,
        "user_id_present": bool(config.user_id),
        "user_id_fingerprint": _fingerprint(config.user_id),
        "password_present": bool(config.password),
        "auth_code_present": bool(config.auth_code),
        "app_id_present": bool(config.app_id),
        "product_info_present": bool(config.product_info),
        "md_front_present": bool(config.md_front),
        "md_front_fingerprint": _fingerprint(config.md_front),
        "td_front_present": bool(config.td_front),
        "td_front_fingerprint": _fingerprint(config.td_front),
        "provider_id": config.provider_id,
        "instruments": list(config.instruments),
        "native_pack_dir_present": bool(config.native_pack_dir),
        "managed_assembly_dir_present": bool(config.managed_assembly_dir),
    }


def _source_package_issues(payload: dict[str, Any]) -> list[str]:
    issues: list[str] = []
    text = json.dumps(payload, ensure_ascii=False).lower()
    account_fields = [
        payload.get("account_id"),
        payload.get("market_data_account_id"),
        payload.get("ctp_account_id"),
        payload.get("account_uid"),
    ]
    if "025292" not in " ".join(str(item or "") for item in account_fields):
        issues.append("source_package.account_not_025292")
    if "025292" not in text:
        issues.append("source_package.missing_025292_lineage")
    if "ctP 025292 official market data only".lower() not in text and "ctp025292" not in text:
        issues.append("source_package.market_data_only_claim_missing")
    runtime_pack = (
        payload.get("runtime_pack")
        or payload.get("native_pack")
        or payload.get("runtime")
        or payload.get("source_pack")
    )
    if not isinstance(runtime_pack, dict):
        issues.append("source_package.runtime_pack_missing")
    else:
        runtime_pack_id = str(runtime_pack.get("runtime_pack_id") or runtime_pack.get("pack_id") or "")
        if not runtime_pack_id:
            issues.append("source_package.runtime_pack_id_missing")
        elif "025292" not in runtime_pack_id and "ctp-live" not in runtime_pack_id:
            issues.append("source_package.runtime_pack_id_not_025292")
        if not (runtime_pack.get("ref") or runtime_pack.get("source_ref") or runtime_pack.get("path")):
            issues.append("source_package.runtime_pack_ref_missing")
    if _contains_openctp_tts(payload):
        issues.append("source_package.openctp_tts_not_allowed_for_025292")
    return issues


def _expected_runtime_hashes(source_package: dict[str, Any] | None) -> dict[str, str]:
    if source_package is None:
        return {}
    runtime_pack = (
        source_package.get("runtime_pack")
        or source_package.get("native_pack")
        or source_package.get("runtime")
        or source_package.get("source_pack")
    )
    if not isinstance(runtime_pack, dict):
        return {}
    dlls = runtime_pack.get("dlls") or runtime_pack.get("dll_sha256") or {}
    if not isinstance(dlls, dict):
        return {}
    expected: dict[str, str] = {}
    for filename, value in dlls.items():
        key = str(filename)
        if isinstance(value, dict):
            digest = value.get("sha256")
        else:
            digest = value
        if digest:
            expected[key] = str(digest).upper()
    return expected


def _runtime_dll_issues(
    runtime_dlls: dict[str, dict[str, Any]],
    *,
    expected_hashes: dict[str, str],
) -> list[str]:
    issues: list[str] = []
    for filename, metadata in runtime_dlls.items():
        if not metadata["exists"]:
            issues.append(f"runtime_dll_missing:{filename}")
            continue
        actual_sha = str(metadata["sha256"] or "").upper()
        if actual_sha == KNOWN_OPENCTP_TTS_DLL_SHA256.get(filename):
            issues.append(f"runtime_dll_known_openctp_tts:{filename}")
        expected_sha = expected_hashes.get(filename)
        if expected_sha and actual_sha != expected_sha:
            issues.append(f"runtime_dll_hash_mismatch:{filename}")
    if expected_hashes:
        for filename in REQUIRED_CTP_RUNTIME_DLLS:
            if filename not in expected_hashes:
                issues.append(f"source_package.runtime_dll_hash_missing:{filename}")
    return issues


def _runtime_manifest_issues(manifest: dict[str, str]) -> list[str]:
    issues: list[str] = []
    runtime_pack_id = str(manifest.get("runtime_pack_id") or manifest.get("pack_id") or "")
    profile = str(manifest.get("profile") or "")
    if not runtime_pack_id:
        issues.append("runtime_manifest.runtime_pack_id_missing")
    elif "025292" not in runtime_pack_id:
        issues.append("runtime_manifest.runtime_pack_id_not_025292")
    if profile.lower() in {"", "auto"}:
        issues.append("runtime_manifest.profile_auto_not_allowed_for_025292")
    return issues


def _config_issues(config: CtpAdapterConfig) -> list[str]:
    issues = list(config.validate())
    if config.broker_id != "0155":
        issues.append("config.broker_id_not_0155")
    if config.user_id != "025292":
        issues.append("config.user_id_not_025292")
    if _contains_openctp_tts({"md_front": config.md_front, "td_front": config.td_front}):
        issues.append("config.openctp_tts_front_not_allowed_for_025292")
    return issues


def build_lineage_summary(
    *,
    config_path: Path = DEFAULT_CONFIG,
    source_package_path: Path = DEFAULT_SOURCE_PACKAGE,
    runtime_bin: Path = DEFAULT_RUNTIME_BIN,
) -> dict[str, Any]:
    config_path = config_path if config_path.is_absolute() else REPO_ROOT / config_path
    source_package_path = (
        source_package_path if source_package_path.is_absolute() else REPO_ROOT / source_package_path
    )
    runtime_bin = runtime_bin if runtime_bin.is_absolute() else REPO_ROOT / runtime_bin
    runtime_manifest_path = runtime_bin / "_synced_from.txt"

    payload: dict[str, Any] = {
        "baseline": BASELINE,
        "route_scenario": "ctp025292_marketdata_sandbox_paper_simulated_001",
        "market_source": "CTP 025292 official market data only",
        "market_data_account_id": "025292",
        "broker_order_submission": False,
        "trading_adapter": "disabled",
        "execution_target": "Nautilus Sandbox Paper account sandbox-paper.simulated-001",
        "success": False,
        "status": "blocked",
        "blocker_id": "ctp025292_source_lineage_unready",
        "issues": [],
        "paths": {
            "config": _safe_path(config_path),
            "source_package": _safe_path(source_package_path),
            "runtime_bin": _safe_path(runtime_bin),
            "runtime_manifest": _safe_path(runtime_manifest_path),
        },
        "config": None,
        "source_package": {
            "exists": source_package_path.exists(),
            "summary": None,
        },
        "runtime_manifest": {
            "exists": runtime_manifest_path.exists(),
            "values": {},
        },
        "runtime_dlls": {},
        "loader_isolation": {
            "required_mode": "fresh_worker_process_per_runtime_pack",
            "reason": "Windows caches loaded DLLs by module name; same-name CTP DLL families must not be switched inside one process.",
        },
        "negative_assertions": {
            "did_not_open_trading_channel": True,
            "did_not_submit_broker_order": True,
            "did_not_generate_or_consume_paper_request": True,
            "did_not_claim_market_data_ready": True,
        },
    }

    issues: list[str] = []
    source_package: dict[str, Any] | None = None
    if not config_path.exists():
        issues.append("config_missing")
    else:
        try:
            config = CtpAdapterConfig.from_json_file(config_path)
        except Exception as exc:
            issues.append(f"config_load_failed:{type(exc).__name__}")
        else:
            payload["config"] = _config_summary(config)
            issues.extend(_config_issues(config))

    if not source_package_path.exists():
        issues.append("source_package_missing")
    else:
        try:
            source_package = _read_json(source_package_path)
        except Exception as exc:
            issues.append(f"source_package_load_failed:{type(exc).__name__}")
        else:
            payload["source_package"]["summary"] = {
                "schema_version": source_package.get("schema_version"),
                "account_id": source_package.get("account_id"),
                "account_uid": source_package.get("account_uid"),
                "market_data_account_id": source_package.get("market_data_account_id"),
                "market_source": source_package.get("market_source"),
            }
            issues.extend(_source_package_issues(source_package))

    runtime_manifest = _read_runtime_manifest(runtime_bin)
    payload["runtime_manifest"]["values"] = runtime_manifest
    runtime_dlls = _runtime_dll_summary(runtime_bin)
    payload["runtime_dlls"] = runtime_dlls
    if not runtime_manifest_path.exists():
        issues.append("runtime_manifest_missing")
    elif _contains_openctp_tts(runtime_manifest):
        issues.append("runtime_manifest_openctp_tts_for_025292")
    issues.extend(_runtime_manifest_issues(runtime_manifest))
    expected_hashes = _expected_runtime_hashes(source_package)
    issues.extend(_runtime_dll_issues(runtime_dlls, expected_hashes=expected_hashes))

    payload["issues"] = issues
    if not issues:
        payload["success"] = True
        payload["status"] = "passed"
        payload["blocker_id"] = None
        payload["negative_assertions"]["did_not_claim_market_data_ready"] = False
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the CTP 025292 market-data-only source package and runtime lineage."
    )
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--source-package", type=Path, default=DEFAULT_SOURCE_PACKAGE)
    parser.add_argument("--runtime-bin", type=Path, default=DEFAULT_RUNTIME_BIN)
    parser.add_argument("--output-json", type=Path, default=None)
    args = parser.parse_args()

    payload = build_lineage_summary(
        config_path=args.config,
        source_package_path=args.source_package,
        runtime_bin=args.runtime_bin,
    )
    text = json.dumps(payload, ensure_ascii=False)
    print(text)

    if args.output_json is not None:
        output_path = args.output_json if args.output_json.is_absolute() else REPO_ROOT / args.output_json
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    return 0 if payload["success"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
