from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from nautilus_ctp_adapter.repo_debug_smoke import collect_repo_debug_smoke_snapshot
from nautilus_ctp_adapter.diagnostics.evidence_payloads import (
    REPO_DEBUG_SMOKE_BASELINE,
    build_repo_debug_smoke_payload,
)


BASELINE = REPO_DEBUG_SMOKE_BASELINE


def _emit_payload(payload: dict[str, object]) -> None:
    print(json.dumps(payload, ensure_ascii=False))


def main() -> int:
    snapshot = collect_repo_debug_smoke_snapshot()

    payload = build_repo_debug_smoke_payload(snapshot)
    _emit_payload(payload)
    return 0 if payload["success"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
