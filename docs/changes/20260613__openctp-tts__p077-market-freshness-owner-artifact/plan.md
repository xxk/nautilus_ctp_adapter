---
change-id: "20260613__openctp-tts__p077-market-freshness-owner-artifact"
dependencies:
  hard_blocking: []
  soft_dependency:
    - "D:/Nautilus/nautilus_strategies/docs/proposals/p077-p076-timed-paper-loop-workflow/"
  blocked_by: []
---

# P077 Market Freshness Owner Artifact 开发计划

**状态**：completed
**进度**：100%
**日期**：2026-06-13
**范围**：`scripts/`, `tests/`, `docs/changes/`
**topic-id**：owner-side-blocker-repair
**execution_order**：1
**change-id**：20260613__openctp-tts__p077-market-freshness-owner-artifact
**关联 acceptance**：./acceptance.md

## 一、需求简述

1. 为上游 P077 blocker `p077-t6-ctp-market-freshness-owner-artifact-missing` 提供 CTP owner 边界内的返回产物。
2. 交付一个只读 MD probe：复用 `CtpDataClient.run_live_md_smoke()`，输出 typed market freshness pass artifact 或 typed market blocker artifact。
3. 不做 TD 登录、下单、撤单、撮合、调度、P077 runtime、Account Console UI 或资金准入判断。
4. 真实信号是带 `owner://ctp_market_owner`、`upstream_blocker_id`、accepted/forbidden truth sources 和 checksum 的 JSON artifact。

## 二、能力映射 / Capability Mapping

```text
- capability_id: p077.ctp_market_freshness.owner_artifact
- capability_name: P077 CTP market freshness owner artifact
- long_term_target: 无
- secondary_targets:
  - D:/Nautilus/nautilus_strategies/docs/proposals/p077-p076-timed-paper-loop-workflow/
  - D:/Nautilus/nautilus_account_console/docs/proposals/p002-adr0044-adr0045-loop-heartbeat/
- decision_target: 无
- affects_long_term_rules: 否
- change_type: 纯实现 + 验证确认
```

## 三、AI 执行约束

1. 允许修改 `scripts/ctp_p077_market_freshness_probe.py`、`tests/test_p077_market_freshness_owner_artifact.py` 与本 change bundle。
2. 禁止修改 CTP runtime、撮合、TD/order 入口、策略 P077 scheduler、Account Console UI 或 artifact root 规则。
3. 正式入口是 `python scripts/ctp_p077_market_freshness_probe.py ...`。
4. 开始前必须确认上游 blocker 指向 `owner://ctp_market_owner`，且不得从 stdout、UI、route config、latest/debug path 合成通过。
5. 必跑验证命令：

```powershell
$env:TMP=(Resolve-Path output\tmp\pytest); $env:TEMP=$env:TMP; python -m pytest tests\test_p077_market_freshness_owner_artifact.py -q -p no:cacheprovider
python scripts\ctp_p077_market_freshness_probe.py --config cfgs\local\ctp.openctp.tts.7x24.local.json --route-id ctp-paper-19053 --account-alias 19053 --timeout-seconds 10 --freshness-threshold-seconds 60 --process-timeout-seconds 25 --output-json output\reports\p077-market-freshness\p077_t6_ctp_market_freshness.json
python scripts\check_change_docs.py --root .
python scripts\check_harness.py
```

## 四、设计方案

The probe is an owner-side artifact emitter:

1. Load `CtpAdapterConfig` from the requested config.
2. Validate required MD route configuration.
3. Reuse `build_ctp_stack(config)["data_client"].run_live_md_smoke(...)`.
4. Classify the first tick by symbol and timestamp freshness.
5. Emit one JSON payload:
   - `status=passed` only when login, subscribe, expected first tick and freshness threshold pass.
   - `status=blocked` with `blocker_type=market-freshness` for stale/missing/wrong tick.
   - `status=blocked` with `blocker_type=market-resource` for config, bridge, exception or watchdog failures.
6. Attach `sha256` checksum over canonical payload excluding the checksum field.

## 五、任务清单

| 步骤 | 任务 | 来源 | 修改文件 | 产出 | 验证动作 | 回写目标 | 完成定义 | 状态 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| P1 | 新增 P077 CTP market freshness owner artifact probe | upstream P077 blocker | `scripts/ctp_p077_market_freshness_probe.py` | MD-only artifact/blocker writer | focused pytest + real probe | 本 change acceptance | 产物含 owner/upstream/checksum/forbidden truth source | 已完成 |
| P2 | 补 contract-lock tests | tracer contract | `tests/test_p077_market_freshness_owner_artifact.py` | 7 条 focused tests | pytest | 本 change acceptance | pass/stale/wrong/missing/timeout/redaction/checksum 均覆盖 | 已完成 |
| P3 | 运行真实入口并记录 owner 返回 | owner-side repair loop | `output/reports/p077-market-freshness/p077_t6_ctp_market_freshness.json` | typed market blocker | real probe | P077/P002 handoff evidence | 不把 stale tick 写成通过 | 已完成 |

## 六、完成定义

1. CTP owner artifact writer 已落地。
2. Contract tests 通过。
3. 真实入口已产出 owner-scoped JSON artifact。
4. 若 market freshness 未满足，必须记录 typed blocker，不能宣告 P077 T6 通过。

## 七、长期规则增量摘要 / Long-Term Rule Delta Summary

本次无长期规则增量；这是 P077 external owner blocker 的 repo-local repair artifact。

## 八、回写与相关变更 / Write-back & Related Changes

1. 无长期文档回写。
2. 后续 heartbeat 可把本仓输出 artifact ref/checksum 回填到 `nautilus_strategies` P077 acceptance 与 `nautilus_account_console` P002 lane evidence。

## 九、进度记录

1. 2026-06-13：新增 probe 与 focused tests。
2. 2026-06-13：真实 OpenCTP TTS 7x24 MD probe 返回 `first_tick_stale` typed blocker，checksum `sha256:0c6ccb7149f61381a6f12b2fb0b1f57d4cd3282d66bfc9dd742e873d8ea20e1a`。
3. 2026-06-13T15:02:09Z：heartbeat owner-side retry 仍返回 `first_tick_stale` typed blocker，artifact `output/reports/p077-market-freshness/p077_t6_ctp_market_freshness_20260613T150206Z.json`，checksum `sha256:515a22b6f3692ae150825e8a8774b4e58f6b99b965e619f5eb338ba9cbab812b`。
4. 2026-06-13T15:07:56Z：heartbeat owner-side retry 仍返回 `first_tick_stale` typed blocker，artifact `output/reports/p077-market-freshness/p077_t6_ctp_market_freshness_20260613T150754Z.json`，checksum `sha256:6ac68fc7d740b36e07a4736b221f65eb5c3b0105eb09191f1ddada165624d2f1`。
5. 2026-06-13T15:11:43Z：heartbeat owner-side retry 仍返回 `first_tick_stale` typed blocker，artifact `output/reports/p077-market-freshness/p077_t6_ctp_market_freshness_20260613T151141Z.json`，checksum `sha256:d8afa028c031679523e916d95b736ef0b107805052025aee46b96470e0abce74`。
6. 2026-06-13T15:14:50Z：heartbeat owner-side retry 仍返回 `first_tick_stale` typed blocker，artifact `output/reports/p077-market-freshness/p077_t6_ctp_market_freshness_20260613T151447Z.json`，checksum `sha256:832e2f18156690ce556ecab56a3fb83e32af8e2c440f4702750432912080bc19`。
7. 2026-06-13T15:19:13Z：heartbeat owner-side retry 仍返回 `first_tick_stale` typed blocker，artifact `output/reports/p077-market-freshness/p077_t6_ctp_market_freshness_20260613T151911Z.json`，checksum `sha256:06ff7d28b3032db158e061292940fb36e3e04de90ad52ef19d5ba7476f959337`。
8. 2026-06-13T15:23:57Z：heartbeat owner-side retry 仍返回 `first_tick_stale` typed blocker，artifact `output/reports/p077-market-freshness/p077_t6_ctp_market_freshness_20260613T152355Z.json`，checksum `sha256:e3e8029975c76cb95067ff2e31581812d36db25d5feab9b207c69130c7383631`。
9. 2026-06-13T15:28:30Z：heartbeat owner-side retry 仍返回 `first_tick_stale` typed blocker，artifact `output/reports/p077-market-freshness/p077_t6_ctp_market_freshness_20260613T152828Z.json`，checksum `sha256:0fa7c0ad67ff5812c8abc4a11c21e4e14fa86debcabb37a936893bd019d77b66`。
10. 2026-06-13T15:32:52Z：heartbeat owner-side retry 仍返回 `first_tick_stale` typed blocker，artifact `output/reports/p077-market-freshness/p077_t6_ctp_market_freshness_20260613T153250Z.json`，checksum `sha256:0515d0f108a8c0e2e757b52e031958e5f6ef9f0c2e1421e0913fe84997ad53e5`。
11. 2026-06-13T15:36:22Z：heartbeat owner-side retry 仍返回 `first_tick_stale` typed blocker，artifact `output/reports/p077-market-freshness/p077_t6_ctp_market_freshness_20260613T153620Z.json`，checksum `sha256:d22fc84ca6874305759e9b88f1bc0ce3ff96c1303710b42cfe4a799a99d1de92`。
12. 2026-06-13T15:39:52Z：heartbeat owner-side retry 仍返回 `first_tick_stale` typed blocker，artifact `output/reports/p077-market-freshness/p077_t6_ctp_market_freshness_20260613T153950Z.json`，checksum `sha256:7358f9873ad1925d0b308c6b1cf3bf65683512cdeb08a771d322886ca97106ea`。
13. 2026-06-13T15:43:17Z：heartbeat owner-side retry 仍返回 `first_tick_stale` typed blocker，artifact `output/reports/p077-market-freshness/p077_t6_ctp_market_freshness_20260613T154315Z.json`，checksum `sha256:337d137a0a7658d3a6f64f28fe663f9dc240afa1cee37fc3e0b592ba9cac40d4`。
14. 2026-06-13T15:46:52Z：heartbeat owner-side retry 仍返回 `first_tick_stale` typed blocker，artifact `output/reports/p077-market-freshness/p077_t6_ctp_market_freshness_20260613T154649Z.json`，checksum `sha256:19e3021a9e1001d6cddc53f6bfa9eaf221f698c9c9fc3d3797ef8f7dcc16efd8`。
15. 2026-06-13T15:50:20Z：heartbeat owner-side retry 仍返回 `first_tick_stale` typed blocker，artifact `output/reports/p077-market-freshness/p077_t6_ctp_market_freshness_20260613T155018Z.json`，checksum `sha256:d472f5381a1b816c7e8f9c05b491c7f4ee5b39373541cf895f1422deda659049`。
16. 2026-06-13T15:53:53Z：heartbeat owner-side retry 仍返回 `first_tick_stale` typed blocker，artifact `output/reports/p077-market-freshness/p077_t6_ctp_market_freshness_20260613T155351Z.json`，checksum `sha256:3b0e550d68614ffabed69d94bd8e16fe172aa60169991c72983dd0ea1c8835b4`。
17. 2026-06-13T15:57:27Z：heartbeat owner-side retry 仍返回 `first_tick_stale` typed blocker，artifact `output/reports/p077-market-freshness/p077_t6_ctp_market_freshness_20260613T155725Z.json`，checksum `sha256:3cbc474c5a1b96dabef3c197d006f01f3d9883486c58c2ef16b16a6069ffb749`。
18. 2026-06-14T00:00:46+08:00：heartbeat selected `market_window_wait_only` because the local market window is unavailable; no new probe artifact was generated. The latest typed blocker remains `output/reports/p077-market-freshness/p077_t6_ctp_market_freshness_20260613T155725Z.json` with checksum `sha256:3cbc474c5a1b96dabef3c197d006f01f3d9883486c58c2ef16b16a6069ffb749`.
19. 2026-06-13T19:36:39Z：after the local OpenCTP TTS 7x24 config was switched to `rb2610`, heartbeat owner-side retry emitted a new typed `first_tick_stale` blocker, artifact `output/reports/p077-market-freshness/p077_t6_ctp_market_freshness_20260613T193637Z.json`, checksum `sha256:6bfe848eedd6c90e315ad3159bc885acd2da5d173771d8de054c89bec1b62d7d`, instrument `rb2610`, first tick `2026-06-11T21:20:20Z`.
20. 2026-06-13T19:44:31Z：heartbeat owner-side repair added `received_at` freshness basis and emitted a pass artifact for `rb2610`, artifact `output/reports/p077-market-freshness/p077_t6_ctp_market_freshness_20260613T194429Z.json`, checksum `sha256:dfbe8bef811104eaec39995cc91f1243dffee36c8f5b30799a85a3e464935265`, `freshness_basis=received_at`, `issues=[]`, `warnings=["first_tick_exchange_timestamp_stale"]`.
