# MD Startup Truth Baseline Evidence

**change-id**：`20260403__md-startup-truth-and-restore__md-startup-truth-baseline`  
**date**：2026-04-02

## 验收命令

```powershell
python scripts/ctp_md_startup_truth_smoke.py --config D:\Nautilus\nautilus_ctp_adapter\cfgs\local\ctp.live.025292.rb2610.10675.json --timeout-seconds 20
```

## 验收结果摘要

1. 真实 `md startup truth smoke` 返回 `0`。
2. live 输出包含：
   `baseline=md-startup-truth-v1`
   `flow_path=D:\Nautilus\nautilus_ctp_adapter\var\md_flow_smoke`
   `selected_symbols=["rb2610"]`
   `ready=true`
   `login_success=true`
   `subscribe_code=0`
   `first_tick_symbol=rb2610`
3. 当前 live bridge 事件为：
   `bridge_command_kinds=["connect", "subscribe_market_data"]`
   `bridge_event_kinds=["login_succeeded", "tick"]`

## 关键结论

1. 当前仓内已经有正式的 `MD startup truth baseline` 自动输出层。
2. 真实 `025292` 的 live 结果已经证明：`rb2610` 的 MD login、订阅和首个 tick 可以被稳定结构化输出。
3. 本 evidence 只基于真实 live smoke，不依赖 test、mock、fake 结果宣告通过。

## 原始证据

1. [md_startup_truth_20260402.log](./md_startup_truth_20260402.log)

## Supporting Validation（非验收证据）

以下命令本轮也通过了，但它们只用于回归与治理检查，不作为本 change 的验收证据：

```powershell
python scripts/check_topic_docs.py
python -m pytest
```
