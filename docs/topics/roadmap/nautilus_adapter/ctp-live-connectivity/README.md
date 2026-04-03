# CTP Live Connectivity Topic Roadmap

**创建日期**：2026-04-01
**最后更新**：2026-04-02
**状态**：已完成
**进度**：Topic 1 / 5
**topic-id**：ctp-live-connectivity
**用途**：作为 `nautilus_ctp_adapter` 的长期主题路线图，管理 CTP 实盘连通、Nautilus 接线、以及后续运行时加固的 phase 顺序与 child change 队列。

---

## 一、主题目标

1. 在不侵入 Nautilus 主仓的前提下，建立可维护的 CTP 实盘适配链路
2. 让仓内维护的 `ctpnative`、共享 runtime、Nautilus adapter 三层边界稳定下来
3. 以真实账号与真实行情链路证明 `rb2610` 等期货合约可通过正式适配路径接入

---

## 二、Topic 定位

这是整个 `nautilus-ctp-adapter-mainline` 的第一个 topic。

它只解决三类问题：

1. 真实账户登录参数、依赖包和前置地址如何在本仓稳定落地
2. 仓内 runtime 能否接住真实 MD/TD 登录流程
3. Nautilus 后续接线所需的最小 live smoke 基线是否存在
4. 主线路径必须收敛到“本项目维护的本地 C wrapper”，不能继续演化成 C# 托管桥

这个 topic 明确不负责：

1. 完整 InstrumentProvider
2. 完整 LiveDataClient
3. 完整 LiveExecutionClient
4. 完整交易、对账、运维闭环

---

## 三、Topic 级出口条件

这个 topic 关闭前，至少要满足：

1. 账号 `025292` 的 live config 路径收敛，且敏感值不进入 tracked 文件
2. 仓内维护的 native pack / loader / `ctpnative` 口径冻结，且 C wrapper 归属明确在本项目
3. `rb2610` 行情可通过正式目标路径复现，不再依赖临时 C# host 或托管桥作为长期方案
4. TD 登录链路的成功口径、失败口径和缺失配置项被明确写清
5. 下一个 topic 可以在“已知 live 连通成立”的前提下继续做 InstrumentProvider 和 Nautilus 数据接线

---

## 四、Child Change 顺序

建议按下面顺序推进，不要并行打散：

| 顺序 | Change | 状态 | 作用 |
| --- | --- | --- | --- |
| C1 | `20260401__ctp-live-connectivity__login-025292-and-subscribe-rb2610` | 进行中 | 冻结 live config、native pack、`rb2610` 行情证据 |
| C2 | `20260401__ctp-live-connectivity__repo-owned-ctpnative-wrapper-bootstrap` | 已完成 | 把仓内维护的 `ctpnative` C wrapper 边界定下来，摆脱临时宿主依赖 |
| C3 | `20260401__ctp-live-connectivity__python-rust-md-login-path` | 已完成 | 把真实 MD 登录与订阅从临时 smoke 路径迁回 Python/Rust 主线 |
| C4 | `20260401__ctp-live-connectivity__td-auth-and-login-readiness` | 已完成 | 冻结 TD auth/login 正确输入顺序，并把历史 `ErrorID=63` 收敛成可复现的错误顺序问题 |
| C5 | `20260401__ctp-live-connectivity__nautilus-live-smoke-baseline` | 已完成 | 冻结正式 baseline 入口 `ctp_nautilus_live_smoke.py`，统一 `MD tick + TD readiness + bridge events` 通过口径 |

## 五、队列执行规则

1. `C1` 是本 topic 的 anchor evidence change；它允许在 `C2-C5` 推进期间保持 `in_progress`，因为它承载整条 Topic 1 的 live bootstrap 证据收口。
2. 除 `C1` 外，同一时刻只允许一个 implementation change 处于 `in_progress`。
3. `C1-C5` 已全部完成，本 topic 不再存在 implementation next action。
4. `C5` 完成后，必须回到 `C1` 补齐剩余 acceptance 空洞，随后整个 topic 才能标记为 completed。
5. 若 `C2-C5` 任一 change 发现需要新增长期规则，必须先回写当前 topic README，再继续后续 child change。

## 六、AI-TASK-QUEUE

**当前活动 Change**：`20260401__ctp-live-connectivity__login-025292-and-subscribe-rb2610`

**当前 implementation next action**：无；等待 mainline 切换到 `nautilus-instrument-provider`

- [x] `docs/changes/20260401__ctp-live-connectivity__login-025292-and-subscribe-rb2610`
- [x] `docs/changes/20260401__ctp-live-connectivity__repo-owned-ctpnative-wrapper-bootstrap`
- [x] `docs/changes/20260401__ctp-live-connectivity__python-rust-md-login-path`
- [x] `docs/changes/20260401__ctp-live-connectivity__td-auth-and-login-readiness`
- [x] `docs/changes/20260401__ctp-live-connectivity__nautilus-live-smoke-baseline`

---

## 七、当前已冻结的已知输入

1. `D:\3.9.3_Spec-Kit\src\providers\CTP\CTPProviderSwig.Tests\bin\Debug\net9.0\appsettings.Live.json`
2. `D:\3.9.3_Spec-Kit\src\providers\CTP\CTPProviderSwig.Tests\bin\Debug\net9.0\CtpSettings.json`
3. `D:\3.9.3_Spec-Kit\src\providers\CTP\CTPProviderSwig\native\bin`
4. `D:\3.9.3_Spec-Kit\QuantConnect\LeanWorkspaceRoll\bin\Plugins\Debug\net9.0`
5. `D:\wt\myvnpy-main\.vntrader\connect_ctp.json`

从这些样例可确认：

1. 仓内配置解析必须兼容中文键名，如 `用户名`、`密码`、`经纪商代码`
2. 前置地址应支持无 `tcp://` 前缀输入并做归一化
3. 登录配置与订阅列表应分离，因为 `connect_ctp.json` 只覆盖登录字段，不带 `instruments`
4. `Spec-Kit` live 样例中的 `AppID=client_iq_3.6.2` 与 `ProductInfo=iQuant` 说明：`myvnpy` 的中文键 `产品名称=client_iq_3.6.2` 更接近 `AppID`，不能仅当作 `ProductInfo`

---

## 八、Topic 级验收

1. 已存在安全、可复现的 live-config 路径，且敏感值不进入 tracked 文件
2. 仓内维护的 `ctpnative` 依赖包、loader 规则和运行时边界已足以复现真实行情接收
3. Python/Rust 主线已能接住真实 MD 登录与 `rb2610` 订阅
4. TD 登录 readiness 的缺口已被明确收敛，不再停留在“可能是配置问题”的模糊状态
5. Nautilus-targeted adapter 路径已成为正式方向，临时诊断工具不再承担长期实现职责
6. 托管 C# 层只保留为历史证据，不再作为新实现的允许落点
7. 正式 smoke baseline 已冻结为 `ctp_nautilus_live_smoke.py`

当前已知最关键的 TD readiness 结论：

1. `MD` 已通过真实前置 `106.75.173.28:51213` 收到 `rb2610` 行情
2. `TD` 已通过本仓本地 `c wrapper` 主线完成鉴权、登录与结算确认 smoke
3. 历史 `ErrorID=63` 已确认由错误的 `TdAuthenticate` 参数顺序触发
4. 冻结后的正确顺序为 `AppID -> AuthCode -> ProductInfo`

---

## 九、不在本层解决的内容

1. 单次 change 的命令输出原文
2. 单轮 smoke 的原始长日志
3. task 级燃尽表与逐步实现细节
4. 与某一笔 child change 强绑定的验收留证

---

## 十、与后续 Topic 的交接关系

本 topic 完成后，后续 topic 应按下面顺序接力：

1. `nautilus-instrument-provider`
   这里开始正式做合约查询、交易所映射、InstrumentProvider
2. `nautilus-live-marketdata`
   这里开始把已验证的行情链路接入 Nautilus `LiveDataClient`
3. `nautilus-live-execution`
   这里才开始推进完整交易侧能力

## 十一、相关设计文档

1. [Platform-neutral CTP runtime](/D:/Nautilus/nautilus_ctp_adapter/docs/architecture/platform-neutral-ctp-runtime.md)
2. [Rust / Python adapter split](/D:/Nautilus/nautilus_ctp_adapter/docs/architecture/rust-python-adapter-split.md)
3. [Runtime performance guidelines](/D:/Nautilus/nautilus_ctp_adapter/docs/architecture/runtime-performance-guidelines.md)
