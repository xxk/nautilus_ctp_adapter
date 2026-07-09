# 仓内维护 ctpnative wrapper 启动变更 验收方案

**模板标识 / Template Marker**：standard
**变更目录 / Change Root**：./
**状态**：✅ 已完成
**日期**：2026-04-01
**范围**：`native/`、`vendor/ctp/`、`rust/ctp_runtime_core/`
**change-id**：20260401__ctp-live-connectivity__repo-owned-ctpnative-wrapper-bootstrap
**关联 plan**：./plan.md
**关联 ai_constraints**：./ai_constraints.md
**长期归宿 / Long-Term Target**：/D:/Nautilus/nautilus_ctp_adapter/docs/architecture/platform-neutral-ctp-runtime.md

<!-- AI-STATUS-BEGIN -->
```yaml
conclusion: passed
allow_declare_pass: true
last_updated: "2026-04-02 18:40"
concluded_by: "Codex"

exit_conditions:
  E1_success_scenarios: passed
  E2_failure_scenarios: passed
  E3_verification_cmds: passed
  E4_evidence_collected: passed
  E5_real_acceptance_only: passed
  E6_minimum_scenarios: passed

scenarios:
  A1: { exec: true, result: pass, blocking: true }
  A2: { exec: true, result: pass, blocking: true }
  A3: { exec: true, result: pass, blocking: true }
  A4: { exec: true, result: pass, blocking: true }
  A5: { exec: true, result: pass, blocking: true }
  A6: { exec: true, result: pass, blocking: false }
```
<!-- AI-STATUS-END -->

## 一、验收目标 / Goals

1. 证明仓内维护 `ctpnative` 的边界已经从“方向”收敛成可执行规则
2. 证明后续 Python/Rust 主线可依赖仓内 native 边界，而不是长期依赖临时宿主

## 五、验收场景 / Scenarios

| # | 场景 | 执行命令/步骤 | 预期结果 | 成功信号 | 失败口径 | 证据路径 |
| --- | --- | --- | --- | --- | --- | --- |
| A1 | Success 1: vendor/native 归属清晰 | 检查 `vendor/ctp/README.md` 与 plan | 仓内维护边界清楚 | 明确写出仓内维护范围与外部样例范围 | 仍依赖“看代码猜” | 当前 change |
| A2 | Success 2: native ABI 最小面明确 | 检查 native/runtime 文档或代码 | 后续 runtime 可依赖统一 native ABI | 导出职责与 runtime 边界一致 | ABI 仍模糊 | 当前 change |
| A3 | Success 3: 同步路径可复用 | 检查 `scripts/` 与 README | vendor/native 获取方式可重复 | 有稳定同步口径 | 仍需手工散复制 | 当前 change |
| A4 | Failure 1: 未引入宿主专属长期依赖 | 检查 plan 与实现 | 未把 C# 宿主继续固化为长期方案 | 文档明确否定宿主长期归属 | 仍把宿主当正式实现 | 当前 change |
| A5 | Failure 2: 未把 Nautilus glue 和 native 边界混层 | 检查目录与 plan | native change 不直接侵入 adapter glue | 落点与边界匹配 | native 与 adapter 混写 | 当前 change |
| A6 | Boundary 1: 只冻结边界，不提前实现完整行情交易 | 对照 scope | 未越界实现不属于本 change 的能力 | scope / out-of-scope 清晰 | 任务范围失控 | 当前 change |
