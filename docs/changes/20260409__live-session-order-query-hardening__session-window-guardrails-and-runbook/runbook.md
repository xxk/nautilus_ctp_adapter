# Session-Window Runbook / 交易与非交易时段运行手册

**日期**：2026-04-10
**更新日期**：2026-06-03
**状态**：in_progress
**change-id**：20260409__live-session-order-query-hardening__session-window-guardrails-and-runbook
**关联 plan**：./plan.md
**关联 acceptance**：./acceptance.md

## 一、目标 / Goal

1. 让操作者在不依赖聊天说明的前提下，判断当前应该走 `offhours read-only`、`vendor-bridge handoff` 还是 `trade-window live order`。
2. 把 gate、正式入口、成功信号、失败口径和 next lane 固定成单一路径。

## 二、总入口 / Start Here

每次进入当前 topic，先执行：

```powershell
python scripts/check_rust_gate.py
```

根据输出进入下面三条路径之一。

### 本机默认 live 输入 / Local Default Live Inputs

当本机存在 `C:\Users\Administrator\Desktop\TradingServer_260603.csv`、`C:\Users\Administrator\Desktop\MarketDataServer_260603.csv` 和 `cfgs/local/ctp.live.025292.local.json` 时，默认直接使用这些输入，不再向操作者询问配置。

1. CSV 只提供 front：TD 默认 `tcp://180.168.159.225:51205`，MD 默认 `tcp://180.168.159.225:51213`。
2. 凭据只从 `cfgs/local/ctp.live.025292.local.json` 读取，不写入受版本控制文件，也不在聊天中展开。
3. 运行 live smoke 前，在仓库外生成临时 config，仅覆盖 `Host` 与 `Pricer`，例如 `D:\Nautilus\_tmp\ctp_login_260603\<name>.json`。
4. 标准顺序是 `check_rust_gate.py`、MD login smoke、formal `ctp_nautilus_live_smoke.py`，TD 定位时再跑 `ctp_td_login_smoke.py`。
5. TD login-only 在 Windows 下设置 `PYTHONIOENCODING=utf-8`。
6. 只有上述本机文件缺失时，才报告 `missing_local_config_or_csv_front` blocker；不要在聊天中索要或复述敏感凭据。

## 三、路径 A：Vendor Bridge 未就绪 / Vendor Bridge Not Ready

### 触发条件

出现以下任一信号：

1. `WARN rust-gate: ctp_vendor_bridge-scaffold-only sdk-not-found`
2. `python scripts/ctp_nautilus_live_smoke.py --config <path>` 中 TD 仍返回 scaffold-only `-9000`
3. `login_error_message = repo-owned ctp_native scaffold only; live vendor bridge not implemented`

### 当前允许动作

1. 允许继续阅读和回写文档
2. 允许继续冻结 blocked evidence 与 handoff checklist
3. 允许执行 repo-only probe 与 governance/check 脚本
4. 不允许继续把问题当成 auth/front/credential 调参
5. 不允许进入真实 `--live-send`

### 正式入口

```powershell
python scripts/check_rust_gate.py
python scripts/ctp_repo_debug_smoke.py
python scripts/ctp_nautilus_live_smoke.py --config <path>
```

### 对应 change

1. 当前 active change 已是 [20260410__live-session-order-query-hardening__vendor-bridge-readiness-and-sdk-handoff](../20260410__live-session-order-query-hardening__vendor-bridge-readiness-and-sdk-handoff/plan.md)
2. [20260409__live-session-order-query-hardening__offhours-query-snapshot-hardening](../20260409__live-session-order-query-hardening__offhours-query-snapshot-hardening/plan.md) 已完成 blocked-closeout，offhours 只读 contract 保持可复用，但不再是当前 active lane。

## 四、路径 B：非交易时段只读开发 / Offhours Read-Only

### 进入条件

1. 当前不是交易时段，或当前明确只允许 read-only
2. 不需要触发任何真实交易副作用
3. 若 gate 仍是 scaffold-only，则只允许做 blocked-closeout、evidence 收集和 handoff，不再重复追 auth/front

### 推荐顺序

```powershell
python scripts/ctp_query_adapter_smoke.py --config <path> --timeout-seconds 20 --completion-grace-seconds 1.0
python scripts/ctp_reconciliation_snapshot_smoke.py --config <path> --timeout-seconds 20 --completion-grace-seconds 1.0
python scripts/ctp_td_merged_reconciliation_policy_smoke.py --config <path> --timeout-seconds 20 --completion-grace-seconds 1.0 --observation-grace-seconds 1.5
python scripts/ctp_position_query_smoke.py --config <path> --timeout-seconds 20 --completion-grace-seconds 1.0
```

### 成功信号

1. `baseline / success / failure_reason` 输出齐全
2. 空仓边界与失败边界能区分
3. `read-only` 入口不会接受 `--live-send`

### 对应 change

当前正式落点是 [20260409__live-session-order-query-hardening__offhours-query-snapshot-hardening](./../20260409__live-session-order-query-hardening__offhours-query-snapshot-hardening/plan.md)

## 五、路径 C：交易时段真实开发 / Trade-Window Live Order

### 进入前提

必须同时满足：

1. `python scripts/check_rust_gate.py` 不再报 `sdk-not-found`
2. 当前处于交易时段
3. 当前净持仓未突破 `5` 手上限
4. 本地 live config 已准备好

### 推荐顺序

```powershell
python scripts/ctp_td_order_truth_smoke.py --config <path> --timeout-seconds 20
python scripts/ctp_order_lifecycle_smoke.py --config <path> --instrument c2609 --quantity 1 --side <BUY|SELL> --limit-price <price> --client-order-id <id> --live-send --timeout-seconds 20
```

### 强约束

1. 只允许 `c2609`
2. 单笔只允许 `1` 手
3. 净持仓上限 `5` 手
4. A1 preflight 不通过时，不得执行 A2 live-send

### 对应 change

当前正式落点是 [20260410__live-session-order-query-hardening__c2609-live-order-dev-loop](./../20260410__live-session-order-query-hardening__c2609-live-order-dev-loop/plan.md)

## 六、Repo-Only 诊断说明 / Repo-Only Probe Note

```powershell
python scripts/ctp_repo_debug_smoke.py
```

1. 这是 repo-only bootstrap probe，不是 formal live readiness verdict
2. 这里看到 TD `-9000` 仍是 expected scaffold contract
3. 正式 live 结论始终看：

```powershell
python scripts/ctp_nautilus_live_smoke.py --config <path>
```

## 七、当前自动推进规则 / Current Autopilot Rule

1. 当前 active lane 已是 U1
2. 当 gate 与 formal live smoke 继续稳定指向 `sdk-not-found / scaffold-only` 时，继续留在 U1 blocked handoff，不再回退到 C3
3. 只有 U1 明确 ready/handoff 条件后，才进入 C2
4. C4 只在 C1/C3/U1/C2 都已有可引用证据后再收口
