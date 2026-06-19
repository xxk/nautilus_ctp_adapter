from __future__ import annotations

import json
from pathlib import Path

from scripts.ctp025292_original_repo_success_lineage_audit import (
    audit_original_repo_success_lineage,
)


def _write_pair(bin_dir: Path, md: bytes = b"md", td: bytes = b"td") -> None:
    bin_dir.mkdir(parents=True, exist_ok=True)
    (bin_dir / "thostmduserapi_se.dll").write_bytes(md)
    (bin_dir / "thosttraderapi_se.dll").write_bytes(td)


def test_original_repo_config_redacts_secrets_and_does_not_auto_trust_empty_native_pack(
    tmp_path: Path,
) -> None:
    root = tmp_path / "original"
    config_dir = root / "cfgs" / "local"
    config_dir.mkdir(parents=True)
    (config_dir / "ctp.live.025292.local.json").write_text(
        json.dumps(
            {
                "BrokerID": "0155",
                "UserID": "025292",
                "Password": "secret-password",
                "AuthCode": "secret-auth",
                "AppID": "secret-app",
                "Host": "tcp://secret-host",
                "Pricer": "tcp://secret-md",
                "NativePackDir": "",
                "Instruments": ["rb2610"],
            }
        ),
        encoding="utf-8",
    )
    vendor_bin = root / "vendor" / "ctp" / "bin"
    _write_pair(vendor_bin)
    (vendor_bin / "_synced_from.txt").write_text(
        "profile=auto\nctp_api=output/openctp/tts-sdk/tts_6.6.9-win64-combined\n",
        encoding="utf-8",
    )

    payload = audit_original_repo_success_lineage(root)

    assert payload["success"] is False
    assert payload["auto_trust_allowed"] is False
    assert "original_current_config_native_pack_dir_empty" in payload["issues"]
    assert "original_vendor_manifest_points_openctp" in payload["issues"]
    rendered = json.dumps(payload, ensure_ascii=False)
    assert "secret-password" not in rendered
    assert "secret-auth" not in rendered
    assert "tcp://secret-host" not in rendered
    assert payload["current_config_summary"]["password_present"] is True
    assert payload["current_config_summary"]["native_pack_dir_value_recorded"] is False


def test_original_repo_historical_success_without_runtime_hash_remains_blocked(tmp_path: Path) -> None:
    root = tmp_path / "original"
    config_dir = root / "cfgs" / "local"
    config_dir.mkdir(parents=True)
    (config_dir / "ctp.live.025292.local.json").write_text(
        '{"BrokerID":"0155","UserID":"025292","NativePackDir":"vendor/ctp/bin"}',
        encoding="utf-8",
    )
    output_dir = root / "output" / "reports"
    output_dir.mkdir(parents=True)
    (output_dir / "historical_success.json").write_text(
        '{"account_id":"025292","login_success":true}',
        encoding="utf-8",
    )
    vendor_bin = root / "vendor" / "ctp" / "bin"
    _write_pair(vendor_bin)
    (vendor_bin / "_synced_from.txt").write_text("profile=auto\nctp_api=vendor/ctp/bin\n", encoding="utf-8")

    payload = audit_original_repo_success_lineage(root)

    assert payload["success"] is False
    assert "original_historical_success_runtime_hash_missing" in payload["issues"]
    assert payload["historical_audit_summary"]["historical_success_ref_count"] == 1
    assert payload["historical_audit_summary"]["trusted_runtime_hash_ref_count"] == 0
    assert payload["negative_assertions"]["did_not_write_trust_marker"] is True
