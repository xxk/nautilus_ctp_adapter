from __future__ import annotations

import argparse
import json
import os
import re
from dataclasses import dataclass
from pathlib import Path


TOPIC_INDEX_RELATIVE_PATH = Path("docs") / "topics" / "README.md"
TOPIC_STATE_REGISTRY_RELATIVE_PATH = (
    Path("docs") / "topics" / "主题状态注册表_Topic State Registry.yaml"
)
DOCS_INDEX_RELATIVE_PATH = Path("docs") / "README.md"
CHANGES_INDEX_RELATIVE_PATH = Path("docs") / "changes" / "README.md"

VALID_CANONICAL_TOPIC_STATUSES = {
    "in_progress",
    "planned",
    "blocked",
    "frozen",
    "completed",
}
OPEN_CANONICAL_TOPIC_STATUSES = {"in_progress", "planned"}
CHANGE_ID_PATTERN = re.compile(r"\d{8}__[A-Za-z0-9\-_]+__[A-Za-z0-9\-_]+")
CHANGE_STATUS_BUCKETS = {
    "completed": ("已完成", "✅", "completed"),
    "in_progress": ("进行中", "🔄", "in_progress"),
    "not_started": ("未开始", "⬜", "待执行", "已建包", "📝", "not_started", "draft", "planned"),
    "blocked": ("阻塞", "blocked"),
}
TOPIC_STATUS_BUCKETS = {
    "completed": ("已完成", "completed"),
    "in_progress": ("进行中", "in_progress"),
    "planned": ("规划中", "未开始", "planned"),
    "blocked": ("阻塞", "blocked"),
    "frozen": ("已冻结", "冻结", "frozen"),
}


class TopicGovernanceError(ValueError):
    """Raised when topic governance state is inconsistent."""


@dataclass(frozen=True)
class ChangeQueueEntry:
    order_label: str
    change_id: str
    status_label: str
    status_bucket: str


@dataclass(frozen=True)
class TopicRoadmapDoc:
    topic_id: str
    domain: str
    display_status: str
    title: str
    roadmap_path: Path
    created_date: str
    last_updated: str
    change_queue: tuple[ChangeQueueEntry, ...]


@dataclass(frozen=True)
class TopicStateRecord:
    topic_id: str
    canonical_status: str
    execution_order: int | None


@dataclass(frozen=True)
class TopicIndexEntry:
    topic_id: str
    domain: str
    display_status: str
    title: str
    roadmap_path: Path
    created_date: str
    last_updated: str
    canonical_status: str
    execution_order: int | None
    next_change_id: str | None
    next_change_status: str | None

    @property
    def is_current_active(self) -> bool:
        return self.canonical_status == "in_progress" and self.execution_order == 1


@dataclass(frozen=True)
class ChangeFrontierEntry:
    change_id: str
    status: str
    status_bucket: str
    title: str
    plan_path: Path
    topic_id: str | None
    execution_order: int | None


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _relative_path(origin: Path, target: Path) -> str:
    return Path(os.path.relpath(target, start=origin.parent)).as_posix()


def _render_link(origin: Path, label: str, target: Path) -> str:
    return f"[{label}]({_relative_path(origin, target)})"


def _extract_heading_title(text: str, fallback: str) -> str:
    for line in text.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return fallback


def _extract_metadata_value(text: str, key: str, path: Path) -> str:
    match = re.search(rf"^\*\*{re.escape(key)}\*\*：\s*(.+)$", text, flags=re.MULTILINE)
    if match is None:
        raise TopicGovernanceError(f"缺少字段 **{key}**：{path}")
    return match.group(1).strip()


def _extract_optional_metadata_value(text: str, key: str) -> str | None:
    match = re.search(rf"^\*\*{re.escape(key)}\*\*[:：]\s*(.+)$", text, flags=re.MULTILINE)
    return None if match is None else match.group(1).strip()


def _normalize_bucket(value: str, mapping: dict[str, tuple[str, ...]]) -> str | None:
    for bucket, markers in mapping.items():
        if any(marker in value for marker in markers):
            return bucket
    return None


def _normalize_topic_status(status: str, path: Path) -> str:
    bucket = _normalize_bucket(status, TOPIC_STATUS_BUCKETS)
    if bucket is None:
        raise TopicGovernanceError(f"无法识别 topic 状态：{path}: {status}")
    return bucket


def _normalize_change_status(status: str, path: Path) -> str:
    bucket = _normalize_bucket(status, CHANGE_STATUS_BUCKETS)
    if bucket is None:
        raise TopicGovernanceError(f"无法识别 change 状态：{path}: {status}")
    return bucket


def _extract_change_title(text: str, fallback: str) -> str:
    for line in text.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return fallback


def _parse_change_plan(plan_path: Path) -> ChangeFrontierEntry:
    text = _read_text(plan_path)
    status = (
        _extract_optional_metadata_value(text, "状态")
        or _extract_optional_metadata_value(text, "Status")
        or ""
    )
    if not status:
        raise TopicGovernanceError(f"change plan 缺少状态字段：{plan_path}")
    execution_order_raw = _extract_optional_metadata_value(text, "execution_order") or ""
    execution_order = int(execution_order_raw) if execution_order_raw.isdigit() else None
    topic_id = _extract_optional_metadata_value(text, "topic-id")
    return ChangeFrontierEntry(
        change_id=plan_path.parent.name,
        status=status,
        status_bucket=_normalize_change_status(status, plan_path),
        title=_extract_change_title(text, plan_path.parent.name),
        plan_path=plan_path,
        topic_id=None if topic_id is None else topic_id.strip().strip("`"),
        execution_order=execution_order,
    )


def collect_change_frontier_entries(root: Path) -> list[ChangeFrontierEntry]:
    changes_dir = root / "docs" / "changes"
    if not changes_dir.exists():
        raise TopicGovernanceError(f"缺少 changes 目录：{changes_dir}")
    entries: list[ChangeFrontierEntry] = []
    for plan_path in sorted(changes_dir.glob("*/plan.md")):
        if plan_path.parent.name.startswith("_"):
            continue
        entries.append(_parse_change_plan(plan_path))
    if not entries:
        raise TopicGovernanceError(f"未发现任何 change plan：{changes_dir}")
    return entries


def _change_sort_key(entry: ChangeFrontierEntry) -> tuple[int, str]:
    return (entry.execution_order if entry.execution_order is not None else 10**6, entry.change_id)


def _parse_change_queue(text: str, path: Path) -> tuple[ChangeQueueEntry, ...]:
    rows: list[ChangeQueueEntry] = []
    in_table = False
    change_index: int | None = None
    status_index: int | None = None
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line.startswith("|"):
            if in_table and rows:
                break
            continue

        cells = [cell.strip() for cell in raw_line.strip().strip("|").split("|")]
        if len(cells) < 4:
            continue
        header_text = " ".join(cells)
        if "顺序" in header_text and ("change-id" in header_text or "Change" in header_text):
            in_table = True
            change_index = next(
                (index for index, cell in enumerate(cells) if "change-id" in cell or cell == "Change"),
                None,
            )
            status_index = next((index for index, cell in enumerate(cells) if "状态" in cell), None)
            if change_index is None or status_index is None:
                raise TopicGovernanceError(f"Child Change 表头缺少 change/status 列：{path}")
            continue
        if not in_table:
            continue
        if set("".join(cells)) <= {":", "-", " "}:
            continue

        if change_index is None or status_index is None:
            raise TopicGovernanceError(f"Child Change 表头解析失败：{path}")

        change_id = next(
            (
                match.group(0)
                for cell in [cells[change_index]]
                if (match := CHANGE_ID_PATTERN.search(cell)) is not None
            ),
            None,
        )
        if change_id is None:
            continue
        status_label = cells[status_index]
        rows.append(
            ChangeQueueEntry(
                order_label=cells[0],
                change_id=change_id,
                status_label=status_label,
                status_bucket=_normalize_change_status(status_label, path),
            )
        )
    return tuple(rows)


def discover_topic_roadmaps(root: Path) -> list[TopicRoadmapDoc]:
    topics_dir = root / "docs" / "topics"
    if not topics_dir.exists():
        raise TopicGovernanceError(f"缺少 topics 目录：{topics_dir}")

    roadmaps: list[TopicRoadmapDoc] = []
    seen_topic_ids: set[str] = set()
    for path in sorted(topics_dir.glob("*.md")):
        if path.name == "README.md":
            continue
        text = _read_text(path)
        topic_id = _extract_metadata_value(text, "topic-id", path).strip("`")
        if topic_id in seen_topic_ids:
            raise TopicGovernanceError(f"topic-id 重复：{topic_id}: {path}")
        seen_topic_ids.add(topic_id)
        roadmaps.append(
            TopicRoadmapDoc(
                topic_id=topic_id,
                domain=_extract_metadata_value(text, "domain", path),
                display_status=_extract_metadata_value(text, "状态", path),
                title=_extract_heading_title(text, path.stem),
                roadmap_path=path,
                created_date=_extract_metadata_value(text, "创建日期", path),
                last_updated=_extract_metadata_value(text, "最后更新", path),
                change_queue=_parse_change_queue(text, path),
            )
        )

    if not roadmaps:
        raise TopicGovernanceError(f"未发现任何 topic 文件：{topics_dir}")
    return roadmaps


def load_topic_state_registry(root: Path) -> tuple[str | None, dict[str, TopicStateRecord]]:
    path = root / TOPIC_STATE_REGISTRY_RELATIVE_PATH
    if not path.exists():
        raise TopicGovernanceError(f"缺少 topic 状态注册表：{path}")

    last_updated: str | None = None
    topics: dict[str, TopicStateRecord] = {}
    current_topic_id: str | None = None
    current_status: str | None = None
    current_order: int | None = None
    in_topics = False

    for raw_line in _read_text(path).splitlines():
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue
        if raw_line.startswith("topics:"):
            in_topics = True
            continue
        if not in_topics:
            if raw_line.startswith("last_updated:"):
                last_updated = raw_line.split(":", 1)[1].strip().strip("'\"")
            continue

        topic_match = re.match(r"^  ([A-Za-z0-9\-_]+):\s*$", raw_line)
        if topic_match is not None:
            if current_topic_id is not None:
                if current_status is None:
                    raise TopicGovernanceError(f"topic 状态注册表缺少 canonical_status：{path}: {current_topic_id}")
                topics[current_topic_id] = TopicStateRecord(
                    topic_id=current_topic_id,
                    canonical_status=current_status,
                    execution_order=current_order,
                )
            current_topic_id = topic_match.group(1)
            current_status = None
            current_order = None
            continue

        if current_topic_id is None:
            raise TopicGovernanceError(f"topic 状态注册表结构非法：{path}: {raw_line}")

        status_match = re.match(r"^    canonical_status:\s*([A-Za-z_]+)\s*$", raw_line)
        if status_match is not None:
            current_status = status_match.group(1)
            if current_status not in VALID_CANONICAL_TOPIC_STATUSES:
                raise TopicGovernanceError(
                    f"topic 状态注册表 canonical_status 非法：{path}: {current_topic_id} -> {current_status}"
                )
            continue

        order_match = re.match(r"^    execution_order:\s*(.+)\s*$", raw_line)
        if order_match is not None:
            raw_value = order_match.group(1).strip()
            if raw_value in {"null", "None", ""}:
                current_order = None
            else:
                try:
                    current_order = int(raw_value)
                except ValueError as exc:
                    raise TopicGovernanceError(
                        f"topic 状态注册表 execution_order 非法：{path}: {current_topic_id} -> {raw_value}"
                    ) from exc
            continue

        raise TopicGovernanceError(f"topic 状态注册表存在无法解析的行：{path}: {raw_line}")

    if current_topic_id is not None:
        if current_status is None:
            raise TopicGovernanceError(f"topic 状态注册表缺少 canonical_status：{path}: {current_topic_id}")
        topics[current_topic_id] = TopicStateRecord(
            topic_id=current_topic_id,
            canonical_status=current_status,
            execution_order=current_order,
        )

    if not topics:
        raise TopicGovernanceError(f"topic 状态注册表没有 topics：{path}")
    return last_updated, topics


def _pick_next_change(change_queue: tuple[ChangeQueueEntry, ...]) -> tuple[str | None, str | None]:
    for entry in change_queue:
        if entry.status_bucket == "in_progress":
            return entry.change_id, entry.status_bucket
    for entry in change_queue:
        if entry.status_bucket == "not_started":
            return entry.change_id, entry.status_bucket
    return None, None


def _topic_sort_key(entry: TopicIndexEntry) -> tuple[int, int, str, str]:
    domain_order = {
        "repo_governance": 0,
        "nautilus_adapter": 1,
        "rust_ctp": 2,
    }
    status_order = {
        "in_progress": 0,
        "planned": 0,
        "blocked": 1,
        "frozen": 2,
        "completed": 3,
    }
    return (
        domain_order.get(entry.domain, 99),
        status_order.get(entry.canonical_status, 99),
        entry.execution_order if entry.execution_order is not None else 10**6,
        entry.topic_id,
    )


def collect_topic_index_entries(root: Path) -> tuple[str | None, list[TopicIndexEntry]]:
    registry_last_updated, registry = load_topic_state_registry(root)
    roadmaps = discover_topic_roadmaps(root)
    roadmap_topic_ids = {roadmap.topic_id for roadmap in roadmaps}
    registry_topic_ids = set(registry)

    missing_topic_ids = sorted(roadmap_topic_ids - registry_topic_ids)
    extra_topic_ids = sorted(registry_topic_ids - roadmap_topic_ids)
    if missing_topic_ids:
        raise TopicGovernanceError(
            "topic 状态注册表缺少 topic-id："
            f"{', '.join(missing_topic_ids)}"
        )
    if extra_topic_ids:
        raise TopicGovernanceError(
            "topic 状态注册表存在多余 topic-id："
            f"{', '.join(extra_topic_ids)}"
        )

    open_orders: list[int] = []
    active_topics: list[str] = []
    entries: list[TopicIndexEntry] = []
    for roadmap in roadmaps:
        record = registry[roadmap.topic_id]
        display_bucket = _normalize_topic_status(roadmap.display_status, roadmap.roadmap_path)
        if display_bucket != record.canonical_status:
            raise TopicGovernanceError(
                "topic README 状态与 registry 不一致："
                f"{roadmap.roadmap_path}: display={display_bucket} registry={record.canonical_status}"
            )
        if record.canonical_status in OPEN_CANONICAL_TOPIC_STATUSES:
            if record.execution_order is None or record.execution_order <= 0:
                raise TopicGovernanceError(
                    f"open topic 缺少合法 execution_order：{roadmap.topic_id}"
                )
            open_orders.append(record.execution_order)
        elif record.execution_order is not None:
            raise TopicGovernanceError(
                f"非 open topic 不得声明 execution_order：{roadmap.topic_id}"
            )
        if record.canonical_status == "in_progress":
            active_topics.append(roadmap.topic_id)

        next_change_id, next_change_status = _pick_next_change(roadmap.change_queue)
        if record.canonical_status in OPEN_CANONICAL_TOPIC_STATUSES and not roadmap.change_queue:
            raise TopicGovernanceError(
                f"open topic 缺少 child change 队列表：{roadmap.roadmap_path}"
            )
        if record.canonical_status == "in_progress" and next_change_id is None:
            raise TopicGovernanceError(
                f"active topic 缺少可推进的 change：{roadmap.roadmap_path}"
            )

        entries.append(
            TopicIndexEntry(
                topic_id=roadmap.topic_id,
                domain=roadmap.domain,
                display_status=roadmap.display_status,
                title=roadmap.title,
                roadmap_path=roadmap.roadmap_path,
                created_date=roadmap.created_date,
                last_updated=roadmap.last_updated,
                canonical_status=record.canonical_status,
                execution_order=record.execution_order,
                next_change_id=next_change_id,
                next_change_status=next_change_status,
            )
        )

    if len(active_topics) > 1:
        raise TopicGovernanceError(f"同一时刻只允许一个 in_progress topic：{', '.join(active_topics)}")
    if active_topics:
        active_entry = next(entry for entry in entries if entry.topic_id == active_topics[0])
        if active_entry.execution_order != 1:
            raise TopicGovernanceError(
                f"active topic 必须位于 execution_order=1：{active_entry.topic_id}"
            )

    expected_open_orders = list(range(1, len(open_orders) + 1))
    actual_open_orders = sorted(open_orders)
    if actual_open_orders != expected_open_orders:
        raise TopicGovernanceError(
            "open topic 的 execution_order 必须连续从 1 开始："
            f"当前={actual_open_orders} 期望={expected_open_orders}"
        )

    return registry_last_updated, sorted(entries, key=_topic_sort_key)


def collect_current_frontier(root: Path) -> dict[str, object]:
    """Return the executable frontier from child change plan metadata.

    Route B keeps `topic-id` as a label on change plans. Topic roadmaps and the
    legacy registry are still available through `--by-topic`, but they must not
    select or advance the default executable frontier.
    """
    entries = collect_change_frontier_entries(root)
    active_entries = [entry for entry in entries if entry.status_bucket == "in_progress"]
    if len(active_entries) > 1:
        raise TopicGovernanceError(
            "同一时刻只允许一个 in_progress child change："
            f"{', '.join(entry.change_id for entry in active_entries)}"
        )
    active_entry = active_entries[0] if active_entries else None
    queued_entries = sorted(
        [entry for entry in entries if entry.status_bucket == "not_started"],
        key=_change_sort_key,
    )
    parked_entries = sorted(
        [entry for entry in entries if entry.status_bucket == "blocked"],
        key=lambda entry: entry.change_id,
    )
    recent_completed_entries = sorted(
        [entry for entry in entries if entry.status_bucket == "completed"],
        key=lambda entry: entry.change_id,
        reverse=True,
    )[:5]

    def serialize_change(entry: ChangeFrontierEntry) -> dict[str, object]:
        payload: dict[str, object] = {
            "change_id": entry.change_id,
            "status": entry.status_bucket,
            "status_label": entry.status,
            "title": entry.title,
            "plan_path": entry.plan_path.relative_to(root).as_posix(),
            "topic_id": entry.topic_id,
            "execution_order": entry.execution_order,
        }
        return payload

    return {
        "status": "ok",
        "frontier_source": "docs/changes/*/plan.md",
        "topic_index_path": TOPIC_INDEX_RELATIVE_PATH.as_posix(),
        "active_topic": None,
        "active_change": None if active_entry is None else serialize_change(active_entry),
        "queued_topics": [],
        "queued_changes": [serialize_change(entry) for entry in queued_entries],
        "parked_topics": [],
        "parked_changes": [serialize_change(entry) for entry in parked_entries],
        "recent_completed_topics": [],
        "recent_completed_changes": [serialize_change(entry) for entry in recent_completed_entries],
        "counts": {
            "change_count": len(entries),
            "active_change_count": len(active_entries),
            "queued_change_count": len(queued_entries),
            "parked_change_count": len(parked_entries),
            "completed_change_count": sum(1 for entry in entries if entry.status_bucket == "completed"),
            "topic_count": 0,
            "open_topic_count": 0,
            "parked_topic_count": 0,
            "completed_topic_count": 0,
        },
    }


def collect_current_frontier_by_topic(root: Path) -> dict[str, object]:
    registry_last_updated, entries = collect_topic_index_entries(root)
    grouped: dict[str, list[dict[str, object]]] = {}
    for entry in sorted(
        entries,
        key=lambda item: (
            item.domain,
            item.execution_order is None,
            item.execution_order if item.execution_order is not None else 10**6,
            item.topic_id,
        ),
    ):
        payload = {
            "topic_id": entry.topic_id,
            "domain": entry.domain,
            "canonical_status": entry.canonical_status,
            "display_status": entry.display_status,
            "title": entry.title,
            "roadmap_path": entry.roadmap_path.relative_to(root).as_posix(),
            "execution_order": entry.execution_order,
            "next_change_id": entry.next_change_id,
            "next_change_status": entry.next_change_status,
            "last_updated": entry.last_updated,
            "is_current_active": entry.is_current_active,
        }
        grouped.setdefault(entry.domain, []).append(payload)

    return {
        "status": "ok",
        "registry_last_updated": registry_last_updated,
        "registry_path": TOPIC_STATE_REGISTRY_RELATIVE_PATH.as_posix(),
        "topic_index_path": TOPIC_INDEX_RELATIVE_PATH.as_posix(),
        "topics_by_domain": grouped,
        "counts": {
            "domain_count": len(grouped),
            "topic_count": len(entries),
            "open_topic_count": sum(
                1 for entry in entries if entry.canonical_status in OPEN_CANONICAL_TOPIC_STATUSES
            ),
            "blocked_or_frozen_count": sum(
                1 for entry in entries if entry.canonical_status in {"blocked", "frozen"}
            ),
            "completed_topic_count": sum(
                1 for entry in entries if entry.canonical_status == "completed"
            ),
        },
    }


def _render_topic_reference(origin: Path, entry: TopicIndexEntry) -> str:
    label = entry.topic_id
    if entry.execution_order is not None:
        label = f"{entry.topic_id} (#{entry.execution_order})"
    return _render_link(origin, label, entry.roadmap_path)


def _render_change_reference(origin: Path, change_id: str) -> str:
    change_plan_path = origin.parents[1] / "changes" / change_id / "plan.md"
    return _render_link(origin, change_id, change_plan_path)


def render_topic_index(root: Path) -> str:
    registry_last_updated, entries = collect_topic_index_entries(root)
    topic_index_path = root / TOPIC_INDEX_RELATIVE_PATH
    active_entry = next((entry for entry in entries if entry.is_current_active), None)
    queued_entries = [
        entry
        for entry in entries
        if entry.canonical_status in OPEN_CANONICAL_TOPIC_STATUSES and not entry.is_current_active
    ]
    parked_entries = [entry for entry in entries if entry.canonical_status in {"blocked", "frozen"}]
    completed_entries = [entry for entry in entries if entry.canonical_status == "completed"]
    recent_completed_entries = sorted(
        completed_entries,
        key=lambda entry: (entry.last_updated, entry.topic_id),
        reverse=True,
    )[:5]

    active_topic_line = (
        _render_topic_reference(topic_index_path, active_entry) if active_entry is not None else "`无`"
    )
    active_change_line = (
        _render_change_reference(topic_index_path, active_entry.next_change_id)
        if active_entry is not None and active_entry.next_change_id is not None
        else "`无`"
    )
    queued_topic_line = (
        "、".join(_render_topic_reference(topic_index_path, entry) for entry in queued_entries)
        if queued_entries
        else "`无`"
    )
    queued_change_line = (
        "、".join(
            _render_change_reference(topic_index_path, entry.next_change_id)
            for entry in queued_entries
            if entry.next_change_id is not None
        )
        if any(entry.next_change_id is not None for entry in queued_entries)
        else "`无`"
    )
    parked_topic_line = (
        "、".join(
            f"{_render_link(topic_index_path, entry.topic_id, entry.roadmap_path)}（{entry.canonical_status}）"
            for entry in parked_entries
        )
        if parked_entries
        else "`无`"
    )
    recent_completed_line = (
        "、".join(
            f"{_render_link(topic_index_path, entry.topic_id, entry.roadmap_path)}（last_updated={entry.last_updated}）"
            for entry in recent_completed_entries
        )
        if recent_completed_entries
        else "`无`"
    )

    by_domain: dict[str, list[TopicIndexEntry]] = {}
    for entry in entries:
        by_domain.setdefault(entry.domain, []).append(entry)

    lines = [
        "# Topic Index",
        "",
        "> 本文件由 `python scripts/sync_topic_index.py --root .` 基于 legacy roadmap 元数据与 topic 状态注册表生成。",
        "> Route B 口径：topic 只做标签与分组投影；默认可执行 frontier 以 `docs/changes/*/plan.md` 为准。",
        "",
        f"**最后同步**：{registry_last_updated or 'unknown'}",
        "",
        "## Legacy Topic Projection / 历史 Topic 投影",
        "",
        f"- **投影 active topic**：{active_topic_line}",
        f"- **投影 active change**：{active_change_line}",
        f"- **排队 topics**：{queued_topic_line}",
        f"- **排队 changes**：{queued_change_line}",
        f"- **冻结/阻塞 topics**：{parked_topic_line}",
        f"- **已完成 topics 数量**：`{len(completed_entries)}/{len(entries)}`",
        f"- **最近完成 topics**：{recent_completed_line}",
        "- **legacy 状态注册表**：`docs/topics/主题状态注册表_Topic State Registry.yaml`",
        "",
        "## Layering Rule / 分层规则",
        "",
        "1. `docs/changes/` 负责单次可执行 child change，也是默认 frontier 的唯一执行来源。",
        "2. `docs/proposals/` 负责 proposal phase、child change 映射与 proposal-local acceptance。",
        "3. `topic-id` 只允许作为 change `plan.md` frontmatter 标签和 `--by-topic` 分组维度。",
        "4. `docs/topics/<topic-id>.md` 与 topic registry 只保留历史 roadmap / grouped projection，不得作为 proposal 推进容器。",
        "5. child change 三件套负责执行、证据、正式验收与 AI 状态回填。",
        "",
        "## Current Topics / 当前 Topics",
        "",
    ]

    for domain in sorted(by_domain):
        lines.append(f"### `{domain}`")
        lines.append("")
        lines.append("| topic-id | canonical-status | execution-order | 显示状态 | 标题 | README |")
        lines.append("| --- | --- | --- | --- | --- | --- |")
        for entry in sorted(by_domain[domain], key=_topic_sort_key):
            order_value = "—" if entry.execution_order is None else str(entry.execution_order)
            lines.append(
                "| "
                f"`{entry.topic_id}` | `{entry.canonical_status}` | `{order_value}` | {entry.display_status} | {entry.title} | "
                f"{_render_link(topic_index_path, 'README', entry.roadmap_path)} |"
            )
        lines.append("")

    lines.extend(
        [
            "## Governance Note / 治理说明",
            "",
            "This README is a legacy human-readable topic projection for the repository.",
            "",
            "Canonical executable state belongs in child change `plan.md` metadata.",
            "",
            "Topic roadmaps under `docs/topics/<topic-id>.md` must not be used as proposal containers.",
            "",
        ]
    )
    return "\n".join(lines)


def sync_topic_index(root: Path, *, check: bool = False) -> Path:
    topic_index_path = root / TOPIC_INDEX_RELATIVE_PATH
    rendered = render_topic_index(root)
    current = _read_text(topic_index_path) if topic_index_path.exists() else None
    if check:
        if current != rendered:
            raise TopicGovernanceError(
                "docs/topics/README.md 与 registry/roadmap 不一致，请执行 `python scripts/sync_topic_index.py --root .`"
            )
        return topic_index_path

    topic_index_path.write_text(rendered, encoding="utf-8")
    return topic_index_path


def audit_topic_docs(root: Path) -> dict[str, object]:
    topic_index_path = sync_topic_index(root, check=True)
    frontier = collect_current_frontier(root)
    entries = collect_topic_index_entries(root)[1]
    failures: list[str] = []

    active_topic = frontier["active_topic"]
    active_change = frontier["active_change"]
    docs_readme = _read_text(root / DOCS_INDEX_RELATIVE_PATH)
    agents_text = _read_text(root / "AGENTS.md")
    changes_index_text = _read_text(root / CHANGES_INDEX_RELATIVE_PATH)

    route_b_snippets = (
        "topic-id is now a label in plan.md frontmatter",
        "docs/changes/*/plan.md",
        "topic 不作为 proposal 推进容器",
    )
    for snippet in route_b_snippets[:2]:
        if snippet not in agents_text:
            failures.append(f"FAIL repo-sync: AGENTS.md 缺少 Route B 口径: {snippet}")
    if route_b_snippets[2] not in docs_readme:
        failures.append("FAIL repo-sync: docs/README.md 缺少 topic/proposal 边界口径")
    if "docs/changes/*/plan.md" not in changes_index_text:
        failures.append("FAIL repo-sync: docs/changes/README.md 缺少 change-plan frontier 入口")

    if isinstance(active_topic, dict):
        expected_topic_id = str(active_topic["topic_id"])
        expected_change_id = None if not isinstance(active_change, dict) else str(active_change["change_id"])
        if expected_topic_id not in docs_readme:
            failures.append("FAIL repo-sync: docs/README.md 未反映当前 active topic")
        if expected_topic_id not in agents_text:
            failures.append("FAIL repo-sync: AGENTS.md 未指向当前 active topic")
        if expected_topic_id not in changes_index_text:
            failures.append("FAIL repo-sync: docs/changes/README.md 未提及当前 active topic")
        if expected_change_id is not None:
            if expected_change_id not in docs_readme:
                failures.append("FAIL repo-sync: docs/README.md 未反映当前 active change")
            if expected_change_id not in changes_index_text:
                failures.append("FAIL repo-sync: docs/changes/README.md 未反映当前 active change")

    if failures:
        raise TopicGovernanceError("\n".join(failures))

    return {
        "status": "ok",
        "checked_topic_count": len(entries),
        "topic_index_path": topic_index_path.relative_to(root).as_posix(),
    }


def audit_topic_governance(root: Path) -> dict[str, object]:
    topic_index_path = sync_topic_index(root, check=False)
    topic_docs_result = audit_topic_docs(root)
    frontier = collect_current_frontier(root)
    return {
        "status": "ok",
        "topic_index_path": topic_index_path.relative_to(root).as_posix(),
        "topic_docs": topic_docs_result,
        "frontier": frontier,
    }


def build_sync_topic_index_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="sync_topic_index")
    parser.add_argument("--root", default=".", help="仓库根目录，默认当前目录")
    parser.add_argument("--check", action="store_true", help="只检查，不写回 README")
    return parser


def main_sync_topic_index(argv: list[str] | None = None) -> int:
    parser = build_sync_topic_index_parser()
    args = parser.parse_args(argv)
    root = Path(args.root).resolve()
    try:
        path = sync_topic_index(root, check=args.check)
    except TopicGovernanceError as exc:
        print(f"TOPIC_INDEX_SYNC_FAILED: {exc}")
        return 1
    status = "CHECK_OK" if args.check else "SYNC_OK"
    print(f"TOPIC_INDEX_{status}: {path.relative_to(root).as_posix()}")
    return 0


def build_check_topic_docs_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="check_topic_docs")
    parser.add_argument("--root", default=".", help="仓库根目录，默认当前目录")
    return parser


def main_check_topic_docs(argv: list[str] | None = None) -> int:
    parser = build_check_topic_docs_parser()
    args = parser.parse_args(argv)
    root = Path(args.root).resolve()
    try:
        _registry_last_updated, entries = collect_topic_index_entries(root)
        for entry in entries:
            print(f"PASS {entry.topic_id}")
        result = audit_topic_docs(root)
    except TopicGovernanceError as exc:
        failures = str(exc).splitlines()
        for failure in failures:
            print(failure)
        try:
            checked_topic_count = len(collect_topic_index_entries(root)[1])
        except TopicGovernanceError:
            checked_topic_count = 0
        print(f"SUMMARY topics={checked_topic_count} failures={len(failures)}")
        return 1

    print(f"SUMMARY topics={result['checked_topic_count']} failures=0")
    return 0


def build_show_current_frontier_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="show_current_frontier")
    parser.add_argument("--root", default=".", help="仓库根目录，默认当前目录")
    parser.add_argument("--by-topic", action="store_true", help="按 domain 分组输出 topic 摘要")
    parser.add_argument("--json", action="store_true", help="输出 JSON 结果")
    return parser


def main_show_current_frontier(argv: list[str] | None = None) -> int:
    parser = build_show_current_frontier_parser()
    args = parser.parse_args(argv)
    root = Path(args.root).resolve()
    try:
        frontier = collect_current_frontier_by_topic(root) if args.by_topic else collect_current_frontier(root)
    except TopicGovernanceError as exc:
        if args.json:
            print(json.dumps({"status": "error", "message": str(exc)}, ensure_ascii=False))
        else:
            print(f"CURRENT_FRONTIER_FAILED: {exc}")
        return 1

    if args.json:
        print(json.dumps(frontier, ensure_ascii=False, indent=2))
        return 0

    if args.by_topic:
        grouped = frontier["topics_by_domain"]
        counts = frontier["counts"]
        print(
            "CURRENT_FRONTIER_BY_TOPIC_OK: "
            f"domains={counts['domain_count']} "
            f"topics={counts['topic_count']} "
            f"open={counts['open_topic_count']} "
            f"completed={counts['completed_topic_count']}"
        )
        for domain, topics in grouped.items():
            print(f"DOMAIN: {domain} topics={len(topics)}")
            for topic in topics:
                print(
                    "TOPIC: "
                    f"domain={domain} "
                    f"topic={topic['topic_id']} "
                    f"status={topic['canonical_status']} "
                    f"order={topic['execution_order'] or ''} "
                    f"active={'yes' if topic['is_current_active'] else 'no'} "
                    f"next_change={topic['next_change_id'] or ''}"
                )
        return 0

    active_change = frontier["active_change"]
    queued_changes = frontier.get("queued_changes", [])
    parked_changes = frontier.get("parked_changes", [])
    completed_count = frontier["counts"].get("completed_change_count", 0)
    print(
        "CURRENT_FRONTIER_OK: "
        f"active_change={active_change['change_id'] if isinstance(active_change, dict) else '无'} "
        f"queued_changes={len(queued_changes)} parked_changes={len(parked_changes)} "
        f"completed_changes={completed_count} "
        f"source={frontier.get('frontier_source', '')}"
    )
    if isinstance(active_change, dict):
        print(
            "ACTIVE_CHANGE: "
            f"change={active_change['change_id']} status={active_change.get('status', '')} "
            f"topic_label={active_change.get('topic_id') or ''} "
            f"order={active_change.get('execution_order') or ''} "
            f"plan={active_change.get('plan_path', '')}"
        )
    for entry in queued_changes:
        print(
            "QUEUED_CHANGE: "
            f"order={entry.get('execution_order') or ''} change={entry['change_id']} "
            f"status={entry.get('status', '')} topic_label={entry.get('topic_id') or ''}"
        )
    for entry in parked_changes:
        print(
            "PARKED_CHANGE: "
            f"change={entry['change_id']} status={entry.get('status', '')} "
            f"topic_label={entry.get('topic_id') or ''} title={entry['title']}"
        )
    return 0


def build_check_topic_governance_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="check_topic_governance")
    parser.add_argument("--root", default=".", help="仓库根目录，默认当前目录")
    parser.add_argument("--json", action="store_true", help="输出 JSON 结果")
    return parser


def main_check_topic_governance(argv: list[str] | None = None) -> int:
    parser = build_check_topic_governance_parser()
    args = parser.parse_args(argv)
    root = Path(args.root).resolve()
    try:
        result = audit_topic_governance(root)
    except TopicGovernanceError as exc:
        if args.json:
            print(json.dumps({"status": "error", "message": str(exc)}, ensure_ascii=False))
        else:
            print(f"TOPIC_GOVERNANCE_CHECK_FAILED: {exc}")
        return 1

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0

    frontier = result["frontier"]
    active_topic = frontier["active_topic"]
    active_change = frontier["active_change"]
    print(
        "TOPIC_GOVERNANCE_CHECK_OK: "
        f"index={result['topic_index_path']} "
        f"topics={result['topic_docs']['checked_topic_count']} "
        f"active_topic={active_topic['topic_id'] if isinstance(active_topic, dict) else '无'} "
        f"active_change={active_change['change_id'] if isinstance(active_change, dict) else '无'}"
    )
    return 0
