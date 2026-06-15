"""PyO3 runtime session factories with Windows DLL search-path setup."""

from __future__ import annotations

from pathlib import Path

from .loader import add_windows_dll_directories, candidate_native_paths


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _prepare_runtime_dll_dirs() -> None:
    add_windows_dll_directories(*candidate_native_paths(_repo_root()))


def create_md_live_session(flow_path: Path):
    _prepare_runtime_dll_dirs()
    try:
        from ctp_runtime._ctp_runtime import CtpMdLiveSession
    except ImportError as exc:
        raise RuntimeError(
            "PyO3 MD bridge unavailable; run maturin develop or pip install -e . before MD operations"
        ) from exc
    return CtpMdLiveSession(str(flow_path))


def create_td_live_session(flow_path: Path):
    _prepare_runtime_dll_dirs()
    try:
        from ctp_runtime._ctp_runtime import CtpTdLiveSession
    except ImportError as exc:
        raise RuntimeError(
            "PyO3 TD bridge unavailable; run maturin develop or pip install -e . before TD operations"
        ) from exc
    return CtpTdLiveSession(str(flow_path))
