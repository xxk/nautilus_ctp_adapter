"""
ctp_runtime — PyO3 bridge exposing the Rust-owned CTP runtime to Python.

Public symbols are re-exported from the compiled ``_ctp_runtime`` extension.
"""

from pathlib import Path
import sys


if sys.platform == "win32":
    from nautilus_ctp_adapter.native.loader import (
        add_windows_dll_directories,
        candidate_native_paths,
        explicit_runtime_pack_bin_from_env,
        preload_runtime_vendor_dlls,
        runtime_pack_strict_from_env,
    )

    _REPO_ROOT = Path(__file__).resolve().parents[2]
    _NATIVE_PATHS = candidate_native_paths(
        _REPO_ROOT,
        runtime_pack_bin=explicit_runtime_pack_bin_from_env(),
        strict_runtime_pack=runtime_pack_strict_from_env(),
    )
    add_windows_dll_directories(
        *_NATIVE_PATHS
    )
    preload_runtime_vendor_dlls(*_NATIVE_PATHS)

from ._ctp_runtime import (  # noqa: F401  (re-export)
    CtpMdSession,
    CtpTdSession,
    SCAFFOLD_NOT_IMPLEMENTED,
    INVALID_HANDLE,
)

__all__ = [
    "CtpMdSession",
    "CtpTdSession",
    "SCAFFOLD_NOT_IMPLEMENTED",
    "INVALID_HANDLE",
]
