from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_deprecated_proposal_template_directory_is_physically_retired() -> None:
    deprecated_dir = PROJECT_ROOT / "docs" / "proposals" / "_template" / "deprecated"
    assert not deprecated_dir.exists()


def test_proposal_phase_plan_template_uses_bilingual_goal_and_next_action_columns() -> None:
    phase_plan_template = PROJECT_ROOT / "docs" / "proposals" / "_template" / "base" / "phase-plan.md"
    text = phase_plan_template.read_text(encoding="utf-8")

    assert "目标 / Goal" in text
    assert "下一动作 / Next Action" in text
    assert "| Phase | Goal |" not in text
    assert "Next Action / 下一步" not in text


def test_proposal_templates_keep_adr_carrier_landing_gate_contract() -> None:
    readme_text = (
        PROJECT_ROOT / "docs" / "proposals" / "_template" / "base" / "README.md"
    ).read_text(encoding="utf-8")
    phase_plan_text = (
        PROJECT_ROOT / "docs" / "proposals" / "_template" / "base" / "phase-plan.md"
    ).read_text(encoding="utf-8")
    acceptance_text = (
        PROJECT_ROOT / "docs" / "proposals" / "_template" / "base" / "acceptance.md"
    ).read_text(encoding="utf-8")
    usage_text = (
        PROJECT_ROOT / "docs" / "proposals" / "_template" / "meta" / "USAGE.md"
    ).read_text(encoding="utf-8")

    for token in (
        "<!-- PROPOSAL-ADR-CARRIER-GATE:v1 -->",
        "ADR carrier acceptance rows are incomplete until mapped",
        "not_started / not_applicable / verified after closeout",
    ):
        assert token in readme_text
    assert "| ADR backfill | required | docs/adr/<adr-file>.md | verified |" not in readme_text
    assert (
        "| Architecture / ownership backfill | required | docs/architecture/<architecture-file>.md | verified |"
        not in readme_text
    )

    for token in ("ADR Decision Coverage Mapping", "Covered decisions", "Primary ADR"):
        assert token in phase_plan_text

    for token in (
        "ADR Carrier Acceptance Matrix",
        "Primary ADR",
        "ADR decision item",
        "ADR successor scenario",
        "Positive path",
        "Must fail if",
        "Authority / retirement boundary",
    ):
        assert token in acceptance_text

    for token in (
        "ADR-carrier landing gate",
        "Decision Coverage IDs",
        "successor acceptance scenarios",
        "phase-plan.md",
        "acceptance.md",
    ):
        assert token in usage_text


def test_proposal_index_and_templates_keep_route_b_topic_boundary() -> None:
    proposal_index = (PROJECT_ROOT / "docs" / "proposals" / "README.md").read_text(encoding="utf-8")
    template_readme = (
        PROJECT_ROOT / "docs" / "proposals" / "_template" / "base" / "README.md"
    ).read_text(encoding="utf-8")
    template_phase_plan = (
        PROJECT_ROOT / "docs" / "proposals" / "_template" / "base" / "phase-plan.md"
    ).read_text(encoding="utf-8")

    for text in (proposal_index, template_readme, template_phase_plan):
        assert "topic 不作为 proposal 推进容器" in text or "Topic 不作为 proposal 推进容器" in text
    assert "不得由 topic queue 推进" in proposal_index
