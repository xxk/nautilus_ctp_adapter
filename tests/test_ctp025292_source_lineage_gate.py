from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from scripts.ctp025292_source_lineage_gate import build_lineage_summary
from scripts.ctp025292_source_package_build import build_source_package_summary


REPO_ROOT = Path(__file__).resolve().parents[1]


def _write_config(path: Path, *, password: str = "secret-password") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "BrokerID": "0155",
                "UserID": "025292",
                "Password": password,
                "AuthCode": "secret-auth",
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


def _write_manifest(runtime_bin: Path, ctp_api: str, *, runtime_pack_id: str = "", profile: str = "auto") -> None:
    runtime_bin.mkdir(parents=True, exist_ok=True)
    lines = [
        f"profile={profile}",
        "pack_kind=runtime",
    ]
    if runtime_pack_id:
        lines.append(f"runtime_pack_id={runtime_pack_id}")
    lines.extend([f"ctp_api={ctp_api}", "managed="])
    (runtime_bin / "_synced_from.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _rewrite_manifest_with_hashes(
    runtime_bin: Path,
    hashes: dict[str, str],
    *,
    ctp_api: str = "D:/trusted/ctp025292/runtime-pack",
) -> None:
    (runtime_bin / "_synced_from.txt").write_text(
        "\n".join(
            [
                "profile=ctp-live-025292-md",
                "pack_kind=runtime",
                "runtime_pack_id=ctp-live-025292-md",
                f"ctp_api={ctp_api}",
                "loader_isolation=fresh_worker_process_per_runtime_pack",
                f"thostmduserapi_se.dll.sha256={hashes['thostmduserapi_se.dll']}",
                f"thosttraderapi_se.dll.sha256={hashes['thosttraderapi_se.dll']}",
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
                "account_id": "025292",
                "account_uid": "ctp-live.025292",
                "market_data_account_id": "025292",
                "market_source": "CTP 025292 official market data only",
                "runtime_pack": {
                    "runtime_pack_id": "ctp-live-025292-md",
                    "ref": "D:/trusted/ctp025292/runtime-pack",
                    "sha256": "0" * 64,
                    "dlls": {
                        "thostmduserapi_se.dll": {
                            "sha256": "A" * 64
                        },
                        "thosttraderapi_se.dll": {
                            "sha256": "B" * 64
                        },
                    },
                },
            }
        ),
        encoding="utf-8",
    )


def _write_runtime_dlls(runtime_bin: Path, *, md_hash_seed: bytes, trader_hash_seed: bytes) -> dict[str, str]:
    runtime_bin.mkdir(parents=True, exist_ok=True)
    files = {
        "thostmduserapi_se.dll": md_hash_seed,
        "thosttraderapi_se.dll": trader_hash_seed,
    }
    hashes: dict[str, str] = {}
    import hashlib

    for filename, content in files.items():
        (runtime_bin / filename).write_bytes(content)
        hashes[filename] = hashlib.sha256(content).hexdigest().upper()
    return hashes


def _write_source_package_with_hashes(path: Path, hashes: dict[str, str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "schema_version": "ctp025292.source_package.v1",
                "account_id": "025292",
                "account_uid": "ctp-live.025292",
                "market_data_account_id": "025292",
                "market_source": "CTP 025292 official market data only",
                "runtime_pack": {
                    "runtime_pack_id": "ctp-live-025292-md",
                    "ref": "D:/trusted/ctp025292/runtime-pack",
                    "dlls": {
                        name: {"sha256": digest}
                        for name, digest in hashes.items()
                    },
                },
            }
        ),
        encoding="utf-8",
    )


def _build_source_package_with_config_lineage(
    *,
    runtime_bin: Path,
    config_path: Path,
    output_path: Path,
) -> None:
    payload = build_source_package_summary(
        runtime_bin=runtime_bin,
        config_path=config_path,
        output_path=output_path,
        write=True,
        observed_at="2026-06-16T00:00:00Z",
        trusted_config_roots=[config_path.parents[2]],
    )
    assert payload["success"] is True


def test_gate_blocks_missing_source_package_and_openctp_runtime(tmp_path: Path) -> None:
    config = tmp_path / "cfgs" / "local" / "ctp.live.025292.local.json"
    runtime_bin = tmp_path / "vendor" / "ctp" / "bin"
    source_package = tmp_path / "missing" / "source-package.json"
    _write_config(config)
    _write_manifest(runtime_bin, "output/openctp/tts-sdk/tts_6.6.9-win64-combined")

    payload = build_lineage_summary(
        config_path=config,
        source_package_path=source_package,
        runtime_bin=runtime_bin,
        trusted_config_roots=[tmp_path],
    )

    assert payload["success"] is False
    assert payload["blocker_id"] == "ctp025292_source_lineage_unready"
    assert "source_package_missing" in payload["issues"]
    assert "runtime_manifest_openctp_tts_for_025292" in payload["issues"]
    assert "runtime_manifest.runtime_pack_id_missing" in payload["issues"]
    assert "runtime_dll_missing:thostmduserapi_se.dll" in payload["issues"]
    assert payload["negative_assertions"]["did_not_submit_broker_order"] is True
    assert "secret-password" not in json.dumps(payload, ensure_ascii=False)


def test_gate_passes_with_trusted_025292_source_package_and_runtime(tmp_path: Path) -> None:
    config = tmp_path / "cfgs" / "local" / "ctp.live.025292.local.json"
    runtime_bin = tmp_path / "vendor" / "ctp" / "bin"
    source_package = tmp_path / "account_console" / "source-package.json"
    _write_config(config)
    _write_manifest(
        runtime_bin,
        "D:/trusted/ctp025292/runtime-pack",
        runtime_pack_id="ctp-live-025292-md",
        profile="ctp-live-025292-md",
    )
    hashes = _write_runtime_dlls(runtime_bin, md_hash_seed=b"ctp025292-md", trader_hash_seed=b"ctp025292-td")
    _rewrite_manifest_with_hashes(runtime_bin, hashes)
    _build_source_package_with_config_lineage(
        runtime_bin=runtime_bin,
        config_path=config,
        output_path=source_package,
    )

    payload = build_lineage_summary(
        config_path=config,
        source_package_path=source_package,
        runtime_bin=runtime_bin,
        trusted_config_roots=[tmp_path],
    )

    assert payload["success"] is True
    assert payload["status"] == "passed"
    assert payload["issues"] == []
    assert payload["broker_order_submission"] is False
    assert payload["trading_adapter"] == "disabled"
    assert payload["negative_assertions"]["did_not_claim_market_data_ready"] is True


def test_gate_rejects_external_config_even_with_trusted_runtime_lineage(tmp_path: Path) -> None:
    external_root = tmp_path / "external-original-repo"
    config = external_root / "cfgs" / "local" / "ctp.live.025292.local.json"
    runtime_bin = tmp_path / "vendor" / "ctp" / "bin"
    source_package = tmp_path / "account_console" / "source-package.json"
    _write_config(config)
    _write_manifest(
        runtime_bin,
        "D:/trusted/ctp025292/runtime-pack",
        runtime_pack_id="ctp-live-025292-md",
        profile="ctp-live-025292-md",
    )
    hashes = _write_runtime_dlls(runtime_bin, md_hash_seed=b"ctp025292-md", trader_hash_seed=b"ctp025292-td")
    _rewrite_manifest_with_hashes(runtime_bin, hashes)
    _build_source_package_with_config_lineage(
        runtime_bin=runtime_bin,
        config_path=config,
        output_path=source_package,
    )

    payload = build_lineage_summary(
        config_path=config,
        source_package_path=source_package,
        runtime_bin=runtime_bin,
        trusted_config_roots=[tmp_path / "trusted-worktree"],
    )

    assert payload["success"] is False
    assert payload["blocker_id"] == "ctp025292_source_lineage_unready"
    assert "config_outside_repo_root" in payload["issues"]
    assert payload["config"]["password_present"] is True
    assert "secret-password" not in json.dumps(payload, ensure_ascii=False)
    assert payload["negative_assertions"]["did_not_claim_market_data_ready"] is True


def test_gate_rejects_source_package_without_md_config_lineage(tmp_path: Path) -> None:
    config = tmp_path / "cfgs" / "local" / "ctp.live.025292.local.json"
    runtime_bin = tmp_path / "vendor" / "ctp" / "bin"
    source_package = tmp_path / "account_console" / "source-package.json"
    _write_config(config)
    _write_manifest(
        runtime_bin,
        "D:/trusted/ctp025292/runtime-pack",
        runtime_pack_id="ctp-live-025292-md",
        profile="ctp-live-025292-md",
    )
    hashes = _write_runtime_dlls(runtime_bin, md_hash_seed=b"ctp025292-md", trader_hash_seed=b"ctp025292-td")
    _write_source_package_with_hashes(source_package, hashes)

    payload = build_lineage_summary(
        config_path=config,
        source_package_path=source_package,
        runtime_bin=runtime_bin,
        trusted_config_roots=[tmp_path],
    )

    assert payload["success"] is False
    assert "source_package.md_config_lineage_missing" in payload["issues"]
    assert payload["source_package"]["summary"]["md_config_lineage_present"] is False
    assert payload["negative_assertions"]["did_not_claim_market_data_ready"] is True


def test_gate_rejects_hash_mismatch_even_when_pack_id_is_025292(tmp_path: Path) -> None:
    config = tmp_path / "cfgs" / "local" / "ctp.live.025292.local.json"
    runtime_bin = tmp_path / "vendor" / "ctp" / "bin"
    source_package = tmp_path / "account_console" / "source-package.json"
    _write_config(config)
    _write_manifest(
        runtime_bin,
        "D:/trusted/ctp025292/runtime-pack",
        runtime_pack_id="ctp-live-025292-md",
        profile="ctp-live-025292-md",
    )
    _write_runtime_dlls(runtime_bin, md_hash_seed=b"wrong-md", trader_hash_seed=b"wrong-td")
    _write_source_package(source_package)

    payload = build_lineage_summary(
        config_path=config,
        source_package_path=source_package,
        runtime_bin=runtime_bin,
        trusted_config_roots=[tmp_path],
    )

    assert payload["success"] is False
    assert "runtime_dll_hash_mismatch:thostmduserapi_se.dll" in payload["issues"]
    assert "runtime_dll_hash_mismatch:thosttraderapi_se.dll" in payload["issues"]


def test_cli_writes_blocker_json_and_returns_nonzero(tmp_path: Path) -> None:
    config = tmp_path / "cfgs" / "local" / "ctp.live.025292.local.json"
    runtime_bin = tmp_path / "vendor" / "ctp" / "bin"
    source_package = tmp_path / "missing" / "source-package.json"
    output_json = tmp_path / "lineage.json"
    _write_config(config)
    _write_manifest(runtime_bin, "output/openctp/tts-sdk/tts_6.6.9-win64-combined")

    result = subprocess.run(
        [
            sys.executable,
            str(REPO_ROOT / "scripts" / "ctp025292_source_lineage_gate.py"),
            "--config",
            str(config),
            "--source-package",
            str(source_package),
            "--runtime-bin",
            str(runtime_bin),
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
    assert "source_package_missing" in payload["issues"]
