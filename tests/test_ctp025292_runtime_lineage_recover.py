from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from scripts.ctp025292_runtime_lineage_recover import recover_runtime_lineage


REPO_ROOT = Path(__file__).resolve().parents[1]


def _write_config(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "BrokerID": "0155",
                "UserID": "025292",
                "Password": "secret",
                "AuthCode": "auth",
                "AppID": "client_iq_3.6.2",
                "ProductInfo": "iQuant",
                "Pricer": "tcp://106.75.173.28:51213",
                "Host": "tcp://106.75.173.28:51205",
                "ProviderId": 45,
                "Instruments": ["ag2612"],
            }
        ),
        encoding="utf-8",
    )


def _write_candidate(path: Path, *, trusted: bool) -> None:
    path.mkdir(parents=True, exist_ok=True)
    (path / "thostmduserapi_se.dll").write_bytes(b"trusted-025292-md")
    (path / "thosttraderapi_se.dll").write_bytes(b"trusted-025292-td")
    if not trusted:
        return
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
    (path / "_ctp025292_runtime_pack.json").write_text(
        json.dumps(marker),
        encoding="utf-8",
    )


def test_pipeline_blocks_without_operator_trusted_marker(tmp_path: Path) -> None:
    source = tmp_path / "candidate" / "bin"
    _write_candidate(source, trusted=False)

    payload = recover_runtime_lineage(
        roots=[tmp_path],
        runtime_bin=tmp_path / "runtime_packs" / "ctp-live-025292-md" / "bin",
        source_package_path=tmp_path / "source-package.json",
        config_path=tmp_path / "cfgs" / "local" / "ctp.live.025292.local.json",
        write=True,
    )

    assert payload["success"] is False
    assert "trusted_runtime_pack_candidate_missing" in payload["issues"]
    assert payload["pipeline"]["discovery"]["blocker_id"] == "ctp025292_runtime_pack_source_unready"
    assert payload["pipeline"]["materialize"] is None
    assert not (tmp_path / "source-package.json").exists()


def test_pipeline_writes_package_and_passes_lineage_with_trusted_marker(tmp_path: Path) -> None:
    source = tmp_path / "trusted" / "bin"
    runtime_bin = tmp_path / "runtime_packs" / "ctp-live-025292-md" / "bin"
    source_package = tmp_path / "account_console" / "source-package.json"
    config = tmp_path / "cfgs" / "local" / "ctp.live.025292.local.json"
    _write_candidate(source, trusted=True)
    _write_config(config)

    payload = recover_runtime_lineage(
        roots=[tmp_path],
        runtime_bin=runtime_bin,
        source_package_path=source_package,
        config_path=config,
        write=True,
    )

    assert payload["success"] is True
    assert payload["pipeline"]["discovery"]["success"] is True
    assert payload["pipeline"]["materialize"]["success"] is True
    assert payload["pipeline"]["source_package"]["success"] is True
    assert payload["pipeline"]["source_lineage_gate"]["success"] is True
    assert source_package.exists()
    assert (runtime_bin / "thostmduserapi_se.dll").exists()


def test_pipeline_preview_does_not_write_even_with_trusted_marker(tmp_path: Path) -> None:
    source = tmp_path / "trusted" / "bin"
    runtime_bin = tmp_path / "runtime_packs" / "ctp-live-025292-md" / "bin"
    source_package = tmp_path / "account_console" / "source-package.json"
    config = tmp_path / "cfgs" / "local" / "ctp.live.025292.local.json"
    _write_candidate(source, trusted=True)
    _write_config(config)

    payload = recover_runtime_lineage(
        roots=[tmp_path],
        runtime_bin=runtime_bin,
        source_package_path=source_package,
        config_path=config,
        write=False,
    )

    assert payload["success"] is False
    assert "ctp025292_runtime_pack_source_unready" in payload["issues"]
    assert payload["pipeline"]["discovery"]["success"] is True
    assert payload["pipeline"]["materialize"]["success"] is False
    assert not source_package.exists()
    assert not runtime_bin.exists()


def test_cli_writes_blocker_json_for_missing_marker(tmp_path: Path) -> None:
    source = tmp_path / "candidate" / "bin"
    output_json = tmp_path / "recover.json"
    _write_candidate(source, trusted=False)

    result = subprocess.run(
        [
            sys.executable,
            str(REPO_ROOT / "scripts" / "ctp025292_runtime_lineage_recover.py"),
            "--root",
            str(tmp_path),
            "--runtime-bin",
            str(tmp_path / "runtime_packs" / "ctp-live-025292-md" / "bin"),
            "--source-package",
            str(tmp_path / "source-package.json"),
            "--config",
            str(tmp_path / "cfgs" / "local" / "ctp.live.025292.local.json"),
            "--write",
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
    assert "trusted_runtime_pack_candidate_missing" in payload["issues"]
