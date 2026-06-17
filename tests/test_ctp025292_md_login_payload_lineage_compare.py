from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from scripts.ctp025292_md_login_payload_lineage_compare import compare_payload_lineage

REPO_ROOT = Path(__file__).resolve().parents[1]


def _write_current_config(path: Path) -> None:
    path.write_text(
        json.dumps(
            {
                "BrokerID": "0155",
                "UserID": "025292",
                "Password": "secret-password",
                "AuthCode": "secret-auth",
                "AppID": "client_iq_3.6.2",
                "ProductInfo": "iQuant",
                "Pricer": "tcp://md-front.example:51213",
                "Host": "tcp://td-front.example:51205",
                "NativePackDir": "",
                "Instruments": ["ag2612"],
            }
        ),
        encoding="utf-8",
    )


def test_compare_blocks_when_success_history_lacks_materialized_payload(tmp_path: Path) -> None:
    current_config = tmp_path / "ctp.live.025292.local.json"
    docs = tmp_path / "docs"
    docs.mkdir()
    _write_current_config(current_config)
    (docs / "md_startup_truth_20260402.log").write_text(
        '{"baseline":"md-startup-truth-v1","account_id":"025292",'
        '"login_success":true,"first_tick_symbol":"rb2610"}\n'
        "MD Auto-login: 0155/025292\n"
        "MD OnRspUserLogin called: pRspInfo=PTR, pRspUserLogin=PTR\n",
        encoding="utf-8",
    )

    payload = compare_payload_lineage(
        current_config=current_config,
        historical_roots=[docs],
        lifecycle_summary_path=None,
    )

    assert payload["status"] == "blocked"
    assert payload["blocker_id"] == "ctp025292_md_login_payload_success_lineage_unavailable"
    assert "known_success_payload_config_artifact_missing" in payload["issues"]
    assert "historical_success_payload_values_unavailable" in payload["issues"]
    assert payload["historical_scan_summary"]["historical_success_ref_count"] == 1
    assert payload["diagnosis"]["historical_success_is_known"] is True
    assert payload["diagnosis"]["historical_success_payload_materialized"] is False
    assert payload["diagnosis"]["payload_delta_decidable"] is False
    assert payload["current_config_summary"]["sensitive_fields"]["password"]["present"] is True
    assert payload["current_config_summary"]["sensitive_fields"]["password"]["raw_value_recorded"] is False
    assert payload["current_config_summary"]["sensitive_fields"]["password"]["sha256_prefix"]
    assert payload["negative_assertions"]["secret_values_recorded"] is False
    assert payload["negative_assertions"]["did_not_generate_or_consume_paper_request"] is True


def test_compare_keeps_payload_fingerprint_only_when_historical_config_exists(tmp_path: Path) -> None:
    current_config = tmp_path / "ctp.live.025292.local.json"
    docs = tmp_path / "docs"
    historical_config = docs / "ctp.live.025292.rb2610.10675.json"
    docs.mkdir()
    _write_current_config(current_config)
    _write_current_config(historical_config)

    payload = compare_payload_lineage(
        current_config=current_config,
        historical_roots=[docs],
        lifecycle_summary_path=None,
    )

    comparison = payload["config_fingerprint_comparisons"][0]
    assert comparison["broker_id_equal"] is True
    assert comparison["user_id_equal"] is True
    assert comparison["field_fingerprint_comparison"]["sensitive_fields.password"][
        "fingerprint_equal"
    ] is True
    assert comparison["field_fingerprint_comparison"]["sensitive_fields.password"][
        "raw_values_recorded"
    ] is False
    assert payload["current_config_summary"]["sensitive_fields"]["auth_code"]["raw_value_recorded"] is False
    assert payload["historical_config_summaries"][0]["sensitive_fields"]["auth_code"][
        "raw_value_recorded"
    ] is False


def test_cli_writes_blocker_json_without_raw_secrets(tmp_path: Path) -> None:
    current_config = tmp_path / "ctp.live.025292.local.json"
    docs = tmp_path / "docs"
    output = tmp_path / "payload_compare.json"
    docs.mkdir()
    _write_current_config(current_config)
    (docs / "evidence.md").write_text("025292 login_success=true\n", encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            str(REPO_ROOT / "scripts" / "ctp025292_md_login_payload_lineage_compare.py"),
            "--current-config",
            str(current_config),
            "--historical-root",
            str(docs),
            "--output-json",
            str(output),
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 1
    text = output.read_text(encoding="utf-8")
    assert "secret-password" not in text
    assert "secret-auth" not in text
    assert "md-front.example" not in text
    payload = json.loads(text)
    assert payload["blocker_id"] == "ctp025292_md_login_payload_success_lineage_unavailable"
