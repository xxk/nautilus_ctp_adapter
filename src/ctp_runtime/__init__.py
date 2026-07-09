"""
ctp_runtime — PyO3 bridge exposing the Rust-owned CTP runtime to Python.

Public symbols are re-exported from the compiled ``_ctp_runtime`` extension.
The native-loader-owned compatibility bootstrap keeps DLL resolution out of
this import shim so it cannot become a second native loading truth.
"""

from pathlib import Path

from nautilus_ctp_adapter.native.pyo3_runtime import bootstrap_pyo3_runtime_import


_REPO_ROOT = Path(__file__).resolve().parents[2]
bootstrap_pyo3_runtime_import(repo_root=_REPO_ROOT)

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
