# Acceptance / 验收基线

**proposal-id**：`p001-ADR001-native-first-runtime-rollout`
**状态**：in_progress

---

## 验收范围 / Scope

当前 proposal 验收以下内容：

1. ADR001 已有 canonical proposal carrier，不再只停留在 ADR 讨论层。
2. proposal 已冻结 phase split、child change mapping、artifact boundary 与 acceptance baseline。
3. 当前 proposal 明确阻止把正在执行的 vendor-bridge active change 扩张成性能 rollout 主承接面。

当前 proposal 不验收以下内容：

1. runtime batch boundary 的代码落地。
2. hot-path ownership 从 Python 到 native/Rust 的完整迁移。
3. thin Python shell contract lock 的测试落地。
4. benchmark 结果或 daemon 是否需要立项的最终结论。

补充口径：

1. A1-A4 是当前 proposal 收敛阶段必须守住的 success / failure / regression 场景。
2. A5-A11 是后续 Phase 1-4 child change 必须承接的验收义务，当前 proposal 只冻结这些场景的边界，不得把它们写成已通过证据。

---

## Artifact Root Rule

本文件引用的 formal artifact、projection、report、verdict 必须属于 sibling `phase-plan.md` 中声明的 `Artifact Trust Boundary`。

未冻结唯一受信根前，只允许记录“待冻结”或 repo-local 诊断留痕，不得把 proposal 外部 artifact 写成当前 proposal 的完成证据。

---

## Acceptance Evidence Boundary

1. `pytest`、mock、stub、monkeypatch 或其他 test-only 输出，只能作为 contract/function guard evidence，不得单独充当 proposal 正式验收证据。
2. proposal 验收场景若要写成 `passed`、`completed` 或等价完成结论，至少还需要一类非 test-only 证据：真实命令执行结果、受信 formal artifact、projection/read-model 结果、live/rendered surface 证据，或可复核的 source evidence。
3. 若当前只有 test/mock 结果，而没有真实入口、真实 artifact 或真实 consumer 证据，只能记录为 guard/reference，不得把该 proposal 场景写成正式收口完成。

---

## 场景矩阵 / Scenario Matrix

| ID | 类型 | 场景 | 验收方式 | 通过信号 | 状态 |
| --- | --- | --- | --- | --- | --- |
| A1 | success | proposal docs gate 通过，proposal 级 carrier 建立完成 | `python scripts/check_proposal_docs.py --root . --proposal-id p001-ADR001-native-first-runtime-rollout` | docs gate 通过，README/phase-plan/acceptance/fragment 闭环成立 | completed |
| A2 | failure | proposal 不得把外部 formal artifact 或 benchmark 结果冒充为当前已完成证据 | 文档审阅 + `phase-plan.md` artifact boundary | `trusted_artifact_roots` 仍为 `未冻结`，没有越权 closeout 语句 | completed |
| A3 | regression | proposal 不得改写当前 active vendor-bridge change 的职责 | `README.md` + `phase-plan.md` + `change-map.md` 审阅 | 当前 active change 仅作为 Phase 0/背景依赖，不作为性能 rollout 主 carrier | completed |
| A4 | regression | daemon 仍保持 gated future extension，而不是默认主线 | `ADR001` + `design.md` 审阅 | daemon 只出现在 benchmark gate phase / future extension 语义下 | completed |
| A5 | success | Phase 1 已冻结 adapter-facing batch runtime boundary | `phase-plan.md` Phase 1 + `20260529__runtime-performance__p1` 审阅 | `submit_command` / `drain_events(limit)` 或等价唯一 batch boundary 被写成主线，per-event Python callback 不再是默认长期边界，且 hot-path owner inventory 仍保留给 Phase 2 | in_progress |
| A6 | failure | Phase 1 不允许新增第二套 adapter-facing runtime API 或偷带 Phase 2/3 职责 | `20260529__runtime-performance__p1` design / touched code / tests 审阅 | 若出现 competing API 或 phase-mixing，必须标记为 fail-fast 或 reframing，不得进入 completed | in_progress |
| A7 | success | Phase 2 已冻结 hot-path ownership inventory 和迁移边界 | owner-cutover child change + runtime/adapter source evidence 审阅 | query / market / trading hot path 的 owner、暂留 Python 项、迁出项和验证入口均有明确列表；本 phase 不伪造“已全部 cutover” | planned |
| A8 | regression | Phase 2/3 不允许把新的 callback parse、state machine 或 query lifecycle ownership 写回 Python adapter | touched Python adapter diff + focused tests / guards 审阅 | Python adapter 只保留 Nautilus host integration，新增 runtime logic 被测试或文档 gate 阻断 | planned |
| A9 | success | Phase 3 已建立 thin Python host glue contract lock | thin-shell child change + adapter contract tests + architecture write-back 审阅 | 合法 Python entry、禁止回流的 runtime logic 类别和 focused guard evidence 同时存在 | planned |
| A10 | success | Phase 4 benchmark gate 能判定 in-process 主线是否足够，以及 daemon 是否需要新 proposal | benchmark-gate child change + report/artifact boundary 审阅 | 精确 benchmark 命令、阈值、formal artifact boundary 和 daemon trigger policy 均在该 child change 中被冻结并可复核；daemon 仍需单独 proposal 承接 | planned |
| A11 | failure | 没有 benchmark 或受信 artifact 时不得宣告 daemon 默认化或性能 rollout closeout | `phase-plan.md` artifact boundary + benchmark-gate evidence 审阅 | 缺量测时状态保持 `planned` / `blocked` / `reframing_required`，不得写成 pass/completed | planned |

---

## Evidence

| 证据 | 路径或命令 | 结论 |
| --- | --- | --- |
| Proposal scaffold created | `python scripts/new_proposal.py --root . --id p001-ADR001-native-first-runtime-rollout --profile multi_phase --fragments design` | proposal bundle 已生成 |
| ADR carrier created | `docs/proposals/p001-ADR001-native-first-runtime-rollout/` | ADR001 现在有 canonical proposal rollout path |
| Proposal docs gate | `python scripts/check_proposal_docs.py --root . --proposal-id p001-ADR001-native-first-runtime-rollout` | 2026-05-29 已验证通过；A1 作为 proposal convergence evidence completed |
| Proposal boundary review | `README.md` + `phase-plan.md` + `change-map.md` + `design.md` + `ADR001` | A2-A4 已用 source evidence 收口；未把外部 artifact、active vendor-bridge change 或 daemon 默认化写成完成证据 |
| Acceptance scenarios aligned | `docs/proposals/p001-ADR001-native-first-runtime-rollout/acceptance.md` | A5-A6 已随 Phase 1 child change 进入 in_progress；A7-A11 仍保持 planned |
| Phase 1 child change created | `docs/changes/20260529__runtime-performance__p1/` | P001 Phase 1 已进入 in_progress；source / Rust gate evidence 已回填；Python focused guard 因当前环境缺 `ctp_runtime._ctp_runtime` 暂未 closeout |

---

## Closeout Checklist

1. 所有 in-scope 场景都有证据。
2. 所有 formal artifact 引用都位于 proposal 已声明的受信 artifact roots 内。
3. residual risk 已回填到 proposal / phase-plan / follow-up child change。
4. 任何 proposal 场景都不得仅凭 test/mock 结果写成正式验收通过；若 test 是当前唯一证据，必须显式标注为 guard/reference，而不是 closeout evidence。
