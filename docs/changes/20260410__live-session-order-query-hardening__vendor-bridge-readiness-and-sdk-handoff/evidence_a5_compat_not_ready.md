# Compat Pack 非 Ready 证据 / Evidence A5

**更新日期**：2026-04-11
**状态**：已执行
**change-id**：20260410__live-session-order-query-hardening__vendor-bridge-readiness-and-sdk-handoff
**场景**：A5 Failure 2 - compat runtime pack 不被误认成 live bridge

## 执行命令 / Command

```bash
python scripts/check_rust_gate.py
```

## 关键结果 / Key Results

```text
INFO rust-gate: runtime-pack=compat path=D:\Nautilus\nautilus_ctp_adapter\vendor\ctp\bin
WARN rust-gate: ctp_vendor_bridge-scaffold-only sdk-not-found
```

## 结论 / Verdict

1. 本机已经存在 `vendor/ctp/bin/` compat pack，因此运行时 DLL 搜索路径是可用的。
2. 即便如此，gate 仍明确宣告 `scaffold-only sdk-not-found`，证明 compat pack 不是 live-ready vendor bridge。
3. A5 通过，因为“有 compat pack 但仍非 ready”的边界已被命令级证据冻结。