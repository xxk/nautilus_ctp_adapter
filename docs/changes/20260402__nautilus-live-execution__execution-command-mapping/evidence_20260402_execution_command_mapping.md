# Execution Command Mapping Evidence

**日期**：2026-04-02  
**change-id**：`20260402__nautilus-live-execution__execution-command-mapping`

## 一、冻结后的中间模型

当前 execution command mapping 已冻结为以下稳定中间模型：

```text
CtpSubmitOrderIntent
CtpCancelOrderIntent
CtpExecutionError
CtpMappedOrderCommand
CtpTdSessionIdentity
```

## 二、冻结后的规则

1. submit mapping 必须依赖已建立的 `td_session_identity`
2. `order_ref` 从 `max_order_ref + 1` 开始分配
3. submit payload 当前稳定包含：
   - `side`
   - `quantity`
   - `limit_price`
   - `position_effect`
   - `order_type`
   - `time_in_force`
   - `order_ref`
   - `front_id`
   - `session_id`
4. cancel payload 当前稳定包含：
   - `order_ref`
   - `front_id`
   - `session_id`
5. guardrails 拒绝会返回稳定的 `CtpExecutionError`
6. 当前 mapping 只提交 runtime command，不触达真实 `TdOrderSend/TdOrderAction`

## 三、代码落点

1. `/D:/Nautilus/nautilus_ctp_adapter/src/nautilus_ctp_adapter/adapters/ctp/execution_client.py`
2. `/D:/Nautilus/nautilus_ctp_adapter/tests/test_smoke_import.py`

## 四、验证结果

执行：

```powershell
python -m pytest
python -m pip install -e .
```

结果：

1. `41 passed`
2. editable install 成功

## 五、交接边界

这笔 change 已完成：

1. submit / cancel runtime command mapping
2. `order_ref / front_id / session_id / error_id` 的稳定表达
3. guardrails 与 command mapping 的协同

这笔 change 不完成：

1. 正式 `LiveExecutionClient` 主线
2. 真发单 / 真撤单
3. order lifecycle smoke baseline
