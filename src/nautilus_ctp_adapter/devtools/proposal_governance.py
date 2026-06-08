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
PROFILE_ALLOWED_KEYS = {"profile_id", "description", "fragments"}

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
TEMPLATE_BASE_REQUIRED_SNIPPETS = (
    "PROPOSAL-ANTI-DRIFT-GATE:v1",
    "PROPOSAL-ADR-CARRIER-GATE:v1",
)
PHASE_PLAN_TEMPLATE_REQUIRED_SNIPPETS = (
    "## ADR Decision Coverage Mapping",
    "## Blocker Handling Discipline",
    "## Closeout Checklist",
)
ACCEPTANCE_TEMPLATE_REQUIRED_SNIPPETS = (
    "## Artifact Root Rule",
    "## Acceptance Evidence Boundary",
    "## ADR Carrier Acceptance Matrix",
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


def _strip_yaml_scalar(value: str) -> str:
    return value.strip().strip("'\"")


def _ensure_template_relative_path(path_text: str, source_path: Path) -> Path:
    relative_path = Path(path_text)
    if relative_path.is_absolute() or ".." in relative_path.parts:
        raise ProposalGovernanceError(f"模板路径必须是 _template 内相对路径: {source_path}: {path_text}")
    return relative_path


def _load_fragment_registry(template_root: Path) -> dict[str, Path]:
    registry_path = template_root / "meta" / "fragment_registry.yaml"
    text = _read_text(registry_path)
    fragment_paths: dict[str, Path] = {}
    current_fragment_id: str | None = None
    in_fragments = False

    for raw_line in text.splitlines():
        line = raw_line.rstrip()
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if line == "fragments:":
            in_fragments = True
            continue
        if not in_fragments:
            continue
        fragment_match = re.match(r"^  (?P<id>[A-Za-z0-9_]+):\s*$", line)
        if fragment_match is not None:
            current_fragment_id = fragment_match.group("id")
            continue
        path_match = re.match(r"^    path:\s*(?P<path>.+?)\s*$", line)
        if path_match is not None and current_fragment_id is not None:
            relative_path = _ensure_template_relative_path(
                _strip_yaml_scalar(path_match.group("path")),
                registry_path,
            )
            fragment_path = template_root / relative_path
            if not fragment_path.is_file():
                raise ProposalGovernanceError(
                    f"fragment registry 指向不存在文件: {registry_path}: {current_fragment_id}: {fragment_path}"
                )
            fragment_paths[current_fragment_id] = fragment_path

    if not fragment_paths:
        raise ProposalGovernanceError(f"fragment_registry.yaml 缺少 fragments path 映射: {registry_path}")
    return fragment_paths


def _load_profile_fragments(template_root: Path, profile_id: str, fragment_paths: dict[str, Path]) -> tuple[str, ...]:
    profile_path = template_root / "profiles" / f"{profile_id}.yaml"
    text = _read_text(profile_path)
    declared_keys: set[str] = set()
    fragments: list[str] = []
    in_fragments = False
    declared_profile_id: str | None = None

    for raw_line in text.splitlines():
        line = raw_line.rstrip()
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if not line.startswith(" ") and ":" in line:
            key, value = line.split(":", 1)
            key = key.strip()
            declared_keys.add(key)
            in_fragments = key == "fragments"
            if key == "profile_id":
                declared_profile_id = _strip_yaml_scalar(value)
            continue
        if in_fragments:
            fragment_match = re.match(r"^  -\s*(?P<id>[A-Za-z0-9_]+)\s*$", line)
            if fragment_match is not None:
                fragments.append(fragment_match.group("id"))

    unknown_keys = declared_keys - PROFILE_ALLOWED_KEYS
    if unknown_keys:
        raise ProposalGovernanceError(f"profile 含非声明字段: {profile_path}: {sorted(unknown_keys)}")
    if declared_profile_id is not None and declared_profile_id != profile_id:
        raise ProposalGovernanceError(f"profile_id 与文件名不一致: {profile_path}: {declared_profile_id} != {profile_id}")
    if not fragments:
        raise ProposalGovernanceError(f"profile 缺少 fragments 列表: {profile_path}")

    unknown_fragments = [fragment_id for fragment_id in fragments if fragment_id not in fragment_paths]
    if unknown_fragments:
        raise ProposalGovernanceError(f"profile 引用未知 fragment: {profile_path}: {unknown_fragments}")
    return tuple(fragments)


def _parse_fragment_list(fragments: str | None, fragment_paths: dict[str, Path]) -> tuple[str, ...]:
    if fragments is None:
        return ()
    parsed = tuple(item.strip() for item in fragments.split(",") if item.strip())
    if not parsed:
        raise ProposalGovernanceError("--fragments 不能是空列表")
    unknown_fragments = [fragment_id for fragment_id in parsed if fragment_id not in fragment_paths]
    if unknown_fragments:
        raise ProposalGovernanceError(f"--fragments 引用未知 fragment: {unknown_fragments}")
    return parsed


def _dedupe_preserve_order(values: tuple[str, ...]) -> tuple[str, ...]:
    deduped: list[str] = []
    for value in values:
        if value not in deduped:
            deduped.append(value)
    return tuple(deduped)


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


def _normalize_table_key(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip().lower())


def _extract_markdown_table_value(text: str, key: str) -> str | None:
    normalized_key = _normalize_table_key(key)
    for match in re.finditer(r"^\|\s*(?P<key>[^|]+?)\s*\|\s*(?P<value>[^|]*?)\s*\|", text, flags=re.MULTILINE):
        if _normalize_table_key(match.group("key")) == normalized_key:
            return match.group("value").strip().strip("`")
    return None


def _truthy_table_value(value: str | None) -> bool:
    if value is None:
        return False
    return value.strip().lower() in {"yes", "true", "1", "是"}


def _extract_decision_refs(value: str | None) -> set[str]:
    if not value:
        return set()
    return {f"D{match.group(1)}" for match in re.finditer(r"\bD(\d{1,2})\b", value, flags=re.IGNORECASE)}


def _validate_adr_carrier_mapping(
    proposal_dir: Path,
    *,
    readme_text: str,
    phase_plan_text: str,
    acceptance_text: str,
) -> list[str]:
    findings: list[str] = []
    if not _truthy_table_value(_extract_markdown_table_value(readme_text, "ADR carrier")):
        return findings

    primary_adr = _extract_markdown_table_value(readme_text, "Primary ADR")
    if primary_adr is None or primary_adr.lower() in {"", "not_applicable", "n/a", "none"}:
        findings.append(f"{proposal_dir / 'README.md'}: ADR carrier=yes 但缺少 Primary ADR")

    if "## ADR Decision Coverage Mapping" not in phase_plan_text:
        findings.append(f"{proposal_dir / 'phase-plan.md'}: ADR carrier proposal 缺少 ADR Decision Coverage Mapping")
    if "## ADR Carrier Acceptance Matrix" not in acceptance_text:
        findings.append(f"{proposal_dir / 'acceptance.md'}: ADR carrier proposal 缺少 ADR Carrier Acceptance Matrix")

    covered_match = re.search(r"^Covered decisions:\s*(?P<value>.+)$", phase_plan_text, flags=re.MULTILINE)
    covered_decisions = _extract_decision_refs(covered_match.group("value") if covered_match else None)
    if not covered_decisions:
        findings.append(f"{proposal_dir / 'phase-plan.md'}: ADR carrier proposal 缺少 Covered decisions")
        return findings

    acceptance_decisions = _extract_decision_refs(acceptance_text)
    missing_acceptance = sorted(covered_decisions - acceptance_decisions)
    if missing_acceptance:
        findings.append(
            f"{proposal_dir / 'acceptance.md'}: ADR Carrier Acceptance Matrix 未覆盖 Covered decisions: {missing_acceptance}"
        )
    return findings


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

    required_paths = [
        Path("base") / "README.md",
        Path("base") / "phase-plan.md",
        Path("base") / "acceptance.md",
        Path("meta") / "USAGE.md",
        Path("meta") / "fragment_registry.yaml",
        Path("profiles") / "multi_phase.yaml",
    ]
    for relative_path in required_paths:
        if not (template_root / relative_path).is_file():
            findings.append(f"缺少 proposal 模板文件: {template_root / relative_path}")

    if findings:
        return findings

    try:
        fragment_paths = _load_fragment_registry(template_root)
        for profile_path in sorted((template_root / "profiles").glob("*.yaml")):
            _load_profile_fragments(template_root, profile_path.stem, fragment_paths)
    except ProposalGovernanceError as exc:
        findings.extend(str(exc).splitlines())
        return findings

    try:
        readme_template = _read_text(template_root / "base" / "README.md")
        phase_plan_template = _read_text(template_root / "base" / "phase-plan.md")
        acceptance_template = _read_text(template_root / "base" / "acceptance.md")
    except ProposalGovernanceError as exc:
        findings.extend(str(exc).splitlines())
        return findings

    findings.extend(_require_snippets(readme_template, template_root / "base" / "README.md", TEMPLATE_BASE_REQUIRED_SNIPPETS))
    findings.extend(
        _require_snippets(
            phase_plan_template,
            template_root / "base" / "phase-plan.md",
            (*PHASE_PLAN_REQUIRED_SNIPPETS, *PHASE_PLAN_TEMPLATE_REQUIRED_SNIPPETS),
        )
    )
    findings.extend(
        _require_snippets(
            acceptance_template,
            template_root / "base" / "acceptance.md",
            (*ACCEPTANCE_REQUIRED_SNIPPETS, *ACCEPTANCE_TEMPLATE_REQUIRED_SNIPPETS),
        )
    )

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
    findings.extend(
        _validate_adr_carrier_mapping(
            proposal_dir,
            readme_text=readme_text,
            phase_plan_text=phase_plan_text,
            acceptance_text=acceptance_text,
        )
    )

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


def _resolve_fragment_ids(template_root: Path, profile: str | None, fragments: str | None) -> tuple[dict[str, Path], tuple[str, ...]]:
    fragment_paths = _load_fragment_registry(template_root)
    selected: list[str] = []
    if profile is not None:
        selected.extend(_load_profile_fragments(template_root, profile, fragment_paths))
    selected.extend(_parse_fragment_list(fragments, fragment_paths))
    return fragment_paths, _dedupe_preserve_order(tuple(selected))


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


def _run_scaffold_creation_gate(proposal_dir: Path) -> None:
    readme_path = proposal_dir / "README.md"
    phase_plan_path = proposal_dir / "phase-plan.md"
    acceptance_path = proposal_dir / "acceptance.md"
    readme_text = _read_text(readme_path)
    phase_plan_text = _read_text(phase_plan_path)
    acceptance_text = _read_text(acceptance_path)

    findings: list[str] = []
    findings.extend(_require_snippets(readme_text, readme_path, README_REQUIRED_SNIPPETS))
    findings.extend(_require_snippets(phase_plan_text, phase_plan_path, PHASE_PLAN_REQUIRED_SNIPPETS))
    findings.extend(_require_snippets(acceptance_text, acceptance_path, ACCEPTANCE_REQUIRED_SNIPPETS))
    if "PROPOSAL-SCAFFOLD:" not in readme_text:
        findings.append(f"{readme_path}: 缺少 proposal scaffold metadata marker")
    if findings:
        raise ProposalGovernanceError("\n".join(findings))


def _write_scaffold_metadata(readme_path: Path, *, profile: str | None, fragment_ids: tuple[str, ...]) -> None:
    text = _read_text(readme_path)
    if "PROPOSAL-SCAFFOLD:" in text:
        raise ProposalGovernanceError(f"README 已存在 proposal scaffold metadata: {readme_path}")
    marker = "<!-- PROPOSAL-ANTI-DRIFT-GATE:v1 -->"
    marker_index = text.find(marker)
    if marker_index < 0:
        raise ProposalGovernanceError(f"README 缺少 anti-drift marker，无法写入 scaffold metadata: {readme_path}")
    insertion_index = marker_index + len(marker)
    profile_value = profile or "manual"
    fragments_value = ",".join(fragment_ids) if fragment_ids else "none"
    metadata = f"\n<!-- PROPOSAL-SCAFFOLD: profile={profile_value}; fragments={fragments_value} -->"
    readme_path.write_text(text[:insertion_index] + metadata + text[insertion_index:], encoding="utf-8")


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

    template_root = root / TEMPLATE_DIR
    fragment_paths, fragment_ids = _resolve_fragment_ids(template_root, profile, fragments)
    proposal_dir = root / PROPOSALS_DIR / proposal_id
    if proposal_dir.exists():
        raise ProposalGovernanceError(f"proposal 目录已存在: {proposal_dir}")

    base_files = tuple((root / BASE_DIR / filename, proposal_dir / filename) for filename in REQUIRED_BASE_FILES)
    fragment_files = tuple(
        (
            fragment_paths[fragment_id],
            proposal_dir / fragment_paths[fragment_id].name,
        )
        for fragment_id in fragment_ids
    )

    if check_only:
        return proposal_dir

    proposal_dir.mkdir(parents=True, exist_ok=False)
    for source_path, target_path in (*base_files, *fragment_files):
        content = _render_template(_read_text(source_path), proposal_id)
        _write_text(target_path, content)
    _write_scaffold_metadata(proposal_dir / "README.md", profile=profile, fragment_ids=fragment_ids)
    _run_scaffold_creation_gate(proposal_dir)
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
        help="Additional fragment ids separated by commas; ids come from docs/proposals/_template/meta/fragment_registry.yaml",
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
