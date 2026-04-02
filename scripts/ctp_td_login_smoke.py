from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from nautilus_ctp_adapter.adapters.ctp.config import CtpAdapterConfig
from nautilus_ctp_adapter.native import CtpTdApi


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the repository-owned Python TD auth/login readiness smoke.")
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--timeout-seconds", type=int, default=20)
    args = parser.parse_args()

    config = CtpAdapterConfig.from_json_file(args.config)
    api = CtpTdApi.load(REPO_ROOT)
    flow_path = REPO_ROOT / "var" / "td_flow_smoke"
    flow_path.mkdir(parents=True, exist_ok=True)
    handle = api.create(flow_path)
    state: dict[str, object] = {"login": None, "disconnects": []}

    try:
        api.set_login_callback(handle, lambda resp: state.__setitem__("login", resp))
        api.set_front_disconnected_callback(
            handle,
            lambda reason: state["disconnects"].append(reason),
        )

        init_code = api.init(handle, config.td_front)
        authenticate_code = api.authenticate(handle, config.app_id, config.auth_code, config.product_info)
        login_code = api.login(handle, config.broker_id, config.user_id, config.password)

        deadline = time.time() + args.timeout_seconds
        while time.time() < deadline:
            if state["login"] is not None:
                break
            time.sleep(0.1)

        login = state["login"]
        settlement_code = -1
        if login is not None and login.success:
            settlement_code = api.confirm_settlement(handle)

        print(
            json.dumps(
                {
                    "init_code": init_code,
                    "authenticate_code": authenticate_code,
                    "login_code": login_code,
                    "settlement_code": settlement_code,
                    "login_success": None if login is None else login.success,
                    "login_error_id": None if login is None else login.error_id,
                    "login_error_message": None if login is None else login.error_message,
                    "front_id": None if login is None else login.front_id,
                    "session_id": None if login is None else login.session_id,
                    "max_order_ref": None if login is None else login.max_order_ref,
                    "disconnects": list(state["disconnects"]),
                },
                ensure_ascii=False,
            )
        )
        return 0 if login is not None and login.success else 1
    finally:
        api.dispose(handle)


if __name__ == "__main__":
    raise SystemExit(main())
