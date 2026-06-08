from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from nautilus_ctp_adapter.adapters.ctp.config import CtpAdapterConfig
from nautilus_ctp_adapter.adapters.ctp.factory import build_ctp_stack


BASELINE = "ctp-paper-session-preflight-v1"
DEFAULT_CONFIG = REPO_ROOT / "cfgs" / "local" / "ctp.openctp.tts.7x24.local.json"
OPENCTP_TTS_7X24_PROFILE = "openctp-tts-7x24-simulation"
OPENCTP_TTS_7X24_PROFILE_ALIASES = {OPENCTP_TTS_7X24_PROFILE, "openctp-paper"}


def _stable_fingerprint(value: str) -> str:
    text = str(value or "").strip()
    if not text:
        return ""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]


def _repo_relative(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def _front_is_openctp(front: str) -> bool:
    return "openctp.cn" in str(front or "").lower()


def paper_config_issues(
    config: CtpAdapterConfig,
    *,
    allow_live_order_smoke: bool = False,
) -> list[str]:
    issues = list(config.validate())
    if config.broker_id != "9999":
        issues.append("paper_profile.broker_id")
    if not _front_is_openctp(config.md_front):
        issues.append("paper_profile.md_front")
    if not _front_is_openctp(config.td_front):
        issues.append("paper_profile.td_front")
    if config.execution_guardrails.allow_live_order_smoke and not allow_live_order_smoke:
        issues.append("execution_guardrails.allow_live_order_smoke_must_be_false")
    return issues


def redacted_config_summary(config: CtpAdapterConfig) -> dict[str, Any]:
    return {
        "broker_id": config.broker_id,
        "user_id_present": bool(config.user_id),
        "user_id_fingerprint": _stable_fingerprint(config.user_id),
        "password_present": bool(config.password),
        "auth_code_present": bool(config.auth_code),
        "app_id_present": bool(config.app_id),
        "md_front_is_openctp": _front_is_openctp(config.md_front),
        "td_front_is_openctp": _front_is_openctp(config.td_front),
        "instruments": list(config.instruments),
        "guardrails": {
            "enabled": config.execution_guardrails.enabled,
            "allowed_instruments": list(config.execution_guardrails.allowed_instruments),
            "max_order_qty": config.execution_guardrails.max_order_qty,
            "max_net_position": config.execution_guardrails.max_net_position,
            "max_submit_per_minute": config.execution_guardrails.max_submit_per_minute,
            "price_mode": config.execution_guardrails.price_mode,
            "allow_live_order_smoke": config.execution_guardrails.allow_live_order_smoke,
        },
    }


def build_preflight_summary(config_path: Path, *, connect_paper: bool = False) -> dict[str, Any]:
    resolved = config_path if config_path.is_absolute() else REPO_ROOT / config_path
    payload: dict[str, Any] = {
        "baseline": BASELINE,
        "account_profile": OPENCTP_TTS_7X24_PROFILE,
        "evidence_class": "openctp-tts-7x24-simulation",
        "action_mode": "paper_connect" if connect_paper else "request_only",
        "connect_requested": connect_paper,
        "config_path": _repo_relative(resolved),
        "success": False,
        "status": "blocked",
        "failure_reason": None,
        "blocker_type": None,
        "issues": [],
        "config": None,
        "paper_session": None,
    }

    if not resolved.exists():
        payload["failure_reason"] = "missing_config"
        payload["blocker_type"] = "paper-resource"
        payload["issues"] = ["config_path_missing"]
        return payload

    try:
        config = CtpAdapterConfig.from_json_file(resolved)
    except Exception as exc:
        payload["failure_reason"] = "config_load_failed"
        payload["blocker_type"] = "paper-resource"
        payload["issues"] = [type(exc).__name__]
        return payload

    issues = paper_config_issues(config)
    payload["config"] = redacted_config_summary(config)
    payload["issues"] = issues
    if issues:
        payload["failure_reason"] = "config_validation_failed"
        payload["blocker_type"] = "paper-resource"
        return payload

    if not connect_paper:
        payload["success"] = True
        payload["status"] = "passed"
        return payload

    try:
        stack = build_ctp_stack(config)
        data_client = stack["data_client"]
        execution_client = stack["execution_client"]
        runtime_bridge = stack["runtime_bridge"]

        bootstrap = data_client.bootstrap_market_data_mainline()
        md_result = data_client.run_live_md_smoke(timeout_seconds=30)
        td_result = execution_client.run_live_td_readiness_smoke(timeout_seconds=30)
        events = runtime_bridge.drain_events()
    except Exception as exc:
        payload["failure_reason"] = "paper_connect_exception"
        payload["blocker_type"] = "paper-resource"
        payload["issues"] = [type(exc).__name__]
        payload["paper_session"] = {"error_type": type(exc).__name__, "error_message": str(exc)}
        return payload

    paper_session = {
        "bootstrap_started": bootstrap.started,
        "md_login_success": md_result.login_success,
        "md_login_error_id": md_result.login_error_id,
        "md_first_tick_seen": bool(md_result.first_tick_symbol),
        "md_first_tick_symbol": md_result.first_tick_symbol,
        "td_login_success": td_result.login_success,
        "td_login_error_id": td_result.login_error_id,
        "td_settlement_code": td_result.settlement_code,
        "td_front_id_present": td_result.front_id is not None,
        "td_session_id_present": td_result.session_id is not None,
        "td_max_order_ref_present": bool(td_result.max_order_ref),
        "td_disconnects": td_result.disconnects,
        "bridge_event_kinds": [event.kind.value for event in events],
    }
    payload["paper_session"] = paper_session

    connect_issues: list[str] = []
    if not bootstrap.started:
        connect_issues.append("md_bootstrap_not_started")
    if md_result.login_success is not True:
        connect_issues.append("md_login_failed")
    if td_result.login_success is not True:
        connect_issues.append("td_login_failed")
    if td_result.settlement_code != 0:
        connect_issues.append("td_settlement_not_confirmed")

    payload["issues"] = connect_issues
    if connect_issues:
        payload["failure_reason"] = "paper_session_not_ready"
        payload["blocker_type"] = "paper-resource"
        return payload

    payload["success"] = True
    payload["status"] = "passed"
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Preflight OpenCTP paper account config and optionally connect to paper fronts."
    )
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--connect-paper", action="store_true")
    parser.add_argument("--output-json", type=Path, default=None)
    args = parser.parse_args()

    payload = build_preflight_summary(args.config, connect_paper=args.connect_paper)
    text = json.dumps(payload, ensure_ascii=False)
    print(text)

    if args.output_json is not None:
        output_path = args.output_json if args.output_json.is_absolute() else REPO_ROOT / args.output_json
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    return 0 if payload["success"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
