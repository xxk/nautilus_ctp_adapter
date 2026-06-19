from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

BASELINE = "ctp025292-historical-runtime-lineage-audit-v1"
ROUTE_SCENARIO = "ctp025292_marketdata_sandbox_paper_simulated_001"
RUNTIME_PACK_ID = "ctp-live-025292-md"
HISTORICAL_CONFIG_NAME = "ctp.live.025292.rb2610.10675.json"
REQUIRED_DLLS = ("thostmduserapi_se.dll", "thosttraderapi_se.dll")
SCANNED_EXTENSIONS = {".json", ".log", ".md", ".txt"}
SKIP_DIR_PARTS = {
    ".git",
    ".pytest_cache",
    "__pycache__",
    "node_modules",
    "pytest_tmp",
    ".pytest_tmp",
}

SUCCESS_PATTERNS = (
    re.compile(r'"login_success"\s*:\s*true', re.IGNORECASE),
    re.compile(r"login_success\s*=\s*true", re.IGNORECASE),
    re.compile(r'"ready"\s*:\s*true', re.IGNORECASE),
    re.compile(r"\bready\s*=\s*true\b", re.IGNORECASE),
    re.compile(r"TD Auto-auth:\s*\S+/025292", re.IGNORECASE),
    re.compile(r'"account_id"\s*:\s*"025292"', re.IGNORECASE),
)
RUNTIME_LINEAGE_KEYWORDS = (
    "runtime_pack_id",
    RUNTIME_PACK_ID,
    "source-package.json",
    "source_package",
    "_synced_from",
    "vendor/ctp",
    "vendor\\ctp",
    "vnpy_ctp",
    "thostmduserapi",
    "thosttraderapi",
)
SHA256_PATTERN = re.compile(r"\b[A-Fa-f0-9]{64}\b")


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


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


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig", errors="replace")


def _matching_lines(text: str, patterns: tuple[re.Pattern[str], ...] | tuple[str, ...]) -> list[str]:
    matches: list[str] = []
    for lineno, line in enumerate(text.splitlines(), start=1):
        if all(isinstance(pattern, str) for pattern in patterns):
            hit = any(str(pattern).lower() in line.lower() for pattern in patterns)
        else:
            hit = any(pattern.search(line) for pattern in patterns if isinstance(pattern, re.Pattern))
        if hit:
            matches.append(f"{lineno}: {line.strip()[:240]}")
        if len(matches) >= 4:
            break
    return matches


def _success_ref(path: Path, text: str) -> dict[str, Any] | None:
    if "025292" not in text:
        return None
    if not any(pattern.search(text) for pattern in SUCCESS_PATTERNS):
        return None
    return {
        "artifact_ref": str(path),
        "sha256": _file_sha256(path),
        "evidence_type": "historical_025292_success",
        "matching_lines": _matching_lines(text, SUCCESS_PATTERNS),
    }


def _runtime_lineage_ref(path: Path, text: str) -> dict[str, Any] | None:
    lowered = text.lower()
    keywords = [keyword for keyword in RUNTIME_LINEAGE_KEYWORDS if keyword.lower() in lowered]
    if not keywords:
        return None
    return {
        "artifact_ref": str(path),
        "sha256": _file_sha256(path),
        "keywords": sorted(set(keywords)),
        "matching_lines": _matching_lines(text, tuple(keywords)),
    }


def _trusted_runtime_hash_ref(path: Path, text: str) -> dict[str, Any] | None:
    lowered = text.lower()
    has_runtime_pack = RUNTIME_PACK_ID.lower() in lowered or "runtime_pack_id" in lowered
    has_required_dll_names = all(filename.lower() in lowered for filename in REQUIRED_DLLS)
    hashes = sorted(set(match.upper() for match in SHA256_PATTERN.findall(text)))
    if not (has_runtime_pack and has_required_dll_names and len(hashes) >= 2):
        return None
    return {
        "artifact_ref": str(path),
        "sha256": _file_sha256(path),
        "runtime_pack_id": RUNTIME_PACK_ID,
        "hash_count": len(hashes),
        "hashes": hashes[:8],
    }


def audit_historical_runtime_lineage(
    roots: list[Path],
    *,
    historical_config: Path | None = None,
) -> dict[str, Any]:
    success_refs: list[dict[str, Any]] = []
    runtime_lineage_refs: list[dict[str, Any]] = []
    trusted_runtime_hash_refs: list[dict[str, Any]] = []
    missing_roots = [str(root) for root in roots if not root.exists()]

    seen_files: set[str] = set()
    for root in roots:
        for path in _text_files(root):
            key = str(path.resolve())
            if key in seen_files:
                continue
            seen_files.add(key)
            text = _read_text(path)
            success = _success_ref(path, text)
            if success is not None:
                success_refs.append(success)
            lineage = _runtime_lineage_ref(path, text)
            if lineage is not None:
                runtime_lineage_refs.append(lineage)
            trusted = _trusted_runtime_hash_ref(path, text)
            if trusted is not None:
                trusted_runtime_hash_refs.append(trusted)

    issues: list[str] = []
    if missing_roots:
        issues.append("audit_root_missing")
    if not success_refs:
        issues.append("historical_success_evidence_missing")
    if success_refs and not trusted_runtime_hash_refs:
        issues.append("historical_success_runtime_hash_missing")

    config_payload: dict[str, Any] | None = None
    if historical_config is not None:
        config_payload = {
            "artifact_ref": str(historical_config),
            "exists": historical_config.exists(),
        }
        if historical_config.exists():
            config_payload["sha256"] = _file_sha256(historical_config)
        else:
            issues.append("historical_success_config_missing")

    success = bool(success_refs and trusted_runtime_hash_refs and not issues)
    return {
        "baseline": BASELINE,
        "route_scenario": ROUTE_SCENARIO,
        "runtime_pack_id": RUNTIME_PACK_ID,
        "market_source": "CTP 025292 official market data only",
        "market_data_account_id": "025292",
        "broker_order_submission": False,
        "trading_adapter": "disabled",
        "historical_config_name": HISTORICAL_CONFIG_NAME,
        "roots": [str(root) for root in roots],
        "missing_roots": missing_roots,
        "scanned_file_count": len(seen_files),
        "historical_success_ref_count": len(success_refs),
        "runtime_lineage_ref_count": len(runtime_lineage_refs),
        "trusted_runtime_hash_ref_count": len(trusted_runtime_hash_refs),
        "historical_config": config_payload,
        "success": success,
        "status": "trusted_historical_lineage_found" if success else "blocked",
        "blocker_id": None if success else "ctp025292_historical_success_runtime_hash_missing",
        "issues": issues,
        "historical_success_refs": success_refs,
        "runtime_lineage_refs": runtime_lineage_refs,
        "trusted_runtime_hash_refs": trusted_runtime_hash_refs,
        "candidate_auto_trust_allowed": success,
        "negative_assertions": {
            "did_not_open_trading_channel": True,
            "did_not_submit_broker_order": True,
            "did_not_generate_or_consume_paper_request": True,
            "did_not_claim_market_data_ready": True,
        },
        "next_action": (
            "Use the trusted historical runtime hash refs to materialize the 025292 runtime pack."
            if success
            else "Restore/provide trusted 025292 source-package/runtime manifest with DLL hashes, or write an operator-trusted marker for the correct 025292 DLL family before retrying MD smoke."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Audit historical 025292 success evidence for route-bound runtime DLL/source lineage."
    )
    parser.add_argument("--root", type=Path, action="append", required=True)
    parser.add_argument("--historical-config", type=Path, default=None)
    parser.add_argument("--output-json", type=Path, default=None)
    args = parser.parse_args()

    payload = audit_historical_runtime_lineage(
        args.root,
        historical_config=args.historical_config,
    )
    print(json.dumps(payload, ensure_ascii=False))

    if args.output_json is not None:
        args.output_json.parent.mkdir(parents=True, exist_ok=True)
        args.output_json.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    return 0 if payload["success"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
