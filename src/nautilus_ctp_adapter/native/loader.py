from __future__ import annotations

import os
from pathlib import Path
from typing import Iterable
import ctypes

from .manifest import BOOTSTRAP_MANAGED_DLLS, REQUIRED_NATIVE_DLLS

_DLL_DIRECTORY_HANDLES: list[object] = []
_PRELOADED_RUNTIME_DLL_HANDLES: list[object] = []
CTP_RUNTIME_PACK_BIN_ENV = "NAUTILUS_CTP_RUNTIME_PACK_BIN"
CTP_RUNTIME_PACK_STRICT_ENV = "NAUTILUS_CTP_RUNTIME_PACK_STRICT"


def _as_bool(value: str | None) -> bool:
    return str(value or "").strip().lower() in {"1", "true", "yes", "on"}


def explicit_runtime_pack_bin_from_env() -> Path | None:
    value = os.environ.get(CTP_RUNTIME_PACK_BIN_ENV, "").strip()
    if not value:
        return None
    return Path(value)


def runtime_pack_strict_from_env() -> bool:
    return _as_bool(os.environ.get(CTP_RUNTIME_PACK_STRICT_ENV))


def _resolve_runtime_pack_bin(base_dir: Path, value: str | Path | None) -> Path | None:
    if value is None:
        return None
    path = Path(value)
    if not path.is_absolute():
        path = base_dir / path
    return path.resolve()


def candidate_native_paths(
    base_dir: str | Path,
    *,
    runtime_pack_bin: str | Path | None = None,
    strict_runtime_pack: bool | None = None,
) -> list[Path]:
    """Return probable directories for CTP native DLL resolution."""
    root = Path(base_dir).resolve()
    explicit_runtime_pack = _resolve_runtime_pack_bin(
        root,
        runtime_pack_bin if runtime_pack_bin else explicit_runtime_pack_bin_from_env(),
    )
    strict = runtime_pack_strict_from_env() if strict_runtime_pack is None else strict_runtime_pack
    repo_owned_native_paths = [
        root / "rust" / "target" / "debug",
        root / "rust" / "target" / "release",
    ]
    fallback_paths = [
        root / "native",
        root / "native" / "bin",
        root / "vendor" / "ctp",
        root / "vendor" / "ctp" / "bin",
    ]
    if explicit_runtime_pack is None:
        return repo_owned_native_paths + fallback_paths
    if strict:
        return [explicit_runtime_pack] + repo_owned_native_paths
    return [explicit_runtime_pack] + repo_owned_native_paths + fallback_paths


def candidate_native_dll_paths(
    base_dir: str | Path,
    *,
    runtime_pack_bin: str | Path | None = None,
    strict_runtime_pack: bool | None = None,
) -> list[Path]:
    return [
        path / "ctp_native.dll"
        for path in candidate_native_paths(
            base_dir,
            runtime_pack_bin=runtime_pack_bin,
            strict_runtime_pack=strict_runtime_pack,
        )
    ]


def candidate_managed_paths(base_dir: str | Path) -> list[Path]:
    root = Path(base_dir)
    return [
        root / "vendor" / "ctp" / "bin",
        root / "vendor" / "ctp" / "managed",
        root,
    ]


def first_existing_path(paths: Iterable[Path]) -> Path | None:
    for path in paths:
        if path.exists():
            return path
    return None


def find_repo_owned_native_dll(
    base_dir: str | Path,
    *,
    runtime_pack_bin: str | Path | None = None,
    strict_runtime_pack: bool | None = None,
) -> Path | None:
    return first_existing_path(
        candidate_native_dll_paths(
            base_dir,
            runtime_pack_bin=runtime_pack_bin,
            strict_runtime_pack=strict_runtime_pack,
        )
    )


def find_native_pack_dir(
    base_dir: str | Path,
    *,
    runtime_pack_bin: str | Path | None = None,
    strict_runtime_pack: bool | None = None,
) -> Path | None:
    runtime_dlls = tuple(name for name in REQUIRED_NATIVE_DLLS if name != "ctp_native.dll")
    for path in candidate_native_paths(
        base_dir,
        runtime_pack_bin=runtime_pack_bin,
        strict_runtime_pack=strict_runtime_pack,
    ):
        if all((path / name).exists() for name in runtime_dlls):
            return path
    return None


def find_managed_assembly_dir(base_dir: str | Path) -> Path | None:
    for path in candidate_managed_paths(base_dir):
        if all((path / name).exists() for name in BOOTSTRAP_MANAGED_DLLS):
            return path
    return None


def add_windows_dll_directories(*paths: str | Path) -> list[Path]:
    registered: list[Path] = []
    add_dll_directory = getattr(os, "add_dll_directory", None)
    if add_dll_directory is None:
        return registered
    for raw_path in paths:
        path = Path(raw_path)
        if not path.exists():
            continue
        _DLL_DIRECTORY_HANDLES.append(add_dll_directory(str(path)))
        registered.append(path)
    return registered


def preload_runtime_vendor_dlls(
    *paths: str | Path,
    dll_loader=ctypes.WinDLL,
) -> list[Path]:
    """Preload MD/TD vendor DLLs so PyO3 imports resolve CTP C++ exports."""
    loaded: list[Path] = []
    for raw_path in paths:
        directory = Path(raw_path)
        if not directory.exists():
            continue
        for dll_name in REQUIRED_NATIVE_DLLS:
            if dll_name == "ctp_native.dll":
                continue
            dll_path = directory / dll_name
            if not dll_path.exists():
                continue
            _PRELOADED_RUNTIME_DLL_HANDLES.append(dll_loader(str(dll_path)))
            loaded.append(dll_path)
    return loaded
