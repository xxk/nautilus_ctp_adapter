"""check_topic_docs: 校验 topic 文档与索引投影是否一致。"""
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from nautilus_ctp_adapter.devtools.topic_governance import main_check_topic_docs


if __name__ == "__main__":
    raise SystemExit(main_check_topic_docs())
