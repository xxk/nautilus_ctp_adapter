from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
ACCOUNT_CONSOLE_ROOT = REPO_ROOT.parent / "nautilus_account_console"
BASELINE = "ctp025292-account-console-runtime-lineage-audit-v1"
ROUTE_SCENARIO = "ctp025292_marketdata_sandbox_paper_simulated_001"
RUNTIME_PACK_ID = "ctp-live-025292-md"
DEFAULT_SOURCE_PACKAGE = (
    ACCOUNT_CONSOLE_ROOT
    / "output"
    / "account_capability"
    / "ctp-live-025292"
    / "source-package.json"
)
DEFAULT_ACCEPTANCE_EVIDENCE = (
    ACCOUNT_CONSOLE_ROOT
    / "docs"
    / "acceptance"
    / "2026-06-15-ctp025292-real-login-ui-acceptance-evidence.json"
)
DEFAULT_TEMPLATE_SOURCE_PACKAGE = (
    ACCOUNT_CONSOLE_ROOT
    / "contracts"
    / "source_artifacts"
    / "templates"
    / "ctp_live_025292_source_package.template.json"
)
REQUIRED_DLLS = ("thostmduserapi_se.dll", "thosttraderapi_se.dll")
RUNTIME_PACK_KEYS = ("runtime_pack", "native_pack", "runtime", "source_pack")
SHA256_PATTERN = re.compile(r"\b[A-Fa-f0-9]{64}\b")


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def _load_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    payload = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path}: JSON payload must be an object")
    return payload


def _artifact_summary(path: Path, payload: dict[str, Any] | None) -> dict[str, Any]:
    summary: dict[str, Any] = {
        "artifact_ref": str(path),
        "exists": path.exists(),
    }
    if path.exists():
        summary["sha256"] = _file_sha256(path)
    if payload is not None:
        summary["schema_version"] = payload.get("schema_version") or payload.get("schema")
        summary["account_id"] = payload.get("account_id")
        summary["account_uid"] = payload.get("account_uid")
        summary["display_alias"] = payload.get("display_alias")
        summary["source_kind"] = payload.get("source_kind")
        summary["source_mode"] = payload.get("source_mode")
        summary["status"] = payload.get("status")
        summary["verdict"] = payload.get("verdict")
        summary["blocker_id"] = payload.get("blocker_id")
        summary["source_ref"] = payload.get("source_ref")
        summary["source_checksum"] = payload.get("source_checksum")
    return summary


def _runtime_pack(payload: dict[str, Any] | None) -> dict[str, Any] | None:
    if payload is None:
        return None
    for key in RUNTIME_PACK_KEYS:
        candidate = payload.get(key)
        if isinstance(candidate, dict):
            return candidate
    return None


def _extract_runtime_hashes(runtime_pack: dict[str, Any] | None) -> dict[str, str]:
    if runtime_pack is None:
        return {}
    dlls = runtime_pack.get("dlls") or runtime_pack.get("dll_sha256") or {}
    if not isinstance(dlls, dict):
        return {}
    hashes: dict[str, str] = {}
    for filename, value in dlls.items():
        digest: Any
        if isinstance(value, dict):
            digest = value.get("sha256")
        else:
            digest = value
        if digest:
            hashes[str(filename)] = str(digest).upper()
    return hashes


def _runtime_lineage_summary(payload: dict[str, Any] | None) -> dict[str, Any]:
    runtime_pack = _runtime_pack(payload)
    runtime_hashes = _extract_runtime_hashes(runtime_pack)
    runtime_pack_id = ""
    runtime_ref = None
    if runtime_pack is not None:
        runtime_pack_id = str(runtime_pack.get("runtime_pack_id") or runtime_pack.get("pack_id") or "")
        runtime_ref = runtime_pack.get("ref") or runtime_pack.get("source_ref") or runtime_pack.get("path")
    text = json.dumps(payload or {}, ensure_ascii=False)
    return {
        "runtime_pack_present": runtime_pack is not None,
        "runtime_pack_id": runtime_pack_id,
        "runtime_ref_present": bool(runtime_ref),
        "runtime_hash_count": len(runtime_hashes),
        "required_dll_hashes_present": all(filename in runtime_hashes for filename in REQUIRED_DLLS),
        "required_dll_hashes": {
            filename: runtime_hashes.get(filename)
            for filename in REQUIRED_DLLS
            if filename in runtime_hashes
        },
        "sha256_like_token_count": len(set(SHA256_PATTERN.findall(text))),
    }


def _acceptance_issues(acceptance: dict[str, Any] | None) -> list[str]:
    if acceptance is None:
        return ["account_console_acceptance_evidence_missing"]
    issues: list[str] = []
    status = str(acceptance.get("status") or "").lower()
    verdict = str(acceptance.get("verdict") or "").lower()
    if "blocked" in status or verdict == "blocked":
        issues.append("account_console_acceptance_evidence_blocked")
    checksum = str(acceptance.get("source_checksum") or "")
    if "3333333333333333333333333333333333333333333333333333333333333333" in checksum:
        issues.append("account_console_acceptance_source_checksum_placeholder")
    source_ref = str(acceptance.get("source_ref") or "")
    if "source-package.json" not in source_ref:
        issues.append("account_console_acceptance_source_ref_missing")
    return issues


def _source_package_issues(
    source_package: dict[str, Any] | None,
    runtime_lineage: dict[str, Any],
) -> list[str]:
    if source_package is None:
        return ["account_console_source_package_missing"]
    issues: list[str] = []
    text = json.dumps(source_package, ensure_ascii=False).lower()
    if "025292" not in text:
        issues.append("account_console_source_package_missing_025292_identity")
    if source_package.get("schema_version") == "account_source_artifact.v1":
        issues.append("account_console_source_package_is_account_source_artifact")
    if not runtime_lineage["runtime_pack_present"]:
        issues.append("account_console_source_package_runtime_pack_missing")
    if runtime_lineage["runtime_pack_present"] and "025292" not in str(runtime_lineage["runtime_pack_id"]):
        issues.append("account_console_source_package_runtime_pack_id_not_025292")
    if runtime_lineage["runtime_pack_present"] and not runtime_lineage["runtime_ref_present"]:
        issues.append("account_console_source_package_runtime_ref_missing")
    if runtime_lineage["runtime_pack_present"] and not runtime_lineage["required_dll_hashes_present"]:
        issues.append("account_console_source_package_required_dll_hashes_missing")
    return issues


def audit_account_console_runtime_lineage(
    *,
    source_package_path: Path = DEFAULT_SOURCE_PACKAGE,
    acceptance_evidence_path: Path = DEFAULT_ACCEPTANCE_EVIDENCE,
    template_source_package_path: Path = DEFAULT_TEMPLATE_SOURCE_PACKAGE,
) -> dict[str, Any]:
    source_package = _load_json(source_package_path)
    acceptance = _load_json(acceptance_evidence_path)
    template = _load_json(template_source_package_path)
    runtime_lineage = _runtime_lineage_summary(source_package)
    issues = [
        *_source_package_issues(source_package, runtime_lineage),
        *_acceptance_issues(acceptance),
    ]

    source_package_satisfies_runtime_lineage = (
        source_package is not None
        and runtime_lineage["runtime_pack_present"]
        and "025292" in str(runtime_lineage["runtime_pack_id"])
        and runtime_lineage["runtime_ref_present"]
        and runtime_lineage["required_dll_hashes_present"]
    )
    account_console_acceptance_passed = acceptance is not None and not _acceptance_issues(acceptance)
    success = source_package_satisfies_runtime_lineage and account_console_acceptance_passed

    return {
        "baseline": BASELINE,
        "route_scenario": ROUTE_SCENARIO,
        "runtime_pack_id": RUNTIME_PACK_ID,
        "market_source": "CTP 025292 official market data only",
        "market_data_account_id": "025292",
        "broker_order_submission": False,
        "trading_adapter": "disabled",
        "success": success,
        "status": "passed" if success else "blocked",
        "blocker_id": None if success else "ctp025292_account_console_runtime_lineage_unready",
        "issues": issues,
        "account_console_source_package": _artifact_summary(source_package_path, source_package),
        "account_console_acceptance_evidence": _artifact_summary(acceptance_evidence_path, acceptance),
        "account_console_template_source_package": _artifact_summary(template_source_package_path, template),
        "runtime_lineage": runtime_lineage,
        "source_package_satisfies_runtime_lineage": source_package_satisfies_runtime_lineage,
        "account_console_acceptance_passed": account_console_acceptance_passed,
        "diagnostic_value": (
            "Account Console account/source artifacts may prove account projection, but they cannot unlock "
            "S2-G2 market-data preflight unless they also carry route-bound runtime_pack_id, runtime ref, "
            "and required CTP DLL hashes."
        ),
        "negative_assertions": {
            "did_not_open_trading_channel": True,
            "did_not_submit_broker_order": True,
            "did_not_use_025292_as_trading_account": True,
            "did_not_generate_or_consume_paper_request": True,
            "did_not_claim_market_data_ready": True,
            "did_not_claim_paper_ready": True,
            "did_not_claim_live_ready": True,
            "did_not_enter_stage3": True,
        },
        "next_action": (
            "Use the Account Console source package runtime refs with source-lineage gate."
            if success
            else "Build or restore output/account_capability/ctp-live-025292/source-package.json with route-bound runtime_pack_id, runtime ref, and required DLL hashes, then rerun the source-lineage gate before MD smoke."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Audit whether Account Console 025292 artifacts can satisfy Stage 2 MD runtime lineage."
    )
    parser.add_argument("--source-package", type=Path, default=DEFAULT_SOURCE_PACKAGE)
    parser.add_argument("--acceptance-evidence", type=Path, default=DEFAULT_ACCEPTANCE_EVIDENCE)
    parser.add_argument("--template-source-package", type=Path, default=DEFAULT_TEMPLATE_SOURCE_PACKAGE)
    parser.add_argument("--output-json", type=Path, default=None)
    args = parser.parse_args()

    payload = audit_account_console_runtime_lineage(
        source_package_path=args.source_package,
        acceptance_evidence_path=args.acceptance_evidence,
        template_source_package_path=args.template_source_package,
    )
    print(json.dumps(payload, ensure_ascii=False))

    if args.output_json is not None:
        args.output_json.parent.mkdir(parents=True, exist_ok=True)
        args.output_json.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    return 0 if payload["success"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
