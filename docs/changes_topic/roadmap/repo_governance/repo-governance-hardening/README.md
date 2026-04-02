# Nautilus CTP Adapter Governance Harness Topic Roadmap

**创建日期**：2026-04-02
**最后更新**：2026-04-02
**状态**：已完成
**topic-id**：repo-governance-hardening
**用途**：修复 Topic 1→2→3 推进后治理层出现的 4 个陈旧点，建立 AGENTS.md 保持鲜活的切换规则，升级 changes_topic 索引，补齐最小文档门禁脚本，并沉淀 topic 切换 checklist；随后补齐 Rust 校验正式门禁。

---

## 一、背景

Topic 1 完成、Topic 2 完成、Topic 3 进入 `in_progress` 后，治理层出现以下已识别陈旧点：

1. `AGENTS.md` read order step 5 仍指向已完成的 `ctp-live-connectivity`，应指向当前活动 topic `nautilus-live-marketdata`。
2. `docs/changes_topic/README.md` 只列了 2 个 topic，遗漏了 `nautilus-instrument-provider` 和 `nautilus-live-marketdata`，且无 current state 信息。
3. 缺少最小文档门禁脚本（`check_topic_docs.py`），无法在手动或 CI 入口下机械验证治理层健康。
4. 缺少"topic 切换后治理层必须同步更新"的显式规则；每次切换都依赖人工记忆，下次必然再次陈旧。

## 二、与主线 Roadmap 的关系

本 topic 是治理辅线，不在主线 5 个 implementation topic 之内。主线进度（当前 Topic 3/5 进行中）不因本 topic 而暂停或推迟。两者可并行推进。

## 三、主题目标

1. 修复以上 4 个陈旧点，让治理层与当前主线进度一致。
2. 为 AGENTS.md 建立"topic 切换规则"，防止下次再度陈旧。
3. 提供可运行的最小文档门禁脚本。
4. 在 doc_harness_kit 沉淀 topic 切换 checklist，供后续任何 topic 切换时复用。

## 四、预期 Child Change 顺序

| 顺序 | change-id | 作用 | 状态 |
| --- | --- | --- | --- |
| C1 | `20260402__governance-harness__agents-entrypoint-sync` | 修复 AGENTS.md step 5 指向当前活动 topic；补充 topic 切换更新规则 | ✅ 已完成 |
| C2 | `20260402__governance-harness__changes-topic-index-upgrade` | 升级 `docs/changes_topic/README.md`：补全 topic 列表，加入 current state 信息 | ✅ 已完成 |
| C3 | `20260402__governance-harness__check-topic-docs-script` | 添加最小文档门禁脚本 `scripts/check_topic_docs.py` | ✅ 已完成 |
| C4 | `20260402__governance-harness__harness-update-policy` | 在 `docs/doc_harness_kit/checks/` 补充显式 topic 切换 checklist 文档 | ✅ 已完成 |
| C5 | `20260402__governance-harness__rust-validation-gate` | 把 Rust 校验从裸 `cargo check` 收敛为正式 gate 脚本与统一文档入口 | ✅ 已完成 |

## 五、AI-TASK-QUEUE

**当前状态**：已激活。

- [x] 完成 C1：agents-entrypoint-sync
- [x] 完成 C2：changes-topic-index-upgrade
- [x] 完成 C3：check-topic-docs-script
- [x] 完成 C4：harness-update-policy
- [x] 完成 C5：rust-validation-gate

**当前 first action**：治理辅线已完成；后续按 checklist 保持保鲜

## 六、Topic 级出口条件

1. `AGENTS.md` read order step 5 已更新为当前活动 topic，且附有切换更新规则。
2. `docs/changes_topic/README.md` 列出所有 6 个 topic（含本 governance topic），显示 current state。
3. `python scripts/check_topic_docs.py` 可运行，所有现有 topic README 通过，exit code = 0。
4. `docs/doc_harness_kit/checks/topic-transition-checklist.md` 存在且包含完整 3 项更新清单。
5. Rust 校验已具备统一脚本入口，在无 `cargo` 环境下也能给出明确 gate 失败语义。

## 七、完成结论

1. 已识别的治理层陈旧点已全部收口。
2. topic README 门禁脚本已落地并通过。
3. topic 切换 checklist 已沉淀到 harness kit。
4. Rust 校验已从裸命令提示升级成正式 gate。
