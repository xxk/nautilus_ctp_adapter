from __future__ import annotations

import os
import json
import shutil
import subprocess
import sys
import tempfile
from collections import deque
from pathlib import Path


RUST_GATE_ROOT_OVERRIDE_ENV = "NAUTILUS_CTP_ADAPTER_ROOT_OVERRIDE"
SDK_ENV_KEYS = ("CTP_VENDOR_SDK_ROOT", "CTP_SDK_ROOT")
SDK_SCAN_ROOTS_ENV = "CTP_SDK_SCAN_ROOTS"
SDK_REQUIRED_FILES = (
    "ThostFtdcMdApi.h",
    "ThostFtdcTraderApi.h",
    "ThostFtdcUserApiStruct.h",
    "thostmduserapi_se.lib",
    "thosttraderapi_se.lib",
)
RUNTIME_VENDOR_DLLS = ("thostmduserapi_se.dll", "thosttraderapi_se.dll")
SDK_SEARCH_MAX_DEPTH = 8


def repository_root() -> Path:
    override = os.environ.get(RUST_GATE_ROOT_OVERRIDE_ENV, "").strip()
    if override:
        return Path(override).expanduser().resolve()
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


def vendor_runtime_bin(root: Path) -> Path | None:
    candidate = root / "vendor" / "ctp" / "bin"
    if candidate.exists():
        return candidate
    return None


def sync_vendor_runtime_dlls_to_target_dirs(
    root: Path,
    build_target_dir: Path,
) -> list[Path]:
    """Keep Cargo test DLL loading aligned with the repo native pack.

    On Windows, Cargo may put target output directories ahead of the vendor
    runtime pack when launching test binaries.  If an older CTP runtime DLL is
    left in target/debug, the test executable can fail during process load with
    STATUS_ENTRYPOINT_NOT_FOUND before any Rust test runs.
    """
    runtime_bin = vendor_runtime_bin(root)
    if runtime_bin is None:
        return []

    target_dirs = [build_target_dir / "debug", build_target_dir / "debug" / "deps"]
    copied: list[Path] = []
    for target_dir in target_dirs:
        target_dir.mkdir(parents=True, exist_ok=True)
        for filename in RUNTIME_VENDOR_DLLS:
            source = runtime_bin / filename
            if not source.exists():
                continue
            target = target_dir / filename
            if target.exists():
                try:
                    if (
                        target.stat().st_size == source.stat().st_size
                        and target.read_bytes() == source.read_bytes()
                    ):
                        continue
                except OSError:
                    pass
            shutil.copy2(source, target)
            copied.append(target)
    return copied


def build_command_env(root: Path) -> dict[str, str]:
    env = os.environ.copy()
    runtime_bin = vendor_runtime_bin(root)
    if runtime_bin is None:
        return env

    runtime_bin_str = str(runtime_bin)
    current_path = env.get("PATH", "")
    path_entries = [entry for entry in current_path.split(os.pathsep) if entry]
    normalized_runtime_bin = os.path.normcase(os.path.normpath(runtime_bin_str))
    normalized_entries = {
        os.path.normcase(os.path.normpath(entry)) for entry in path_entries
    }
    if normalized_runtime_bin not in normalized_entries:
        path_entries.insert(0, runtime_bin_str)
    env["PATH"] = os.pathsep.join(path_entries) if path_entries else runtime_bin_str
    return env


def synced_manifest_path(root: Path) -> Path:
    return root / "vendor" / "ctp" / "bin" / "_synced_from.txt"


def read_synced_manifest(root: Path) -> dict[str, str]:
    manifest_path = synced_manifest_path(root)
    if not manifest_path.exists():
        return {}
    entries: dict[str, str] = {}
    for line in manifest_path.read_text(encoding="utf-8", errors="replace").splitlines():
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        if not key:
            continue
        entries[key] = value.strip()
    return entries


def unique_paths(candidates: list[Path]) -> list[Path]:
    seen: set[str] = set()
    paths: list[Path] = []
    for candidate in candidates:
        normalized = str(candidate.resolve(strict=False)).casefold()
        if normalized in seen:
            continue
        seen.add(normalized)
        paths.append(candidate)
    return paths


def sdk_scan_roots_from_env() -> list[Path]:
    raw = os.environ.get(SDK_SCAN_ROOTS_ENV, "").strip()
    if not raw:
        return []
    candidates: list[Path] = []
    for item in raw.split(os.pathsep):
        value = item.strip()
        if not value:
            continue
        candidates.append(Path(value))
    return unique_paths(candidates)


def is_valid_sdk_dir(path: Path) -> bool:
    return path.is_dir() and all((path / filename).exists() for filename in SDK_REQUIRED_FILES)


def _is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.resolve(strict=False).relative_to(parent.resolve(strict=False))
    except ValueError:
        return False
    return True


def should_skip_sdk_scan_dir(path: Path, scan_root: Path) -> bool:
    temp_root = Path(tempfile.gettempdir())
    if _is_relative_to(scan_root, temp_root):
        return False
    if _is_relative_to(path, temp_root):
        return True
    return False


def find_sdk_dir_under(root: Path) -> Path | None:
    if not root.exists():
        return None
    queue: deque[tuple[Path, int]] = deque([(root, 0)])
    while queue:
        path, depth = queue.popleft()
        if should_skip_sdk_scan_dir(path, root):
            continue
        if is_valid_sdk_dir(path):
            return path
        if depth >= SDK_SEARCH_MAX_DEPTH:
            continue
        try:
            children = list(path.iterdir())
        except OSError:
            continue
        for child in children:
            if child.is_dir():
                queue.append((child, depth + 1))
    return None


def resolve_sdk_dir(candidate: Path) -> Path | None:
    if is_valid_sdk_dir(candidate):
        return candidate
    search_root = candidate / "3rdLib" / "CTP" if (candidate / "3rdLib" / "CTP").exists() else candidate
    return find_sdk_dir_under(search_root)


def external_root_from_synced_manifest(root: Path) -> Path | None:
    manifest = read_synced_manifest(root)
    for raw_path in manifest.values():
        if not raw_path:
            continue
        candidate = Path(raw_path)
        if not candidate.exists():
            continue
        for ancestor in [candidate, *candidate.parents]:
            if (ancestor / "3rdLib" / "CTP").exists():
                return ancestor
    return None


def locate_sdk_dir(root: Path) -> Path | None:
    candidates: list[Path] = []
    for env_key in SDK_ENV_KEYS:
        raw_path = os.environ.get(env_key, "").strip()
        if raw_path:
            candidates.append(Path(raw_path))

    candidates.extend(sdk_scan_roots_from_env())

    candidates.append(root / "vendor" / "ctp" / "sdk")

    external_root = external_root_from_synced_manifest(root)
    if external_root is not None:
        candidates.append(external_root)
        candidates.append(external_root / "3rdLib" / "CTP")

    for candidate in unique_paths(candidates):
        resolved = resolve_sdk_dir(candidate)
        if resolved is not None:
            return resolved
    return None


def print_vendor_bridge_inputs(root: Path, sdk_dir: Path | None) -> None:
    runtime_bin = root / "vendor" / "ctp" / "bin"
    manifest_fields = read_synced_manifest(root)
    pack_kind = manifest_fields.get("pack_kind", "").strip() or "unknown"
    if runtime_bin.exists():
        print(f"INFO rust-gate: runtime-pack={pack_kind} path={runtime_bin}")
    else:
        print(f"INFO rust-gate: runtime-pack=missing path={runtime_bin}")

    for env_key in SDK_ENV_KEYS:
        raw_value = os.environ.get(env_key, "").strip()
        print(f"INFO rust-gate: sdk-probe {env_key}={raw_value or '<unset>'}")

    scan_roots = sdk_scan_roots_from_env()
    raw_scan_roots = os.environ.get(SDK_SCAN_ROOTS_ENV, "").strip()
    print(f"INFO rust-gate: sdk-probe {SDK_SCAN_ROOTS_ENV}={raw_scan_roots or '<unset>'}")
    for scan_root in scan_roots:
        print(f"INFO rust-gate: sdk-scan-root={scan_root}")

    vendor_sdk_root = root / "vendor" / "ctp" / "sdk"
    print(
        "INFO rust-gate: sdk-probe "
        f"vendor/ctp/sdk={vendor_sdk_root} exists={vendor_sdk_root.exists()}"
    )

    external_root = external_root_from_synced_manifest(root)
    if external_root is not None:
        print(f"INFO rust-gate: sdk-probe external_3rdLib_root={external_root}")
    else:
        print("INFO rust-gate: sdk-probe external_3rdLib_root=<not-detected>")

    print("INFO rust-gate: repo-only-probe=python scripts/ctp_repo_debug_smoke.py")
    print(
        "INFO rust-gate: formal-live-verdict="
        "python scripts/ctp_nautilus_live_smoke.py --config <path>"
    )
    if sdk_dir is not None:
        print(f"INFO rust-gate: sdk-selected={sdk_dir}")


def run_command(
    command: list[str], env: dict[str, str] | None = None
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
        env=env,
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

    command_env = build_command_env(root)
    runtime_bin = vendor_runtime_bin(root)
    if runtime_bin is not None:
        print(f"INFO rust-gate: runtime-dll-search={runtime_bin}")

    metadata_command = [
        cargo,
        "metadata",
        "--format-version",
        "1",
        "--no-deps",
        "--manifest-path",
        str(manifest),
    ]
    metadata_result = run_command(metadata_command, env=command_env)
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
    check_result = run_command(check_command, env=command_env)
    if check_result.returncode != 0:
        print("FAIL rust-gate: cargo-check")
        print(f"INFO rust-gate: command={' '.join(check_command)}")
        print_block("STDOUT rust-gate: ", check_result.stdout)
        print_block("STDERR rust-gate: ", check_result.stderr)
        return 1

    print("PASS rust-gate: cargo-check")
    print_block("STDOUT rust-gate: ", check_result.stdout)

    build_command = [cargo, "build", "--manifest-path", str(manifest)]
    build_result = run_command(build_command, env=command_env)
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

    sdk_dir = locate_sdk_dir(root)
    print_vendor_bridge_inputs(root, sdk_dir)
    if sdk_dir is not None:
        print(f"PASS rust-gate: ctp_vendor_bridge-ready sdk_dir={sdk_dir}")
    else:
        print("WARN rust-gate: ctp_vendor_bridge-scaffold-only sdk-not-found")
        synced_manifest = synced_manifest_path(root)
        manifest_fields = read_synced_manifest(root)
        repo_native_mode = manifest_fields.get("repo_native_mode", "").strip()
        if repo_native_mode:
            print(
                f"INFO rust-gate: repo_native_mode={repo_native_mode} "
                f"manifest={synced_manifest}"
            )
        elif synced_manifest.exists():
            print(f"INFO rust-gate: synced-manifest={synced_manifest}")
        print(
            "NEXT rust-gate: provide CTP SDK via CTP_VENDOR_SDK_ROOT / CTP_SDK_ROOT, "
            "vendor/ctp/sdk, or external 3rdLib/CTP root"
        )

    # ── ctp_py PyO3 extension build check ─────────────────────────────────
    ctp_py_manifest = root / "rust" / "ctp_py" / "Cargo.toml"
    if ctp_py_manifest.exists():
        ctp_py_build_command = [cargo, "build", "-p", "ctp_py", "--manifest-path", str(manifest)]
        ctp_py_build_result = run_command(ctp_py_build_command, env=command_env)
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

    synced_runtime_dlls = sync_vendor_runtime_dlls_to_target_dirs(root, build_target_dir)
    if synced_runtime_dlls:
        for copied_path in synced_runtime_dlls:
            print(f"INFO rust-gate: runtime-dll-synced={copied_path}")

    # ── cargo test ────────────────────────────────────────────────────────
    test_command = [cargo, "test", "--manifest-path", str(manifest)]
    test_result = run_command(test_command, env=command_env)
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
