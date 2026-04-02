# Exchange And Symbol Normalization Evidence

**日期**：2026-04-02  
**change-id**：`20260402__nautilus-instrument-provider__exchange-and-symbol-normalization`

## 一、冻结后的规则

### 1. 交易所归一化

当前冻结的最小 alias 规则：

1. `SHF -> SHFE`
2. `CZC -> CZCE`
3. `ZCE -> CZCE`
4. `DL -> DCE`
5. `CFF/CFE -> CFFEX`
6. `XINE -> INE`
7. `GFEX -> GFEX`

### 2. Symbol 大小写规则

当前冻结的大小写规则：

1. `SHFE / DCE / INE / GFEX` 使用小写合约代码
2. `CZCE / CFFEX` 使用大写合约代码
3. 这条规则当前只用于 shared adapter 中间模型，不直接宣称已等价于所有下游数据源格式

### 3. Product kind 归一化

当前冻结的最小映射：

1. `1 -> futures`
2. `2 -> option`
3. `3 -> combination`
4. `4 -> spot`
5. `5 -> efp`
6. `6 -> spot_option`
7. `7 -> tas`

### 4. 月份码与郑商所边界

1. 当前只提取 trailing `3-4` 位月份码。
2. `CZCE` 本轮只冻结大小写与 exchange 归一化，不提前做 `4位 -> 3位` 月份压缩。
3. 若后续需要引入 `CZCE` 的 `TA2609 -> TA609` 之类兼容变换，必须在后续 change 明确单独留证。

## 二、代码落点

1. normalization helper：
   `/D:/Nautilus/nautilus_ctp_adapter/src/nautilus_ctp_adapter/adapters/ctp/normalization.py`
2. provider normalized view：
   `/D:/Nautilus/nautilus_ctp_adapter/src/nautilus_ctp_adapter/adapters/ctp/instrument_provider.py`
3. tests：
   `/D:/Nautilus/nautilus_ctp_adapter/tests/test_smoke_import.py`

## 三、本地对照来源

这轮规则的本地对照主要参考：

1. `/D:/wt/myvnpy-main/core/contracts/utils.py`
2. `/D:/wt/myvnpy-main/core/contracts/contract_manager.py`

从这些样例可确认：

1. 交易所 alias 归一化是稳定需求
2. `SHFE/DCE/INE` 常见 lower-case symbol 规则有现成实践
3. `CZCE` 的 3 位/4 位月份码兼容属于独立问题，不应在本 change 偷偷混入

## 四、验证结果

执行：

```powershell
python -m pytest
python -m pip install -e .
```

结果：

1. `26 passed`
2. editable install 成功
