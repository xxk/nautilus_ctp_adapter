from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from nautilus_ctp_adapter.diagnostics.paper_session_preflight import (  # noqa: E402
    BASELINE,
    DEFAULT_CONFIG,
    OPENCTP_TTS_7X24_PROFILE,
    OPENCTP_TTS_7X24_PROFILE_ALIASES,
    build_preflight_summary,
    paper_config_issues,
    redacted_config_summary,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Preflight OpenCTP paper account config and optionally connect to paper fronts."
    )
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--connect-paper", action="store_true")
    parser.add_argument("--output-json", type=Path, default=None)
    args = parser.parse_args()

    payload = build_preflight_summary(args.config, connect_paper=args.connect_paper)
    text = json.dumps(payload, ensure_ascii=False)
    print(text)

    if args.output_json is not None:
        output_path = args.output_json if args.output_json.is_absolute() else REPO_ROOT / args.output_json
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    return 0 if payload["success"] else 1


__all__ = [
    "BASELINE",
    "DEFAULT_CONFIG",
    "OPENCTP_TTS_7X24_PROFILE",
    "OPENCTP_TTS_7X24_PROFILE_ALIASES",
    "build_preflight_summary",
    "paper_config_issues",
    "redacted_config_summary",
]


if __name__ == "__main__":
    raise SystemExit(main())
