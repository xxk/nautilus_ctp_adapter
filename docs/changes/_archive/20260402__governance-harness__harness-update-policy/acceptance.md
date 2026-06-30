# Acceptance: harness-update-policy

**change-id**: `20260402__governance-harness__harness-update-policy`
**创建日期**: 2026-04-02
**状态**: pass

## 继承事实

1. `docs/doc_harness_kit/checks/` 目录已存在，内含：`任务类型到验证入口速查表_Task Verification Matrix.md`、`接入检查清单_Adoption Checklist.md`、`最小守卫规范_Minimal Guardrails.md`、`运行手册_Runbook.md`。
2. 目前没有任何文件专门说明 topic 切换后治理层必须同步更新哪些文件，这是本 change 填补的空白。
3. C3 产出的 `scripts/check_topic_docs.py` 是本 checklist 的验证命令；C3 必须先于本 change 完成，或在同一 commit 中完成。

## 验收场景

### SC-1：checklist 文件存在

`docs/doc_harness_kit/checks/topic-transition-checklist.md` 存在。

### SC-2：3 项更新清单完整

checklist 包含以下 3 项，每项有"改什么文件 → 改哪个字段 → 改为什么值"的具体操作说明：
- AGENTS.md read order step 5
- `docs/topics/README.md` Current State 节
- `docs/README.md` Current Active Delivery 节

### SC-3：触发时机明确

checklist 中存在"触发时机"段落，说明 topic README `**状态**` 从 `进行中` 改为 `已完成` 时即触发。

### SC-4：包含验证命令

checklist 末尾包含 `python scripts/check_topic_docs.py` 验证命令。

### SC-5：doc_harness_kit README 已更新

`docs/doc_harness_kit/README.md` 中存在 `topic-transition-checklist.md` 的链接或条目。

## 最终结论

**conclusion**: pass

## 实际结果

1. SC-1：通过。`topic-transition-checklist.md` 已创建。
2. SC-2：通过。3 项更新清单完整。
3. SC-3：通过。触发时机已明确写为 topic 完成并切换到下一 topic 时必须同步执行。
4. SC-4：通过。文末包含 `python scripts/check_topic_docs.py`。
5. SC-5：通过。`docs/doc_harness_kit/README.md` 已加入 checklist 链接。

## 证据

1. [evidence_20260402_harness_update_policy.md](/D:/Nautilus/nautilus_ctp_adapter/docs/changes/20260402__governance-harness__harness-update-policy/evidence_20260402_harness_update_policy.md)
