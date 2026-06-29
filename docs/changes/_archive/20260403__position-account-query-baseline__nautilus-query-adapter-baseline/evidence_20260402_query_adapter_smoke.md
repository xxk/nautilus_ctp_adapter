# Nautilus Query Adapter Baseline Evidence

**change-id**：`20260403__position-account-query-baseline__nautilus-query-adapter-baseline`  
**date**：2026-04-02

## 验证命令

```powershell
python scripts/check_topic_docs.py
python -m pytest
python scripts/ctp_query_adapter_smoke.py --config D:\Nautilus\nautilus_ctp_adapter\cfgs\local\ctp.live.025292.rb2610.10675.json --timeout-seconds 20 --completion-grace-seconds 1.0
```

## 结果摘要

1. `python scripts/check_topic_docs.py` 返回：`SUMMARY topics=8 failures=0`
2. `python -m pytest` 返回：`59 passed`
3. 统一 `query adapter smoke` 返回：
   `positions.query_code=0`
   `positions.completed=true`
   `positions.timed_out=false`
   `positions.position_count=73`
   `account.query_code=0`
   `account.completed=true`
   `account.timed_out=false`
   `account.account_id=025292`

## 关键结论

1. `CtpQueryAdapter` 已把真实 `TdQryPosition` 和 `TdQryAccount` 收口成 Nautilus 可消费的最小统一入口。
2. 工厂已保证 `query_adapter`、`execution_client`、`runtime_bridge` 共享同一条主线边界，没有再造第二套 query runtime。
3. 真实账户 `025292` 的 position/account 只读查询已能通过单个 smoke 入口完成顺序执行和结构化结果返回。
4. 原始日志里出现的 `TD Front Disconnected: 4097` 属于会话噪声，不影响本次 query baseline 的成功判定，因为 position/account 两段查询都已闭合并返回有效结果。

## 原始证据

1. [query_adapter_smoke_20260402.log](./query_adapter_smoke_20260402.log)
