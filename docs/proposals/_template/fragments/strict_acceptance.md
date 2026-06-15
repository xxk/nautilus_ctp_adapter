# Strict Acceptance Fragment

**fragment-id**：`strict_acceptance`
**适用场景**：medium/high 复杂度 proposal，需要超越基本验收场景。

---

## Strict Acceptance Addendum

| ID | 类型 | 严格场景 | 验收方式 | 通过信号 | 状态 |
| --- | --- | --- | --- | --- | --- |
| S1 | success | 正式入口或接近正式入口通过 | <命令/检查> | <通过信号> | planned |
| S2 | failure | 缺受信 artifact 时拒绝通过 | <命令/检查> | <拒绝信号> | planned |
| S3 | regression | 历史 debug / 外部 artifact 不被误用 | <命令/检查> | <无误用> | planned |
