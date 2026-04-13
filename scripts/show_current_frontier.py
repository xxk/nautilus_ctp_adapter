"""show_current_frontier: 输出当前 active change 与 frontier 状态摘要。

扫描 docs/changes/ 下所有 change 目录，从 plan.md 提取状态，
识别 in_progress 的 change 并输出 JSON 摘要。
支持 --by-topic 按 topic-id 分组输出。
支持 execution_order 消歧（多 active change 时按升序排列）。
输出 CURRENT_FRONTIER_OK，exit 0。
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

CHANGE_ID_RE = re.compile(r"^(?:\d{8}|\d{4}-\d{2}-\d{2})__[^_]+__.+$")
STATUS_RE = re.compile(r"^\*\*(?:状态|Status)\*\*[:：]\s*(.+)$", re.MULTILINE)
PROGRESS_RE = re.compile(r"^\*\*(?:进度|Progress)\*\*[:：]\s*(.+)$", re.MULTILINE)
TITLE_RE = re.compile(r"^#\s+(.+)", re.MULTILINE)
TOPIC_ID_RE = re.compile(r"^\*\*topic-id\*\*[:：]\s*(.+)$", re.MULTILINE)
EXECUTION_ORDER_RE = re.compile(r"^\*\*execution_order\*\*[:：]\s*(\d+)", re.MULTILINE)


def discover_change_dirs(changes_dir: Path) -> list[Path]:
    if not changes_dir.exists():
        return []
    return sorted(
        path
        for path in changes_dir.iterdir()
        if path.is_dir() and CHANGE_ID_RE.fullmatch(path.name)
    )


def _extract_plan_metadata(plan_path: Path) -> dict[str, str | int | None]:
    if not plan_path.exists():
        return {"status": "unknown", "progress": "unknown", "title": "unknown",
                "topic_id": None, "execution_order": None}

    text = plan_path.read_text(encoding="utf-8")

    status_match = STATUS_RE.search(text)
    status = status_match.group(1).strip() if status_match else "unknown"

    progress_match = PROGRESS_RE.search(text)
    progress = progress_match.group(1).strip() if progress_match else "unknown"

    title_match = TITLE_RE.search(text)
    title = title_match.group(1).strip() if title_match else "unknown"

    topic_match = TOPIC_ID_RE.search(text)
    topic_id = topic_match.group(1).strip() if topic_match else None
    if topic_id and ("{{" in topic_id or "例如" in topic_id):
        topic_id = None

    order_match = EXECUTION_ORDER_RE.search(text)
    execution_order = int(order_match.group(1)) if order_match else None

    return {"status": status, "progress": progress, "title": title,
            "topic_id": topic_id, "execution_order": execution_order}


def _classify_status(raw_status: str) -> str:
    low = raw_status.lower()
    if "进行中" in raw_status or "in_progress" in low or "in progress" in low:
        return "in_progress"
    if "已完成" in raw_status or "completed" in low or "done" in low:
        return "completed"
    if "已验收" in raw_status or "accepted" in low:
        return "completed"
    if "draft" in low:
        return "draft"
    if "blocked" in low or "阻塞" in raw_status:
        return "blocked"
    return "not_started"


def show_frontier(root: Path) -> dict:
    changes_dir = root / "docs" / "changes"
    change_dirs = discover_change_dirs(changes_dir)

    active_changes: list[dict] = []
    completed_count = 0
    draft_count = 0
    blocked_count = 0
    total = len(change_dirs)

    for change_dir in change_dirs:
        meta = _extract_plan_metadata(change_dir / "plan.md")
        classified = _classify_status(meta["status"])

        if classified == "in_progress":
            active_changes.append({
                "change_id": change_dir.name,
                "title": meta["title"],
                "progress": meta["progress"],
                "raw_status": meta["status"],
                "topic_id": meta["topic_id"],
                "execution_order": meta["execution_order"],
            })
        elif classified == "completed":
            completed_count += 1
        elif classified == "draft":
            draft_count += 1
        elif classified == "blocked":
            blocked_count += 1

    def _sort_key(ch: dict) -> tuple:
        order = ch["execution_order"]
        return (0 if order is not None else 1, order or 999999, ch["change_id"])

    active_changes.sort(key=_sort_key)

    return {
        "active_changes": active_changes,
        "active_count": len(active_changes),
        "completed_count": completed_count,
        "draft_count": draft_count,
        "blocked_count": blocked_count,
        "total_changes": total,
    }


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Show current active changes and frontier status summary.",
    )
    parser.add_argument("--root", type=Path, default=REPO_ROOT, help="Repository root")
    parser.add_argument("--json", action="store_true", help="Output JSON format")
    parser.add_argument("--by-topic", action="store_true", help="Group by topic-id")
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    root = args.root.resolve()
    result = show_frontier(root)

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        active = result["active_changes"]
        if active:
            if args.by_topic:
                groups: dict[str, list[dict]] = {}
                for ch in active:
                    tid = ch.get("topic_id") or "(no topic)"
                    groups.setdefault(tid, []).append(ch)
                for tid, changes in groups.items():
                    print(f"\n[{tid}] ({len(changes)} changes):")
                    for ch in changes:
                        order = f" order={ch['execution_order']}" if ch.get("execution_order") else ""
                        print(f"  - {ch['change_id']}: {ch['title']} [{ch['progress']}]{order}")
            else:
                print(f"Active changes ({len(active)}):")
                for ch in active:
                    order = f" order={ch['execution_order']}" if ch.get("execution_order") else ""
                    tid = f" [{ch['topic_id']}]" if ch.get("topic_id") else ""
                    print(f"  - {ch['change_id']}: {ch['title']} [{ch['progress']}]{tid}{order}")
        else:
            print("Active changes: none")
        print(
            f"CURRENT_FRONTIER_OK:"
            f" active={result['active_count']}"
            f" completed={result['completed_count']}"
            f" draft={result['draft_count']}"
            f" blocked={result['blocked_count']}"
            f" total={result['total_changes']}"
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
