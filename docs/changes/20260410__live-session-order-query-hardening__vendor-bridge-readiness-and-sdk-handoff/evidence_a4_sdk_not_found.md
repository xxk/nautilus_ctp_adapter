# SDK 缺失阻塞证据 / Evidence A4

**更新日期**：2026-04-11
**状态**：已执行
**change-id**：20260410__live-session-order-query-hardening__vendor-bridge-readiness-and-sdk-handoff
**场景**：A4 Failure 1 - SDK 缺失时 blocker 明确

## 执行命令 / Command

```bash
python scripts/check_rust_gate.py
```

## 关键结果 / Key Results

1. `CTP_VENDOR_SDK_ROOT=<unset>`。
2. `CTP_SDK_ROOT=<unset>`。
3. `CTP_SDK_SCAN_ROOTS=<unset>`。
4. `vendor/ctp/sdk exists=False`。
5. `external_3rdLib_root=<not-detected>`。
6. gate 明确输出：`WARN rust-gate: ctp_vendor_bridge-scaffold-only sdk-not-found`。
7. gate 明确输出下一步：`provide CTP SDK via CTP_VENDOR_SDK_ROOT / CTP_SDK_ROOT, vendor/ctp/sdk, or external 3rdLib/CTP root`。

## 结论 / Verdict

1. 当前 blocker 已被正式归因为 SDK/live DLL 输入缺失，而不是 auth/front/credential 类问题。
2. A4 通过，因为失败原因已稳定冻结为 `sdk-not-found`，operator 无需再回头猜测根因。