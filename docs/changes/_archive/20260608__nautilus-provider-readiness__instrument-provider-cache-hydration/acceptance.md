# Nautilus Provider Readiness Phase 1 InstrumentProvider Cache Hydration 验收方案 / Acceptance Plan

**模板标识 / Template Marker**：standard
**变更目录 / Change Root**：./
**状态**：✅ Repo-only 通过
**日期**：2026-06-08
**范围**：P002 Phase 1 repo-only provider/cache contract
**change-id**：20260608__nautilus-provider-readiness__instrument-provider-cache-hydration
**关联 plan**：./plan.md
**关联 ai_constraints**：./ai_constraints.md
**长期归宿 / Long-Term Target**：docs/proposals/p002-nautilus-provider-production-readiness/

<!-- AI-STATUS-BEGIN -->
```yaml
conclusion: passed
allow_declare_pass: true
last_updated: "2026-06-08 15:05"
concluded_by: "Codex"

exit_conditions:
  E1_success_scenarios: passed
  E2_failure_scenarios: passed
  E3_verification_cmds: passed
  E4_evidence_collected: passed
  E5_real_acceptance_only: passed
  E6_minimum_scenarios: passed

scenarios:
  A1: { exec: true, result: passed, blocking: true }
  A2: { exec: true, result: passed, blocking: true }
  A3: { exec: true, result: passed, blocking: true }
  A4: { exec: true, result: passed, blocking: true }
  A5: { exec: true, result: passed, blocking: true }
  A6: { exec: true, result: passed, blocking: false }
```
<!-- AI-STATUS-END -->

## 总览看板 / Dashboard

| 项目 | 值 | 说明 |
| --- | :---: | --- |
| 验收结论 | ✅ Repo-only 通过 | provider factory、metadata contract、FuturesContract hydration 和 negative path 已通过 |
| AI 建议宣告通过 | 是 | 仅限本 change repo-only scope；不包含 L5/L6 |
| 最后更新 | 2026-06-08 15:05 | |
| AI 执行人 | Codex | |

## 出口条件 / Exit Criteria

| # | 出口条件 | 状态 | 判定规则 | 证据 |
| --- | --- | :---: | --- | --- |
| E1 | 关键成功场景全部通过 | ✅ | A1/A2/A3 passed | `evidence_repo_only_provider_contract.md` |
| E2 | 关键失败场景符合预期 | ✅ | A4/A5 passed | focused pytest |
| E3 | 必跑验证命令已完成 | ✅ | focused pytest 已执行 | `evidence_repo_only_provider_contract.md` |
| E4 | 关键证据已留存 | ✅ | 当前 bundle 有 evidence | `evidence_repo_only_provider_contract.md` |
| E5 | 正式验收不依赖 mock 或 test | ✅ | 本 change scope 是 repo-only contract；不声明 L5/L6 pass | evidence limits documented |
| E6 | 正式场景数不少于 6 个 | ✅ | A1-A6 | 本文件 |

## 场景看板 / Scenario Board

| # | 场景 | 执行 | 结论 | 阻塞 | 证据/备注 |
| --- | --- | :---: | :---: | :---: | --- |
| A1 | Success: factories return CTP-aware provider | ✅ | ✅ | 是 | `CtpNautilusInstrumentProvider` |
| A2 | Success: same config shares provider instance | ✅ | ✅ | 是 | existing + updated factory tests |
| A3 | Success: normalized CTP metadata can hydrate Nautilus futures | ✅ | ✅ | 是 | `FuturesContract` added to provider cache |
| A4 | Failure: blank base `InstrumentProvider()` regression is rejected | ✅ | ✅ | 是 | provider type assertion |
| A5 | Failure: incomplete CTP metadata does not fabricate cache entry | ✅ | ✅ | 是 | negative test passed |
| A6 | Boundary: account profile remains repo-only/openctp-paper separated | ✅ | ✅ | 否 | P002 docs profile fields |

## 一、验收目标 / Goals

1. 防止 CTP factories 回退到空白 Nautilus `InstrumentProvider()`。
2. 给 Phase 1 后续 cache hydration 留下 CTP metadata contract。
3. 保持 repo-only evidence 与 OpenCTP paper/formal-trading evidence 分层。

## 二、验收范围 / Scope

### 覆盖（In Scope）

1. `get_ctp_instrument_provider()` 返回 CTP-aware provider。
2. 同 config provider cache 共享。
3. Normalized CTP metadata staging, lookup, and futures contract hydration。

### 不覆盖（Out of Scope）

1. OpenCTP live login/tick pass。
2. formal-trading evidence。
3. 完整 Nautilus `FuturesContract` 构造与 cache hydration。

## 三、验收场景 / Scenarios

| # | 场景 | 执行命令/步骤 | 预期结果 | 成功信号 | 失败口径 | 证据路径 |
| --- | --- | --- | --- | --- | --- | --- |
| A1 | Factories return CTP-aware provider | focused pytest | provider type is `CtpNautilusInstrumentProvider` | test passed | returns base `InstrumentProvider` | `./evidence_repo_only_provider_contract.md` |
| A2 | Same config shares provider | focused pytest | same object identity | test passed | data/exec get distinct providers | `./evidence_repo_only_provider_contract.md` |
| A3 | Metadata hydration works | focused pytest | `FuturesContract` added to provider cache | test passed | metadata lost or unqueryable | `./evidence_repo_only_provider_contract.md` |
| A4 | Blank provider regression rejected | focused pytest | `isinstance(..., CtpNautilusInstrumentProvider)` | test passed | blank provider accepted | `./evidence_repo_only_provider_contract.md` |
| A5 | Incomplete metadata not fabricated | focused pytest | incomplete metadata remains metadata-only | test passed | partial instrument added | `./evidence_repo_only_provider_contract.md` |
| A6 | Account profile boundary intact | proposal docs check | P002 uses account profile fields | docs check passed | profile missing/mixed | proposal docs |

## 四、证据清单 / Evidence

| # | 证据类型 | 路径/链接 | 说明 |
| --- | --- | --- | --- |
| 1 | repo-only provider contract | `./evidence_repo_only_provider_contract.md` | focused pytest output |

## 五、未通过处理 / On Failure

1. 若 provider type test fails，回到 `nautilus_factories.py`。
2. 若 metadata lookup fails，回到 `nautilus_provider.py`。
3. 若 docs gate fails，回到 P002 account profile / Phase 1 mapping。

## 六、真实验收待办清单 / Pending E2E Checklist

| # | 对应场景 | 当前阶段结果 | 还缺的真实验证 | 真实入口/命令 | 通过信号 | 阻塞项 | 证据路径 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| R1 | A5 | passed | Nautilus Instrument/cache hydration | focused pytest | fake normalized futures instrument appears in provider/cache; incomplete metadata does not | none in current scope | `./evidence_repo_only_provider_contract.md` |
| R2 | L5 | available_for_later_phase | OpenCTP paper smoke | `ctp_nautilus_live_smoke.py --config cfgs/local/ctp.openctp.tts.7x24.local.json` | login/tick/provider trace | provider-specific L5 evidence not in this repo-only change scope | OpenCTP runbook change |

## 七、最终结论 / Final Verdict

- **结论**：✅ Repo-only 通过
- **日期**：2026-06-08
- **执行人**：Codex
- **建议**：可宣告本 change repo-only scope 通过
- **说明**：OpenCTP L5 和 formal-trading L6 不在本 change 通过范围内。
