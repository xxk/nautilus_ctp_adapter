"""check_change_docs: 全量扫描 docs/changes/ 下所有 change 目录，检查三件套完整性与格式。

输出 CHANGE_DOCS_CHECK_OK 或 CHANGE_DOCS_CHECK_FAIL，exit 0/1。
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

CHANGE_ID_RE = re.compile(r"^(?:\d{8}|\d{4}-\d{2}-\d{2})__[^_]+__.+$")
STATUS_RE = re.compile(r"^\*\*(?:状态|Status)\*\*[:：]", re.MULTILINE)
PROGRESS_RE = re.compile(r"^\*\*(?:进度|Progress)\*\*[:：]\s*(\d{1,3})%\s*$", re.MULTILINE)


def _display_path(path: Path) -> str:
    try:
        return path.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def discover_change_dirs(changes_dir: Path) -> list[Path]:
    if not changes_dir.exists():
        return []
    return sorted(
        path
        for path in changes_dir.iterdir()
        if path.is_dir() and CHANGE_ID_RE.fullmatch(path.name)
    )


def check_change_dir(change_dir: Path) -> list[str]:
    findings: list[str] = []
    plan_path = change_dir / "plan.md"
    acceptance_path = change_dir / "acceptance.md"

    if not plan_path.exists():
        findings.append(f"{_display_path(change_dir)}: missing required file `plan.md`.")
    if not acceptance_path.exists():
        findings.append(f"{_display_path(change_dir)}: missing required file `acceptance.md`.")
    if findings:
        return findings

    plan_text = plan_path.read_text(encoding="utf-8")
    acceptance_text = acceptance_path.read_text(encoding="utf-8")

    if not STATUS_RE.search(plan_text):
        findings.append(f"{_display_path(change_dir)}: `plan.md` is missing a `状態` field.")
    if not PROGRESS_RE.search(plan_text):
        findings.append(
            f"{_display_path(change_dir)}: `plan.md` is missing a `進度` field in the format `**进度**：0%`."
        )
    if not STATUS_RE.search(acceptance_text):
        findings.append(f"{_display_path(change_dir)}: `acceptance.md` is missing a `状態` field.")

    return findings


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Check all change directories under docs/changes/ for completeness.",
    )
    parser.add_argument("--root", type=Path, default=REPO_ROOT, help="Repository root")
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    root = args.root.resolve()

    changes_dir = root / "docs" / "changes"
    change_dirs = discover_change_dirs(changes_dir)

    if not change_dirs:
        print("No matching change directories found.")
        print("CHANGE_DOCS_CHECK_OK: changes=0")
        return 0

    all_findings: list[str] = []
    for change_dir in change_dirs:
        findings = check_change_dir(change_dir)
        all_findings.extend(findings)

    if all_findings:
        for finding in all_findings:
            print(f"FAIL: {finding}")
        print(f"CHANGE_DOCS_CHECK_FAIL: {len(all_findings)} issues in {len(change_dirs)} changes")
        return 1

    print(f"CHANGE_DOCS_CHECK_OK: changes={len(change_dirs)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
