# TD Mainline Login Bootstrap Evidence

**日期**：2026-04-02  
**change-id**：`20260402__nautilus-live-execution__td-mainline-login-bootstrap`

## 一、冻结后的 execution bootstrap 主线

当前 execution 侧正式 TD bootstrap 主线已经固定为：

```text
execution bootstrap command
  -> repo-owned c wrapper TD auth/login
  -> settlement confirmation
```

对应代码落点：

1. `/D:/Nautilus/nautilus_ctp_adapter/src/nautilus_ctp_adapter/adapters/ctp/execution_client.py`
2. `/D:/Nautilus/nautilus_ctp_adapter/tests/test_smoke_import.py`

## 二、冻结后的输出模型

```text
CtpTdBootstrapState
  - started
  - connect_request_id

CtpExecutionBootstrapResult
  - bootstrap_state
  - td_smoke
```

## 三、真实验证

执行了仓内 bootstrap 主线验证，结果摘要：

```json
{
  "bootstrap_started": true,
  "connect_request_id": "td-connect-1",
  "command_kinds": ["connect"],
  "td": {
    "init_code": 0,
    "authenticate_code": 0,
    "login_code": 0,
    "settlement_code": 0,
    "login_success": true,
    "login_error_id": 0
  },
  "event_kinds": ["login_succeeded", "settlement_confirmed"],
  "settlement_seen": true
}
```

## 四、验证命令

```powershell
python -m pytest
python -m pip install -e .
python - <<'PY'
... run_td_mainline_login_bootstrap ...
PY
```

## 五、边界

这笔 change 已完成：

1. execution bootstrap 主线
2. bootstrap 输出模型
3. 与 guardrails 共存的 TD login / settlement 入口

这笔 change 不完成：

1. order send / cancel 映射
2. 真发单主线
3. order lifecycle smoke baseline
