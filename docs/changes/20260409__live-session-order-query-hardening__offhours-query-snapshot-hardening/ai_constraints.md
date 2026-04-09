# Offhours Query Snapshot Hardening AI Constraints

**change-id**：20260409__live-session-order-query-hardening__offhours-query-snapshot-hardening
**topic-id**：live-session-order-query-hardening

## Allowed

1. 修改 `scripts/`、`src/nautilus_ctp_adapter/adapters/ctp/`、`tests/`。
2. 修改当前 change 三件套。
3. 修改 `docs/topics/roadmap/nautilus_adapter/live-session-order-query-hardening/README.md` 以同步 offhours-first 优先级。

## Not Allowed

1. 不得新增真实下单、撤单、改单行为。
2. 不得把本地 real-account config 或 broken-config 副本提交进仓库。
3. 不得把 `pytest`、mock 或 dry-run 结果写成正式只读 live acceptance 通过。
4. 不得把 read-only 路径做成“看起来也能 live-send”的模糊入口。

## Working Mode

1. 先读 sibling `acceptance.md`，再读 `plan.md`，优先解决 A1-A6 中最阻塞 offhours 开发的场景。
2. 一次只修一个最小缺口，优先补清晰语义，再补新功能。
3. 如果脚本输出已经足够清楚，不为“统一”而额外新增 CLI。

## Required Validation

```powershell
python scripts/check_topic_docs.py
python -m pytest
```

说明：仅当本轮触及 `scripts/`、`src/` 或 `tests/` 时，`python -m pytest` 才是必跑项；若只改文档，最低验证为 `python scripts/check_topic_docs.py`。