# Decision Log Fragment

**fragment-id**：`decision_log`
**适用场景**：评审过程中产生了多轮需要保留的判断。

---

## Decision Log

| 日期 | 决策 | 原因 | 回写动作 | 明确不做 |
| --- | --- | --- | --- | --- |
| 2026-06-08 | 建立 P003 承接 provider capability readiness | P002 已完成 paper/repo provider baseline，但 paper 环境中仍缺 session、order lifecycle、reconciliation、recovery 和 ops evidence 的系统化补齐 | README GAP 表、phase-plan、acceptance、change-map | 不把 P002 completed 等同于 paper 能力全部闭环 |
| 2026-06-08 | P003 当前 profile 改为 `openctp-tts-7x24-simulation` | 用户明确要求使用 24 小时可调试 API 的模拟账户开发下达功能，暂时不要 formal Live | Top status block、artifact boundary、acceptance account matrix | 不使用 formal-trading / Live 作为当前验收条件 |
| 2026-06-08 | 授权 OpenCTP TTS 7x24 simulation 下达不超过 3 手 | 用户明确授权模拟账户下达 <=3 手；`zn2610 BUY 2` 已按 guarded order loop 执行 | Phase 3 guarded order evidence 回写 | 不扩大到 formal-trading，不默认保持 `AllowLiveOrderSmoke=true` |
| 2026-06-08 | Phase 1 只做 paper preflight/readiness，不发单 | order 前必须先冻结 config、redaction、session truth 和 blocker semantics | Phase 1 scope | 不在 preflight 阶段触发 native order send |
| 2026-06-08 | 第一条 order loop 限定为 guarded paper order | paper 环境可持续调试完整 order/cancel/fill/reject 链路，风险低且可复跑 | Phase 3 scope | 不扩展到正式实盘、多合约、多策略或自动交易 |
| 2026-06-08 | P003 closeout 采用 paper-only pass + typed blocker 口径 | 当前目标是补齐 OpenCTP paper provider 能力；unarmed paper send、不可控断线等安全/资源限制必须显式留为 typed blocker 或 successor evidence | Phase 3-5 acceptance、paper ops runbook | 不用 paper pass 关闭 formal-trading / Live readiness |

## 记录规则

1. 只记录会影响后续执行边界的稳定判断。
2. 已升格为长期规则的内容应回写到 `docs/architecture/` 或 `docs/adr/`。
3. 账号、密码、auth code 或 broker private fields 不得进入本文件。
