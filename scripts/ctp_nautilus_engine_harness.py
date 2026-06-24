from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from nautilus_trader.core.uuid import UUID4
from nautilus_trader.execution.messages import (
    GenerateFillReports,
    GenerateOrderStatusReports,
    GeneratePositionStatusReports,
)
from nautilus_trader.model.identifiers import InstrumentId

from nautilus_ctp_adapter.adapters.ctp.nautilus_execution import (
    CtpLiveExecutionClient,
    ctp_account_record_to_account_state,
    ctp_position_record_to_status_report,
)
from nautilus_ctp_adapter.adapters.ctp.nautilus_provider import CtpNautilusInstrumentProvider
from nautilus_ctp_adapter.adapters.ctp.normalization import CtpProductKind, NormalizedCtpInstrument
from nautilus_ctp_adapter.adapters.ctp.execution_client import CtpTdExecEventPayload
from nautilus_ctp_adapter.devtools.offhours_cli import write_json_payload
from nautilus_ctp_adapter.diagnostics.evidence_payloads import (
    NAUTILUS_ENGINE_HARNESS_ACCOUNT_PROFILE,
    NAUTILUS_ENGINE_HARNESS_BASELINE,
    NAUTILUS_ENGINE_HARNESS_EVIDENCE_CLASS,
    build_nautilus_engine_harness_payload,
)
from nautilus_ctp_adapter.runtime.query import CtpAccountRecord, CtpPositionRecord


BASELINE = NAUTILUS_ENGINE_HARNESS_BASELINE
ACCOUNT_PROFILE = NAUTILUS_ENGINE_HARNESS_ACCOUNT_PROFILE
EVIDENCE_CLASS = NAUTILUS_ENGINE_HARNESS_EVIDENCE_CLASS


class _HarnessClock:
    def timestamp_ns(self) -> int:
        return 1_780_926_800_000_000_000


class _HarnessLog:
    def debug(self, *_args: Any, **_kwargs: Any) -> None:
        return None

    def warning(self, *_args: Any, **_kwargs: Any) -> None:
        return None


class _HarnessClient:
    def __init__(self, provider: CtpNautilusInstrumentProvider) -> None:
        self.instrument_provider = provider
        self._clock = _HarnessClock()
        self._log = _HarnessLog()
        self._order_status_reports = []
        self._fill_reports = []
        self._position_status_reports = []
        self._seen_exec_report_keys = set()
        self._coerce_exec_payload = CtpLiveExecutionClient._coerce_exec_payload
        self._exec_report_key = CtpLiveExecutionClient._exec_report_key

    def _report_account_id(self) -> str:
        return "OPENCTP-TTS-REDACTED"


def _provider() -> CtpNautilusInstrumentProvider:
    provider = CtpNautilusInstrumentProvider()
    provider.hydrate_ctp_metadata(
        (
            NormalizedCtpInstrument(
                raw_symbol="c2609",
                raw_exchange_id="DCE",
                venue_symbol="c2609",
                exchange_id="DCE",
                display_symbol="c2609.DCE",
                underlying="c",
                contract_month="2609",
                product_kind=CtpProductKind.FUTURES,
                instrument_name="corn simulation",
                price_tick=1.0,
                volume_multiple=10,
            ),
        )
    )
    return provider


def _event_payloads() -> list[CtpTdExecEventPayload]:
    return [
        CtpTdExecEventPayload(
            order_id="SYS-ACCEPT",
            venue_symbol="c2609",
            order_ref="11",
            front_id=1,
            session_id=-1,
            status=0,
            is_trade=False,
            trade_price=0.0,
            trade_volume=0,
            leaves_qty=1,
            error_message="",
        ),
        CtpTdExecEventPayload(
            order_id="SYS-CANCEL",
            venue_symbol="c2609",
            order_ref="12",
            front_id=1,
            session_id=-1,
            status=53,
            is_trade=False,
            trade_price=0.0,
            trade_volume=0,
            leaves_qty=0,
            error_message="",
        ),
        CtpTdExecEventPayload(
            order_id="SYS-REJECT",
            venue_symbol="c2609",
            order_ref="13",
            front_id=1,
            session_id=-1,
            status=97,
            is_trade=False,
            trade_price=0.0,
            trade_volume=0,
            leaves_qty=1,
            error_message="price rejected",
        ),
        CtpTdExecEventPayload(
            order_id="SYS-FILL",
            venue_symbol="c2609",
            order_ref="14",
            front_id=1,
            session_id=-1,
            status=0,
            is_trade=True,
            trade_price=2300.0,
            trade_volume=1,
            leaves_qty=0,
            error_message="",
        ),
        CtpTdExecEventPayload(
            order_id="SYS-FILL",
            venue_symbol="c2609",
            order_ref="14",
            front_id=1,
            session_id=-1,
            status=0,
            is_trade=True,
            trade_price=2300.0,
            trade_volume=1,
            leaves_qty=0,
            error_message="",
        ),
    ]


def build_engine_harness_payload(*, run_id: str) -> dict[str, Any]:
    provider = _provider()
    client = _HarnessClient(provider)
    for payload in _event_payloads():
        CtpLiveExecutionClient._handle_td_exec_event(client, payload)

    position_report = ctp_position_record_to_status_report(
        CtpPositionRecord(
            venue_symbol="c2609",
            exchange_id="DCE",
            direction="SHORT",
            position_qty=2,
            yd_position_qty=2,
            td_position_qty=0,
            position_cost=46_000.0,
        ),
        account_id="OPENCTP-TTS-REDACTED",
        instrument_provider=provider,
        ts_init=client._clock.timestamp_ns(),
    )
    if position_report is not None:
        client._position_status_reports.append(position_report)
    account_state = ctp_account_record_to_account_state(
        CtpAccountRecord(
            account_id="OPENCTP-TTS-REDACTED",
            balance=10_000_000.0,
            available=9_950_000.0,
            margin=50_000.0,
            commission=0.0,
            close_profit=0.0,
            position_profit=0.0,
        ),
        ts_init=client._clock.timestamp_ns(),
    )

    instrument_id = InstrumentId.from_str("c2609.DCE")
    order_reports = asyncio.run(
        CtpLiveExecutionClient.generate_order_status_reports(
            client,
            GenerateOrderStatusReports(
                instrument_id=instrument_id,
                start=None,
                end=None,
                open_only=False,
                command_id=UUID4(),
                ts_init=1,
            ),
        )
    )
    fill_reports = asyncio.run(
        CtpLiveExecutionClient.generate_fill_reports(
            client,
            GenerateFillReports(
                instrument_id=instrument_id,
                venue_order_id=None,
                start=None,
                end=None,
                command_id=UUID4(),
                ts_init=1,
            ),
        )
    )
    position_reports = asyncio.run(
        CtpLiveExecutionClient.generate_position_status_reports(
            client,
            GeneratePositionStatusReports(
                instrument_id=instrument_id,
                start=None,
                end=None,
                command_id=UUID4(),
                ts_init=1,
            ),
        )
    )

    return build_nautilus_engine_harness_payload(
        run_id=run_id,
        instrument_ids=[item.id.value for item in provider.list_all()],
        order_statuses=[report.order_status.name for report in order_reports],
        order_report_count=len(order_reports),
        fill_report_count=len(fill_reports),
        position_report_count=len(position_reports),
        account_state_reported=account_state.is_reported,
        account_id_redacted=account_state.account_id.value == "OPENCTP-TTS-REDACTED",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Run minimal Nautilus-facing CTP engine harness evidence.")
    parser.add_argument("--run-id", default="p004-nautilus-engine-harness")
    parser.add_argument("--output-json", type=Path)
    args = parser.parse_args()

    payload = build_engine_harness_payload(run_id=args.run_id)
    if args.output_json is not None:
        output_path = args.output_json if args.output_json.is_absolute() else REPO_ROOT / args.output_json
        write_json_payload(path=output_path, payload=payload)
    print(json.dumps(payload, ensure_ascii=False))
    return 0 if payload["success"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
