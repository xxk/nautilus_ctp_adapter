from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
PROPOSALS_DIR = Path("docs") / "proposals"
ADR_DIR = Path("docs") / "adr"
TEMPLATE_DIR = PROPOSALS_DIR / "_template"
BASE_DIR = TEMPLATE_DIR / "base"
FRAGMENTS_DIR = TEMPLATE_DIR / "fragments"

PROPOSAL_ID_PATTERN = re.compile(r"^p\d{3}(?:-[A-Za-z0-9][A-Za-z0-9\-]*)?$")
STATUS_PATTERN = re.compile(r"^\*\*状态\*\*[:：]\s*(?P<value>[^\n]+)$", flags=re.MULTILINE)
PROPOSAL_ID_FIELD_PATTERN = re.compile(
    r"^\*\*proposal-id\*\*[:：]\s*`?(?P<value>[^`\n]+)`?\s*$",
    flags=re.MULTILINE | re.IGNORECASE,
)
AI_PHASE_STATUS_PATTERN = re.compile(
    r"<!--\s*AI-PHASE-STATUS-BEGIN\s*\n(?P<body>.*?)\nAI-PHASE-STATUS-END\s*-->",
    flags=re.DOTALL,
)
OVERALL_STATUS_PATTERN = re.compile(r"^overall_status:\s*(?P<value>[^\n#]+)$", flags=re.MULTILINE)

REQUIRED_BASE_FILES = ("README.md", "phase-plan.md", "acceptance.md")
FRAGMENT_FILE_BY_ID = {
    "change_map": "change-map.md",
    "decision_log": "decision-log.md",
    "design": "design.md",
    "review_lane": "review-lane.md",
}
PROFILE_FRAGMENT_IDS = {
    "multi_phase": ("change_map", "decision_log"),
}

README_REQUIRED_SNIPPETS = (
    "## 评审结论 / Review Verdict",
    "## 当前状态快照 / Reality Snapshot",
    "## Graduation / Closeout Matrix",
)
PHASE_PLAN_REQUIRED_SNIPPETS = (
    "## Artifact Trust Boundary",
    "## AI 跟踪状态（AI Tracking Status）",
    "## Phase 状态表（Phase Status Board）",
)
ACCEPTANCE_REQUIRED_SNIPPETS = (
    "## 场景矩阵 / Scenario Matrix",
    "## Evidence",
)


class ProposalGovernanceError(ValueError):
    pass


@dataclass(frozen=True)
class ProposalReport:
    proposal_id: str
    status: str


def _read_text(path: Path) -> str:
    if not path.is_file():
        raise ProposalGovernanceError(f"缺少文件: {path}")
    return path.read_text(encoding="utf-8")


def _write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _normalize_status(value: str) -> str:
    normalized = value.strip().strip("`").lower()
    if "已完成" in normalized:
        return "completed"
    if "推进中" in normalized or "进行中" in normalized:
        return "in_progress"
    if "待评审" in normalized:
        return "pending_review"
    return normalized


def _extract_status(text: str, path: Path) -> str:
    match = STATUS_PATTERN.search(text)
    if match is None:
        raise ProposalGovernanceError(f"缺少顶部状态字段: {path}")
    return match.group("value").strip()


def _extract_proposal_id(text: str, path: Path) -> str:
    match = PROPOSAL_ID_FIELD_PATTERN.search(text)
    if match is None:
        raise ProposalGovernanceError(f"缺少 proposal-id 字段: {path}")
    return match.group("value").strip()


def _extract_ai_phase_overall_status(text: str) -> str | None:
    match = AI_PHASE_STATUS_PATTERN.search(text)
    if match is None:
        return None
    overall_status = OVERALL_STATUS_PATTERN.search(match.group("body"))
    if overall_status is None:
        return None
    return overall_status.group("value").strip().strip("\"'")


def _require_snippets(text: str, path: Path, snippets: tuple[str, ...]) -> list[str]:
    findings: list[str] = []
    for snippet in snippets:
        if snippet not in text:
            findings.append(f"{path}: 缺少必需片段: {snippet}")
    return findings


def _validate_template(root: Path) -> list[str]:
    findings: list[str] = []
    proposals_root = root / PROPOSALS_DIR
    if not proposals_root.is_dir():
        findings.append("docs/proposals/ 目录不存在")
        return findings

    if not (proposals_root / "README.md").is_file():
        findings.append("docs/proposals/README.md 不存在")

    template_root = root / TEMPLATE_DIR
    if not template_root.is_dir():
        findings.append("docs/proposals/_template/ 目录不存在")
        return findings

    for relative_path in (
        Path("base") / "README.md",
        Path("base") / "phase-plan.md",
        Path("base") / "acceptance.md",
        Path("fragments") / "change-map.md",
        Path("fragments") / "decision-log.md",
        Path("fragments") / "design.md",
        Path("fragments") / "review-lane.md",
        Path("meta") / "USAGE.md",
        Path("meta") / "fragment_registry.yaml",
        Path("profiles") / "multi_phase.yaml",
    ):
        if not (template_root / relative_path).is_file():
            findings.append(f"缺少 proposal 模板文件: {template_root / relative_path}")

    return findings


def _discover_proposal_dirs(root: Path, proposal_id: str | None = None) -> list[Path]:
    proposals_root = root / PROPOSALS_DIR
    if proposal_id is not None:
        target = proposals_root / proposal_id
        return [target] if target.is_dir() else []
    return sorted(
        path
        for path in proposals_root.iterdir()
        if path.is_dir() and not path.name.startswith("_")
    )


def _validate_proposal_dir(proposal_dir: Path) -> ProposalReport:
    findings: list[str] = []
    files = {name: proposal_dir / name for name in REQUIRED_BASE_FILES}
    for file_path in files.values():
        if not file_path.is_file():
            findings.append(f"{proposal_dir}: 缺少必需文件 {file_path.name}")

    if findings:
        raise ProposalGovernanceError("\n".join(findings))

    readme_text = _read_text(files["README.md"])
    phase_plan_text = _read_text(files["phase-plan.md"])
    acceptance_text = _read_text(files["acceptance.md"])

    readme_proposal_id = _extract_proposal_id(readme_text, files["README.md"])
    phase_plan_proposal_id = _extract_proposal_id(phase_plan_text, files["phase-plan.md"])
    if readme_proposal_id != proposal_dir.name:
        findings.append(
            f"{files['README.md']}: proposal-id={readme_proposal_id} 与目录名 {proposal_dir.name} 不一致"
        )
    if phase_plan_proposal_id != proposal_dir.name:
        findings.append(
            f"{files['phase-plan.md']}: proposal-id={phase_plan_proposal_id} 与目录名 {proposal_dir.name} 不一致"
        )

    findings.extend(_require_snippets(readme_text, files["README.md"], README_REQUIRED_SNIPPETS))
    findings.extend(_require_snippets(phase_plan_text, files["phase-plan.md"], PHASE_PLAN_REQUIRED_SNIPPETS))
    findings.extend(_require_snippets(acceptance_text, files["acceptance.md"], ACCEPTANCE_REQUIRED_SNIPPETS))

    readme_status = _normalize_status(_extract_status(readme_text, files["README.md"]))
    phase_plan_status = _normalize_status(_extract_status(phase_plan_text, files["phase-plan.md"]))
    overall_status = _extract_ai_phase_overall_status(phase_plan_text)
    if overall_status is None:
        findings.append(f"{files['phase-plan.md']}: 缺少 AI-PHASE-STATUS overall_status")
    else:
        normalized_overall_status = _normalize_status(overall_status)
        if readme_status != normalized_overall_status:
            findings.append(
                f"{files['README.md']}: 顶部状态 {readme_status} 与 AI-PHASE-STATUS {normalized_overall_status} 不一致"
            )
        if phase_plan_status != normalized_overall_status:
            findings.append(
                f"{files['phase-plan.md']}: 顶部状态 {phase_plan_status} 与 AI-PHASE-STATUS {normalized_overall_status} 不一致"
            )

    if findings:
        raise ProposalGovernanceError("\n".join(findings))

    return ProposalReport(proposal_id=proposal_dir.name, status=overall_status or phase_plan_status)


def check_proposal_docs(root: Path, proposal_id: str | None = None) -> list[ProposalReport]:
    findings = _validate_template(root)
    if findings:
        raise ProposalGovernanceError("\n".join(findings))

    proposal_dirs = _discover_proposal_dirs(root, proposal_id=proposal_id)
    if proposal_id is not None and not proposal_dirs:
        raise ProposalGovernanceError(f"proposal 不存在: {proposal_id}")

    reports: list[ProposalReport] = []
    for proposal_dir in proposal_dirs:
        reports.append(_validate_proposal_dir(proposal_dir))
    return reports


def _parse_fragment_ids(profile: str | None, fragments: str | None) -> tuple[str, ...]:
    selected: list[str] = []
    if profile is not None:
        if profile not in PROFILE_FRAGMENT_IDS:
            raise ProposalGovernanceError(f"未知 profile: {profile}")
        selected.extend(PROFILE_FRAGMENT_IDS[profile])
    if fragments is not None:
        for fragment_id in [item.strip() for item in fragments.split(",") if item.strip()]:
            if fragment_id not in FRAGMENT_FILE_BY_ID:
                raise ProposalGovernanceError(f"未知 fragment: {fragment_id}")
            selected.append(fragment_id)

    deduped: list[str] = []
    for fragment_id in selected:
        if fragment_id not in deduped:
            deduped.append(fragment_id)
    return tuple(deduped)


def _build_proposal_title(proposal_id: str) -> str:
    if "-" not in proposal_id:
        return proposal_id.upper()
    _, slug = proposal_id.split("-", 1)
    return slug.replace("-", " ").strip().title()


def _render_template(text: str, proposal_id: str) -> str:
    today = date.today().isoformat()
    rendered = text.replace("<proposal-id>", proposal_id)
    rendered = rendered.replace("<proposal-title>", _build_proposal_title(proposal_id))
    rendered = rendered.replace("<YYYY-MM-DD>", today)
    return rendered


def scaffold_proposal(
    root: Path,
    *,
    proposal_id: str,
    profile: str | None,
    fragments: str | None,
    check_only: bool,
) -> Path:
    if not PROPOSAL_ID_PATTERN.fullmatch(proposal_id):
        raise ProposalGovernanceError(f"proposal-id 格式非法: {proposal_id}")

    template_findings = _validate_template(root)
    if template_findings:
        raise ProposalGovernanceError("\n".join(template_findings))

    fragment_ids = _parse_fragment_ids(profile, fragments)
    proposal_dir = root / PROPOSALS_DIR / proposal_id
    if proposal_dir.exists():
        raise ProposalGovernanceError(f"proposal 目录已存在: {proposal_dir}")

    base_files = tuple((root / BASE_DIR / filename, proposal_dir / filename) for filename in REQUIRED_BASE_FILES)
    fragment_files = tuple(
        (
            root / FRAGMENTS_DIR / FRAGMENT_FILE_BY_ID[fragment_id],
            proposal_dir / FRAGMENT_FILE_BY_ID[fragment_id],
        )
        for fragment_id in fragment_ids
    )

    if check_only:
        return proposal_dir

    proposal_dir.mkdir(parents=True, exist_ok=False)
    for source_path, target_path in (*base_files, *fragment_files):
        content = _render_template(_read_text(source_path), proposal_id)
        _write_text(target_path, content)
    return proposal_dir


def _build_check_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Check proposal docs, template, and proposal status alignment.")
    parser.add_argument("--root", type=Path, default=REPO_ROOT, help="Repository root")
    parser.add_argument("--proposal-id", type=str, default=None, help="Check only one proposal directory")
    return parser


def _build_new_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Create a new proposal from docs/proposals/_template.")
    parser.add_argument("--root", type=Path, default=REPO_ROOT, help="Repository root")
    parser.add_argument("--id", required=True, dest="proposal_id", help="Proposal id, for example p001-example")
    parser.add_argument("--profile", default="multi_phase", help="Template profile id")
    parser.add_argument(
        "--fragments",
        default=None,
        help="Additional fragment ids separated by commas: change_map,decision_log,design,review_lane",
    )
    parser.add_argument("--check-only", action="store_true", help="Validate the scaffold command without writing files")
    return parser


def main_check_proposal_docs() -> int:
    args = _build_check_parser().parse_args()
    root = args.root.resolve()
    try:
        reports = check_proposal_docs(root, proposal_id=args.proposal_id)
    except ProposalGovernanceError as exc:
        for line in str(exc).splitlines():
            print(f"FAIL: {line}")
        print("PROPOSAL_DOCS_CHECK_FAIL")
        return 1

    if not reports:
        print("PROPOSAL_DOCS_CHECK_OK: proposals=0")
        return 0

    print(
        "PROPOSAL_DOCS_CHECK_OK: "
        f"proposals={len(reports)} statuses={', '.join(f'{report.proposal_id}:{report.status}' for report in reports)}"
    )
    return 0


def main_new_proposal() -> int:
    args = _build_new_parser().parse_args()
    root = args.root.resolve()
    try:
        proposal_dir = scaffold_proposal(
            root,
            proposal_id=args.proposal_id,
            profile=args.profile,
            fragments=args.fragments,
            check_only=args.check_only,
        )
    except ProposalGovernanceError as exc:
        for line in str(exc).splitlines():
            print(f"FAIL: {line}")
        print("NEW_PROPOSAL_FAIL")
        return 1

    if args.check_only:
        print(f"NEW_PROPOSAL_CHECK_OK: {proposal_dir.relative_to(root).as_posix()}")
        return 0

    print(f"NEW_PROPOSAL_OK: {proposal_dir.relative_to(root).as_posix()}")
    return 0