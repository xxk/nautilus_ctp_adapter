"""new_proposal: 从本仓 docs/proposals/_template/ 生成新的 proposal scaffold。"""
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from nautilus_ctp_adapter.devtools.proposal_governance import main_new_proposal


if __name__ == "__main__":
    raise SystemExit(main_new_proposal())