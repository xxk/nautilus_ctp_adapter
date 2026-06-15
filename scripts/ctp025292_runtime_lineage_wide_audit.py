from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
from typing import Any, Iterable

BASELINE = "ctp025292-runtime-lineage-wide-audit-v1"
RUNTIME_PACK_ID = "ctp-live-025292-md"
TRUST_MARKER = "_ctp025292_runtime_pack.json"
REQUIRED_DLLS = ("thostmduserapi_se.dll", "thosttraderapi_se.dll")
DEFAULT_ROOTS = (Path("D:/Nautilus"), Path("D:/wt"))
SKIP_DIR_PARTS = {
    ".git",
    ".pytest_cache",
    "__pycache__",
    "node_modules",
    "pytest_tmp",
    ".pytest_tmp",
}


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def _is_skipped(path: Path) -> bool:
    parts = {part.lower() for part in path.parts}
    return bool(parts & SKIP_DIR_PARTS)


def _walk_named_files(roots: Iterable[Path], filename: str) -> tuple[list[Path], list[Path], list[str]]:
    matches: list[Path] = []
    skipped: list[Path] = []
    missing_roots: list[str] = []
    for root in roots:
        if not root.exists():
            missing_roots.append(str(root))
            continue
        root = root.resolve()
        for current, dirs, files in os.walk(root):
            current_path = Path(current)
            kept_dirs: list[str] = []
            for item in dirs:
                lowered = item.lower()
                if lowered in {"pytest_tmp", ".pytest_tmp"}:
                    skipped.extend(sorted((current_path / item).rglob(filename)))
                    continue
                if lowered in SKIP_DIR_PARTS or item.startswith(".tmp"):
                    continue
                kept_dirs.append(item)
            dirs[:] = kept_dirs
            if filename not in files:
                continue
            candidate = current_path / filename
            try:
                relative_candidate = candidate.resolve().relative_to(root)
            except ValueError:
                relative_candidate = candidate
            if _is_skipped(relative_candidate):
                skipped.append(candidate)
            else:
                matches.append(candidate)
    return sorted(matches), sorted(skipped), missing_roots


def _load_json(path: Path) -> dict[str, Any] | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception:
        return None
    return payload if isinstance(payload, dict) else None


def _dlls(path: Path) -> dict[str, dict[str, Any]]:
    payload: dict[str, dict[str, Any]] = {}
    for filename in REQUIRED_DLLS:
        dll_path = path.parent / filename
        payload[filename] = {
            "exists": dll_path.exists(),
            "sha256": _file_sha256(dll_path) if dll_path.exists() else None,
            "length": dll_path.stat().st_size if dll_path.exists() else None,
        }
    return payload


def _marker_summary(path: Path) -> dict[str, Any]:
    payload = _load_json(path)
    dlls = _dlls(path)
    issues: list[str] = []
    if payload is None:
        issues.append("marker_json_invalid")
        runtime_pack_id = None
        source_kind = None
        marker_dlls = {}
    else:
        runtime_pack_id = payload.get("runtime_pack_id")
        source_kind = payload.get("source_kind")
        marker_dlls = payload.get("dlls") if isinstance(payload.get("dlls"), dict) else {}
    if runtime_pack_id != RUNTIME_PACK_ID:
        issues.append("marker_runtime_pack_id_mismatch")
    if source_kind != "operator_trusted_025292":
        issues.append("marker_source_kind_not_operator_trusted_025292")
    for filename in REQUIRED_DLLS:
        actual = str(dlls[filename]["sha256"] or "").upper()
        marker_value = marker_dlls.get(filename) if isinstance(marker_dlls, dict) else None
        if isinstance(marker_value, dict):
            marker_value = marker_value.get("sha256")
        marker_hash = str(marker_value or "").upper()
        if not actual:
            issues.append(f"marker_source_dll_missing:{filename}")
        elif marker_hash != actual:
            issues.append(f"marker_dll_hash_mismatch:{filename}")
    return {
        "artifact_ref": str(path),
        "sha256": _file_sha256(path),
        "runtime_pack_id": runtime_pack_id,
        "source_kind": source_kind,
        "valid": not issues,
        "issues": issues,
        "dlls": dlls,
    }


def _runtime_pack_dirs_from_manifests(roots: Iterable[Path]) -> tuple[list[Path], list[Path], list[str]]:
    manifests, skipped, missing = _walk_named_files(roots, "_synced_from.txt")
    runtime_manifests: list[Path] = []
    for manifest in manifests:
        try:
            text = manifest.read_text(encoding="utf-8-sig", errors="replace")
        except Exception:
            text = ""
        if RUNTIME_PACK_ID in text or RUNTIME_PACK_ID in str(manifest):
            runtime_manifests.append(manifest)
    return runtime_manifests, skipped, missing


def _runtime_pack_summary(manifest: Path) -> dict[str, Any]:
    values: dict[str, str] = {}
    for line in manifest.read_text(encoding="utf-8-sig", errors="replace").splitlines():
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip()
    dlls = {
        filename: {
            "exists": (manifest.parent / filename).exists(),
            "sha256": _file_sha256(manifest.parent / filename)
            if (manifest.parent / filename).exists()
            else None,
        }
        for filename in REQUIRED_DLLS
    }
    return {
        "manifest_ref": str(manifest),
        "sha256": _file_sha256(manifest),
        "runtime_pack_id": values.get("runtime_pack_id"),
        "profile": values.get("profile"),
        "loader_isolation": values.get("loader_isolation"),
        "valid_materialized_pack": (
            values.get("runtime_pack_id") == RUNTIME_PACK_ID
            and values.get("loader_isolation") == "fresh_worker_process_per_runtime_pack"
            and all(item["exists"] for item in dlls.values())
        ),
        "dlls": dlls,
    }


def _source_package_summary(path: Path) -> dict[str, Any]:
    payload = _load_json(path)
    runtime_pack = payload.get("runtime_pack") if isinstance(payload, dict) else None
    runtime_pack = runtime_pack if isinstance(runtime_pack, dict) else {}
    return {
        "artifact_ref": str(path),
        "sha256": _file_sha256(path),
        "schema_version": payload.get("schema_version") if isinstance(payload, dict) else None,
        "account_id": payload.get("account_id") if isinstance(payload, dict) else None,
        "runtime_pack_id": runtime_pack.get("runtime_pack_id"),
        "has_required_dll_hashes": all(
            filename in json.dumps(runtime_pack, ensure_ascii=False)
            for filename in REQUIRED_DLLS
        ),
        "valid_runtime_lineage_source": (
            runtime_pack.get("runtime_pack_id") == RUNTIME_PACK_ID
            and all(filename in json.dumps(runtime_pack, ensure_ascii=False) for filename in REQUIRED_DLLS)
        ),
    }


def audit_wide_runtime_lineage(roots: list[Path] | None = None) -> dict[str, Any]:
    roots = roots or list(DEFAULT_ROOTS)
    marker_paths, skipped_markers, missing_roots = _walk_named_files(roots, TRUST_MARKER)
    markers = [_marker_summary(path) for path in marker_paths]
    valid_markers = [item for item in markers if item["valid"]]

    source_paths, skipped_source_packages, missing_source_roots = _walk_named_files(roots, "source-package.json")
    source_paths = [
        path
        for path in source_paths
        if "025292" in str(path).lower() or "ctp-live" in str(path).lower()
    ]
    source_packages = [_source_package_summary(path) for path in source_paths]
    valid_source_packages = [item for item in source_packages if item["valid_runtime_lineage_source"]]

    runtime_manifests, skipped_manifests, missing_manifest_roots = _runtime_pack_dirs_from_manifests(roots)
    runtime_packs = [_runtime_pack_summary(path) for path in runtime_manifests]
    valid_runtime_packs = [item for item in runtime_packs if item["valid_materialized_pack"]]

    issues: list[str] = []
    if not valid_markers:
        issues.append("production_operator_trusted_marker_missing")
    if not valid_runtime_packs:
        issues.append("materialized_ctp_live_025292_runtime_pack_missing")
    if not valid_source_packages:
        issues.append("account_console_ctp025292_source_package_missing")
    success = len(valid_markers) == 1 and bool(valid_runtime_packs) and bool(valid_source_packages)
    return {
        "baseline": BASELINE,
        "route_scenario": "ctp025292_marketdata_sandbox_paper_simulated_001",
        "runtime_pack_id": RUNTIME_PACK_ID,
        "market_source": "CTP 025292 official market data only",
        "market_data_account_id": "025292",
        "broker_order_submission": False,
        "trading_adapter": "disabled",
        "success": success,
        "status": "passed" if success else "blocked",
        "blocker_id": None if success else "ctp025292_wide_runtime_lineage_unready",
        "issues": issues,
        "roots": [str(root) for root in roots],
        "missing_roots": sorted(set(missing_roots + missing_source_roots + missing_manifest_roots)),
        "marker_count": len(markers),
        "valid_marker_count": len(valid_markers),
        "skipped_test_marker_count": len(skipped_markers),
        "source_package_count": len(source_packages),
        "valid_source_package_count": len(valid_source_packages),
        "skipped_test_source_package_count": len(skipped_source_packages),
        "runtime_pack_manifest_count": len(runtime_packs),
        "valid_runtime_pack_count": len(valid_runtime_packs),
        "skipped_manifest_count": len(skipped_manifests),
        "markers": markers,
        "source_packages": source_packages,
        "runtime_packs": runtime_packs,
        "negative_assertions": {
            "did_not_open_trading_channel": True,
            "did_not_submit_broker_order": True,
            "did_not_use_025292_as_trading_account": True,
            "did_not_materialize_runtime_pack": True,
            "did_not_write_account_console_source_package": True,
            "did_not_generate_or_consume_paper_request": True,
            "did_not_claim_market_data_ready": True,
        },
        "next_action": (
            "Run ctp025292_runtime_lineage_recover.py --write with the discovered trusted marker."
            if success
            else "Create or restore production runtime lineage: exactly one operator_trusted_025292 marker, materialized ctp-live-025292-md runtime pack, and Account Console ctp-live-025292/source-package.json."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Wide read-only audit for production CTP 025292 runtime markers/source packages."
    )
    parser.add_argument("--root", type=Path, action="append", default=None)
    parser.add_argument("--output-json", type=Path, default=None)
    args = parser.parse_args()

    payload = audit_wide_runtime_lineage(args.root)
    print(json.dumps(payload, ensure_ascii=False))

    if args.output_json is not None:
        args.output_json.parent.mkdir(parents=True, exist_ok=True)
        args.output_json.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    return 0 if payload["success"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
