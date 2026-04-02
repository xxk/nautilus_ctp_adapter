from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from nautilus_ctp_adapter.adapters.ctp.config import CtpAdapterConfig
from nautilus_ctp_adapter.adapters.ctp.factory import build_ctp_stack


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the repository-owned instrument query smoke.")
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--symbol", required=True)
    parser.add_argument("--timeout-seconds", type=int, default=20)
    args = parser.parse_args()

    config = CtpAdapterConfig.from_json_file(args.config)
    stack = build_ctp_stack(config)
    provider = stack["instrument_provider"]
    bridge = stack["runtime_bridge"]

    result = provider.run_live_instrument_smoke(symbol=args.symbol, timeout_seconds=args.timeout_seconds)
    events = bridge.drain_events()

    payload = {
        "request_id": result.request_id,
        "loaded": result.loaded,
        "instrument_count": result.instrument_count,
        "symbols": [item.display_symbol for item in result.instruments],
        "bridge_event_kinds": [event.kind.value for event in events],
        "first_instrument": None
        if not result.instruments
        else {
            "display_symbol": result.instruments[0].display_symbol,
            "underlying": result.instruments[0].underlying,
            "contract_month": result.instruments[0].contract_month,
            "product_kind": result.instruments[0].product_kind.value,
            "price_tick": result.instruments[0].price_tick,
            "volume_multiple": result.instruments[0].volume_multiple,
        },
    }
    print(json.dumps(payload, ensure_ascii=False))
    return 0 if result.loaded and result.instrument_count > 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
