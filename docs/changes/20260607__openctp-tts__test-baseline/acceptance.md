# OpenCTP TTS Test Baseline 验收方案 / Acceptance Plan

**模板标识 / Template Marker**：standard
**变更目录 / Change Root**：./
**状态**：✅ 通过
**日期**：2026-06-08
**范围**：OpenCTP TTS 7x24 配置模板、配置校验、测试入口导航、真实连通证据
**change-id**：20260607__openctp-tts__test-baseline
**关联 plan**：./plan.md
**关联 ai_constraints**：./ai_constraints.md
**长期归宿 / Long-Term Target**：/D:/Nautilus/nautilus_ctp_adapter/docs/topics/live-session-order-query-hardening.md

<!-- AI-STATUS-BEGIN -->
```yaml
conclusion: passed
allow_declare_pass: true
last_updated: "2026-06-08 14:45"
concluded_by: "Codex"

exit_conditions:
  E1_success_scenarios: passed
  E2_failure_scenarios: passed
  E3_verification_cmds: passed
  E4_evidence_collected: passed
  E5_real_acceptance_only: passed
  E6_minimum_scenarios: passed

scenarios:
  A1: { exec: true, result: passed, blocking: true }
  A2: { exec: true, result: passed, blocking: true }
  A3: { exec: true, result: passed, blocking: true }
  A4: { exec: true, result: passed, blocking: true }
  A5: { exec: true, result: passed, blocking: true }
  A6: { exec: true, result: passed, blocking: false }
```
<!-- AI-STATUS-END -->

## 总览看板 / Dashboard

### 验收总状态 / Overall

| 项目 | 值 | 说明 |
| --- | :---: | --- |
| 验收结论 | ✅ 通过 | OpenCTP 7x24 paper MD/TD/query/dry-run smoke 已通过 |
| AI 建议宣告通过 | 是 | 由 `AI-STATUS allow_declare_pass` 派生 |
| 最后更新 | 2026-06-08 14:45 | |
| AI 执行人 | Codex | |

### 出口条件 / Exit Criteria

| # | 出口条件 | 状态 | 判定规则 | 证据 |
| --- | --- | :---: | --- | --- |
| E1 | 关键成功场景全部通过 | ✅ | A1/A2/A3 通过 | A2/A3 已补 OpenCTP paper 证据 |
| E2 | 关键失败场景符合预期 | ✅ | A4/A5 通过 | targeted pytest + dry-run evidence |
| E3 | 必跑验证命令已完成 | ✅ | plan.md 中声明的命令已执行 | pytest、rust gate、live smoke、docs gates |
| E4 | 关键证据已留存 | ✅ | 当前 change bundle 中存在证据路径 | A1/A2/A3/A5/A6 |
| E5 | 正式验收不依赖 mock 或 test | ✅ | live smoke 必须走真实 OpenCTP 环境 | A2/A3 使用 OpenCTP paper account |
| E6 | 正式场景数不少于 6 个 | ✅ | 6 个场景已定义 | A1-A6 |

### 场景看板 / Scenario Board

| # | 场景 | 执行 | 结论 | 阻塞 | 证据/备注 |
| --- | --- | :---: | :---: | :---: | --- |
| A1 | Success 1: OpenCTP 模板可加载 | ✅ | ✅ | 是 | targeted pytest |
| A2 | Success 2: OpenCTP MD/TD live smoke 可跑 | ✅ | ✅ | 是 | `./evidence_a2_openctp_live_smoke.md` |
| A3 | Success 3: OpenCTP query/order dry-run 路径可复用 | ✅ | ✅ | 是 | `./evidence_a3_openctp_query_order_dry_run.md` |
| A4 | Failure 1: 普通 CTP 配置仍要求 BrokerID | ✅ | ✅ | 是 | targeted pytest |
| A5 | Failure 2: 默认不会武装 live-send | ✅ | ✅ | 是 | targeted pytest 覆盖 tracked 模板 |
| A6 | Boundary 1: OpenCTP TEST 与 real-account c2609 不混用 | ✅ | ✅ | 否 | `check_topic_governance.py` 通过 |

## 一、验收目标 / Goals

1. 让 OpenCTP TTS 7x24 成为当前优先测试目标。
2. 保持普通 CTP 配置校验严格；OpenCTP 当前官网配置使用 `BrokerID=9999`。
3. 真实外部模拟柜台证据补齐后才宣告交付通过。

## 二、验收范围 / Scope

### 覆盖（In Scope）

1. OpenCTP TTS 7x24 tracked example config。
2. `AllowEmptyBrokerID` 配置校验 contract。
3. scripts/topic 导航中的 OpenCTP-first 测试路径。

### 不覆盖（Out of Scope）

1. 申请 OpenCTP 模拟账号。
2. 下载或提交 TTS-CTPAPI runtime/SDK。
3. 默认开启 live-send。

## 三、前置条件 / Prerequisites

| 条件 | 类型 | 阻断开发 | 阻断验收 | 状态 | 备注 |
| --- | --- | :---: | :---: | :---: | --- |
| OpenCTP 本地账号密码 | 外部输入 | 否 | 是 | ✅ | 凭据已写入 ignored `.env` 并生成 ignored local config；不得写入仓库 |
| TTS-CTPAPI runtime/SDK | 外部输入 | 否 | 是 | ✅ | runtime/SDK 已放入 ignored `output/openctp/`；`check_rust_gate.py` 已通过 |
| OpenCTP 7x24 CTP 端口可达 | 外部网络 | 否 | 是 | ✅ | `trading.openctp.cn:30001/30011` TCP 可达 |
| tracked config/test/docs | 仓库产物 | 是 | 是 | ✅ | 当前已落地 |

## 四、验收专属 AI 边界 / Acceptance-Only AI Boundaries

1. 不得把 targeted pytest 写成真实 OpenCTP 连通通过。
2. 不得把 `AllowLiveOrderSmoke` 在 tracked 模板中设为 true。
3. OpenCTP 7x24 默认标的使用官方适合开发调试的 `TEST`，不得与 real-account `c2609` guardrails 混写。

## 五、验收场景 / Scenarios

| # | 场景 | 执行命令/步骤 | 预期结果 | 成功信号 | 失败口径 | 证据路径 |
| --- | --- | --- | --- | --- | --- | --- |
| A1 | Success 1: OpenCTP 模板可加载 | targeted pytest | 模板可解析、validate 通过 | `4 passed` 中包含 OpenCTP config test | 缺字段或默认武装 live-send | `./evidence_a1_config_contract.md` |
| A2 | Success 2: OpenCTP MD/TD live smoke 可跑 | `python scripts/ctp_md_login_smoke.py ...` + `python scripts/ctp_td_login_smoke.py ...` | MD/TD smoke 进入真实 OpenCTP 路径 | login/tick/readiness 字段结构化 | TCP 不通、runtime/SDK/账号缺失或登录失败 | `./evidence_a2_openctp_live_smoke.md` |
| A3 | Success 3: query/order dry-run 可复用 | query smoke + order lifecycle dry-run | 只读与 dry-run 入口可执行 | query/dry-run 输出结构化 | 把 OpenCTP 失败混成 real-account 失败 | `./evidence_a3_openctp_query_order_dry_run.md` |
| A4 | Failure 1: 普通 CTP 仍要求 BrokerID | targeted pytest | 未显式允许时 validate 返回 `broker_id` | test passed | 普通配置被放宽 | `./evidence_a1_config_contract.md` |
| A5 | Failure 2: 默认不会武装 live-send | 读取 tracked 模板并 dry-run | `AllowLiveOrderSmoke=false` | live_send 不被武装 | tracked 模板可直接实发 | `./evidence_a5_live_send_default_guard.md` |
| A6 | Boundary 1: TEST 与 c2609 不混用 | docs/checks | OpenCTP TEST 与 real-account c2609 路径分层 | runbook 表述清晰 | 两条路径 guardrails 混写 | `./evidence_a6_docs_boundary.md` |

## 六、证据清单 / Evidence

| # | 证据类型 | 路径/链接 | 说明 |
| --- | --- | --- | --- |
| 1 | config contract | `./evidence_a1_config_contract.md` | targeted pytest 输出 |
| 2 | live smoke | `./evidence_a2_openctp_live_smoke.md` | MD/TD/instrument/aggregate live smoke 通过 |
| 3 | query/order dry-run | `./evidence_a3_openctp_query_order_dry_run.md` | account/position/query adapter/order dry-run 通过 |

## 七、未通过处理 / On Failure

1. 若失败来自账号/runtime/SDK 缺失，记录 blocked，不改代码硬过。
2. 若失败来自配置解析或 guardrail 退化，回到 `plan.md` P1/P2 修复。

## 八、真实验收待办清单 / Pending E2E Checklist

| # | 对应场景 | 当前阶段结果 | 还缺的真实验证 | 真实入口/命令 | 通过信号 | 阻塞项 | 证据路径 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| R1 | A2 | 通过 | OpenCTP live smoke | `python scripts/ctp_nautilus_live_smoke.py --config cfgs/local/<openctp-local>.json` | MD/TD 输出结构化且进入 OpenCTP 前置 | 无 | `./evidence_a2_openctp_live_smoke.md` |
| R2 | A3 | 通过 | query/order dry-run | query smoke + order lifecycle dry-run | 只读与 dry-run 输出结构化 | 无 | `./evidence_a3_openctp_query_order_dry_run.md` |

## 九、Contract/Function 锁定证据

| 项目 | 路径/命令 | 说明 |
| --- | --- | --- |
| Config contract | `python -m pytest tests/test_smoke_import.py -k "ctp_config_loads_repo_example or ctp_config_allows_empty_broker_id_only_when_explicit or ctp_config_loads_openctp_tts_7x24_example or ctp_config_accepts_myvnpy_connect_ctp_shape" -q --basetemp output/pytest-tmp` | 锁定普通 CTP 空 BrokerID strict validation 与 OpenCTP tracked example config |

## 十、最终结论 / Final Verdict

- **结论**：✅ 通过
- **日期**：2026-06-08
- **执行人**：Codex
- **建议**：可以宣告本 change 通过
- **说明**：配置、contract、本地 secret/config 生成、TTS 6.6.9 runtime/SDK、MD/TD live smoke、query/order dry-run 与 runbook 均已落地；OpenCTP paper evidence 不替代 formal-trading final evidence。
