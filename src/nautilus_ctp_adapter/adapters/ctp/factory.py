"""Factory helpers for downstream project integration."""

from nautilus_ctp_adapter.runtime import CtpRuntimeBridge

from .config import CtpAdapterConfig
from .data_client import CtpDataClient
from .execution_client import CtpExecutionClient
from .instrument_provider import CtpInstrumentProvider


def build_ctp_stack(config: CtpAdapterConfig) -> dict[str, object]:
    """Return a minimal placeholder stack for future Nautilus wiring."""
    runtime_bridge = CtpRuntimeBridge()
    return {
        "config": config,
        "runtime_bridge": runtime_bridge,
        "instrument_provider": CtpInstrumentProvider(),
        "data_client": CtpDataClient(config, runtime_bridge),
        "execution_client": CtpExecutionClient(config, runtime_bridge),
    }
