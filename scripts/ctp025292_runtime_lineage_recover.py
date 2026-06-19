from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.ctp025292_runtime_pack_discover import discover_runtime_packs
from scripts.ctp025292_runtime_pack_materialize import build_runtime_pack_summary
from scripts.ctp025292_source_lineage_gate import build_lineage_summary
from scripts.ctp025292_source_package_build import (
    DEFAULT_RUNTIME_BIN,
    DEFAULT_SOURCE_PACKAGE,
    build_source_package_summary,
)

BASELINE = "ctp025292-runtime-lineage-recover-v1"
RUNTIME_PACK_ID = "ctp-live-025292-md"
DEFAULT_ROOTS = (
    Path("D:/Nautilus/nautilus_ctp_adapter/vendor/ctp/bin"),
    Path("D:/Nautilus/nautilus_ctp_adapter/output"),
    Path("D:/wt/main/.venv/Lib/site-packages/vnpy_ctp/api"),
)
DEFAULT_CONFIG = REPO_ROOT / "cfgs" / "local" / "ctp.live.025292.local.json"


def _stage_status(success: bool, blocker_id: str | None) -> dict[str, Any]:
    return {
        "success": success,
        "status": "passed" if success else "blocked",
        "blocker_id": blocker_id if not success else None,
    }


def recover_runtime_lineage(
    *,
    roots: list[Path] | None = None,
    runtime_bin: Path = DEFAULT_RUNTIME_BIN,
    source_package_path: Path = DEFAULT_SOURCE_PACKAGE,
    config_path: Path = DEFAULT_CONFIG,
    write: bool = False,
) -> dict[str, Any]:
    roots = roots or list(DEFAULT_ROOTS)
    discovery = discover_runtime_packs(roots)
    trusted = [
        candidate
        for candidate in discovery["candidates"]
        if candidate.get("classification") == "operator_trusted_025292"
    ]

    materialize: dict[str, Any] | None = None
    source_package: dict[str, Any] | None = None
    lineage: dict[str, Any] | None = None
    issues: list[str] = []

    if len(trusted) == 0:
        issues.append("trusted_runtime_pack_candidate_missing")
    elif len(trusted) > 1:
        issues.append("trusted_runtime_pack_candidate_ambiguous")
    else:
        materialize = build_runtime_pack_summary(
            source_bin=Path(str(trusted[0]["path"])),
            target_bin=runtime_bin,
            source_kind="operator_trusted_025292",
            materialize=write,
        )
        if not materialize["success"]:
            issues.append(str(materialize["blocker_id"]))
        else:
            source_package = build_source_package_summary(
                runtime_bin=runtime_bin,
                config_path=config_path,
                output_path=source_package_path,
                write=write,
                trusted_config_roots=roots,
            )
            if not source_package["success"]:
                issues.append(str(source_package["blocker_id"]))
            else:
                lineage = build_lineage_summary(
                    config_path=config_path,
                    source_package_path=source_package_path,
                    runtime_bin=runtime_bin,
                    trusted_config_roots=roots,
                )
                if not lineage["success"]:
                    issues.append(str(lineage["blocker_id"]))

    success = not issues and lineage is not None and lineage["success"]
    blocker_id = None if success else "ctp025292_runtime_lineage_recovery_unready"
    return {
        "baseline": BASELINE,
        "route_scenario": "ctp025292_marketdata_sandbox_paper_simulated_001",
        "runtime_pack_id": RUNTIME_PACK_ID,
        "market_source": "CTP 025292 official market data only",
        "market_data_account_id": "025292",
        "broker_order_submission": False,
        "trading_adapter": "disabled",
        "write_requested": write,
        "success": success,
        "status": "passed" if success else "blocked",
        "blocker_id": blocker_id,
        "issues": issues,
        "roots": [str(root) for root in roots],
        "runtime_bin": str(runtime_bin),
        "source_package_path": str(source_package_path),
        "config_path": str(config_path),
        "pipeline": {
            "discovery": _stage_status(
                bool(discovery["success"]),
                str(discovery.get("blocker_id") or "ctp025292_runtime_pack_source_unready"),
            ),
            "materialize": None
            if materialize is None
            else _stage_status(
                bool(materialize["success"]),
                str(materialize.get("blocker_id") or "ctp025292_runtime_pack_source_unready"),
            ),
            "source_package": None
            if source_package is None
            else _stage_status(
                bool(source_package["success"]),
                str(source_package.get("blocker_id") or "ctp025292_source_package_runtime_pack_unready"),
            ),
            "source_lineage_gate": None
            if lineage is None
            else _stage_status(
                bool(lineage["success"]),
                str(lineage.get("blocker_id") or "ctp025292_source_lineage_unready"),
            ),
        },
        "discovery_summary": {
            "candidate_count": discovery["candidate_count"],
            "trusted_candidate_count": discovery["trusted_candidate_count"],
            "candidate_classifications": {
                classification: sum(
                    1 for item in discovery["candidates"] if item.get("classification") == classification
                )
                for classification in sorted({str(item.get("classification")) for item in discovery["candidates"]})
            },
        },
        "trusted_candidates": trusted,
        "materialize_result": materialize,
        "source_package_result": source_package,
        "source_lineage_result": lineage,
        "negative_assertions": {
            "did_not_open_trading_channel": True,
            "did_not_submit_broker_order": True,
            "did_not_use_025292_as_trading_account": True,
            "did_not_generate_or_consume_paper_request": True,
            "did_not_claim_market_data_ready": True,
            "did_not_claim_paper_ready": True,
            "did_not_claim_live_ready": True,
        },
        "next_action": (
            "Run read-only 025292 MD smoke with the generated route-bound source package."
            if success
            else "Add exactly one operator_trusted_025292 marker for the correct 025292 DLL source directory, then rerun this pipeline with --write."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Recover Stage 2 CTP 025292 runtime lineage from marker discovery through source-lineage gate."
    )
    parser.add_argument("--root", type=Path, action="append", default=None)
    parser.add_argument("--runtime-bin", type=Path, default=DEFAULT_RUNTIME_BIN)
    parser.add_argument("--source-package", type=Path, default=DEFAULT_SOURCE_PACKAGE)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--output-json", type=Path, default=None)
    args = parser.parse_args()

    payload = recover_runtime_lineage(
        roots=args.root,
        runtime_bin=args.runtime_bin,
        source_package_path=args.source_package,
        config_path=args.config,
        write=args.write,
    )
    print(json.dumps(payload, ensure_ascii=False))

    if args.output_json is not None:
        args.output_json.parent.mkdir(parents=True, exist_ok=True)
        args.output_json.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    return 0 if payload["success"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
