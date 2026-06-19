from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from scripts.ctp025292_account_console_runtime_lineage_audit import (
    audit_account_console_runtime_lineage,
)


REPO_ROOT = Path(__file__).resolve().parents[1]


def _write_acceptance(path: Path, *, status: str = "passed", checksum: str | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "schema": "account-console.ctp025292-real-login-ui-acceptance-evidence.v1",
                "status": status,
                "verdict": "pass" if status == "passed" else "blocked",
                "account_id": "acct.ctp.live.025292",
                "source_ref": "output/account_capability/ctp-live-025292/source-package.json",
                "source_checksum": checksum or "sha256:" + "A" * 64,
            }
        ),
        encoding="utf-8",
    )


def _write_template(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "schema_version": "account_source_artifact.v1",
                "account_id": "acct.ctp.live.025292",
                "source_kind": "ctp_trader_api",
            }
        ),
        encoding="utf-8",
    )


def _write_account_source(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "schema_version": "account_source_artifact.v1",
                "account_id": "acct.ctp.live.025292",
                "source_kind": "ctp_trader_api",
                "source_mode": "live_observation",
                "source_health": {"state": "ready"},
            }
        ),
        encoding="utf-8",
    )


def _write_runtime_source(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "schema_version": "ctp025292.source_package.v1",
                "account_id": "acct.ctp.live.025292",
                "market_data_account_id": "025292",
                "runtime_pack": {
                    "runtime_pack_id": "ctp-live-025292-md",
                    "ref": "D:/trusted/ctp025292/runtime-pack",
                    "dlls": {
                        "thostmduserapi_se.dll": {"sha256": "A" * 64},
                        "thosttraderapi_se.dll": {"sha256": "B" * 64},
                    },
                },
            }
        ),
        encoding="utf-8",
    )


def test_missing_account_console_source_package_keeps_runtime_lineage_blocked(tmp_path: Path) -> None:
    source = tmp_path / "output" / "source-package.json"
    acceptance = tmp_path / "acceptance.json"
    template = tmp_path / "template.json"
    _write_acceptance(
        acceptance,
        status="blocked_waiting_for_real_login_source_package",
        checksum="sha256:" + "3" * 64,
    )
    _write_template(template)

    payload = audit_account_console_runtime_lineage(
        source_package_path=source,
        acceptance_evidence_path=acceptance,
        template_source_package_path=template,
    )

    assert payload["success"] is False
    assert payload["source_package_satisfies_runtime_lineage"] is False
    assert "account_console_source_package_missing" in payload["issues"]
    assert "account_console_acceptance_evidence_blocked" in payload["issues"]
    assert "account_console_acceptance_source_checksum_placeholder" in payload["issues"]


def test_account_source_artifact_does_not_satisfy_runtime_pack_lineage(tmp_path: Path) -> None:
    source = tmp_path / "source-package.json"
    acceptance = tmp_path / "acceptance.json"
    template = tmp_path / "template.json"
    _write_account_source(source)
    _write_acceptance(acceptance)
    _write_template(template)

    payload = audit_account_console_runtime_lineage(
        source_package_path=source,
        acceptance_evidence_path=acceptance,
        template_source_package_path=template,
    )

    assert payload["success"] is False
    assert payload["account_console_acceptance_passed"] is True
    assert "account_console_source_package_is_account_source_artifact" in payload["issues"]
    assert "account_console_source_package_runtime_pack_missing" in payload["issues"]


def test_route_bound_runtime_source_package_can_satisfy_audit(tmp_path: Path) -> None:
    source = tmp_path / "source-package.json"
    acceptance = tmp_path / "acceptance.json"
    template = tmp_path / "template.json"
    _write_runtime_source(source)
    _write_acceptance(acceptance)
    _write_template(template)

    payload = audit_account_console_runtime_lineage(
        source_package_path=source,
        acceptance_evidence_path=acceptance,
        template_source_package_path=template,
    )

    assert payload["success"] is True
    assert payload["status"] == "passed"
    assert payload["issues"] == []
    assert payload["runtime_lineage"]["required_dll_hashes_present"] is True


def test_cli_writes_blocker_json_and_returns_nonzero(tmp_path: Path) -> None:
    source = tmp_path / "missing" / "source-package.json"
    acceptance = tmp_path / "acceptance.json"
    template = tmp_path / "template.json"
    output_json = tmp_path / "audit.json"
    _write_acceptance(acceptance, status="blocked_waiting_for_real_login_source_package")
    _write_template(template)

    result = subprocess.run(
        [
            sys.executable,
            str(REPO_ROOT / "scripts" / "ctp025292_account_console_runtime_lineage_audit.py"),
            "--source-package",
            str(source),
            "--acceptance-evidence",
            str(acceptance),
            "--template-source-package",
            str(template),
            "--output-json",
            str(output_json),
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 1
    payload = json.loads(output_json.read_text(encoding="utf-8"))
    assert payload["status"] == "blocked"
    assert "account_console_source_package_missing" in payload["issues"]
