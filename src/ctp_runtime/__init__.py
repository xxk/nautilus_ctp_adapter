"""
ctp_runtime — PyO3 bridge exposing the Rust-owned CTP runtime to Python.

Public symbols are re-exported from the compiled ``_ctp_runtime`` extension.
"""

from pathlib import Path
import sys


if sys.platform == "win32":
    from nautilus_ctp_adapter.native.loader import add_windows_dll_directories, find_native_pack_dir

    _REPO_ROOT = Path(__file__).resolve().parents[2]
    _NATIVE_PACK_DIR = find_native_pack_dir(_REPO_ROOT)
    if _NATIVE_PACK_DIR is not None:
        add_windows_dll_directories(_NATIVE_PACK_DIR)

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
