# Readiness Gate 证据 / Evidence A1

**更新日期**：2026-04-11
**状态**：已执行
**change-id**：20260410__live-session-order-query-hardening__vendor-bridge-readiness-and-sdk-handoff
**场景**：A1 Success 1 - gate 能明确报告 vendor-bridge ready 或 scaffold-only

## 执行命令 / Command

```bash
python scripts/check_rust_gate.py
```

## 关键结果 / Key Results

```text
INFO rust-gate: runtime-pack=compat path=D:\Nautilus\nautilus_ctp_adapter\vendor\ctp\bin
INFO rust-gate: sdk-probe CTP_VENDOR_SDK_ROOT=<unset>
INFO rust-gate: sdk-probe CTP_SDK_ROOT=<unset>
INFO rust-gate: sdk-probe CTP_SDK_SCAN_ROOTS=<unset>
INFO rust-gate: sdk-probe vendor/ctp/sdk=D:\Nautilus\nautilus_ctp_adapter\vendor\ctp\sdk exists=False
INFO rust-gate: sdk-probe external_3rdLib_root=<not-detected>
INFO rust-gate: repo-only-probe=python scripts/ctp_repo_debug_smoke.py
INFO rust-gate: formal-live-verdict=python scripts/ctp_nautilus_live_smoke.py --config <path>
WARN rust-gate: ctp_vendor_bridge-scaffold-only sdk-not-found
NEXT rust-gate: provide CTP SDK via CTP_VENDOR_SDK_ROOT / CTP_SDK_ROOT, vendor/ctp/sdk, or external 3rdLib/CTP root
```

## 结论 / Verdict

1. gate 已稳定输出 operator 可读的三类输入信息：runtime pack、SDK probe roots、follow-up entrypoints。
2. 当前环境下 gate 给出的正式结论是 `ctp_vendor_bridge-scaffold-only sdk-not-found`，不是模糊失败。
3. A1 通过口径成立，因为 change 目标要求的是“明确 ready 或 scaffold-only”，而不是必须 ready。