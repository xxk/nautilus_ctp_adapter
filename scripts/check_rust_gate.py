from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path


def repository_root() -> Path:
    return Path(__file__).resolve().parent.parent


def rust_manifest(root: Path) -> Path:
    return root / "rust" / "Cargo.toml"


def expected_pyo3_extension_name() -> str:
    """Return the expected basename prefix for the _ctp_runtime PyO3 extension."""
    # maturin builds _ctp_runtime.cpython-3NN-<platform>.pyd / .so
    if sys.platform == "win32":
        return "_ctp_runtime"
    return "_ctp_runtime"


def find_pyo3_extension(build_target_dir: Path) -> Path | None:
    """Locate the built _ctp_runtime cdylib artifact in the debug target directory.

    ``cargo build`` produces a platform-native shared library (``_ctp_runtime.dll``
    on Windows, ``lib_ctp_runtime.so`` on Linux).  The ``.pyd`` renaming only
    happens during ``maturin develop``/``maturin build``.  We therefore accept
    whichever artifact cargo actually produces.
    """
    debug_dir = build_target_dir / "debug"
    if not debug_dir.exists():
        return None
    prefix = expected_pyo3_extension_name()
    # On Windows cargo produces _ctp_runtime.dll; on Linux lib_ctp_runtime.so
    candidate_exts = (".dll", ".pyd", ".so")
    for ext in candidate_exts:
        p = debug_dir / f"{prefix}{ext}"
        if p.exists():
            return p
    # Also accept ABI-tagged names (cpython-3NN-...) produced by maturin
    for p in debug_dir.glob(f"{prefix}*.pyd"):
        return p
    for p in debug_dir.glob(f"{prefix}*.so"):
        return p
    return None


def expected_dynamic_library_name() -> str:
    if sys.platform == "win32":
        return "ctp_native.dll"
    if sys.platform == "darwin":
        return "libctp_native.dylib"
    return "libctp_native.so"


def target_directory(root: Path, metadata: dict[str, object]) -> Path:
    target_dir = metadata.get("target_directory")
    if isinstance(target_dir, str) and target_dir.strip():
        return Path(target_dir)
    return root / "rust" / "target"


def run_command(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )


def print_block(prefix: str, content: str) -> None:
    normalized = content.strip()
    if not normalized:
        return
    for line in normalized.splitlines():
        print(f"{prefix}{line}")


def main() -> int:
    root = repository_root()
    manifest = rust_manifest(root)
    if not manifest.exists():
        print(f"FAIL rust-gate: missing manifest at {manifest}")
        return 1

    cargo = shutil.which("cargo")
    if cargo is None:
        print("FAIL rust-gate: cargo-not-found")
        print(f"INFO rust-gate: expected manifest={manifest}")
        print("NEXT rust-gate: install Rust toolchain and ensure cargo is available on PATH")
        return 1

    metadata_command = [
        cargo,
        "metadata",
        "--format-version",
        "1",
        "--no-deps",
        "--manifest-path",
        str(manifest),
    ]
    metadata_result = run_command(metadata_command)
    if metadata_result.returncode != 0:
        print("FAIL rust-gate: cargo-metadata")
        print(f"INFO rust-gate: command={' '.join(metadata_command)}")
        print_block("STDOUT rust-gate: ", metadata_result.stdout)
        print_block("STDERR rust-gate: ", metadata_result.stderr)
        return 1

    try:
        metadata = json.loads(metadata_result.stdout)
    except json.JSONDecodeError as exc:
        print("FAIL rust-gate: metadata-json")
        print(f"INFO rust-gate: unable to parse cargo metadata output ({exc})")
        print_block("STDOUT rust-gate: ", metadata_result.stdout)
        return 1

    workspace_members = metadata.get("workspace_members", [])
    build_target_dir = target_directory(root, metadata)
    print(f"PASS rust-gate: cargo-found {cargo}")
    print(f"PASS rust-gate: workspace-members={len(workspace_members)} manifest={manifest}")

    check_command = [cargo, "check", "--manifest-path", str(manifest)]
    check_result = run_command(check_command)
    if check_result.returncode != 0:
        print("FAIL rust-gate: cargo-check")
        print(f"INFO rust-gate: command={' '.join(check_command)}")
        print_block("STDOUT rust-gate: ", check_result.stdout)
        print_block("STDERR rust-gate: ", check_result.stderr)
        return 1

    print("PASS rust-gate: cargo-check")
    print_block("STDOUT rust-gate: ", check_result.stdout)

    build_command = [cargo, "build", "--manifest-path", str(manifest)]
    build_result = run_command(build_command)
    if build_result.returncode != 0:
        print("FAIL rust-gate: cargo-build")
        print(f"INFO rust-gate: command={' '.join(build_command)}")
        print_block("STDOUT rust-gate: ", build_result.stdout)
        print_block("STDERR rust-gate: ", build_result.stderr)
        return 1

    artifact_path = build_target_dir / "debug" / expected_dynamic_library_name()
    if not artifact_path.exists():
        print("FAIL rust-gate: artifact-missing")
        print(f"INFO rust-gate: expected artifact={artifact_path}")
        print_block("STDOUT rust-gate: ", build_result.stdout)
        print_block("STDERR rust-gate: ", build_result.stderr)
        return 1

    print(f"PASS rust-gate: cargo-build artifact={artifact_path}")
    print_block("STDOUT rust-gate: ", build_result.stdout)

    # ── ctp_py PyO3 extension build check ─────────────────────────────────
    ctp_py_manifest = root / "rust" / "ctp_py" / "Cargo.toml"
    if ctp_py_manifest.exists():
        ctp_py_build_command = [cargo, "build", "-p", "ctp_py", "--manifest-path", str(manifest)]
        ctp_py_build_result = run_command(ctp_py_build_command)
        if ctp_py_build_result.returncode != 0:
            print("FAIL rust-gate: cargo-build-ctp_py")
            print(f"INFO rust-gate: command={' '.join(ctp_py_build_command)}")
            print_block("STDOUT rust-gate: ", ctp_py_build_result.stdout)
            print_block("STDERR rust-gate: ", ctp_py_build_result.stderr)
            return 1

        pyo3_ext = find_pyo3_extension(build_target_dir)
        if pyo3_ext is None:
            print("FAIL rust-gate: ctp_py-extension-missing")
            print(f"INFO rust-gate: searched {build_target_dir / 'debug'} for _ctp_runtime.*")
            return 1

        print(f"PASS rust-gate: ctp_py-build extension={pyo3_ext}")
        print_block("STDOUT rust-gate: ", ctp_py_build_result.stdout)
    else:
        print("WARN rust-gate: ctp_py-not-found (skipping PyO3 bridge check)")

    # ── cargo test ────────────────────────────────────────────────────────
    test_command = [cargo, "test", "--manifest-path", str(manifest)]
    test_result = run_command(test_command)
    if test_result.returncode != 0:
        print("FAIL rust-gate: cargo-test")
        print(f"INFO rust-gate: command={' '.join(test_command)}")
        print_block("STDOUT rust-gate: ", test_result.stdout)
        print_block("STDERR rust-gate: ", test_result.stderr)
        return 1

    print("PASS rust-gate: cargo-test")
    print_block("STDOUT rust-gate: ", test_result.stdout)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
