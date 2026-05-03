# A5 Read-Only Rejects Trade Semantics Evidence

**日期**：2026-04-10
**状态**：✅ passed
**对应场景**：A5 Failure 2: 只读路径不会接受交易语义或误导为 live-send

## 1. 执行命令

```powershell
python scripts/ctp_query_adapter_smoke.py --config cfgs/local/ctp.live.025292.local.json --live-send
```

## 2. 实际输出

```text
usage: ctp_query_adapter_smoke.py [-h] --config CONFIG
                                  [--timeout-seconds TIMEOUT_SECONDS]
                                  [--completion-grace-seconds COMPLETION_GRACE_SECONDS]
ctp_query_adapter_smoke.py: error: unrecognized arguments: --live-send
```

## 3. 结论

1. A5 已证明 read-only query 入口不会假装支持 live-send。
2. 非法交易语义在 argparse 层就被清楚拒绝，不会误导操作者进入真实交易路径。
3. 当前真正剩余的 blocker 已收敛到 live vendor bridge / A6 live boundary，不再包含“只读入口是否会误接交易参数”的歧义。
