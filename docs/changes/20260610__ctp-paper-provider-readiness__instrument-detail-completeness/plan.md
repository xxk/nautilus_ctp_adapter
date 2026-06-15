---
change-id: "20260610__ctp-paper-provider-readiness__instrument-detail-completeness"
dependencies:
  hard_blocking: []
  soft_dependency:
    - id: "20260608__ctp-paper-provider-readiness__paper-readonly-truth-snapshot"
      reason: "C1 instrument detail completeness extends the existing paper readonly snapshot contract"
      expected_status: completed
    - id: "20260608__ctp-paper-provider-readiness__guarded-paper-order-loop"
      reason: "C1 lifecycle, trading status and order-volume fields must feed paper order preflight"
      expected_status: completed
  blocked_by: []
---

# Paper Instrument Detail Completeness 开发计划

**状态**：已完成
**进度**：100%
**日期**：2026-06-10
**范围**：`src/nautilus_ctp_adapter/adapters/ctp/`、`src/nautilus_ctp_adapter/runtime/`、`scripts/`、`tests/`、`docs/changes/20260608__ctp-paper-provider-readiness__paper-readonly-truth-snapshot/`、当前 change 三件套
**topic-id**：none
**execution_order**：1
**change-id**：20260610__ctp-paper-provider-readiness__instrument-detail-completeness
**关联 acceptance**：./acceptance.md

## 一、需求简述

1. 把 paper instrument query / readonly snapshot 从当前只稳定覆盖 C0 基础字段，扩展到 C1 合约明细字段。
2. 让 `InstrumentName`、`OpenDate`、`ExpireDate`、`StartDelivDate`、`EndDelivDate`、`IsTrading`、保证金比例、最小/最大委托量、`ProductID`、`UnderlyingInstrID`、`DeliveryYear`、`DeliveryMonth` 进入本仓正式 contract。
3. 把这些字段接到 provider/cache/preflight 的可消费规则上，尤其是 trading status、delivery window、min/max volume 和 margin preview。
4. 不把 options-specific / combination fields 混进当前 futures paper baseline。

## 二、能力映射 / Capability Mapping

```text
- capability_id: paper-instrument-detail-completeness
- capability_name: Paper instrument detail completeness
- long_term_target: /D:/Nautilus/nautilus_ctp_adapter/docs/proposals/p003-ctp-live-trading-provider-readiness/
- secondary_targets: /D:/Nautilus/nautilus_ctp_adapter/docs/changes/20260608__ctp-paper-provider-readiness__paper-readonly-truth-snapshot/acceptance.md
- decision_target: /D:/Nautilus/nautilus_ctp_adapter/docs/architecture/openctp-tts-simulation-provider-completeness.md
- affects_long_term_rules: 是
- change_type: 修改规则
```

## 三、AI 执行约束

1. 允许修改：当前 change 三件套、paper readonly snapshot/paper order preflight 相关源码、相关 tests、必要 scripts、相关 acceptance / architecture 回写。
2. 禁止修改：ADR 状态、proposal 主状态、formal-trading / Live scope、任何 secret/local config、`vendor/`。
3. 当前正式入口优先使用：`python scripts/ctp_paper_readonly_snapshot.py ...`、paper guarded order dry-run / preflight、focused pytest、docs gates。
4. AI 开始前必须阅读：P003 acceptance / phase-plan、`20260608__ctp-paper-provider-readiness__paper-readonly-truth-snapshot/acceptance.md`、`20260608__ctp-paper-provider-readiness__guarded-paper-order-loop/acceptance.md`。
5. 改完后至少执行：focused pytest、`python scripts/check_change_docs.py --root .`、必要时 `python scripts/check_proposal_docs.py --root . --proposal-id p003-ctp-live-trading-provider-readiness`。

## 四、背景与约束

1. 当前 P003/P004 已证明 paper trading 主链路可用，但 C1 合约明细字段仍停留在 acceptance design 中的 `planned`。
2. 当前正式通过范围只稳定覆盖 C0：symbol、exchange、product kind、price tick、volume multiple、display id。
3. 这次 change 的目标不是新建 proposal/ADR，而是把现有 paper instrument detail contract 做完整。
4. 若上游 OpenCTP query 在某些字段上缺值，必须以 typed `data-contract` disposition 表达，不能伪造 pass。

## 五、设计方案

1. 扩展 instrument query -> normalized snapshot record，使 C1 字段进入 `raw_detail` / `detail_fields`。
2. 新增 completeness / correctness summary 和 issue taxonomy，覆盖字段缺失、未知 product kind、conflict、non-tradable / delivery-window / min-max-volume violations。
3. 把 `IsTrading`、delivery window、min/max volume、margin ratio 等接入 guarded paper order preflight。
4. 维持 C2 options-specific 为 out-of-scope，除非仅以 typed `out_of_scope_current` 明示。

## 六、任务清单

| 步骤 | 任务 | 来源 | 修改文件 | 产出 | 验证动作 | 回写目标 | 完成定义 | 状态 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| P1 | 扩展 snapshot schema 承载 C1 字段 | P3-A16 / CD-C2 | runtime/adapter/snapshot files | `detail_fields` / `raw_detail` / correctness summary | focused pytest | readonly snapshot acceptance | C1 可见字段进入 redacted evidence | 已完成 |
| P2 | 补 C1 correctness/completeness rules | P3-A16 / P3-F9 / CD-C5~CD-C8 | tests + validation helpers | typed `data-contract` issues | focused pytest | current change acceptance | unknown product kind / conflicts / missing fields 不再静默 pass | 已完成 |
| P3 | 接入 paper preflight 消费规则 | P3-A17 / guarded order successor tests | order preflight files + tests | `IsTrading` / delivery window / min-max-volume / margin preview guard | focused pytest | guarded order acceptance / architecture | 不可交易或数量越界在 native send 前阻断 | 已完成 |
| P4 | 真实 paper evidence 与文档回填 | P003 successor evidence | current change evidence + docs | redacted snapshot / dry-run or typed blocker | docs gates + optional paper command | P003 / architecture | 文档明确 C1 哪些 passed、哪些仍 out_of_scope | 已完成 |

## 七、验证动作

```powershell
python -m pytest tests/test_paper_readonly_snapshot.py tests/test_guarded_paper_order_loop.py tests/test_nautilus_integration.py -q --basetemp output/pytest-tmp -p no:cacheprovider
python scripts/check_change_docs.py --root .
python scripts/check_proposal_docs.py --root . --proposal-id p003-ctp-live-trading-provider-readiness
```

## 八、完成定义

### 开发完成

1. C1 字段在运行时可见时进入 paper readonly snapshot contract。
2. completeness / correctness issue taxonomy 可区分 missing / conflict / unknown / out_of_scope。
3. guarded paper order preflight 能消费 trading status、delivery window、min/max volume 等关键字段。

### 交付完成

1. 当前 change `acceptance.md` 中 C1 in-scope 场景通过，或 external field absence 被 typed `data-contract` / `paper-resource` blocker 收口。
2. `paper-readonly-truth-snapshot` 相关 acceptance 已回写，不再只停留在 `planned` 描述。
3. proposal / architecture 的稳定规则已回写，或明确保持 change-local。

## 九、长期规则增量摘要 / Long-Term Rule Delta Summary

本次计划把 C1 instrument detail fields 纳入 paper snapshot / preflight 正式 contract；若上游查询可见，这些字段必须进入 redacted evidence 并驱动 provider/cache/order guard，而不是停留在文档设计层。

## 十、回写与相关变更 / Write-back & Related Changes

1. 主回写目标：P003 paper readonly truth snapshot 相关 acceptance 口径。
2. 次级回写目标：若形成稳定 provider rule，则回写 `openctp-tts-simulation-provider-completeness` architecture 文档。
3. 不改 ADR，不新建 proposal。

## 十一、进度记录

1. 2026-06-10：补齐 runtime query / instrument normalization / readonly snapshot / guarded preflight 对 C1 detail contract 的代码承载。
2. 2026-06-10：focused pytest 通过：`tests/test_paper_readonly_snapshot.py`、`tests/test_guarded_paper_order_loop.py`、`tests/test_nautilus_integration.py`。
3. 2026-06-10：真实 paper readonly snapshot 证据已生成到 `output/reports/p003-ctp-live-trading-provider-readiness/instrument-detail-completeness/paper_readonly_snapshot_connect.json`；当前 front 实际提供 `instrument_name/open_date/expire_date/product_id/delivery_year/delivery_month`，其余 C1 字段维持 typed partial/missing。
