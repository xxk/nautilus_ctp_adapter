from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CURRENT_CHANGES = PROJECT_ROOT / "docs" / "changes"
ARCHIVE_CUTOFF = "20260619"


def _change_status(change_dir: Path) -> str:
    for name in ("plan.md", "README.md", "acceptance.md"):
        path = change_dir / name
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8", errors="ignore").lower()
        if "status: completed" in text:
            return "completed"
        if "status: in_progress" in text:
            return "in_progress"
    return "unknown"


def test_completed_changes_older_than_ten_days_are_archived() -> None:
    offenders: list[str] = []
    for change_dir in sorted(CURRENT_CHANGES.iterdir()):
        if not change_dir.is_dir() or change_dir.name.startswith("_"):
            continue
        date_prefix = change_dir.name.split("__", 1)[0].split("-", 1)[0]
        if len(date_prefix) == 8 and date_prefix.isdigit() and date_prefix < ARCHIVE_CUTOFF:
            if _change_status(change_dir) == "completed":
                offenders.append(change_dir.name)

    assert offenders == []
