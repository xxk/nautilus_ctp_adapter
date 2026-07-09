# OpenSpec-lite AI 执行约束 / OpenSpec-lite AI Execution Constraints

**模板标识 / Template Marker**：standard
**变更目录 / Change Root**：./
**change-id**：20260613__openctp-tts__p077-market-freshness-owner-artifact
**关联 acceptance**：./acceptance.md
**关联 plan**：./plan.md

## 单文档启动 / Standalone Kickoff

1. 先读取 sibling `acceptance.md` 与 `plan.md`。
2. 上游 blocker 是 `p077-t6-ctp-market-freshness-owner-artifact-missing`。
3. 本仓 owner 是 `owner://ctp_market_owner`；不得把 CTP truth 写到 strategies 或 Account Console 里伪造。

## 方法论 / Working Mode

1. 只复用 `CtpDataClient.run_live_md_smoke()`。
2. 只输出 pass artifact 或 typed blocker artifact。
3. Test 只锁定 contract；真实入口是 `scripts/ctp_p077_market_freshness_probe.py`。

## 边界 / Boundaries

1. 不得创建第二 runtime、第二 market data route、第二 schema family、第二 artifact root。
2. 不得调用 TD/order 下单、撤单、报单查询或资金准入流程。
3. 不得从 stdout、logs、route config、latest/debug path、UI screenshot、browser/process/window state 合成 tick freshness。
4. 不得声明 Paper ready、Live ready、admitted、production ready、capital allocated、broker tradable、P077 T6 pass。
5. 若 market freshness 不满足，必须产出 typed blocker 并保持上游阻塞。

## 必跑验证

```powershell
$env:TMP=(Resolve-Path output\tmp\pytest); $env:TEMP=$env:TMP; python -m pytest tests\test_p077_market_freshness_owner_artifact.py -q -p no:cacheprovider
python scripts\ctp_p077_market_freshness_probe.py --config cfgs\local\ctp.openctp.tts.7x24.local.json --route-id ctp-paper-19053 --account-alias 19053 --timeout-seconds 10 --freshness-threshold-seconds 60 --process-timeout-seconds 25 --output-json output\reports\p077-market-freshness\p077_t6_ctp_market_freshness.json
python scripts\check_change_docs.py --root .
python scripts\check_harness.py
```

## 收尾 / Wrap-up

1. If output status is `passed`, upstream P077 may consume the checksum as market freshness evidence.
2. If output status is `blocked`, upstream P077 may consume the checksum as the current typed market blocker.
3. In both cases, Account Console remains a projection consumer only.
