from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

BASELINE = "ctp025292-md-error-and-dll-family-audit-v1"
ROUTE_SCENARIO = "ctp025292_marketdata_sandbox_paper_simulated_001"
MARKET_SOURCE = "CTP 025292 official market data only"
MARKET_DATA_ACCOUNT_ID = "025292"
RUNTIME_PACK_ID = "ctp-live-025292-md"
DLL_NAMES = (
    "thostmduserapi_se.dll",
    "thosttraderapi_se.dll",
    "thosttraderapi_sm.dll",
    "ctp_native.dll",
)
REQUIRED_MD_TD_SE_PAIR = ("thostmduserapi_se.dll", "thosttraderapi_se.dll")
TRUST_MARKER = "_ctp025292_runtime_pack.json"
SYNCED_MANIFEST = "_synced_from.txt"
KNOWN_OPENCTP_TTS_DLL_SHA256 = {
    "thostmduserapi_se.dll": "66BACF7E33AD901534DA4B08662F08FC9F6169760B2AA0EEA85766C93FB6501E",
    "thosttraderapi_se.dll": "543ECE8B55C6FBC671B251E8CC0EE909708EE0F3C5ADC4FD2FD542E3B4C8D4E1",
}
VERSION_MARKER_PATTERN = re.compile(
    r"(?:v\d+\.\d+(?:\.\d+)?[_A-Za-z0-9 .:-]{0,40}|openctp-tts v\d+\.\d+\.\d+|THOST UserAPI v\d+\.\d+)",
    re.IGNORECASE,
)


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path}: expected JSON object")
    return payload


def _manifest_values(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    values: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8-sig", errors="replace").splitlines():
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip()
    return values


def _ascii_strings(path: Path, *, minimum: int = 5) -> list[str]:
    data = path.read_bytes()
    strings: list[str] = []
    for match in re.finditer(rb"[ -~]{%d,}" % minimum, data):
        text = match.group().decode("ascii", errors="ignore").strip()
        if text:
            strings.append(text)
    return strings


def _version_markers(path: Path) -> list[str]:
    markers: set[str] = set()
    for text in _ascii_strings(path):
        for match in VERSION_MARKER_PATTERN.finditer(text):
            marker = " ".join(match.group(0).split())
            if len(marker) <= 80:
                markers.add(marker)
    return sorted(markers)


def _dll_metadata(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    stat = path.stat()
    return {
        "exists": True,
        "sha256": _file_sha256(path),
        "length": stat.st_size,
        "last_write_time": datetime.fromtimestamp(stat.st_mtime).astimezone().isoformat(),
        "version_info_available": False,
        "version_markers": _version_markers(path),
    }


def _trust_marker_summary(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    payload = _load_json(path)
    return {
        "runtime_pack_id": payload.get("runtime_pack_id"),
        "source_kind": payload.get("source_kind"),
        "source_bin": payload.get("source_bin"),
    }


def _family(root: Path) -> dict[str, Any]:
    root = root.resolve()
    files: dict[str, Any] = {}
    for name in DLL_NAMES:
        metadata = _dll_metadata(root / name)
        if metadata is not None:
            files[name] = metadata

    marker = root / TRUST_MARKER
    manifest = root / SYNCED_MANIFEST
    payload: dict[str, Any] = {
        "root": str(root),
        "exists": root.exists(),
        "files": files,
        "has_required_se_pair": all(name in files for name in REQUIRED_MD_TD_SE_PAIR),
        "trust_marker_ref": str(marker) if marker.exists() else None,
        "synced_manifest_ref": str(manifest) if manifest.exists() else None,
    }
    if marker.exists():
        payload["trust_marker_sha256"] = _file_sha256(marker)
        payload["trust_marker_summary"] = _trust_marker_summary(marker)
    if manifest.exists():
        payload["synced_manifest_sha256"] = _file_sha256(manifest)
        payload["synced_manifest_summary"] = _manifest_values(manifest)
    payload["classification"] = _family_classification(payload)
    return payload


def _family_classification(family: dict[str, Any]) -> str:
    files = family.get("files")
    files = files if isinstance(files, dict) else {}
    version_text = json.dumps(
        {
            name: metadata.get("version_markers", [])
            for name, metadata in files.items()
            if isinstance(metadata, dict)
        },
        ensure_ascii=False,
    ).lower()
    manifest_text = json.dumps(family.get("synced_manifest_summary", {}), ensure_ascii=False).lower()
    known_openctp_hash_pair = all(
        isinstance(files.get(name), dict)
        and str(files[name].get("sha256", "")).upper() == expected
        for name, expected in KNOWN_OPENCTP_TTS_DLL_SHA256.items()
    )
    if known_openctp_hash_pair or "openctp" in version_text or "openctp" in manifest_text:
        return "rejected_openctp_tts_paper_family"
    marker = family.get("trust_marker_summary")
    if (
        isinstance(marker, dict)
        and marker.get("runtime_pack_id") == RUNTIME_PACK_ID
        and marker.get("source_kind") == "operator_trusted_025292"
    ):
        return "operator_trusted_025292_non_openctp_family"
    if family.get("has_required_se_pair"):
        return "untrusted_non_openctp_candidate"
    return "incomplete_or_non_se_pair"


def _console_summary(capture: dict[str, Any]) -> dict[str, Any]:
    console = capture.get("console_capture")
    console = console if isinstance(console, dict) else {}
    summary = console.get("summary")
    return summary if isinstance(summary, dict) else {}


def _smoke_result(capture: dict[str, Any]) -> dict[str, Any]:
    smoke = capture.get("smoke_result")
    return smoke if isinstance(smoke, dict) else {}


def _error_return_analysis(summary: dict[str, Any], capture: dict[str, Any]) -> dict[str, Any]:
    console_summary = _console_summary(capture)
    smoke = _smoke_result(capture)
    return {
        "req_user_login_return_codes": summary.get("return_codes", []),
        "last_login_return_codes_before_disconnect": (
            summary.get("native_close_detail", {}).get("last_login_return_codes", [])
            if isinstance(summary.get("native_close_detail"), dict)
            else []
        ),
        "disconnect_reasons": summary.get("disconnect_reasons", []),
        "login_response_count": summary.get("login_response_count", 0),
        "rsp_error_count": summary.get("rsp_error_count", 0),
        "heartbeat_warning_count": summary.get("heartbeat_warning_count", 0),
        "vendor_console_non_json_line_count": console_summary.get("non_json_console_line_count", 0),
        "vendor_console_matched_line_counts": console_summary.get("matched_line_counts", {}),
        "login_error_id": smoke.get("login_error_id", -1),
        "login_error_message_empty": not bool(str(smoke.get("login_error_message", ""))),
        "classification": "no_ctp_login_error_payload_observed_before_front_disconnect",
        "interpretation": (
            "The strict runtime pack produced no parsed CTP ErrorID/ErrorMsg and no vendor prompt "
            "line. The observed signal is local ReqUserLogin dispatch return_code=0 followed by "
            "OnFrontDisconnected(reason=0)."
        ),
    }


def _historical_refs(paths: list[Path]) -> list[dict[str, Any]]:
    refs: list[dict[str, Any]] = []
    for path in paths:
        refs.append(
            {
                "artifact_ref": str(path),
                "exists": path.exists(),
                "sha256": _file_sha256(path) if path.exists() else None,
            }
        )
    return refs


def build_audit(
    *,
    lifecycle_summary: Path,
    console_capture: Path,
    dll_roots: list[Path],
    historical_refs: list[Path],
    current_runtime_family: Path | None = None,
    current_runtime_source: Path | None = None,
    historical_success_family: Path | None = None,
    created_at: str | None = None,
) -> dict[str, Any]:
    summary = _load_json(lifecycle_summary)
    capture = _load_json(console_capture)
    families = [_family(root) for root in dll_roots]

    current_runtime_family = current_runtime_family or (dll_roots[0] if dll_roots else None)
    payload: dict[str, Any] = {
        "baseline": BASELINE,
        "created_at": created_at or datetime.now().astimezone().isoformat(),
        "route_scenario": ROUTE_SCENARIO,
        "runtime_pack_id": RUNTIME_PACK_ID,
        "market_source": MARKET_SOURCE,
        "market_data_account_id": MARKET_DATA_ACCOUNT_ID,
        "broker_order_submission": False,
        "trading_adapter": "disabled",
        "success": False,
        "status": "blocked",
        "blocker_id": "ctp025292_md_current_dll_family_mismatch_or_front_policy_unresolved",
        "error_return_analysis": _error_return_analysis(summary, capture),
        "dll_family_audit": {
            "families": families,
            "finding": (
                "The current trusted ctp-live-025292-md runtime pack must be compared by "
                "source root, SHA256, length and manifest/trust marker. Same DLL names are not "
                "sufficient version identity. OpenCTP/TTS DLL families are Paper/simulation-only "
                "and are rejected for Stage 2 CTP 025292 official market-data evidence."
            ),
            "current_runtime_family_ref": str(current_runtime_family) if current_runtime_family else None,
            "current_runtime_source_ref": str(current_runtime_source) if current_runtime_source else None,
            "historical_success_family_ref": str(historical_success_family)
            if historical_success_family
            else None,
            "version_resource_note": (
                "Windows VersionInfo fields are not available from these CTP DLLs in this environment; "
                "hash/length/path/source manifest and extracted version marker strings are used as "
                "the reliable version fingerprints."
            ),
        },
        "historical_success_refs": _historical_refs(historical_refs),
        "negative_assertions": {
            "did_not_open_td_order_or_live_send_script": True,
            "did_not_configure_025292_as_trading_account": True,
            "did_not_submit_broker_order": True,
            "did_not_generate_or_consume_paper_request": True,
            "did_not_claim_market_data_ready": True,
            "did_not_claim_paper_ready": True,
            "did_not_claim_live_ready": True,
            "raw_secret_values_recorded": False,
            "raw_front_values_recorded": False,
        },
        "next_action": (
            "Do not repeat subscription probes. Resolve DLL-family lineage first: prove the "
            "current non-OpenCTP/TTS family is the intended official 025292 MD family despite "
            "missing login response, or obtain another non-OpenCTP/TTS operator-trusted official "
            "025292 MD DLL family. Do not materialize OpenCTP/TTS for Stage 2 025292."
        ),
    }
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Audit the current 025292 MD login error-return layer and same-name CTP DLL families."
    )
    parser.add_argument("--lifecycle-summary", type=Path, required=True)
    parser.add_argument("--console-capture", type=Path, required=True)
    parser.add_argument("--dll-root", type=Path, action="append", required=True)
    parser.add_argument("--historical-ref", type=Path, action="append", default=[])
    parser.add_argument("--current-runtime-family", type=Path, default=None)
    parser.add_argument("--current-runtime-source", type=Path, default=None)
    parser.add_argument("--historical-success-family", type=Path, default=None)
    parser.add_argument("--created-at", default=None)
    parser.add_argument("--output-json", type=Path, default=None)
    args = parser.parse_args()

    payload = build_audit(
        lifecycle_summary=args.lifecycle_summary,
        console_capture=args.console_capture,
        dll_roots=args.dll_root,
        historical_refs=args.historical_ref,
        current_runtime_family=args.current_runtime_family,
        current_runtime_source=args.current_runtime_source,
        historical_success_family=args.historical_success_family,
        created_at=args.created_at,
    )
    print(json.dumps(payload, ensure_ascii=False))
    if args.output_json is not None:
        args.output_json.parent.mkdir(parents=True, exist_ok=True)
        args.output_json.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return 0 if payload["success"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
