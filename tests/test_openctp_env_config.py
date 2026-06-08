from __future__ import annotations

import json
from pathlib import Path

from scripts.write_openctp_tts_config_from_env import build_openctp_payload, load_dotenv
from scripts.write_openctp_tts_config_from_env import load_env_bundle
from scripts.ctp_paper_session_preflight import build_preflight_summary
from scripts.ctp_paper_session_preflight import paper_config_issues
from scripts.ctp_paper_session_preflight import redacted_config_summary
from nautilus_ctp_adapter.adapters.ctp.config import CtpAdapterConfig


def test_openctp_dotenv_parser_reads_basic_values(tmp_path: Path) -> None:
    env_path = tmp_path / ".env"
    env_path.write_text(
        "\n".join(
            [
                "OPENCTP_TTS_7X24_USER_ID=PAPER_USER_TEST",
                "OPENCTP_TTS_7X24_PASSWORD='secret'",
                "# ignored",
                "",
            ]
        ),
        encoding="utf-8",
    )

    values = load_dotenv(env_path)

    assert values["OPENCTP_TTS_7X24_USER_ID"] == "PAPER_USER_TEST"
    assert values["OPENCTP_TTS_7X24_PASSWORD"] == "secret"


def test_openctp_env_payload_keeps_live_send_disarmed(tmp_path: Path) -> None:
    template = tmp_path / "template.json"
    template.write_text(
        json.dumps(
            {
                "BrokerID": "9999",
                "UserID": "",
                "Password": "",
                "Pricer": "tcp://trading.openctp.cn:30011",
                "Host": "tcp://trading.openctp.cn:30001",
                "AllowEmptyBrokerID": False,
                "Instruments": ["TEST"],
                "ExecutionGuardrails": {
                    "Enabled": True,
                    "AllowedInstruments": ["TEST"],
                    "MaxOrderQty": 1,
                    "MaxNetPosition": 5,
                    "MaxSubmitPerMinute": 10,
                    "PriceMode": "best_level_1",
                    "AllowLiveOrderSmoke": True,
                },
            }
        ),
        encoding="utf-8",
    )

    payload = build_openctp_payload(
        template,
        {
            "OPENCTP_TTS_7X24_USER_ID": "PAPER_USER_TEST",
            "OPENCTP_TTS_7X24_PASSWORD": "secret",
        },
    )

    assert payload["UserID"] == "PAPER_USER_TEST"
    assert payload["Password"] == "secret"
    assert payload["BrokerID"] == "9999"
    assert payload["AllowEmptyBrokerID"] is False
    assert payload["ExecutionGuardrails"]["AllowLiveOrderSmoke"] is False


def test_openctp_env_bundle_overlays_profile_directory(tmp_path: Path) -> None:
    env_path = tmp_path / ".env"
    env_dir = tmp_path / ".env.d"
    env_dir.mkdir()
    env_path.write_text(
        "\n".join(
            [
                "CTP_ACCOUNT_PROFILE=openctp-tts-7x24-simulation",
                "OPENCTP_TTS_CONFIG=cfgs/local/ctp.openctp.tts.7x24.local.json",
            ]
        ),
        encoding="utf-8",
    )
    (env_dir / "openctp-tts-7x24-simulation.env").write_text(
        "\n".join(
            [
                "OPENCTP_TTS_7X24_USER_ID=PAPER_USER_TEST",
                "OPENCTP_TTS_7X24_PASSWORD=secret",
            ]
        ),
        encoding="utf-8",
    )

    values = load_env_bundle(env_path=env_path, env_dir=env_dir)

    assert values["CTP_ACCOUNT_PROFILE"] == "openctp-tts-7x24-simulation"
    assert values["OPENCTP_TTS_CONFIG"] == "cfgs/local/ctp.openctp.tts.7x24.local.json"
    assert values["OPENCTP_TTS_7X24_USER_ID"] == "PAPER_USER_TEST"
    assert values["OPENCTP_TTS_7X24_PASSWORD"] == "secret"


def _paper_payload(**overrides: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "BrokerID": "9999",
        "UserID": "PAPER_USER_TEST",
        "Password": "secret",
        "ProductInfo": "OpenCTP",
        "AppID": "",
        "AuthCode": "",
        "Pricer": "tcp://trading.openctp.cn:30011",
        "Host": "tcp://trading.openctp.cn:30001",
        "ProviderId": 45,
        "AllowEmptyBrokerID": False,
        "Instruments": ["TEST"],
        "ExecutionGuardrails": {
            "Enabled": True,
            "AllowedInstruments": ["TEST"],
            "MaxOrderQty": 1,
            "MaxNetPosition": 5,
            "MaxSubmitPerMinute": 10,
            "PriceMode": "best_level_1",
            "AllowLiveOrderSmoke": False,
        },
    }
    payload.update(overrides)
    return payload


def test_paper_preflight_summary_redacts_account_secret(tmp_path: Path) -> None:
    config_path = tmp_path / "paper.json"
    config_path.write_text(json.dumps(_paper_payload()), encoding="utf-8")

    summary = build_preflight_summary(config_path)
    serialized = json.dumps(summary, ensure_ascii=False)

    assert summary["success"] is True
    assert summary["account_profile"] == "openctp-tts-7x24-simulation"
    assert summary["evidence_class"] == "openctp-tts-7x24-simulation"
    assert summary["action_mode"] == "request_only"
    assert summary["config"]["user_id_present"] is True
    assert summary["config"]["password_present"] is True
    assert "PAPER_USER_TEST" not in serialized
    assert "secret" not in serialized


def test_paper_preflight_missing_config_is_typed_blocker(tmp_path: Path) -> None:
    summary = build_preflight_summary(tmp_path / "missing.json")

    assert summary["success"] is False
    assert summary["status"] == "blocked"
    assert summary["failure_reason"] == "missing_config"
    assert summary["blocker_type"] == "paper-resource"


def test_paper_preflight_rejects_non_openctp_fronts() -> None:
    config = CtpAdapterConfig.from_dict(
        _paper_payload(Pricer="tcp://formal.example:1", Host="tcp://formal.example:2")
    )

    issues = paper_config_issues(config)

    assert "paper_profile.md_front" in issues
    assert "paper_profile.td_front" in issues


def test_paper_preflight_rejects_armed_order_smoke() -> None:
    payload = _paper_payload()
    guardrails = dict(payload["ExecutionGuardrails"])  # type: ignore[arg-type]
    guardrails["AllowLiveOrderSmoke"] = True
    payload["ExecutionGuardrails"] = guardrails
    config = CtpAdapterConfig.from_dict(payload)

    assert "execution_guardrails.allow_live_order_smoke_must_be_false" in paper_config_issues(
        config
    )


def test_paper_preflight_can_allow_armed_order_smoke_when_explicit() -> None:
    payload = _paper_payload()
    guardrails = dict(payload["ExecutionGuardrails"])  # type: ignore[arg-type]
    guardrails["AllowLiveOrderSmoke"] = True
    payload["ExecutionGuardrails"] = guardrails
    config = CtpAdapterConfig.from_dict(payload)

    assert "execution_guardrails.allow_live_order_smoke_must_be_false" not in paper_config_issues(
        config, allow_live_order_smoke=True
    )


def test_redacted_config_summary_does_not_emit_raw_front_for_formal_like_config() -> None:
    config = CtpAdapterConfig.from_dict(
        _paper_payload(Pricer="tcp://private-front:1", Host="tcp://private-front:2")
    )

    summary = redacted_config_summary(config)
    serialized = json.dumps(summary, ensure_ascii=False)

    assert "private-front" not in serialized
    assert summary["md_front_is_openctp"] is False
    assert summary["td_front_is_openctp"] is False
