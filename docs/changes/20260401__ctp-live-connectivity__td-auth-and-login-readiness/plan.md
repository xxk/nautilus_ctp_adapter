---
change-id: "20260401__ctp-live-connectivity__td-auth-and-login-readiness"
dependencies:
  hard_blocking:
    - id: "20260401__ctp-live-connectivity__python-rust-md-login-path"
      reason: "需要先站稳主线 MD，再聚焦 TD auth/login readiness"
      expected_status: completed
  soft_dependency:
    - id: "20260401__ctp-live-connectivity__login-025292-and-subscribe-rb2610"
      reason: "需要继承当前 ErrorID=63 的失败证据"
      expected_status: in_progress
  blocked_by: []
---

# TD 鉴权与登录就绪 开发计划

**状态**：draft
**进度**：0%
**日期**：2026-04-01
**范围**：`rust/ctp_runtime_core/`、`src/nautilus_ctp_adapter/runtime/`、live config docs、当前 change 三件套
**topic-id**：ctp-live-connectivity
**change-id**：20260401__ctp-live-connectivity__td-auth-and-login-readiness
**关联 acceptance**：./acceptance.md

## 一、需求简述

本 change 聚焦 TD `AuthCode / AppID / front / product_info` 的组合问题，把当前 `ErrorID=63` 从模糊失败收敛为明确可执行的 readiness 口径。它的目标是回答“交易侧还差什么”，而不是在本 change 里直接完成完整交易执行适配。

## 二、能力映射 / Capability Mapping

```text
- capability_id: ctp-td-login-readiness
- capability_name: TD 鉴权与登录就绪 / TD auth and login readiness
- long_term_target: /D:/Nautilus/nautilus_ctp_adapter/docs/changes_topic/roadmap/nautilus_adapter/ctp-live-connectivity/README.md
- secondary_targets: /D:/Nautilus/nautilus_ctp_adapter/docs/architecture/platform-neutral-ctp-runtime.md
- decision_target: /D:/Nautilus/nautilus_ctp_adapter/README.md
- affects_long_term_rules: 是
- change_type: 验证确认
```

## 三、AI 执行约束

1. 允许修改：runtime session/login 边界、config 解析、当前 change 三件套。
2. 禁止修改：完整下单撤单实现；本 change 只聚焦 readiness。
3. 改完后至少执行：`python -m pytest`，以及 TD readiness 相关最小验证。

## 七、任务清单

| 步骤 | 任务 | 来源 | 修改文件 | 产出 | 验证动作 | 回写目标 | 完成定义 | 状态 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| P1 | 收集并冻结 TD 缺失参数口径 | ErrorID=63 evidence | config/runtime docs | 明确缺项清单 | 文档检查 | topic roadmap | 不再停留在“可能配置不对” | 未开始 |
| P2 | 对齐 TD auth/login 输入模型 | runtime session | runtime/config 文件 | 就绪输入模型 | `python -m pytest` | architecture doc | 输入字段与实际样例一致 | 未开始 |
| P3 | 留证 TD readiness 结果 | acceptance | 当前 change 三件套 | pass/fail 解释证据 | 最小 smoke | topic roadmap | 后续 Topic 4 可直接接力 | 未开始 |

