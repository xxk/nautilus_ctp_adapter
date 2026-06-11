"""check_harness: 检查 AGENTS.md 入口地图与治理闭环最小结构。

输出 HARNESS_CHECK_OK 或 HARNESS_CHECK_FAIL，exit 0/1。
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

try:
    from check_adr_docs import validate_adr_docs
except ModuleNotFoundError:
    from scripts.check_adr_docs import validate_adr_docs

REPO_ROOT = Path(__file__).resolve().parents[1]

AGENTS_MD = "AGENTS.md"

REQUIRED_SECTIONS = (
    "Read First",
    "Directory Map",
    "Verification",
)

REQUIRED_VERIFY_COMMANDS = (
    "python scripts/check_harness.py",
    "python scripts/check_adr_docs.py",
    "python scripts/check_change_docs.py",
    "python scripts/check_proposal_docs.py --root .",
    "python scripts/show_current_frontier.py",
)

DOC_HARNESS_README = "docs/doc_harness_kit/README.md"
DOC_HARNESS_TOPIC_CHECKLIST = "docs/doc_harness_kit/checks/topic-transition-checklist.md"


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


def _check_adr_dir(root: Path) -> list[str]:
    findings: list[str] = []
    adr_dir = root / "docs" / "adr"
    if not adr_dir.exists():
        findings.append("docs/adr/ directory does not exist")
        return findings

    for required_file in ("README.md", "ADR模板_ADR Template.md"):
        if not (adr_dir / required_file).exists():
            findings.append(f"docs/adr/{required_file} does not exist")

    return findings


def _check_proposals_dir(root: Path) -> list[str]:
    findings: list[str] = []
    proposals_dir = root / "docs" / "proposals"
    if not proposals_dir.exists():
        findings.append("docs/proposals/ directory does not exist")
        return findings

    if not (proposals_dir / "README.md").exists():
        findings.append("docs/proposals/README.md does not exist")

    template_dir = proposals_dir / "_template"
    if not template_dir.exists():
        findings.append("docs/proposals/_template/ directory does not exist")
        return findings

    for required_file in (
        "base/README.md",
        "base/phase-plan.md",
        "base/acceptance.md",
        "fragments/change-map.md",
        "fragments/decision-log.md",
        "fragments/design.md",
        "fragments/review-lane.md",
        "meta/USAGE.md",
        "meta/fragment_registry.yaml",
        "profiles/multi_phase.yaml",
    ):
        if not (template_dir / required_file).exists():
            findings.append(f"docs/proposals/_template/{required_file} does not exist")

    return findings


def _check_workflows_dir(root: Path) -> list[str]:
    findings: list[str] = []
    workflows_dir = root / "docs" / "workflows"
    if not workflows_dir.exists():
        findings.append("docs/workflows/ directory does not exist")
        return findings

    for required_file in (
        "README.md",
        "work-item-type-system.md",
        "fragments/adr-template-contract.md",
        "gates/adr-template-contract-gate.md",
    ):
        if not (workflows_dir / required_file).exists():
            findings.append(f"docs/workflows/{required_file} does not exist")

    for manifest_path in workflows_dir.rglob("tracer-manifest.md"):
        findings.append(
            f"{manifest_path.relative_to(root).as_posix()} must not be a concrete tracer manifest; "
            "docs/workflows/ only owns templates and gate specs"
        )

    return findings


def _check_doc_harness_entry(root: Path) -> list[str]:
    findings: list[str] = []
    readme_path = root / DOC_HARNESS_README
    checklist_path = root / DOC_HARNESS_TOPIC_CHECKLIST

    if not readme_path.exists():
        findings.append(f"{DOC_HARNESS_README} does not exist")
        return findings

    text = readme_path.read_text(encoding="utf-8")
    if "D:\\Nautilus\\docs\\doc_harness_kit" not in text:
        findings.append(
            f"{DOC_HARNESS_README} must point to the upstream doc harness kit baseline"
        )
    if "nautilus_strategies" not in text:
        findings.append(
            f"{DOC_HARNESS_README} must describe nautilus_strategies as the advanced governance baseline"
        )

    if not checklist_path.exists():
        findings.append(f"{DOC_HARNESS_TOPIC_CHECKLIST} does not exist")

    return findings


def check_harness(root: Path) -> list[str]:
    findings: list[str] = []
    findings.extend(_check_agents_md(root))
    findings.extend(_check_changes_dir(root))
    findings.extend(_check_adr_dir(root))
    findings.extend(_check_proposals_dir(root))
    findings.extend(_check_workflows_dir(root))
    findings.extend(_check_doc_harness_entry(root))
    findings.extend(validate_adr_docs(root))
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
