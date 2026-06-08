# Cross Tracer Gate Fragment

**fragment-id**：`cross_tracer_gate`
**适用场景**：改动影响共享模块，需要跨 tracer gate 字段。

---

## Cross-Tracer Gate

| Tracer | 受影响面 | 验证命令 | 通过信号 |
| --- | --- | --- | --- |
| <tracer> | <surface> | <command> | <signal> |

## Gate Rules

1. 共享模块改动必须列出受影响 tracer。
2. 不能只用当前 tracer 的 happy path 证明共享模块安全。
