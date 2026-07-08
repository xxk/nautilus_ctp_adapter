import json
from pathlib import Path
from nautilus_ctp_adapter.adapters.ctp.config import CtpAdapterConfig
from nautilus_ctp_adapter.adapters.ctp.factory import build_ctp_stack
config = CtpAdapterConfig.from_json_file(Path('cfgs/local/ctp.live.025292.local.json'))
stack = build_ctp_stack(config)
result = stack['execution_client'].run_live_td_readiness_smoke(timeout_seconds=20)
payload = {
    'init_code': result.init_code,
    'authenticate_code': result.authenticate_code,
    'login_code': result.login_code,
    'settlement_code': result.settlement_code,
    'login_success': result.login_success,
    'login_error_id': result.login_error_id,
    'login_error_message': result.login_error_message,
    'front_id': result.front_id,
    'session_id': result.session_id,
    'max_order_ref': result.max_order_ref,
    'disconnects': result.disconnects,
}
print(json.dumps(payload, ensure_ascii=False))
