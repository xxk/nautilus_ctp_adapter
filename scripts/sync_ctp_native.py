from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from nautilus_ctp_adapter.native import BOOTSTRAP_MANAGED_DLLS, OPTIONAL_COMPAT_DLLS, REQUIRED_NATIVE_DLLS


BOOTSTRAP_FILES = tuple(("managed", name) for name in BOOTSTRAP_MANAGED_DLLS) + tuple(
    ("native", name) for name in REQUIRED_NATIVE_DLLS + OPTIONAL_COMPAT_DLLS
)


def source_profiles() -> dict[str, dict[str, Path]]:
    return {
        "spec-kit": {
            "managed": Path(r"D:\3.9.3_Spec-Kit\bin\Debug\net9.0"),
            "native": Path(r"D:\3.9.3_Spec-Kit\bin\Debug\net9.0\native\bin"),
        },
        "spec-kit-provider": {
            "managed": Path(r"D:\3.9.3_Spec-Kit\src\providers\CTP\CTPProviderSwig.Tests\bin\Debug\net9.0"),
            "native": Path(r"D:\3.9.3_Spec-Kit\src\providers\CTP\CTPProviderSwig\native\bin"),
        },
        "lean-plugin": {
            "managed": Path(r"D:\3.9.3_Spec-Kit\QuantConnect\LeanWorkspaceRoll\bin\Plugins\Debug\net9.0"),
            "native": Path(r"D:\3.9.3_Spec-Kit\QuantConnect\LeanWorkspaceRoll\bin\Plugins\Debug\net9.0"),
        },
    }


def default_source_roots(profile: str = "spec-kit") -> dict[str, Path]:
    profiles = source_profiles()
    if profile not in profiles:
        raise KeyError(f"unknown profile: {profile}")
    return profiles[profile]


def sync_file(source_dir: Path, target_dir: Path, filename: str) -> Path:
    source = source_dir / filename
    if not source.exists():
        raise FileNotFoundError(f"missing source file: {source}")
    target_dir.mkdir(parents=True, exist_ok=True)
    target = target_dir / filename
    shutil.copy2(source, target)
    return target


def sync_manifest(target_dir: Path, profile: str, source_roots: dict[str, Path]) -> Path:
    target_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = target_dir / "_synced_from.txt"
    lines = [
        f"profile={profile}",
        f"managed={source_roots['managed']}",
        f"native={source_roots['native']}",
    ]
    manifest_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return manifest_path


def verify_target(target_dir: Path) -> list[str]:
    missing: list[str] = []
    for _, filename in BOOTSTRAP_FILES:
        if not (target_dir / filename).exists():
            missing.append(filename)
    return missing


def main() -> int:
    parser = argparse.ArgumentParser(description="Sync the local CTP bootstrap pack into vendor/ctp/bin.")
    parser.add_argument("--profile", default="spec-kit", choices=tuple(source_profiles().keys()))
    parser.add_argument("--managed-source", type=Path, default=None)
    parser.add_argument("--native-source", type=Path, default=None)
    parser.add_argument(
        "--target-dir",
        type=Path,
        default=REPO_ROOT / "vendor" / "ctp" / "bin",
    )
    args = parser.parse_args()

    defaults = default_source_roots(args.profile)
    source_roots = {
        "managed": args.managed_source or defaults["managed"],
        "native": args.native_source or defaults["native"],
    }

    copied: list[Path] = []
    for source_kind, filename in BOOTSTRAP_FILES:
        copied.append(sync_file(source_roots[source_kind], args.target_dir, filename))

    manifest_path = sync_manifest(args.target_dir, args.profile, source_roots)
    missing = verify_target(args.target_dir)
    if missing:
        raise FileNotFoundError(f"missing synced files under {args.target_dir}: {missing}")

    print(f"Synced {len(copied)} files into {args.target_dir}")
    print(manifest_path)
    for path in copied:
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
