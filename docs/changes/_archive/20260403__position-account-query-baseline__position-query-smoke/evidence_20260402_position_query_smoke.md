# Position Query Smoke Evidence

**change-id**：`20260403__position-account-query-baseline__position-query-smoke`  
**date**：2026-04-02

## 验证命令

```powershell
python scripts/check_topic_docs.py
python -m pytest
python scripts/ctp_position_query_smoke.py --config D:\Nautilus\nautilus_ctp_adapter\cfgs\local\ctp.live.025292.rb2610.10675.json --timeout-seconds 20 --completion-grace-seconds 1.0
```

## 结果摘要

1. `python scripts/check_topic_docs.py` 返回：`SUMMARY topics=8 failures=0`
2. `python -m pytest` 返回：`58 passed`
3. 真实 `position query smoke` 返回：
   `query_code=0`
   `completed=true`
   `timed_out=false`
   `no_positions=false`
   `position_count=73`

## 关键结论

1. 仓内维护的本地 `c wrapper` 已经能通过 `TdQryPosition` 返回真实账户 `025292` 的持仓快照。
2. shared runtime 已经能把真实 position callback 归一化为 `POSITION` 事件并形成可消费的 query result。
3. 当前结果明确不是“无持仓”，而是“成功收到多条真实持仓记录”。

## 原始证据

1. [position_query_smoke_20260402.log](./position_query_smoke_20260402.log)

