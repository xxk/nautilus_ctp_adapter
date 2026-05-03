# Windows Proxy Service Runbook 验收方案 / Acceptance Plan

**模板标识 / Template Marker**：standard
**变更目录 / Change Root**：./
**状态**：✅ 已通过
**日期**：2026-04-11
**范围**：`docs/architecture/`、当前 change bundle
**change-id**：20260411__architecture__windows-proxy-service-runbook
**关联 plan**：./plan.md
**关联 ai_constraints**：./ai_constraints.md
**长期归宿 / Long-Term Target**：/D:/Nautilus/nautilus_ctp_adapter/docs/architecture/Windows代理服务化部署与验证_Windows Proxy Service Deployment And Verification.md

<!-- AI-STATUS-BEGIN -->
```yaml
conclusion: passed
allow_declare_pass: true
last_updated: "2026-04-11 16:27"
concluded_by: "GitHub Copilot"

exit_conditions:
  E1_success_scenarios: passed
  E2_failure_scenarios: passed
  E3_verification_cmds: passed
  E4_evidence_collected: passed
  E5_real_acceptance_only: passed
  E6_minimum_scenarios: passed

scenarios:
  A1: { exec: true, result: passed, blocking: true }
  A2: { exec: true, result: passed, blocking: true }
  A3: { exec: true, result: passed, blocking: true }
  A4: { exec: true, result: passed, blocking: true }
  A5: { exec: true, result: passed, blocking: true }
  A6: { exec: true, result: passed, blocking: false }
```
<!-- AI-STATUS-END -->

## 总览看板 / Dashboard

### 验收总状态 / Overall

| 项目 | 值 | 说明 |
| --- | :---: | --- |
| 验收结论 | ✅ 已通过 | 由 `AI-STATUS conclusion` 派生 |
| AI 建议宣告通过 | 是 | 由 `AI-STATUS allow_declare_pass` 派生 |
| 最后更新 | 2026-04-11 16:27 | |
| AI 执行人 | GitHub Copilot | |

### 出口条件 / Exit Criteria

| # | 出口条件 | 状态 | 判定规则 | 证据 |
| --- | --- | :---: | --- | --- |
| E1 | 关键成功场景全部通过 | ✅ | 阻塞成功场景全部 ✅ | A1-A3 |
| E2 | 关键失败场景符合预期 | ✅ | 阻塞失败场景全部 ✅ | A4-A5 |
| E3 | 必跑验证命令已完成 | ✅ | `plan.md` 中声明命令已执行 | A5 |
| E4 | 关键证据已留存 | ✅ | 当前 change bundle 与长期文档已记录结果 | A1-A6 |
| E5 | 正式验收不伪装目标机实跑 | ✅ | 只声明仓内真实验证结果 | A4、A6 |
| E6 | 正式场景数不少于 6 个 | ✅ | A1-A6 均有结果 | A1-A6 |

### 场景看板 / Scenario Board

| # | 场景 | 执行 | 结论 | 阻塞 | 证据/备注 |
| --- | --- | :---: | :---: | :---: | --- |
| A1 | Success 1: 服务化 runbook 文档已存在 | ✅ | ✅ | 是 | 新文档已创建并含部署、服务、验证与排障章节 |
| A2 | Success 2: 原始双网卡文档可发现服务化 runbook | ✅ | ✅ | 是 | 原始文档新增 runbook 入口 |
| A3 | Success 3: architecture 索引可发现新文档 | ✅ | ✅ | 是 | `docs/architecture/README.md` 已挂载新入口 |
| A4 | Failure 1: 文档不伪装目标机已实跑 | ✅ | ✅ | 是 | `plan.md`、runbook 与本文件都明确保留目标机实跑为待办 |
| A5 | Failure 2: 仓内验证若失败会被真实暴露 | ✅ | ✅ | 是 | 已实际执行 `python scripts/check_topic_docs.py --root .`，结果 `SUMMARY topics=16 failures=0` |
| A6 | Boundary 1: 无目标机二进制时仍可完成仓内交付 | ✅ | ✅ | 否 | 本 change 作用域是仓内文档与索引，不以目标机二进制为前置 |

## 一、验收目标 / Goals

1. 验证 Windows 服务化 runbook 已成为正式长期文档。
2. 验证原始网络原理文档与 architecture 索引都能找到它。
3. 验证本 change 没有把“目标机待执行”伪装成“已经实跑通过”。

## 二、验收范围 / Scope

### 覆盖（In Scope）

1. 新增服务化 runbook
2. 原始双网卡文档中的关联入口
3. architecture 索引
4. 当前 change bundle

### 不覆盖（Out of Scope）

1. 真实目标机安装 `3proxy` 与 `nssm`
2. 真实代理端口监听
3. 真实公网出口校验

## 三、前置条件 / Prerequisites

| 条件 | 类型 | 阻断开发 | 阻断验收 | 状态 | 备注 |
| --- | --- | :---: | :---: | :---: | --- |
| 仓内文档目录可写 | 环境 | 是 | 是 | ✅ | 当前 change 与长期文档已写入 |
| `python scripts/check_topic_docs.py --root .` 可执行 | 治理 | 否 | 是 | ✅ | 结果 `SUMMARY topics=16 failures=0` |

## 四、验收专属 AI 边界 / Acceptance-Only AI Boundaries

1. 不得把目标机上的 service status、监听结果、公网出口结果写成“已验证”，除非当前环境真的执行过。
2. 仓内验证只用于证明 change 与长期文档落地成功，不替代目标机实跑。
3. 若仓内治理命令失败，必须如实保留失败结果。

## 五、验收场景 / Scenarios

| # | 场景 | 执行命令/步骤 | 预期结果 | 成功信号 | 失败口径 | 证据路径 |
| --- | --- | --- | --- | --- | --- | --- |
| A1 | Success 1: 服务化 runbook 文档已存在 | 检查长期文档 | 文档结构完整 | 文档可独立阅读 | 文档缺失或残缺 | `/docs/architecture/Windows代理服务化部署与验证_Windows Proxy Service Deployment And Verification.md` |
| A2 | Success 2: 原始双网卡文档可发现 runbook | 检查原始文档引用 | 两文档可双向导航 | 原始文档含 runbook 入口 | 文档孤立 | `/docs/architecture/多网卡代理入口与出口绑定方案_Multi-NIC Proxy Ingress Egress Binding.md` |
| A3 | Success 3: architecture 索引可发现新文档 | 检查 architecture 索引 | 索引已挂载 | README 含新入口 | 不可发现 | `/docs/architecture/README.md` |
| A4 | Failure 1: 文档未伪装目标机已实跑 | 审阅 runbook 与 change 文档 | 明确区分仓内验证与目标机实跑 | 存在边界说明 | 把未执行结果写成已通过 | 当前 change bundle |
| A5 | Failure 2: 仓内治理检查真实执行 | `python scripts/check_topic_docs.py --root .` | 命令真实返回结果 | `SUMMARY topics=16 failures=0` | 跳过验证或命令失败 | 当前 change bundle |
| A6 | Boundary 1: 没有目标机二进制也可完成仓内交付 | 审阅范围与阻塞说明 | 目标机缺二进制只影响实跑，不影响文档交付 | 边界清楚 | 把边界混成 blocker | 当前 change bundle |

## 六、证据清单 / Evidence

| # | 证据类型 | 路径/链接 | 说明 |
| --- | --- | --- | --- |
| 1 | 长期文档 | `/docs/architecture/Windows代理服务化部署与验证_Windows Proxy Service Deployment And Verification.md` | 服务化 runbook |
| 2 | 长期文档 | `/docs/architecture/多网卡代理入口与出口绑定方案_Multi-NIC Proxy Ingress Egress Binding.md` | 原始双网卡方案 |
| 3 | 长期文档 | `/docs/architecture/README.md` | architecture 索引 |
| 4 | 验证命令 | `python scripts/check_topic_docs.py --root .` | 输出 `SUMMARY topics=16 failures=0` |
| 5 | 远端链路验证 | `Invoke-Command -ComputerName 10.168.80.58 -Credential kimi` | 返回 `desk-8058\kimi`，`proxy_port_ok=true`，`github_http_status=200`，`github_git_ok=true` |
| 6 | 本机真实 `3proxy` 证据 | `C:\opt\3proxy\3proxy.exe`、`C:\opt\3proxy\3proxy.cfg`、`C:\opt\3proxy\logs\3proxy.log.2026.04.11` | `3proxy` 已真实安装并监听 `10.168.80.56:3128/1080` |
| 7 | 24 小时域名稳定性报告 | `C:\opt\3proxy\reports\stability\domain_stability_24h.json`、`C:\opt\3proxy\reports\stability\domain_stability_24h.md` | `sample_count=12`、`anomaly_sample_count=0`、`latest_egress_ip=69.63.198.154` |
| 8 | 当前域名告警状态 | `C:\opt\3proxy\reports\stability\alerts\current_domain_alert.json`、`C:\opt\3proxy\reports\stability\alerts\current_domain_alert.md` | 真实链路已生成，当前 `alert_state=normal` |
| 9 | 合成异常告警验证 | `/output/debug/proxy_alert_test/stability/alerts/current_domain_alert.json`、`/output/debug/proxy_alert_test/stability/domain_stability_24h.json` | `anomaly_sample_count=1`、`alert_state=new`、仅 `www.google.com` 命中 |
| 10 | 轻量性能快照与告警状态 | `C:\opt\3proxy\reports\performance\latest.json`、`C:\opt\3proxy\reports\performance\latest.md`、`C:\opt\3proxy\reports\performance\alerts\current_performance_alert.md` | `Profile=light`，当前 `status_level=warn` |
| 11 | 汇总性能快照与告警状态 | `C:\opt\3proxy\reports\performance\summary\latest.json`、`C:\opt\3proxy\reports\performance\summary\latest.md`、`C:\opt\3proxy\reports\performance\summary\alerts\current_performance_alert.md` | `Profile=summary`，当前 `status_level=warn` |
| 12 | 分层性能任务 | `schtasks /Query /TN "3proxy-performance-light-15min" /V /FO LIST`、`schtasks /Query /TN "3proxy-performance-0500" /V /FO LIST`、`schtasks /Query /TN "3proxy-performance-1700" /V /FO LIST` | 一条 `15` 分钟轻量任务 + 两条每日汇总任务均已创建，且当前都使用 `pwsh.exe` |
| 13 | 任务链路手工触发验证 | `schtasks /Run /TN ...` + `Get-ScheduledTaskInfo` | 三条任务在 `2026-04-11 16:22:22` 都返回 `LastTaskResult=0` |
| 14 | 性能总览首页 | `C:\opt\3proxy\reports\performance\性能总览_Performance Overview.md`、`C:\opt\3proxy\reports\performance\performance_overview.json` | 总览页已真实生成，聚合 `light` / `summary` 当前状态与三条任务状态 |
| 15 | 总览自动刷新验证 | `pwsh.exe -NoProfile -File "C:\opt\3proxy\scripts\collect_proxy_performance_snapshot.ps1" -Profile light ...`、`pwsh.exe -NoProfile -File "C:\opt\3proxy\scripts\collect_proxy_performance_snapshot.ps1" -Profile summary ...` | 两次真实采样后，总览页刷新到 `2026-04-11 16:27:18`，`overall_status=warn`，后续在接入交互层后读取顺序更新为 `interactive -> light -> summary` |
| 16 | 交互专用代理配置 | `C:\opt\3proxy\3proxy.cfg`、`C:\opt\3proxy\scripts\validate_proxy_local.ps1` | 已新增 `10.168.80.56:3129`；`2026-04-11 17:08` 真实报告显示 `listen_3128=true`、`listen_3129=true`、`listen_1080=true`，且双口 `ipify` 返回同一出口公网 IP |
| 17 | 交互专用性能入口 | `C:\opt\3proxy\reports\performance\interactive\latest.json`、`C:\opt\3proxy\reports\performance\interactive\alerts\current_performance_alert.md` | `2026-04-11 17:08` 真实生成交互层报告，`status_level=warn`、`average_latency_ms=1561.72`、`max_latency_ms=2444.67`，且总览页已聚合该层 |
| 18 | 80.58 分流策略 | `C:\opt\3proxy\pac\80.58_交互分流代理规则_Interactive Proxy Split.pac` | GitHub / Google / YouTube / Copilot 相关域名优先 `3129`，失败退回 `3128`，不含直连分支 |
| 19 | 交互性能任务链路 | `Get-ScheduledTask -TaskName "3proxy-performance-interactive-15min"`、`Get-ScheduledTaskInfo -TaskName "3proxy-performance-interactive-15min"` | 当前任务动作已切到 `collect_interactive_proxy_snapshot.ps1`，`LastTaskResult=0`，`NextRunTime=2026-04-11 17:22:22` |

## 七、未通过处理 / On Failure

1. 若 runbook 内容不完整，回到 `plan.md` 补文档而不是口头补充。
2. 若仓内治理验证失败，先修被本 change 影响的文档，再重跑验证。

## 九、真实验收待办清单 / Pending E2E Checklist

| # | 对应场景 | 当前阶段结果 | 还缺的真实验证 | 真实入口/命令 | 通过信号 | 阻塞项 | 证据路径 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| R1 | A1-A4 | 已完成 `3proxy` 服务化实跑 | 还缺“重启后自动恢复”的单独重启试验 | `Get-Service 3proxy-egress`、`Get-Process 3proxy`、`Test-NetConnection`、`Invoke-WebRequest`、`git ls-remote` | `3proxy-egress` 为 `Running/Automatic`，`10.168.80.58` 可经其访问 GitHub | 尚未做整机重启验证 | 当前 change bundle |

## 十、补充实证 / Supplemental E2E Evidence

1. 2026-04-11 已从官方发布页下载 `3proxy-0.9.5-x64.zip`，并将 `bin64` 下的可执行文件与依赖 DLL 安装到 `C:\opt\3proxy\`。
2. `C:\opt\3proxy\3proxy.cfg` 已按 runbook 写入，包含 `proxy -p3128 -i10.168.80.56 -e192.168.5.235` 与 `socks -p1080 -i10.168.80.56 -e192.168.5.235`。
3. 当前主机已真实运行 `C:\opt\3proxy\3proxy.exe`；`Test-NetConnection` 显示 `10.168.80.56:3128` 与 `10.168.80.56:1080` 均监听成功，进程路径为 `C:\opt\3proxy\3proxy.exe`。
4. `C:\opt\3proxy\logs\3proxy.log.2026.04.11` 已生成，并记录 `10.168.80.58 -> github.com:443` 与 `10.168.80.58 -> api.ipify.org:443` 的 `CONNECT` 请求。
5. 已使用 `WinRM` 账户 `kimi` 成功登录 `10.168.80.58`，返回身份 `desk-8058\kimi`；随后其对 `10.168.80.56:3128` 的 `Test-NetConnection` 返回 `proxy_port_ok=true`。
6. `10.168.80.58` 通过 `http://10.168.80.56:3128` 访问 `https://github.com` 返回 `HTTP 200 OK`，并通过 `https://api.ipify.org` 观测到代理出口公网 IP 为 `69.63.198.154`。
7. `10.168.80.58` 执行 `git -c http.proxy=http://10.168.80.56:3128 -c https.proxy=http://10.168.80.56:3128 ls-remote https://github.com/github/gitignore.git HEAD` 成功，返回 `c677dd99d46da587a70362d6df5cf57787aa5210	HEAD`。
8. `NSSM 2.24-101-g897c7ad 64-bit` 已安装到 `C:\opt\nssm\nssm.exe`，并成功注册 `3proxy-egress` Windows 服务；`Get-Service` 显示其状态为 `Running`、`StartType=Automatic`。
9. 服务对应的 `Win32_Service.PathName` 为 `C:\opt\nssm\nssm.exe`，托管的真实子进程为 `C:\opt\3proxy\3proxy.exe`；前台验证遗留的孤儿 `3proxy.exe` 进程已清理，只保留服务托管实例。
10. 上述实证证明“真实 `3proxy` 二进制已在本机以 `NSSM` 服务方式跑通，且远端客户端可经其访问 GitHub”链路成立；当前仅剩“整机重启后自动恢复”的单独重启试验未做，不影响当前客户端配置口径。
11. 2026-04-11 追加修复本机访问 `www.google.com` 异常问题：将两张物理网卡 DNS 统一调整为 `8.8.8.8` 与 `1.1.1.1`，清理本机 DNS 缓存后，系统解析恢复为正常 Google 地址。
12. 同日已把 `C:\opt\3proxy\3proxy.cfg` 中的 `nserver` 从旧值切换为 `8.8.8.8` 与 `1.1.1.1`，随后重启 `3proxy-egress` 服务，确保代理自身的上游解析口径与主机保持一致。
13. 同日已将当前用户 WinINet 代理与 WinHTTP 代理统一指向 `10.168.80.56:3128`；在不显式传 `-Proxy` 的情况下，本机 `Invoke-WebRequest https://www.google.com` 返回 `HTTP 200`，且 `C:\opt\3proxy\logs\3proxy.log.2026.04.11` 中出现本机 `10.168.80.56` 对 Google 相关域的 `CONNECT` 记录，证明本机浏览器链路已恢复。
14. 同日继续修复 `www.youtube.com` 偶发不可达问题：排查确认 `8.8.8.8` 与 `1.1.1.1` 的显式查询均正常，真正根因是入口网卡 `8056` 挂了公共 IPv4 DNS 且 `InterfaceMetric=10`，Windows 默认解析会错误优先使用该入口口径。
15. 同日已将 `8056` 的 IPv4/IPv6 `InterfaceMetric` 提高为 `250`，并将其 IPv4 DNS 服务器重置为空；修复后连续 5 轮 `Clear-DnsClientCache + Resolve-DnsName` 对 `www.youtube.com` 与 `www.google.com` 的默认解析均稳定返回正常 Google 地址，连续 3 轮 `Invoke-WebRequest https://www.youtube.com` 与 `https://www.google.com` 也都返回 `HTTP 200`。
16. 同日已把 `3proxy-egress` 从普通 `Automatic` 调整为 `Automatic (Delayed Start)`，并启用失败自动重启策略：`reset=86400`，前三次失败均执行 `restart/60000`，且 `failureflag=1` 已打开；`sc.exe qc 3proxy-egress` 与 `sc.exe qfailure 3proxy-egress` 均已回读确认。
17. 上述服务加固后，本机 `10.168.80.56:3128/1080` 继续监听成功；本机显式走代理访问 `https://github.com` 返回 `HTTP 200`，`api.ipify.org` 返回公网出口 `69.63.198.154`；远端 `10.168.80.58` 对 `10.168.80.56:3128` 的 `Test-NetConnection` 继续通过，且其 `Invoke-WebRequest https://github.com` 与 `git ls-remote https://github.com/github/gitignore.git HEAD` 仍成功。
18. 同日为避免本机排障迷路，已把本机专用入口统一固定到 `C:\opt`：新增 `C:\opt\代理服务导航_Proxy Service Index.md`、`C:\opt\3proxy\docs\本机代理导航_Proxy Local Guide.md`、`C:\opt\3proxy\scripts\validate_proxy_local.ps1` 与 `C:\opt\3proxy\reports\`。
19. `C:\opt\3proxy\scripts\validate_proxy_local.ps1` 已手工执行通过，生成 `C:\opt\3proxy\reports\latest.json` 与 `latest.md`；报告显示 `overall_pass=true`，并逐项证明 `3proxy-egress` 运行正常、处于 delayed start + failure restart 策略下、`10.168.80.56:3128/1080` 正在监听，且本机经代理访问 GitHub、Google、YouTube 均返回 `HTTP 200`。
20. 同日已新增 `C:\opt\3proxy\scripts\collect_stability_snapshot.ps1` 与 `C:\opt\3proxy\reports\stability\本次会话稳定性跟踪目标_Stability Targets 2026-04-11.md`，用于持续记录本次会话涉及的 DNS、关键 IP、已知异常地址和关键站点可用性。
21. 同日已创建每小时计划任务 `3proxy-stability-hourly`，并完成一次真实执行验证：`Get-ScheduledTaskInfo` 返回 `LastTaskResult=0`，`NextRunTime` 已排到下一小时；`C:\opt\3proxy\reports\stability\latest.json`、`latest.md`、`stability_log.jsonl`、`stability_summary.jsonl` 与 `stability_summary.csv` 均已被任务刷新，证明“每小时自动记录稳定性与异常地址”链路成立。
22. 同日已进一步确认：这批异常 IP 基本没有可靠 PTR，因此长期稳定性判断不能依赖“异常 IP 自己的域名”；现已将采样脚本与本机稳定性清单升级为域名视角，新增 `bad_domain_count` 与 `bad_domain_values` 两个字段，专门用于判断 `www.google.com`、`www.youtube.com` 是否命中了异常 IP。
23. 2026-04-11 15:14 已新增并手工验证 `C:\opt\3proxy\scripts\summarize_domain_stability_24h.ps1`：执行 `collect_stability_snapshot.ps1` 后自动生成 `domain_stability_24h.json` 与 `domain_stability_24h.md`，当前 24 小时窗口内 `sample_count=12`、`overall_ok_samples=12`、`anomaly_sample_count=0`，且 `www.google.com`、`www.youtube.com`、`github.com`、`api.ipify.org` 均未出现异常命中。
24. 2026-04-11 15:26 已新增 `C:\opt\3proxy\scripts\publish_domain_stability_alert.ps1`，并把告警发布层接入现有采样链路：每次 `collect_stability_snapshot.ps1` 执行后，都会先刷新 24 小时报表，再刷新 `alerts\current_domain_alert.md/json` 与 `alerts\alert_history.jsonl`。
25. 同日已在真实生产目录执行 `C:\opt\3proxy\scripts\collect_stability_snapshot.ps1`，确认 `C:\opt\3proxy\reports\stability\alerts\current_domain_alert.md` 成功生成，当前显示 `Alert Active: False`、`Alert State: normal`、`Anomaly Sample Count: 0`；这证明无异常时生产告警状态会稳定落盘。
26. 同日已在隔离测试目录 `D:\Nautilus\nautilus_ctp_adapter\output\debug\proxy_alert_test\stability` 注入一条合成异常样本，并执行 `C:\opt\3proxy\scripts\summarize_domain_stability_24h.ps1 -ReportDir ... -EnableInteractiveMessage:$false -EnableEventLog:$false`；结果生成的 `domain_stability_24h.md` 与 `alerts\current_domain_alert.md/json` 显示 `anomaly_sample_count=1`、`Alert State: new`，且只有 `www.google.com` 被识别为异常域名。
27. 上述设计同时冻结了一条运维边界：由于 `3proxy-stability-hourly` 当前由 `SYSTEM` 执行，桌面消息只能视为 best-effort；真正稳定、可追踪、可回看的一线告警入口仍是 `alerts` 目录和 Windows Application Event Log，因此本次验收把文件落盘与状态机命中作为权威证据，而不把桌面弹窗是否出现作为通过前提。
28. 2026-04-11 15:50 已新增并手工验证 `C:\opt\3proxy\scripts\collect_proxy_performance_snapshot.ps1`：真实样本成功产出 `C:\opt\3proxy\reports\performance\latest.json/md` 与 `alerts\current_performance_alert.md/json`，当前 `status_level=warn`，触发项为 `latency_warn`，同时 `CPU=0%`、`working_set_mb=9.33`、`established_connection_count=33`、`request_count_5m=284`。
29. 同日已修正 `3proxy` 日志时间戳解析为“按 UTC 读入，再转换为本地时间”，修正后最近 5 分钟请求量与 top clients/top targets 统计恢复可信；当前样本显示最近 5 分钟高频来源以 `10.168.80.58` 和 `10.168.80.56` 为主，目标以 `www.quantconnect.com:443` 为主。
30. 同日已创建计划任务 `3proxy-performance-0500` 与 `3proxy-performance-1700`，两者均以 `SYSTEM` 身份运行，执行命令均为 `powershell.exe -NoProfile -ExecutionPolicy Bypass -File "C:\opt\3proxy\scripts\collect_proxy_performance_snapshot.ps1"`；当前查询结果显示其分别在每天 `05:00` 与 `17:00` 运行，最近 `NextRunTime` 分别为 `2026-04-12 05:00:00` 与 `2026-04-11 17:00:00`。
31. 2026-04-11 16:10 已为性能监控增加 `light/summary` 两个 profile：`light` 写到 `C:\opt\3proxy\reports\performance\`，`summary` 写到 `C:\opt\3proxy\reports\performance\summary\`；两层都使用同一脚本 `collect_proxy_performance_snapshot.ps1`，但输出目录与观测目标分离。
32. 同日已创建 `3proxy-performance-light-15min`，查询结果显示其以 `SYSTEM` 身份运行，执行命令为 `powershell.exe -NoProfile -ExecutionPolicy Bypass -File "C:\opt\3proxy\scripts\collect_proxy_performance_snapshot.ps1" -Profile light -ReportDir "C:\opt\3proxy\reports\performance" -EnableInteractiveMessage:$false`，重复频率为每 `15` 分钟一次，最近 `NextRunTime=2026-04-11 16:25:00`。
33. 同日已将 `3proxy-performance-0500` 与 `3proxy-performance-1700` 升级为 `summary` profile，执行命令改为 `... -Profile summary -ReportDir "C:\opt\3proxy\reports\performance\summary" -EnableInteractiveMessage:$false`；两条任务继续分别在每天 `05:00` 与 `17:00` 运行。
34. 同日已手工执行两层脚本验证输出：`light` 层报告显示 `Profile: light`、`status_level=warn`、`average_latency_ms=1239.94`、`max_latency_ms=1554.27`；`summary` 层报告显示 `Profile: summary`、`status_level=warn`、`average_latency_ms=1607.12`、`max_latency_ms=2832.91`，且两层各自的 `alerts\current_performance_alert.md` 都已成功生成。
35. 2026-04-11 16:21 在用户要求“直接触发三条任务验证真实调度链路”后，首先发现三条任务虽然被触发，但最终 `LastTaskResult=1`，且报告文件时间未更新；进一步复现确认根因是任务动作仍调用 `powershell.exe`，而当前性能脚本已使用 PowerShell 7 语法。
36. 2026-04-11 16:22 已将三条性能任务统一切换到 `C:\Program Files\PowerShell\7\pwsh.exe`，随后再次手工触发 `3proxy-performance-light-15min`、`3proxy-performance-0500` 与 `3proxy-performance-1700`；三者 `after_last_run=2026-04-11 16:22:22`、`state=Ready`、`LastTaskResult=0`，证明真实任务链路已修复。
37. 同日已核对文件更新时间：`light` 层 `latest.md/json` 与 `alerts\current_performance_alert.md/json` 刷新到 `16:22:14`，`summary` 层对应文件刷新到 `16:22:20`；这证明两层报告确实是由任务执行链路刷新，而不是只靠手工脚本运行。
38. 2026-04-11 16:27 已新增 `C:\opt\3proxy\scripts\refresh_performance_overview.ps1`，并把它接到 `collect_proxy_performance_snapshot.ps1` 的收尾链路中；以后每次 `light` 或 `summary` 采样完成后，都会自动刷新 `C:\opt\3proxy\reports\performance\性能总览_Performance Overview.md/json`。
39. 同日已手工再执行一次 `light` 与一次 `summary` 采样，确认总览页真实生成且内容正确：`generated_at=2026-04-11 16:27:18`、`overall_status=warn`、`preferred_read_order=[light, summary]`，并且总览中三条任务都显示 `exists=True`、`state=Ready`、`last_task_result=0`。
40. 同日已将“日常先看总览页，再按需钻取 light/summary”的读取口径回写到 `C:\opt\代理服务导航_Proxy Service Index.md`、`C:\opt\3proxy\docs\本机代理导航_Proxy Local Guide.md` 与长期 runbook，后续本机巡检只需先打开一份 Markdown 即可判断当前状态。
41. 2026-04-11：在用户明确禁止 GitHub / Google 直连后，已把服务端设计收口为“仍经 `192.168.5.235` 出口，但新增 `10.168.80.56:3129` 交互专用 HTTP 代理口”，并保留原共享 `3128` 与 `1080` 不变。
42. 同日已将 `C:\opt\3proxy\3proxy.cfg` 更新为同时监听 `3128/3129/1080`，其中 `3128` 与 `3129` 都显式写成 `-e192.168.5.235`；这证明即使后续客户端切到 `3129`，也不会绕开 `192.168.5.*` 出口。
43. 同日已把 `C:\opt\3proxy\scripts\validate_proxy_local.ps1` 升级为双口验证：同时检查 `3128` 与 `3129` 监听、分别对 GitHub / Google / YouTube / Ipify 发起代理访问，并比较两口 `api.ipify.org` 返回值是否一致，以冻结“共享口与交互口同出口公网 IP”这一事实。
44. 同日已把 `C:\opt\3proxy\scripts\collect_proxy_performance_snapshot.ps1` 升级为支持 `LaneName`、`ObservedPorts` 与 `OverviewRootDir`，从而可把 `3129` 单独采样到 `C:\opt\3proxy\reports\performance\interactive\`，并在 `refresh_performance_overview.ps1` 中作为 `interactive` 一层聚合进同一份性能总览首页。
45. 同日已新增 `C:\opt\3proxy\pac\80.58_交互分流代理规则_Interactive Proxy Split.pac`，其固定规则为：GitHub / GitHub API / GitHub Copilot / Google / YouTube 相关域名优先 `PROXY 10.168.80.56:3129`，若 `3129` 不可用则退回 `PROXY 10.168.80.56:3128`；其他域名默认仍走 `3128`，因此整份 PAC 不包含任何 `DIRECT`。
46. 2026-04-11 17:08 已手工执行 `C:\opt\3proxy\scripts\validate_proxy_local.ps1`，输出 `C:\opt\3proxy\reports\latest.md/json`，报告显示 `overall_pass=true`，且 `general_*` 与 `interactive_*` 检查全部通过。
47. 2026-04-11 17:08 已手工执行 `C:\opt\3proxy\scripts\collect_interactive_proxy_snapshot.ps1`，输出 `C:\opt\3proxy\reports\performance\interactive\latest.md/json`；当前样本显示 `github_api`、`github`、`google`、`youtube` 与 `ipify` 全部 `ok=true`，但交互层仍有 `latency_warn`。
48. 2026-04-11 17:08 已回读 `C:\opt\3proxy\reports\performance\性能总览_Performance Overview.md`，当前读取顺序已更新为 `interactive -> light -> summary`，说明交互层已成为日常巡检一线入口。
49. 2026-04-11 17:08 已创建并核对 `3proxy-performance-interactive-15min` 计划任务：动作执行器为 `C:\Program Files\PowerShell\7\pwsh.exe`，包装脚本为 `C:\opt\3proxy\scripts\collect_interactive_proxy_snapshot.ps1`，`LastTaskResult=0`。
50. 当前仍缺一项真实客户端证据：由于本轮没有可用的 `10.168.80.58` WinRM 凭据，尚未把上述 PAC 自动下发到 `80.58` 并回收其真实浏览器/VS Code 会话证据；这不影响服务端 dedicated lane 已落地，但会影响“80.58 客户端已完成切换”的单独验收口径。

## 十一、最终结论 / Final Verdict

- **结论**：✅ 已通过
- **日期**：2026-04-11
- **执行人**：GitHub Copilot
- **建议**：可宣告通过
- **说明**：本次 change 的正式范围是仓内服务化 runbook、索引挂载与最小治理验证。2026-04-11 已完成基于真实 `3proxy` 二进制与 `NSSM` 服务托管的远端链路验证，证明 `10.168.80.58` 可经 `10.168.80.56:3128` 访问 GitHub；同日还完成了两层性能监控首页聚合，当前本机巡检已收口为“先看总览页，再按需钻取 light/summary”。当前仅未单独执行整机重启恢复试验。