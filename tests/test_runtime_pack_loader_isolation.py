from __future__ import annotations

from pathlib import Path

import pytest

from nautilus_ctp_adapter.adapters.ctp.config import CtpAdapterConfig
from nautilus_ctp_adapter.adapters.ctp.data_client import CtpDataClient
import nautilus_ctp_adapter.adapters.ctp.data_client as data_client_module
from nautilus_ctp_adapter.runtime import CtpRuntimeEventKind
from nautilus_ctp_adapter.native import loader as loader_module
from nautilus_ctp_adapter.native.loader import (
    CTP_RUNTIME_PACK_BIN_ENV,
    CTP_RUNTIME_PACK_STRICT_ENV,
    candidate_native_paths,
    find_native_pack_dir,
    preload_runtime_vendor_dlls,
)
from nautilus_ctp_adapter.native import pyo3_runtime


def _write_runtime_pack(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)
    (path / "thostmduserapi_se.dll").write_bytes(b"md")
    (path / "thosttraderapi_se.dll").write_bytes(b"td")


def test_explicit_runtime_pack_is_first_and_strict_omits_vendor_fallback(tmp_path: Path) -> None:
    runtime_pack = tmp_path / "output" / "runtime_packs" / "ctp-live-025292-md" / "bin"

    paths = candidate_native_paths(
        tmp_path,
        runtime_pack_bin=runtime_pack,
        strict_runtime_pack=True,
    )

    assert paths[0] == runtime_pack
    assert tmp_path / "rust" / "target" / "debug" in paths
    assert tmp_path / "vendor" / "ctp" / "bin" not in paths


def test_find_native_pack_dir_prefers_explicit_runtime_pack(tmp_path: Path) -> None:
    runtime_pack = tmp_path / "output" / "runtime_packs" / "ctp-live-025292-md" / "bin"
    vendor_pack = tmp_path / "vendor" / "ctp" / "bin"
    _write_runtime_pack(runtime_pack)
    _write_runtime_pack(vendor_pack)

    selected = find_native_pack_dir(
        tmp_path,
        runtime_pack_bin=runtime_pack,
        strict_runtime_pack=True,
    )

    assert selected == runtime_pack


def test_runtime_pack_env_drives_candidate_paths(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    runtime_pack = tmp_path / "runtime_packs" / "ctp-live-025292-md" / "bin"
    monkeypatch.setenv(CTP_RUNTIME_PACK_BIN_ENV, str(runtime_pack))
    monkeypatch.setenv(CTP_RUNTIME_PACK_STRICT_ENV, "1")

    paths = candidate_native_paths(tmp_path)

    assert paths[0] == runtime_pack
    assert tmp_path / "vendor" / "ctp" / "bin" not in paths


def test_relative_runtime_pack_resolves_against_repo_root(tmp_path: Path) -> None:
    runtime_pack = Path("output") / "runtime_packs" / "ctp-live-025292-md" / "bin"

    paths = candidate_native_paths(
        tmp_path,
        runtime_pack_bin=runtime_pack,
        strict_runtime_pack=True,
    )

    assert paths[0] == (tmp_path / runtime_pack).resolve()


def test_pyo3_runtime_rejects_in_process_runtime_pack_switch(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    first_pack = tmp_path / "runtime_packs" / "ctp-live-025292-md" / "bin"
    second_pack = tmp_path / "runtime_packs" / "ctp-paper-19053-md" / "bin"
    monkeypatch.setattr(pyo3_runtime, "_ACTIVE_RUNTIME_PACK_BIN", None)
    monkeypatch.delenv(CTP_RUNTIME_PACK_BIN_ENV, raising=False)
    monkeypatch.delenv(CTP_RUNTIME_PACK_STRICT_ENV, raising=False)

    pyo3_runtime._select_runtime_pack(first_pack, strict_runtime_pack=True)
    with pytest.raises(RuntimeError, match="fresh worker process"):
        pyo3_runtime._select_runtime_pack(second_pack, strict_runtime_pack=True)


def test_pyo3_runtime_preloads_explicit_runtime_thost_dependencies(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    runtime_pack = tmp_path / "runtime_packs" / "ctp-live-025292-md" / "bin"
    _write_runtime_pack(runtime_pack)
    loaded: list[Path] = []

    class FakeWinDll:
        def __init__(self, path: str) -> None:
            loaded.append(Path(path))

    monkeypatch.setattr(pyo3_runtime, "_PRELOADED_NATIVE_DLLS", [])
    monkeypatch.setattr(pyo3_runtime.ctypes, "WinDLL", FakeWinDll)

    pyo3_runtime._preload_runtime_dependencies(
        runtime_pack_bin=runtime_pack,
        strict_runtime_pack=True,
    )

    assert loaded == [
        runtime_pack / "thostmduserapi_se.dll",
        runtime_pack / "thosttraderapi_se.dll",
    ]


def test_pyo3_runtime_import_bootstrap_is_explicit_native_loader_owner(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    runtime_pack = tmp_path / "runtime_packs" / "ctp-live-025292-md" / "bin"
    _write_runtime_pack(runtime_pack)
    registered: list[tuple[Path, ...]] = []
    preloaded: list[tuple[Path, ...]] = []

    monkeypatch.setattr(pyo3_runtime, "_ACTIVE_RUNTIME_PACK_BIN", None)
    monkeypatch.setattr(pyo3_runtime, "_BOOTSTRAPPED_PYO3_IMPORT", False)
    monkeypatch.setenv(CTP_RUNTIME_PACK_BIN_ENV, str(runtime_pack))
    monkeypatch.setenv(CTP_RUNTIME_PACK_STRICT_ENV, "1")
    monkeypatch.setattr(pyo3_runtime.os, "name", "nt")
    monkeypatch.setattr(
        pyo3_runtime,
        "add_windows_dll_directories",
        lambda *paths: registered.append(tuple(Path(path) for path in paths)) or list(paths),
    )
    monkeypatch.setattr(
        pyo3_runtime,
        "preload_runtime_vendor_dlls",
        lambda *paths: preloaded.append(tuple(Path(path) for path in paths)) or [],
    )

    paths = pyo3_runtime.bootstrap_pyo3_runtime_import(repo_root=tmp_path)

    assert paths[0] == runtime_pack
    assert registered == [tuple(paths)]
    assert preloaded == [tuple(paths)]
    assert pyo3_runtime._ACTIVE_RUNTIME_PACK_BIN == runtime_pack
    assert pyo3_runtime._BOOTSTRAPPED_PYO3_IMPORT is True


def test_loader_preloads_runtime_vendor_dlls_for_package_import(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    runtime_pack = tmp_path / "runtime_packs" / "ctp-live-025292-md" / "bin"
    _write_runtime_pack(runtime_pack)
    loaded: list[Path] = []

    class FakeWinDll:
        def __init__(self, path: str) -> None:
            loaded.append(Path(path))

    monkeypatch.setattr(loader_module, "_PRELOADED_RUNTIME_DLL_HANDLES", [])

    result = preload_runtime_vendor_dlls(runtime_pack, dll_loader=FakeWinDll)

    assert result == [
        runtime_pack / "thostmduserapi_se.dll",
        runtime_pack / "thosttraderapi_se.dll",
    ]
    assert loaded == result


def test_md_smoke_passes_configured_native_pack_dir_to_session_factory(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    runtime_pack = tmp_path / "runtime_packs" / "ctp-live-025292-md" / "bin"
    records: dict[str, object] = {}

    class FakeMdLiveSession:
        def __init__(self, flow_path: Path) -> None:
            records["flow_path"] = flow_path
            self._front_connected_callback = None
            self._login_callback = None
            self._tick_callback = None

        def set_front_connected_callback(self, callback) -> None:
            self._front_connected_callback = callback

        def set_login_callback(self, callback) -> None:
            self._login_callback = callback

        def set_tick_callback(self, callback) -> None:
            self._tick_callback = callback

        def set_front_disconnected_callback(self, callback) -> None:
            pass

        def init(self, front: str) -> int:
            assert self._front_connected_callback is not None
            self._front_connected_callback()
            return 0

        def login(self, *args: str) -> int:
            class LoginResponse:
                success = True
                error_id = 0
                error_message = ""
                front_id = 1
                session_id = 2
                max_order_ref = 3

            assert self._login_callback is not None
            self._login_callback(LoginResponse())
            return 0

        def subscribe(self, symbols: list[str]) -> int:
            class Tick:
                symbol = "ag2612"
                last = 100.0
                bid = 99.0
                ask = 101.0
                ts_epoch_us = 1775052501781380
                bid_size = 1
                ask_size = 1
                volume = 1
                open_interest = 2.0

            assert self._tick_callback is not None
            self._tick_callback(Tick())
            return 0

        def dispose(self) -> None:
            records["disposed"] = True

    def fake_create_md_live_session(flow_path: Path, **kwargs: object) -> FakeMdLiveSession:
        records["runtime_pack_kwargs"] = kwargs
        return FakeMdLiveSession(flow_path)

    monkeypatch.setattr(data_client_module, "_create_md_live_session", fake_create_md_live_session)
    config = CtpAdapterConfig.from_dict(
        {
            "BrokerID": "0155",
            "UserID": "025292",
            "Password": "secret",
            "Pricer": "tcp://127.0.0.1:41213",
            "Host": "tcp://127.0.0.1:41205",
            "NativePackDir": str(runtime_pack),
            "Instruments": ["ag2612"],
        }
    )

    result = CtpDataClient(config).run_live_md_smoke(
        timeout_seconds=1,
        flow_path=tmp_path / "md_flow",
    )

    assert records["runtime_pack_kwargs"] == {
        "runtime_pack_bin": str(runtime_pack),
        "strict_runtime_pack": True,
    }
    assert records["disposed"] is True
    assert result.login_success is True
