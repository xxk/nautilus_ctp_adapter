from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

BASELINE = "ctp025292-md-login-payload-lineage-compare-v1"
ROUTE_SCENARIO = "ctp025292_marketdata_sandbox_paper_simulated_001"
RUNTIME_PACK_ID = "ctp-live-025292-md"
MARKET_SOURCE = "CTP 025292 official market data only"
MARKET_DATA_ACCOUNT_ID = "025292"
HISTORICAL_CONFIG_NAME = "ctp.live.025292.rb2610.10675.json"

SCANNED_EXTENSIONS = {".json", ".log", ".md", ".txt"}
SKIP_DIR_PARTS = {
    ".git",
    ".pytest_cache",
    "__pycache__",
    "node_modules",
    "pytest_tmp",
    ".pytest_tmp",
}

SUCCESS_PATTERNS = {
    "login_success_true": re.compile(r'"login_success"\s*:\s*true|login_success\s*=\s*true', re.I),
    "md_on_rsp_user_login": re.compile(r"MD\s+OnRspUserLogin\s+called", re.I),
    "md_auto_login_025292": re.compile(r"MD\s+Auto-login:\s*0155/025292", re.I),
    "first_tick_rb2610": re.compile(r"first_tick_symbol[\"=:\s]+rb2610|first_tick_symbol\"\s*:\s*\"rb2610\"", re.I),
    "login_succeeded_event": re.compile(r"login_succeeded", re.I),
}
PAYLOAD_HINT_PATTERNS = {
    "historical_config_ref": re.compile(re.escape(HISTORICAL_CONFIG_NAME), re.I),
    "appid_hint": re.compile(r"\bAppID\b|\bapp_id\b", re.I),
    "authcode_hint": re.compile(r"\bAuthCode\b|\bauth_code\b", re.I),
    "productinfo_hint": re.compile(r"\bProductInfo\b|\bproduct_info\b|\biQuant\b", re.I),
    "compatibility_hint": re.compile(
        r"UserProductInfo|InterfaceProductInfo|ProtocolInfo|MacAddress|ClientIPAddress|LoginRemark",
        re.I,
    ),
    "native_pack_hint": re.compile(r"NativePackDir|runtime_pack_id|source-package|thostmduserapi", re.I),
}

SECRET_FIELD_NAMES = {
    "password",
    "auth_code",
    "authcode",
    "app_id",
    "appid",
    "md_front",
    "td_front",
    "pricer",
    "host",
    "行情服务器",
    "交易服务器",
    "front",
    "mac_address",
    "macaddress",
    "client_ip_address",
    "clientipaddress",
    "login_remark",
    "loginremark",
}


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def _fingerprint(value: Any) -> dict[str, Any]:
    text = "" if value is None else str(value)
    present = bool(text.strip())
    return {
        "present": present,
        "length": len(text) if present else 0,
        "sha256_prefix": hashlib.sha256(text.encode("utf-8")).hexdigest().upper()[:16]
        if present
        else None,
        "raw_value_recorded": False,
    }


def _load_json(path: Path) -> dict[str, Any] | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception:
        return None
    return payload if isinstance(payload, dict) else None


def _first(values: dict[str, Any], *keys: str, default: Any = "") -> Any:
    for key in keys:
        if key in values and values[key] is not None:
            return values[key]
    lowered = {str(key).lower(): value for key, value in values.items()}
    for key in keys:
        lowered_key = key.lower()
        if lowered_key in lowered and lowered[lowered_key] is not None:
            return lowered[lowered_key]
    return default


def _config_summary(path: Path) -> dict[str, Any]:
    payload = _load_json(path)
    summary: dict[str, Any] = {
        "artifact_ref": str(path),
        "exists": path.exists(),
        "sha256": _file_sha256(path) if path.exists() else None,
        "json_valid": payload is not None,
        "broker_id": None,
        "user_id": None,
        "instruments": [],
        "secret_values_recorded": False,
        "sensitive_fields": {},
        "diagnostic_fields": {},
        "md_login_compatibility": {},
    }
    if payload is None:
        return summary

    instruments = _first(payload, "instruments", "Instruments", default=[])
    if isinstance(instruments, str):
        instruments = [instruments]
    summary["broker_id"] = str(_first(payload, "broker_id", "BrokerID", "经纪商代码"))
    summary["user_id"] = str(_first(payload, "user_id", "UserID", "用户名"))
    summary["instruments"] = [str(item) for item in instruments] if isinstance(instruments, list) else []

    for output_name, keys in {
        "password": ("password", "Password", "密码"),
        "auth_code": ("auth_code", "AuthCode", "授权编码"),
        "app_id": ("app_id", "AppID"),
        "md_front": ("md_front", "Pricer", "行情服务器"),
        "td_front": ("td_front", "Host", "交易服务器"),
    }.items():
        summary["sensitive_fields"][output_name] = _fingerprint(_first(payload, *keys))

    for output_name, keys in {
        "product_info": ("product_info", "ProductInfo", "service", "Service", "产品名称"),
        "native_pack_dir": ("native_pack_dir", "NativePackDir"),
        "post_login_delay_seconds": ("post_login_delay_seconds", "PostLoginDelaySeconds"),
    }.items():
        value = _first(payload, *keys)
        field = _fingerprint(value)
        if output_name == "post_login_delay_seconds":
            field["value"] = int(value or 0)
        summary["diagnostic_fields"][output_name] = field

    compat_payload = _first(payload, "md_login_compatibility", "MdLoginCompatibility", default={}) or {}
    if not isinstance(compat_payload, dict):
        compat_payload = {}
    for top_key, compat_key in {
        "interface_product_info": "InterfaceProductInfo",
        "protocol_info": "ProtocolInfo",
        "mac_address": "MacAddress",
        "client_ip_address": "ClientIPAddress",
        "login_remark": "LoginRemark",
    }.items():
        value = _first(payload, top_key, compat_key, default=_first(compat_payload, top_key, compat_key))
        summary["md_login_compatibility"][top_key] = _fingerprint(value)

    return summary


def _has_skipped_part(path: Path) -> bool:
    return any(part in SKIP_DIR_PARTS for part in path.parts)


def _text_files(root: Path) -> list[Path]:
    if not root.exists():
        return []
    if root.is_file():
        return [root] if root.suffix.lower() in SCANNED_EXTENSIONS else []
    files: list[Path] = []
    for path in root.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in SCANNED_EXTENSIONS:
            continue
        try:
            relative = path.relative_to(root)
        except ValueError:
            relative = path
        if _has_skipped_part(relative):
            continue
        files.append(path)
    return sorted(files, key=lambda item: str(item).lower())


def _pattern_hits(text: str, patterns: dict[str, re.Pattern[str]]) -> dict[str, list[int]]:
    hits: dict[str, list[int]] = {}
    for lineno, line in enumerate(text.splitlines(), start=1):
        for name, pattern in patterns.items():
            if pattern.search(line):
                hits.setdefault(name, []).append(lineno)
    return {name: lines[:8] for name, lines in hits.items()}


def _scan_historical_roots(roots: list[Path]) -> dict[str, Any]:
    missing_roots = [str(root) for root in roots if not root.exists()]
    success_refs: list[dict[str, Any]] = []
    payload_hint_refs: list[dict[str, Any]] = []
    config_candidates: list[Path] = []
    seen_files: set[str] = set()

    for root in roots:
        for path in _text_files(root):
            resolved = str(path.resolve())
            if resolved in seen_files:
                continue
            seen_files.add(resolved)
            if path.name == HISTORICAL_CONFIG_NAME:
                config_candidates.append(path)
            text = path.read_text(encoding="utf-8-sig", errors="replace")
            if "025292" not in text and HISTORICAL_CONFIG_NAME not in text:
                continue
            success_hits = _pattern_hits(text, SUCCESS_PATTERNS)
            if success_hits:
                success_refs.append(
                    {
                        "artifact_ref": str(path),
                        "sha256": _file_sha256(path),
                        "matched_patterns": sorted(success_hits),
                        "line_numbers": success_hits,
                        "raw_lines_recorded": False,
                    }
                )
            payload_hits = _pattern_hits(text, PAYLOAD_HINT_PATTERNS)
            if payload_hits:
                payload_hint_refs.append(
                    {
                        "artifact_ref": str(path),
                        "sha256": _file_sha256(path),
                        "matched_patterns": sorted(payload_hits),
                        "line_numbers": payload_hits,
                        "raw_lines_recorded": False,
                    }
                )

    historical_config_summaries = [_config_summary(path) for path in sorted(set(config_candidates))]
    return {
        "roots": [str(root) for root in roots],
        "missing_roots": missing_roots,
        "scanned_file_count": len(seen_files),
        "historical_success_ref_count": len(success_refs),
        "payload_hint_ref_count": len(payload_hint_refs),
        "historical_config_candidate_count": len(historical_config_summaries),
        "historical_success_refs": success_refs[:12],
        "payload_hint_refs": payload_hint_refs[:12],
        "historical_config_summaries": historical_config_summaries,
    }


def _compare_config_fingerprints(
    current: dict[str, Any],
    historical_configs: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    comparisons: list[dict[str, Any]] = []
    for historical in historical_configs:
        fields: dict[str, Any] = {}
        for section_name in ("sensitive_fields", "diagnostic_fields", "md_login_compatibility"):
            current_section = current.get(section_name, {})
            historical_section = historical.get(section_name, {})
            if not isinstance(current_section, dict) or not isinstance(historical_section, dict):
                continue
            for field_name, current_value in current_section.items():
                historical_value = historical_section.get(field_name)
                if not isinstance(current_value, dict) or not isinstance(historical_value, dict):
                    continue
                fields[f"{section_name}.{field_name}"] = {
                    "current_present": current_value.get("present"),
                    "historical_present": historical_value.get("present"),
                    "fingerprint_equal": (
                        current_value.get("sha256_prefix") == historical_value.get("sha256_prefix")
                        and bool(current_value.get("present"))
                        and bool(historical_value.get("present"))
                    ),
                    "raw_values_recorded": False,
                }
        comparisons.append(
            {
                "historical_config_ref": historical.get("artifact_ref"),
                "historical_config_sha256": historical.get("sha256"),
                "broker_id_equal": current.get("broker_id") == historical.get("broker_id"),
                "user_id_equal": current.get("user_id") == historical.get("user_id"),
                "field_fingerprint_comparison": fields,
            }
        )
    return comparisons


def _lifecycle_summary(path: Path | None) -> dict[str, Any] | None:
    if path is None:
        return None
    payload = _load_json(path)
    if payload is None:
        return {
            "artifact_ref": str(path),
            "exists": path.exists(),
            "json_valid": False,
        }
    diagnosis = payload.get("diagnosis", {}) if isinstance(payload.get("diagnosis"), dict) else {}
    latency = (
        payload.get("dispatch_to_disconnect_latency", {})
        if isinstance(payload.get("dispatch_to_disconnect_latency"), dict)
        else {}
    )
    return {
        "artifact_ref": str(path),
        "exists": path.exists(),
        "sha256": _file_sha256(path) if path.exists() else None,
        "json_valid": True,
        "blocker_id": payload.get("blocker_id"),
        "event_counts": payload.get("event_counts"),
        "login_response_count": payload.get("login_response_count"),
        "tick_count": payload.get("tick_count"),
        "return_codes": payload.get("return_codes"),
        "disconnect_reasons": payload.get("disconnect_reasons"),
        "dispatch_to_disconnect_avg_ms": latency.get("avg_ms"),
        "signature": diagnosis.get("signature"),
        "broker_side_rejection_captured": False,
        "raw_secret_values_recorded": False,
    }


def compare_payload_lineage(
    *,
    current_config: Path,
    historical_roots: list[Path],
    lifecycle_summary_path: Path | None,
) -> dict[str, Any]:
    current_summary = _config_summary(current_config)
    historical = _scan_historical_roots(historical_roots)
    lifecycle = _lifecycle_summary(lifecycle_summary_path)
    comparisons = _compare_config_fingerprints(
        current_summary,
        historical["historical_config_summaries"],
    )

    issues: list[str] = []
    if not current_summary["exists"]:
        issues.append("current_025292_config_missing")
    if current_summary.get("user_id") != MARKET_DATA_ACCOUNT_ID:
        issues.append("current_config_user_id_not_025292")
    if historical["historical_success_ref_count"] == 0:
        issues.append("historical_025292_success_refs_missing")
    if historical["historical_config_candidate_count"] == 0:
        issues.append("known_success_payload_config_artifact_missing")
    if historical["historical_success_ref_count"] > 0 and historical["historical_config_candidate_count"] == 0:
        issues.append("historical_success_payload_values_unavailable")
    if lifecycle is not None and lifecycle.get("login_response_count") == 0:
        issues.append("broker_side_login_rejection_detail_not_captured")
    if not current_summary["diagnostic_fields"]["native_pack_dir"]["present"]:
        issues.append("current_config_native_pack_dir_empty_requires_runtime_pack_overlay")

    success = not issues and bool(comparisons)
    blocker_id = None if success else "ctp025292_md_login_payload_success_lineage_unavailable"
    return {
        "baseline": BASELINE,
        "route_scenario": ROUTE_SCENARIO,
        "runtime_pack_id": RUNTIME_PACK_ID,
        "market_source": MARKET_SOURCE,
        "market_data_account_id": MARKET_DATA_ACCOUNT_ID,
        "broker_order_submission": False,
        "trading_adapter": "disabled",
        "success": success,
        "status": "passed_payload_lineage_compare" if success else "blocked",
        "blocker_id": blocker_id,
        "issues": issues,
        "current_config_summary": current_summary,
        "historical_scan_summary": {
            key: historical[key]
            for key in (
                "roots",
                "missing_roots",
                "scanned_file_count",
                "historical_success_ref_count",
                "payload_hint_ref_count",
                "historical_config_candidate_count",
            )
        },
        "historical_success_refs": historical["historical_success_refs"],
        "payload_hint_refs": historical["payload_hint_refs"],
        "historical_config_summaries": historical["historical_config_summaries"],
        "config_fingerprint_comparisons": comparisons,
        "lifecycle_summary": lifecycle,
        "diagnosis": {
            "current_config_loaded_with_secrets_redacted": bool(current_summary["json_valid"]),
            "historical_success_is_known": historical["historical_success_ref_count"] > 0,
            "historical_success_payload_materialized": historical["historical_config_candidate_count"] > 0,
            "payload_delta_decidable": bool(comparisons),
            "explicit_broker_rejection_captured": False,
            "does_not_prove_credentials_valid_or_invalid": True,
            "does_not_override_runtime_lineage_pass": True,
            "does_not_satisfy_market_data_preflight": True,
        },
        "negative_assertions": {
            "did_not_open_trading_channel": True,
            "did_not_submit_broker_order": True,
            "did_not_use_025292_as_trading_account": True,
            "did_not_generate_or_consume_paper_request": True,
            "did_not_claim_market_data_ready": True,
            "did_not_claim_paper_ready": True,
            "did_not_claim_live_ready": True,
            "did_not_enter_stage3": True,
            "secret_values_recorded": False,
        },
        "next_action": (
            "Recover or provide the historical successful 025292 MD payload/config fingerprint "
            f"({HISTORICAL_CONFIG_NAME}) or add native MD SPI/network-close detail that captures "
            "why the front closes after ReqUserLogin return_code=0; then retry only read-only 025292 "
            "MD smoke for ag2612 under ctp-live-025292-md."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Compare current 025292 MD login payload/config lineage against known success refs."
    )
    parser.add_argument("--current-config", type=Path, required=True)
    parser.add_argument("--historical-root", type=Path, action="append", required=True)
    parser.add_argument("--lifecycle-summary", type=Path, default=None)
    parser.add_argument("--output-json", type=Path, default=None)
    args = parser.parse_args()

    payload = compare_payload_lineage(
        current_config=args.current_config,
        historical_roots=args.historical_root,
        lifecycle_summary_path=args.lifecycle_summary,
    )
    print(json.dumps(payload, ensure_ascii=False))
    if args.output_json is not None:
        args.output_json.parent.mkdir(parents=True, exist_ok=True)
        args.output_json.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return 0 if payload["success"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
