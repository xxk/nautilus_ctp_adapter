---
change-id: "20260410__live-session-order-query-hardening__vendor-bridge-readiness-and-sdk-handoff"
dependencies:
  hard_blocking:
    - id: "20260409__live-session-order-query-hardening__offhours-query-snapshot-hardening"
      reason: "需要继承当前 C3 对 scaffold-only `ctp_native.dll` 与 `sdk-not-found` 的正式定位证据"
      expected_status: blocked
    - id: "20260410__rust-ctp-runtime-cutover__rust-owned-td-bootstrap-runtime"
      reason: "需要继承 Rust-owned TD bootstrap mainline 与当前 `check_rust_gate.py` 输出口径"
      expected_status: completed
  soft_dependency:
    - id: "20260409__live-session-order-query-hardening__session-window-guardrails-and-runbook"
      reason: "需要把 vendor-bridge readiness 写回 session-window runbook，而不是继续散落在聊天里"
      expected_status: blocked
  blocked_by: []
---

# Vendor Bridge Readiness 与 SDK Handoff 开发计划

**状态**：blocked-completed
**进度**：P1/P2/P3 全部完成；A1-A6 全 pass；C2 解锁条件已冻结写入 topic README；当前保持 blocked handoff 等待私有 SDK/live DLL 输入
**日期**：2026-04-10
**更新日期**：2026-04-11
**范围**：`docs/changes/20260410__live-session-order-query-hardening__vendor-bridge-readiness-and-sdk-handoff/`、`scripts/check_rust_gate.py`、`scripts/README.md`、`docs/topics/live-session-order-query-hardening.md`
**topic-id**：live-session-order-query-hardening
**change-id**：20260410__live-session-order-query-hardening__vendor-bridge-readiness-and-sdk-handoff
**关联 acceptance**：./acceptance.md

## 一、需求简述

1. 把当前 topic 的真实主阻塞从“模糊 live 连接问题”冻结成“vendor bridge / SDK 输入缺口”的正式 child change。
2. 让后续 Autopilot 在 `sdk-not-found` 出现时自动切到同一条 unblock 路线，而不是重复围绕 auth/front/credential 调参。
3. 把 `vendor/ctp/bin` runtime pack、`vendor/ctp/sdk` full SDK、仓外 live `ctp_native.dll` 三类输入边界写成可执行 handoff 口径。
4. 本 change 不要求把私有 SDK 或 live DLL 提交进仓库，只负责把 readiness、缺口和交接证据冻结清楚。

## 二、能力映射 / Capability Mapping

```text
- capability_id: ctp-vendor-bridge-readiness
- capability_name: Vendor bridge readiness / SDK handoff
- long_term_target: /D:/Nautilus/nautilus_ctp_adapter/docs/topics/live-session-order-query-hardening.md
- secondary_targets: /D:/Nautilus/nautilus_ctp_adapter/scripts/README.md
- decision_target: /D:/Nautilus/nautilus_ctp_adapter/scripts/check_rust_gate.py
- affects_long_term_rules: 是
- change_type: 新增规则
```

## 三、AI 执行约束

1. 允许修改：当前 change 三件套、`scripts/check_rust_gate.py`、`scripts/README.md`、当前 topic README。
2. 禁止修改：`vendor/`、仓外私有 SDK、仓外 live `ctp_native.dll`、任何真实交易入口。
3. 当前正式入口优先使用：`python scripts/check_rust_gate.py`、`python scripts/ctp_nautilus_live_smoke.py --config <path>`、`python scripts/ctp_repo_debug_smoke.py`。
4. AI 开始前必须阅读：当前 topic README、C3 `plan.md/acceptance.md`、`scripts/README.md`、`scripts/check_rust_gate.py`。
5. 改完后必须执行：`python scripts/check_topic_docs.py`、`python scripts/check_topic_governance.py --root .`；若触及脚本，再执行 `python -m pytest tests/test_topic_governance.py -q` 或最小 targeted pytest。

## 四、背景与约束

1. 当前 `vendor/ctp/bin` 已具备 compat runtime pack，但 formal TD readiness 仍返回 scaffold-only `-9000`。
2. 当前仓内没有可直接提交的 full SDK，也没有可直接提交的 live vendor-bridge `ctp_native.dll`。
3. 本 change 重点是冻结“什么叫 ready、缺什么算 blocker、拿到私有输入后如何验收”，而不是继续在缺输入时伪造通过。

## 五、设计方案（可选）

1. 把 `check_rust_gate.py` 视为 vendor-bridge readiness 的唯一前置门禁。
2. 把 `ctp_nautilus_live_smoke.py` 视为 formal live TD readiness 的唯一结果面。
3. 把 `ctp_repo_debug_smoke.py` 视为 repo-only bootstrap probe，不再允许它被误解为 live-ready verdict。

## 六、阶段划分（可选）

1. P1：冻结 vendor-bridge 输入矩阵与缺口分类。
2. P2：对齐 gate、formal live smoke 与 repo-only probe 的术语与 operator 说明。
3. P3：冻结 handoff 证据、退出条件与切换到 C2 的触发条件。

## 七、任务清单

| 步骤 | 任务 | 来源 | 修改文件 | 产出 | 验证动作 | 回写目标 | 完成定义 | 状态 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| P1 | 冻结 runtime pack / SDK / live DLL 三类输入边界 | C3 blocker evidence | 当前 change、当前 topic README | readiness matrix、blocked note | `python scripts/check_topic_docs.py` | topic README | 后续不再把 compat pack 误认成 live bridge | 进行中 |
| P2 | 对齐 gate 与 smoke 入口的 operator 术语 | `check_rust_gate.py` + formal smoke | `scripts/check_rust_gate.py`、`scripts/README.md` | 统一 ready/blocker 口径 | `python scripts/check_topic_docs.py`；必要时 `python -m pytest` | `scripts/README.md` | operator 能一眼区分 repo-only / formal-live / vendor-bridge-ready | 进行中 |
| P3 | 冻结 SDK handoff 与 C2 解锁条件 | topic queue | 当前 change 三件套、topic README | unblock checklist、handoff evidence path | `python scripts/check_topic_governance.py --root .` | topic README | 拿到私有输入后可直接进入 C2，不再重新讨论路径 | 已完成 |

## 八、验证动作（可选）

```powershell
python scripts/check_topic_docs.py
python scripts/check_topic_governance.py --root .
python -m pytest tests/test_topic_governance.py -q
```

## 九、完成定义（可选）

### 开发完成

1. vendor-bridge readiness 的唯一门禁、唯一结果面和唯一 repo-only probe 已冻结。
2. SDK/live DLL 缺口不再通过聊天临时解释。
3. 进入 C2 的触发条件已写进 topic queue。

### 交付完成

1. `acceptance.md` 中 handoff/blocker 场景通过。
2. 当前 change bundle 中存在 unblock 证据或明确阻塞说明。
3. topic README 已回写 Autopilot 切换条件。

## 十、长期规则增量摘要 / Long-Term Rule Delta Summary

本次新增长期规则：`check_rust_gate.py` 是 vendor-bridge readiness 的正式前置门禁；`ctp_repo_debug_smoke.py` 不是 live-ready verdict；`ctp_nautilus_live_smoke.py` 才是 formal live readiness 结果面。

## 十一、回写与相关变更 / Write-back & Related Changes

1. 需要回写当前 topic README 的 Autopilot 批次与 unblock 条件。
2. 需要回写 `scripts/README.md` 的 entrypoint 说明。

## 十二、阻塞项（可选）

1. full SDK 或仓外 live `ctp_native.dll` 仍属于私有输入，不在仓内。
2. 若没有私有输入，本 change 只能冻结 handoff 与 blocker，不能伪造 ready 证据。

## 十三、进度记录（可选）

1. 2026-04-10：基于 C3 的正式 evidence，新增 vendor-bridge readiness / SDK handoff child change，作为从 offhours-only 推进到 live order dev loop 的唯一解锁面。
2. 2026-04-10：已复跑 `python scripts/check_rust_gate.py`、`python scripts/ctp_repo_debug_smoke.py` 与 `python scripts/ctp_nautilus_live_smoke.py --config cfgs/local/ctp.live.025292.local.json`；当前 machine 结果稳定为 `compat runtime pack present + sdk-not-found + formal live smoke still scaffold-only`。
3. 2026-04-10：已把 `check_rust_gate.py` 的 operator 输出补齐为 runtime pack、SDK probe roots、repo-only probe 与 formal-live verdict 四类信息；当前先作为 C3 的前置 blocker 说明，待切到 U1 时直接复用。
4. 2026-04-10：已进一步把 broad-root SDK 诊断产品化为 `CTP_SDK_SCAN_ROOTS`，并补齐“跳过 system temp 子树、避免 pytest 假 SDK 假阳性”的规则与回归测试；本机在常用 roots 上复验后仍为 `sdk-not-found`。
5. 2026-04-11：C3 已完成 blocked-closeout，当前 frontier 已正式切到 U1；后续工作面从扩脚本 contract 转为冻结 vendor-bridge readiness、formal live verdict 与 SDK/live DLL handoff checklist。
6. 2026-04-11：已重新执行 `python scripts/check_rust_gate.py` 与 `python scripts/ctp_repo_debug_smoke.py`，把 `runtime-pack=compat`、`sdk-not-found`、`repo_only_debug_bootstrap` 与 blocked handoff 路径分别固化到 A1/A2/A4/A5/A6 evidence。
7. 2026-04-11：已实际运行 `python scripts/ctp_nautilus_live_smoke.py --config cfgs/local/ctp.live.025292.local.json`，输出稳定结构化 payload，当前 machine verdict 为 `md_login_failed`；A3 evidence 已补齐并与 scripts/README、docs/README、startup runbook、session-window runbook 的唯一 formal-live 引用对齐。
