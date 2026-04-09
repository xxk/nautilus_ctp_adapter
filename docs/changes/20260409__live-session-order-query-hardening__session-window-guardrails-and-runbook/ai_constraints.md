# Session Window Guardrails 与真实场景验收驱动 Runbook AI Constraints

**change-id**：20260409__live-session-order-query-hardening__session-window-guardrails-and-runbook
**topic-id**：live-session-order-query-hardening

## Allowed

1. 修改当前 change 三件套。
2. 修改 `docs/topics/roadmap/nautilus_adapter/live-session-order-query-hardening/README.md`。
3. 在必要时修改 `scripts/`、`src/nautilus_ctp_adapter/adapters/ctp/`、`tests/`，前提是改动直接服务于 A1-A6 的执行与判定。

## Not Allowed

1. 不得把本地未跟踪的 real-account config、密码或其他敏感值写入仓库。
2. 不得新增绕过现有 guardrails 的自动发单流程。
3. 不得把 `pytest` 或 mock 结果写成正式 live acceptance 通过。
4. 不得把非交易时段场景写成“顺便可以 live-send”。

## Working Mode

1. 必须先读 `acceptance.md`，再读 `plan.md`，先锁定当前最小阻塞场景再进入实现。
2. 每轮只解决一个阻塞 A1-A6 的最小缺口。
3. 如果某个场景无法判定成功/失败，优先补失败语义或 runbook，而不是扩大实现范围。

## Required Validation

```powershell
python scripts/check_topic_docs.py
python -m pytest
```

说明：`python -m pytest` 只在触及 `scripts/`、`src/` 或 `tests/` 时必跑；若本轮仅改当前 change 和 topic 文档，最低必跑是 `python scripts/check_topic_docs.py`。