from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from nautilus_ctp_adapter.repo_debug_smoke import collect_repo_debug_smoke_snapshot


BASELINE = "repo-debug-smoke-v1"


def _emit_payload(payload: dict[str, object]) -> None:
    print(json.dumps(payload, ensure_ascii=False))


def main() -> int:
    snapshot = collect_repo_debug_smoke_snapshot()

    scaffold_code = snapshot["scaffold_not_implemented"]
    invalid_handle = snapshot["invalid_handle"]
    failure_reason = None
    if not snapshot["has_internal_md_live_session"]:
        failure_reason = "internal_md_live_session_missing"
    elif not (
        snapshot["has_internal_md_live_session"]
        and snapshot["md_init_code"] == scaffold_code
        and snapshot["md_login_code"] == scaffold_code
        and snapshot["md_subscribe_code"] == scaffold_code
        and snapshot["td_init_code"] == scaffold_code
        and snapshot["td_authenticate_code"] == scaffold_code
        and snapshot["td_login_code"] == scaffold_code
        and snapshot["md_init_after_dispose_code"] == invalid_handle
    ):
        failure_reason = "scaffold_contract_mismatch"

    _emit_payload(
        {
            "baseline": BASELINE,
            "success": failure_reason is None,
            "failure_reason": failure_reason,
            **snapshot,
        }
    )
    return 0 if failure_reason is None else 1


if __name__ == "__main__":
    raise SystemExit(main())