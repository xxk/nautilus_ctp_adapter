---
change-id: "20260401__ctp-live-connectivity__python-rust-md-login-path"
dependencies:
  hard_blocking:
    - id: "20260401__ctp-live-connectivity__repo-owned-ctpnative-wrapper-bootstrap"
      reason: "需要先冻结仓内 native 边界，再把 MD 登录迁回 Python/Rust 主线"
      expected_status: completed
  soft_dependency:
    - id: "20260401__ctp-live-connectivity__login-025292-and-subscribe-rb2610"
      reason: "需要继承 rb2610 已验证行情路径"
      expected_status: in_progress
  blocked_by: []
---

# Python Rust 主线 MD 登录路径 开发计划

**状态**：completed
**进度**：100%
**日期**：2026-04-01
**范围**：`rust/ctp_runtime_core/`、`src/nautilus_ctp_adapter/runtime/`、`src/nautilus_ctp_adapter/adapters/ctp/`
**topic-id**：ctp-live-connectivity
**change-id**：20260401__ctp-live-connectivity__python-rust-md-login-path
**关联 acceptance**：./acceptance.md

## 一、需求简述

本 change 要把真实 MD 登录与 `rb2610` 订阅从临时 smoke 路径迁回 Python/Rust 主线，让后续 Nautilus 数据接线建立在正式 runtime 边界上。当前不做完整 Nautilus `LiveDataClient`，只做主线接通与可留证的最小路径。

## 二、能力映射 / Capability Mapping

```text
- capability_id: ctp-md-mainline-path
- capability_name: Python/Rust 主线行情登录路径 / Python-Rust market-data mainline path
- long_term_target: /D:/Nautilus/nautilus_ctp_adapter/docs/architecture/rust-python-adapter-split.md
- secondary_targets: /D:/Nautilus/nautilus_ctp_adapter/docs/topics/roadmap/nautilus_adapter/ctp-live-connectivity/README.md
- decision_target: /D:/Nautilus/nautilus_ctp_adapter/docs/architecture/platform-neutral-ctp-runtime.md
- affects_long_term_rules: 是
- change_type: 纯实现
```

## 三、AI 执行约束

1. 允许修改：`rust/ctp_runtime_core/`、`src/nautilus_ctp_adapter/runtime/`、`src/nautilus_ctp_adapter/adapters/ctp/data_client.py`、当前 change 三件套。
2. 禁止修改：完整交易执行逻辑与 TD 长链路；本 change 只聚焦 MD。
3. 改完后至少执行：`python -m pytest`、与 MD live 相关的最小 smoke。

## 七、任务清单

| 步骤 | 任务 | 来源 | 修改文件 | 产出 | 验证动作 | 回写目标 | 完成定义 | 状态 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| P1 | 打通 Python/Rust 主线 MD connect/login | topic C3 | runtime 相关文件 | 主线 MD login path | `python -m pytest` | `rust-python-adapter-split.md` | 无需临时宿主即可描述主线流程 | 已完成 |
| P2 | 打通 `rb2610` 订阅与事件出桥 | live bootstrap | runtime + data adapter | 最小行情事件链路 | live smoke | topic roadmap | 能留证 `rb2610` 事件 | 已完成 |
| P3 | 收口失败口径与证据入口 | governance | 当前 change 三件套 | 可重复的 smoke 口径 | 文档检查 | topic roadmap | 后续 Topic 3 可直接复用 | 已完成 |

## 八、当前进展记录

1. 2026-04-02 已通过仓内 `ctypes` 边界完成 Python 主线 `MD login` smoke，证据见 `evidence_20260402_python_md_login_smoke.md`。
2. 同日已通过反射冻结 `MdSubscribe` 的 native 真实签名：`MdSubscribe(IntPtr md, IntPtr instruments, Int32 count)`，调用约定为 `cdecl`。
3. 同日已通过 Python 主线收到 `rb2610` tick，且 bridge 中出现 `login_succeeded` 与 `tick` 事件，证据见 `evidence_20260402_python_md_subscribe_smoke.md`。
