"""check_harness: 检查 AGENTS.md 入口地图与治理闭环最小结构。

输出 HARNESS_CHECK_OK 或 HARNESS_CHECK_FAIL，exit 0/1。
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

AGENTS_MD = "AGENTS.md"

REQUIRED_SECTIONS = (
    "Read First",
    "Directory Map",
    "Verification",
)

REQUIRED_VERIFY_COMMANDS = (
    "python scripts/check_harness.py",
    "python scripts/check_change_docs.py",
    "python scripts/show_current_frontier.py",
)


def _check_agents_md(root: Path) -> list[str]:
    findings: list[str] = []
    agents_path = root / AGENTS_MD
    if not agents_path.exists():
        findings.append(f"{AGENTS_MD} does not exist")
        return findings

    text = agents_path.read_text(encoding="utf-8")

    for section in REQUIRED_SECTIONS:
        if section not in text:
            findings.append(f"{AGENTS_MD} missing required section: {section}")

    for cmd in REQUIRED_VERIFY_COMMANDS:
        if cmd not in text:
            findings.append(f"{AGENTS_MD} missing verify command: {cmd}")

    return findings


def _check_changes_dir(root: Path) -> list[str]:
    findings: list[str] = []
    changes_dir = root / "docs" / "changes"
    if not changes_dir.exists():
        findings.append("docs/changes/ directory does not exist")
        return findings

    template_dir = changes_dir / "_template"
    if not template_dir.exists():
        findings.append("docs/changes/_template/ directory does not exist")
    else:
        for required_file in ("plan.md", "acceptance.md", "ai_constraints.md"):
            if not (template_dir / required_file).exists():
                findings.append(f"docs/changes/_template/{required_file} does not exist")

    return findings


def check_harness(root: Path) -> list[str]:
    findings: list[str] = []
    findings.extend(_check_agents_md(root))
    findings.extend(_check_changes_dir(root))
    return findings


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Check AGENTS.md entry map and minimal governance structure.",
    )
    parser.add_argument("--root", type=Path, default=REPO_ROOT, help="Repository root")
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    root = args.root.resolve()

    findings = check_harness(root)
    if findings:
        for f in findings:
            print(f"FAIL: {f}")
        print(f"HARNESS_CHECK_FAIL: {len(findings)} issues found")
        return 1

    print("HARNESS_CHECK_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
