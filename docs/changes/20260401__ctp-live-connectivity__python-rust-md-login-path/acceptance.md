# Python Rust 主线 MD 登录路径 验收方案

**模板标识 / Template Marker**：standard
**变更目录 / Change Root**：./
**状态**：✅ 已完成
**日期**：2026-04-01
**范围**：`rust/ctp_runtime_core/`、`src/nautilus_ctp_adapter/runtime/`、`src/nautilus_ctp_adapter/adapters/ctp/data_client.py`
**change-id**：20260401__ctp-live-connectivity__python-rust-md-login-path
**关联 plan**：./plan.md
**关联 ai_constraints**：./ai_constraints.md
**长期归宿 / Long-Term Target**：/D:/Nautilus/nautilus_ctp_adapter/docs/architecture/rust-python-adapter-split.md

<!-- AI-STATUS-BEGIN -->
```yaml
conclusion: passed
allow_declare_pass: true
last_updated: "2026-04-02 19:20"
concluded_by: "Codex"

exit_conditions:
  E1_success_scenarios: passed
  E2_failure_scenarios: passed
  E3_verification_cmds: passed
  E4_evidence_collected: passed
  E5_real_acceptance_only: passed
  E6_minimum_scenarios: passed

scenarios:
  A1: { exec: true, result: pass, blocking: true }
  A2: { exec: true, result: pass, blocking: true }
  A3: { exec: true, result: pass, blocking: true }
  A4: { exec: true, result: pass, blocking: true }
  A5: { exec: true, result: pass, blocking: true }
  A6: { exec: true, result: pass, blocking: false }
```
<!-- AI-STATUS-END -->

## 一、验收目标 / Goals

1. 证明真实 MD 登录与订阅已迁回 Python/Rust 主线
2. 证明后续 Nautilus 数据侧 topic 可直接复用这条主线

## 二、当前已继承事实 / Current Inherited Facts

1. `20260401__ctp-live-connectivity__repo-owned-ctpnative-wrapper-bootstrap` 已完成，可作为本 change 的稳定前置。
2. `20260401__ctp-live-connectivity__login-025292-and-subscribe-rb2610` 已证明 `rb2610` 行情能通过临时路径收到，但这还不能替代本 change 的主线验收。
3. 本 change 当前的真正目标是把同一条 MD 登录与订阅路径迁回 Python/Rust 主线，并把证据留在当前 bundle，而不是复用 C1 的临时宿主证据直接宣告通过。

## 五、验收场景 / Scenarios

| # | 场景 | 执行命令/步骤 | 预期结果 | 成功信号 | 失败口径 | 证据路径 |
| --- | --- | --- | --- | --- | --- | --- |
| A1 | Success 1: 主线 MD connect/login 成立 | `python scripts\ctp_md_login_smoke.py --config <local>` | Python/Rust 主线能触发 MD 登录 | 看到主线登录成功信号 | 仍依赖临时宿主链路 | `evidence_20260402_python_md_login_smoke.md` |
| A2 | Success 2: `rb2610` 订阅成功 | `python scripts\ctp_md_login_smoke.py --config <local>` | 主线订阅 `rb2610` | 至少一条 `rb2610` 事件 | 订阅无事件 | `evidence_20260402_python_md_subscribe_smoke.md` |
| A3 | Success 3: 事件能进入 adapter 边界 | `python scripts\ctp_md_login_smoke.py --config <local>` | 行情事件可被 adapter 消费 | bridge -> adapter 路径清晰 | 仍停在 raw callback | `evidence_20260402_python_md_subscribe_smoke.md` |
| A4 | Failure 1: 登录失败口径清晰 | 缺配置或错误前置 | 错误可诊断 | 缺少字段/登录失败可定位 | 错误模糊 | 当前 change |
| A5 | Failure 2: 订阅失败口径清晰 | 当前记录 `MdSubscribe` ABI 未冻结 | 失败可归因 | 明确标注“不能再猜签名” | 失败静默 | `evidence_20260402_python_md_login_smoke.md` |
| A6 | Boundary 1: 不提前做完整 LiveDataClient | 对照 scope | 本 change 不越界 | 仅建立主线，不偷做 Topic 3 | 范围失控 | 当前 change |

## 六、证据清单 / Evidence

| # | 证据类型 | 路径/链接 | 说明 |
| --- | --- | --- | --- |
| 1 | 上游前置完成事实 | `/D:/Nautilus/nautilus_ctp_adapter/docs/changes/20260401__ctp-live-connectivity__repo-owned-ctpnative-wrapper-bootstrap/acceptance.md` | 证明 native 边界已冻结 |
| 2 | 继承的临时行情证据 | `/D:/Nautilus/nautilus_ctp_adapter/docs/changes/20260401__ctp-live-connectivity__login-025292-and-subscribe-rb2610/rb2610_md_smoke_20260401.log` | 只能作为 inherited evidence，不能替代主线通过证据 |
| 3 | 当前 change 主线登录证据 | `/D:/Nautilus/nautilus_ctp_adapter/docs/changes/20260401__ctp-live-connectivity__python-rust-md-login-path/evidence_20260402_python_md_login_smoke.md` | Python 主线直连 `ctp_native.dll` 的 MD login 证据 |
| 4 | 当前 change 主线订阅证据 | `/D:/Nautilus/nautilus_ctp_adapter/docs/changes/20260401__ctp-live-connectivity__python-rust-md-login-path/evidence_20260402_python_md_subscribe_smoke.md` | Python 主线 `rb2610` tick 与 bridge 证据 |

## 七、当前阻塞 / Current Blocking Gap

1. 当前 change 的主路径、失败路径和 bridge 证据已收齐。

## 八、最终结论 / Final Verdict

- **结论**：✅ 已完成
- **建议**：可宣告通过，并进入 `C4`
- **说明**：当前 verdict 只代表 C3 bundle 状态，不代表 Topic 1 已关闭。
