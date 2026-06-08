# Factor Board Fragment

**fragment-id**：`factor_board`
**适用场景**：Factor Board 验收字段。

---

## Factor Board Acceptance

| Section | 必需信号 | 证据 |
| --- | --- | --- |
| decision | 决策状态可见 | <evidence> |
| performance | 关键收益指标可追踪 | <evidence> |
| evidence_links | artifact link 可打开且受信 | <evidence> |

## UI Contract

1. 影响 board label、flag、key 或 section 可见性的改动必须有 CONTRACT-LOCK 测试。
