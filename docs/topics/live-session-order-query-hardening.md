# Live Session Order Query Hardening Topic Roadmap

**创建日期**：2026-04-09
**最后更新**：2026-04-11
**状态**：进行中
**进度**：C1/C3/U1 bundles created；C3 已把 offhours 只读脚本面收口到统一 `flow-path / session-label / evidence-root / output-json` contract，并把剩余 `td_login`/MD leaf 也纳入同一 evidence namespace；runtime/compat pack sync path 与 `check_rust_gate.py` vendor-bridge readiness 口径已稳定；当前 active frontier 已从 C3 切到 U1，且已完成 gate / repo-only probe / formal-live / blocked-handoff 首批证据冻结，当前结果保持 blocked handoff，等待私有 SDK/live DLL 输入
**topic-id**：live-session-order-query-hardening
**domain**：nautilus_adapter
**用途**：利用可直连 CTP 的真实时间窗口，把 `nautilus_ctp_adapter` 现有 execution/query baseline 推进成更可操作的 session-window 开发主线：交易时段聚焦 `c2609` 一手真实下单开发，非交易时段聚焦资金、持仓与相关只读查询能力。

---

## 一、为什么现在值得单独开这个 topic

当前仓内已经完成过：

1. `nautilus-live-execution` 的真实下单 guardrails、submit/cancel mapping 与 order lifecycle smoke baseline
2. `position-account-query-baseline` 的 `POSITION / ACCOUNT` 正式 query baseline
3. `td-position-account-truth-merge` 与 `live-ops-truth-snapshot` 的 startup/query/reconciliation truth 收口

但现在还缺一个更贴近真实开发窗口的 topic，把这些已经存在的基线能力变成“按时间窗口推进”的正式工作面：

1. 开盘/交易时段如何安全地继续开发真实下单链路
2. 非交易时段如何稳定推进 `account / position / order / trade snapshot` 等非交易能力
3. 如何把“可以连上 CTP”的机会转成结构化 evidence，而不是零散临时验证

因此，这个 topic 不重复发明 execution/query baseline，而是把它们重组为可持续推进的 session-window capability hardening 主线。

## 二、主题目标

1. 把交易时段的真实下单开发收敛到单一口径：`c2609`、单笔 `1` 手、净持仓上限 `5` 手。
2. 把非交易时段可做的 `INSTRUMENT / ACCOUNT / POSITION / ORDER / TRADE` 相关只读查询整理成正式开发面。
3. 明确“当前时间窗口允许做什么、不允许做什么”的 session-window runbook。
4. 为后续更稳定的 live debug / operator playbook / evidence matrix 打基础。

## 三、实盘边界 / Session Guardrails

本 topic 继续使用真实账户与真实 CTP 连接，但必须继承并细化已有 execution guardrails：

1. 交易时段允许开发真实下单功能，但标的只允许 `c2609`。
2. 单笔报单数量最多 `1` 手。
3. 调试净持仓上限按 `5` 手处理。
4. 若当前净持仓未知，或已达到/超过 `5` 手，不允许新增开仓；只允许查询或减仓方向动作。
5. 非交易时段不允许发送新的报单、撤单、改单；只允许做 `account / position / order / trade` 等只读查询、truth merge 与 evidence 收集。
6. 不允许用 mock、fake、历史截图替代正式 live evidence。
7. 任何新脚本或新入口若无法明确区分“交易时段可交易模式”和“非交易时段只读模式”，不得宣告 topic ready。

## 四、进入条件

1. [nautilus-live-execution](../nautilus-live-execution/README.md) 已冻结的实盘 guardrails 继续有效。
2. [position-account-query-baseline](../position-account-query-baseline/README.md) 的 query contract 继续作为继承输入，而不是重新定义。
3. [live-ops-truth-snapshot](../live-ops-truth-snapshot/README.md) 当前仍保留为 parallel blocked topic；本 topic 已切为当前可推进的 active frontier，优先推进 offhours-first 开发面。
4. `python -m pytest`、`python -m pip install -e .`、`python scripts/check_rust_gate.py`、`python scripts/check_topic_docs.py` 保持可执行。
5. 本地 real-account live config 必须基于 [cfgs/ctp.live.example.json](/D:/Nautilus/nautilus_ctp_adapter/cfgs/ctp.live.example.json) 复制到忽略目录 `cfgs/local/ctp.live.025292.local.json` 后再填写真实 `Password/AuthCode/front/native path`，不得直接改 tracked 模板。
6. 开始任何真实交易动作前，必须先确认当日 CTP 可直连、`c2609` 处于可交易时间窗口、以及当前真实净持仓未突破 guardrail。

## 五、Topic 级出口条件

1. 已形成正式的 session-window runbook，明确交易时段与非交易时段的允许动作和验证路径。
2. `c2609` 的真实下单开发链路至少完成一轮正式证据闭环，能清楚区分 submit success、cancel success、trade fill 或预期失败。
3. 非交易时段的 `account / position` 查询与至少一种 `order / trade snapshot` 查询已形成稳定 evidence 口径。
4. live evidence 能明确区分“交易所休市/不可下单”“只读查询可执行”“CTP 断连/查询失败”这几类状态。
5. 后续操作者可以不依赖临时聊天说明，直接根据 topic + child change 文档判断当前该走交易开发还是只读开发。

## 六、预期 Child Change 顺序

| 顺序 | 建议 change-id | 作用 | 状态 |
| --- | --- | --- | --- |
| C1 | `20260409__live-session-order-query-hardening__session-window-guardrails-and-runbook` | 冻结交易时段/非交易时段边界、脚本入口与 evidence 口径 | 📝 已建包（runbook 已落地，待切 active） |
| C3 | `20260409__live-session-order-query-hardening__offhours-query-snapshot-hardening` | 在非交易时段补齐 `instrument / account / position / order / trade` 只读查询与失败语义 | 🟨 阻塞（脚本面已收口，剩余 blocker 已移交 U1） |
| U1 | `20260410__live-session-order-query-hardening__vendor-bridge-readiness-and-sdk-handoff` | 冻结 vendor-bridge readiness、SDK/live DLL handoff 与 unblock 条件 | 🔄 进行中（当前 active change） |
| C2 | `20260410__live-session-order-query-hardening__c2609-live-order-dev-loop` | 用 `c2609` 单笔 `1` 手的真实报单推进 submit/cancel/fill 开发闭环 | 📝 已建包（交易时段后置） |
| C4 | `20260410__live-session-order-query-hardening__session-evidence-and-operator-playbook` | 把 order/query 两条时间窗口能力收成操作者可执行 playbook 与 evidence matrix | 📝 已建包 |
| C5 | `20260410__live-session-order-query-hardening__aggregated-query-evidence-export` | 把 instrument/position/account/order-truth/reconciliation 聚合成单次 offhours 查询入口，并支持 evidence 导出 | 📝 已建包（持续开发 backlog） |
| C6 | `20260410__live-session-order-query-hardening__readonly-order-trade-snapshot-contract` | 冻结 `ORDER / TRADE` 只读快照 contract，与 callback truth 明确分层 | 📝 已建包（持续开发 backlog） |
| C7 | `20260410__live-session-order-query-hardening__query-flow-path-and-session-labeling` | 统一 offhours 入口的 `flow-path / session-label / evidence-root` 口径 | 📝 已建包（持续开发 backlog） |

## 七、AI-TASK-QUEUE

**当前状态**：已激活；当前聚焦 `U1`。

**当前优先策略**：C3 的脚本面 contract 已基本收口；当前保持 `U1` 为 active lane，沿唯一 gate / formal-live / repo-only 路径维护 `sdk-not-found / scaffold-only` blocked handoff，直到拿到私有 SDK/live DLL 输入。

- [x] 创建 topic roadmap
- [x] 创建 `C1` child change bundle
- [x] 创建 `C3` child change bundle
- [x] 创建 `U1` child change bundle
- [x] 创建 `C2` child change bundle
- [x] 创建 `C4` child change bundle
- [x] 创建 `C5` child change bundle
- [x] 创建 `C6` child change bundle
- [x] 创建 `C7` child change bundle
- [ ] 收口 `C1`
- [x] 推进 `C3` 到 blocked-closeout 或 real evidence 完成
- [x] 推进 `U1` 冻结 unblock checklist（P3 已完成：C2 解锁条件已写入 topic README）
- [ ] 完成 `C2`
- [ ] 完成 `C4`
- [ ] 完成 `C5`
- [ ] 完成 `C6`
- [ ] 完成 `C7`
- [ ] 回写 topic index、docs/README 与相关长期文档

**当前 first action**：`U1` 的 blocked handoff 已冻结完成（P1/P2/P3 全收口）。当前等待私有 SDK/live DLL 输入解锁 C2。

### C2 解锁条件 / C2 Unlock Trigger

以下三项**任一**满足即可解锁 `C2`（`c2609-live-order-dev-loop`）：

1. `vendor/ctp/sdk/` 下出现可被 `check_rust_gate.py` 识别的 full SDK（包含 `ThostFtdcTraderApi.h` 等头文件 + 对应 `.lib/.so`）。
2. 环境变量 `CTP_VENDOR_SDK_ROOT` 或 `CTP_SDK_ROOT` 指向有效 SDK 目录，且 `check_rust_gate.py` 输出 `vendor_bridge=ready`。
3. 外部 broad-root（如 `CTP_SDK_SCAN_ROOTS`）探测到有效 SDK，且 `check_rust_gate.py` 可从中解析出 SDK path。

解锁后的验证路径：`check_rust_gate.py` → `ctp_nautilus_live_smoke.py --config <path>` → 确认 TD login success → 进入 C2 live order dev loop。

**未解锁时**：保持 blocked handoff，不回退到 C3 或重复调 auth/front/credential。

### Autopilot 批次 / Autopilot Batches

| 批次 | 默认目标 | 对应 change | 启动条件 | 停止条件 | 当前状态 |
| --- | --- | --- | --- | --- | --- |
| B1 | 用现有 evidence 收口 session-window 规则与 runbook | `C1` | 不依赖私有 SDK/live DLL | runbook、场景矩阵与 queue 交接冻结 | ready-now |
| B2 | 继续把 offhours query/snapshot 口径推进到 blocked-closeout 或 real evidence 完成 | `C3` | 当前 active frontier | 新的最小缺口只剩 vendor bridge 或真实 evidence 回填 | completed-as-blocked-closeout |
| B3 | 冻结 vendor-bridge readiness、SDK/live DLL handoff 与 unblock checklist | `U1` | `check_rust_gate.py` 报 `sdk-not-found` 或 formal smoke 仍是 scaffold-only | ready/blocker/handoff 术语冻结完成 | completed-first-batch-blocked-handoff |
| B4 | 进入 `c2609` 单笔 `1` 手的 trade-window live order dev loop | `C2` | `U1` 明确 ready，且交易窗口可用 | live-send/guardrail/trade evidence 形成闭环 | gated |
| B5 | 收口 operator playbook、evidence matrix 与 closeout 导航 | `C4` | `C1/C2/C3/U1` 均已有可引用证据 | topic 进入稳定操作面或 closeout 阶段 | queued |
| B6 | 把 offhours 查询结果收成单次聚合入口，并补 evidence 导出 | `C5` | `C3` 基础 contract 收口，且仍需持续非交易开发 | 聚合入口稳定、evidence 导出冻结 | queued |
| B7 | 建立 `ORDER / TRADE` 只读快照 contract，与 callback truth 分层 | `C6` | 需要继续非交易时间开发 order/trade read-only | `ORDER / TRADE` 快照成功/失败语义冻结 | queued |
| B8 | 统一 `flow-path / session-label / evidence-root` 的 operator 口径 | `C7` | C5/C6 已明确入口与 evidence 归属 | 多入口 session 隔离与 evidence 命名冻结 | queued |

## 八、成功信号

1. 操作者能一眼判断当前时段应该走“交易开发”还是“只读查询开发”。
2. `c2609` 的真实下单开发不再靠口头 guardrail，而是有文档、入口和证据三层同时约束。
3. 非交易时段的查询功能不再只是历史 baseline，而是能稳定复用在当前 live debug 上下文中。
4. 真实证据可以复盘：当次会话里到底是连通问题、交易窗口问题、风控边界问题，还是业务实现问题。

## 九、与现有 Topic 的关系

1. 本 topic 继承 [nautilus-live-execution](../nautilus-live-execution/README.md) 已冻结的 `c2609 + 1 手 + 5 手上限` guardrails，不重复改写其主线结论。
2. 本 topic 继承 [position-account-query-baseline](../position-account-query-baseline/README.md) 的 query contract，但把它推进到更贴近当前 session-window 开发的使用方式。
3. 本 topic 不替代当前 active topic [live-ops-truth-snapshot](../live-ops-truth-snapshot/README.md)；在治理上它是下一轮更偏 live capability hardening 的候选主线。