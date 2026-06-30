# Live Startup Runbook

**日期**：2026-04-02  
**topic-id**：`live-ops-and-reconciliation`  
**change-id**：`20260402__live-ops-and-reconciliation__live-startup-runbook`

## 一、用途

这份 runbook 用来冻结 `nautilus_ctp_adapter` 的最小 live 启动路径。

它只回答 3 个问题：

1. 正式主线入口是什么
2. 诊断入口是什么
3. 遇到异常时先从哪一层排查

## 二、正式入口与分层

### 正式主线入口

1. 包与仓库验证

```powershell
python -m pip install -e .
python -m pytest
python scripts/check_topic_docs.py
python scripts/check_rust_gate.py
```

2. 最小 live bootstrap

```powershell
python scripts/ctp_nautilus_live_smoke.py --config <path>
```

这条命令是当前仓库唯一的正式 live 启动基线。  
它应同时验证：

1. `MD` 登录
2. `rb2610` 首个 tick
3. `TD` 鉴权、登录与结算确认
4. shared runtime bridge 在 Nautilus 方向的事件流

### Topic 4 继承入口

在 Topic 5 中，下面这些脚本不再是“主入口”，但它们是正式主线的已冻结下游能力：

1. `python scripts/ctp_marketdata_smoke.py --config <path> --symbol rb2610`
2. `python scripts/ctp_order_lifecycle_smoke.py --config <path> --instrument c2609 --quantity 1 --limit-price <price>`

使用规则：

1. 先跑 `ctp_nautilus_live_smoke.py`
2. 只有在主线入口失败或需要局部定位时，才下钻到 marketdata/execution 子入口

### 诊断入口

以下属于 diagnostics，不是 mainline success 的直接替代品：

1. `python scripts/ctp_md_login_smoke.py --config <path>`
2. `python scripts/ctp_td_login_smoke.py --config <path>`
3. `python scripts/ctp_instrument_query_smoke.py --config <path> --symbol <symbol>`
4. `python scripts/ctp_live_data_client_bootstrap_smoke.py --config <path> --symbol <symbol>`

它们的职责是定位问题，不是宣告“live startup 已完成”。

## 三、启动前检查

在运行任何 live 脚本前，先确认：

1. 本机 Python 环境可正常执行仓内脚本
2. `ctpnative` 与依赖 DLL 已按仓库 loader 路径放置
3. live config 文件存在，且不把敏感值写回受版本控制目录
4. 当前目标只在 Nautilus 主线内工作，不回退到托管 C# 主线
5. 若要触达 execution，必须继承 Topic 4 冻结的 guardrails

### 本机 260603 CSV front 覆盖

当下面 3 个本机输入同时存在时，后续 live 登录验证默认直接使用它们，不再向操作者询问账号、front 或凭据：

1. `C:\Users\Administrator\Desktop\TradingServer_260603.csv`
2. `C:\Users\Administrator\Desktop\MarketDataServer_260603.csv`
3. `cfgs/local/ctp.live.025292.local.json`

使用规则：

1. CSV 只作为 front 来源；凭据、BrokerID、UserID、ProductInfo、AppID、AuthCode、Password 与合约列表继续来自本地 live config。
2. `TradingServer_260603.csv` 当前默认 TD front 为 `tcp://180.168.159.225:51205`。
3. `MarketDataServer_260603.csv` 当前默认 MD front 为 `tcp://180.168.159.225:51213`。
4. 不把凭据或生成后的 live config 写入受版本控制目录，不在聊天或文档中展开敏感字段。
5. 运行前在仓库外生成临时 config，例如 `D:\Nautilus\_tmp\ctp_login_260603\<name>.json`，只覆盖 MD/TD front；运行结束后删除。
6. Windows 控制台运行 TD login-only 诊断时设置 `PYTHONIOENCODING=utf-8`，避免 CTP 返回中文错误文本时触发本地编码异常。

默认执行顺序：

```powershell
python scripts/check_rust_gate.py
python scripts/ctp_md_login_smoke.py --config <temp-config> --timeout-seconds 20
python scripts/ctp_nautilus_live_smoke.py --config <temp-config> --md-timeout-seconds 20 --td-timeout-seconds 20
$env:PYTHONIOENCODING = "utf-8"
python scripts/ctp_td_login_smoke.py --config <temp-config> --timeout-seconds 20
```

2026-06-03 本机结果口径：

1. `check_rust_gate.py` 通过。
2. 使用 CSV front 的 `ctp_md_login_smoke.py` 通过，MD 登录、订阅与首个 `rb2610` tick 均成功。
3. 使用 CSV front 的 `ctp_nautilus_live_smoke.py` 到达真实 TD 请求路径，但 TD 登录回调返回 `login_error_id=3`，主线结果为 `td_login_failed`。
4. 使用原本 local config TD front 单独跑 `ctp_td_login_smoke.py` 也返回同类 `login_error_id=3`，所以后续不要再把该结果优先归因为 CSV front 缺失或需要重新询问 front。

2026-06-16 本机补充口径：

1. `vendor/ctp/bin` 当前同步的是 OpenCTP TTS 6.6.9 runtime/SDK，不应直接用于判断正式 broker 账号 `025292` 的 TD readiness。
2. `025292` 对应的本机 operator-trusted runtime/SDK 位于 `output/vnpy_ctp_clone/vnpy_ctp/api`，其 API family 为 6.7.x。
3. 两套 runtime 的 CTP factory ABI 不同：6.6.9 TD 导出 `CreateFtdcTraderApi(const char*)`，6.7.x TD 导出 `CreateFtdcTraderApi(const char*, bool)`；MD 也相应多出 `bIsProductionMode` 参数。
4. 使用 6.6.9 bridge/runtime 连接 `025292` formal front 会产生误导性的 disconnect-only 或 DLL load failure；必须用 6.7.x SDK/runtime 重建 bridge 后再判断正式 TD 登录状态。
5. 更新本地凭据并使用 6.7.x runtime 后，真实 `025292` TD 登录、结算确认和 `TdQryAccount` 已成功；证据见 `docs/changes/20260403__position-account-query-baseline__account-query-smoke/evidence_20260616_account_query_6_7_runtime.md`。
6. 具体登录和资金查询步骤见 [ctp_025292_login_runbook.md](./ctp_025292_login_runbook.md)。

## 四、标准启动顺序

### Phase 1: 仓库门禁

```powershell
python -m pip install -e .
python -m pytest
python scripts/check_topic_docs.py
python scripts/check_rust_gate.py
```

判定规则：

1. `pytest` 必须通过
2. topic docs gate 必须 `failures=0`
3. Rust gate 若失败，必须明确是 `cargo-not-found` 或 workspace check 失败，不允许模糊跳过

### Phase 2: 正式 live bootstrap

```powershell
python scripts/ctp_nautilus_live_smoke.py --config <path>
```

判定规则：

1. 必须看到 `MD` 登录成功
2. 必须拿到目标合约首个行情事件
3. 必须看到 `TD` readiness 成功信号
4. 必须确认 shared runtime bridge 有事件输出

### Phase 3: 定向定位

只有在 Phase 2 失败时才继续：

1. `MD` 问题：跑 `ctp_md_login_smoke.py` 或 `ctp_marketdata_smoke.py`
2. `TD` 问题：跑 `ctp_td_login_smoke.py`
3. 合约问题：跑 `ctp_instrument_query_smoke.py`
4. data client 问题：跑 `ctp_live_data_client_bootstrap_smoke.py`
5. execution 生命周期问题：跑 `ctp_order_lifecycle_smoke.py`

## 五、Execution 相关特别约束

`025292` 是实盘账户，所以 Topic 5 runbook 只继承，不放宽 Topic 4 guardrails：

1. 调试下单只允许 `c2609`
2. 单笔报单最多 `1` 手
3. 调试净持仓上限按 `5` 手处理
4. 任意 `1` 分钟窗口报单次数不得超过 `10` 次
5. 一档价原则：`BUY -> ask1`，`SELL -> bid1`
6. 缺少 `AllowLiveOrderSmoke=true` 与脚本显式 `--live-send` 时，不得触发真实发送路径

## 六、成功信号

当前 Topic 5 的 `C1` 不要求新增业务能力，它要求的是“启动路径可执行且分层清楚”。  
所以 runbook 通过的信号是：

1. 主线入口明确
2. diagnostics 入口明确
3. 启动顺序明确
4. execution guardrails 被显式继承
5. 现有仓库门禁与测试未被 runbook 变更破坏

## 七、后续 Topic 5 子阶段如何继承本 runbook

1. `C2 reconnect-and-recovery-policy` 直接继承本 runbook 的 Phase 2/3 分层
2. `C3 audit-and-reconciliation-baseline` 继承本 runbook 的正式入口与证据路径
3. `C4 operational-evidence-matrix` 继承本 runbook 的成功信号与验证顺序
