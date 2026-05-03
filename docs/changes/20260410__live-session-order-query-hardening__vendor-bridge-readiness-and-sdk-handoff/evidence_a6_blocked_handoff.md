# Blocked Handoff 证据 / Evidence A6

**更新日期**：2026-04-11
**状态**：已执行
**change-id**：20260410__live-session-order-query-hardening__vendor-bridge-readiness-and-sdk-handoff
**场景**：A6 Boundary 1 - 没有私有输入时允许 blocked 交接

## 当前 frontier / Current Frontier

```text
CURRENT_FRONTIER_OK: active_topic=live-session-order-query-hardening active_change=20260410__live-session-order-query-hardening__vendor-bridge-readiness-and-sdk-handoff queued_topics=0 parked_topics=1 completed_topics=14
ACTIVE_CHANGE: change=20260410__live-session-order-query-hardening__vendor-bridge-readiness-and-sdk-handoff status=in_progress plan=docs/changes/20260410__live-session-order-query-hardening__vendor-bridge-readiness-and-sdk-handoff/plan.md
```

## 已冻结的交接口径 / Frozen Handoff Contract

1. preflight gate 唯一入口：`python scripts/check_rust_gate.py`。
2. repo-only bootstrap 唯一入口：`python scripts/ctp_repo_debug_smoke.py`。
3. formal live readiness 唯一入口：`python scripts/ctp_nautilus_live_smoke.py --config <path>`。
4. 当前 blocker 统一口径：`ctp_vendor_bridge-scaffold-only sdk-not-found`。
5. 当前 unblock 条件：通过 `vendor/ctp/sdk`、`CTP_VENDOR_SDK_ROOT` / `CTP_SDK_ROOT`，或可识别的外部 `3rdLib/CTP` root 提供私有 SDK/live DLL 输入。

## 关联证据 / Linked Evidence

1. `./evidence_a1_gate_contract.md`
2. `./evidence_a2_repo_probe_contract.md`
3. `./evidence_a4_sdk_not_found.md`
4. `./evidence_a5_compat_not_ready.md`

## 结论 / Verdict

1. 即便当前没有私有 SDK/live DLL，change 也已经能给出可复用的 blocked handoff，而不是停留在聊天说明。
2. 后续拿到私有输入后，operator 应直接沿同一条 gate -> formal-live 路径继续，不再重新定义 readiness 规则。
3. A6 通过，因为 blocked 结果已经被文档、脚本入口和 frontier 状态共同固定。