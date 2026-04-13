"""autopilot: 一条命令输出 frontier + TASK-LIST 粒度 + checkpoint 断点续做。

Route B 实现：无独立 registry，从 plan.md frontmatter 聚合 topic/execution_order。

用法：
    python scripts/autopilot.py --root .
    python scripts/autopilot.py --root . --update-checkpoint "T1 done: 完成骨架"
    python scripts/autopilot.py --root . --backfill
    python scripts/autopilot.py --root . --json
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.show_current_frontier import (
    _extract_plan_metadata,
    _classify_status,
    discover_change_dirs,
    show_frontier,
)

# ── TASK-LIST 解析 ──────────────────────────────────────────
TASK_LIST_BLOCK_PATTERN = re.compile(
    r"<!-- TASK-LIST-BEGIN\s*\n(?P<body>.*?)\nTASK-LIST-END -->",
    re.DOTALL,
)
TASK_ITEM_PATTERN = re.compile(
    r"^- \[(?P<check>[ xX])\] (?P<key>T\d+): (?P<label>.+)$",
)

CHECKPOINT_FILENAME = ".autopilot_checkpoint.json"

# ── acceptance AI-STATUS 解析 ───────────────────────────────
AI_STATUS_BLOCK_PATTERN = re.compile(
    r"```ya?ml\s*\n(?P<body>.*?)\n```",
    re.DOTALL,
)
AI_CONCLUSION_RE = re.compile(r"conclusion:\s*(\S+)")
AI_SCENARIOS_TOTAL_RE = re.compile(r"scenarios_total:\s*(\d+)")
AI_SCENARIOS_PASSED_RE = re.compile(r"scenarios_passed:\s*(\d+)")


@dataclass(frozen=True)
class TaskListItem:
    key: str
    label: str
    completed: bool


@dataclass(frozen=True)
class AutopilotCheckpoint:
    change_id: str
    current_task: str | None
    completed_tasks: tuple[str, ...]
    last_action: str
    context_summary: str
    updated_at: str


@dataclass(frozen=True)
class AcceptanceSnapshot:
    conclusion: str
    scenarios_total: int
    scenarios_passed: int


@dataclass(frozen=True)
class AutopilotSnapshot:
    active_change_id: str | None
    active_title: str
    active_progress: str
    topic_id: str | None
    execution_order: int | None
    task_list: tuple[TaskListItem, ...]
    current_task: str | None
    next_task: str | None
    checkpoint: AutopilotCheckpoint | None
    acceptance: AcceptanceSnapshot | None
    total_changes: int
    active_count: int
    completed_count: int


# ── TASK-LIST 解析 ──────────────────────────────────────────

def parse_task_list(plan_path: Path) -> tuple[TaskListItem, ...]:
    if not plan_path.exists():
        return ()
    text = plan_path.read_text(encoding="utf-8")
    match = TASK_LIST_BLOCK_PATTERN.search(text)
    if match is None:
        return ()
    items: list[TaskListItem] = []
    for line in match.group("body").strip().splitlines():
        m = TASK_ITEM_PATTERN.match(line.strip())
        if m is None:
            continue
        items.append(TaskListItem(
            key=m.group("key"),
            label=m.group("label").strip(),
            completed=m.group("check").strip().lower() == "x",
        ))
    return tuple(items)


def resolve_current_task(tasks: tuple[TaskListItem, ...]) -> str | None:
    for task in tasks:
        if not task.completed:
            return task.key
    return None


def resolve_next_task(tasks: tuple[TaskListItem, ...], current: str | None) -> str | None:
    found_current = False
    for task in tasks:
        if task.key == current:
            found_current = True
            continue
        if found_current and not task.completed:
            return task.key
    return None


# ── Checkpoint 读写 ─────────────────────────────────────────

def read_checkpoint(root: Path) -> AutopilotCheckpoint | None:
    path = root / CHECKPOINT_FILENAME
    if not path.exists():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        completed_raw = payload.get("completed_tasks") or []
        return AutopilotCheckpoint(
            change_id=str(payload.get("change_id") or ""),
            current_task=str(payload["current_task"]) if payload.get("current_task") else None,
            completed_tasks=tuple(str(t) for t in completed_raw if t),
            last_action=str(payload.get("last_action") or ""),
            context_summary=str(payload.get("context_summary") or ""),
            updated_at=str(payload.get("updated_at") or ""),
        )
    except (json.JSONDecodeError, OSError, KeyError):
        return None


def write_checkpoint(root: Path, checkpoint: AutopilotCheckpoint) -> None:
    path = root / CHECKPOINT_FILENAME
    payload = {
        "version": 1,
        "change_id": checkpoint.change_id,
        "current_task": checkpoint.current_task,
        "completed_tasks": list(checkpoint.completed_tasks),
        "last_action": checkpoint.last_action,
        "context_summary": checkpoint.context_summary,
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


# ── Acceptance 解析 ─────────────────────────────────────────

def parse_acceptance_status(acceptance_path: Path) -> AcceptanceSnapshot | None:
    if not acceptance_path.exists():
        return None
    text = acceptance_path.read_text(encoding="utf-8")
    match = AI_STATUS_BLOCK_PATTERN.search(text)
    if match is None:
        return None
    body = match.group("body")
    conclusion_m = AI_CONCLUSION_RE.search(body)
    total_m = AI_SCENARIOS_TOTAL_RE.search(body)
    passed_m = AI_SCENARIOS_PASSED_RE.search(body)
    return AcceptanceSnapshot(
        conclusion=conclusion_m.group(1) if conclusion_m else "unknown",
        scenarios_total=int(total_m.group(1)) if total_m else 0,
        scenarios_passed=int(passed_m.group(1)) if passed_m else 0,
    )


# ── Snapshot 构建 ───────────────────────────────────────────

def build_snapshot(root: Path, change_id: str | None = None) -> AutopilotSnapshot:
    frontier = show_frontier(root)
    active = frontier["active_changes"]
    checkpoint = read_checkpoint(root)

    selected = None
    if checkpoint and checkpoint.change_id:
        selected = next((c for c in active if c["change_id"] == checkpoint.change_id), None)
    if selected is None and change_id:
        selected = next((c for c in active if c["change_id"] == change_id), None)
    if selected is None and active:
        selected = active[0]

    if selected is None:
        return AutopilotSnapshot(
            active_change_id=None, active_title="none", active_progress="N/A",
            topic_id=None, execution_order=None,
            task_list=(), current_task=None, next_task=None,
            checkpoint=checkpoint, acceptance=None,
            total_changes=frontier["total_changes"],
            active_count=frontier["active_count"],
            completed_count=frontier["completed_count"],
        )

    plan_path = root / "docs" / "changes" / selected["change_id"] / "plan.md"
    acceptance_path = root / "docs" / "changes" / selected["change_id"] / "acceptance.md"

    task_list = parse_task_list(plan_path)
    current_task = resolve_current_task(task_list)
    next_task = resolve_next_task(task_list, current_task)
    acceptance = parse_acceptance_status(acceptance_path)

    return AutopilotSnapshot(
        active_change_id=selected["change_id"],
        active_title=selected["title"],
        active_progress=selected["progress"],
        topic_id=selected.get("topic_id"),
        execution_order=selected.get("execution_order"),
        task_list=task_list,
        current_task=current_task,
        next_task=next_task,
        checkpoint=checkpoint,
        acceptance=acceptance,
        total_changes=frontier["total_changes"],
        active_count=frontier["active_count"],
        completed_count=frontier["completed_count"],
    )


# ── Backfill: acceptance 结论回写 plan.md ───────────────────

def backfill_plan_from_acceptance(root: Path, change_id: str | None = None) -> list[str]:
    changes_dir = root / "docs" / "changes"
    results: list[str] = []

    dirs = discover_change_dirs(changes_dir)
    if change_id:
        dirs = [d for d in dirs if d.name == change_id]

    for change_dir in dirs:
        plan_path = change_dir / "plan.md"
        acceptance_path = change_dir / "acceptance.md"
        if not plan_path.exists() or not acceptance_path.exists():
            continue

        acc = parse_acceptance_status(acceptance_path)
        if acc is None or acc.conclusion == "unknown":
            continue

        plan_text = plan_path.read_text(encoding="utf-8")
        meta = _extract_plan_metadata(plan_path)
        classified = _classify_status(meta["status"])

        if acc.conclusion == "passed" and classified != "completed":
            new_text = re.sub(
                r"^\*\*状态\*\*[:：]\s*.+$",
                "**状态**：已完成",
                plan_text,
                count=1,
                flags=re.MULTILINE,
            )
            if new_text != plan_text:
                plan_path.write_text(new_text, encoding="utf-8")
                results.append(f"BACKFILL: {change_dir.name} status -> 已完成")

    return results


# ── 文本渲染 ────────────────────────────────────────────────

def render_text(snapshot: AutopilotSnapshot) -> str:
    lines = [
        f"ACTIVE_CHANGE: {snapshot.active_change_id or 'none'}",
        f"ACTIVE_TITLE: {snapshot.active_title}",
        f"ACTIVE_PROGRESS: {snapshot.active_progress}",
        f"TOPIC_ID: {snapshot.topic_id or 'N/A'}",
        f"EXECUTION_ORDER: {snapshot.execution_order or 'N/A'}",
    ]

    if snapshot.task_list:
        lines.append(f"TASK_LIST: {len(snapshot.task_list)} items")
        for task in snapshot.task_list:
            mark = "✅" if task.completed else "⬜"
            lines.append(f"  {mark} {task.key}: {task.label}")
        lines.append(f"CURRENT_TASK: {snapshot.current_task or 'all done'}")
        lines.append(f"NEXT_TASK: {snapshot.next_task or 'N/A'}")
    else:
        lines.append("TASK_LIST: none (no TASK-LIST-BEGIN/END block)")

    if snapshot.acceptance:
        a = snapshot.acceptance
        lines.append(f"ACCEPTANCE: {a.conclusion} ({a.scenarios_passed}/{a.scenarios_total})")

    if snapshot.checkpoint:
        cp = snapshot.checkpoint
        lines.append(f"CHECKPOINT: change={cp.change_id} task={cp.current_task} updated={cp.updated_at}")
        lines.append(f"LAST_ACTION: {cp.last_action}")

    lines.append(
        f"FRONTIER: active={snapshot.active_count}"
        f" completed={snapshot.completed_count}"
        f" total={snapshot.total_changes}"
    )
    lines.append("AUTOPILOT_OK")
    return "\n".join(lines)


# ── CLI ─────────────────────────────────────────────────────

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="autopilot", description="Autopilot CLI (Route B)")
    parser.add_argument("--root", type=Path, default=REPO_ROOT, help="Repository root")
    parser.add_argument("--change-id", help="Target change-id")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    parser.add_argument("--update-checkpoint", metavar="ACTION", help="Update checkpoint with action")
    parser.add_argument("--checkpoint-context", default="", help="Additional checkpoint context")
    parser.add_argument("--backfill", action="store_true", help="Backfill plan.md status from acceptance")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    root = args.root.resolve()

    if args.backfill:
        results = backfill_plan_from_acceptance(root, change_id=args.change_id)
        if results:
            for r in results:
                print(r)
        else:
            print("BACKFILL: no changes needed")
        return 0

    if args.update_checkpoint:
        snapshot = build_snapshot(root, change_id=args.change_id)
        existing = read_checkpoint(root)
        change_id = args.change_id or (existing.change_id if existing else None) or snapshot.active_change_id
        if not change_id:
            print("ERROR: no active change to checkpoint", file=sys.stderr)
            return 1
        new_checkpoint = AutopilotCheckpoint(
            change_id=change_id,
            current_task=snapshot.current_task,
            completed_tasks=existing.completed_tasks if existing else (),
            last_action=args.update_checkpoint,
            context_summary=args.checkpoint_context,
            updated_at=datetime.now().strftime("%Y-%m-%d %H:%M"),
        )
        write_checkpoint(root, new_checkpoint)
        print(f"CHECKPOINT_UPDATED: {root / CHECKPOINT_FILENAME}")
        return 0

    snapshot = build_snapshot(root, change_id=args.change_id)
    if args.json:
        print(json.dumps(asdict(snapshot), indent=2, ensure_ascii=False))
    else:
        print(render_text(snapshot))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
