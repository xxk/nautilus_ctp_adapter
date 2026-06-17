from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any


BASELINE = "ctp025292-md-lifecycle-trace-summary-v1"


def _load_events(path: Path) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        payload = json.loads(line)
        if not isinstance(payload, dict):
            raise ValueError(f"trace row must be an object: {path}")
        events.append(payload)
    return events


def _duration_ms(events: list[dict[str, Any]]) -> float | None:
    timestamps = [int(event["ts_epoch_us"]) for event in events if "ts_epoch_us" in event]
    if not timestamps:
        return None
    return round((max(timestamps) - min(timestamps)) / 1000.0, 3)


def _dispatch_to_disconnect_ms(events: list[dict[str, Any]]) -> dict[str, float | int | None]:
    latencies: list[float] = []
    pending_dispatch_ts: int | None = None
    for event in events:
        event_name = str(event.get("event", ""))
        if event_name == "md_login_dispatch_return":
            pending_dispatch_ts = int(event["ts_epoch_us"])
            continue
        if event_name == "front_disconnected" and pending_dispatch_ts is not None:
            latencies.append((int(event["ts_epoch_us"]) - pending_dispatch_ts) / 1000.0)
            pending_dispatch_ts = None
    if not latencies:
        return {"count": 0, "min_ms": None, "max_ms": None, "avg_ms": None}
    return {
        "count": len(latencies),
        "min_ms": round(min(latencies), 3),
        "max_ms": round(max(latencies), 3),
        "avg_ms": round(sum(latencies) / len(latencies), 3),
    }


def _numeric_field_stats(events: list[dict[str, Any]], event_name: str, field_name: str) -> dict[str, float | int | None]:
    values: list[float] = []
    for event in events:
        if str(event.get("event", "")) != event_name or field_name not in event:
            continue
        value = event[field_name]
        if value is None:
            continue
        values.append(float(value))
    if not values:
        return {"count": 0, "min": None, "max": None, "avg": None}
    return {
        "count": len(values),
        "min": round(min(values), 3),
        "max": round(max(values), 3),
        "avg": round(sum(values) / len(values), 3),
    }


def _bool_field_counts(events: list[dict[str, Any]], event_name: str, field_name: str) -> dict[str, int]:
    counts = {"true": 0, "false": 0, "missing": 0}
    for event in events:
        if str(event.get("event", "")) != event_name:
            continue
        if field_name not in event:
            counts["missing"] += 1
        elif bool(event[field_name]):
            counts["true"] += 1
        else:
            counts["false"] += 1
    return counts


def _payload_shape_summary(events: list[dict[str, Any]]) -> dict[str, Any]:
    payload_events = [
        event for event in events if str(event.get("event", "")) == "md_login_payload_shape"
    ]
    field_names = (
        "broker_id",
        "user_id",
        "password",
        "user_product_info",
        "interface_product_info",
        "protocol_info",
        "mac_address",
        "client_ip_address",
        "login_remark",
    )
    fields: dict[str, Any] = {}
    for field_name in field_names:
        present_key = f"{field_name}_present"
        len_key = f"{field_name}_len"
        lengths = sorted(
            {
                int(event[len_key])
                for event in payload_events
                if len_key in event and event.get(present_key) is not None
            }
        )
        fields[field_name] = {
            "present_counts": _bool_field_counts(payload_events, "md_login_payload_shape", present_key),
            "lengths": lengths,
            "raw_values_recorded": False,
        }
    return {
        "event_count": len(payload_events),
        "request_ids": sorted(
            {
                int(event["request_id"])
                for event in payload_events
                if "request_id" in event
            }
        ),
        "fields": fields,
        "raw_values_recorded": False,
    }


def _front_shape_summary(events: list[dict[str, Any]]) -> dict[str, Any]:
    front_events = [
        event for event in events if str(event.get("event", "")) == "md_register_front"
    ]
    lengths = sorted(
        {
            int(event["front_len"])
            for event in front_events
            if "front_len" in event
        }
    )
    return {
        "event_count": len(front_events),
        "present_counts": _bool_field_counts(front_events, "md_register_front", "front_present"),
        "tcp_scheme_counts": _bool_field_counts(front_events, "md_register_front", "front_tcp_scheme"),
        "lengths": lengths,
        "raw_values_recorded": False,
    }


def _rsp_error_summary(events: list[dict[str, Any]]) -> dict[str, Any]:
    rsp_error_events = [
        event for event in events if str(event.get("event", "")) == "md_rsp_error"
    ]
    error_ids = sorted(
        {
            int(event["error_id"])
            for event in rsp_error_events
            if "error_id" in event
        }
    )
    return {
        "event_count": len(rsp_error_events),
        "error_ids": error_ids,
        "message_present_counts": _bool_field_counts(rsp_error_events, "md_rsp_error", "error_message_present"),
        "message_lengths": sorted(
            {
                int(event["error_message_len"])
                for event in rsp_error_events
                if "error_message_len" in event
            }
        ),
        "raw_values_recorded": False,
    }


def build_summary(trace_path: Path, *, output_path: Path | None = None) -> dict[str, Any]:
    events = _load_events(trace_path)
    event_counts = Counter(str(event.get("event", "")) for event in events)
    request_ids = [
        int(event["request_id"])
        for event in events
        if str(event.get("event")) == "md_login_dispatch_return" and "request_id" in event
    ]
    return_codes = sorted(
        {
            int(event["return_code"])
            for event in events
            if str(event.get("event")) == "md_login_dispatch_return" and "return_code" in event
        }
    )
    disconnect_reasons = sorted(
        {
            int(event["reason"])
            for event in events
            if str(event.get("event")) == "front_disconnected" and "reason" in event
        }
    )
    login_response_count = int(event_counts.get("md_login_response", 0))
    tick_count = int(event_counts.get("md_tick", 0) + event_counts.get("tick", 0))
    payload_shape_count = int(event_counts.get("md_login_payload_shape", 0))
    register_front_count = int(event_counts.get("md_register_front", 0))
    init_call_count = int(event_counts.get("md_init_call", 0))
    init_return_count = int(event_counts.get("md_init_return", 0))
    rsp_error_count = int(event_counts.get("md_rsp_error", 0))
    heartbeat_warning_count = int(event_counts.get("md_heartbeat_warning", 0))
    dispatch_count = int(event_counts.get("md_login_dispatch_return", 0))
    disconnect_count = int(event_counts.get("front_disconnected", 0))
    connected_count = int(event_counts.get("front_connected", 0))
    response_missing_after_dispatch = dispatch_count > 0 and login_response_count == 0
    all_dispatch_returns_ok = bool(return_codes) and return_codes == [0]
    all_disconnect_reasons_zero = disconnect_reasons == [0]

    payload: dict[str, Any] = {
        "baseline": BASELINE,
        "route_scenario": "ctp025292_marketdata_sandbox_paper_simulated_001",
        "market_source": "CTP 025292 official market data only",
        "market_data_account_id": "025292",
        "broker_order_submission": False,
        "trading_adapter": "disabled",
        "trace_path": str(trace_path),
        "success": False,
        "status": "blocked",
        "blocker_id": "ctp025292_marketdata_login_response_missing_after_runtime_lineage",
        "event_count": len(events),
        "event_counts": dict(sorted(event_counts.items())),
        "duration_ms": _duration_ms(events),
        "connected_count": connected_count,
        "dispatch_count": dispatch_count,
        "payload_shape_count": payload_shape_count,
        "register_front_count": register_front_count,
        "init_call_count": init_call_count,
        "init_return_count": init_return_count,
        "rsp_error_count": rsp_error_count,
        "heartbeat_warning_count": heartbeat_warning_count,
        "disconnect_count": disconnect_count,
        "login_response_count": login_response_count,
        "tick_count": tick_count,
        "request_id_min": min(request_ids) if request_ids else None,
        "request_id_max": max(request_ids) if request_ids else None,
        "request_id_count": len(request_ids),
        "return_codes": return_codes,
        "disconnect_reasons": disconnect_reasons,
        "dispatch_to_disconnect_latency": _dispatch_to_disconnect_ms(events),
        "native_close_detail": {
            "front_shape_summary": _front_shape_summary(events),
            "rsp_error_summary": _rsp_error_summary(events),
            "heartbeat_warning_time_lapse": _numeric_field_stats(events, "md_heartbeat_warning", "time_lapse"),
            "dispatch_to_disconnect_us": _numeric_field_stats(events, "front_disconnected", "dispatch_to_disconnect_us"),
            "connected_to_disconnect_us": _numeric_field_stats(events, "front_disconnected", "connected_to_disconnect_us"),
            "last_login_return_codes": sorted(
                {
                    int(event["last_login_return_code"])
                    for event in events
                    if str(event.get("event")) == "front_disconnected" and "last_login_return_code" in event
                }
            ),
        },
        "payload_shape_summary": _payload_shape_summary(events),
        "disconnect_state_summary": {
            "login_requested": _bool_field_counts(events, "front_disconnected", "login_requested"),
            "login_dispatched_before_disconnect": _bool_field_counts(
                events,
                "front_disconnected",
                "login_dispatched_before_disconnect",
            ),
            "connected_before_disconnect": _bool_field_counts(
                events,
                "front_disconnected",
                "connected_before_disconnect",
            ),
            "pending_login_request_ids": sorted(
                {
                    int(event["pending_login_request_id"])
                    for event in events
                    if str(event.get("event")) == "front_disconnected"
                    and "pending_login_request_id" in event
                    and int(event["pending_login_request_id"]) >= 0
                }
            ),
        },
        "diagnosis": {
            "response_missing_after_dispatch": response_missing_after_dispatch,
            "all_dispatch_returns_ok": all_dispatch_returns_ok,
            "all_disconnect_reasons_zero": all_disconnect_reasons_zero,
            "payload_shape_trace_available": payload_shape_count > 0,
            "front_registration_trace_available": register_front_count > 0,
            "init_trace_available": init_call_count > 0 and init_return_count > 0,
            "rsp_error_trace_available": rsp_error_count > 0,
            "heartbeat_warning_trace_available": heartbeat_warning_count > 0,
            "disconnect_latency_trace_available": any(
                str(event.get("event")) == "front_disconnected"
                and "dispatch_to_disconnect_us" in event
                for event in events
            ),
            "disconnect_pending_login_trace_available": any(
                str(event.get("event")) == "front_disconnected"
                and "login_dispatched_before_disconnect" in event
                for event in events
            ),
            "signature": "front_connected -> md_login_dispatch_return(return_code=0) -> front_disconnected(reason=0), without md_login_response",
        },
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
            "Compare current 025292 MD login payload against known-success payload/config lineage and "
            "capture any broker-side login rejection or network close reason without opening TD/order channels."
        ),
    }
    if output_path is not None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description="Summarize CTP 025292 MD native lifecycle trace.")
    parser.add_argument("--trace", type=Path, required=True)
    parser.add_argument("--output-json", type=Path, default=None)
    args = parser.parse_args()

    payload = build_summary(args.trace, output_path=args.output_json)
    print(json.dumps(payload, ensure_ascii=False))
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
