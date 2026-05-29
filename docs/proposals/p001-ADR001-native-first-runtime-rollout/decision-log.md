# Decision Log Fragment

**fragment-id**：`decision_log`
**适用场景**：评审过程中产生了多轮需要保留的判断。

---

## Decision Log

| 日期 | 决策 | 原因 | 回写动作 | 明确不做 |
| --- | --- | --- | --- | --- |
| 2026-05-29 | 为 ADR001 新建 `p001-ADR001-native-first-runtime-rollout` proposal | ADR 已有方向，但缺少多 phase rollout carrier，AI 无法稳定自动推进后续实现 | proposal bundle、proposal index、ADR001 landing map | 不把性能 rollout 并入当前 active vendor-bridge change |
| 2026-05-29 | 保持 `native-first runtime + thin Python host glue` 为 proposal 默认主线 | 这是当前 Nautilus 宿主约束下与既有 architecture 最一致的路线 | proposal README、design、phase-plan | 不把 pure native plugin / C++ rewrite 升为默认路线 |
| 2026-05-29 | external daemon 仅作为 Phase 4 benchmark-gated future extension | daemon 可能更激进，但只有在 batch/in-process 路线被量测证明不足时才值得立项 | ADR001 + proposal Phase 4 | 不在无 benchmark 证据时直接创建 daemon 实现面 |
| 2026-05-29 | 收紧 Phase 1-4 职责边界：Phase 1 只管 batch contract，Phase 2 只管 owner inventory / migration boundary，Phase 3 才冻结 thin-shell contract，Phase 4 才冻结 benchmark gate | 原始 landing map 与 proposal fragments 对 hot-path/host-glue/benchmark 责任有混线，后续 child change 会失去唯一边界 | phase-plan、design、change-map、acceptance、ADR001 landing map | 不在 proposal 收敛阶段伪造 Phase 1-4 完成证据 |

## 记录规则

1. 只记录会影响后续执行边界的稳定判断。
2. 已升格为长期规则的内容应回写到 `docs/architecture/` 或 `docs/adr/`。