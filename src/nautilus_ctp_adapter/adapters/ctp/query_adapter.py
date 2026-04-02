"""Nautilus-facing CTP query adapter baseline built on the shared runtime."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from nautilus_ctp_adapter.runtime import CtpAccountRecord, CtpPositionRecord, CtpRuntimeBridge

from .config import CtpAdapterConfig
from .execution_client import (
    CtpAccountQuerySmokeResult,
    CtpExecutionClient,
    CtpPositionQuerySmokeResult,
)


@dataclass(slots=True)
class CtpPositionQueryBaseline:
    request_id: str
    query_code: int
    completed: bool
    timed_out: bool
    no_positions: bool
    position_count: int
    positions: tuple[CtpPositionRecord, ...]


@dataclass(slots=True)
class CtpAccountQueryBaseline:
    request_id: str
    query_code: int
    completed: bool
    timed_out: bool
    account: CtpAccountRecord | None


@dataclass(slots=True)
class CtpQueryAdapterSnapshot:
    positions: CtpPositionQueryBaseline
    account: CtpAccountQueryBaseline


class CtpQueryAdapter:
    """Minimal Nautilus-consumable adapter baseline for position/account queries."""

    def __init__(
        self,
        config: CtpAdapterConfig | None = None,
        runtime_bridge: CtpRuntimeBridge | None = None,
        execution_client: CtpExecutionClient | None = None,
    ) -> None:
        self._config = config or CtpAdapterConfig()
        self._runtime_bridge = runtime_bridge or CtpRuntimeBridge()
        self._execution_client = execution_client or CtpExecutionClient(self._config, self._runtime_bridge)

    @property
    def runtime_bridge(self) -> CtpRuntimeBridge:
        return self._runtime_bridge

    @property
    def execution_client(self) -> CtpExecutionClient:
        return self._execution_client

    def query_positions_mainline(
        self,
        *,
        timeout_seconds: int = 20,
        flow_path: str | Path | None = None,
        completion_grace_seconds: float = 1.0,
    ) -> CtpPositionQueryBaseline:
        result = self._execution_client.run_live_position_query_smoke(
            timeout_seconds=timeout_seconds,
            flow_path=flow_path,
            completion_grace_seconds=completion_grace_seconds,
        )
        return self._map_position_result(result)

    def query_account_mainline(
        self,
        *,
        timeout_seconds: int = 20,
        flow_path: str | Path | None = None,
    ) -> CtpAccountQueryBaseline:
        result = self._execution_client.run_live_account_query_smoke(
            timeout_seconds=timeout_seconds,
            flow_path=flow_path,
        )
        return self._map_account_result(result)

    def query_snapshot_mainline(
        self,
        *,
        timeout_seconds: int = 20,
        flow_path: str | Path | None = None,
        completion_grace_seconds: float = 1.0,
    ) -> CtpQueryAdapterSnapshot:
        positions = self.query_positions_mainline(
            timeout_seconds=timeout_seconds,
            flow_path=flow_path,
            completion_grace_seconds=completion_grace_seconds,
        )
        account = self.query_account_mainline(
            timeout_seconds=timeout_seconds,
            flow_path=flow_path,
        )
        return CtpQueryAdapterSnapshot(
            positions=positions,
            account=account,
        )

    def _map_position_result(self, result: CtpPositionQuerySmokeResult) -> CtpPositionQueryBaseline:
        return CtpPositionQueryBaseline(
            request_id=result.query_request_id,
            query_code=result.query_code,
            completed=result.completed,
            timed_out=result.timed_out,
            no_positions=result.no_positions,
            position_count=result.position_count,
            positions=result.positions,
        )

    def _map_account_result(self, result: CtpAccountQuerySmokeResult) -> CtpAccountQueryBaseline:
        return CtpAccountQueryBaseline(
            request_id=result.query_request_id,
            query_code=result.query_code,
            completed=result.completed,
            timed_out=result.timed_out,
            account=result.account,
        )
