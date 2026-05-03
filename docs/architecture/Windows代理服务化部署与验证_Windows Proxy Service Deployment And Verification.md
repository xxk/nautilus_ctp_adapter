# Windows代理服务化部署与验证 / Windows Proxy Service Deployment And Verification

**更新日期**：2026-04-11

## 一、目标 / Goal

本手册把 [多网卡代理入口与出口绑定方案 / Multi-NIC Proxy Ingress Egress Binding](./%E5%A4%9A%E7%BD%91%E5%8D%A1%E4%BB%A3%E7%90%86%E5%85%A5%E5%8F%A3%E4%B8%8E%E5%87%BA%E5%8F%A3%E7%BB%91%E5%AE%9A%E6%96%B9%E6%A1%88_Multi-NIC%20Proxy%20Ingress%20Egress%20Binding.md) 进一步收口成可落地的 Windows 服务化 runbook。

目标固定为：

1. 客户端统一连接 `10.168.80.56:3128` 或 `10.168.80.56:1080`
2. GitHub / Google / YouTube / Copilot 等交互敏感流量可切到 `10.168.80.56:3129`
3. 代理进程对外发起连接时强制绑定 `192.168.5.235`
4. 代理以稳定后台服务方式启动，而不是依赖手工前台进程

## 二、适用范围 / Scope

本手册覆盖：

1. `3proxy` 的目录布局
2. `3proxy.cfg` 的固定配置
3. 用 `NSSM` 托管为 Windows 服务的方式
4. 防火墙与最小验证步骤

本手册不覆盖：

1. 目标主机公网出口变更
2. 上游 NAT、ACL、核心交换机策略修改
3. 透明网关模式或 ICS 模式

## 三、前提条件 / Preconditions

部署前必须满足：

1. 本机同时拥有 `10.168.80.56` 与 `192.168.5.235`
2. `192.168.5.235` 所在网卡可以直接访问外网
3. 本机具备管理员权限，用于注册服务与防火墙规则
4. 已准备好 `3proxy.exe`
5. 已准备好 `NSSM`，即 `nssm.exe`
6. 仅承担代理入口的网卡不要保留公共 DNS，且其 `InterfaceMetric` 不应低于真实外网出口网卡

如果没有 `NSSM`，可以先用前台方式验证配置；但本手册的正式落地口径仍以 Windows 服务为主。

## 四、推荐目录布局 / Recommended Layout

建议固定目录如下：

```text
C:\opt\3proxy\
  3proxy.exe
  3proxy.cfg
  logs\
  docs\
  scripts\
  reports\

C:\opt\nssm\
  nssm.exe

C:\opt\
  代理服务导航_Proxy Service Index.md
```

要求：

1. `3proxy.exe` 与 `3proxy.cfg` 放在同一根目录，便于服务参数固定
2. `logs\` 单独预留，避免把日志写到系统目录
3. `nssm.exe` 单独存放，避免与业务二进制混放
4. 本机导航文档、验证脚本与验证报告也固定落在 `C:\opt\3proxy\` 下，避免后续在仓库与运行目录之间迷路

## 五、固定代理配置 / Fixed Proxy Configuration

建议的 `C:\opt\3proxy\3proxy.cfg` 内容如下：

```ini
daemon
log C:\opt\3proxy\logs\3proxy.log D
rotate 30
nserver 8.8.8.8
nserver 1.1.1.1
nscache 65536
timeouts 1 5 30 60 180 1800 15 60
auth none
allow *

proxy -p3128 -i10.168.80.56 -e192.168.5.235
proxy -p3129 -i10.168.80.56 -e192.168.5.235
socks -p1080 -i10.168.80.56 -e192.168.5.235
```

固定语义：

1. `-i10.168.80.56` 负责入口监听
2. `-e192.168.5.235` 负责出口绑定
3. `proxy -p3128` 提供 HTTP/HTTPS 显式代理
4. `proxy -p3129` 提供 GitHub / Google / YouTube / Copilot 交互敏感流量的专用 HTTP/HTTPS 显式代理
5. `socks -p1080` 提供 SOCKS5 代理

## 六、首次前台验证 / Foreground Validation

在注册服务前，先执行一次前台验证：

```powershell
C:\opt\3proxy\3proxy.exe C:\opt\3proxy\3proxy.cfg
```

预期：

1. 进程可正常启动
2. `C:\opt\3proxy\logs\3proxy.log` 被创建
3. 没有立即报绑定地址失败、端口占用或配置语法错误

如果前台都启动不了，不要继续注册服务，先修配置。

## 七、注册 Windows 服务 / Register As Windows Service

推荐使用 `NSSM`：

```powershell
C:\opt\nssm\nssm.exe install 3proxy-egress
```

在 `NSSM` 配置界面中固定以下字段：

1. `Application path`：`C:\opt\3proxy\3proxy.exe`
2. `Startup directory`：`C:\opt\3proxy`
3. `Arguments`：`C:\opt\3proxy\3proxy.cfg`

也可以直接用命令行方式写入：

```powershell
C:\opt\nssm\nssm.exe install 3proxy-egress C:\opt\3proxy\3proxy.exe C:\opt\3proxy\3proxy.cfg
C:\opt\nssm\nssm.exe set 3proxy-egress AppDirectory C:\opt\3proxy
sc.exe config 3proxy-egress start= delayed-auto
sc.exe failureflag 3proxy-egress 1
sc.exe failure 3proxy-egress reset= 86400 actions= restart/60000/restart/60000/restart/60000
```

注册完成后启动服务：

```powershell
Start-Service 3proxy-egress
```

开机自启动检查：

```powershell
Get-Service 3proxy-egress
```

期望状态：

1. `Status` 为 `Running`
2. `StartType` 为 `Automatic`
3. `sc.exe qc 3proxy-egress` 显示 `AUTO_START (DELAYED)`
4. `sc.exe qfailure 3proxy-egress` 显示失败后自动重启动作

## 八、防火墙规则 / Firewall Rules

至少放行这两个入口端口：

```powershell
New-NetFirewallRule -DisplayName "3proxy HTTP 3128" -Direction Inbound -Action Allow -Protocol TCP -LocalAddress 10.168.80.56 -LocalPort 3128
New-NetFirewallRule -DisplayName "3proxy HTTP 3129 Interactive" -Direction Inbound -Action Allow -Protocol TCP -LocalAddress 10.168.80.56 -LocalPort 3129
New-NetFirewallRule -DisplayName "3proxy SOCKS 1080" -Direction Inbound -Action Allow -Protocol TCP -LocalAddress 10.168.80.56 -LocalPort 1080
```

如果只打算提供一种代理协议，可以删去另一条规则。

## 九、主机侧验证 / Host-Side Verification

### 1. 服务状态

```powershell
Get-Service 3proxy-egress
sc.exe qc 3proxy-egress
sc.exe qfailure 3proxy-egress
```

### 2. 端口监听

```powershell
netstat -ano | findstr ":3128"
netstat -ano | findstr ":3129"
netstat -ano | findstr ":1080"
```

### 3. 日志创建

```powershell
Get-ChildItem C:\opt\3proxy\logs
```

判定标准：

1. 服务正在运行
2. `10.168.80.56:3128`、`10.168.80.56:3129` 或 `10.168.80.56:1080` 正在监听
3. 日志文件已生成

## 十、客户端验证 / Client-Side Verification

从其他机器验证 HTTP 代理：

```bash
curl -x http://10.168.80.56:3128 https://api.ipify.org
```

从其他机器验证 SOCKS5：

```bash
curl --socks5 10.168.80.56:1080 https://api.ipify.org
```

期望：

1. 能通过 `10.168.80.56` 成功连上代理
2. 返回的公网 IP 属于 `192.168.5.235` 所在出口网络
3. 不是客户端自己的公网出口

如果要验证本机浏览器链路，而不是其他客户端链路，先确认：

1. 两张物理网卡的 DNS 都使用干净解析器，例如 `8.8.8.8` 和 `1.1.1.1`
2. 当前用户 WinINet 系统代理已指向 `10.168.80.56:3128`
3. WinHTTP 代理也已同步到 `10.168.80.56:3128`

如果要长期跟踪稳定性，而不是只做一次性验收，建议在本机再加一条每小时采样任务：

```powershell
schtasks /Query /TN "3proxy-stability-hourly" /V /FO LIST
```

其本机固定入口为：

1. 采样脚本：`C:\opt\3proxy\scripts\collect_stability_snapshot.ps1`
2. 完整快照日志：`C:\opt\3proxy\reports\stability\stability_log.jsonl`
3. 简洁摘要日志：`C:\opt\3proxy\reports\stability\stability_summary.jsonl`
4. 摘要 CSV：`C:\opt\3proxy\reports\stability\stability_summary.csv`
5. 24 小时域名汇总脚本：`C:\opt\3proxy\scripts\summarize_domain_stability_24h.ps1`
6. 24 小时域名汇总报告：`C:\opt\3proxy\reports\stability\domain_stability_24h.md`
7. 当前域名告警状态：`C:\opt\3proxy\reports\stability\alerts\current_domain_alert.md`
8. 域名告警历史：`C:\opt\3proxy\reports\stability\alerts\alert_history.jsonl`
9. 性能采样脚本：`C:\opt\3proxy\scripts\collect_proxy_performance_snapshot.ps1`
10. 交互专用性能快照：`C:\opt\3proxy\reports\performance\interactive\latest.md`
11. 交互专用性能告警状态：`C:\opt\3proxy\reports\performance\interactive\alerts\current_performance_alert.md`
12. 性能快照报告：`C:\opt\3proxy\reports\performance\latest.md`
13. 当前性能告警状态：`C:\opt\3proxy\reports\performance\alerts\current_performance_alert.md`

长期看稳定性时，优先读下面两个域名级字段：

1. `bad_domain_count`
2. `bad_domain_values`

原因：

1. 本次会话里出现过的异常 IP 基本没有可靠 PTR
2. 真正可操作的判断口径不是“异常 IP 属于哪个域名”，而是“哪个被跟踪域名命中了异常 IP”
3. 当前重点盯的域名是 `www.google.com` 与 `www.youtube.com`

如果要快速看最近 24 小时域名稳定性，而不是逐条翻 `jsonl`，直接执行：

```powershell
& C:\opt\3proxy\scripts\summarize_domain_stability_24h.ps1
```

补充说明：

1. `collect_stability_snapshot.ps1` 每次采样结束后会自动刷新这份 24 小时报表
2. `domain_stability_24h.md` 适合作为人工巡检入口，`domain_stability_24h.json` 适合作为后续脚本消费入口
3. `summarize_domain_stability_24h.ps1` 刷新 24 小时报表后，还会继续调用 `publish_domain_stability_alert.ps1`，把当前域名告警状态写入 `alerts\current_domain_alert.md/json`
4. 若 `anomaly_sample_count > 0`，告警脚本会优先写 `alerts` 目录，再尝试写 Windows Application Event Log，并向当前桌面会话发送消息
5. 当前计划任务 `3proxy-stability-hourly` 以 `SYSTEM` 身份执行，所以桌面消息只能视为 best-effort；真正稳定的告警入口仍是 `alerts` 目录与 Event Log

如果要监控本机代理性能，而不是只看可用性，推荐改成“两层性能监控”：

```powershell
schtasks /Query /TN "3proxy-performance-light-15min" /V /FO LIST
schtasks /Query /TN "3proxy-performance-0500" /V /FO LIST
schtasks /Query /TN "3proxy-performance-1700" /V /FO LIST
schtasks /Query /TN "3proxy-performance-interactive-15min" /V /FO LIST
```

其本机固定入口为：

1. 总览刷新脚本：`C:\opt\3proxy\scripts\refresh_performance_overview.ps1`
2. 总览首页：`C:\opt\3proxy\reports\performance\性能总览_Performance Overview.md`
3. 总览 JSON：`C:\opt\3proxy\reports\performance\performance_overview.json`
4. 统一脚本：`C:\opt\3proxy\scripts\collect_proxy_performance_snapshot.ps1`
5. 交互专用快照：`C:\opt\3proxy\reports\performance\interactive\latest.md`
6. 交互专用告警：`C:\opt\3proxy\reports\performance\interactive\alerts\current_performance_alert.md`
7. 轻量快照：`C:\opt\3proxy\reports\performance\latest.md`
8. 轻量告警：`C:\opt\3proxy\reports\performance\alerts\current_performance_alert.md`
9. 汇总快照：`C:\opt\3proxy\reports\performance\summary\latest.md`
10. 汇总告警：`C:\opt\3proxy\reports\performance\summary\alerts\current_performance_alert.md`
11. 轻量摘要日志：`C:\opt\3proxy\reports\performance\performance_summary.jsonl`
12. 汇总摘要日志：`C:\opt\3proxy\reports\performance\summary\performance_summary.jsonl`

当前正式调度口径：

1. `3proxy-performance-interactive-15min`：每 `15` 分钟运行一次，使用 `interactive/light` 口径并固定观测 `3129`
2. `3proxy-performance-light-15min`：每 `15` 分钟运行一次，使用 `light` profile
3. `3proxy-performance-0500`：每天 `05:00` 运行一次，使用 `summary` profile
4. `3proxy-performance-1700`：每天 `17:00` 运行一次，使用 `summary` profile
5. 四条任务统一使用 `C:\Program Files\PowerShell\7\pwsh.exe` 执行脚本，而不是 `powershell.exe`

当前首页读取口径：

1. 日常巡检默认先打开 `C:\opt\3proxy\reports\performance\性能总览_Performance Overview.md`
2. 若总览页显示问题主要来自 `interactive` 层，再打开 `interactive\latest.md` 与 `interactive\alerts\current_performance_alert.md`
3. 若总览页显示问题主要来自 `light` 层，再打开 `latest.md` 与 `current_performance_alert.md`
4. 若需要确认慢站点或趋势，再打开 `summary\latest.md` 与其告警文件
5. 每次 `collect_proxy_performance_snapshot.ps1` 完成 `interactive`、`light` 或 `summary` 采样后，都会自动刷新总览首页；如果只想重建首页，可单独运行 `refresh_performance_overview.ps1`

推荐理由：

1. `interactive` 层把 GitHub / Google / YouTube / Copilot 交互链路从共享流量里分离出来，但仍保持同一条 `192.168.5.235` 出口
2. `light` 层优先服务“共享代理现在要不要调整”
3. `summary` 层优先服务“趋势判断”和“慢站点观察”，保留更完整的延迟视角
4. 三层分目录输出，避免频繁监控覆盖汇总结论
5. 统一切到 `pwsh.exe` 后，计划任务与当前开发/实测环境一致，避免 Windows PowerShell 5.1 对脚本语法的兼容性失败

如果要在 `10.168.80.58` 上把 GitHub / Google 相关域名切到专用交互口，同时确保所有流量仍经 `192.168.5.235` 出网，建议使用 PAC：

1. 文件路径：`C:\opt\3proxy\pac\80.58_交互分流代理规则_Interactive Proxy Split.pac`
2. GitHub / GitHub API / GitHub Copilot / Google / YouTube 相关域名优先走 `10.168.80.56:3129`
3. 其他域名继续走 `10.168.80.56:3128`
4. 即使 `3129` 不可用，PAC 仍会退回 `3128`，不会转成直连

建议优先盯下面这些性能字段：

1. `status_level`
2. `average_latency_ms` 与 `max_latency_ms`
3. `established_connection_count`
4. `request_count_5m`
5. `top_connected_clients`

看到异常时，建议按下面顺序调整：

1. `CPU` 与连接数一起高：优先看 `top_connected_clients`，先找单一异常来源，再决定是否限流或 ACL
2. 延迟高但 `request_count_5m` 不高：优先排查 DNS、出口网关和上游站点，不要先重启 `3proxy`
3. 最近 5 分钟请求量高，且目标高度集中：先判断是否业务高峰；若不是，先从异常客户端或异常目标模式下手
4. 内存高但连接数不高：先保留连续样本，再安排低峰重启并比对回落，避免把瞬时波动误判为泄漏
5. `possible_error_line_count_5m` 上升：先看 `3proxy` 最新日志和域名告警，区分域名侧问题和代理侧问题

## 十一、故障定位顺序 / Troubleshooting Order

按这个顺序排：

1. `Get-Service 3proxy-egress` 看服务是否已启动
2. `netstat` 看端口是否监听在预期地址
3. 看 `3proxy.log` 是否有配置语法错误或 bind 失败
4. 看 `route print`，确认默认出网仍走 `192.168.5.235` 所在网络
5. 从客户端做一次 `curl`，区分“连不上代理”还是“代理能收但外连失败”
6. 若 `google.com` 可达但 `www.google.com` 超时或证书异常，先查系统 DNS 是否返回了异常地址，再核对 `3proxy.cfg` 中的 `nserver` 是否仍是旧值
7. 若 `youtube.com`、`google.com` 等域名仍偶发漂到异常 IP，先确认入口网卡没有公共 IPv4 DNS，且其 `InterfaceMetric` 高于外网出口网卡

## 十二、运维结论 / Operational Verdict

对于“入口固定 `10.168.80.56`，出口固定 `192.168.5.235`”的场景，推荐的正式落地方式是：

1. 用 `3proxy` 处理代理协议与双地址绑定
2. 用 `NSSM` 把 `3proxy` 固定成 Windows 服务
3. 用防火墙和 `curl` 把入口、监听和出口公网结果串成同一条验证链路

这样落地后，代理不再依赖人工前台启动，验证口径也固定成可重复执行的 runbook。