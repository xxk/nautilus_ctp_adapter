---
change-id: "20260402__governance-harness__rust-validation-gate"
dependencies:
  hard_blocking: []
  soft_dependency:
    - "20260402__governance-harness__check-topic-docs-script"
  blocked_by: []
---

# Rust 校验门禁补齐 开发计划

**状态**：completed
**进度**：100%
**日期**：2026-04-02
**范围**：[`scripts/`](D:/Nautilus/nautilus_ctp_adapter/scripts/check_rust_gate.py)、[`tests/`](D:/Nautilus/nautilus_ctp_adapter/tests/test_smoke_import.py)、[`README.md`](D:/Nautilus/nautilus_ctp_adapter/README.md)、[`AGENTS.md`](D:/Nautilus/nautilus_ctp_adapter/AGENTS.md)、[`docs/`](D:/Nautilus/nautilus_ctp_adapter/docs/README.md)
**topic-id**：repo-governance-hardening
**change-id**：20260402__governance-harness__rust-validation-gate
**关联 acceptance**：[acceptance.md](./acceptance.md)

## 一、需求简述

1. 把 Rust 校验从“口头要求跑 `cargo check`”升级成仓内正式 gate。
2. 在无 `cargo` 环境下，也要给出清晰、稳定、可留证的失败口径。
3. 把 Rust gate 接入仓库官方验证入口与治理文档。
4. 用真实命令信号验证 gate 行为，而不是只补说明。

## 二、能力映射 / Capability Mapping

```text
- capability_id: governance.rust_validation_gate
- capability_name: Rust Validation Gate
- long_term_target: D:/Nautilus/nautilus_ctp_adapter/AGENTS.md
- secondary_targets: D:/Nautilus/nautilus_ctp_adapter/README.md; D:/Nautilus/nautilus_ctp_adapter/docs/README.md; D:/Nautilus/nautilus_ctp_adapter/scripts/README.md
- decision_target: D:/Nautilus/nautilus_ctp_adapter/docs/topics/repo-governance-hardening.md
- affects_long_term_rules: 是
- change_type: 新增规则
```

## 三、AI 执行约束

1. 允许修改 `scripts/`、`tests/`、`README.md`、`AGENTS.md`、`docs/` 下的治理文档。
2. 不修改 `src/nautilus_ctp_adapter/adapters/ctp/`、`src/nautilus_ctp_adapter/runtime/`、`rust/ctp_runtime_core/src/` 的业务实现。
3. 当前正式 Rust gate 入口应落在 `scripts/check_rust_gate.py`。
4. AI 开始前必须阅读 sibling `acceptance.md`、本文件，以及当前 governance topic README。
5. 改完后必须执行 `python scripts/check_rust_gate.py`、`python scripts/check_topic_docs.py`、`python -m pytest`、`python -m pip install -e .`。

## 四、背景与约束

1. 当前仓库已把 `cargo check --manifest-path rust/Cargo.toml` 写进多个入口，但这台机器没有安装 `cargo`。
2. 如果没有统一 gate，团队很容易把“本机没装 Rust”与“workspace 本身编不过”混成一个模糊结论。

## 五、任务清单

| 步骤 | 任务 | 来源 | 修改文件 | 产出 | 验证动作 | 回写目标 | 完成定义 | 状态 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| P1 | 新增正式 Rust gate 脚本 | capability:governance.rust_validation_gate | `scripts/check_rust_gate.py` | 统一脚本入口 | `python scripts/check_rust_gate.py` | `README.md` | 无 cargo 时清晰失败；有 cargo 时执行 metadata + check | 已完成 |
| P2 | 为 Rust gate 补定向测试 | capability:governance.rust_validation_gate | `tests/test_smoke_import.py` | 缺 toolchain / fake cargo 双场景锁定 | `python -m pytest` | 无 | 至少覆盖缺 cargo 和成功路径 | 已完成 |
| P3 | 回写官方验证入口与治理口径 | capability:governance.rust_validation_gate | `README.md` `AGENTS.md` `docs/README.md` `scripts/README.md` `docs/topics/...` | 正式口径统一 | `python scripts/check_topic_docs.py` | governance topic README | Rust gate 成为官方入口之一 | 已完成 |
| P4 | 留证并关账当前 change | capability:governance.rust_validation_gate | 当前 change bundle | evidence + acceptance | `python -m pip install -e .` | 当前 change bundle | 证据、结论、长期规则回写完成 | 已完成 |

## 六、完成定义

### 开发完成

1. `scripts/check_rust_gate.py` 已存在并可运行。
2. 本机无 `cargo` 时给出明确 `cargo-not-found` 失败口径。
3. 文档入口已改为优先引用 Rust gate 脚本。

### 交付完成

1. `acceptance.md` 已通过。
2. 当前 change bundle 已留存命令证据。
3. governance topic README 已登记本次 Rust gate 能力。

## 七、长期规则增量摘要 / Long-Term Rule Delta Summary

1. 新增正式 Rust 校验入口：`python scripts/check_rust_gate.py`。
2. 原先“直接写 `cargo check`”的验证口径，统一收敛为“先跑 Rust gate；若 toolchain 存在，再由脚本执行 `cargo check`”。

## 八、回写与相关变更 / Write-back & Related Changes

1. 已完成长期文档回写。
2. governance topic README 已增加 Rust gate child change 记录。

## 九、进度记录

1. 2026-04-02：完成 Rust gate 脚本、定向测试、入口回写与证据留存。
