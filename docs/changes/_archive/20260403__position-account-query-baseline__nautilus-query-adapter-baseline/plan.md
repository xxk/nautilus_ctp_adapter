---
change-id: "20260403__position-account-query-baseline__nautilus-query-adapter-baseline"
dependencies:
  hard_blocking:
    - id: "20260403__position-account-query-baseline__position-query-smoke"
      reason: "需要先拿到真实 position query evidence"
      expected_status: completed
    - id: "20260403__position-account-query-baseline__account-query-smoke"
      reason: "需要先拿到真实 account query evidence"
      expected_status: completed
  soft_dependency: []
  blocked_by: []
---

# Nautilus Query Adapter Baseline 开发计划

**状态**：completed
**进度**：100%
**日期**：2026-04-02
**范围**：`src/nautilus_ctp_adapter/adapters/ctp/`、`scripts/`、`docs/`
**topic-id**：position-account-query-baseline
**change-id**：20260403__position-account-query-baseline__nautilus-query-adapter-baseline
**关联 acceptance**：./acceptance.md

## 一、需求简述

1. 把已通过的 `TdQryPosition / TdQryAccount` 接成 Nautilus 可消费的最小 adapter baseline。
2. 统一 query 入口、结果对象和脚本口径。
3. 不新增真实交易动作。

## 二、实现摘要

1. 在 `src/nautilus_ctp_adapter/adapters/ctp/query_adapter.py` 新增 `CtpQueryAdapter`、`CtpPositionQueryBaseline`、`CtpAccountQueryBaseline` 和 `CtpQueryAdapterSnapshot`。
2. 在 `src/nautilus_ctp_adapter/adapters/ctp/factory.py` 让 `query_adapter` 与 `execution_client`、`runtime_bridge` 共享同一条主线实例。
3. 在 `scripts/ctp_query_adapter_smoke.py` 建立统一只读 smoke 入口，串行完成真实 `position/account` 查询。
4. 在 `tests/test_smoke_import.py` 补齐 query adapter snapshot 的委托与映射回归测试。

## 三、验收结果

1. 统一 `query adapter smoke` 已通过。
2. 2026-04-02 实测 `positions.query_code=0`、`positions.position_count=73`、`account.query_code=0`、`account.account_id=025292`。
3. 结果已写入 evidence 和原始 log。

## 四、验证命令

```powershell
python scripts/check_topic_docs.py
python -m pytest
python scripts/ctp_query_adapter_smoke.py --config D:\Nautilus\nautilus_ctp_adapter\cfgs\local\ctp.live.025292.rb2610.10675.json --timeout-seconds 20 --completion-grace-seconds 1.0
```
