from __future__ import annotations

import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "scripts" / "sync_ctp_native.py"


def _write_stub_dlls(directory: Path, *names: str) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    for name in names:
        (directory / name).write_bytes(f"stub:{name}".encode("utf-8"))


def _run_sync(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT_PATH), *args],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


def test_sync_ctp_native_runtime_pack_from_explicit_ctp_api_source(tmp_path: Path) -> None:
    ctp_api_source = tmp_path / "site-packages" / "vnpy_ctp" / "api"
    _write_stub_dlls(
        ctp_api_source,
        "thostmduserapi_se.dll",
        "thosttraderapi_se.dll",
        "thostmduserapi.dll",
    )
    target_dir = tmp_path / "synced" / "bin"

    result = _run_sync(
        "--pack-kind",
        "runtime",
        "--ctp-api-source",
        str(ctp_api_source),
        "--target-dir",
        str(target_dir),
    )

    assert result.returncode == 0, result.stderr or result.stdout
    assert (target_dir / "thostmduserapi_se.dll").exists()
    assert (target_dir / "thosttraderapi_se.dll").exists()
    assert (target_dir / "thostmduserapi.dll").exists()
    assert not (target_dir / "ctp_native.dll").exists()

    manifest = (target_dir / "_synced_from.txt").read_text(encoding="utf-8")
    assert "pack_kind=runtime" in manifest
    assert f"ctp_api={ctp_api_source}" in manifest


def test_sync_ctp_native_compat_pack_discovers_ctp_api_from_scan_root(tmp_path: Path) -> None:
    repo_native_source = tmp_path / "rust" / "target" / "debug"
    _write_stub_dlls(repo_native_source, "ctp_native.dll")

    scan_root = tmp_path / "scan-root"
    ctp_api_source = scan_root / ".venv" / "Lib" / "site-packages" / "vnpy_ctp" / "api"
    _write_stub_dlls(
        ctp_api_source,
        "thostmduserapi_se.dll",
        "thosttraderapi_se.dll",
        "thosttraderapi.dll",
    )
    target_dir = tmp_path / "compat" / "bin"

    result = _run_sync(
        "--pack-kind",
        "compat",
        "--repo-native-source",
        str(repo_native_source),
        "--scan-root",
        str(scan_root),
        "--target-dir",
        str(target_dir),
    )

    assert result.returncode == 0, result.stderr or result.stdout
    assert (target_dir / "ctp_native.dll").exists()
    assert (target_dir / "thostmduserapi_se.dll").exists()
    assert (target_dir / "thosttraderapi_se.dll").exists()
    assert (target_dir / "thosttraderapi.dll").exists()

    manifest = (target_dir / "_synced_from.txt").read_text(encoding="utf-8")
    assert "pack_kind=compat" in manifest
    assert f"repo_native={repo_native_source}" in manifest
    assert "repo_native_mode=repo_build_requires_sdk_for_live" in manifest
    assert f"ctp_api={ctp_api_source}" in manifest
    assert "WARNING: repo-built ctp_native.dll is scaffold-only" in result.stdout