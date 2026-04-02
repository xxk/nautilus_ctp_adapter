# Live Execution Client Bootstrap Evidence

**日期**：2026-04-02  
**change-id**：`20260402__nautilus-live-execution__live-execution-client-bootstrap`

## 一、冻结后的主线路径

当前最小 `LiveExecutionClient` 主线已经固定为：

```text
TD bootstrap
  -> capture td_session_identity
  -> debug submit/cancel mainline
  -> runtime bridge command queue
```

## 二、冻结后的输出模型

```text
CtpLiveExecutionClientBootstrapResult
  - execution_bootstrap
  - ready
  - td_session_identity
```

## 三、关键结论

1. `LiveExecutionClient` 的 bootstrap readiness 现在不只依赖 TD 登录成功，还要求 settlement ready 和 session identity 可用。
2. debug submit/cancel 主线已经能复用 `C2` 的 mapping contract，把 command 安全送进 runtime bridge。
3. 当前主线仍未默认开启真实 `TdOrderSend/TdOrderAction`。

## 四、验证结果

执行：

```powershell
python -m pytest
python -m pip install -e .
```

结果：

1. `43 passed`
2. editable install 成功

## 五、交接边界

这笔 change 已完成：

1. 最小 `LiveExecutionClient` bootstrap path
2. bootstrap 后复用 session identity 的 debug submit/cancel 主线

这笔 change 不完成：

1. 真实 order lifecycle smoke
2. 真发单 / 真撤单
3. execution topic 最终 closure
