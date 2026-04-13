# Rust-Owned TD Bootstrap Runtime 验收方案 / Acceptance Plan

**模板标识 / Template Marker**：standard
**变更目录 / Change Root**：./
**状态**：✅ 已验收
**日期**：2026-04-10
**范围**：TD bootstrap/readiness PyO3 mainline
**change-id**：20260410__rust-ctp-runtime-cutover__rust-owned-td-bootstrap-runtime
**关联 plan**：./plan.md
**关联 ai_constraints**：./ai_constraints.md
**长期归宿 / Long-Term Target**：/D:/Nautilus/nautilus_ctp_adapter/docs/topics/rust-ctp-runtime-cutover.md

<!-- AI-STATUS-BEGIN -->
```yaml
conclusion: passed
allow_declare_pass: true
last_updated: "2026-04-10"
concluded_by: "GitHub Copilot"

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

## 总览看板 / Dashboard

### 验收总状态 / Overall

| 项目 | 值 | 说明 |
| --- | :---: | --- |
| 验收结论 | ✅ 已验收 | 由 `AI-STATUS conclusion` 派生 |
| AI 建议宣告通过 | 是 | 由 `AI-STATUS allow_declare_pass` 派生 |
| 最后更新 | 2026-04-10 | |
| AI 执行人 | GitHub Copilot | |

### 出口条件 / Exit Criteria

| # | 出口条件 | 状态 | 判定规则 | 证据 |
| --- | --- | :---: | --- | --- |
| E1 | 关键成功场景全部通过 | ✅ | 阻塞成功场景全部 ✅ | A1-A3 |
| E2 | 关键失败场景符合预期 | ✅ | 阻塞失败场景全部 ✅ | A4-A5 |
| E3 | 必跑验证命令已完成 | ✅ | `plan.md` 中声明的必跑命令已执行 | `check_rust_gate.py`; `ctp_repo_debug_smoke.py`; `pytest tests/ -q` |
| E4 | 关键证据已留存 | ✅ | 当前 change bundle 中存在证据与 closeout notes | 当前 acceptance + `plan.md` |
| E5 | 正式验收不依赖 mock 或 test | ✅ | 正式结论以主路径源码与真实验证命令为准 | `execution_client.py` 主路径已切到 PyO3 |
| E6 | 正式场景数不少于 6 个 | ✅ | 少于 6 个时必须存在明确豁免说明 | A1-A6 共 6 个 |

### 场景看板 / Scenario Board

| # | 场景 | 执行 | 结论 | 阻塞 | 证据/备注 |
| --- | --- | :---: | :---: | :---: | --- |
| A1 | Success 1: TD bootstrap/readiness 主路径切到 PyO3 internal live session | ✅ | ✅ | 是 | `run_live_td_readiness_smoke()` 已通过 `_create_td_live_session()` 构造 internal `CtpTdLiveSession` |
| A2 | Success 2: internal TD live session 能驱动 login/disconnect callback 与 settlement confirmed event | ✅ | ✅ | 是 | 新增 PyO3 TD contract tests 通过 |
| A3 | Success 3: Rust gate、repo debug smoke 与全量 pytest 继续通过 | ✅ | ✅ | 是 | `check_rust_gate.py` PASS；`ctp_repo_debug_smoke.py` PASS；`94 passed` |
| A4 | Failure 1: public TD scaffold contract 继续冻结在 `-9000/-9001` | ✅ | ✅ | 是 | public `CtpTdSession` 未被本 change 破坏 |
| A5 | Failure 2: 缺 bridge 时 fail-fast，不静默 fallback 到 ctypes | ✅ | ✅ | 是 | `run_live_td_readiness_smoke_fails_fast_when_pyo3_td_bridge_unavailable` |
| A6 | Boundary 1: query/account smoke 在保留 ctypes 查询 callback 验证时，对齐新的 PyO3 bootstrap 口径 | ✅ | ✅ | 否 | position/account query smoke tests 已改为同时 mock PyO3 bootstrap factory |

## 一、验收目标 / Goals

1. TD bootstrap/readiness 主路径切到 PyO3 internal live session。
2. execution guardrails 与 host glue 口径不退化。
3. gate 与 pytest 继续通过。

## 二、验收范围 / Scope

### 覆盖（In Scope）

1. `rust/ctp_py/src/lib.rs` 中 internal `CtpTdLiveSession` 的 create/init/authenticate/login/confirm_settlement/dispose 与 callback bridge。
2. `bootstrap_live_execution_client_mainline()`、`run_live_td_readiness_smoke()` 的正式主调用链。
3. 与之直接相关的 contract tests、repo debug smoke、current change docs 回填。

### 不覆盖（Out of Scope）

1. 真实 order send cutover。
2. position/account/order-truth 全量 consumer 切桥。
3. public `CtpTdSession` scaffold 对外 API 语义调整。

## 三、前置条件 / Prerequisites

| 条件 | 类型 | 阻断开发 | 阻断验收 | 状态 | 备注 |
| --- | --- | :---: | :---: | :---: | --- |
| C2 已验收 | 治理 | 是 | 是 | ✅ | MD PyO3 mainline 已完成 |
| `python scripts/check_rust_gate.py` 可运行 | 工具 | 是 | 是 | ✅ | 本次已验证通过 |
| editable install 可导入 `_ctp_runtime` | 工具 | 否 | 是 | ✅ | `ctp_repo_debug_smoke.py` 已验证 |

## 四、验收专属 AI 边界 / Acceptance-Only AI Boundaries

1. 不得把 ctypes fallback 写成“自动兜底成功”。
2. public scaffold contract 不是本 change 的 live cutover 对象，不得借此掩盖主路径是否已切换。
3. 正式通过前，必须能指出 `execution_client` 的 TD readiness mainline 已不再直接使用 `CtpTdApi`。

## 五、验收场景 / Scenarios

| # | 场景 | 执行命令/步骤 | 预期结果 | 成功信号 | 失败口径 | 证据路径 |
| --- | --- | --- | --- | --- | --- | --- |
| A1 | TD readiness 主路径改为 PyO3 | 代码检查 + targeted pytest | `run_live_td_readiness_smoke()` 不再走 `CtpTdApi` | 主路径通过 factory 构造 `CtpTdLiveSession` | 仍直接走 ctypes bootstrap | `tests/test_smoke_import.py` |
| A2 | PyO3 TD callback bridge 生效 | 运行相关 tests | login/disconnect 回调与 settlement event 可达 | runtime bridge 继续收到 `LOGIN_SUCCEEDED`、`SETTLEMENT_CONFIRMED` | callback 不达或顺序漂移 | `pytest -k run_live_td_readiness_smoke_uses_pyo3_td_live_session_mainline` |
| A3 | 门禁不退化 | `python scripts/check_rust_gate.py`; `python scripts/ctp_repo_debug_smoke.py`; `python -m pytest tests/ -q` | 全部通过 | rust gate pass + repo debug smoke pass + `94 passed` | 任一失败 | 终端输出 |
| A4 | public scaffold contract 保持冻结 | contract tests | 仍返回 `-9000/-9001` | public `CtpTdSession` contract tests 继续通过 | scaffold 语义被提前改写 | `pytest -k pyo3_bridge_td_session_scaffold_contract` |
| A5 | 缺 bridge 时 fail-fast | contract tests | 抛出 RuntimeError | 不 fallback 到 ctypes | 静默挂起或 fallback | `pytest -k run_live_td_readiness_smoke_fails_fast_when_pyo3_td_bridge_unavailable` |
| A6 | 查询 smoke 对齐新 bootstrap 口径 | targeted/full pytest | query smoke 继续通过 | position/account tests 通过 | query smoke 因 bootstrap drift 回归 | `pytest tests/test_smoke_import.py -q` |

## 六、证据清单 / Evidence

| # | 证据类型 | 路径/链接 | 说明 |
| --- | --- | --- | --- |
| 1 | gate 输出 | 本次执行结果 | `PASS rust-gate: ctp_py-build extension=..._ctp_runtime.dll` |
| 2 | repo debug smoke | 本次执行结果 | scaffold snapshot 保持稳定，public TD scaffold 仍为 `-9000` |
| 3 | pytest 输出 | 本次执行结果 | `94 passed in 1.27s` |
| 4 | contract tests | `tests/test_smoke_import.py` | 新增 TD PyO3 mainline / fail-fast / query bootstrap 对齐测试 |

## 七、未通过处理 / On Failure

1. 回退到 `plan.md` 重新制定修复计划。
2. 不得用 fallback 或临时 mock 掩盖 PyO3 TD mainline 未完成。

## 八、豁免说明 / Scenario Waiver

本 change 维持 6 个正式场景，无豁免。

## 九、真实验收待办清单 / Pending E2E Checklist

| # | 对应场景 | 当前阶段结果 | 还缺的真实验证 | 真实入口/命令 | 通过信号 | 阻塞项 | 证据路径 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| R1 | A1-A6 | 已完成 | 无 | `python scripts/check_rust_gate.py`; `python scripts/ctp_repo_debug_smoke.py`; `python -m pytest tests/ -q` | 三者全绿 | 无 | 当前 acceptance |

## 十、Contract/Function 锁定证据（可选）

| 项目 | 路径/命令 | 说明 |
| --- | --- | --- |
| Contract 锁定 | `tests/test_smoke_import.py` | 锁定 internal TD live session symbol、PyO3 mainline 与 fail-fast 行为 |
| Function 锁定 | `python -m pytest tests/ -q` | 全量回归验证 |

## 十一、最终结论 / Final Verdict

- **结论**：✅ 已验收
- **日期**：2026-04-10
- **执行人**：GitHub Copilot
- **建议**：可宣告通过
- **说明**：C3 已把 TD bootstrap/readiness 主路径切到 PyO3 internal live session，且 Rust gate、repo debug smoke 与全量 pytest 全部通过。
