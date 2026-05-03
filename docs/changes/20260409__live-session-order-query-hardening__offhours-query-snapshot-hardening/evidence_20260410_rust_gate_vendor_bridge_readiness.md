# Rust Gate Vendor Bridge Readiness Evidence

**日期**：2026-04-10
**用途**：证明 `python scripts/check_rust_gate.py` 现在会在 cargo/build 通过之外，额外显式报告当前是 `ctp_vendor_bridge-ready` 还是 `scaffold-only`，并支持 `CTP_SDK_SCAN_ROOTS` 作为 broad-root SDK 探测入口。

## 1. 执行命令

当前 PowerShell 会话未自动带出 cargo PATH，因此先补齐 `C:\Users\Administrator\.cargo\bin` 后再执行正式 gate：

```powershell
$env:PATH = "$env:USERPROFILE\.cargo\bin;$env:PATH"
python scripts/check_rust_gate.py
```

## 2. 实际输出

```text
PASS rust-gate: cargo-found C:\Users\Administrator\.cargo\bin\cargo.EXE
PASS rust-gate: workspace-members=2 manifest=D:\Nautilus\nautilus_ctp_adapter\rust\Cargo.toml
PASS rust-gate: cargo-check
PASS rust-gate: cargo-build artifact=D:\Nautilus\nautilus_ctp_adapter\rust\target\debug\ctp_native.dll
INFO rust-gate: sdk-probe CTP_VENDOR_SDK_ROOT=<unset>
INFO rust-gate: sdk-probe CTP_SDK_ROOT=<unset>
WARN rust-gate: ctp_vendor_bridge-scaffold-only sdk-not-found
INFO rust-gate: synced-manifest=D:\Nautilus\nautilus_ctp_adapter\vendor\ctp\bin\_synced_from.txt
NEXT rust-gate: provide CTP SDK via CTP_VENDOR_SDK_ROOT / CTP_SDK_ROOT, vendor/ctp/sdk, or external 3rdLib/CTP root
PASS rust-gate: ctp_py-build extension=D:\Nautilus\nautilus_ctp_adapter\rust\target\debug\_ctp_runtime.dll
PASS rust-gate: cargo-test
```

补充：在当前机器上使用

```powershell
$env:PATH = "$env:USERPROFILE\.cargo\bin;$env:PATH"
$env:CTP_SDK_SCAN_ROOTS = 'D:/3.9.3_Spec-Kit;D:/spec-kit;D:/QuantConnect;D:/Nautilus;D:/wt;C:/Users/Administrator'
python scripts/check_rust_gate.py
```

实际仍返回 `WARN rust-gate: ctp_vendor_bridge-scaffold-only sdk-not-found`，说明 broad-root 探测没有找到真实 SDK；同时 system temp 子树不会再被旧 pytest 假 SDK 污染成假阳性。

## 3. 结论

1. `check_rust_gate.py` 不再只是“cargo/build 绿不绿”的粗门禁，而是已经能前置暴露 live vendor bridge readiness。
2. `CTP_SDK_SCAN_ROOTS` 现在可以承接 operator 常用的 broad-root 探测流程，不需要重复手工写长串扫描命令。
3. broad-root 探测会跳过 system temp 子树，避免 pytest 生成的占位 SDK 导致假阳性 `sdk_dir`。
4. 当前机器上的正式结论与 direct TD mainline probe 一致：现在阻塞 A1/A2/A3 的不是 auth/front/credential，而是 `ctp_native.dll` 仍处于 scaffold-only 状态。
5. 后续若 `check_rust_gate.py` 输出 `PASS rust-gate: ctp_vendor_bridge-ready sdk_dir=...`，才值得继续把主要排查重心放回真实 CTP 登录与 query 行为。