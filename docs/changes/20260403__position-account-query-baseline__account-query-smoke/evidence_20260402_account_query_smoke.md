# Account Query Smoke Evidence

**change-id**：`20260403__position-account-query-baseline__account-query-smoke`  
**date**：2026-04-02

## 验证命令

```powershell
python scripts/check_topic_docs.py
python -m pytest
python scripts/ctp_account_query_smoke.py --config D:\Nautilus\nautilus_ctp_adapter\cfgs\local\ctp.live.025292.rb2610.10675.json --timeout-seconds 20
```

## 结果摘要

1. `python scripts/check_topic_docs.py` 返回：`SUMMARY topics=8 failures=0`
2. `python -m pytest` 返回：`58 passed`
3. 真实 `account query smoke` 返回：
   `query_code=0`
   `completed=true`
   `timed_out=false`
   `account_id=025292`

## 关键结论

1. 仓内维护的本地 `c wrapper` 已经能通过 `TdQryAccount` 返回真实账户 `025292` 的资金快照。
2. shared runtime 已经能把真实 account callback 归一化为 `ACCOUNT` 事件并形成可消费的 query result。
3. 当前结果为真实 live snapshot，不涉及任何新的交易动作。

## 原始证据

1. [account_query_smoke_20260402.log](./account_query_smoke_20260402.log)

