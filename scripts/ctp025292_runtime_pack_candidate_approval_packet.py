from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

RUNTIME_PACK_ID = "ctp-live-025292-md"
REQUIRED_DLLS = ("thostmduserapi_se.dll", "thosttraderapi_se.dll")
REQUIRED_BRIDGE_HEADERS = (
    "ThostFtdcMdApi.h",
    "ThostFtdcTraderApi.h",
    "ThostFtdcUserApiDataType.h",
    "ThostFtdcUserApiStruct.h",
)
REQUIRED_BRIDGE_LIBS = ("thostmduserapi_se.lib", "thosttraderapi_se.lib")
DEFAULT_DISCOVERY_JSON = Path("var/stage2/ctp025292_runtime_pack_discovery_inventory_latest.json")
PAPER_TTS_PATH_TOKENS = ("tts-sdk", "tts_6.6.9", "py-openctp-tts", "openctp_tts")


def _family_id(candidate: dict[str, Any]) -> str:
    dlls = candidate.get("dlls") if isinstance(candidate.get("dlls"), dict) else {}
    parts: list[str] = []
    for filename in REQUIRED_DLLS:
        metadata = dlls.get(filename) if isinstance(dlls, dict) else {}
        if not isinstance(metadata, dict):
            metadata = {}
        parts.append(f"{filename}:{str(metadata.get('sha256') or '').upper()}:{metadata.get('length')}")
    digest = hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest().upper()
    return f"ctp025292-dll-family-{digest[:16]}"


def _path_is_paper_tts_like(path: str) -> bool:
    lowered = path.replace("\\", "/").lower()
    return any(token in lowered for token in PAPER_TTS_PATH_TOKENS)


def _bridge_inputs_for_path(path: str) -> dict[str, Any]:
    root = Path(path)
    headers_present = sorted(name for name in REQUIRED_BRIDGE_HEADERS if (root / name).exists())
    libs_present = sorted(name for name in REQUIRED_BRIDGE_LIBS if (root / name).exists())
    return {
        "headers_required": list(REQUIRED_BRIDGE_HEADERS),
        "headers_present": headers_present,
        "headers_missing": sorted(set(REQUIRED_BRIDGE_HEADERS) - set(headers_present)),
        "libs_required": list(REQUIRED_BRIDGE_LIBS),
        "libs_present": libs_present,
        "libs_missing": sorted(set(REQUIRED_BRIDGE_LIBS) - set(libs_present)),
        "bridge_rebuild_ready": (
            len(headers_present) == len(REQUIRED_BRIDGE_HEADERS)
            and len(libs_present) == len(REQUIRED_BRIDGE_LIBS)
        ),
    }


def _family_summary(family_id: str, members: list[dict[str, Any]]) -> dict[str, Any]:
    first = members[0]
    paths = [str(member.get("path")) for member in members]
    classifications = sorted({str(member.get("classification")) for member in members})
    issues = sorted(
        {
            str(issue)
            for member in members
            for issue in (member.get("issues") or [])
        }
    )
    bridge_inputs_by_path = {path: _bridge_inputs_for_path(path) for path in paths}
    bridge_rebuild_ready = any(
        bool(inputs.get("bridge_rebuild_ready"))
        for inputs in bridge_inputs_by_path.values()
    )
    path_paper_tts_like = any(_path_is_paper_tts_like(path) for path in paths)
    known_openctp_tts = "known_openctp_tts_rejected" in classifications
    marker_present = any(bool(member.get("trust_marker_present")) for member in members)
    operator_ack_eligible = not known_openctp_tts and not path_paper_tts_like and not marker_present
    family_issues = list(issues)
    if known_openctp_tts:
        family_issues.append("family_known_openctp_tts_rejected")
    if path_paper_tts_like:
        family_issues.append("family_path_paper_tts_rejected")
    if marker_present:
        family_issues.append("family_marker_already_present_requires_discovery_validation")
    if operator_ack_eligible and not bridge_rebuild_ready:
        family_issues.append("bridge_rebuild_inputs_missing_for_candidate_family")
    if operator_ack_eligible:
        family_issues.append("operator_ack_missing")
    return {
        "family_id": family_id,
        "paths": sorted(paths),
        "path_count": len(paths),
        "classifications": classifications,
        "dlls": first.get("dlls"),
        "path_paper_tts_like": path_paper_tts_like,
        "known_openctp_tts": known_openctp_tts,
        "trust_marker_present": marker_present,
        "bridge_rebuild_ready": bridge_rebuild_ready,
        "bridge_inputs_by_path": bridge_inputs_by_path,
        "operator_ack_eligible": operator_ack_eligible,
        "issues": sorted(set(family_issues)),
    }


def _operator_ack_choices(eligible_families: list[dict[str, Any]]) -> list[dict[str, Any]]:
    raw_choices: list[dict[str, Any]] = []
    for family in eligible_families:
        bridge_inputs_by_path = family.get("bridge_inputs_by_path")
        if not isinstance(bridge_inputs_by_path, dict):
            bridge_inputs_by_path = {}
        for path in family["paths"]:
            bridge_inputs = bridge_inputs_by_path.get(path)
            if not isinstance(bridge_inputs, dict):
                bridge_inputs = _bridge_inputs_for_path(path)
            raw_choices.append(
                {
                    "family_id": family["family_id"],
                    "source_bin": path,
                    "dlls": family.get("dlls"),
                    "bridge_rebuild_ready": bool(bridge_inputs.get("bridge_rebuild_ready")),
                    "headers_present": bridge_inputs.get("headers_present"),
                    "headers_missing": bridge_inputs.get("headers_missing"),
                    "libs_present": bridge_inputs.get("libs_present"),
                    "libs_missing": bridge_inputs.get("libs_missing"),
                    "marker_preview_command": (
                        "python scripts\\ctp025292_runtime_pack_trust_marker.py "
                        f"--source-bin \"{path}\" --operator-ack --write "
                        "--output-json var\\stage2\\ctp025292_runtime_pack_trust_marker_write.json"
                    ),
                }
            )
    raw_choices.sort(key=lambda item: (not item["bridge_rebuild_ready"], item["family_id"], item["source_bin"]))
    for rank, choice in enumerate(raw_choices, start=1):
        choice["rank"] = rank
        choice["selection_requires_operator_ack"] = True
        choice["recommended_next_repair"] = (
            "operator-ack this source_bin, then rebuild/sync the route runtime pack against this SDK family before MD smoke"
            if choice["bridge_rebuild_ready"]
            else "operator-ack only after matching SDK headers/libs are supplied or a compatible bridge rebuild path is documented"
        )
    return raw_choices


def build_candidate_approval_packet(discovery: dict[str, Any]) -> dict[str, Any]:
    raw_candidates = discovery.get("candidates")
    candidates = raw_candidates if isinstance(raw_candidates, list) else []
    families_by_id: dict[str, list[dict[str, Any]]] = {}
    for candidate in candidates:
        if not isinstance(candidate, dict):
            continue
        families_by_id.setdefault(_family_id(candidate), []).append(candidate)

    families = [
        _family_summary(family_id, members)
        for family_id, members in sorted(families_by_id.items())
    ]
    eligible = [family for family in families if family["operator_ack_eligible"]]
    rejected = [family for family in families if not family["operator_ack_eligible"]]

    if len(eligible) == 1:
        status = "blocked_waiting_operator_ack"
        blocker_id = "ctp025292_candidate_family_operator_ack_missing"
        issues = ["operator_ack_missing_for_unique_candidate_family"]
    elif len(eligible) == 0:
        status = "blocked_no_operator_ack_eligible_family"
        blocker_id = "ctp025292_candidate_family_unavailable"
        issues = ["operator_ack_eligible_family_missing"]
    else:
        status = "blocked_ambiguous_operator_ack_family"
        blocker_id = "ctp025292_candidate_family_ambiguous"
        issues = ["operator_ack_eligible_family_not_unique"]

    source_bin_choices = _operator_ack_choices(eligible)

    return {
        "baseline": "ctp025292-runtime-pack-candidate-approval-packet-v1",
        "route_scenario": "ctp025292_marketdata_sandbox_paper_simulated_001",
        "runtime_pack_id": RUNTIME_PACK_ID,
        "market_source": "CTP 025292 official market data only",
        "market_data_account_id": "025292",
        "broker_order_submission": False,
        "trading_adapter": "disabled",
        "success": False,
        "status": status,
        "blocker_id": blocker_id,
        "issues": issues,
        "discovery_ref": discovery.get("discovery_ref"),
        "candidate_count": len(candidates),
        "family_count": len(families),
        "operator_ack_eligible_family_count": len(eligible),
        "rejected_family_count": len(rejected),
        "families": families,
        "operator_ack_choices": source_bin_choices,
        "operator_ack_required": True,
        "auto_select_allowed": False,
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
            "Operator must approve exactly one source_bin from operator_ack_choices, then rebuild/sync the route runtime pack and run ctp025292_runtime_lineage_recover.py --write."
            if len(eligible) == 1
            else "Resolve candidate ambiguity by approving exactly one non-Paper/TTS source_bin, or provide a trusted source package before writing a marker."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build a read-only operator approval packet for candidate 025292 CTP DLL families."
    )
    parser.add_argument("--discovery-json", type=Path, default=DEFAULT_DISCOVERY_JSON)
    parser.add_argument("--output-json", type=Path, default=None)
    args = parser.parse_args()

    discovery = json.loads(args.discovery_json.read_text(encoding="utf-8-sig"))
    if not isinstance(discovery, dict):
        raise ValueError("discovery JSON must be an object")
    discovery["discovery_ref"] = str(args.discovery_json)
    payload = build_candidate_approval_packet(discovery)
    print(json.dumps(payload, ensure_ascii=False))
    if args.output_json is not None:
        args.output_json.parent.mkdir(parents=True, exist_ok=True)
        args.output_json.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
