from __future__ import annotations

import os
from pathlib import Path
from types import SimpleNamespace

from nautilus_ctp_adapter.native.loader import (
    CTP_RUNTIME_PACK_BIN_ENV,
    CTP_RUNTIME_PACK_STRICT_ENV,
)
from scripts.ctp025292_runtime_pack_process_preflight import build_preflight_payload


def _write_runtime_pack(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)
    for name in ("ctp_native.dll", "thostmduserapi_se.dll", "thosttraderapi_se.dll"):
        (path / name).write_bytes(f"{name}\n".encode("ascii"))


def test_runtime_pack_process_preflight_passes_with_symbols(tmp_path: Path, monkeypatch) -> None:
    runtime_pack = tmp_path / "runtime_packs" / "ctp-live-025292-md" / "bin"
    _write_runtime_pack(runtime_pack)
    monkeypatch.delenv(CTP_RUNTIME_PACK_BIN_ENV, raising=False)
    monkeypatch.delenv(CTP_RUNTIME_PACK_STRICT_ENV, raising=False)
    loaded: list[str] = []

    def fake_loader(path: str) -> object:
        loaded.append(path)
        return object()

    def fake_importer(name: str):
        assert name == "ctp_runtime._ctp_runtime"
        return SimpleNamespace(CtpMdLiveSession=object, CtpTdLiveSession=object)

    payload = build_preflight_payload(
        runtime_pack_bin=runtime_pack,
        win_dll_loader=fake_loader,
        module_importer=fake_importer,
    )

    assert payload["success"] is True
    assert payload["result_status"] == "runtime_process_preflight_passed"
    assert payload["ready_for_md_smoke"] is True
    assert payload["is_s2_g2_market_data_pass"] is False
    assert payload["negative_assertions"]["does_not_connect_md_front"] is True
    assert payload["runtime_pack_environment"] == {
        "bound": True,
        "runtime_pack_bin_env": CTP_RUNTIME_PACK_BIN_ENV,
        "runtime_pack_strict_env": CTP_RUNTIME_PACK_STRICT_ENV,
        "runtime_pack_bin": str(runtime_pack.resolve()),
        "strict": True,
    }
    assert os.environ[CTP_RUNTIME_PACK_BIN_ENV] == str(runtime_pack.resolve())
    assert os.environ[CTP_RUNTIME_PACK_STRICT_ENV] == "1"
    assert len(loaded) == 2


def test_runtime_pack_process_preflight_redacts_loader_os_error(tmp_path: Path) -> None:
    runtime_pack = tmp_path / "runtime_packs" / "ctp-live-025292-md" / "bin"
    _write_runtime_pack(runtime_pack)

    def fake_loader(path: str) -> object:
        raise OSError("raw loader failure details must not be recorded")

    payload = build_preflight_payload(
        runtime_pack_bin=runtime_pack,
        win_dll_loader=fake_loader,
        module_importer=lambda name: SimpleNamespace(),
    )

    assert payload["success"] is False
    assert payload["result_status"] == "stage2_tool_or_runtime_blocker"
    assert payload["blocker_id"] == "ctp025292_runtime_pack_process_preflight_failed"
    assert payload["failure_stage"] == "runtime_pack_preload"
    assert payload["exception"]["error_message"] == "<redacted; see error_message_shape>"
    assert payload["exception"]["raw_error_message_recorded"] is False
    assert payload["negative_assertions"]["raw_secret_values_recorded"] is False


def test_runtime_pack_process_preflight_blocks_missing_required_dll(tmp_path: Path) -> None:
    runtime_pack = tmp_path / "runtime_packs" / "ctp-live-025292-md" / "bin"
    runtime_pack.mkdir(parents=True)
    (runtime_pack / "ctp_native.dll").write_bytes(b"native")

    payload = build_preflight_payload(runtime_pack_bin=runtime_pack)

    assert payload["success"] is False
    assert payload["failure_stage"] == "runtime_pack_inventory"
    assert "required_dll_missing:thostmduserapi_se.dll" in payload["issues"]
    assert payload["ready_for_md_smoke"] is False
