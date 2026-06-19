from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

BASELINE = "ctp025292-runtime-pack-discover-v1"
RUNTIME_PACK_ID = "ctp-live-025292-md"
REQUIRED_DLLS = ("thostmduserapi_se.dll", "thosttraderapi_se.dll")
KNOWN_OPENCTP_TTS_DLL_SHA256 = {
    "thostmduserapi_se.dll": "66BACF7E33AD901534DA4B08662F08FC9F6169760B2AA0EEA85766C93FB6501E",
    "thosttraderapi_se.dll": "543ECE8B55C6FBC671B251E8CC0EE909708EE0F3C5ADC4FD2FD542E3B4C8D4E1",
}
TRUST_MARKER = "_ctp025292_runtime_pack.json"
SKIP_DIR_PARTS = {
    ".git",
    ".pytest_cache",
    "__pycache__",
    "pytest_tmp",
    ".pytest_tmp",
    "node_modules",
}


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def _has_skipped_part(path: Path) -> bool:
    return any(part in SKIP_DIR_PARTS for part in path.parts)


def _candidate_dirs(root: Path) -> list[Path]:
    if not root.exists():
        return []
    if root.is_file():
        root = root.parent
    if all((root / filename).exists() for filename in REQUIRED_DLLS):
        return [root]
    dirs: dict[str, Path] = {}
    for match in root.rglob(REQUIRED_DLLS[0]):
        try:
            relative_match = match.relative_to(root)
        except ValueError:
            relative_match = match
        if _has_skipped_part(relative_match):
            continue
        candidate = match.parent
        if all((candidate / filename).exists() for filename in REQUIRED_DLLS):
            dirs[str(candidate.resolve())] = candidate
    return sorted(dirs.values(), key=lambda path: str(path).lower())


def _dlls(candidate: Path) -> dict[str, dict[str, Any]]:
    payload: dict[str, dict[str, Any]] = {}
    for filename in REQUIRED_DLLS:
        path = candidate / filename
        payload[filename] = {
            "sha256": _file_sha256(path),
            "length": path.stat().st_size,
        }
    return payload


def _load_trust_marker(candidate: Path) -> dict[str, Any] | None:
    marker_path = candidate / TRUST_MARKER
    if not marker_path.exists():
        return None
    payload = json.loads(marker_path.read_text(encoding="utf-8-sig"))
    if not isinstance(payload, dict):
        raise ValueError(f"{marker_path}: trust marker must be a JSON object")
    return payload


def _marker_matches(marker: dict[str, Any] | None, dlls: dict[str, dict[str, Any]]) -> bool:
    if marker is None:
        return False
    if marker.get("runtime_pack_id") != RUNTIME_PACK_ID:
        return False
    if marker.get("source_kind") != "operator_trusted_025292":
        return False
    marker_dlls = marker.get("dlls")
    if not isinstance(marker_dlls, dict):
        return False
    for filename in REQUIRED_DLLS:
        expected = marker_dlls.get(filename)
        if isinstance(expected, dict):
            expected = expected.get("sha256")
        if str(expected or "").upper() != str(dlls[filename]["sha256"]).upper():
            return False
    return True


def _classification(candidate: Path, dlls: dict[str, dict[str, Any]]) -> tuple[str, list[str], dict[str, Any] | None]:
    issues: list[str] = []
    marker = _load_trust_marker(candidate)
    all_openctp_tts = all(
        dlls[filename]["sha256"] == KNOWN_OPENCTP_TTS_DLL_SHA256[filename]
        for filename in REQUIRED_DLLS
    )
    if all_openctp_tts:
        issues.append("candidate_known_openctp_tts")
        return "known_openctp_tts_rejected", issues, marker
    if _marker_matches(marker, dlls):
        return "operator_trusted_025292", issues, marker
    if marker is not None:
        issues.append("trust_marker_present_but_invalid")
    else:
        issues.append("trust_marker_missing")
    return "candidate_untrusted", issues, marker


def discover_runtime_packs(roots: list[Path]) -> dict[str, Any]:
    candidates: list[dict[str, Any]] = []
    seen: set[str] = set()
    for root in roots:
        for candidate_dir in _candidate_dirs(root):
            key = str(candidate_dir.resolve())
            if key in seen:
                continue
            seen.add(key)
            dll_payload = _dlls(candidate_dir)
            classification, issues, marker = _classification(candidate_dir, dll_payload)
            candidates.append(
                {
                    "path": str(candidate_dir),
                    "classification": classification,
                    "issues": issues,
                    "dlls": dll_payload,
                    "trust_marker_present": marker is not None,
                    "path_mentions_025292": "025292" in str(candidate_dir),
                }
            )

    trusted = [item for item in candidates if item["classification"] == "operator_trusted_025292"]
    payload: dict[str, Any] = {
        "baseline": BASELINE,
        "runtime_pack_id": RUNTIME_PACK_ID,
        "route_scenario": "ctp025292_marketdata_sandbox_paper_simulated_001",
        "market_source": "CTP 025292 official market data only",
        "market_data_account_id": "025292",
        "broker_order_submission": False,
        "trading_adapter": "disabled",
        "success": bool(trusted),
        "status": "trusted_source_found" if trusted else "blocked",
        "blocker_id": None if trusted else "ctp025292_runtime_pack_source_unready",
        "roots": [str(root) for root in roots],
        "candidate_count": len(candidates),
        "trusted_candidate_count": len(trusted),
        "candidates": candidates,
        "negative_assertions": {
            "did_not_open_trading_channel": True,
            "did_not_submit_broker_order": True,
            "did_not_generate_or_consume_paper_request": True,
            "did_not_claim_market_data_ready": True,
        },
        "next_action": (
            "Use the operator_trusted_025292 candidate with ctp025292_runtime_pack_materialize.py"
            if trusted
            else "Provide a trust marker or an operator-trusted 025292 DLL source directory, then rerun discovery."
        ),
    }
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Inventory same-name CTP DLL candidate directories for the 025292 market-data runtime pack."
    )
    parser.add_argument("--root", type=Path, action="append", required=True)
    parser.add_argument("--output-json", type=Path, default=None)
    args = parser.parse_args()

    payload = discover_runtime_packs(args.root)
    print(json.dumps(payload, ensure_ascii=False))

    if args.output_json is not None:
        args.output_json.parent.mkdir(parents=True, exist_ok=True)
        args.output_json.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    return 0 if payload["success"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
