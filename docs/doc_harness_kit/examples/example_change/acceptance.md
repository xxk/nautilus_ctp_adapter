# 统一运行入口 / Unified Run Entrypoint 验收方案 / Acceptance Plan

**模板标识 / Template Marker**：standard
**变更目录 / Change Root**：./
**状态**：⬜ 待执行
**日期**：2026-03-27
**范围**：正式入口、兼容入口、导航回写
**change-id**：20260327__project-entry__unified-run-entrypoint
**关联 plan**：./plan.md
**关联 ai_constraints**：./ai_constraints.md
**长期归宿 / Long-Term Target**：docs/architecture/正式入口与兼容入口清单.md

<!-- AI-STATUS-BEGIN -->
```yaml
conclusion: pending
allow_declare_pass: false
last_updated: "2026-03-27 HH:MM"
concluded_by: ""

exit_conditions:
  E1_success_scenarios: pending
  E2_failure_scenarios: pending
  E3_verification_cmds: pending
  E4_evidence_collected: pending
  E5_real_acceptance_only: pending
  E6_minimum_scenarios: pending

scenarios:
  A1: { exec: false, result: null, blocking: true }
  A2: { exec: false, result: null, blocking: true }
  A3: { exec: false, result: null, blocking: true }
  A4: { exec: false, result: null, blocking: true }
  A5: { exec: false, result: null, blocking: true }
  A6: { exec: false, result: null, blocking: false }
```
<!-- AI-STATUS-END -->

## 总览看板 / Dashboard

### 验收总状态 / Overall

| 项目 | 值 | 说明 |
| --- | :---: | --- |
| 验收结论 | ⬜ 待执行 | 由 `AI-STATUS conclusion` 派生 |
| AI 建议宣告通过 | 否 | 由 `AI-STATUS allow_declare_pass` 派生 |
| 最后更新 | 2026-03-27 HH:MM | |
| AI 执行人 | — | |

### 出口条件 / Exit Criteria

| # | 出口条件 | 状态 | 判定规则 | 证据 |
| --- | --- | :---: | --- | --- |
| E1 | 关键成功场景全部通过 | ⬜ | 阻塞成功场景全部 ✅ | |
| E2 | 关键失败场景符合预期 | ⬜ | 阻塞失败场景全部 ✅ | |
| E3 | 必跑验证命令已完成 | ⬜ | `plan.md` 中声明的必跑命令已执行 | |
| E4 | 关键证据已留存 | ⬜ | 当前 change bundle 中存在证据路径 | |
| E5 | 正式验收不依赖 test、mock、fake | ⬜ | 只接受真实入口、真实环境、真实产物与真实证据；test/mock/fake 只能作为补充锁定证据 | |
| E6 | 正式场景数不少于 5 且至少 1 个 failure | ⬜ | 少于 5 个或没有 failure 场景时必须存在明确豁免说明 | |

### 场景看板 / Scenario Board

| # | 场景 | 执行 | 结论 | 阻塞 | 证据/备注 |
| --- | --- | :---: | :---: | :---: | --- |
| A1 | Success 1: 正式入口可执行 | ⬜ | ⬜ | 是 | |
| A2 | Success 2: 兼容入口行为明确 | ⬜ | ⬜ | 是 | |
| A3 | Success 3: 导航只指向正式入口 | ⬜ | ⬜ | 是 | |
| A4 | Failure 1: 旧入口不再承载真实实现 | ⬜ | ⬜ | 是 | |
| A5 | Failure 2: 文档和实现不再漂移 | ⬜ | ⬜ | 是 | |
| A6 | Boundary 1: 不扩大改动范围 | ⬜ | ⬜ | 否 | |

## 一、验收目标 / Goals

1. 证明项目已经存在唯一正式运行入口。
2. 证明兼容入口行为明确，不再与正式入口竞争。
3. 证明导航文档能把读者导向正式入口。

## 二、验收范围 / Scope

### 覆盖（In Scope）

1. 正式入口命令。
2. 兼容入口行为。
3. 导航与入口文档。

### 不覆盖（Out of Scope）

1. 部署自动化。
2. 远端环境联调。
3. 全量历史脚本清理。

## 三、前置条件 / Prerequisites

| 条件 | 类型 | 阻断开发 | 阻断验收 | 状态 | 备注 |
| --- | --- | :---: | :---: | :---: | --- |
| 目标项目存在至少一个当前可运行入口 | 环境 | 是 | 是 | ⬜ | |
| 目标项目已有导航或 architecture 索引 | 文档 | 否 | 是 | ⬜ | |

## 四、验收专属 AI 边界 / Acceptance-Only AI Boundaries

1. 任务级边界与必跑验证，以 sibling `plan.md` 为准。
2. 测试结果只能作为 contract/function 锁定证据，不能单独充当正式通过依据。
3. mock、stub、fake、monkeypatch、伪造返回值都不能作为正式验收证据。
4. 本例保留 6 个正式场景，满足“至少 5 个且至少 1 个 failure”的最低要求，便于跨项目直接复用该结构。

## 五、验收场景 / Scenarios

| # | 场景 | 执行命令/步骤 | 预期结果 | 成功信号 | 失败口径 | 证据路径 |
| --- | --- | --- | --- | --- | --- | --- |
| A1 | Success 1: 正式入口可执行 | `python <正式入口> --help` | 命令成功返回且帮助信息正确 | 退出码 = 0，帮助信息包含正式命令说明 | 退出码非 0 或仍指向旧入口 | |
| A2 | Success 2: 兼容入口行为明确 | 执行旧入口或查看兼容说明 | 旧入口要么转发到正式入口，要么显式提示弃用 | 日志/输出中明确写出正式入口或弃用说明 | 兼容入口继续承载真实主逻辑且无说明 | |
| A3 | Success 3: 导航只指向正式入口 | 阅读导航索引 | 文档能导向唯一正式入口 | 导航存在唯一入口说明 | 导航仍列出多个“正式入口” | |
| A4 | Failure 1: 旧入口不再承载真实实现 | 阅读兼容入口实现 | 旧入口只做转发、提示或显式失败 | 不再藏有真实主逻辑 | 兼容壳继续承载核心实现 | |
| A5 | Failure 2: 文档和实现不再漂移 | 对照入口文档和代码 | 导航、实现、长期文档一致 | 三处口径一致 | 文档说 A、代码跑 B | |
| A6 | Boundary 1: 不扩大改动范围 | 查看 diff | 只修改入口治理相关文件 | 无无关业务逻辑改动 | 顺手改了无关模块 | |

## 六、证据清单 / Evidence

| # | 证据类型 | 路径/链接 | 说明 |
| --- | --- | --- | --- |
| 1 | 正式入口命令输出 | | |
| 2 | 兼容入口输出或说明 | | |
| 3 | 导航文档链接 | | |

## 七、未通过处理 / On Failure

1. 回退到 `plan.md` 重新制定修复计划。
2. 不得覆盖已通过的历史证据。

## 八、真实验收待办清单 / Pending E2E Checklist

| # | 对应场景 | 当前阶段结果 | 还缺的真实验证 | 真实入口/命令 | 通过信号 | 阻塞项 | 证据路径 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| R1 | A1 | 未执行 | 跑正式入口帮助命令 | `python <正式入口> --help` | 退出码 = 0 | 目标项目命令待替换 | |
| R2 | A2 | 未执行 | 跑兼容入口或核对弃用提示 | `python <兼容入口> --help` | 输出明确写出正式入口 | 兼容入口待识别 | |

## 九、Contract/Function 锁定证据（可选）

| 项目 | 路径/命令 | 说明 |
| --- | --- | --- |
| Contract 锁定 | | |
| Function 锁定 | | |

## 十、最终结论 / Final Verdict

- **结论**：⬜ 待执行
- **日期**：
- **执行人**：
- **建议**：暂不建议宣告通过
- **说明**：
