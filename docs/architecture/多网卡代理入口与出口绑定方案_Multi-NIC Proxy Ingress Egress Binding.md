# 多网卡代理入口与出口绑定方案 / Multi-NIC Proxy Ingress Egress Binding

**更新日期**：2026-04-11

## 一、目标 / Goal

本方案用于把同一台 Windows 主机同时作为：

1. 代理入口：外部客户端连接 `10.168.80.56:<port>`
2. 出口发起端：代理向外网建立连接时强制绑定 `192.168.5.235`

目标效果：

1. 内外部客户端统一把代理地址配置为 `10.168.80.56`
2. 代理收到请求后，所有出站连接优先走 `192.168.5.235` 所在网卡
3. 外部网站最终看到的是 `192.168.5.235` 所在网络出口做 NAT 后的公网 IP，而不是私网地址 `192.168.5.235`

## 二、适用前提 / Preconditions

满足以下前提时，本方案才成立：

1. 同一台主机同时持有 `10.168.80.56` 和 `192.168.5.235`
2. `192.168.5.235` 所在网卡具备真实外网访问能力
3. 代理软件支持分别指定监听地址和出站绑定地址
4. Windows 防火墙允许外部访问代理监听端口
5. 路由上避免两个网卡同时承担默认出口，优先让 `192.168.5.235` 所在网卡成为默认出网口
6. 仅承担代理入口的网卡不要再额外挂公共 DNS，且其 `InterfaceMetric` 不应低于真实外网出口网卡

不满足上述前提时，常见结果是：

1. 代理可以收到请求，但外连失败
2. 代理能外连，但没有稳定从 `192.168.5.235` 发出
3. 回包路径异常，导致连接超时或不稳定

## 三、推荐实现 / Recommended Implementation

推荐使用 `3proxy`，原因如下：

1. 支持 `-i` 指定监听入口地址
2. 支持 `-e` 指定出站绑定地址
3. 同时支持 `HTTP proxy` 和 `SOCKS5`
4. 配置简单，适合当前这种双网卡入口/出口分离场景

核心映射关系如下：

```text
client
  -> 10.168.80.56:3128 or 10.168.80.56:1080
  -> proxy process on the same Windows host
  -> bind outbound socket to 192.168.5.235
  -> upstream Internet target
```

## 四、推荐配置 / Recommended Configuration

建议准备一个最小配置文件。`C:\opt\3proxy\3proxy.cfg` 只是本文示例路径，不是仓库或系统预置目录；如果本机还没有这个目录，需要先手动创建：

为了后续不迷路，当前主机建议把本机专用入口也固定到 `C:\opt`：

1. 顶层导航：`C:\opt\代理服务导航_Proxy Service Index.md`
2. 本机导航文档：`C:\opt\3proxy\docs\本机代理导航_Proxy Local Guide.md`
3. 本地验证脚本：`C:\opt\3proxy\scripts\validate_proxy_local.ps1`
4. 本地验证报告：`C:\opt\3proxy\reports\`

```ini
daemon
nserver 8.8.8.8
nserver 1.1.1.1
nscache 65536
timeouts 1 5 30 60 180 1800 15 60
auth none
allow *

proxy -p3128 -i10.168.80.56 -e192.168.5.235
socks -p1080 -i10.168.80.56 -e192.168.5.235
```

含义如下：

1. `proxy -p3128`：开启 HTTP/HTTPS 显式代理，监听 `10.168.80.56:3128`
2. `socks -p1080`：开启 SOCKS5 代理，监听 `10.168.80.56:1080`
3. `-i10.168.80.56`：只接受打到 `10.168.80.56` 的代理请求
4. `-e192.168.5.235`：向外建立连接时绑定本机源地址 `192.168.5.235`

如果只需要一种代理类型，可以只保留其中一行。

## 五、部署步骤 / Deployment Steps

### 1. 确认网卡与地址

在目标主机执行：

```powershell
ipconfig
Get-NetIPAddress | Where-Object { $_.IPAddress -in @('10.168.80.56', '192.168.5.235') }
route print
```

重点确认：

1. 两个地址都属于同一台主机
2. 默认路由 `0.0.0.0/0` 优先走 `192.168.5.235` 所在网络
3. `10.168.80.56` 所在网卡不要与出口网卡争抢默认路由
4. 如果 `10.168.80.56` 所在网卡只是入口网卡，不要给它配置 `8.8.8.8`、`1.1.1.1` 这类公共 DNS
5. 入口网卡的 `InterfaceMetric` 应显著高于出口网卡，避免 Windows 把默认 DNS 查询从入口口径发出

### 2. 准备代理程序与配置

建议目录结构如下；该目录不会因为阅读本文而自动出现，需要你在目标主机上自行创建：

```text
C:\opt\3proxy\
  3proxy.exe
  3proxy.cfg
  logs\
```

最小落地步骤如下：

```powershell
# 1) 创建目录
New-Item -ItemType Directory -Path C:\opt\3proxy -Force | Out-Null
New-Item -ItemType Directory -Path C:\opt\3proxy\logs -Force | Out-Null

# 2) 把下载得到的 3proxy 压缩包手动解压后，将 3proxy.exe 放到 C:\opt\3proxy\
#    如果你下载后得到的文件不在这个目录，请先自行复制或移动进去。

# 3) 生成配置文件
$cfg = @'
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
socks -p1080 -i10.168.80.56 -e192.168.5.235
'@
Set-Content -Path C:\opt\3proxy\3proxy.cfg -Value $cfg -Encoding utf8
```

下载口径：

1. 从 `3proxy` 官方发布页下载 Windows 版本压缩包
2. 解压后确认拿到 `3proxy.exe`
3. 把 `3proxy.exe` 放到 `C:\opt\3proxy\`

执行完成后，至少应满足：

1. `C:\opt\3proxy\3proxy.exe` 已存在
2. `C:\opt\3proxy\3proxy.cfg` 已存在
3. `C:\opt\3proxy\logs\` 已存在

先使用前台方式启动，确认配置正确：

```powershell
C:\opt\3proxy\3proxy.exe C:\opt\3proxy\3proxy.cfg
```

启动成功后，再接入你自己的服务托管方式，例如计划任务、现有运维壳或统一服务管理器。

如果只是想快速确认当前主机代理是否仍然健康，优先执行：

```powershell
& C:\opt\3proxy\scripts\validate_proxy_local.ps1
```

如果启动失败，先按下面顺序检查：

1. `Test-Path C:\opt\3proxy\3proxy.exe`
2. `Get-Content C:\opt\3proxy\3proxy.cfg`
3. `Get-NetIPAddress | Where-Object { $_.IPAddress -in @('10.168.80.56', '192.168.5.235') }`
4. 确认 `10.168.80.56` 与 `192.168.5.235` 当前都真实挂在本机

### 3. 放行防火墙

至少放行对外提供服务的代理端口：

```powershell
New-NetFirewallRule -DisplayName "3proxy HTTP 3128" -Direction Inbound -Action Allow -Protocol TCP -LocalAddress 10.168.80.56 -LocalPort 3128
New-NetFirewallRule -DisplayName "3proxy SOCKS 1080" -Direction Inbound -Action Allow -Protocol TCP -LocalAddress 10.168.80.56 -LocalPort 1080
```

如果只启用一种代理类型，只保留对应端口规则即可。

## 六、客户端配置 / Client Configuration

客户端不要把 `192.168.5.235` 当代理地址，而应始终连接入口地址 `10.168.80.56`：

1. HTTP 代理：`10.168.80.56:3128`
2. SOCKS5 代理：`10.168.80.56:1080`

代理服务器再负责把出站连接绑定到 `192.168.5.235`。

## 七、验证步骤 / Verification

### 1. 从客户端验证代理入口

HTTP 代理验证：

```bash
curl -x http://10.168.80.56:3128 https://api.ipify.org
```

SOCKS5 验证：

```bash
curl --socks5 10.168.80.56:1080 https://api.ipify.org
```

### 2. 判定标准

验证成功时应满足：

1. 客户端能够正常通过 `10.168.80.56` 建立代理连接
2. 目标网站返回的 IP 不再是客户端自己的公网出口
3. 目标网站返回的 IP 应属于 `192.168.5.235` 所在网络的公网 NAT 出口

注意：

1. 目标网站不会直接看到私网地址 `192.168.5.235`
2. 如果返回的是 `10.168.80.56` 所在网络对应的公网出口，说明出站并没有稳定绑定到 `192.168.5.235`

## 八、常见问题 / Common Failure Modes

### 1. 可以连代理，但外网访问失败

优先检查：

1. `192.168.5.235` 所在网卡是否真的可访问外网
2. 默认路由是否仍走另一块网卡
3. 目标防火墙是否禁止该网卡方向的流量

### 2. 外部网站看到的不是预期出口

优先检查：

1. 配置中是否遗漏 `-e192.168.5.235`
2. 操作系统路由是否把连接重新导向其他出口
3. 出口网络是否还有额外 NAT、策略路由或上游代理

### 3. `google.com` 能通，但 `www.google.com` 超时或证书异常

优先检查：

1. 本机系统 DNS 是否把 `www.google.com` 解析到了异常地址
2. `3proxy` 的 `nserver` 是否仍使用容易返回污染结果的 DNS
3. 若需要让本机浏览器直接复用当前代理，可把 Windows 系统代理指向 `10.168.80.56:3128`

### 4. 代理端口无法从其他机器访问

优先检查：

1. 服务是否真的监听在 `10.168.80.56`，而不是仅监听 `127.0.0.1`
2. Windows 防火墙是否放行入站端口
3. 客户端与 `10.168.80.56` 之间的网络 ACL 是否允许访问

### 5. `youtube.com`、`google.com` 等域名偶发解析到异常 IP

优先检查：

1. 入口网卡是否仍配置了公共 DNS；若该网卡只承担代理入口，应清空其公共 IPv4 DNS
2. 入口网卡的 `InterfaceMetric` 是否低于出口网卡；若是，应调高入口网卡 metric，避免系统把它当作默认解析优先口
3. 出口网卡保留公共 DNS，入口网卡只负责监听代理端口，不要同时承担默认外网解析职责

## 九、服务化落地入口 / Service Deployment Entry

如果要把当前方案进一步收口成稳定后台服务，请继续阅读：

1. [Windows代理服务化部署与验证 / Windows Proxy Service Deployment And Verification](./Windows%E4%BB%A3%E7%90%86%E6%9C%8D%E5%8A%A1%E5%8C%96%E9%83%A8%E7%BD%B2%E4%B8%8E%E9%AA%8C%E8%AF%81_Windows%20Proxy%20Service%20Deployment%20And%20Verification.md)

## 十、结论 / Conclusion

对于“外部连接使用 `10.168.80.56`，代理转发时从 `192.168.5.235` 出网”的需求，最直接、最稳的落地方案是：

1. 使用支持双地址绑定的显式代理软件
2. 入口监听固定到 `10.168.80.56`
3. 出站绑定固定到 `192.168.5.235`
4. 把默认出网、路由和防火墙一并校正

在当前 Windows 双网卡场景下，`3proxy` 是最小可行方案。