---
change-id: "20260607__openctp-tts__test-baseline"
dependencies:
  hard_blocking: []
  soft_dependency:
    - id: "20260410__live-session-order-query-hardening__vendor-bridge-readiness-and-sdk-handoff"
      reason: "OpenCTP TTS still needs a compatible CTPAPI runtime/SDK pack before formal live smoke can pass"
      expected_status: blocked-completed
  blocked_by: []
  runtime_blocker: []
---

# OpenCTP TTS Test Baseline 开发计划

**状态**：已完成
**进度**：100%
**日期**：2026-06-08
**范围**：`cfgs/`、`src/nautilus_ctp_adapter/adapters/ctp/config.py`、`tests/`、`scripts/README.md`、`docs/topics/live-session-order-query-hardening.md`
**topic-id**：live-session-order-query-hardening
**execution_order**：1
**change-id**：20260607__openctp-tts__test-baseline
**关联 acceptance**：./acceptance.md

## 一、需求简述

1. 先采用 OpenCTP TTS 7x24 作为全天候开发调试目标。
2. 新增可复制到 `cfgs/local/` 的 OpenCTP TTS 7x24 配置模板。
3. 支持 OpenCTP 当前官网口径中的 7x24 `BrokerID=9999`、空 `AuthCode/AppID`；普通 CTP 配置校验仍保持严格。
4. OpenCTP 资料查询与 paper account 申请入口为 `http://www.openctp.cn/`；公开资料描述的注册动作需要操作者通过 OpenCTP/CTP开放平台公众号完成。
5. 本 change 不把账号密码、下载的 TTS-CTPAPI runtime/SDK、OpenCTP wheel 或 smoke output 写入仓库。

## 二、能力映射 / Capability Mapping

```text
- capability_id: openctp-tts-test-baseline
- capability_name: OpenCTP TTS 7x24 test baseline
- long_term_target: /D:/Nautilus/nautilus_ctp_adapter/docs/topics/live-session-order-query-hardening.md
- secondary_targets: /D:/Nautilus/nautilus_ctp_adapter/scripts/README.md
- decision_target: /D:/Nautilus/nautilus_ctp_adapter/docs/adr/ADR002 OpenCTP TTS Paper Simulation Test Environment.md
- affects_long_term_rules: 是
- change_type: 新增规则
```

## 三、AI 执行约束

1. 允许修改：当前 change 三件套、`cfgs/ctp.openctp.tts.7x24.example.json`、`config.py`、相关 tests、`scripts/README.md`、topic README。
2. 禁止修改：`cfgs/local/`、`vendor/`、真实账户凭据、任何会默认武装 `AllowLiveOrderSmoke=true` 的配置。
3. 当前正式入口优先使用：`python scripts/check_rust_gate.py`、`python scripts/ctp_nautilus_live_smoke.py --config cfgs/local/<openctp-local>.json`、只读 query smoke、dry-run order lifecycle smoke。
4. AI 开始前必须确认 OpenCTP 官方 TTS 7x24 前置、BrokerID、auth/app 口径。
5. 改完后必须执行：targeted pytest、`python scripts/check_change_docs.py --root .`；若 topic README 修改，执行 topic governance check。

## 四、背景与约束

1. 当前 real-account CTP 路线受私有 SDK/live DLL 与交易窗口制约。
2. OpenCTP TTS 7x24 提供 CTPAPI 兼容接口，适合作为全天候登录、行情、查询、下单链路开发调试目标。
3. [ADR002](../../adr/ADR002%20OpenCTP%20TTS%20Paper%20Simulation%20Test%20Environment.md) 已冻结 OpenCTP TTS 7x24 作为当前默认 paper simulation / development test environment。
4. OpenCTP 7x24 的当前官网前置为 TD `tcp://trading.openctp.cn:30001`、MD `tcp://trading.openctp.cn:30011`，`BrokerID=9999`，`AuthCode/AppID` 为空。
5. OpenCTP 7x24 live-send 仍是真实外部模拟柜台动作，默认必须保持 `AllowLiveOrderSmoke=false`，只在 operator 明确武装的本地 config 中开启。

## 五、任务清单

| 步骤 | 任务 | 来源 | 修改文件 | 产出 | 验证动作 | 回写目标 | 完成定义 | 状态 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| P1 | 支持显式空 BrokerID 配置 | A1/A4 | `config.py`、`tests/` | `AllowEmptyBrokerID` contract | targeted pytest | 无 | 显式兼容空 broker，普通 CTP 仍要求 broker；OpenCTP tracked default 使用 BrokerID `9999` | 已完成 |
| P2 | 新增 OpenCTP TTS 7x24 模板 | A1/A2 | `cfgs/`、`tests/` | tracked example config | targeted pytest | scripts README | 模板可加载且默认不武装 live-send | 已完成 |
| P3 | 回写优先测试路径 | A3/A5/A6 | `scripts/README.md`、topic README | OpenCTP-first runbook | docs checks | topic README | operator 知道先走 OpenCTP TTS 7x24 | 已完成 |
| P4 | 真实连通证据 | A2/A3 | 当前 change evidence | OpenCTP live smoke evidence | live smoke commands | acceptance | MD/TD/query/dry-run smoke 通过 | 已完成 |

## 六、验证动作

```powershell
python -m pytest tests/test_smoke_import.py -k "ctp_config_loads_repo_example or ctp_config_allows_empty_broker_id_only_when_explicit or ctp_config_loads_openctp_tts_7x24_example or ctp_config_accepts_myvnpy_connect_ctp_shape" -q --basetemp output/pytest-tmp
python scripts/check_change_docs.py --root .
python scripts/check_topic_governance.py --root .
python -m pytest tests/test_openctp_env_config.py -q --basetemp output/pytest-tmp -p no:cacheprovider
```

## 七、完成定义

### 开发完成

1. OpenCTP TTS 7x24 模板已存在且能被 `CtpAdapterConfig` 加载。
2. 空 BrokerID 只在显式 `AllowEmptyBrokerID=true` 时通过校验。
3. 脚本导航和 topic 入口明确 OpenCTP-first 测试路径。

### 交付完成

1. 本地 OpenCTP 账号、TTS-CTPAPI runtime/SDK 就绪。
2. `check_rust_gate.py` 不再因 runtime/SDK 缺口阻塞。
3. 本机到 OpenCTP 7x24 TD `30001` 和 MD `30011` 的 TCP 连接可达。
4. 至少完成一次 `ctp_nautilus_live_smoke.py` 或等价 MD/TD/query smoke 真实证据。

## 八、长期规则增量摘要 / Long-Term Rule Delta Summary

新增规则：在私有 real-account CTP 路线不可全天候验证时，优先使用 OpenCTP TTS 7x24 作为开发调试测试目标；但该路径仍必须使用本地未跟踪配置和本地 runtime/SDK 输入，不能把模拟账号或下载包写入仓库。

## 九、回写与相关变更 / Write-back & Related Changes

1. 已回写 `scripts/README.md` 的测试入口导航。
2. 已回写 live-session-order-query-hardening topic 的 blocked/unblock 口径，使 OpenCTP TTS 成为新优先解锁路径。

## 十、阻塞项

无。

## 十一、进度记录

1. 2026-06-07：确认 OpenCTP TTS 7x24 官方前置与 broker/auth/app 口径，开始落地配置模板和校验 contract。
2. 2026-06-07：已新增 OpenCTP TTS 7x24 tracked example config、`AllowEmptyBrokerID` contract、targeted pytest、scripts/topic 导航与当前 change bundle；真实 OpenCTP live smoke 仍等待本地账号和 TTS-CTPAPI runtime/SDK。
3. 2026-06-08：账号写入本地 `.env`，本地 config 由 `scripts/write_openctp_tts_config_from_env.py` 生成；OpenCTP TTS CTPAPI runtime/SDK 下载到 ignored `output/openctp/`，`check_rust_gate.py` 通过，PyO3 extension 通过本地构建产物同步后可导入。
4. 2026-06-08：按 `http://www.openctp.cn/simenv.html` 与 `TTS-CTPAPI.html` 校正到 `trading.openctp.cn:30001/30011`、`BrokerID=9999`，并改用官网 `tts_6.6.9.zip` 组装的 TTS 6.6.9 win64 SDK/runtime；MD、TD、instrument query、account/position/query adapter、order dry-run 与 `ctp_nautilus_live_smoke.py` 均通过，旧 TCP blocker 解除。
