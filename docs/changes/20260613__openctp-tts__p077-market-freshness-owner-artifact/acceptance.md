# P077 Market Freshness Owner Artifact 验收方案 / Acceptance Plan

**模板标识 / Template Marker**：standard
**变更目录 / Change Root**：./
**状态**：✅ 已执行
**日期**：2026-06-13
**范围**：`scripts/`, `tests/`, `docs/changes/`
**change-id**：20260613__openctp-tts__p077-market-freshness-owner-artifact
**关联 plan**：./plan.md
**关联 ai_constraints**：./ai_constraints.md
**长期归宿 / Long-Term Target**：无

<!-- AI-STATUS-BEGIN -->
```yaml
conclusion: pass_owner_artifact_or_typed_blocker_emitted
allow_declare_pass: true
last_updated: "2026-06-13 23:02"
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

### 验收总状态 / Overall

| 项目 | 值 | 说明 |
| --- | :---: | --- |
| 验收结论 | ✅ 已执行 | owner artifact/blocker writer 已完成 |
| AI 建议宣告通过 | 是 | 仅表示本 owner-side repair change 通过，不表示 P077 T6 通过 |
| 最后更新 | 2026-06-13 22:52 | |
| AI 执行人 | Codex | |

### 出口条件 / Exit Criteria

| # | 出口条件 | 状态 | 判定规则 | 证据 |
| --- | --- | :---: | --- | --- |
| E1 | 关键成功场景全部通过 | ✅ | pass artifact builder 覆盖 owner/source/checksum | focused pytest |
| E2 | 关键失败场景符合预期 | ✅ | stale/wrong/missing/timeout 均 blocked | focused pytest |
| E3 | 必跑验证命令已完成 | ✅ | focused pytest 与真实 probe 已执行 | 命令记录 |
| E4 | 关键证据已留存 | ✅ | output artifact 已生成 | `output/reports/p077-market-freshness/p077_t6_ctp_market_freshness.json` |
| E5 | 正式验收不依赖 mock 或 test | ✅ | 正式入口真实运行；pytest 只做 contract-lock | real probe |
| E6 | 正式场景数不少于 6 个 | ✅ | A1-A6 均覆盖 | 场景表 |

### 场景看板 / Scenario Board

| # | 场景 | 执行 | 结论 | 阻塞 | 证据/备注 |
| --- | --- | :---: | :---: | :---: | --- |
| A1 | Success 1: fresh tick artifact builder | ✅ | ✅ | 是 | `test_pass_artifact_is_owner_scoped_source_backed_and_checksummed` |
| A2 | Success 2: secret redaction | ✅ | ✅ | 是 | `test_artifact_redacts_account_and_password` |
| A3 | Success 3: checksum canonicalization | ✅ | ✅ | 是 | `test_checksum_is_canonical_and_changes_when_payload_changes` |
| A4 | Failure 1: stale tick -> typed blocker | ✅ | ✅ | 是 | `test_stale_tick_becomes_typed_market_freshness_blocker` |
| A5 | Failure 2: missing config / watchdog -> typed blocker | ✅ | ✅ | 是 | focused pytest |
| A6 | Boundary 1: real OpenCTP probe emits owner pass or typed blocker, not stdout/UI truth | ✅ | ✅ | 否 | latest retry checksum `sha256:dfbe8bef811104eaec39995cc91f1243dffee36c8f5b30799a85a3e464935265`; instrument `rb2610`; `freshness_basis=received_at`; warning `first_tick_exchange_timestamp_stale` |

## 一、验收目标 / Goals

Provide a CTP-owner-scoped artifact for upstream P077 T6 without creating a second runtime or claiming Paper readiness.

## 二、验收范围 / Scope

### 覆盖（In Scope）

1. MD-only market freshness probe.
2. Typed pass artifact when first tick is fresh.
3. Typed blocker artifact when config, runtime, tick or freshness fails.
4. Redacted identity and canonical checksum.

### 不覆盖（Out of Scope）

1. TD login or order submission.
2. Strategy scheduler/runtime repair.
3. Account Console UI or read-model truth.
4. P077 T6 pass declaration.

## 三、前置条件 / Prerequisites

| 条件 | 类型 | 阻断开发 | 阻断验收 | 状态 | 备注 |
| --- | --- | :---: | :---: | :---: | --- |
| Python can run repo tests | 环境 | 是 | 是 | ✅ | Used repo-local temp dir due default temp permission issue |
| OpenCTP local config exists | 环境 | 否 | 否 | ✅ | `cfgs/local/ctp.openctp.tts.7x24.local.json` |
| Market emits fresh tick | 外部资源 | 否 | 否 | ⚠️ | 当前真实 run 返回 stale tick typed blocker |

## 四、验收专属 AI 边界 / Acceptance-Only AI Boundaries

1. Focused pytest only locks artifact contract and negative paths.
2. Real acceptance signal is the script artifact or typed blocker JSON.
3. `allow_declare_pass=true` only closes this CTP owner-side repair change.
4. P077 T6 remains blocked until upstream records an owner artifact whose `status=passed`, or explicitly records the typed market blocker as the current external blocker.

## 五、验收场景 / Scenarios

| # | 场景 | 执行命令/步骤 | 预期结果 | 成功信号 | 失败口径 | 证据路径 |
| --- | --- | --- | --- | --- | --- | --- |
| A1 | Fresh tick artifact builder | focused pytest | `status=passed` with owner/upstream/checksum | owner/source/checksum present | missing owner/checksum | pytest |
| A2 | Redaction | focused pytest | raw account/password absent | fingerprint present | raw secret appears | pytest |
| A3 | Checksum | focused pytest | canonical checksum stable | mutation changes checksum | checksum ignores mutation | pytest |
| A4 | Stale tick | focused pytest | `blocker_type=market-freshness` | `failure_reason=first_tick_stale` | stale tick passes | pytest |
| A5 | Missing config / timeout | focused pytest | `blocker_type=market-resource` | owner blocker emitted | raw exception only | pytest |
| A6 | Real OpenCTP probe | script command | pass or typed blocker JSON | checksum emitted | stdout/log only | `output/reports/p077-market-freshness/p077_t6_ctp_market_freshness.json` |

## 六、证据清单 / Evidence

| # | 证据类型 | 路径/链接 | 说明 |
| --- | --- | --- | --- |
| 1 | Contract tests | `python -m pytest tests\test_p077_market_freshness_owner_artifact.py -q -p no:cacheprovider` | `8 passed` |
| 2 | Real owner artifact | `output/reports/p077-market-freshness/p077_t6_ctp_market_freshness_20260613T194429Z.json` | owner pass artifact: `status=passed`; `freshness_basis=received_at` |
| 3 | Artifact checksum | `sha256:dfbe8bef811104eaec39995cc91f1243dffee36c8f5b30799a85a3e464935265` | Latest heartbeat owner retry artifact checksum |
| 4 | Retry artifact | `output/reports/p077-market-freshness/p077_t6_ctp_market_freshness_20260613T194429Z.json` | instrument `rb2610`; first tick received at `2026-06-13T19:44:31Z`; warning `first_tick_exchange_timestamp_stale` |
| 5 | Diagnostic screenshot | `output/debug/screenshots/19053_terminal_20260613T193902Z.png` | operator-visible `TickTrader[19053] - rb2610`; diagnostic only, not artifact truth |

## 七、未通过处理 / On Failure

1. If the probe emits `market-resource`, repair CTP config/native bridge only inside this repo.
2. If the probe emits `market-freshness`, wait for market freshness, fix the owner-side timestamp basis, or rerun during an active market window.
3. Do not turn stale tick, logs, screenshots or route config into P077 pass evidence.

## 八、Contract/Function 锁定证据

| 项目 | 路径/命令 | 说明 |
| --- | --- | --- |
| Contract 锁定 | `tests/test_p077_market_freshness_owner_artifact.py` | owner identity, upstream blocker id, checksum, redaction and blocker semantics |
| Function 锁定 | `scripts/ctp_p077_market_freshness_probe.py` | MD-only owner artifact writer |

## 九、最终结论 / Final Verdict

- **结论**：✅ 本 CTP owner-side repair change 已完成
- **日期**：2026-06-13
- **执行人**：Codex
- **建议**：可宣告本 change 通过
- **说明**：真实 OpenCTP probe 已切到 `rb2610`，并以 `received_at` basis 返回 owner pass artifact；交易所 tick 时间戳仍有 `first_tick_exchange_timestamp_stale` warning。该证据只解除 CTP owner freshness blocker，不声明 Paper ready。
