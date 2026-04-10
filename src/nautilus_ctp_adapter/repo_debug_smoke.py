from __future__ import annotations

from pathlib import Path

import ctp_runtime
import ctp_runtime._ctp_runtime as native_runtime
from ctp_runtime import CtpMdSession, CtpTdSession, INVALID_HANDLE, SCAFFOLD_NOT_IMPLEMENTED


def collect_repo_debug_smoke_snapshot() -> dict[str, object]:
    md = CtpMdSession(front="tcp://md.example:51213", broker="0155", user="025292", password="debug")
    td = CtpTdSession(
        front="tcp://td.example:51205",
        broker="0155",
        user="025292",
        password="debug",
        appid="client_iq_3.6.2",
        auth_code="RFLEXUGHCKIKWGPC",
    )
    snapshot: dict[str, object] = {
        "probe_scope": "repo_only_debug_bootstrap",
        "td_probe_mode": "public_pyo3_scaffold_before_c3",
        "formal_live_td_entrypoint": "python scripts/ctp_nautilus_live_smoke.py --config <path>",
        "formal_live_td_path": "execution_client.run_live_td_readiness_smoke -> native.td_ctypes -> ctp_native.dll",
        "runtime_package_file": str(Path(ctp_runtime.__file__).resolve()),
        "runtime_native_module_file": str(Path(native_runtime.__file__).resolve()),
        "has_internal_md_live_session": hasattr(native_runtime, "CtpMdLiveSession"),
        "scaffold_not_implemented": SCAFFOLD_NOT_IMPLEMENTED,
        "invalid_handle": INVALID_HANDLE,
        "md_init_code": md.init(),
        "md_login_code": md.login(),
        "md_subscribe_code": md.subscribe(["rb2610"]),
        "td_init_code": td.init(),
        "td_authenticate_code": td.authenticate(),
        "td_login_code": td.login(),
    }
    md.dispose()
    snapshot["md_init_after_dispose_code"] = md.init()
    return snapshot