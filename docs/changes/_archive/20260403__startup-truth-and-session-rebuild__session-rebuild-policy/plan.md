---
change-id: "20260403__startup-truth-and-session-rebuild__session-rebuild-policy"
dependencies:
  hard_blocking:
    - id: "20260403__startup-truth-and-session-rebuild__td-session-truth-baseline"
      reason: "需要先继承 td startup truth baseline"
      expected_status: completed
  soft_dependency: []
  blocked_by: []
---

# Session Rebuild Policy 开发计划

**状态**：completed
**进度**：100%
**日期**：2026-04-03
**范围**：`src/nautilus_ctp_adapter/adapters/ctp/`、`docs/`、必要时 `scripts/`
**topic-id**：startup-truth-and-session-rebuild
**change-id**：20260403__startup-truth-and-session-rebuild__session-rebuild-policy
**关联 acceptance**：./acceptance.md

## 一、需求简述

1. 冻结 session rebuild 和历史 artifact 隔离口径。
2. 明确哪些 startup truth 可以继承，哪些必须重建。
3. 保持只读，不使用 test/mock/fake 作为验收证据。

## 二、实现摘要

1. 在 `src/nautilus_ctp_adapter/adapters/ctp/startup_truth.py` 新增 `CtpSessionRebuildFinding`、`CtpSessionRebuildPolicyResult` 和 policy 评估逻辑。
2. 新增真实 live 入口 `scripts/ctp_session_rebuild_policy_smoke.py`。
3. 在 `tests/test_smoke_import.py` 锁住 session rebuild policy 的回归契约。
4. 使用真实账户 `025292` 运行 session rebuild policy smoke，并把原始输出落到当前 change bundle。

## 三、验收结果

1. 真实 `025292` session rebuild policy smoke 已通过。
2. 2026-04-03 实测 `disposition=rebuild_required`、`shared_flow_reuse_allowed=false`、`session_rotated=true`、`max_order_ref_reset=true`。
3. 当前 live 结果已经把 `rebuild_required` 与 `evidence_only` 正式区分开。

## 四、验收说明

1. 本 change 的验收证据只认真实 live smoke 与原始 log。
2. `python -m pytest` 与 `python scripts/check_topic_docs.py` 仅作为 supporting validation，不作为验收证据。
