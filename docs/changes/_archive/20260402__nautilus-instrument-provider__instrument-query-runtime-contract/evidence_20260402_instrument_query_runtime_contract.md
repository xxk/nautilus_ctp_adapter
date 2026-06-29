# Instrument Query Runtime Contract Evidence

**日期**：2026-04-02  
**change-id**：`20260402__nautilus-instrument-provider__instrument-query-runtime-contract`

## 一、冻结后的 contract

本 change 冻结的 shared runtime / adapter query contract 是：

```text
QUERY_INSTRUMENTS
  -> INSTRUMENT (0..n)
  -> INSTRUMENT_END (1)
```

当前口径包含：

1. `QUERY_INSTRUMENTS` 由 adapter `InstrumentProvider` 发起，必须携带 `request_id`
2. `INSTRUMENT` 事件承载最小合约快照：
   `venue_symbol / exchange_id / product_class / instrument_name / price_tick / volume_multiple`
3. `INSTRUMENT_END` 负责明确结束信号，后续 change 不允许再用“无更多回调”代替结束语义

## 二、当前正式 adapter 入口

已冻结的最小 query bootstrap 入口：

```text
CtpInstrumentProvider.bootstrap_instrument_query_mainline()
```

它的职责是：

1. 通过共享 `runtime_bridge` 提交 `QUERY_INSTRUMENTS`
2. 复用 Topic 1 已冻结的 live/bootstrap 配置口径
3. 不新造新的 live smoke baseline

## 三、当前代码落点

1. Python runtime query state：
   `/D:/Nautilus/nautilus_ctp_adapter/src/nautilus_ctp_adapter/runtime/query.py`
2. Python bridge 集成：
   `/D:/Nautilus/nautilus_ctp_adapter/src/nautilus_ctp_adapter/runtime/bridge.py`
3. Adapter query bootstrap：
   `/D:/Nautilus/nautilus_ctp_adapter/src/nautilus_ctp_adapter/adapters/ctp/instrument_provider.py`
4. Rust placeholder parity：
   `/D:/Nautilus/nautilus_ctp_adapter/rust/ctp_runtime_core/src/query.rs`

## 四、验证结果

执行：

```powershell
python -m pytest
python -m pip install -e .
```

结果：

1. `22 passed`
2. editable install 成功

## 五、边界说明

1. 本 change 只冻结 query contract，不宣称已完成真实 instrument query。
2. symbol / exchange normalization 留给 Topic 2 的 `C2`。
3. 正式 `InstrumentProvider` bootstrap 留给 Topic 2 的 `C3`。
