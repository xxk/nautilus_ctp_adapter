use std::collections::VecDeque;
use std::env;
use std::fs;
use std::path::{Path, PathBuf};

fn main() {
    println!("cargo:rustc-check-cfg=cfg(ctp_vendor_bridge)");
    println!("cargo:rerun-if-changed=build.rs");
    println!("cargo:rerun-if-changed=native/ctp_bridge.hpp");
    println!("cargo:rerun-if-changed=native/ctp_vendor_bridge.cpp");
    println!("cargo:rerun-if-env-changed=CTP_VENDOR_SDK_ROOT");
    println!("cargo:rerun-if-env-changed=CTP_SDK_ROOT");

    let manifest_dir =
        PathBuf::from(env::var("CARGO_MANIFEST_DIR").expect("missing CARGO_MANIFEST_DIR"));
    let repo_root = manifest_dir
        .parent()
        .and_then(Path::parent)
        .expect("crate must live under <repo>/rust/<crate>")
        .to_path_buf();
    let synced_from = repo_root
        .join("vendor")
        .join("ctp")
        .join("bin")
        .join("_synced_from.txt");
    println!("cargo:rerun-if-changed={}", synced_from.display());

    let Some(sdk_dir) = locate_sdk_dir(&repo_root, &synced_from) else {
        println!(
            "cargo:warning=CTP SDK not found; building scaffold-only repo-owned ctp_native bridge"
        );
        return;
    };

    cc::Build::new()
        .cpp(true)
        .file("native/ctp_vendor_bridge.cpp")
        .include("native")
        .include(&sdk_dir)
        .flag_if_supported("/std:c++20")
        .flag_if_supported("/EHsc")
        .warnings(false)
        .compile("ctp_vendor_bridge");

    println!("cargo:rustc-cfg=ctp_vendor_bridge");
    println!("cargo:rustc-link-search=native={}", sdk_dir.display());
    println!("cargo:rustc-link-lib=dylib=thostmduserapi_se");
    println!("cargo:rustc-link-lib=dylib=thosttraderapi_se");
    println!(
        "cargo:warning=using CTP SDK directory {}",
        sdk_dir.display()
    );
}

fn locate_sdk_dir(repo_root: &Path, synced_from: &Path) -> Option<PathBuf> {
    let mut candidates: Vec<PathBuf> = ["CTP_VENDOR_SDK_ROOT", "CTP_SDK_ROOT"]
        .into_iter()
        .filter_map(|key| env::var(key).ok())
        .map(|value| PathBuf::from(value.trim()))
        .filter(|path| !path.as_os_str().is_empty())
        .collect();

    candidates.extend(parse_synced_sdk_candidates(repo_root, synced_from));

    if let Some(external_root) = parse_external_root(synced_from) {
        candidates.push(external_root.clone());
        candidates.push(external_root.join("3rdLib").join("CTP"));
    }

    candidates.push(repo_root.join("vendor").join("ctp").join("sdk"));

    let mut seen: Vec<PathBuf> = Vec::new();
    for candidate in candidates {
        if seen.iter().any(|path| path == &candidate) {
            continue;
        }
        seen.push(candidate.clone());

        if let Some(found) = resolve_sdk_dir(&candidate) {
            return Some(found);
        }
    }
    None
}

fn parse_synced_sdk_candidates(repo_root: &Path, synced_from: &Path) -> Vec<PathBuf> {
    let mut candidates = Vec::new();
    let Ok(content) = fs::read_to_string(synced_from) else {
        return candidates;
    };
    for line in content.lines() {
        let Some((_, raw_path)) = line.split_once('=') else {
            continue;
        };
        let trimmed = raw_path.trim();
        if trimmed.is_empty() {
            continue;
        }
        let candidate = resolve_repo_relative_path(repo_root, trimmed);
        if candidate.exists() {
            candidates.push(candidate);
        }
    }
    candidates
}

fn resolve_repo_relative_path(repo_root: &Path, raw_path: &str) -> PathBuf {
    let candidate = PathBuf::from(raw_path);
    if candidate.is_absolute() {
        candidate
    } else {
        repo_root.join(candidate)
    }
}

fn parse_external_root(synced_from: &Path) -> Option<PathBuf> {
    let content = fs::read_to_string(synced_from).ok()?;
    for line in content.lines() {
        let (_, raw_path) = line.split_once('=')?;
        let candidate = PathBuf::from(raw_path.trim());
        if !candidate.exists() {
            continue;
        }
        for ancestor in candidate.ancestors() {
            if ancestor.join("3rdLib").join("CTP").exists() {
                return Some(ancestor.to_path_buf());
            }
        }
    }
    None
}

fn resolve_sdk_dir(candidate: &Path) -> Option<PathBuf> {
    if is_valid_sdk_dir(candidate) {
        return Some(candidate.to_path_buf());
    }

    let search_root = if candidate.join("3rdLib").join("CTP").exists() {
        candidate.join("3rdLib").join("CTP")
    } else {
        candidate.to_path_buf()
    };
    find_sdk_dir_under(&search_root)
}

fn find_sdk_dir_under(root: &Path) -> Option<PathBuf> {
    if !root.exists() {
        return None;
    }

    let mut queue = VecDeque::from([(root.to_path_buf(), 0usize)]);
    while let Some((path, depth)) = queue.pop_front() {
        if is_valid_sdk_dir(&path) {
            return Some(path);
        }
        if depth >= 8 {
            continue;
        }
        let Ok(entries) = fs::read_dir(&path) else {
            continue;
        };
        for entry in entries.flatten() {
            let child = entry.path();
            if child.is_dir() {
                queue.push_back((child, depth + 1));
            }
        }
    }
    None
}

fn is_valid_sdk_dir(path: &Path) -> bool {
    path.join("ThostFtdcMdApi.h").exists()
        && path.join("ThostFtdcTraderApi.h").exists()
        && path.join("ThostFtdcUserApiStruct.h").exists()
        && path.join("thostmduserapi_se.lib").exists()
        && path.join("thosttraderapi_se.lib").exists()
}
