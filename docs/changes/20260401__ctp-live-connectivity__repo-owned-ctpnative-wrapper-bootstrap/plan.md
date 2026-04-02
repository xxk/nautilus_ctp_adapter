---
change-id: "20260401__ctp-live-connectivity__repo-owned-ctpnative-wrapper-bootstrap"
dependencies:
  hard_blocking:
    - id: "20260401__ctp-live-connectivity__login-025292-and-subscribe-rb2610"
      reason: "需要继承已确认的 live config、native pack 来源和 rb2610 行情证据"
      expected_status: in_progress
  soft_dependency: []
  blocked_by: []
---

# 仓内维护 ctpnative wrapper 启动变更 开发计划

**状态**：completed
**进度**：100%
**日期**：2026-04-01
**范围**：`native/`、`vendor/ctp/`、`rust/ctp_runtime_core/`、`docs/changes/20260401__ctp-live-connectivity__repo-owned-ctpnative-wrapper-bootstrap/`
**topic-id**：ctp-live-connectivity
**change-id**：20260401__ctp-live-connectivity__repo-owned-ctpnative-wrapper-bootstrap
**关联 acceptance**：./acceptance.md

## 一、需求简述

本 change 要把“仓内维护 `ctpnative`”从口头方向落成明确边界：冻结 C wrapper 的职责、输入输出、依赖来源与构建归属。当前不做完整 Nautilus 接线，也不在本 change 里直接解决 TD 登录问题。做完后应能明确回答：后续 Python/Rust 主线要依赖哪个仓内 native 边界，而不是继续依赖临时宿主或外部生成物。

## 二、能力映射 / Capability Mapping

```text
- capability_id: ctp-repo-owned-native-boundary
- capability_name: 仓内维护 ctpnative 边界 / Repository-owned ctpnative boundary
- long_term_target: /D:/Nautilus/nautilus_ctp_adapter/docs/architecture/platform-neutral-ctp-runtime.md
- secondary_targets: /D:/Nautilus/nautilus_ctp_adapter/docs/changes_topic/roadmap/nautilus_adapter/ctp-live-connectivity/README.md
- decision_target: /D:/Nautilus/nautilus_ctp_adapter/README.md
- affects_long_term_rules: 是
- change_type: 新增规则
```

## 三、AI 执行约束

1. 允许修改：`vendor/ctp/`、`scripts/`、`src/nautilus_ctp_adapter/native/`、`rust/ctp_runtime_core/`、当前 change 三件套。
2. 禁止修改：`src/nautilus_ctp_adapter/adapters/ctp/` 的正式 Nautilus glue 逻辑，除非为了接本 change 明确声明的新 native 边界。
3. 本 change 的正式落点是“仓内 native ownership 边界”，不是最终行情/交易适配。
4. AI 开始前必须阅读：当前 topic roadmap、`vendor/ctp/README.md`、`src/nautilus_ctp_adapter/native/loader.py`。
5. 改完后至少执行：`python -m pytest`、`python -m pip install -e .`。

## 七、任务清单

| 步骤 | 任务 | 来源 | 修改文件 | 产出 | 验证动作 | 回写目标 | 完成定义 | 状态 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| P1 | 冻结仓内 `ctpnative` ownership 边界 | topic C2 | `vendor/ctp/README.md`、当前 change 三件套 | 明确仓内维护口径 | 文档检查 | `platform-neutral-ctp-runtime.md` | 说明谁维护、维护到哪层、哪些外部产物只作样例 | 已完成 |
| P2 | 定义 C wrapper 最小导出面 | capability | `rust/ctp_runtime_core/`、`src/nautilus_ctp_adapter/native/` | 最小 native ABI 草案 | `python -m pytest` | architecture doc | 导出职责与 runtime 边界一致 | 已完成 |
| P3 | 收敛 vendor/native 同步方式 | implementation | `scripts/`、`vendor/ctp/` | 可复用同步/打包口径 | `python -m pip install -e .` | topic roadmap | 不再依赖临时宿主路径作为长期方案 | 已完成 |
| P4 | 回写 topic queue 与长期规则 | governance | 当前 change 三件套、topic roadmap | 已冻结规则与证据入口 | 文档检查 | topic roadmap | 后续 C3 可直接接 Python/Rust 主线 | 已完成 |
