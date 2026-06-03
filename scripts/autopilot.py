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
import hashlib
import json
import re
import sys
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.check_change_docs import discover_change_dirs
from nautilus_ctp_adapter.devtools.topic_governance import collect_current_frontier


def _extract_plan_metadata(plan_path: Path) -> dict[str, object]:
    text = plan_path.read_text(encoding="utf-8")

    def field(name: str, default: str = "") -> str:
        match = re.search(rf"^\*\*{re.escape(name)}\*\*[:：]\s*(.+)$", text, flags=re.MULTILINE)
        return default if match is None else match.group(1).strip()

    title = plan_path.parent.name
    for line in text.splitlines():
        if line.startswith("# "):
            title = line[2:].strip()
            break

    execution_order_raw = field("execution_order")
    execution_order: int | None = None
    if execution_order_raw.isdigit():
        execution_order = int(execution_order_raw)

    return {
        "title": title,
        "status": field("状态", field("Status", "")),
        "progress": field("进度", field("Progress", "N/A")),
        "topic_id": field("topic-id").strip("`") or None,
        "execution_order": execution_order,
    }


def _classify_status(status: object) -> str:
    value = str(status).strip().lower()
    if any(marker in value for marker in ("completed", "已完成", "✅", "passed", "pass")):
        return "completed"
    if any(marker in value for marker in ("in_progress", "进行中", "🔄")):
        return "in_progress"
    if any(marker in value for marker in ("blocked", "阻塞")):
        return "blocked"
    return "not_started"


def show_frontier(root: Path) -> dict[str, object]:
    frontier = collect_current_frontier(root)
    changes_dir = root / "docs" / "changes"
    change_dirs = discover_change_dirs(changes_dir)

    active_changes: list[dict[str, object]] = []
    active_change = frontier.get("active_change")
    active_topic = frontier.get("active_topic")
    if isinstance(active_change, dict) and active_change.get("change_id"):
        change_id = str(active_change["change_id"])
        plan_path = changes_dir / change_id / "plan.md"
        meta = _extract_plan_metadata(plan_path) if plan_path.exists() else {}
        active_changes.append(
            {
                "change_id": change_id,
                "title": meta.get("title", change_id),
                "progress": meta.get("progress", "N/A"),
                "topic_id": None if not isinstance(active_topic, dict) else active_topic.get("topic_id"),
                "execution_order": None
                if not isinstance(active_topic, dict)
                else active_topic.get("execution_order"),
            }
        )

    completed_count = 0
    for change_dir in change_dirs:
        plan_path = change_dir / "plan.md"
        if plan_path.exists() and _classify_status(_extract_plan_metadata(plan_path)["status"]) == "completed":
            completed_count += 1

    return {
        "active_changes": active_changes,
        "total_changes": len(change_dirs),
        "active_count": len(active_changes),
        "completed_count": completed_count,
    }

# ── TASK-LIST 解析 ──────────────────────────────────────────
TASK_LIST_BLOCK_PATTERN = re.compile(
    r"<!-- TASK-LIST-BEGIN\s*\n(?P<body>.*?)\nTASK-LIST-END -->",
    re.DOTALL,
)
TASK_ITEM_PATTERN = re.compile(
    r"^- \[(?P<check>[ xX])\] (?P<key>T\d+): (?P<label>.+)$",
)

CHECKPOINT_FILENAME = ".autopilot_checkpoint.json"
TRAJECTORY_FILENAME = ".autopilot_trajectory.jsonl"

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
    version: int = 2
    repo_state_hash: dict[str, str] = field(default_factory=dict)
    completed_task_summaries: dict[str, str] = field(default_factory=dict)
    blocker: dict[str, object] | None = None


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
    recent_actions: tuple[dict[str, object], ...]
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
            version=int(payload.get("version") or 1),
            repo_state_hash={str(k): str(v) for k, v in (payload.get("repo_state_hash") or {}).items()},
            completed_task_summaries={
                str(k): str(v) for k, v in (payload.get("completed_task_summaries") or {}).items()
            },
            blocker=payload.get("blocker") if isinstance(payload.get("blocker"), dict) else None,
        )
    except (json.JSONDecodeError, OSError, KeyError):
        return None


def write_checkpoint(root: Path, checkpoint: AutopilotCheckpoint) -> None:
    path = root / CHECKPOINT_FILENAME
    payload = {
        "version": checkpoint.version,
        "change_id": checkpoint.change_id,
        "current_task": checkpoint.current_task,
        "completed_tasks": list(checkpoint.completed_tasks),
        "last_action": checkpoint.last_action,
        "context_summary": checkpoint.context_summary,
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "repo_state_hash": checkpoint.repo_state_hash,
        "completed_task_summaries": checkpoint.completed_task_summaries,
        "blocker": checkpoint.blocker,
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _hash_file(path: Path) -> str | None:
    if not path.exists() or not path.is_file():
        return None
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    return digest[:12]


def compute_repo_state_hash(root: Path, change_id: str | None) -> dict[str, str]:
    paths = [
        root / "scripts" / "autopilot.py",
        root / "scripts" / "show_current_frontier.py",
        root / "AGENTS.md",
    ]
    if change_id:
        change_root = root / "docs" / "changes" / change_id
        paths.extend(
            [
                change_root / "plan.md",
                change_root / "acceptance.md",
                change_root / "ai_constraints.md",
            ]
        )

    state: dict[str, str] = {}
    for path in paths:
        digest = _hash_file(path)
        if digest is None:
            continue
        state[path.relative_to(root).as_posix()] = digest
    return state


def detect_drift(root: Path, checkpoint: AutopilotCheckpoint | None) -> tuple[str, ...]:
    if checkpoint is None or not checkpoint.repo_state_hash:
        return ("DRIFT_CLEAN: no checkpoint hash available",)
    current = compute_repo_state_hash(root, checkpoint.change_id)
    findings = []
    for rel_path, old_hash in checkpoint.repo_state_hash.items():
        new_hash = current.get(rel_path)
        if new_hash != old_hash:
            findings.append(f"DRIFT_DETECTED: {rel_path} changed since last checkpoint")
    if findings:
        return tuple(findings)
    return ("DRIFT_CLEAN: no file changes detected",)


def read_trajectory(root: Path, limit: int) -> tuple[dict[str, object], ...]:
    path = root / TRAJECTORY_FILENAME
    if not path.exists():
        return ()
    records: list[dict[str, object]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(payload, dict):
            records.append(payload)
    return tuple(records[-limit:])


def append_trajectory(
    root: Path,
    *,
    change_id: str | None,
    task: str | None,
    action: str,
    target: str,
    detail: str,
    result: str,
) -> Path:
    path = root / TRAJECTORY_FILENAME
    entry = {
        "ts": datetime.now().isoformat(timespec="seconds"),
        "session_id": uuid.uuid4().hex[:8],
        "change_id": change_id,
        "task": task,
        "action": action,
        "target": target,
        "result": result,
        "detail": detail,
    }
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry, ensure_ascii=False, sort_keys=True) + "\n")
    return path


def parse_blocker(raw: str) -> dict[str, object]:
    blocker_type, sep, description = raw.partition(":")
    parsed_type = blocker_type.strip() if sep else "dependency_missing"
    parsed_description = description.strip() if sep else raw.strip()
    escalation = {
        "scope_expansion": "split_derived",
        "dependency_missing": "wait_human",
        "contract_conflict": "wait_human",
        "test_failure": "auto_retry",
    }.get(parsed_type, "wait_human")
    return {
        "type": parsed_type,
        "description": parsed_description,
        "escalation": escalation,
        "retry_count": 0,
        "max_retries": 2,
    }


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
            recent_actions=read_trajectory(root, 5),
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
        recent_actions=read_trajectory(root, 5),
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
        summaries = snapshot.checkpoint.completed_task_summaries if snapshot.checkpoint else {}
        for task in snapshot.task_list:
            mark = "[x]" if task.completed else "[ ]"
            summary = summaries.get(task.key)
            suffix = f" — {summary}" if summary else ""
            lines.append(f"  {mark} {task.key}: {task.label}{suffix}")
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
        if cp.blocker:
            lines.append(f"BLOCKER: {cp.blocker.get('type')}: {cp.blocker.get('description')}")

    if snapshot.recent_actions:
        lines.append(f"RECENT_TRAJECTORY: {len(snapshot.recent_actions)} entries")
        for entry in snapshot.recent_actions[-3:]:
            lines.append(
                "  "
                f"{entry.get('ts')} {entry.get('action')} {entry.get('target')} "
                f"result={entry.get('result')}"
            )

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
    parser.add_argument("--task-summary", default="", help="Completed task summary for checkpoint history")
    parser.add_argument("--log-action", help="Append a trajectory action")
    parser.add_argument("--log-target", default="", help="Trajectory target path or object")
    parser.add_argument("--log-detail", default="", help="Trajectory detail")
    parser.add_argument("--log-result", default="ok", help="Trajectory result")
    parser.add_argument("--show-trajectory", type=int, metavar="N", help="Show recent trajectory entries")
    parser.add_argument("--detect-drift", action="store_true", help="Detect drift against checkpoint file hashes")
    parser.add_argument("--report-blocker", metavar="TYPE: DESCRIPTION", help="Persist a structured blocker")
    parser.add_argument("--clear-blocker", action="store_true", help="Clear the persisted blocker")
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

    if args.show_trajectory is not None:
        records = read_trajectory(root, args.show_trajectory)
        for record in records:
            print(json.dumps(record, ensure_ascii=False, sort_keys=True))
        if not records:
            print("TRAJECTORY_EMPTY")
        return 0

    if args.detect_drift:
        checkpoint = read_checkpoint(root)
        for line in detect_drift(root, checkpoint):
            print(line)
        return 0

    if args.log_action:
        snapshot = build_snapshot(root, change_id=args.change_id)
        path = append_trajectory(
            root,
            change_id=snapshot.active_change_id,
            task=snapshot.current_task,
            action=args.log_action,
            target=args.log_target,
            detail=args.log_detail,
            result=args.log_result,
        )
        print(f"TRAJECTORY_LOGGED: {path}")
        return 0

    if args.report_blocker or args.clear_blocker:
        snapshot = build_snapshot(root, change_id=args.change_id)
        existing = read_checkpoint(root)
        change_id = args.change_id or (existing.change_id if existing else None) or snapshot.active_change_id
        if not change_id:
            print("ERROR: no active change for blocker", file=sys.stderr)
            return 1
        blocker = None if args.clear_blocker else parse_blocker(args.report_blocker)
        checkpoint = AutopilotCheckpoint(
            change_id=change_id,
            current_task=snapshot.current_task,
            completed_tasks=existing.completed_tasks if existing else (),
            last_action="clear-blocker" if args.clear_blocker else "report-blocker",
            context_summary=existing.context_summary if existing else "",
            updated_at=datetime.now().strftime("%Y-%m-%d %H:%M"),
            repo_state_hash=compute_repo_state_hash(root, change_id),
            completed_task_summaries=existing.completed_task_summaries if existing else {},
            blocker=blocker,
        )
        write_checkpoint(root, checkpoint)
        print("BLOCKER_CLEARED" if args.clear_blocker else f"BLOCKER_REPORTED: {blocker['type']}")
        return 0

    if args.update_checkpoint:
        snapshot = build_snapshot(root, change_id=args.change_id)
        existing = read_checkpoint(root)
        change_id = args.change_id or (existing.change_id if existing else None) or snapshot.active_change_id
        if not change_id:
            print("ERROR: no active change to checkpoint", file=sys.stderr)
            return 1
        completed_tasks = list(existing.completed_tasks if existing else ())
        task_match = re.search(r"\b(T\d+)\b", args.update_checkpoint)
        task_key = task_match.group(1) if task_match else snapshot.current_task
        if args.task_summary and task_key and task_key not in completed_tasks:
            completed_tasks.append(task_key)
        summaries = dict(existing.completed_task_summaries if existing else {})
        if args.task_summary and task_key:
            summaries[task_key] = args.task_summary

        new_checkpoint = AutopilotCheckpoint(
            change_id=change_id,
            current_task=snapshot.current_task,
            completed_tasks=tuple(completed_tasks),
            last_action=args.update_checkpoint,
            context_summary=args.checkpoint_context,
            updated_at=datetime.now().strftime("%Y-%m-%d %H:%M"),
            repo_state_hash=compute_repo_state_hash(root, change_id),
            completed_task_summaries=summaries,
            blocker=existing.blocker if existing else None,
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
