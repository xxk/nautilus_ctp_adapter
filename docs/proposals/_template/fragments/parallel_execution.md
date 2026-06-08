# Parallel Execution Fragment

**fragment-id**：`parallel_execution`
**适用场景**：并行搜索 tracer，需要 parallel proof 验收字段。

---

## Parallel Proof

| 维度 | 要求 | 证据 |
| --- | --- | --- |
| partitioning | 分片边界明确且可复现 | <evidence> |
| merge | 合并顺序不改变语义 | <evidence> |
| isolation | 分片输出互不污染 | <evidence> |

## Runtime Signals

1. <并行运行命令>
2. <聚合证据路径>
