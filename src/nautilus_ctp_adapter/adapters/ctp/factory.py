"""Factory helpers for downstream project integration."""

from nautilus_ctp_adapter.runtime import CtpRuntimeBridge

from .config import CtpAdapterConfig
from .data_client import CtpDataClient
from .execution_client import CtpExecutionClient
from .instrument_provider import CtpInstrumentProvider
from .ops_snapshot import CtpLiveOpsSnapshotAdapter
from .query_adapter import CtpQueryAdapter
from .reconciliation import CtpReconciliationAdapter
from .startup_truth import CtpStartupTruthAdapter
from .truth_merge import CtpTruthMergeAdapter


def build_ctp_stack(config: CtpAdapterConfig) -> dict[str, object]:
    """Return a minimal placeholder stack for future Nautilus wiring."""
    runtime_bridge = CtpRuntimeBridge()
    execution_client = CtpExecutionClient(config, runtime_bridge)
    query_adapter = CtpQueryAdapter(config, runtime_bridge, execution_client)
    return {
        "config": config,
        "runtime_bridge": runtime_bridge,
        "instrument_provider": CtpInstrumentProvider(config, runtime_bridge),
        "data_client": CtpDataClient(config, runtime_bridge),
        "execution_client": execution_client,
        "query_adapter": query_adapter,
        "reconciliation_adapter": CtpReconciliationAdapter(
            config,
            runtime_bridge,
            query_adapter,
        ),
        "truth_merge_adapter": CtpTruthMergeAdapter(
            config,
            runtime_bridge,
            execution_client,
            query_adapter,
        ),
        "startup_truth_adapter": CtpStartupTruthAdapter(
            config,
            runtime_bridge,
            execution_client,
        ),
        "live_ops_snapshot_adapter": CtpLiveOpsSnapshotAdapter(
            config,
            runtime_bridge,
        ),
    }
