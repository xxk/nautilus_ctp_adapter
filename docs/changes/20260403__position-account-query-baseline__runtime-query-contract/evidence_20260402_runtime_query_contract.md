# Runtime Query Contract Evidence

**日期**：2026-04-02  
**topic-id**：`position-account-query-baseline`  
**change-id**：`20260403__position-account-query-baseline__runtime-query-contract`

## 一、代码落点

本次已更新：

1. [query.py](/D:/Nautilus/nautilus_ctp_adapter/src/nautilus_ctp_adapter/runtime/query.py)
2. [__init__.py](/D:/Nautilus/nautilus_ctp_adapter/src/nautilus_ctp_adapter/runtime/__init__.py)
3. [test_smoke_import.py](/D:/Nautilus/nautilus_ctp_adapter/tests/test_smoke_import.py)

## 二、当前冻结的 contract

1. `QUERY_POSITIONS -> POSITION(snapshot_complete=true)` 形成 position query 完成信号
2. `QUERY_ACCOUNT -> ACCOUNT` 形成 account query 完成信号
3. runtime query 现在可稳定返回：
   - `positions_for_request`
   - `position_count_for_request`
   - `account_for_request`

## 三、验证结果

1. `python scripts/check_topic_docs.py`
   结果：`SUMMARY topics=8 failures=0`
2. `python -m pytest`
   结果：`55 passed`

## 四、完成结论

当前 `C1` 已完成：

1. position/account runtime contract 已冻结
2. 后续 `C2/C3` 可直接在此基础上做真实 `025292` query smoke
