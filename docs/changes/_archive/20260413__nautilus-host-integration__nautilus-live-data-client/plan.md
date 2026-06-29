---
change-id: "20260413__nautilus-host-integration__nautilus-live-data-client"
dependencies:
  hard_blocking:
    - id: "20260413__nautilus-host-integration__adapter-interface-design"
      reason: "接口设计已冻结，本 change 按冻结设计实现"
      expected_status: completed
  soft_dependency: []
  blocked_by: []
---

# Nautilus Live Data Client 集成 开发计划

**状态**：completed
**进度**：100%
**日期**：2026-04-13
**范围**：`src/nautilus_ctp_adapter/adapters/ctp/`
**topic-id**：nautilus-host-integration
**change-id**：20260413__nautilus-host-integration__nautilus-live-data-client
**关联 acceptance**：./acceptance.md

> 按冻结设计 `docs/architecture/nautilus-host-integration-design.md` 实现 `CtpLiveDataClient(LiveMarketDataClient)` 和 `CtpDataClientConfig(LiveDataClientConfig)`。

## 一、需求简述

1. 实现 `CtpLiveDataClient`，继承 Nautilus `LiveMarketDataClient`，内部复用现有 `CtpDataClient`。
2. 实现 `CtpDataClientConfig(LiveDataClientConfig, frozen=True)` 和 `CtpInstrumentProviderConfig`。
3. 实现 async 桥接：CTP sync callback → `loop.call_soon_threadsafe()` → asyncio event loop。
4. 不做：ExecutionClient、Factory、TradingNode 集成（C3/C4 范围）。
5. 完成信号：`CtpLiveDataClient` 可以独立实例化，`_connect()` / `_disconnect()` / `_subscribe_quote_ticks()` 通过单元测试。

## 二、能力映射 / Capability Mapping

```text
- capability_id: nautilus-live-data-client
- capability_name: Nautilus Live Data Client 集成 / Nautilus Live Data Client Integration
- long_term_target: docs/architecture/nautilus-host-integration-design.md
- secondary_targets: 无
- decision_target: docs/architecture/nautilus-host-integration-design.md
- affects_long_term_rules: 否
- change_type: 纯实现
```

## 三、AI 执行约束

1. 允许修改：`src/nautilus_ctp_adapter/adapters/ctp/` 下新建 `nautilus_config.py`、`nautilus_data.py`；修改 `__init__.py` 添加导出。
2. 禁止修改：现有 `data_client.py`、`execution_client.py`、`config.py`、`factory.py` 的签名和行为。
3. 当前正式参考：冻结设计 `docs/architecture/nautilus-host-integration-design.md` 第三、五、七节。
4. AI 开始前必须阅读：冻结设计文档、现有 `CtpDataClient` 类、`CtpAdapterConfig`。
5. 改完后必须执行：`python -m pytest tests/ -q`、`python scripts/check_change_docs.py --root .`、`python scripts/check_harness.py`。

## 四、任务清单

<!-- TASK-LIST-BEGIN -->
- [x] T1: 创建 nautilus_config.py（CtpDataClientConfig + CtpInstrumentProviderConfig + to_adapter_config）
- [x] T2: 创建 nautilus_data.py（CtpLiveDataClient 骨架 + _connect + _disconnect）
- [x] T3: 实现 _subscribe_quote_ticks / _unsubscribe_quote_ticks + tick callback 桥接
- [x] T4: 实现 _subscribe_instrument / _request_instrument 委托
- [x] T5: 更新 __init__.py 添加新类导出
- [x] T6: 编写单元测试验证类实例化和方法签名
- [x] T7: 回填 acceptance.md 并验证治理闭环
<!-- TASK-LIST-END -->

## 五、验证动作

```bash
python -m pytest tests/ -q
python scripts/check_change_docs.py --root .
python scripts/check_harness.py
```

## 六、完成定义

### 开发完成

1. `nautilus_config.py` 和 `nautilus_data.py` 已创建，含完整类型注解。
2. `CtpLiveDataClient` 的 P0 方法（_connect、_disconnect、_subscribe_quote_ticks、_unsubscribe_quote_ticks、_subscribe_instrument、_request_instrument）全部实现。
3. 单元测试通过。

### 交付完成

1. `acceptance.md` 中阻塞场景通过。
2. 治理检查通过。
