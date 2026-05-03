# A6 Empty Positions Boundary Evidence

**日期**：2026-04-10
**状态**：🟨 code-contract locked, live execution blocked
**对应场景**：A6 Boundary 1: 空仓不等于查询失败

## 1. 本轮修复点

1. TD position callback 现在正式透传 `request_id/is_last`，不再只依赖“是否收到了 position payload”。
2. `run_live_position_query_smoke()` 现在以 `positions_complete` 作为完成判定来源；当 CTP 返回 `is_last=true` 且没有任何 position record 时，会被识别成“空仓但查询成功完成”。
3. `ctp_position_query_smoke.py` 的结构化 JSON contract 已用脚本级回归测试锁定：`query_code=0`、`completed=true`、`no_positions=true` 时，`success=true`、`failure_reason=null`。

## 2. 本地 contract / function 验证

```powershell
python -m pytest tests/test_smoke_import.py -k "empty_snapshot_as_completed or empty_positions_as_success_structured_json" -q
```

预期口径：

1. execution client 层：空仓完成不再返回 `timed_out=true`。
2. CLI 层：`no_positions=true` 不再被包装成失败语义。

## 3. 真实 live evidence 为什么仍未执行

1. 当前正式前置 gate 仍输出：`WARN rust-gate: ctp_vendor_bridge-scaffold-only sdk-not-found`。
2. direct TD mainline probe 已证明本机 `ctp_native.dll` 仍是 scaffold-only，而不是可用的 live vendor bridge。
3. 在这个前提下直接跑 A6，无法把“真实空仓”与“bridge 根本未接通”做出可信区分，因此本轮不把 live run 伪装成正式通过。

相关 blocker evidence：

1. `./evidence_20260410_rust_gate_vendor_bridge_readiness.md`
2. `./evidence_20260410_td_mainline_scaffold_probe.md`

## 4. 当前结论

1. A6 的代码主线已经补到位：空仓完成信号可穿透到 Python / CLI。
2. A6 的正式 live evidence 仍待 `check_rust_gate.py` 进入 `ctp_vendor_bridge-ready` 后再执行。
3. 当前不再允许把“空仓”与“position query timeout”混成一个语义。