from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

BASELINE = "ctp025292-csharp-runtime-parity-audit-v1"
ROUTE_SCENARIO = "ctp025292_marketdata_sandbox_paper_simulated_001"
RUNTIME_PACK_ID = "ctp-live-025292-md"
MARKET_SOURCE = "CTP 025292 official market data only"
MARKET_DATA_ACCOUNT_ID = "025292"
TRUST_MARKER = "_ctp025292_runtime_pack.json"
SYNCED_MANIFEST = "_synced_from.txt"
REQUIRED_SE_PAIR = ("thostmduserapi_se.dll", "thosttraderapi_se.dll")
DLL_NAMES = (
    "thostmduserapi_se.dll",
    "thosttraderapi_se.dll",
    "thostmduserapi.dll",
    "thosttraderapi.dll",
    "thosttraderapi_sm.dll",
)
KNOWN_OPENCTP_TTS_DLL_SHA256 = {
    "thostmduserapi_se.dll": "66BACF7E33AD901534DA4B08662F08FC9F6169760B2AA0EEA85766C93FB6501E",
    "thosttraderapi_se.dll": "543ECE8B55C6FBC671B251E8CC0EE909708EE0F3C5ADC4FD2FD542E3B4C8D4E1",
}
VERSION_MARKER_PATTERN = re.compile(
    r"(?:v\d+\.\d+(?:\.\d+)?[_A-Za-z0-9 .:-]{0,48}|openctp-tts v\d+\.\d+\.\d+|THOST UserAPI v\d+\.\d+)",
    re.IGNORECASE,
)
SOURCE_PATTERNS = {
    "create_md_api": "CreateFtdcMdApi",
    "req_user_login_request_id_zero": "ReqUserLogin(&m_logonField, 0)",
    "subscribe_after_login_path": "SubscribeMarketData",
    "protocol_info_q7_155": "ProtocolInfo",
    "user_product_info_q7_155": "UserProductInfo",
}


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


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
            if len(marker) <= 90:
                markers.add(marker)
    return sorted(markers)


def _load_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
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


def _dll_metadata(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    stat = path.stat()
    return {
        "exists": True,
        "sha256": _file_sha256(path),
        "length": stat.st_size,
        "last_write_time": datetime.fromtimestamp(stat.st_mtime).astimezone().isoformat(),
        "version_markers": _version_markers(path),
    }


def _marker_matches_dlls(marker: dict[str, Any], files: dict[str, Any]) -> bool:
    marker_dlls = marker.get("dlls")
    if not isinstance(marker_dlls, dict):
        return False
    for filename in REQUIRED_SE_PAIR:
        expected = marker_dlls.get(filename)
        if isinstance(expected, dict):
            expected = expected.get("sha256")
        metadata = files.get(filename)
        if not isinstance(metadata, dict):
            return False
        if str(expected or "").upper() != str(metadata.get("sha256", "")).upper():
            return False
    return True


def _trust_marker_summary(root: Path) -> dict[str, Any] | None:
    marker = root / TRUST_MARKER
    payload = _load_json(marker)
    if payload is None:
        return None
    return {
        "artifact_ref": str(marker),
        "sha256": _file_sha256(marker),
        "runtime_pack_id": payload.get("runtime_pack_id"),
        "source_kind": payload.get("source_kind"),
        "source_bin": payload.get("source_bin"),
    }


def _source_trust_marker_summary(root: Path, files: dict[str, Any]) -> dict[str, Any] | None:
    manifest = _manifest_values(root / SYNCED_MANIFEST)
    source_bin_text = manifest.get("ctp_api")
    if not source_bin_text:
        return None
    source_bin = Path(source_bin_text)
    marker = source_bin / TRUST_MARKER
    payload = _load_json(marker)
    if payload is None:
        return None
    return {
        "artifact_ref": str(marker),
        "sha256": _file_sha256(marker),
        "runtime_pack_id": payload.get("runtime_pack_id"),
        "source_kind": payload.get("source_kind"),
        "source_bin": payload.get("source_bin"),
        "matches_runtime_bin_dlls": _marker_matches_dlls(payload, files),
    }


def _candidate(root: Path) -> dict[str, Any]:
    root = root.resolve()
    files: dict[str, Any] = {}
    for name in DLL_NAMES:
        metadata = _dll_metadata(root / name)
        if metadata is not None:
            files[name] = metadata
    payload: dict[str, Any] = {
        "root": str(root),
        "exists": root.exists(),
        "files": files,
        "has_required_se_pair": all(name in files for name in REQUIRED_SE_PAIR),
        "trust_marker": _trust_marker_summary(root),
        "synced_manifest": _manifest_values(root / SYNCED_MANIFEST),
        "source_trust_marker": _source_trust_marker_summary(root, files),
    }
    payload["classification"] = _classification(payload)
    return payload


def _classification(candidate: dict[str, Any]) -> str:
    files = candidate.get("files")
    files = files if isinstance(files, dict) else {}
    version_text = json.dumps(
        {
            name: metadata.get("version_markers", [])
            for name, metadata in files.items()
            if isinstance(metadata, dict)
        },
        ensure_ascii=False,
    ).lower()
    known_openctp_pair = all(
        isinstance(files.get(name), dict)
        and str(files[name].get("sha256", "")).upper() == expected
        for name, expected in KNOWN_OPENCTP_TTS_DLL_SHA256.items()
    )
    if known_openctp_pair or "openctp" in version_text or "tts" in version_text:
        return "rejected_openctp_tts_paper_family"

    marker = candidate.get("trust_marker")
    if (
        isinstance(marker, dict)
        and marker.get("runtime_pack_id") == RUNTIME_PACK_ID
        and marker.get("source_kind") == "operator_trusted_025292"
    ):
        return "operator_trusted_025292_non_openctp_family"
    source_marker = candidate.get("source_trust_marker")
    if (
        isinstance(source_marker, dict)
        and source_marker.get("runtime_pack_id") == RUNTIME_PACK_ID
        and source_marker.get("source_kind") == "operator_trusted_025292"
        and source_marker.get("matches_runtime_bin_dlls") is True
    ):
        return "operator_trusted_025292_non_openctp_family"

    if "v6.3.15_20190220" in version_text and candidate.get("has_required_se_pair"):
        return "csharp_reference_v6315_se_candidate_untrusted_for_route"
    if "v6.7.11_20250617" in version_text and candidate.get("has_required_se_pair"):
        return "v6711_se_candidate_untrusted_for_route"
    if candidate.get("has_required_se_pair"):
        return "untrusted_non_openctp_se_pair_candidate"
    if files:
        return "incomplete_or_mixed_ctp_dll_candidate"
    return "no_ctp_dlls_found"


def _scan_source_ref(path: Path) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "artifact_ref": str(path),
        "exists": path.exists(),
        "sha256": _file_sha256(path) if path.exists() else None,
        "findings": {},
    }
    if not path.exists():
        return payload
    text = path.read_text(encoding="utf-8-sig", errors="replace")
    lines = text.splitlines()
    for key, pattern in SOURCE_PATTERNS.items():
        matches = [index for index, line in enumerate(lines, start=1) if pattern in line]
        payload["findings"][key] = {
            "present": bool(matches),
            "line_numbers": matches[:12],
            "truncated": len(matches) > 12,
        }
    return payload


def _csv_ref(path: Path) -> dict[str, Any]:
    return {
        "artifact_ref": str(path),
        "exists": path.exists(),
        "sha256": _file_sha256(path) if path.exists() else None,
        "length": path.stat().st_size if path.exists() else None,
        "last_write_time": datetime.fromtimestamp(path.stat().st_mtime).astimezone().isoformat()
        if path.exists()
        else None,
        "raw_front_values_recorded": False,
    }


def _same_hash(left: dict[str, Any], right: dict[str, Any], filename: str) -> bool | None:
    left_files = left.get("files") if isinstance(left.get("files"), dict) else {}
    right_files = right.get("files") if isinstance(right.get("files"), dict) else {}
    left_meta = left_files.get(filename)
    right_meta = right_files.get(filename)
    if not isinstance(left_meta, dict) or not isinstance(right_meta, dict):
        return None
    return str(left_meta.get("sha256", "")).upper() == str(right_meta.get("sha256", "")).upper()


def _parity(current: dict[str, Any] | None, candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if current is None:
        return []
    rows: list[dict[str, Any]] = []
    for candidate in candidates:
        if candidate is current:
            continue
        rows.append(
            {
                "candidate_root": candidate["root"],
                "candidate_classification": candidate["classification"],
                "md_same_sha_as_current": _same_hash(current, candidate, "thostmduserapi_se.dll"),
                "td_same_sha_as_current": _same_hash(current, candidate, "thosttraderapi_se.dll"),
                "same_required_se_pair_as_current": (
                    _same_hash(current, candidate, "thostmduserapi_se.dll") is True
                    and _same_hash(current, candidate, "thosttraderapi_se.dll") is True
                ),
            }
        )
    return rows


def build_audit(
    *,
    current_runtime_bin: Path,
    candidate_roots: list[Path],
    source_refs: list[Path],
    desktop_csvs: list[Path],
    created_at: str | None = None,
) -> dict[str, Any]:
    current_candidate = _candidate(current_runtime_bin)
    candidates = [current_candidate]
    seen = {current_candidate["root"].lower()}
    for root in candidate_roots:
        item = _candidate(root)
        key = item["root"].lower()
        if key in seen:
            continue
        seen.add(key)
        candidates.append(item)

    csharp_v6315 = [
        item
        for item in candidates
        if item["classification"] == "csharp_reference_v6315_se_candidate_untrusted_for_route"
    ]
    rejected_openctp = [
        item for item in candidates if item["classification"] == "rejected_openctp_tts_paper_family"
    ]
    parity_rows = _parity(current_candidate, candidates)
    materialization_safe = False
    csharp_replay_safe = False
    payload: dict[str, Any] = {
        "baseline": BASELINE,
        "schema_version": "ctp025292.csharp_runtime_parity_audit.v1",
        "created_at": created_at or datetime.now().astimezone().isoformat(),
        "route_scenario": ROUTE_SCENARIO,
        "runtime_pack_id": RUNTIME_PACK_ID,
        "market_source": MARKET_SOURCE,
        "market_data_account_id": MARKET_DATA_ACCOUNT_ID,
        "market_data_role": "market_data_only",
        "broker_order_submission": False,
        "trading_adapter": "disabled",
        "success": False,
        "status": "blocked",
        "blocker_id": "ctp025292_csharp_success_runtime_family_not_route_trusted_or_replay_safe_yet",
        "current_runtime_pack": current_candidate,
        "candidate_runtime_families": candidates[1:],
        "parity_against_current_runtime": parity_rows,
        "source_refs": [_scan_source_ref(path) for path in source_refs],
        "desktop_front_csv_refs": [_csv_ref(path) for path in desktop_csvs],
        "findings": {
            "same_name_dlls_are_not_identity": True,
            "current_runtime_is_operator_trusted": current_candidate["classification"]
            == "operator_trusted_025292_non_openctp_family",
            "csharp_v6315_reference_candidates_found": len(csharp_v6315),
            "openctp_tts_candidates_rejected": len(rejected_openctp),
            "subscription_not_primary_blocker": True,
            "reason": (
                "Known C# success references use a CTP MD flow shape that was already emulated "
                "on the current trusted runtime pack, but the current pack still closes before "
                "OnRspUserLogin. The remaining gap is runtime family / front policy, not a missing "
                "SubscribeMarketData call."
            ),
        },
        "safety_decision": {
            "materialize_csharp_dll_family_into_route_runtime_now": materialization_safe,
            "launch_csharp_provider_replay_now": csharp_replay_safe,
            "operator_authorization_required_for_csharp_provider_replay": True,
            "route_trust_required_before_new_runtime_pack": True,
            "bridge_rebuild_required_if_sdk_family_changes": bool(csharp_v6315),
            "reason": (
                "The C# reference DLL family is not the accepted ctp-live-025292-md route runtime. "
                "Swapping SDK families safely requires an explicit operator-trusted 025292 source "
                "package plus a repo-owned bridge/runtime rebuild against the matching headers/libs. "
                "Launching the legacy C# provider is a separate read-only replay diagnostic and is "
                "not performed by this audit."
            ),
        },
        "blocker": {
            "blocker_type": "ctp025292_marketdata_unready",
            "owner": "nautilus_ctp_adapter",
            "reason": (
                "A C# historical success lineage exists, but its probable DLL family is not yet "
                "route-trusted for the Stage 2 runtime pack and cannot be treated as current "
                "S2-G2 market-data pass evidence."
            ),
            "next_action": (
                "Pick exactly one next repair path: either operator-ack and materialize a "
                "matching non-OpenCTP/TTS 025292 MD DLL family with bridge rebuild, or authorize "
                "a legacy C# provider read-only MD replay to capture the current login response/tick. "
                "Do not use OpenCTP/TTS and do not retry subscription before login response."
            ),
        },
        "negative_assertions": {
            "did_not_launch_legacy_csharp_provider": True,
            "did_not_copy_or_materialize_external_dlls": True,
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
    }
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Compare known-success C# CTP provider runtime families against the trusted 025292 route runtime."
    )
    parser.add_argument("--current-runtime-bin", type=Path, required=True)
    parser.add_argument("--candidate-root", type=Path, action="append", default=[])
    parser.add_argument("--source-ref", type=Path, action="append", default=[])
    parser.add_argument("--desktop-csv", type=Path, action="append", default=[])
    parser.add_argument("--created-at", default=None)
    parser.add_argument("--output-json", type=Path, default=None)
    args = parser.parse_args()

    payload = build_audit(
        current_runtime_bin=args.current_runtime_bin,
        candidate_roots=args.candidate_root,
        source_refs=args.source_ref,
        desktop_csvs=args.desktop_csv,
        created_at=args.created_at,
    )
    text = json.dumps(payload, ensure_ascii=False, indent=2)
    print(text)
    if args.output_json is not None:
        args.output_json.parent.mkdir(parents=True, exist_ok=True)
        args.output_json.write_text(text + "\n", encoding="utf-8")
    return 0 if payload["success"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
