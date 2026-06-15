---
status: accepted
owner: architecture
adr_id: "ADR002"
decision_status: accepted
landing_status: completed
---

# ADR002 OpenCTP TTS / Paper Simulation Test Environment

- 日期：`2026-06-07`
- ADR 类型：standard
- 决策状态：accepted
- 落地状态：completed
- 落地摘要：completed via change `20260607__openctp-tts__test-baseline`
- 覆盖摘要：decision 1/1, config contract 1/1, live evidence 2/2
- 适用范围：`D:\Nautilus\nautilus_ctp_adapter`
- 决策问题：当前 CTP adapter 的全天候开发、TTS 与 paper simulation 测试默认采用哪个外部模拟环境。
- 当前倾向：采用 OpenCTP TTS 7x24 作为默认 paper simulation / development test environment。
- 最终决策：accepted；OpenCTP TTS 7x24 是当前默认测试环境，SimNow 和 real-account CTP 仍保留为上线前补充验证路径。

---

## 1. Problem Frame / 问题框架

当前 real-account CTP 与 SimNow 路径受交易窗口、账号、私有 SDK/live DLL、柜台可用性影响，不适合承担 nightly/weekend/CI-like 的持续调试目标。仓库需要一个明确的 paper simulation 默认环境，用于持续验证登录、订阅行情、查询、dry-run order lifecycle，以及在明确武装后验证模拟报单/撤单/成交回报链路。

OpenCTP TTS 提供 CTPAPI 兼容模拟柜台。OpenCTP 当前官网 `simenv.html` 列出 7x24 TD/MD 前置运行状态，`TTS-CTPAPI.html` 列出 7x24 环境参数：`BrokerID=9999`，`AppID/AuthCode` 为空；因此它适合作为本仓当前全天候测试默认环境。

### 1.1 Hard Constraints / 硬约束

1. OpenCTP TTS 7x24 只作为 paper simulation / development test default，不替代 real-account CTP 上线前最终验证。
2. OpenCTP 资料查询与 paper account 申请入口记录为 `http://www.openctp.cn/`；账号申请需要操作者通过 OpenCTP/CTP开放平台公众号等个人身份入口完成，账号、密码、下载的 TTS-CTPAPI runtime/SDK 只能作为本地输入，不能进入 Git；敏感值优先写入 ignored `.env`，再生成 ignored local config。
3. Tracked config 模板必须默认 `AllowLiveOrderSmoke=false`；模拟 live-send 必须由本地 config 和操作者显式武装。
4. OpenCTP tracked default 使用 `BrokerID=9999` 与 `AllowEmptyBrokerID=false`；空 `BrokerID` 只能通过显式 `AllowEmptyBrokerID=true` 作为兼容路径放行，普通 CTP 配置仍必须要求 `broker_id`。

### 1.2 Explicit Non-Goals / 明确不做

1. 本 ADR 不代替操作者申请 OpenCTP paper account，不处理微信/验证码/个人身份动作，也不托管 OpenCTP runtime/SDK。
2. 本 ADR 不改变 ADR001 的 native-first runtime 决策。
3. 本 ADR 不把 OpenCTP paper evidence 写成 real-account `c2609` 的最终生产证据。

### 1.3 Owner / Canonical Entry Impact

1. 新增配置语义 owner：`CtpAdapterConfig.allow_empty_broker_id`，只用于兼容明确允许空 BrokerID 的模拟柜台；OpenCTP 7x24 tracked default 不再使用该兼容路径。
2. 新增 tracked template：`cfgs/ctp.openctp.tts.7x24.example.json`。
3. 不新增新的 smoke entrypoint；继续复用 `check_rust_gate.py`、`ctp_md_login_smoke.py`、`ctp_td_login_smoke.py`、`ctp_nautilus_live_smoke.py` 和现有 query/order smoke。

### 1.4 概念判重 / Canonical Naming Check

| Candidate term | Layer / Owner | Existing nearby term | Collision risk | Decision | Guard / Evidence |
| --- | --- | --- | --- | --- | --- |
| `OpenCTP TTS 7x24` | external paper simulation environment | SimNow, real-account CTP | 可能被误读为生产柜台 | 采纳为默认 development test env | ADR002 + config template + scripts README |
| `paper simulation` | test environment class | live smoke, real acceptance | 可能被误写成实盘验收 | 采纳为模拟验收层，不替代 real-account final evidence | topic README boundary |
| `AllowEmptyBrokerID` | config field | `broker_id` required validation | 可能放宽所有 CTP 配置 | 只允许显式 opt-in | focused pytest |

---

## 2. 与既有 ADR / Architecture 的关系

1. ADR001 决定 runtime 主线仍是 native-first runtime + thin Python host glue；本 ADR 只决定外部测试柜台默认选择。
2. [runtime-performance-guidelines](../architecture/runtime-performance-guidelines.md) 仍约束 runtime 边界；OpenCTP 不改变 runtime owner。
3. [live-session-order-query-hardening](../topics/live-session-order-query-hardening.md) 负责把 OpenCTP-first 测试路径映射到可执行 child change。

---

## 3. 方案对比 / Options Comparison

| 方案 | 核心思路 | 适用场景 | 优点 | 缺点 / 风险 | 架构一致性 | 实施成本 | 结论 | 采纳与落地 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A. OpenCTP TTS 7x24 | 使用 CTPAPI 兼容 TTS 模拟柜台作为默认 paper test env | 夜间、周末、持续开发调试 | 7x24；覆盖登录/行情/查询/模拟交易链路；贴近 CTPAPI | 仍需本地账号和 TTS runtime/SDK；不能替代实盘最终证据 | 高 | 中 | 推荐 | accepted + completed |
| B. SimNow | 使用上期技术 SimNow 第一/第二套环境 | 上线前贴近国内期货 CTP 的补充验证 | 行业内常用；更贴近国内期货 CTP | 非全天候；窗口限制明显 | 高 | 中 | 补充 | retained as final pre-go-live supplement |
| C. Real-account CTP | 直接用期货公司仿真/实盘账号 | 上线前最终验证 | 最贴近真实柜台 | 时间窗口、风控和交易副作用约束高 | 高 | 高 | 补充/最终证据 | retained as final evidence path |
| D. Repo-only scaffold/mock | 只用本仓 scaffold 或 mock | Fresh clone bootstrap | 稳定、可本地跑 | 不能证明外部柜台链路 | 中 | 低 | 只作 bootstrap | debug-only |

### 3.1 Landing Evidence / 落地证据

| 方案 | decision_state | landing_state | evidence_state | evidence_ref | residual_risk |
| --- | --- | --- | --- | --- | --- |
| A | accepted | implemented | live_smoke_passed | `20260607__openctp-tts__test-baseline` + focused pytest + OpenCTP paper smoke evidence | real-account final evidence 仍需 formal-trading 路径 |
| B | included | not_implemented | docs_only | 本 ADR | 只作为上线前补充验证 |
| C | included | not_implemented | docs_only | topic `c2609` path | 受交易窗口和真实风控限制 |
| D | included | implemented | contract_locked | repo debug smoke tests | 不能作为 live evidence |

---

## 4. 决策 / Decision

### 4.1 决策结论 / Decision Summary

1. 当前默认 paper simulation / development test environment 采用 OpenCTP TTS 7x24。
2. SimNow 保留为贴近国内期货 CTP 的补充验证环境。
3. 期货公司 real-account 仿真/实盘路径保留为上线前最终证据路径。
4. Repo-only scaffold/mock 只用于 fresh clone bootstrap 和 contract lock，不得声明外部柜台链路通过。

### 4.2 决策边界 / Decision Boundaries

1. OpenCTP local config 必须由 ignored `.env` 通过 `python scripts/write_openctp_tts_config_from_env.py` 生成到 `cfgs/local/`；资料查询与 paper account 申请从 `http://www.openctp.cn/` 进入，具体账号申请由操作者在 OpenCTP/CTP开放平台公众号完成。
2. OpenCTP 7x24 默认 TD front 为 `tcp://trading.openctp.cn:30001`，MD front 为 `tcp://trading.openctp.cn:30011`。
3. OpenCTP 7x24 的 `BrokerID=9999`，`AuthCode/AppID` 为空；本仓 tracked default 使用 `AllowEmptyBrokerID=false`，`AllowEmptyBrokerID=true` 仅保留为显式兼容测试路径。
4. 默认 instrument 使用 `TEST`；real-account `c2609` guardrails 不与 OpenCTP `TEST` 混用。
5. OpenCTP TTS runtime/SDK readiness 仍必须通过本仓正式 gate 判定，不能只靠 config 字段存在。

### 4.3 Design Kernel / 设计内核

1. Test environment selection belongs to docs/config/runbook governance, not runtime architecture ownership.
2. Runtime and smoke entrypoints stay stable; changing the test counterparty must be a config/runtime-pack concern.
3. OpenCTP config differences are modeled explicitly, not hidden through silent validation downgrade.
4. Paper evidence can unblock development loops, but final production readiness still needs real-account or chosen broker validation.

### 4.4 推荐产物 / Recommended Deliverables

1. `cfgs/ctp.openctp.tts.7x24.example.json`
2. `AllowEmptyBrokerID` focused config test
3. scripts README OpenCTP-first run order
4. active child change `20260607__openctp-tts__test-baseline`

### 4.5 决策覆盖与落地矩阵

| 决策项 | 必须覆盖的落点 | 覆盖状态 | 承接 proposal / change | executable evidence | docs evidence | 剩余缺口 |
| --- | --- | --- | --- | --- | --- | --- |
| D1. OpenCTP TTS 7x24 is default paper env | config / docs / runbook | completed | `20260607__openctp-tts__test-baseline` | focused config pytest + OpenCTP live smoke | ADR002 + scripts README + topic README | 无 |
| D2. Empty BrokerID is explicit opt-in | config / tests | verified | `20260607__openctp-tts__test-baseline` | `test_ctp_config_allows_empty_broker_id_only_when_explicit` | ADR002 | 无 |
| D3. Paper evidence does not replace real-account final evidence | topic / acceptance docs | implemented | `20260607__openctp-tts__test-baseline` + future `c2609` change | docs gates | ADR002 + topic README | real-account evidence later |

---

## 5. Landing Map / 落地映射

### 5.0 Accepted Decision Boundary

Accepted:

1. OpenCTP TTS 7x24 is the default paper simulation and全天候 development test environment.
2. SimNow and real-account CTP remain supplemental/final validation paths.
3. Empty broker handling is explicit and scoped.

### 5.0.1 Not Accepted By This ADR

1. 不接受把 OpenCTP paper evidence 当作 real-account production readiness。
2. 不接受提交本地 OpenCTP 账号、密码、runtime 或 SDK。
3. 不接受 tracked 模板默认开启 live-send。

### 5.0.2 Successor Change Boundary

| Phase | 目标 | 承接 proposal / change | 退出条件 | retirement 影响 | 承接状态 |
| --- | --- | --- | --- | --- | --- |
| Phase 0 | ADR 决策冻结 | ADR002 | index 已登记为 binding | 无 | completed |
| Phase 1 | 配置模板与校验 contract | `20260607__openctp-tts__test-baseline` | tracked template + focused pytest | 无 | completed |
| Phase 2 | OpenCTP live smoke evidence | `20260607__openctp-tts__test-baseline` | 本地账号/runtime/SDK 就绪、TCP 30001/30011 可达并跑通 smoke | 无 | completed |
| Final | real-account final evidence | future `c2609` / real-account change | 上线前 real-account 证据补齐 | 无 | planned |

### 5.1 旧代码退役与文档收口

| 旧项 / 路径 | 当前职责 | 新归宿 / 替代物 | 处理动作 | 暂留边界 | 最终移除条件 | 文档同步项 | 承接状态 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| SimNow as implicit default | 历史默认外部模拟选择 | OpenCTP TTS 7x24 as paper default | 降级为 supplement | 上线前补充验证仍可用 | 不删除 | README/runbook/topic | active |
| Real-account CTP as all-purpose dev loop | 最终验证和实盘边界 | OpenCTP for全天候 dev, real-account for final evidence | 分层 | real-account 仍用于 final | 不删除 | topic/change acceptance | active |

---

## 6. Acceptance And Evidence

### 6.0 ADR-Level Acceptance Only

本 ADR accepted 的条件是环境选择和边界冻结；当前落地 closeout 已由 child change 留存 OpenCTP paper live smoke evidence。

### 6.1 Successor Acceptance Requirements

| ADR decision item | Required acceptance scenario | Positive path | Must fail if | Authority / retirement boundary | Minimal evidence |
| --- | --- | --- | --- | --- | --- |
| D1 | OpenCTP template loads and routes through existing smoke entries | `CtpAdapterConfig.from_json_file` + smoke scripts | tracked template requires secrets or live-send defaults true | config owner remains `CtpAdapterConfig` | focused pytest |
| D2 | Empty broker requires explicit opt-in | `AllowEmptyBrokerID=true` | ordinary empty broker config validates cleanly | normal CTP remains strict | focused pytest |
| D3 | Paper and real-account evidence stay distinct | topic/change docs | OpenCTP `TEST` evidence is claimed as `c2609` final readiness | OpenCTP and real-account paths stay separate | docs checks + later live evidence |

### 6.2 Architecture-Level Acceptance

1. ADR002 is binding once listed under current ADR constraints.
2. `20260607__openctp-tts__test-baseline` owns implementation and evidence.
3. ADR closeout moved `landing_status` to completed after OpenCTP live smoke evidence was stored in the child change.

### 6.3 ADR Closeout Distillation

Closeout 后只沉淀稳定结论：OpenCTP TTS 7x24 remains paper default, real-account CTP remains final evidence path. 一次性 smoke 输出留在 child change evidence，不复制进 ADR。

---

## 7. Related Documents / 关联文档

1. [OpenCTP repository](https://github.com/openctp/openctp)
2. [OpenCTP simulated environment monitor](http://www.openctp.cn/simenv.html)
3. [OpenCTP TTS-CTPAPI page](http://www.openctp.cn/TTS-CTPAPI.html)
4. [OpenCTP official site / paper account entry](http://www.openctp.cn/)
5. [OpenCTP TTS test baseline change](../changes/20260607__openctp-tts__test-baseline/plan.md)
6. [Live session order query hardening topic](../topics/live-session-order-query-hardening.md)
7. [Scripts README](../../scripts/README.md)
