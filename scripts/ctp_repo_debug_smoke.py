from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from nautilus_ctp_adapter.repo_debug_smoke import collect_repo_debug_smoke_snapshot


def main() -> int:
    snapshot = collect_repo_debug_smoke_snapshot()
    print(json.dumps(snapshot, ensure_ascii=False, indent=2))

    scaffold_code = snapshot["scaffold_not_implemented"]
    invalid_handle = snapshot["invalid_handle"]
    success = (
        snapshot["has_internal_md_live_session"]
        and snapshot["md_init_code"] == scaffold_code
        and snapshot["md_login_code"] == scaffold_code
        and snapshot["md_subscribe_code"] == scaffold_code
        and snapshot["td_init_code"] == scaffold_code
        and snapshot["td_authenticate_code"] == scaffold_code
        and snapshot["td_login_code"] == scaffold_code
        and snapshot["md_init_after_dispose_code"] == invalid_handle
    )
    return 0 if success else 1


if __name__ == "__main__":
    raise SystemExit(main())