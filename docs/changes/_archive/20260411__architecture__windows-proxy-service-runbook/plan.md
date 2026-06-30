---
change-id: "20260411__architecture__windows-proxy-service-runbook"
dependencies:
  hard_blocking: []
  soft_dependency: []
  blocked_by: []
---

# Windows Proxy Service Runbook 开发计划

**状态**：completed
**进度**：100%
**日期**：2026-04-11
**范围**：`docs/architecture/`、当前 change bundle
**topic-id**：architecture
**change-id**：20260411__architecture__windows-proxy-service-runbook
**关联 acceptance**：./acceptance.md

> 本 change 使用 `plan.md + acceptance.md + ai_constraints.md + design.md` 四件套。原因：本次不是单纯补一句说明，而是要把双网卡代理方案固定成 Windows 服务化 runbook，并冻结验证链路与边界。

## 一、需求简述

1. 本 change 要把现有双网卡代理方案补成可直接执行的 Windows 服务化 runbook。
2. 交付内容包括：服务目录布局、固定配置、服务注册方式、主机侧验证步骤和客户端验证步骤。
3. 本 change 不在仓内安装真实代理软件，也不触碰任何目标机网络配置。
4. 真正做成的信号是：仓内存在一份可独立阅读的服务化 runbook，索引可发现，且仓内治理验证未被破坏。

## 二、能力映射 / Capability Mapping

```text
- capability_id: windows-proxy-service-runbook
- capability_name: Windows 代理服务化部署与验证 / Windows Proxy Service Deployment And Verification
- long_term_target: /D:/Nautilus/nautilus_ctp_adapter/docs/architecture/Windows代理服务化部署与验证_Windows Proxy Service Deployment And Verification.md
- secondary_targets: /D:/Nautilus/nautilus_ctp_adapter/docs/architecture/多网卡代理入口与出口绑定方案_Multi-NIC Proxy Ingress Egress Binding.md
- decision_target: /D:/Nautilus/nautilus_ctp_adapter/docs/architecture/README.md
- affects_long_term_rules: 是
- change_type: 新增规则
```

## 三、AI 执行约束

1. 允许修改：`docs/architecture/`、当前 change bundle。
2. 禁止修改：`src/`、`scripts/`、`vendor/`、topic frontier 文档与状态注册表。
3. 当前正式落点：`docs/architecture/Windows代理服务化部署与验证_Windows Proxy Service Deployment And Verification.md`。
4. AI 开始前必须阅读：现有双网卡代理文档与 `docs/architecture/README.md`。
5. 改完后必须执行：文档错误检查；如索引被修改，再补仓内最小治理检查。

## 四、背景与约束

1. 当前仓内已经有入口/出口绑定方案，但还没有“如何把它作为 Windows 服务稳定运行”的落地说明。
2. 当前仓库不是该代理服务的真实部署宿主，因此正式验收只覆盖仓内文档落地与治理一致性，不伪造目标机实跑结果。

## 五、设计方案

1. 新增一篇独立的 Windows 服务化 runbook，而不是把所有部署细节塞回原始网络原理文档。
2. 原始文档继续负责网络拓扑与绑定原理，新文档负责服务化、验证和排障顺序。

## 六、阶段划分

1. P1：创建 change bundle，冻结范围和边界。
2. P2：编写 Windows 服务化 runbook，并与原始双网卡文档建立双向关联。
3. P3：更新 architecture 索引并执行仓内验证。

## 七、任务清单

| 步骤 | 任务 | 来源 | 修改文件 | 产出 | 验证动作 | 回写目标 | 完成定义 | 状态 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| P1 | 建立 change bundle | 用户请求 | 当前 change bundle | 正式执行单元 | 文档检查 | 无 | change 已可独立阅读 | 已完成 |
| P2 | 编写服务化 runbook | 用户请求 | `docs/architecture/Windows代理服务化部署与验证_Windows Proxy Service Deployment And Verification.md`、原始双网卡文档 | Windows 服务化部署与验证口径 | 文档检查 | 原始双网卡文档 | 读者不再需要补问服务化步骤 | 已完成 |
| P3 | 更新 architecture 索引并验证 | discoverability | `docs/architecture/README.md` | 可发现入口 | `check_topic_docs.py --root .` | `docs/architecture/README.md` | 索引可发现且仓内治理不受影响 | 已完成 |

## 八、验证动作

```powershell
python scripts/check_topic_docs.py --root .
```

## 九、完成定义

### 开发完成

1. 服务化 runbook 已写成独立文档
2. 原始网络原理文档与新 runbook 已互相可发现
3. architecture 索引已补入口

### 交付完成

1. `acceptance.md` 中阻塞场景通过
2. 仓内验证命令通过
3. 长期文档回写已完成

## 十、长期规则增量摘要 / Long-Term Rule Delta Summary

本次新增一条长期规则：双网卡代理方案若进入稳定运维口径，必须把网络原理与 Windows 服务化 runbook 分开维护，而不是混成单篇说明。

## 十一、回写与相关变更 / Write-back & Related Changes

1. 需要完成长期文档回写：已指定主文档与索引。
2. 暂不需要在其他 topic 文档登记 `Related Changes`。

## 十二、阻塞项

1. 当前环境已真实安装并启动 `3proxy.exe`，并已完成 `NSSM` 服务注册，因此“远端客户端经本机代理访问 GitHub”的链路已可作为正式服务口径实测。
2. 当前仅未执行“整机重启后服务自动恢复”的单独重启试验；这属于补充运维验证项，不阻断本次 change 的当前交付范围。

## 十三、进度记录

1. 2026-04-11：创建本 change，作为双网卡代理服务化 runbook 的正式宿主。
2. 2026-04-11：新增独立的 Windows 服务化部署与验证文档，并从原始双网卡文档与 architecture 索引建立可发现入口。
3. 2026-04-11：执行 `python scripts/check_topic_docs.py --root .`，结果为 `SUMMARY topics=16 failures=0`。
4. 2026-04-11：使用 `WinRM` 账户 `kimi` 登录 `10.168.80.58`，先验证其可通过本机临时代理 `10.168.80.56:3128` 访问 `github.com`，HTTP 与 `git ls-remote` 均成功。
5. 2026-04-11：从官方发布页下载 `3proxy-0.9.5-x64.zip`，将 `3proxy.exe` 与依赖 DLL 安装到 `C:\opt\3proxy\`，生成正式 `C:\opt\3proxy\3proxy.cfg`，启动真实 `3proxy` 后确认 `10.168.80.56:3128/1080` 正在监听。
6. 2026-04-11：再次使用 `WinRM` 账户 `kimi` 从 `10.168.80.58` 验证其可经真实 `3proxy` 访问 `github.com`，HTTP 返回 `200 OK`，`git ls-remote` 成功，`api.ipify.org` 返回公网 IP `69.63.198.154`；该结果已回填至 `acceptance.md`。
7. 2026-04-11：从 Chocolatey 包源提取 `NSSM 2.24-101-g897c7ad 64-bit` 并安装到 `C:\opt\nssm\nssm.exe`，随后注册 `3proxy-egress` 服务，设置为 `Automatic`，并成功启动。
8. 2026-04-11：清理前台验证遗留的孤儿 `3proxy.exe` 进程，仅保留 `NSSM` 托管的服务实例；再次验证 `10.168.80.56:3128/1080` 正在监听，且 `10.168.80.58` 经该服务托管代理访问 `github.com`、`api.ipify.org` 与 `git ls-remote` 仍然成功。
9. 2026-04-11：针对本机访问 `www.google.com` 异常问题，确认根因是系统 DNS 污染与本机未启用正确系统代理；随后将两张物理网卡 DNS 统一切换为 `8.8.8.8` 与 `1.1.1.1`，并刷新本机 DNS 缓存。
10. 2026-04-11：同步把 `C:\opt\3proxy\3proxy.cfg` 的 `nserver` 更新为 `8.8.8.8` 与 `1.1.1.1`，重启 `3proxy-egress`，再把当前用户 WinINet 与 WinHTTP 代理都指向 `10.168.80.56:3128`；验证本机 `Invoke-WebRequest https://www.google.com` 返回 `HTTP 200`，说明本机浏览器链路已恢复。
11. 2026-04-11：继续排查 `www.youtube.com` 偶发不可达，确认不是 `8.8.8.8` 或 `1.1.1.1` 上游污染，而是入口网卡 `8056` 同时挂了公共 DNS 且 `InterfaceMetric=10`，导致 Windows 会把默认 DNS 查询错误地优先从入口口径发出。
12. 2026-04-11：将 `8056` 的 IPv4/IPv6 `InterfaceMetric` 提高到 `250`，并重置其 IPv4 DNS 服务器为空，仅保留出口网卡 `以太网` 挂公共 DNS；随后连续 5 轮 `Clear-DnsClientCache + Resolve-DnsName` 对 `www.youtube.com` 与 `www.google.com` 的默认解析均稳定返回正常 Google 地址，且两者 `Invoke-WebRequest` 连续 3 轮均返回 `HTTP 200`。
13. 2026-04-11：将 `3proxy-egress` 的启动方式从普通 `Automatic` 收口为 `Automatic (Delayed Start)`，并追加服务失败自动重启策略：连续三次失败均在 60 秒后自动重启，`reset period=86400`，同时启用 `failureflag` 覆盖非崩溃型失败。
14. 2026-04-11：变更后已核对 `sc.exe qc 3proxy-egress` 显示 `AUTO_START (DELAYED)`，`sc.exe qfailure 3proxy-egress` 显示三次 `restart/60000`；本机经 `10.168.80.56:3128` 访问 GitHub 返回 `HTTP 200`、出口公网 IP 仍为 `69.63.198.154`，且 `10.168.80.58` 经该代理访问 GitHub 与 `git ls-remote` 也继续成功。
15. 2026-04-11：为避免后续本机排障迷路，已把本机专用导航、运行入口和验证入口统一固定到 `C:\opt`：新增 `C:\opt\代理服务导航_Proxy Service Index.md`、`C:\opt\3proxy\docs\本机代理导航_Proxy Local Guide.md`、`C:\opt\3proxy\scripts\validate_proxy_local.ps1` 与 `C:\opt\3proxy\reports\`。
16. 2026-04-11：已手工执行 `C:\opt\3proxy\scripts\validate_proxy_local.ps1`，报告输出到 `C:\opt\3proxy\reports\latest.json` 与 `latest.md`，结果 `overall_pass=true`，确认服务、监听、GitHub/Google/YouTube 访问和网卡布局检查均通过。
17. 2026-04-11：新增稳定性采样脚本 `C:\opt\3proxy\scripts\collect_stability_snapshot.ps1`，可同时记录默认 DNS、显式 DNS、代理出口 IP、关键 HTTP 状态和已知异常地址命中情况；输出固定到 `C:\opt\3proxy\reports\stability\`。
18. 2026-04-11：新增每小时计划任务 `3proxy-stability-hourly`，以 `SYSTEM` 身份每小时执行一次采样；`schtasks /Query` 已确认其 `NextRunTime` 正常排到下一小时，随后 `LastTaskResult=0`，并成功刷新 `latest.json`、`latest.md`、`stability_log.jsonl`、`stability_summary.jsonl` 与 `stability_summary.csv`。
19. 2026-04-11：继续把稳定性分析从“只盯异常 IP”升级为“优先盯被影响域名”：确认这批异常 IP 基本没有可靠 PTR，随后将 `collect_stability_snapshot.ps1` 增强为输出 `bad_domain_count` 与 `bad_domain_values`，并将重点域名收口为 `www.google.com` 与 `www.youtube.com`。
20. 2026-04-11：新增 `C:\opt\3proxy\scripts\summarize_domain_stability_24h.ps1`，用于从 `stability_log.jsonl` 汇总最近 24 小时的域名异常统计；同时把 `collect_stability_snapshot.ps1` 改为每次采样后自动刷新 `domain_stability_24h.json` 与 `domain_stability_24h.md`。
21. 2026-04-11 15:14：已手工执行 `C:\opt\3proxy\scripts\collect_stability_snapshot.ps1`，确认 24 小时报表真实生成；当前窗口 `sample_count=12`、`anomaly_sample_count=0`、`latest_egress_ip=69.63.198.154`，重点域名 `www.google.com`、`www.youtube.com`、`github.com`、`api.ipify.org` 均无异常样本。
22. 2026-04-11 15:26：新增 `C:\opt\3proxy\scripts\publish_domain_stability_alert.ps1`，用于从 24 小时域名汇总结果发布当前告警状态；固定输出 `alerts\current_domain_alert.md/json` 与 `alerts\alert_history.jsonl`，并在异常时尝试写 Windows Application Event Log 与向当前桌面会话发消息。
23. 2026-04-11 15:26：已在真实链路执行 `C:\opt\3proxy\scripts\collect_stability_snapshot.ps1`，确认生产目录 `C:\opt\3proxy\reports\stability\alerts\current_domain_alert.md` 成功生成，当前状态为 `Alert State: normal`。
24. 2026-04-11 15:26：已在隔离测试目录 `output/debug/proxy_alert_test/stability` 注入合成异常样本，并执行 `summarize_domain_stability_24h.ps1 -EnableInteractiveMessage:$false -EnableEventLog:$false`；结果 `anomaly_sample_count=1`、`Alert State: new`，且仅 `www.google.com` 被识别为活跃异常域名。
25. 2026-04-11 15:50：新增 `C:\opt\3proxy\scripts\collect_proxy_performance_snapshot.ps1`，把本机代理监控从“可用性 + 域名稳定性”扩展到“性能”：新增 CPU、工作集内存、已建立连接数、代理请求延迟、最近 5 分钟请求量、最近 5 分钟疑似错误行以及 top clients / top targets 采样，并输出到 `C:\opt\3proxy\reports\performance\`。
26. 2026-04-11 15:50：修正 `3proxy` 日志时间戳解析口径，按 UTC 读入后转换为本地时间；修正后真实样本显示 `request_count_5m=284`，说明最近 5 分钟流量统计不再被误判为 0。
27. 2026-04-11 15:50：已手工执行性能采样脚本，真实输出 `status_level=warn`，当前唯一触发项为 `latency_warn`；同时记录到 `C:\opt\3proxy\reports\performance\alerts\current_performance_alert.md`，并成功写入 Windows Application Event Log。
28. 2026-04-11 15:50：已创建计划任务 `3proxy-performance-5min`，以 `SYSTEM` 身份执行 `collect_proxy_performance_snapshot.ps1`，作为性能监控正式入口。
29. 2026-04-11：按用户要求，将性能分析调度从“每 5 分钟一次”修正为“每天两次”：删除 `3proxy-performance-5min`，改为 `3proxy-performance-0500` 与 `3proxy-performance-1700` 两条任务，分别在每天 `05:00` 与 `17:00` 执行。
30. 2026-04-11：按用户确认，正式采用“两层性能监控”：新增 `light/summary` profile，其中 `light` 保留根目录 `C:\opt\3proxy\reports\performance\` 作为及时调整入口，`summary` 写入 `C:\opt\3proxy\reports\performance\summary\` 作为汇总分析入口。
31. 2026-04-11 16:10：已创建轻量任务 `3proxy-performance-light-15min`，每 `15` 分钟执行一次 `collect_proxy_performance_snapshot.ps1 -Profile light -ReportDir C:\opt\3proxy\reports\performance -EnableInteractiveMessage:$false`。
32. 2026-04-11 16:10：已将 `3proxy-performance-0500` 与 `3proxy-performance-1700` 升级为 `summary` profile，执行命令改为 `collect_proxy_performance_snapshot.ps1 -Profile summary -ReportDir C:\opt\3proxy\reports\performance\summary -EnableInteractiveMessage:$false`。
33. 2026-04-11 16:10：已手工验证两层输出均正常：`light` 层当前 `status_level=warn`、`average_latency_ms=1239.94`、`max_latency_ms=1554.27`；`summary` 层当前 `status_level=warn`、`average_latency_ms=1607.12`、`max_latency_ms=2832.91`，两层报告和告警目录都已成功生成。
34. 2026-04-11：用户明确拒绝“GitHub / Google 直连”方案后，当前方案收口为“仍强制经 `192.168.5.235` 出网，但新增 `10.168.80.56:3129` 交互专用 HTTP 代理口，把 GitHub / Google / YouTube / Copilot 相关流量从共享 `3128` 通道中分离出来”。
35. 2026-04-11：已把 `C:\opt\3proxy\3proxy.cfg` 升级为三入口：共享 HTTP `3128`、交互 HTTP `3129`、SOCKS5 `1080`，三者都固定绑定 `192.168.5.235`；并同步把 `validate_proxy_local.ps1` 扩展为同时验证 `3128` 与 `3129`，确认两口 `ipify` 返回同一出口公网 IP。
36. 2026-04-11：已把 `collect_proxy_performance_snapshot.ps1` 扩展为支持 `LaneName`、`ObservedPorts` 与 `OverviewRootDir`，从而可以把 `3129` 交互通道独立输出到 `C:\opt\3proxy\reports\performance\interactive\`，并继续汇总到同一份性能总览首页。
37. 2026-04-11：已新增 `C:\opt\3proxy\pac\80.58_交互分流代理规则_Interactive Proxy Split.pac`，固定口径为“GitHub / GitHub API / GitHub Copilot / Google / YouTube 优先走 `3129`，失败时退回 `3128`，其余流量仍走 `3128`”；该 PAC 不包含直连分支，因此不违背“全部仍经 `192.168.5.*`”约束。
38. 2026-04-11 17:08：已手工执行 `C:\opt\3proxy\scripts\validate_proxy_local.ps1`，真实报告显示 `listen_3128=true`、`listen_3129=true`、`listen_1080=true`，且 `general_*` 与 `interactive_*` 对 GitHub / Google / YouTube / Ipify 的检查全部通过，`interactive_egress_consistent=true`。
39. 2026-04-11 17:08：已手工执行 `C:\opt\3proxy\scripts\collect_interactive_proxy_snapshot.ps1`，真实生成 `C:\opt\3proxy\reports\performance\interactive\latest.json/md` 与 `interactive\alerts\current_performance_alert.json/md`；当前 `status_level=warn`，主问题为 `latency_warn`，`average_latency_ms=1561.72`，`max_latency_ms=2444.67`。
40. 2026-04-11 17:08：`refresh_performance_overview.ps1` 已把交互层聚合进总览页；当前 `C:\opt\3proxy\reports\performance\性能总览_Performance Overview.md` 显示 `Read First: interactive -> light -> summary`。
41. 2026-04-11 17:08：已创建并回读计划任务 `3proxy-performance-interactive-15min`，当前执行器为 `C:\Program Files\PowerShell\7\pwsh.exe`，参数为 `-File "C:\opt\3proxy\scripts\collect_interactive_proxy_snapshot.ps1"`，`LastTaskResult=0`，`NextRunTime=2026-04-11 17:22:22`。
34. 2026-04-11 16:21：在用户要求“直接手工触发三条任务验证真实调度链路”后，确认任务最初仍失败，根因不是调度本身，而是任务动作仍使用 `powershell.exe`；当前性能脚本已包含 PowerShell 7 语法，导致 Windows PowerShell 5.1 解析失败并返回 `LastTaskResult=1`。
35. 2026-04-11 16:22：已将 `3proxy-performance-light-15min`、`3proxy-performance-0500` 与 `3proxy-performance-1700` 三条任务的执行器统一切换为 `C:\Program Files\PowerShell\7\pwsh.exe`，随后重新手工触发三条任务，三者 `LastRunTime` 均更新到 `2026-04-11 16:22:22`，且 `LastTaskResult=0`。
36. 2026-04-11 16:22：任务链路修复后，`light` 层关键文件 `C:\opt\3proxy\reports\performance\latest.md/json` 与 `alerts\current_performance_alert.md/json` 已刷新到 `16:22:14`；`summary` 层对应文件已刷新到 `16:22:20`，证明轻量层与汇总层都已由计划任务本身成功落盘。
37. 2026-04-11 16:27：新增 `C:\opt\3proxy\scripts\refresh_performance_overview.ps1`，并将 `C:\opt\3proxy\scripts\collect_proxy_performance_snapshot.ps1` 挂接为每次 `light/summary` 采样完成后自动刷新总览首页；固定输出为 `C:\opt\3proxy\reports\performance\性能总览_Performance Overview.md` 与 `performance_overview.json`。
38. 2026-04-11 16:27：已手工执行一次 `light` 与一次 `summary` 采样，确认总览首页真实生成，当前 `overall_status=warn`、推荐读取顺序为 `light -> summary`，且三条性能任务在首页中均显示 `state=Ready`、`last_result=0`。
39. 2026-04-11：已将“先看总览页，再钻取 light/summary 两层”的读取口径回写到 `C:\opt` 导航与长期 runbook，后续日常巡检不再需要先分别打开两层报告。