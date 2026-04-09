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
