---
change-id: "20260608__openctp-tts-simulation-provider__cancel-lifecycle"
dependencies:
  hard_blocking:
    - docs/proposals/p004-openctp-tts-simulation-provider-completeness/
  soft_dependency:
    - docs/proposals/p003-ctp-live-trading-provider-readiness/
  blocked_by: []
---

# OpenCTP TTS Simulation Cancel Lifecycle 开发计划

**状态**：已完成
**进度**：100%
**日期**：2026-06-08
**范围**：`scripts/`, `src/nautilus_ctp_adapter/adapters/ctp/`, `tests/`, `docs/changes/20260608__openctp-tts-simulation-provider__cancel-lifecycle/`
**topic-id**：openctp-tts-simulation-provider
**execution_order**：1
**change-id**：20260608__openctp-tts-simulation-provider__cancel-lifecycle
**关联 acceptance**：./acceptance.md

## 一、需求简述

1. 补齐 OpenCTP TTS 7x24 simulation 账户上的主动撤单 lifecycle。
2. 明确 passive order staging、cancel command mapping、cancel callback classification 和 Nautilus cancel report。
3. 明确不做 formal-trading，不用模拟证据关闭正式 broker readiness。
4. 用真实 simulation evidence 或 typed `paper-resource` blocker 判断是否完成。

## 二、能力映射 / Capability Mapping

```text
- capability_id: openctp-tts-simulation-provider.cancel-lifecycle
- capability_name: OpenCTP TTS Simulation Cancel Lifecycle
- long_term_target: docs/architecture/openctp-tts-simulation-provider-completeness.md
- secondary_targets: docs/changes/20260607__openctp-tts__test-baseline/runbook.md
- decision_target: docs/proposals/p004-openctp-tts-simulation-provider-completeness/
- affects_long_term_rules: 是
- change_type: 纯实现 + 验证确认
```

## 三、AI 执行约束

1. 允许修改 `scripts/`, `src/nautilus_ctp_adapter/adapters/ctp/`, `tests/` 和本 change 目录。
2. 禁止修改 `.env.d/`、提交 raw account id/password/auth code、使用 `formal-trading`。
3. 当前正式入口从现有 guarded order loop 和 Nautilus execution cancel mapping 延展，不新建第二套 provider。
4. 开始前必须阅读 P004 `acceptance.md`、P003 guarded order evidence 和本目录 `acceptance.md`。
5. 改完后必须执行 `python -m pytest tests/test_nautilus_integration.py -q`、proposal/change docs gate，并按实际 simulation 命令回填 evidence。

## 七、任务清单

| 步骤 | 任务 | 来源 | 修改文件 | 产出 | 验证动作 | 回写目标 | 完成定义 | 状态 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| P1 | 冻结 cancel intent 和 native cancel contract | P4-A3/P4-F2 | `src/`, `tests/` | cancel mapping tests | `pytest tests/test_nautilus_integration.py -q` | 本 change evidence | missing native identity blocks send | 已完成 |
| P2 | 增加 passive order staging 方案 | P4-A2/P4-B2 | `scripts/` | staging command or typed blocker | simulation dry-run/live guarded command | runbook | order can be staged or blocker typed | 已完成 |
| P3 | 采集 simulation cancel evidence | P4-A3 | 本 change evidence | redacted evidence markdown/json | OpenCTP TTS simulation command | P004 acceptance | cancel accepted/rejected classified | 已完成 |
| P4 | 覆盖 duplicate cancel callback idempotency | P4-F3 | `tests/` | regression tests | focused pytest | 无 | duplicate report not emitted | 已完成 |
| P5 | 补齐 pre-cancel snapshot 和 residual order detection | P4-A16/P4-A20/P4-F19 | `scripts/`, 本 change evidence | snapshot/residual evidence | read-only snapshot command | P004 acceptance | residual order handled or carried forward | 已完成 |
| P6 | 补齐 dry-run/armed cancel safety 一致性 | P4-A19/P4-F17 | `scripts/`, `tests/` | dry-run and armed guard evidence | focused pytest + simulation command | P004 acceptance | dry-run never sends; armed path checks guards | 已完成 |
| P7 | 补齐 cancel-after-fill race 分类 | P4-A7/P4-F6 | `scripts/`, 本 change evidence | race classification evidence | simulation command or typed blocker | P004 acceptance | final lifecycle is unambiguous | 已完成 |
| P8 | 补齐 redaction/evidence schema review | P4-A17/P4-F14/P4-F15 | 本 change evidence | evidence schema checklist | docs/evidence review | P004 acceptance | scenario id/run id/profile present and secrets absent | 已完成 |

## 九、验证动作

```bash
python -m pytest tests/test_nautilus_integration.py -q
python -m pytest tests/test_guarded_paper_cancel_loop.py tests/test_nautilus_integration.py -q --basetemp output/pytest-tmp -p no:cacheprovider
python -m pytest tests/test_smoke_import.py -q --basetemp output/pytest-tmp -p no:cacheprovider -k "check_rust_gate or pyo3_internal_td_live_session"
python -m pytest tests/test_paper_readonly_snapshot.py -q --basetemp output/pytest-tmp -p no:cacheprovider
python scripts/check_rust_gate.py
python scripts/check_proposal_docs.py --root . --proposal-id p004-openctp-tts-simulation-provider-completeness
python scripts/check_change_docs.py --root .
python scripts/check_harness.py
```

## 十、完成定义

1. Cancel command mapping 和 negative tests 完成。
2. Simulation cancel evidence 或 typed `paper-resource` blocker 留存在本 change。
3. P004 acceptance 对应 rows 更新。

## 十一、长期规则增量摘要 / Long-Term Rule Delta Summary

本次可能新增 simulation provider cancel lifecycle 长期规则，完成时回写 architecture/runbook。

## 十四、进度记录

| 时间 | 记录 |
| --- | --- |
| 2026-06-08 | Repo-only cancel contract implemented. `map_cancel_order` now rejects missing order ref/front/session identity; duplicate Nautilus exec callbacks are idempotent; dry-run cancel loop emits command contract without native send. Simulation cancel evidence remains pending. |
| 2026-06-08 18:55 | Fixed Rust/PyO3 runtime loader gate. `check_rust_gate.py` now syncs vendor CTP runtime DLLs into Cargo test loader dirs before `cargo test`; `ctp_runtime` now registers all repo native candidate DLL directories; local Python 3.12 `_ctp_runtime` exposes `CtpTdLiveSession.order_action`. Focused tests, Rust gate, proposal docs, change docs, and harness checks passed. |
| 2026-06-08 19:05 | Added process-level watchdog to `ctp_paper_readonly_snapshot.py`. Connected pre-cancel snapshot now emits a typed `paper-resource` blocker instead of hanging when the OpenCTP TTS API connect/query path does not return. Live staging/cancel remains gated because pre-cancel snapshot did not complete. |
| 2026-06-08 20:55 | Completed real OpenCTP TTS cancel lifecycle evidence after restoring official TTS 6.6.9 runtime/SDK and using `rust/target/debug` first on `PATH`. Covered TD login, account/position/instrument snapshots, passive staging, reject classification, armed native cancel (`native_code=0`), no-residual cleanup, and fill-before-cancel cleanup. |
