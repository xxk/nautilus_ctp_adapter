# Subscription Restore And Batching 验收方案 / Acceptance Plan

**模板标识 / Template Marker**：standard
**变更目录 / Change Root**：./
**状态**：✅ 通过
**日期**：2026-04-02
**范围**：subscription restore and batching
**change-id**：20260402__nautilus-live-marketdata__subscription-restore-and-batching
**关联 plan**：./plan.md
**关联 ai_constraints**：./ai_constraints.md
**长期归宿 / Long-Term Target**：/D:/Nautilus/nautilus_ctp_adapter/docs/changes_topic/roadmap/nautilus_adapter/nautilus-live-marketdata/README.md

<!-- AI-STATUS-BEGIN -->
```yaml
conclusion: pass
allow_declare_pass: true
last_updated: "2026-04-02 11:56"
concluded_by: "Codex"

exit_conditions:
  E1_success_scenarios: pass
  E2_failure_scenarios: pass
  E3_verification_cmds: pass
  E4_evidence_collected: pass
  E5_real_acceptance_only: pass
  E6_minimum_scenarios: pass

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

1. 证明 `LiveDataClient` 具备可恢复的订阅状态视图。
2. 证明 data-side 批量 drain 语义对 `C4` 已足够稳定。

## 二、验收场景 / Scenarios

| # | 场景 | 执行命令/步骤 | 预期结果 | 成功信号 | 失败口径 | 证据路径 |
| --- | --- | --- | --- | --- | --- | --- |
| A1 | Success 1: 恢复状态明确 | 检查 data client/runtime | 有稳定 subscription state | 恢复前置条件明确 | 仍依赖隐式状态 | 当前 change |
| A2 | Success 2: batch drain 语义冻结 | 检查 drain contract | 批量行为稳定 | C4 不再重写 drain | drain contract 漂移 | 当前 change |
| A3 | Success 3: C4 可复用 | 对照 topic 目标 | smoke baseline 可直接继承 | topic 交接清楚 | 仍需重做 | 当前 change |
| A4 | Failure 1: 不越界做 execution | 对照 scope | 不触及下单主线 | 范围收敛 | 越界进 Topic 4 | 当前 change |
| A5 | Failure 2: 不重写 C2 bootstrap | 对照 C2 | 继承 bootstrap 主线 | 无 competing bootstrap | 再次分叉 | 当前 change |
| A6 | Boundary 1: 可交接给 C4 | 对照 topic queue | C4 可直接接力 | next action 清楚 | topic queue 模糊 | 当前 change |

## 三、验收结论 / Conclusion

1. `LiveDataClient` 已具备稳定的 restore state 与批量 drain contract。
2. 当前实现没有越界改 execution，也没有重写 `C2` 的 bootstrap 主线。
3. Topic 3 的 `C4` 已可直接复用这套 contract 去冻结正式 smoke baseline。

## 四、验证命令 / Verification Commands

```powershell
python -m pytest
python -m pip install -e .
```

## 五、证据 / Evidence

1. [evidence_20260402_subscription_restore_and_batching.md](/D:/Nautilus/nautilus_ctp_adapter/docs/changes/20260402__nautilus-live-marketdata__subscription-restore-and-batching/evidence_20260402_subscription_restore_and_batching.md)
