from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from scripts.ctp025292_runtime_lineage_wide_audit import audit_wide_runtime_lineage


REPO_ROOT = Path(__file__).resolve().parents[1]


def _write_marker(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)
    (path / "thostmduserapi_se.dll").write_bytes(b"trusted-025292-md")
    (path / "thosttraderapi_se.dll").write_bytes(b"trusted-025292-td")
    import hashlib

    marker = {
        "runtime_pack_id": "ctp-live-025292-md",
        "source_kind": "operator_trusted_025292",
        "dlls": {
            "thostmduserapi_se.dll": {
                "sha256": hashlib.sha256(b"trusted-025292-md").hexdigest().upper()
            },
            "thosttraderapi_se.dll": {
                "sha256": hashlib.sha256(b"trusted-025292-td").hexdigest().upper()
            },
        },
    }
    (path / "_ctp025292_runtime_pack.json").write_text(json.dumps(marker), encoding="utf-8")


def _write_runtime_pack(path: Path) -> None:
    _write_marker(path)
    import hashlib

    (path / "_synced_from.txt").write_text(
        "\n".join(
            [
                "profile=ctp-live-025292-md",
                "runtime_pack_id=ctp-live-025292-md",
                "loader_isolation=fresh_worker_process_per_runtime_pack",
                f"thostmduserapi_se.dll.sha256={hashlib.sha256(b'trusted-025292-md').hexdigest().upper()}",
                f"thosttraderapi_se.dll.sha256={hashlib.sha256(b'trusted-025292-td').hexdigest().upper()}",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def _write_source_package(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "schema_version": "ctp025292.source_package.v1",
                "account_id": "acct.ctp.live.025292",
                "runtime_pack": {
                    "runtime_pack_id": "ctp-live-025292-md",
                    "dlls": {
                        "thostmduserapi_se.dll": {"sha256": "A" * 64},
                        "thosttraderapi_se.dll": {"sha256": "B" * 64},
                    },
                },
            }
        ),
        encoding="utf-8",
    )


def test_wide_audit_ignores_pytest_tmp_markers(tmp_path: Path) -> None:
    root = tmp_path / "scan_root"
    _write_marker(root / "pytest_tmp" / "test_marker" / "trusted" / "bin")

    payload = audit_wide_runtime_lineage([root])

    assert payload["success"] is False
    assert payload["marker_count"] == 0
    assert payload["skipped_test_marker_count"] == 1
    assert "production_operator_trusted_marker_missing" in payload["issues"]


def test_wide_audit_passes_with_marker_runtime_pack_and_source_package(tmp_path: Path) -> None:
    root = tmp_path / "scan_root"
    _write_runtime_pack(root / "prod" / "runtime_packs" / "ctp-live-025292-md" / "bin")
    _write_source_package(root / "account_console" / "output" / "account_capability" / "ctp-live-025292" / "source-package.json")

    payload = audit_wide_runtime_lineage([root])

    assert payload["success"] is True
    assert payload["valid_marker_count"] == 1
    assert payload["valid_runtime_pack_count"] == 1
    assert payload["valid_source_package_count"] == 1


def test_cli_writes_blocker_json(tmp_path: Path) -> None:
    output_json = tmp_path / "wide.json"
    result = subprocess.run(
        [
            sys.executable,
            str(REPO_ROOT / "scripts" / "ctp025292_runtime_lineage_wide_audit.py"),
            "--root",
            str(tmp_path),
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
    assert "production_operator_trusted_marker_missing" in payload["issues"]
