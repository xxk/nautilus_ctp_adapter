from __future__ import annotations

import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _tracked(*patterns: str) -> list[str]:
    result = subprocess.run(
        ["git", "ls-files", *patterns],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )
    return [line for line in result.stdout.splitlines() if line.strip()]


def test_adr0010_wi2_generated_runtime_outputs_are_not_tracked() -> None:
    assert _tracked("output/debug/**", "var/**", "pytest_tmp/**") == []


def test_adr0010_wi2_output_artifacts_are_not_tracked() -> None:
    assert _tracked("output/**") == []


def test_adr0010_wi2_root_ctp_flow_files_are_not_tracked() -> None:
    assert _tracked("*.con") == []


def test_adr0010_wi2_generated_runtime_outputs_are_ignored() -> None:
    result = subprocess.run(
        [
            "git",
            "check-ignore",
            "output/debug/future-runtime.log",
            "var/future-runtime.bin",
            "pytest_tmp/future-runtime.json",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    assert result.returncode == 0


def test_adr0010_active_governance_docs_use_canonical_dslresearch_spelling() -> None:
    active_docs = [
        ROOT / "AGENTS.md",
        ROOT / "docs" / "topics" / "repo-governance-hardening.md",
    ]

    offenders = [
        str(path.relative_to(ROOT))
        for path in active_docs
        if "DSLReserach" in path.read_text(encoding="utf-8")
    ]

    assert offenders == []
