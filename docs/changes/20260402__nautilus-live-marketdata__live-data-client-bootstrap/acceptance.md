# Live Data Client Bootstrap 验收方案 / Acceptance Plan

**模板标识 / Template Marker**：standard
**变更目录 / Change Root**：./
**状态**：✅ 通过
**日期**：2026-04-02
**范围**：live data client bootstrap
**change-id**：20260402__nautilus-live-marketdata__live-data-client-bootstrap
**关联 plan**：./plan.md
**关联 ai_constraints**：./ai_constraints.md
**长期归宿 / Long-Term Target**：/D:/Nautilus/nautilus_ctp_adapter/docs/topics/roadmap/nautilus_adapter/nautilus-live-marketdata/README.md

<!-- AI-STATUS-BEGIN -->
```yaml
conclusion: pending
conclusion: pass
allow_declare_pass: true
last_updated: "2026-04-02 11:49"
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

1. 证明最小 `LiveDataClient` 主线已经成立。
2. 证明 Topic 3 的 `C3/C4` 可以在此基础上继续推进。

## 五、验收场景 / Scenarios

| # | 场景 | 执行命令/步骤 | 预期结果 | 成功信号 | 失败口径 | 证据路径 |
| --- | --- | --- | --- | --- | --- | --- |
| A1 | Success 1: bootstrap 成立 | 检查 data client 主线 | 有明确 bootstrap 入口 | data client 不再只是 topic1 residue | 仍是拼凑 | 当前 change |
| A2 | Success 2: 输出模型冻结 | 检查 data client output | 输出 shape 稳定 | 结果模型清楚 | 输出仍漂移 | 当前 change |
| A3 | Success 3: Topic 3 后续可复用 | 对照 topic 目标 | C3/C4 可直接接力 | 交接边界清楚 | 仍需重做 | 当前 change |
| A4 | Failure 1: 不越界做恢复/批量策略 | 对照 scope | 不提前完成 C3 | 范围收敛 | 范围失控 | 当前 change |
| A5 | Failure 2: 不重写 event contract | 对照 C1 | 继承 C1 contract | 无 competing contract | 再次分叉 | 当前 change |
| A6 | Boundary 1: 可交接给 C3 | 对照 topic queue | C3 可直接接力 | topic queue 清楚 | topic queue 模糊 | 当前 change |

## 六、验收结论 / Conclusion

1. `LiveDataClient` bootstrap 主线已经成立。
2. bootstrap 输出模型已冻结成稳定 shape。
3. 当前实现明确继承 `C1` 的 marketdata event contract，没有再发明 competing contract。
4. 当前实现没有越界提前完成恢复/批量策略，Topic 3 的 `C3` 仍保持独立实现空间。

## 七、验证命令 / Verification Commands

```powershell
python -m pytest
python -m pip install -e .
python scripts/ctp_live_data_client_bootstrap_smoke.py --config D:\Nautilus\nautilus_ctp_adapter\cfgs\local\ctp.live.025292.rb2610.10675.json --symbol rb2610
```

## 八、证据 / Evidence

1. [evidence_20260402_live_data_client_bootstrap.md](/D:/Nautilus/nautilus_ctp_adapter/docs/changes/20260402__nautilus-live-marketdata__live-data-client-bootstrap/evidence_20260402_live_data_client_bootstrap.md)
2. [live_data_client_bootstrap_smoke_20260402.log](/D:/Nautilus/nautilus_ctp_adapter/docs/changes/20260402__nautilus-live-marketdata__live-data-client-bootstrap/live_data_client_bootstrap_smoke_20260402.log)
