"""check_proposal_docs: 检查 docs/proposals/ 索引、模板与 proposal 文档完整性。"""
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from nautilus_ctp_adapter.devtools.proposal_governance import main_check_proposal_docs


if __name__ == "__main__":
    raise SystemExit(main_check_proposal_docs())