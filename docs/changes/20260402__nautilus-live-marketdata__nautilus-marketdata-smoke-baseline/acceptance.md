# Nautilus Marketdata Smoke Baseline 验收方案 / Acceptance Plan

**模板标识 / Template Marker**：standard
**变更目录 / Change Root**：./
**状态**：✅ 通过
**日期**：2026-04-02
**范围**：marketdata smoke baseline
**change-id**：20260402__nautilus-live-marketdata__nautilus-marketdata-smoke-baseline
**关联 plan**：./plan.md
**关联 ai_constraints**：./ai_constraints.md
**长期归宿 / Long-Term Target**：/D:/Nautilus/nautilus_ctp_adapter/docs/changes_topic/roadmap/nautilus_adapter/nautilus-live-marketdata/README.md

<!-- AI-STATUS-BEGIN -->
```yaml
conclusion: pass
allow_declare_pass: true
last_updated: "2026-04-02 12:07"
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

1. 证明 Topic 3 的正式 marketdata smoke 入口已经固定。
2. 证明 `rb2610` 能从当前 `LiveDataClient` 主线稳定收到真实 tick。

## 二、验收场景 / Scenarios

| # | 场景 | 执行命令/步骤 | 预期结果 | 成功信号 | 失败口径 | 证据路径 |
| --- | --- | --- | --- | --- | --- | --- |
| A1 | Success 1: 正式入口存在 | 执行 smoke 脚本 | 有稳定脚本入口 | 命令固定 | 仍依赖临时脚本 | 当前 change |
| A2 | Success 2: 真实 `rb2610` tick | 运行 live smoke | 收到真实 tick | symbol = `rb2610` | 只登录不出 tick | 当前 change |
| A3 | Success 3: 继承 C2/C3 | 对照输出 | bootstrap + batch contract 可见 | Topic 4 可直接复用 | 又起一条新主线 | 当前 change |
| A4 | Failure 1: 不越界做 execution | 对照 scope | 不触及真发单主线 | 范围收敛 | 越界到 Topic 4 | 当前 change |
| A5 | Failure 2: 不回退到托管主线 | 对照仓内口径 | 继续走 repo-owned c wrapper | 无 C# 主线依赖 | 回退到 managed host | 当前 change |
| A6 | Boundary 1: Topic 3 可关闭 | 对照 topic queue | Topic 4 进入条件清楚 | mainline 可前推 | topic 级出口仍模糊 | 当前 change |

## 三、验收结论 / Conclusion

1. Topic 3 的正式 marketdata smoke 入口已经固定。
2. `rb2610` 能从当前 `LiveDataClient` 主线稳定收到真实 tick。
3. 当前实现继续走 repo-owned local c wrapper，没有回退到托管主线。

## 四、验证命令 / Verification Commands

```powershell
python -m pytest
python -m pip install -e .
python scripts/ctp_marketdata_smoke.py --config D:\Nautilus\nautilus_ctp_adapter\cfgs\local\ctp.live.025292.rb2610.10675.json --symbol rb2610
```

## 五、证据 / Evidence

1. [evidence_20260402_nautilus_marketdata_smoke_baseline.md](/D:/Nautilus/nautilus_ctp_adapter/docs/changes/20260402__nautilus-live-marketdata__nautilus-marketdata-smoke-baseline/evidence_20260402_nautilus_marketdata_smoke_baseline.md)
2. [marketdata_smoke_20260402.log](/D:/Nautilus/nautilus_ctp_adapter/docs/changes/20260402__nautilus-live-marketdata__nautilus-marketdata-smoke-baseline/marketdata_smoke_20260402.log)
