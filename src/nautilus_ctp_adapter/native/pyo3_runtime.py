"""PyO3 runtime session factories with Windows DLL search-path setup."""

from __future__ import annotations

import os
from pathlib import Path

from .loader import (
    CTP_RUNTIME_PACK_BIN_ENV,
    CTP_RUNTIME_PACK_STRICT_ENV,
    add_windows_dll_directories,
    candidate_native_paths,
)

_ACTIVE_RUNTIME_PACK_BIN: Path | None = None


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
