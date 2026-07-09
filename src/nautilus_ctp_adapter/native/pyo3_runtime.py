"""PyO3 runtime session factories with Windows DLL search-path setup."""

from __future__ import annotations

import os
from pathlib import Path
import ctypes

from .loader import (
    CTP_RUNTIME_PACK_BIN_ENV,
    CTP_RUNTIME_PACK_STRICT_ENV,
    add_windows_dll_directories,
    candidate_native_paths,
    explicit_runtime_pack_bin_from_env,
    preload_runtime_vendor_dlls,
    runtime_pack_strict_from_env,
)
from .manifest import REQUIRED_NATIVE_DLLS

_ACTIVE_RUNTIME_PACK_BIN: Path | None = None
_PRELOADED_NATIVE_DLLS: list[object] = []
_BOOTSTRAPPED_PYO3_IMPORT = False


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _select_runtime_pack(runtime_pack_bin: str | Path | None, *, strict_runtime_pack: bool) -> None:
    global _ACTIVE_RUNTIME_PACK_BIN
    if runtime_pack_bin is None:
        return
    selected = Path(runtime_pack_bin).resolve()
    if _ACTIVE_RUNTIME_PACK_BIN is not None and _ACTIVE_RUNTIME_PACK_BIN != selected:
        raise RuntimeError(
            "CTP runtime pack cannot be switched inside one process; start a fresh worker process "
            f"for {selected}"
        )
    _ACTIVE_RUNTIME_PACK_BIN = selected
    os.environ[CTP_RUNTIME_PACK_BIN_ENV] = str(selected)
    if strict_runtime_pack:
        os.environ[CTP_RUNTIME_PACK_STRICT_ENV] = "1"


def _prepare_runtime_dll_dirs(
    *,
    runtime_pack_bin: str | Path | None = None,
    strict_runtime_pack: bool = False,
) -> None:
    _select_runtime_pack(runtime_pack_bin, strict_runtime_pack=strict_runtime_pack)
    add_windows_dll_directories(
        *candidate_native_paths(
            _repo_root(),
            runtime_pack_bin=runtime_pack_bin,
            strict_runtime_pack=strict_runtime_pack,
        )
    )
    _preload_runtime_dependencies(
        runtime_pack_bin=runtime_pack_bin,
        strict_runtime_pack=strict_runtime_pack,
    )


def bootstrap_pyo3_runtime_import(
    *,
    repo_root: str | Path | None = None,
    runtime_pack_bin: str | Path | None = None,
    strict_runtime_pack: bool | None = None,
) -> list[Path]:
    """Prepare Windows DLL resolution before importing ``ctp_runtime._ctp_runtime``.

    This is the native-loader-owned compatibility bootstrap for the top-level
    ``ctp_runtime`` package.  New code should call owner APIs here instead of
    duplicating DLL search/preload logic in import shims or smoke scripts.
    """
    global _BOOTSTRAPPED_PYO3_IMPORT
    if os.name != "nt":
        _BOOTSTRAPPED_PYO3_IMPORT = True
        return []

    selected_runtime_pack = (
        runtime_pack_bin if runtime_pack_bin is not None else explicit_runtime_pack_bin_from_env()
    )
    strict = runtime_pack_strict_from_env() if strict_runtime_pack is None else strict_runtime_pack
    if selected_runtime_pack is not None:
        _select_runtime_pack(selected_runtime_pack, strict_runtime_pack=strict)

    root = Path(repo_root).resolve() if repo_root is not None else _repo_root()
    native_paths = candidate_native_paths(
        root,
        runtime_pack_bin=selected_runtime_pack,
        strict_runtime_pack=strict,
    )
    add_windows_dll_directories(*native_paths)
    preload_runtime_vendor_dlls(*native_paths)
    _BOOTSTRAPPED_PYO3_IMPORT = True
    return native_paths


def _preload_runtime_dependencies(
    *,
    runtime_pack_bin: str | Path | None = None,
    strict_runtime_pack: bool = False,
) -> None:
    if strict_runtime_pack and runtime_pack_bin is not None:
        candidate_dirs = [Path(runtime_pack_bin).resolve()]
    else:
        candidate_dirs = candidate_native_paths(
            _repo_root(),
            runtime_pack_bin=runtime_pack_bin,
            strict_runtime_pack=strict_runtime_pack,
        )
    for directory in candidate_dirs:
        if not directory.exists():
            continue
        for dll_name in REQUIRED_NATIVE_DLLS:
            if dll_name == "ctp_native.dll":
                continue
            dll_path = directory / dll_name
            if dll_path.exists():
                _PRELOADED_NATIVE_DLLS.append(ctypes.WinDLL(str(dll_path)))


def create_md_live_session(
    flow_path: Path,
    runtime_pack_bin: str | Path | None = None,
    *,
    strict_runtime_pack: bool = False,
):
    _prepare_runtime_dll_dirs(
        runtime_pack_bin=runtime_pack_bin,
        strict_runtime_pack=strict_runtime_pack,
    )
    try:
        from ctp_runtime._ctp_runtime import CtpMdLiveSession
    except ImportError as exc:
        raise RuntimeError(
            "PyO3 MD bridge unavailable; run maturin develop or pip install -e . before MD operations"
        ) from exc
    return CtpMdLiveSession(str(flow_path))


def create_td_live_session(
    flow_path: Path,
    runtime_pack_bin: str | Path | None = None,
    *,
    strict_runtime_pack: bool = False,
):
    _prepare_runtime_dll_dirs(
        runtime_pack_bin=runtime_pack_bin,
        strict_runtime_pack=strict_runtime_pack,
    )
    try:
        from ctp_runtime._ctp_runtime import CtpTdLiveSession
    except ImportError as exc:
        raise RuntimeError(
            "PyO3 TD bridge unavailable; run maturin develop or pip install -e . before TD operations"
        ) from exc
    return CtpTdLiveSession(str(flow_path))
