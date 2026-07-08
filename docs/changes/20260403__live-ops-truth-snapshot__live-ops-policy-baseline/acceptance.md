# Live Ops Policy Baseline 验收方案 / Acceptance Plan

**模板标识 / Template Marker**：standard
**变更目录 / Change Root**：./
**状态**：🟡 进行中（真实重跑受前置不稳定阻塞）
**日期**：2026-04-02
**范围**：live ops policy baseline
**change-id**：20260403__live-ops-truth-snapshot__live-ops-policy-baseline
**关联 plan**：./plan.md
**关联 ai_constraints**：./ai_constraints.md
**长期归宿 / Long-Term Target**：/D:/Nautilus/nautilus_ctp_adapter/docs/topics/live-ops-truth-snapshot.md

## 一、验收目标 / Goals

1. 冻结统一 live ops snapshot 的 policy/disposition 口径。
2. 继续保持真实 live smoke 为唯一验收证据来源。
3. 保持只读。

## 二、预期场景 / Planned Scenarios

1. live ops policy smoke 成功返回 0。
2. unified disposition 与 code bucket 归并规则稳定。
3. real-only evidence 口径继续保持。

## 三、当前状态 / Current State

1. supporting validation 已通过，但不作为验收证据：
   `python scripts/check_topic_docs.py`
   `python -m pytest D:\Nautilus\nautilus_ctp_adapter\tests\test_smoke_import.py -q`
2. 当前真实 `025292` 重跑已执行，但结果受高密度 `TD Front Disconnected: 4097` 影响，未达到可宣告通过的稳定口径。
3. 当前 acceptance 继续只认真实 live smoke；在重跑恢复稳定之前，不用 test/mock/fake 或本轮失败结果冒充通过。
