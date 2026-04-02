---
change-id: "20260403__position-account-query-baseline__account-query-smoke"
dependencies:
  hard_blocking:
    - id: "20260403__position-account-query-baseline__runtime-query-contract"
      reason: "需要先继承 account query runtime contract"
      expected_status: completed
  soft_dependency:
    - "20260403__position-account-query-baseline__position-query-smoke"
  blocked_by: []
---

# Account Query Smoke 开发计划

**状态**：completed
**进度**：100%
**日期**：2026-04-02
**范围**：`src/nautilus_ctp_adapter/`、`scripts/`、`docs/`
**topic-id**：position-account-query-baseline
**change-id**：20260403__position-account-query-baseline__account-query-smoke
**关联 acceptance**：./acceptance.md

## 一、需求简述

1. 使用真实账户 `025292` 建立只读 `account query smoke`。
2. 产出结构化 account evidence。
3. 不新增任何真实交易动作。

## 二、实现摘要

1. 在 `src/nautilus_ctp_adapter/native/td_ctypes.py` 补齐了 `TdQryAccount`、`TdSetAccountCallback` 和 `NativeTradingAccountView`。
2. 在 `src/nautilus_ctp_adapter/adapters/ctp/execution_client.py` 增加 `run_live_account_query_smoke(...)`。
3. 在 `scripts/ctp_account_query_smoke.py` 建立正式只读 smoke 入口。
4. 在 `tests/test_smoke_import.py` 补齐 fake-native account smoke 回归测试。

## 三、验收结果

1. 真实账户 `025292` 的 account query smoke 已通过。
2. 2026-04-02 实测 `query_code=0`，`completed=true`，`timed_out=false`。
3. 账户资金快照已形成结构化 evidence。

## 四、验证命令

```powershell
python scripts/check_topic_docs.py
python -m pytest
python scripts/ctp_account_query_smoke.py --config D:\Nautilus\nautilus_ctp_adapter\cfgs\local\ctp.live.025292.rb2610.10675.json --timeout-seconds 20
```

