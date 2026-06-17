from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from nautilus_ctp_adapter.adapters.ctp.config import CtpAdapterConfig


BASELINE = "ctp025292-md-vendor-console-capture-v1"


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest().upper()


def _field_shape(value: str) -> dict[str, object]:
    text = str(value or "")
    return {"present": bool(text), "length": len(text), "raw_value_recorded": False}


def _front_shape(value: str) -> dict[str, object]:
    text = str(value or "")
    return {
        "present": bool(text),
        "length": len(text),
        "tcp_scheme": text.startswith("tcp://"),
        "raw_value_recorded": False,
    }


def _redaction_pairs(config: CtpAdapterConfig, *, cli_values: list[tuple[str, str]]) -> list[tuple[str, str]]:
    pairs: list[tuple[str, str]] = []

    def add(label: str, value: str, *, front: bool = False) -> None:
        text = str(value or "")
        if len(text) < 3:
            return
        shape = "tcp_len" if front and text.startswith("tcp://") else "len"
        pairs.append((text, f"<redacted:{label}:{shape}={len(text)}>"))

    add("broker_id", config.broker_id)
    add("user_id", config.user_id)
    add("password", config.password)
    add("auth_code", config.auth_code)
    add("app_id", config.app_id)
    add("product_info", config.product_info)
    add("md_front", config.md_front, front=True)
    add("td_front", config.td_front, front=True)
    add("md_interface_product_info", config.md_login_compatibility.interface_product_info)
    add("md_protocol_info", config.md_login_compatibility.protocol_info)
    add("md_mac_address", config.md_login_compatibility.mac_address)
    add("md_client_ip_address", config.md_login_compatibility.client_ip_address)
    add("md_login_remark", config.md_login_compatibility.login_remark)
    for label, value in cli_values:
        add(label, value, front=label == "md_front")

    # Longest first avoids partial redaction when values overlap.
    deduped = dict(sorted(pairs, key=lambda item: len(item[0]), reverse=True))
    return list(deduped.items())


def redact_text(value: str, pairs: list[tuple[str, str]]) -> str:
    redacted = value
    for raw, replacement in pairs:
        redacted = redacted.replace(raw, replacement)
    return redacted


def _line_is_json_object(line: str) -> bool:
    text = line.strip()
    if not text.startswith("{") or not text.endswith("}"):
        return False
    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        return False
    return isinstance(payload, dict)


def classify_console_lines(stdout: str, stderr: str) -> dict[str, object]:
    lines = [line for line in (stdout + "\n" + stderr).splitlines() if line.strip()]
    non_json_lines = [line for line in lines if not _line_is_json_object(line)]
    patterns = {
        "native_session_disconnect": re.compile(r"CThostFtdcUserApiImplBase::OnSessionDisconnected", re.I),
        "front_disconnect": re.compile(r"OnFrontDisconnected|Front Disconnected|disconnected", re.I),
        "login_response": re.compile(r"OnRspUserLogin|MD Login Success|MD login callback|登录行情成功", re.I),
        "rsp_error": re.compile(r"OnRspError|On Rsp Error|ErrorID|ErrorMsg|Authenticate Failed|Login Failed|登录失败|失败", re.I),
        "tick": re.compile(r"\bTICK\b|first matching tick|first_tick", re.I),
    }
    matches: dict[str, list[str]] = {}
    for name, pattern in patterns.items():
        matches[name] = [line for line in non_json_lines if pattern.search(line)]
    return {
        "stdout_line_count": len(stdout.splitlines()),
        "stderr_line_count": len(stderr.splitlines()),
        "json_stdout_line_count": sum(1 for line in stdout.splitlines() if _line_is_json_object(line)),
        "non_json_console_line_count": len(non_json_lines),
        "matched_line_counts": {name: len(value) for name, value in matches.items()},
        "matched_lines": matches,
    }


def _build_smoke_command(args: argparse.Namespace, smoke_output: Path) -> list[str]:
    script = REPO_ROOT / "scripts" / "ctp_md_login_smoke.py"
    command = [
        str(Path(args.python_exe)),
        str(script),
        "--config",
        str(args.config),
        "--timeout-seconds",
        str(args.timeout_seconds),
        "--flow-path",
        str(args.flow_path),
        "--output-json",
        str(smoke_output),
    ]
    for symbol in args.instrument or []:
        command.extend(["--instrument", symbol])
    optional_args = [
        ("--md-front", args.md_front),
        ("--md-user-product-info", args.md_user_product_info),
        ("--md-interface-product-info", args.md_interface_product_info),
        ("--md-protocol-info", args.md_protocol_info),
        ("--md-mac-address", args.md_mac_address),
        ("--md-client-ip-address", args.md_client_ip_address),
        ("--md-login-remark", args.md_login_remark),
    ]
    for flag, value in optional_args:
        if value is not None:
            command.extend([flag, value])
    if args.runtime_pack_bin is not None:
        command.extend(["--runtime-pack-bin", str(args.runtime_pack_bin)])
    return command


def _config_shape(config: CtpAdapterConfig, *, md_front_override: str | None) -> dict[str, object]:
    return {
        "broker_id": _field_shape(config.broker_id),
        "user_id": _field_shape(config.user_id),
        "password": _field_shape(config.password),
        "auth_code": _field_shape(config.auth_code),
        "app_id": _field_shape(config.app_id),
        "product_info": _field_shape(config.product_info),
        "md_front": _front_shape(md_front_override if md_front_override is not None else config.md_front),
        "td_front": _front_shape(config.td_front),
        "native_pack_dir_present": bool(config.native_pack_dir),
        "md_login_compatibility": {
            "interface_product_info": _field_shape(config.md_login_compatibility.interface_product_info),
            "protocol_info": _field_shape(config.md_login_compatibility.protocol_info),
            "mac_address": _field_shape(config.md_login_compatibility.mac_address),
            "client_ip_address": _field_shape(config.md_login_compatibility.client_ip_address),
            "login_remark": _field_shape(config.md_login_compatibility.login_remark),
        },
    }


def build_capture(args: argparse.Namespace) -> dict[str, object]:
    config = CtpAdapterConfig.from_json_file(args.config)
    args.flow_path.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    smoke_output = args.smoke_output_json or args.output_json.with_name(
        args.output_json.stem + "_smoke.json"
    )
    smoke_output.parent.mkdir(parents=True, exist_ok=True)
    if args.runtime_pack_bin is not None:
        config.native_pack_dir = str(args.runtime_pack_bin)

    cli_values = [
        ("md_front", args.md_front or ""),
        ("md_user_product_info", args.md_user_product_info or ""),
        ("md_interface_product_info", args.md_interface_product_info or ""),
        ("md_protocol_info", args.md_protocol_info or ""),
        ("md_mac_address", args.md_mac_address or ""),
        ("md_client_ip_address", args.md_client_ip_address or ""),
        ("md_login_remark", args.md_login_remark or ""),
    ]
    redactions = _redaction_pairs(config, cli_values=cli_values)
    command = _build_smoke_command(args, smoke_output)
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    env.setdefault("PYTHONUTF8", "1")
    if args.runtime_pack_bin is not None:
        env["NAUTILUS_CTP_RUNTIME_PACK_BIN"] = str(args.runtime_pack_bin)
        env["NAUTILUS_CTP_RUNTIME_PACK_STRICT"] = "1"

    completed = subprocess.run(
        command,
        cwd=str(REPO_ROOT),
        env=env,
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=max(5, int(args.timeout_seconds) + int(args.extra_timeout_seconds)),
        check=False,
    )

    redacted_stdout = redact_text(completed.stdout, redactions)
    redacted_stderr = redact_text(completed.stderr, redactions)
    console_summary = classify_console_lines(redacted_stdout, redacted_stderr)
    smoke_payload: dict[str, Any] | None = None
    if smoke_output.exists():
        try:
            smoke_payload = json.loads(smoke_output.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            smoke_payload = None

    payload: dict[str, object] = {
        "baseline": BASELINE,
        "route_scenario": "ctp025292_marketdata_sandbox_paper_simulated_001",
        "market_source": "CTP 025292 official market data only",
        "market_data_account_id": "025292",
        "broker_order_submission": False,
        "trading_adapter": "disabled",
        "success": bool(smoke_payload and smoke_payload.get("success") is True),
        "status": "pass" if smoke_payload and smoke_payload.get("success") is True else "blocked",
        "blocker_id": None
        if smoke_payload and smoke_payload.get("success") is True
        else "ctp025292_md_vendor_console_no_login_response",
        "command": {
            "argv_redacted": [redact_text(item, redactions) for item in command],
            "cwd": str(REPO_ROOT),
            "returncode": completed.returncode,
            "pythonioencoding": "utf-8",
            "runtime_pack_strict": args.runtime_pack_bin is not None,
        },
        "redacted_config_shape": _config_shape(config, md_front_override=args.md_front),
        "smoke_result": smoke_payload,
        "console_capture": {
            "stdout_redacted": redacted_stdout,
            "stderr_redacted": redacted_stderr,
            "summary": console_summary,
            "raw_secret_values_recorded": False,
            "raw_front_values_recorded": False,
        },
        "artifacts": {
            "smoke_output_json": {
                "path": str(smoke_output),
                "sha256": _sha256(smoke_output) if smoke_output.exists() else None,
            },
            "flow_path": str(args.flow_path),
            "repo_md_lifecycle_trace_jsonl": str(args.flow_path / "repo_md_lifecycle_trace.jsonl"),
        },
        "interpretation": {
            "vendor_console_capture_present": True,
            "non_json_vendor_prompt_lines_present": bool(
                console_summary["non_json_console_line_count"]
            ),
            "spi_login_response_prompt_present": bool(
                console_summary["matched_line_counts"]["login_response"]
            ),
            "spi_error_prompt_present": bool(console_summary["matched_line_counts"]["rsp_error"]),
            "native_session_disconnect_prompt_present": bool(
                console_summary["matched_line_counts"]["native_session_disconnect"]
            ),
            "summary": (
                "Captured stdout/stderr around the read-only MD smoke. If login_response/rsp_error "
                "matched counts remain zero while lifecycle trace shows front disconnects, the missing "
                "broker prompt is below or before the SPI response layer."
            ),
        },
        "negative_assertions": {
            "did_not_run_td_script": True,
            "did_not_run_order_script": True,
            "did_not_open_trading_channel": True,
            "did_not_submit_broker_order": True,
            "did_not_use_025292_as_trading_account": True,
            "did_not_generate_or_consume_paper_request": True,
            "did_not_claim_market_data_ready": True,
            "did_not_claim_paper_ready": True,
            "did_not_claim_live_ready": True,
            "secret_values_recorded": False,
            "front_values_recorded": False,
        },
        "next_action": (
            "If no vendor console login/error prompt is captured, isolate the old successful DLL family "
            "or broker/front login policy rather than repeating front reachability probes."
        ),
    }
    args.output_json.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run CTP 025292 MD-only smoke and capture redacted vendor console prompts."
    )
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--timeout-seconds", type=int, default=20)
    parser.add_argument("--extra-timeout-seconds", type=int, default=15)
    parser.add_argument("--flow-path", type=Path, required=True)
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--smoke-output-json", type=Path, default=None)
    parser.add_argument("--instrument", action="append", default=None)
    parser.add_argument("--md-front")
    parser.add_argument("--md-user-product-info")
    parser.add_argument("--md-interface-product-info")
    parser.add_argument("--md-protocol-info")
    parser.add_argument("--md-mac-address")
    parser.add_argument("--md-client-ip-address")
    parser.add_argument("--md-login-remark")
    parser.add_argument("--runtime-pack-bin", type=Path, default=None)
    parser.add_argument("--python-exe", default=sys.executable)
    args = parser.parse_args()

    payload = build_capture(args)
    print(json.dumps(payload, ensure_ascii=False))
    return 0 if payload["success"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
