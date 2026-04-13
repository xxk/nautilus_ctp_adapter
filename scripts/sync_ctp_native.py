from __future__ import annotations

import argparse
from collections.abc import Iterable
import shutil
import site
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from nautilus_ctp_adapter.native import (
    BOOTSTRAP_MANAGED_DLLS,
    OPTIONAL_COMPAT_DLLS,
    REQUIRED_NATIVE_DLLS,
    find_repo_owned_native_dll,
)


RUNTIME_VENDOR_DLLS = tuple(name for name in REQUIRED_NATIVE_DLLS if name != "ctp_native.dll")
PACK_REQUIREMENTS = {
    "runtime": {
        "ctp_api": RUNTIME_VENDOR_DLLS,
        "optional_ctp_api": OPTIONAL_COMPAT_DLLS,
    },
    "compat": {
        "repo_native": ("ctp_native.dll",),
        "ctp_api": RUNTIME_VENDOR_DLLS,
        "optional_ctp_api": OPTIONAL_COMPAT_DLLS,
    },
    "full": {
        "repo_native": ("ctp_native.dll",),
        "ctp_api": RUNTIME_VENDOR_DLLS,
        "optional_ctp_api": OPTIONAL_COMPAT_DLLS,
        "managed": BOOTSTRAP_MANAGED_DLLS,
    },
}


def source_profiles() -> dict[str, dict[str, Path]]:
    return {
        "auto": {},
        "spec-kit": {
            "managed": Path(r"D:\3.9.3_Spec-Kit\bin\Debug\net9.0"),
            "repo_native": Path(r"D:\3.9.3_Spec-Kit\bin\Debug\net9.0\native\bin"),
            "ctp_api": Path(r"D:\3.9.3_Spec-Kit\bin\Debug\net9.0\native\bin"),
        },
        "spec-kit-provider": {
            "managed": Path(r"D:\3.9.3_Spec-Kit\src\providers\CTP\CTPProviderSwig.Tests\bin\Debug\net9.0"),
            "repo_native": Path(r"D:\3.9.3_Spec-Kit\src\providers\CTP\CTPProviderSwig\native\bin"),
            "ctp_api": Path(r"D:\3.9.3_Spec-Kit\src\providers\CTP\CTPProviderSwig\native\bin"),
        },
        "lean-plugin": {
            "managed": Path(r"D:\3.9.3_Spec-Kit\QuantConnect\LeanWorkspaceRoll\bin\Plugins\Debug\net9.0"),
            "repo_native": Path(r"D:\3.9.3_Spec-Kit\QuantConnect\LeanWorkspaceRoll\bin\Plugins\Debug\net9.0"),
            "ctp_api": Path(r"D:\3.9.3_Spec-Kit\QuantConnect\LeanWorkspaceRoll\bin\Plugins\Debug\net9.0"),
        },
    }


def default_source_roots(profile: str = "spec-kit") -> dict[str, Path]:
    profiles = source_profiles()
    if profile not in profiles:
        raise KeyError(f"unknown profile: {profile}")
    return profiles[profile]


def unique_paths(paths: Iterable[Path]) -> list[Path]:
    unique: list[Path] = []
    seen: set[str] = set()
    for path in paths:
        key = str(path)
        if key in seen:
            continue
        seen.add(key)
        unique.append(path)
    return unique


def classify_repo_native_source(source_dir: Path | None) -> str:
    if source_dir is None:
        return ""
    normalized_parts = tuple(part.lower() for part in source_dir.parts)
    if "rust" in normalized_parts and "target" in normalized_parts:
        return "repo_build_requires_sdk_for_live"
    return "external_or_unknown"


def current_python_site_roots() -> list[Path]:
    roots: list[Path] = []
    try:
        roots.extend(Path(raw) for raw in site.getsitepackages())
    except AttributeError:
        pass

    try:
        roots.append(Path(site.getusersitepackages()))
    except AttributeError:
        pass

    return unique_paths(path for path in roots if path.exists())


def discover_dir_with_files(
    search_roots: Iterable[Path],
    required_files: tuple[str, ...],
    *,
    preferred_tokens: tuple[str, ...] = (),
) -> Path | None:
    required = tuple(required_files)
    if not required:
        return None

    candidates: list[Path] = []
    candidate_keys: set[str] = set()
    probe_filename = required[0]
    for root in unique_paths(path for path in search_roots if path.exists() and path.is_dir()):
        for match in root.rglob(probe_filename):
            candidate = match.parent
            key = str(candidate)
            if key in candidate_keys:
                continue
            if all((candidate / filename).exists() for filename in required):
                candidate_keys.add(key)
                candidates.append(candidate)

    if not candidates:
        return None

    def rank(path: Path) -> tuple[int, int, str]:
        lower = str(path).lower()
        preferred = 0 if all(token in lower for token in preferred_tokens) else 1
        return (preferred, len(path.parts), lower)

    return sorted(candidates, key=rank)[0]


def discover_repo_native_source(search_roots: Iterable[Path]) -> Path | None:
    repo_owned = find_repo_owned_native_dll(REPO_ROOT)
    if repo_owned is not None:
        return repo_owned.parent
    return discover_dir_with_files(search_roots, ("ctp_native.dll",), preferred_tokens=("rust", "target"))


def discover_ctp_api_source(search_roots: Iterable[Path]) -> Path | None:
    return discover_dir_with_files(
        [*current_python_site_roots(), *search_roots],
        RUNTIME_VENDOR_DLLS,
        preferred_tokens=("vnpy_ctp", "api"),
    )


def discover_managed_source(search_roots: Iterable[Path]) -> Path | None:
    return discover_dir_with_files(
        search_roots,
        BOOTSTRAP_MANAGED_DLLS,
        preferred_tokens=("ctpproviderswig",),
    )


def required_files_for_pack(pack_kind: str) -> list[tuple[str, str]]:
    requirements = PACK_REQUIREMENTS[pack_kind]
    pairs: list[tuple[str, str]] = []
    for source_key in ("repo_native", "ctp_api", "managed"):
        for filename in requirements.get(source_key, ()):  # type: ignore[arg-type]
            pairs.append((source_key, filename))
    return pairs


def optional_files_for_pack(pack_kind: str) -> list[tuple[str, str]]:
    return [("ctp_api", filename) for filename in PACK_REQUIREMENTS[pack_kind].get("optional_ctp_api", ())]  # type: ignore[arg-type]


def sync_file(source_dir: Path, target_dir: Path, filename: str) -> Path:
    source = source_dir / filename
    if not source.exists():
        raise FileNotFoundError(f"missing source file: {source}")
    target_dir.mkdir(parents=True, exist_ok=True)
    target = target_dir / filename
    if target.exists() and source.resolve(strict=False) == target.resolve(strict=False):
        return target
    shutil.copy2(source, target)
    return target


def sync_manifest(
    target_dir: Path,
    *,
    profile: str,
    pack_kind: str,
    source_roots: dict[str, Path | None],
    scan_roots: list[Path],
) -> Path:
    target_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = target_dir / "_synced_from.txt"
    lines = [
        f"profile={profile}",
        f"pack_kind={pack_kind}",
        f"repo_native={source_roots['repo_native'] or ''}",
        f"repo_native_mode={classify_repo_native_source(source_roots['repo_native'])}",
        f"ctp_api={source_roots['ctp_api'] or ''}",
        f"managed={source_roots['managed'] or ''}",
    ]
    lines.extend(f"scan_root={root}" for root in scan_roots)
    manifest_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return manifest_path


def verify_target(target_dir: Path, *, pack_kind: str) -> list[str]:
    missing: list[str] = []
    for _, filename in required_files_for_pack(pack_kind):
        if not (target_dir / filename).exists():
            missing.append(filename)
    return missing


def resolve_source_roots(
    *,
    profile: str,
    pack_kind: str,
    native_source: Path | None,
    repo_native_source: Path | None,
    ctp_api_source: Path | None,
    managed_source: Path | None,
    scan_roots: Iterable[Path],
) -> tuple[dict[str, Path | None], list[Path]]:
    defaults = default_source_roots(profile)
    shared_native_source = native_source or defaults.get("native")
    normalized_scan_roots = unique_paths(Path(path) for path in scan_roots)
    source_roots: dict[str, Path | None] = {
        "repo_native": repo_native_source or defaults.get("repo_native") or shared_native_source,
        "ctp_api": ctp_api_source or defaults.get("ctp_api") or shared_native_source,
        "managed": managed_source or defaults.get("managed"),
    }

    if source_roots["ctp_api"] is None:
        source_roots["ctp_api"] = discover_ctp_api_source(normalized_scan_roots)
    if pack_kind in {"compat", "full"} and source_roots["repo_native"] is None:
        source_roots["repo_native"] = discover_repo_native_source(normalized_scan_roots)
    if pack_kind == "full" and source_roots["managed"] is None:
        source_roots["managed"] = discover_managed_source(normalized_scan_roots)

    return source_roots, normalized_scan_roots


def require_source_dir(source_roots: dict[str, Path | None], source_key: str, filenames: tuple[str, ...]) -> Path:
    source_dir = source_roots.get(source_key)
    if source_dir is not None:
        return source_dir

    hint_map = {
        "repo_native": "--repo-native-source, --native-source, or a repo build under rust/target",
        "ctp_api": "--ctp-api-source, --native-source, or --scan-root pointing at a vnpy_ctp/api runtime",
        "managed": "--managed-source or --scan-root pointing at a legacy managed bootstrap pack",
    }
    raise FileNotFoundError(
        f"missing {source_key} source directory for {list(filenames)}; provide {hint_map[source_key]}"
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Sync the local CTP runtime/bootstrap pack into vendor/ctp/bin or another target directory."
    )
    parser.add_argument("--profile", default="auto", choices=tuple(source_profiles().keys()))
    parser.add_argument("--pack-kind", default="runtime", choices=tuple(PACK_REQUIREMENTS.keys()))
    parser.add_argument("--managed-source", type=Path, default=None)
    parser.add_argument("--native-source", type=Path, default=None)
    parser.add_argument("--repo-native-source", type=Path, default=None)
    parser.add_argument("--ctp-api-source", type=Path, default=None)
    parser.add_argument("--scan-root", type=Path, action="append", default=[])
    parser.add_argument(
        "--target-dir",
        type=Path,
        default=REPO_ROOT / "vendor" / "ctp" / "bin",
    )
    args = parser.parse_args()

    source_roots, scan_roots = resolve_source_roots(
        profile=args.profile,
        pack_kind=args.pack_kind,
        native_source=args.native_source,
        repo_native_source=args.repo_native_source,
        ctp_api_source=args.ctp_api_source,
        managed_source=args.managed_source,
        scan_roots=args.scan_root,
    )

    copied: list[Path] = []
    for source_key, filename in required_files_for_pack(args.pack_kind):
        source_dir = require_source_dir(source_roots, source_key, tuple(name for key, name in required_files_for_pack(args.pack_kind) if key == source_key))
        copied.append(sync_file(source_dir, args.target_dir, filename))

    ctp_api_dir = source_roots.get("ctp_api")
    if ctp_api_dir is not None:
        for _, filename in optional_files_for_pack(args.pack_kind):
            source_file = ctp_api_dir / filename
            if source_file.exists():
                copied.append(sync_file(ctp_api_dir, args.target_dir, filename))

    manifest_path = sync_manifest(
        args.target_dir,
        profile=args.profile,
        pack_kind=args.pack_kind,
        source_roots=source_roots,
        scan_roots=scan_roots,
    )
    missing = verify_target(args.target_dir, pack_kind=args.pack_kind)
    if missing:
        raise FileNotFoundError(f"missing synced files under {args.target_dir}: {missing}")

    repo_native_mode = classify_repo_native_source(source_roots.get("repo_native"))
    if repo_native_mode == "repo_build_requires_sdk_for_live":
        print(
            "WARNING: repo-built ctp_native.dll is scaffold-only unless it was built with a detected CTP SDK/vendor bridge; "
            "this pack is not sufficient for real live smoke by itself."
        )

    print(f"Synced {len(copied)} files into {args.target_dir} ({args.pack_kind})")
    print(manifest_path)
    for path in copied:
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
