---
change-id: "20260403__position-account-query-baseline__position-query-smoke"
dependencies:
  hard_blocking:
    - id: "20260403__position-account-query-baseline__runtime-query-contract"
      reason: "需要先继承 position query runtime contract"
      expected_status: completed
  soft_dependency: []
  blocked_by: []
---

# Position Query Smoke 开发计划

**状态**：completed
**进度**：100%
**日期**：2026-04-02
**范围**：`src/nautilus_ctp_adapter/`、`scripts/`、`docs/`
**topic-id**：position-account-query-baseline
**change-id**：20260403__position-account-query-baseline__position-query-smoke
**关联 acceptance**：./acceptance.md

## 一、需求简述

1. 使用真实账户 `025292` 建立只读 `position query smoke`。
2. 区分“无持仓”和“查询失败”。
3. 产出结构化 position evidence。
4. 不新增新的真实交易动作。

## 二、实现摘要

1. 在 `src/nautilus_ctp_adapter/native/td_ctypes.py` 补齐了仓内维护的 `TdQryPosition`、`TdSetPositionCallback` 和 `NativePositionView`。
2. 在 `src/nautilus_ctp_adapter/adapters/ctp/execution_client.py` 增加 `run_live_position_query_smoke(...)`，把真实 TD query 接到 shared runtime。
3. 在 `scripts/ctp_position_query_smoke.py` 建立正式只读 smoke 入口。
4. 在 `tests/test_smoke_import.py` 补齐 position completion marker 与 fake-native smoke 回归测试。

## 三、验收结果

1. 真实账户 `025292` 的 position query smoke 已通过。
2. 2026-04-02 实测 `query_code=0`，`completed=true`，`timed_out=false`，`position_count=73`。
3. 结果已写入 evidence 和原始 log。

## 四、验证命令

```powershell
python scripts/check_topic_docs.py
python -m pytest
python scripts/ctp_position_query_smoke.py --config D:\Nautilus\nautilus_ctp_adapter\cfgs\local\ctp.live.025292.rb2610.10675.json --timeout-seconds 20 --completion-grace-seconds 1.0
```
