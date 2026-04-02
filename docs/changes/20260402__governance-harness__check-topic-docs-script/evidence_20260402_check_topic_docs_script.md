# Evidence: check-topic-docs-script

**change-id**: `20260402__governance-harness__check-topic-docs-script`  
**日期**: 2026-04-02

## 产出

1. 新增脚本：`/D:/Nautilus/nautilus_ctp_adapter/scripts/check_topic_docs.py`
2. 新增脚本入口说明：`/D:/Nautilus/nautilus_ctp_adapter/scripts/README.md`
3. 同步修复治理索引陈旧：
   - `/D:/Nautilus/nautilus_ctp_adapter/AGENTS.md`
   - `/D:/Nautilus/nautilus_ctp_adapter/docs/changes_topic/README.md`

## 验证结果

执行：

```powershell
python scripts/check_topic_docs.py
```

输出：

```text
PASS ctp-live-connectivity
PASS live-ops-and-reconciliation
PASS nautilus-ctp-adapter-mainline
PASS nautilus-instrument-provider
PASS nautilus-live-execution
PASS nautilus-live-marketdata
PASS repo-governance-hardening
SUMMARY topics=7 failures=0
```
