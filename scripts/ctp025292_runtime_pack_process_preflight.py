from __future__ import annotations

import argparse
import ctypes
from datetime import datetime, timezone
import hashlib
import importlib
import json
import os
from pathlib import Path
import sys
from types import ModuleType
from typing import Callable

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from nautilus_ctp_adapter.native.loader import (
    CTP_RUNTIME_PACK_BIN_ENV,
    CTP_RUNTIME_PACK_STRICT_ENV,
    add_windows_dll_directories,
)
from nautilus_ctp_adapter.native.manifest import REQUIRED_NATIVE_DLLS


SCHEMA_VERSION = "ctp025292.runtime_pack_process_preflight.v1"
BLOCKER_ID = "ctp025292_runtime_pack_process_preflight_failed"
REQUIRED_PYO3_SYMBOLS = ("CtpMdLiveSession", "CtpTdLiveSession")


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def _file_sha256(path: Path) -> str | None:
    try:
        return _sha256_bytes(path.read_bytes())
    except OSError:
        return None


def _message_shape(exc: BaseException) -> dict[str, object]:
    message = str(exc)
    return {
        "present": bool(message),
        "length": len(message),
        "sha256": _sha256_bytes(message.encode("utf-8", errors="replace")),
        "raw_value_recorded": False,
    }


def _exception_summary(stage: str, exc: BaseException) -> dict[str, object]:
    return {
        "stage": stage,
        "error_type": type(exc).__name__,
        "error_message": "<redacted; see error_message_shape>",
        "error_message_shape": _message_shape(exc),
        "raw_error_message_recorded": False,
    }


def _dll_inventory(runtime_pack_bin: Path) -> list[dict[str, object]]:
    inventory: list[dict[str, object]] = []
    for name in REQUIRED_NATIVE_DLLS:
        path = runtime_pack_bin / name
        exists = path.exists()
        inventory.append(
            {
                "name": name,
                "path": str(path),
                "exists": exists,
                "size": path.stat().st_size if exists else None,
                "sha256": _file_sha256(path) if exists else None,
            }
        )
    return inventory


def _missing_required_dlls(inventory: list[dict[str, object]]) -> list[str]:
    return [str(item["name"]) for item in inventory if not item.get("exists")]


def build_preflight_payload(
    *,
    runtime_pack_bin: Path,
    smoke_result_json: Path | None = None,
    win_dll_loader: Callable[[str], object] | None = None,
    module_importer: Callable[[str], ModuleType] | None = None,
) -> dict[str, object]:
    runtime_pack_bin = runtime_pack_bin.resolve()
    loader = win_dll_loader or ctypes.WinDLL
    importer = module_importer or importlib.import_module
    inventory = _dll_inventory(runtime_pack_bin)
    missing = _missing_required_dlls(inventory)
    payload: dict[str, object] = {
        "schema_version": SCHEMA_VERSION,
        "created_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "route_scenario": "ctp025292_marketdata_sandbox_paper_simulated_001",
        "runtime_pack_bin": str(runtime_pack_bin),
        "source_smoke_result_json": None if smoke_result_json is None else str(smoke_result_json),
        "dll_inventory": inventory,
        "preload": {
            "attempted": False,
            "loaded": [],
        },
        "pyo3_import": {
            "attempted": False,
            "module": "ctp_runtime._ctp_runtime",
            "required_symbols": list(REQUIRED_PYO3_SYMBOLS),
            "symbols_present": {},
        },
        "negative_assertions": {
            "does_not_connect_md_front": True,
            "does_not_submit_broker_order": True,
            "does_not_generate_or_consume_paper_request": True,
            "does_not_claim_readiness_or_can_trade": True,
            "raw_secret_values_recorded": False,
            "raw_front_values_recorded": False,
            "raw_error_message_recorded": False,
        },
    }
    if missing:
        payload.update(
            {
                "success": False,
                "result_status": "stage2_tool_or_runtime_blocker",
                "blocker_id": BLOCKER_ID,
                "failure_stage": "runtime_pack_inventory",
                "issues": [f"required_dll_missing:{name}" for name in missing],
                "ready_for_md_smoke": False,
                "is_s2_g2_market_data_pass": False,
            }
        )
        return payload

    try:
        registered = add_windows_dll_directories(runtime_pack_bin)
        os.environ[CTP_RUNTIME_PACK_BIN_ENV] = str(runtime_pack_bin)
        os.environ[CTP_RUNTIME_PACK_STRICT_ENV] = "1"
        payload["dll_directory_registration"] = {
            "attempted": True,
            "registered": [str(path) for path in registered],
        }
        payload["runtime_pack_environment"] = {
            "bound": True,
            "runtime_pack_bin_env": CTP_RUNTIME_PACK_BIN_ENV,
            "runtime_pack_strict_env": CTP_RUNTIME_PACK_STRICT_ENV,
            "runtime_pack_bin": str(runtime_pack_bin),
            "strict": True,
        }
        loaded: list[str] = []
        payload["preload"]["attempted"] = True  # type: ignore[index]
        for name in REQUIRED_NATIVE_DLLS:
            if name == "ctp_native.dll":
                continue
            dll_path = runtime_pack_bin / name
            loader(str(dll_path))
            loaded.append(str(dll_path))
        payload["preload"]["loaded"] = loaded  # type: ignore[index]
    except OSError as exc:
        payload.update(
            {
                "success": False,
                "result_status": "stage2_tool_or_runtime_blocker",
                "blocker_id": BLOCKER_ID,
                "failure_stage": "runtime_pack_preload",
                "exception": _exception_summary("runtime_pack_preload", exc),
                "issues": ["runtime_pack_preload_os_error"],
                "ready_for_md_smoke": False,
                "is_s2_g2_market_data_pass": False,
            }
        )
        return payload

    try:
        payload["pyo3_import"]["attempted"] = True  # type: ignore[index]
        module = importer("ctp_runtime._ctp_runtime")
        symbols_present = {
            symbol: hasattr(module, symbol)
            for symbol in REQUIRED_PYO3_SYMBOLS
        }
        payload["pyo3_import"]["symbols_present"] = symbols_present  # type: ignore[index]
    except (ImportError, OSError, RuntimeError) as exc:
        payload.update(
            {
                "success": False,
                "result_status": "stage2_tool_or_runtime_blocker",
                "blocker_id": BLOCKER_ID,
                "failure_stage": "pyo3_import",
                "exception": _exception_summary("pyo3_import", exc),
                "issues": ["pyo3_import_failed"],
                "ready_for_md_smoke": False,
                "is_s2_g2_market_data_pass": False,
            }
        )
        return payload

    missing_symbols = [
        symbol
        for symbol, present in payload["pyo3_import"]["symbols_present"].items()  # type: ignore[index, union-attr]
        if not present
    ]
    if missing_symbols:
        payload.update(
            {
                "success": False,
                "result_status": "stage2_tool_or_runtime_blocker",
                "blocker_id": BLOCKER_ID,
                "failure_stage": "pyo3_symbol_contract",
                "issues": [f"pyo3_symbol_missing:{symbol}" for symbol in missing_symbols],
                "ready_for_md_smoke": False,
                "is_s2_g2_market_data_pass": False,
            }
        )
        return payload

    payload.update(
        {
            "success": True,
            "result_status": "runtime_process_preflight_passed",
            "blocker_id": None,
            "failure_stage": None,
            "issues": [],
            "ready_for_md_smoke": True,
            "is_s2_g2_market_data_pass": False,
        }
    )
    return payload


def write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="ctp025292_runtime_pack_process_preflight",
        description="Run a non-connecting process-level preflight for the route-bound CTP 025292 runtime pack.",
    )
    parser.add_argument("--runtime-pack-bin", type=Path, required=True)
    parser.add_argument("--smoke-result-json", type=Path)
    parser.add_argument("--output-json", type=Path, required=True)
    args = parser.parse_args()

    payload = build_preflight_payload(
        runtime_pack_bin=args.runtime_pack_bin,
        smoke_result_json=args.smoke_result_json,
    )
    write_json(args.output_json, payload)
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if payload["success"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
