---
change-id: "20260413__nautilus-host-integration__adapter-interface-design"
dependencies:
  hard_blocking: []
  soft_dependency:
    - id: "20260410__rust-ctp-runtime-cutover__python-native-path-retirement"
      reason: "依赖 Rust-owned PyO3 bridge 已完成，确保新 adapter 基于 PyO3 主路径构建"
      expected_status: completed
  blocked_by: []
---

# Nautilus Adapter Interface Design 接口设计冻结 开发计划

**状态**：completed
**进度**：100%
**日期**：2026-04-13
**范围**：`src/nautilus_ctp_adapter/adapters/ctp/`、`docs/architecture/`、当前 change bundle
**topic-id**：nautilus-host-integration
**change-id**：20260413__nautilus-host-integration__adapter-interface-design
**关联 acceptance**：./acceptance.md

> 本 change 采用 `plan.md + acceptance.md + ai_constraints.md + design.md` 四件套。原因：Nautilus 宿主集成涉及多个基类继承、Factory 模式、Config schema 和 EventBus 桥接设计，必须先冻结接口再实现。

## 一、需求简述

1. 冻结 CTP adapter 集成为 Nautilus TradingNode 原生 adapter 的接口设计。
2. 交付文档：`docs/architecture/nautilus-host-integration-design.md`，包含以下决策：
   - `CtpLiveDataClient(LiveMarketDataClient)` 必须实现的方法清单与映射关系
   - `CtpLiveExecutionClient(LiveExecutionClient)` 必须实现的方法清单与映射关系
   - `CtpLiveDataClientFactory` / `CtpLiveExecClientFactory` 创建模式
   - Config schema：`CtpDataClientConfig(LiveDataClientConfig)` / `CtpExecClientConfig(LiveExecClientConfig)`
   - InstrumentProvider 对接 Nautilus `InstrumentProvider` 基类的方式
   - 现有 standalone smoke 脚本的保留策略
3. 不做：不在本 change 编写任何实现代码，只冻结设计。
4. 完成信号：设计文档可支撑 C2/C3/C4 直接开始实现，不需要再讨论接口形状。

## 二、能力映射 / Capability Mapping

```text
- capability_id: nautilus-host-integration-design
- capability_name: Nautilus 宿主集成接口设计 / Nautilus Host Integration Interface Design
- long_term_target: /D:/Nautilus/nautilus_ctp_adapter/docs/architecture/nautilus-host-integration-design.md
- secondary_targets: /D:/Nautilus/nautilus_ctp_adapter/docs/topics/nautilus-host-integration.md
- decision_target: /D:/Nautilus/nautilus_ctp_adapter/docs/architecture/nautilus-host-integration-design.md
- affects_long_term_rules: 是
- change_type: 新增规则
```

## 三、AI 执行约束

1. 允许修改：当前 change bundle、`docs/architecture/nautilus-host-integration-design.md`（新建）、topic roadmap README。
2. 禁止修改：`src/`、`rust/`、`tests/`、`scripts/` 中的任何实现代码。
3. 当前正式参考：`nautilus_trader/live/data_client.py`、`nautilus_trader/live/execution_client.py`、`nautilus_trader/live/factories.py`、`nautilus_trader/adapters/interactive_brokers/`。
4. AI 开始前必须阅读：本 change bundle、topic README、`docs/architecture/pyo3-bridge-design.md`、`docs/architecture/platform-neutral-ctp-runtime.md`、Nautilus 上游 adapter 基类源码。
5. 改完后必须执行：`python scripts/check_change_docs.py --root .`、`python scripts/check_harness.py`。

## 四、背景与约束

1. 现有 `CtpDataClient` / `CtpExecutionClient` 已包含完整的 MD/TD 生命周期管理（bootstrap、subscription、tick callback、order lifecycle、position/account query）。
2. 集成目标是**包装**而非**重写**——新的 Nautilus adapter 类内部复用现有 client，不重复实现 CTP 通信逻辑。
3. Nautilus 使用 asyncio event loop；现有 CTP adapter 主要是同步 poll/callback 模式。需要设计 async 桥接方案。
4. Nautilus `LiveMarketDataClient.__init__` 需要 `loop`, `msgbus`, `cache`, `clock` 等参数，不能沿用现有的简单 `CtpDataClient.__init__`。

## 五、设计方案

详见 sibling `design.md`。

## 六、阶段划分

1. P1：阅读 Nautilus 上游基类源码，确认必须实现的方法与参数。
2. P2：设计方法映射表（现有 CTP client 方法 → Nautilus adapter 方法）。
3. P3：设计 Config schema 与 Factory 模式。
4. P4：设计 async 桥接方案（同步 callback → asyncio event loop）。
5. P5：冻结设计文档，回写 architecture。

## 七、任务清单

<!-- TASK-LIST-BEGIN -->
- [x] T1: 阅读 Nautilus 上游 LiveMarketDataClient 和 LiveExecutionClient 源码，提取必须实现的方法签名
- [x] T2: 阅读 IB adapter 实现作为参考，确认 Factory + InstrumentProvider 模式
- [x] T3: 设计 CtpLiveDataClient 方法映射（现有 CtpDataClient → Nautilus 接口）
- [x] T4: 设计 CtpLiveExecutionClient 方法映射（现有 CtpExecutionClient → Nautilus 接口）
- [x] T5: 设计 Config schema 和 Factory 创建模式
- [x] T6: 设计 async 桥接方案（sync callback → asyncio integration）
- [x] T7: 撰写 docs/architecture/nautilus-host-integration-design.md
- [x] T8: 回填 acceptance.md 并验证治理闭环
<!-- TASK-LIST-END -->

## 八、验证动作

```bash
python scripts/check_change_docs.py --root .
python scripts/check_harness.py
```

## 九、完成定义

### 开发完成

1. `docs/architecture/nautilus-host-integration-design.md` 已创建并包含完整的接口映射、Config schema、Factory 模式和 async 桥接方案。
2. C2/C3/C4 可以直接基于本设计开始实现，无需再讨论接口形状。

### 交付完成

1. `acceptance.md` 中所有场景通过。
2. 设计文档已回写到 `docs/architecture/`。
