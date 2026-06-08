from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from nautilus_ctp_adapter.adapters.ctp.config import CtpAdapterConfig


DEFAULT_ENV_PATH = REPO_ROOT / ".env"
DEFAULT_ENV_DIR = REPO_ROOT / ".env.d"
DEFAULT_TEMPLATE_PATH = REPO_ROOT / "cfgs" / "ctp.openctp.tts.7x24.example.json"
DEFAULT_OUTPUT_PATH = REPO_ROOT / "cfgs" / "local" / "ctp.openctp.tts.7x24.local.json"
OPENCTP_TTS_7X24_PROFILE = "openctp-tts-7x24-simulation"
OPENCTP_TTS_7X24_PROFILE_ALIASES = {"openctp-paper", OPENCTP_TTS_7X24_PROFILE}
OPENCTP_TTS_7X24_ENV_FILES = (
    "openctp-tts-7x24-simulation.env",
    "openctp-paper.env",
)


def load_dotenv(path: Path = DEFAULT_ENV_PATH) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.exists():
        return values
    for raw_line in path.read_text(encoding="utf-8-sig").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def env_value(values: dict[str, str], name: str, default: str = "") -> str:
    return os.environ.get(name, values.get(name, default)).strip()


def merge_env_file(values: dict[str, str], path: Path) -> None:
    values.update(load_dotenv(path))


def canonical_account_profile(profile: str) -> str:
    if not profile:
        return OPENCTP_TTS_7X24_PROFILE
    if profile in OPENCTP_TTS_7X24_PROFILE_ALIASES:
        return OPENCTP_TTS_7X24_PROFILE
    raise ValueError(
        "CTP_ACCOUNT_PROFILE must be openctp-tts-7x24-simulation for this helper "
        f"(openctp-paper is accepted as a legacy alias), got {profile!r}"
    )


def load_env_bundle(
    *,
    env_path: Path = DEFAULT_ENV_PATH,
    env_dir: Path = DEFAULT_ENV_DIR,
    profile: str | None = None,
) -> dict[str, str]:
    values = load_dotenv(env_path)
    selected_profile = canonical_account_profile(
        profile
        or os.environ.get("CTP_ACCOUNT_PROFILE", "").strip()
        or values.get("CTP_ACCOUNT_PROFILE", "").strip()
        or OPENCTP_TTS_7X24_PROFILE
    )

    if env_dir.exists():
        for file_name in OPENCTP_TTS_7X24_ENV_FILES:
            candidate = env_dir / file_name
            if candidate.exists():
                merge_env_file(values, candidate)
                break

    values["CTP_ACCOUNT_PROFILE"] = selected_profile
    return values


def build_openctp_payload(template_path: Path, values: dict[str, str]) -> dict[str, object]:
    payload = json.loads(template_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("OpenCTP config template must contain a JSON object")

    user_id = env_value(values, "OPENCTP_TTS_7X24_USER_ID")
    password = env_value(values, "OPENCTP_TTS_7X24_PASSWORD")
    if not user_id:
        raise ValueError("missing OPENCTP_TTS_7X24_USER_ID")
    if not password:
        raise ValueError("missing OPENCTP_TTS_7X24_PASSWORD")

    payload["UserID"] = user_id
    payload["Password"] = password
    payload.setdefault("ExecutionGuardrails", {})["AllowLiveOrderSmoke"] = False
    return payload


def resolve_account_profile(values: dict[str, str]) -> str:
    profile = env_value(values, "CTP_ACCOUNT_PROFILE", OPENCTP_TTS_7X24_PROFILE)
    return canonical_account_profile(profile)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Write ignored OpenCTP TTS 7x24 local config from .env/.env.d."
    )
    parser.add_argument("--env", type=Path, default=DEFAULT_ENV_PATH)
    parser.add_argument("--env-dir", type=Path, default=DEFAULT_ENV_DIR)
    parser.add_argument("--profile", default=None)
    parser.add_argument("--template", type=Path, default=DEFAULT_TEMPLATE_PATH)
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()

    values = load_env_bundle(env_path=args.env, env_dir=args.env_dir, profile=args.profile)
    account_profile = resolve_account_profile(values)
    output_path = args.output or Path(
        env_value(values, "OPENCTP_TTS_CONFIG", str(DEFAULT_OUTPUT_PATH))
    )
    if not output_path.is_absolute():
        output_path = REPO_ROOT / output_path

    payload = build_openctp_payload(args.template, values)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    config = CtpAdapterConfig.from_json_file(output_path)
    print(
        json.dumps(
            {
                "account_profile": account_profile,
                "profile_aliases": sorted(OPENCTP_TTS_7X24_PROFILE_ALIASES - {account_profile}),
                "path": str(output_path.relative_to(REPO_ROOT)),
                "user_id": config.user_id,
                "password_present": bool(config.password),
                "allow_empty_broker_id": config.allow_empty_broker_id,
                "md_front": config.md_front,
                "td_front": config.td_front,
                "instruments": config.instruments,
                "allow_live_order_smoke": config.execution_guardrails.allow_live_order_smoke,
                "validate": config.validate(),
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
