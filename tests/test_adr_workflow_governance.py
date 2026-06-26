from __future__ import annotations

from pathlib import Path

from scripts.check_adr_docs import validate_adr_docs


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_adr_docs_gate_accepts_current_index_and_adr003() -> None:
    assert validate_adr_docs(PROJECT_ROOT) == []
    assert validate_adr_docs(PROJECT_ROOT, adr_id="ADR003") == []


def test_workflows_define_specs_not_execution_state() -> None:
    workflows_root = PROJECT_ROOT / "docs" / "workflows"

    assert (workflows_root / "README.md").is_file()
    assert (workflows_root / "work-item-type-system.md").is_file()
    assert (workflows_root / "fragments" / "adr-template-contract.md").is_file()
    assert (workflows_root / "gates" / "adr-template-contract-gate.md").is_file()
    assert list(workflows_root.rglob("tracer-manifest.md")) == []


def test_proposal_template_exposes_work_item_contract_boundary() -> None:
    readme_text = (
        PROJECT_ROOT / "docs" / "proposals" / "_template" / "base" / "README.md"
    ).read_text(encoding="utf-8")
    usage_text = (
        PROJECT_ROOT / "docs" / "proposals" / "_template" / "meta" / "USAGE.md"
    ).read_text(encoding="utf-8")

    for token in (
        "Work item type",
        "Work item layer",
        "Surface mode",
        "Action mode",
        "docs/workflows/",
    ):
        assert token in readme_text

    assert "docs/workflows/work-item-type-system.md" in usage_text
    assert "proposal_type" in usage_text
    assert "change_kind" in usage_text
