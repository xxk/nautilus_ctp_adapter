# A4 Query Failure Semantics Evidence

**日期**：2026-04-10
**状态**：✅ passed
**对应场景**：A4 Failure 1: query 路径异常时有清晰失败语义

## 1. 执行方式

1. 从本地真实 config 复制出一个未跟踪的临时 broken-config 副本。
2. 删除 `BrokerID` 字段后执行正式脚本入口。
3. 脚本执行完成后，立即删除该临时 broken-config 文件，避免把含敏感字段的副本留在仓库中。

## 2. 执行命令

```powershell
python scripts/ctp_query_adapter_smoke.py --config output/debug/ctp.live.025292.broken.missing-broker.json --timeout-seconds 20 --completion-grace-seconds 1.0
```

## 3. 实际输出

```json
{"baseline": "nautilus-query-adapter-v1", "success": false, "failure_reason": "exception", "error_stage": "run_smoke", "error_type": "ValueError", "error_message": "missing config fields: ['broker_id']"}
```

## 4. 结论

1. A4 已证明 query 脚本不会把配置异常静默吞掉。
2. 失败输出是结构化 JSON，而不是模糊 traceback。
3. 当前失败语义已经足以把“配置缺字段”和“运行到 live vendor bridge 之后的查询失败”区分开。
