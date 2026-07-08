# TD Mainline Scaffold Probe 证据 / Evidence

**日期**：2026-04-10
**状态**：❌ blocked
**用途**：确认当前 offhours mainline 的更根阻塞不是 auth/front，而是 `ctp_native.dll` 仍为 scaffold-only。

## 执行命令

```powershell
C:/Users/Administrator/.virtualenvs/.venv-1/Scripts/python.exe output/debug/td_mainline_probe.py
```

## 输出结果

```json
{"init_code": -9000, "authenticate_code": -9000, "login_code": -9000, "settlement_code": -1, "login_success": false, "login_error_id": -9000, "login_error_message": "repo-owned ctp_native scaffold only; live vendor bridge not implemented", "front_id": 0, "session_id": 0, "max_order_ref": 0, "disconnects": []}
```

## 配套事实

1. 当前 `vendor/ctp/bin/_synced_from.txt` 指向的 `repo_native` 来源为 `D:\Nautilus\nautilus_ctp_adapter\rust\target\debug`。
2. 当前机器未找到仓外 live `ctp_native.dll` 来源。
3. `D:\wt\main\.venv\Lib\site-packages\vnpy_ctp\api` 只提供 `thost*api*_se.dll`，不提供构建 `ctp_vendor_bridge` 所需的 SDK 头文件与 `thost*_se.lib`。

## 结论

1. A1/A2/A3 中看到的 `login_failed` 是当前 scaffold-only `ctp_native.dll` 下游症状，不是已经进入真实 vendor bridge 后的 auth/front 失败。
2. 当前要继续推进真实 offhours live smoke，首先需要外部 live `ctp_native.dll`，或本地补齐 CTP SDK 头文件/导入库后重建出启用 `ctp_vendor_bridge` 的 `ctp_native.dll`。