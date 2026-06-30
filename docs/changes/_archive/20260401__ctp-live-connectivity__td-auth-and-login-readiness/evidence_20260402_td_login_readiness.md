# TD Auth / Login Readiness Evidence

**日期**：2026-04-02  
**change-id**：`20260401__ctp-live-connectivity__td-auth-and-login-readiness`

## 一、结论

本仓维护的本地 `c wrapper` 路径已经证明：

1. `TD` 鉴权与登录可以成功，不需要走 C# 托管桥。
2. `ErrorID=63` 的核心原因不是“配置模糊不对”，而是旧临时宿主把 `TdAuthenticate` 的参数顺序传错了。
3. 仓内冻结的 `TdAuthenticate` 正确口径是：

```text
TdAuthenticate(handle, app_id, auth_code, product_info)
```

不是：

```text
TdAuthenticate(handle, broker_id, app_id, auth_code)
```

## 二、成功场景

执行命令：

```powershell
python scripts\ctp_td_login_smoke.py --config D:\Nautilus\nautilus_ctp_adapter\cfgs\local\ctp.live.025292.rb2610.10675.json --timeout-seconds 20
```

关键结果：

```json
{
  "init_code": 0,
  "authenticate_code": 0,
  "login_code": 0,
  "settlement_code": 0,
  "login_success": true,
  "login_error_id": 0,
  "disconnects": []
}
```

关键控制台信号：

```text
TD Front Connected
TD Auto-auth: 0155/025292
TD Authenticate Success, proceeding to login
```

说明：

1. 这条链路只使用本仓维护的 `ctp_native.dll` 和 Python `ctypes` 边界。
2. 该结果足以证明 Topic 1 所需的 TD readiness 已成立。
3. 这不是发单验收；只是交易前置的鉴权、登录、结算确认 readiness。

## 三、失败场景

为了复现历史 `ErrorID=63`，使用同一条本地 `c wrapper` 链路，故意按错误顺序调用：

```text
TdAuthenticate(handle, broker_id, app_id, auth_code)
```

关键结果：

```text
{'init_code': 0, 'authenticate_code': 0, 'login_code': 0, 'login_seen': False, 'disconnects': [4097, 4097, 4097, 4097, 4097, 4097, 4097, 4097]}
TD Authenticate Failed: ErrorID=63
```

说明：

1. 登录回调始终未到达。
2. 前置持续断开，断开原因可见为 `4097`。
3. 这条失败路径和历史临时宿主中的 `ErrorID=63` 现象一致，说明旧失败已被明确解释。

## 四、对 Topic 1 的意义

1. `C4` 现在已经把 `TD` 问题从“模糊配置风险”收敛成“调用口径已知、输入模型已知、错误顺序可复现”。
2. `C5` 可以在此基础上继续做 Nautilus 方向的 live smoke baseline。
3. Topic 4 的 execution 真正实现仍需单独推进，但不必再从 `TD` 鉴权参数摸索开始。
