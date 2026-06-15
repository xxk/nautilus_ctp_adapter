from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from scripts.ctp025292_source_lineage_gate import build_lineage_summary
from scripts.ctp025292_source_package_build import build_source_package_summary


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


def _write_runtime_pack(runtime_bin: Path) -> None:
    runtime_bin.mkdir(parents=True, exist_ok=True)
    dlls = {
        "thostmduserapi_se.dll": b"trusted-025292-md",
        "thosttraderapi_se.dll": b"trusted-025292-td",
    }
    import hashlib

    hashes: dict[str, str] = {}
    for filename, content in dlls.items():
        (runtime_bin / filename).write_bytes(content)
        hashes[filename] = hashlib.sha256(content).hexdigest().upper()
    (runtime_bin / "_synced_from.txt").write_text(
        "\n".join(
            [
                "profile=ctp-live-025292-md",
                "pack_kind=runtime",
                "runtime_pack_id=ctp-live-025292-md",
                "ctp_api=D:/trusted/ctp025292/runtime-pack",
                "loader_isolation=fresh_worker_process_per_runtime_pack",
                f"thostmduserapi_se.dll.sha256={hashes['thostmduserapi_se.dll']}",
                f"thosttraderapi_se.dll.sha256={hashes['thosttraderapi_se.dll']}",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def test_missing_runtime_pack_blocks_source_package_write(tmp_path: Path) -> None:
    output_path = tmp_path / "source-package.json"

    payload = build_source_package_summary(
        runtime_bin=tmp_path / "missing-runtime-pack",
        output_path=output_path,
        write=True,
        observed_at="2026-06-16T00:00:00Z",
    )

    assert payload["success"] is False
    assert payload["status"] == "blocked"
    assert "runtime_pack_bin_missing" in payload["issues"]
    assert "write_rejected_due_to_source_package_issues" in payload["issues"]
    assert payload["source_package_preview"]["source_health"]["state"] == "runtime_lineage_unready_preview"
    assert not output_path.exists()


def test_runtime_pack_builds_source_package_that_passes_lineage_gate(tmp_path: Path) -> None:
    runtime_bin = tmp_path / "runtime_packs" / "ctp-live-025292-md" / "bin"
    output_path = tmp_path / "account_console" / "source-package.json"
    config_path = tmp_path / "cfgs" / "local" / "ctp.live.025292.local.json"
    _write_runtime_pack(runtime_bin)
    _write_config(config_path)

    payload = build_source_package_summary(
        runtime_bin=runtime_bin,
        output_path=output_path,
        write=True,
        observed_at="2026-06-16T00:00:00Z",
    )

    assert payload["success"] is True
    assert output_path.exists()
    package = json.loads(output_path.read_text(encoding="utf-8"))
    assert package["runtime_pack"]["runtime_pack_id"] == "ctp-live-025292-md"
    assert package["source_health"]["state"] == "runtime_lineage_ready"
    assert package["negative_assertions"]["not_market_data_ready_evidence"] is True

    lineage = build_lineage_summary(
        config_path=config_path,
        source_package_path=output_path,
        runtime_bin=runtime_bin,
    )
    assert lineage["success"] is True


def test_cli_preview_returns_nonzero_without_writing_for_missing_runtime(tmp_path: Path) -> None:
    output_json = tmp_path / "preview.json"
    source_package = tmp_path / "source-package.json"

    result = subprocess.run(
        [
            sys.executable,
            str(REPO_ROOT / "scripts" / "ctp025292_source_package_build.py"),
            "--runtime-bin",
            str(tmp_path / "missing"),
            "--output-path",
            str(source_package),
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
    assert payload["write_requested"] is False
    assert payload["status"] == "blocked"
    assert not source_package.exists()
