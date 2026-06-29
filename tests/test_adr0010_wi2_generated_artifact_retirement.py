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
