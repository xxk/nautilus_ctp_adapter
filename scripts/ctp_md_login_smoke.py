from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from nautilus_ctp_adapter.adapters.ctp.config import (
    CtpAdapterConfig,
    CtpMdLoginCompatibility,
)
from nautilus_ctp_adapter.adapters.ctp.data_client import CtpDataClient
from nautilus_ctp_adapter.devtools.offhours_cli import (
    build_export_metadata,
    resolve_export_path,
    resolve_flow_mode,
    resolve_session_label,
    write_json_payload,
)
from nautilus_ctp_adapter.diagnostics.evidence_payloads import (
    MD_LOGIN_SMOKE_BASELINE,
    build_md_login_smoke_payload,
)


BASELINE = MD_LOGIN_SMOKE_BASELINE


def _field_shape(value: str) -> dict[str, object]:
    text = str(value or "")
    return {
        "present": bool(text),
        "length": len(text),
        "raw_value_recorded": False,
    }


def _front_shape(value: str) -> dict[str, object]:
    text = str(value or "")
    return {
        "present": bool(text),
        "length": len(text),
        "tcp_scheme": text.startswith("tcp://"),
        "raw_value_recorded": False,
    }


def _apply_md_login_overrides(config: CtpAdapterConfig, args: argparse.Namespace) -> dict[str, object]:
    user_product_info = args.md_user_product_info
    interface_product_info = args.md_interface_product_info
    protocol_info = args.md_protocol_info
    mac_address = args.md_mac_address
    client_ip_address = args.md_client_ip_address
    login_remark = args.md_login_remark

    if user_product_info is not None:
        config.product_info = user_product_info

    existing = config.md_login_compatibility
    config.md_login_compatibility = CtpMdLoginCompatibility(
        interface_product_info=(
            existing.interface_product_info
            if interface_product_info is None
            else interface_product_info
        ),
        protocol_info=existing.protocol_info if protocol_info is None else protocol_info,
        mac_address=existing.mac_address if mac_address is None else mac_address,
        client_ip_address=(
            existing.client_ip_address if client_ip_address is None else client_ip_address
        ),
        login_remark=existing.login_remark if login_remark is None else login_remark,
    )

    applied = {
        "md_user_product_info": user_product_info,
        "md_interface_product_info": interface_product_info,
        "md_protocol_info": protocol_info,
        "md_mac_address": mac_address,
        "md_client_ip_address": client_ip_address,
        "md_login_remark": login_remark,
    }
    applied_shapes = {
        key: _field_shape(value)
        for key, value in applied.items()
        if value is not None
    }
    return {
        "enabled": bool(applied_shapes),
        "fields": sorted(applied_shapes),
        "field_shapes": applied_shapes,
    }


def _emit_payload(payload: dict[str, object]) -> None:
    print(json.dumps(payload, ensure_ascii=False))


def _message_shape(value: object) -> dict[str, object]:
    text = str(value or "")
    return {
        "present": bool(text),
        "length": len(text),
        "sha256": hashlib.sha256(text.encode("utf-8")).hexdigest() if text else None,
        "raw_value_recorded": False,
    }


def _runtime_pack_override(runtime_pack_bin: Path | None) -> dict[str, object]:
    return {
        "enabled": runtime_pack_bin is not None,
        "path": None if runtime_pack_bin is None else str(runtime_pack_bin),
        "strict_runtime_pack": runtime_pack_bin is not None,
    }


def _exception_payload(
    *,
    stage: str,
    exc: Exception,
    runtime_pack_bin: Path | None,
    include_raw_message: bool,
) -> dict[str, object]:
    error_message = str(exc)
    return {
        "baseline": BASELINE,
        "success": False,
        "failure_reason": "exception",
        "runtime_pack_override": _runtime_pack_override(runtime_pack_bin),
        "error_stage": stage,
        "error_type": type(exc).__name__,
        "error_message": (
            error_message if include_raw_message else "<redacted; see error_message_shape>"
        ),
        "error_message_shape": _message_shape(error_message),
        "raw_secret_values_recorded": False,
        "raw_front_values_recorded": False,
    }


def _emit_exception(
    *,
    stage: str,
    exc: Exception,
    export_path: Path | None = None,
    runtime_pack_bin: Path | None = None,
) -> int:
    export_written = False
    if export_path is not None:
        artifact_payload = _exception_payload(
            stage=stage,
            exc=exc,
            runtime_pack_bin=runtime_pack_bin,
            include_raw_message=False,
        )
        artifact_payload["exception_export"] = {
            "attempted": True,
            "written": True,
            "path": str(export_path),
            "raw_error_message_recorded": False,
        }
        try:
            write_json_payload(path=export_path, payload=artifact_payload)
            export_written = True
        except Exception:
            export_written = False

    stdout_payload = _exception_payload(
        stage=stage,
        exc=exc,
        runtime_pack_bin=runtime_pack_bin,
        include_raw_message=export_path is None,
    )
    stdout_payload["exception_export"] = {
        "attempted": export_path is not None,
        "written": export_written,
        "path": None if export_path is None else str(export_path),
        "raw_error_message_recorded": False,
    }
    _emit_payload(stdout_payload)
    return 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the repository-owned Python MD login smoke.")
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--timeout-seconds", type=int, default=20)
    parser.add_argument("--flow-path", type=Path, default=None)
    parser.add_argument("--session-label")
    parser.add_argument(
        "--instrument",
        dest="instruments",
        action="append",
        default=None,
        help="Override config instruments for this read-only MD smoke; repeat for multiple symbols.",
    )
    parser.add_argument(
        "--md-front",
        help="Override MD front for this smoke only; raw value is not emitted.",
    )
    parser.add_argument("--evidence-root", type=Path)
    parser.add_argument("--output-json", type=Path)
    parser.add_argument(
        "--runtime-pack-bin",
        type=Path,
        help="Use this runtime pack bin for this MD smoke only; path is emitted, no config secrets are copied.",
    )
    parser.add_argument(
        "--md-user-product-info",
        help="Override MD UserProductInfo/ProductInfo for this smoke only; raw value is not emitted.",
    )
    parser.add_argument(
        "--md-interface-product-info",
        help="Override MD InterfaceProductInfo for this smoke only; raw value is not emitted.",
    )
    parser.add_argument(
        "--md-protocol-info",
        help="Override MD ProtocolInfo for this smoke only; raw value is not emitted.",
    )
    parser.add_argument(
        "--md-mac-address",
        help="Override MD MacAddress for this smoke only; raw value is not emitted.",
    )
    parser.add_argument(
        "--md-client-ip-address",
        help="Override MD ClientIPAddress for this smoke only; raw value is not emitted.",
    )
    parser.add_argument(
        "--md-login-remark",
        help="Override MD LoginRemark for this smoke only; raw value is not emitted.",
    )
    args = parser.parse_args()

    try:
        flow_mode = resolve_flow_mode(flow_path=args.flow_path)
        session_label = resolve_session_label(session_label=args.session_label, flow_path=args.flow_path)
        export_path = resolve_export_path(
            output_json=args.output_json,
            evidence_root=args.evidence_root,
            session_label=session_label,
            default_file_name="md_login_smoke.json",
        )
    except Exception as exc:
        return _emit_exception(stage="argument_validation", exc=exc)

    try:
        config = CtpAdapterConfig.from_json_file(args.config)
        if args.runtime_pack_bin is not None:
            config.native_pack_dir = str(args.runtime_pack_bin)
        if args.instruments:
            config.instruments = [str(item) for item in args.instruments]
        md_front_override = {
            "enabled": args.md_front is not None,
            "field_shape": _front_shape(args.md_front) if args.md_front is not None else None,
        }
        if args.md_front is not None:
            config.md_front = args.md_front
        md_login_override = _apply_md_login_overrides(config, args)
    except Exception as exc:
        return _emit_exception(
            stage="config_load",
            exc=exc,
            export_path=export_path,
            runtime_pack_bin=args.runtime_pack_bin,
        )

    try:
        client = CtpDataClient(config)
        result = client.run_live_md_smoke(timeout_seconds=args.timeout_seconds, flow_path=args.flow_path)
        events = client.runtime_bridge.drain_events()
    except Exception as exc:
        return _emit_exception(
            stage="run_smoke",
            exc=exc,
            export_path=export_path,
            runtime_pack_bin=args.runtime_pack_bin,
        )

    payload = build_md_login_smoke_payload(
        result,
        flow_path=None if args.flow_path is None else str(args.flow_path),
        flow_mode=flow_mode,
        session_label=session_label,
        instruments=getattr(config, "instruments", []),
        instrument_override=args.instruments is not None,
        md_front_override=md_front_override,
        md_login_override=md_login_override,
        runtime_pack_override=_runtime_pack_override(args.runtime_pack_bin),
        export=build_export_metadata(
            export_path=export_path,
            evidence_root=args.evidence_root,
            session_label=session_label,
            explicit_path=args.output_json is not None,
        ),
        bridge_events=events,
    )

    if export_path is not None:
        try:
            write_json_payload(path=export_path, payload=payload)
        except Exception as exc:
            return _emit_exception(
                stage="export_payload",
                exc=exc,
                export_path=export_path,
                runtime_pack_bin=args.runtime_pack_bin,
            )

    _emit_payload(payload)
    return 0 if payload["success"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
