from __future__ import annotations

import os
from pathlib import Path
from typing import Iterable

from .manifest import BOOTSTRAP_MANAGED_DLLS, REQUIRED_NATIVE_DLLS


def candidate_native_paths(base_dir: str | Path) -> list[Path]:
    """Return probable directories for CTP native DLL resolution."""
    root = Path(base_dir)
    return [
        root / "native",
        root / "native" / "bin",
        root / "vendor" / "ctp",
        root / "vendor" / "ctp" / "bin",
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


def find_native_pack_dir(base_dir: str | Path) -> Path | None:
    for path in candidate_native_paths(base_dir):
        if all((path / name).exists() for name in REQUIRED_NATIVE_DLLS):
            return path
    return None


def find_managed_assembly_dir(base_dir: str | Path) -> Path | None:
    for path in candidate_managed_paths(base_dir):
        if all((path / name).exists() for name in BOOTSTRAP_MANAGED_DLLS):
            return path
    return None


def add_windows_dll_directories(*paths: str | Path) -> list[Path]:
    registered: list[Path] = []
    for raw_path in paths:
        path = Path(raw_path)
        if not path.exists():
            continue
        os.add_dll_directory(str(path))
        registered.append(path)
    return registered
