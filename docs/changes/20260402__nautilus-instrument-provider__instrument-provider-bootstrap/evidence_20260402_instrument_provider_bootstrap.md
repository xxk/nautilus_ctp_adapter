# Instrument Provider Bootstrap Evidence

**日期**：2026-04-02  
**change-id**：`20260402__nautilus-instrument-provider__instrument-provider-bootstrap`

## 一、当前最小主线

本 change 之后，`InstrumentProvider` 已经不再只是 callback 占位，而是具备了稳定的最小 load 主线：

1. `bootstrap_instrument_query_mainline()`
2. `load_all_instruments_mainline()`
3. `load_result_for_request(request_id)`
4. `latest_load_result`

## 二、冻结后的输出模型

当前 provider 输出模型已经冻结为：

```text
CtpInstrumentProviderLoadResult
  - request_id
  - loaded
  - instrument_count
  - instruments: tuple[NormalizedCtpInstrument, ...]
```

说明：

1. `loaded` 表示 query 是否已收到 `INSTRUMENT_END`
2. `instrument_count` 与 `instruments` 必须一致
3. `NormalizedCtpInstrument` 继承 `C2` 已冻结的 normalization rule

## 三、代码落点

1. provider mainline：
   `/D:/Nautilus/nautilus_ctp_adapter/src/nautilus_ctp_adapter/adapters/ctp/instrument_provider.py`
2. provider public exports：
   `/D:/Nautilus/nautilus_ctp_adapter/src/nautilus_ctp_adapter/adapters/ctp/__init__.py`
3. tests：
   `/D:/Nautilus/nautilus_ctp_adapter/tests/test_smoke_import.py`

## 四、验证结果

执行：

```powershell
python -m pytest
python -m pip install -e .
```

结果：

1. `28 passed`
2. editable install 成功

## 五、边界说明

1. 本 change 只建立最小 provider bootstrap，不宣称真实 instrument query 已接通。
2. 正式 instrument smoke baseline 仍留给 `C4`。
3. 若后续能直接接上本仓 `TdQryInstrument` 的真实回调，本 change 的输出模型可直接复用，不需要重做 provider 对外接口。
