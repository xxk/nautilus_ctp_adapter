# Work Item Type System / 工作项类型系统

**状态**：proposed-specification
**ADR**：[ADR003](../adr/ADR003%20Doc%20Harness%20Capability%20Replication%20And%20Strategies%20Alignment.md)

---

## Canonical Metadata / 标准元数据

```yaml
work_item_type: governance | delivery | tracer
work_item_layer: proposal | change | tracer_row
surface_mode: none | ui | report | board | console
action_mode: read_only | request_only | execution_capable
```

`work_item_type` is the only formal classification field. Do not add `proposal_profile`, `proposal_type` or `change_kind` as a second taxonomy.

## Simplified Operating Vocabulary / 简化执行口径

| Daily term | Meaning | Canonical contract |
| --- | --- | --- |
| Proposal | the big objective and roll-up acceptance | `work_item_layer=proposal` |
| Change | the next executable slice with tests and acceptance | `work_item_layer=change` |
| Workflow | internal template/gate implementation | `docs/workflows/` fragments and gates |

Daily rule:

```text
Use Proposal for the big objective.
Use Change for the small executable step.
Use Work Item Contract metadata in files when modern routing is needed.
Let workflow/gate enforce details through work_item_type/work_item_layer/modes.
```

## Work Item Types / 工作项类型

| Type | Question It Answers | Adapter Examples | Must Not Do |
| --- | --- | --- | --- |
| `governance` | How are rules, templates, ADRs or gates defined? | ADR/template/gate/harness proposals | Produce runtime truth or live broker evidence |
| `delivery` | How is an adapter capability delivered? | runtime bridge, config, smoke, provider/client feature | Pretend to be a tracer without source/destination identity |
| `tracer` | Can this typed source-to-destination path be proven? | CTP config -> smoke evidence -> acceptance projection | Create a second runtime, writer, truth or readiness shortcut |

## Work Item Layers / 工作项层级

| Layer | Authority | Examples | Must Not Do |
| --- | --- | --- | --- |
| `proposal` | Long-running roadmap, phases, queues and roll-up acceptance | `docs/proposals/<proposal-id>/` | Replace child change execution evidence |
| `change` | Current executable slice, tests and acceptance evidence | `docs/changes/<change-id>/` | Rewrite proposal goals or merge unrelated slices |
| `tracer_row` | One source truth to destination proof item inside a proposal queue | proposal-local manifest row when used | Become proposal status or change acceptance |

## Modes / 模式

| Mode | Meaning | Additional Guard |
| --- | --- | --- |
| `surface_mode=none` | no UI/report/board/console surface | no surface-specific gate |
| `surface_mode=ui/report/board/console` | display or request surface exists | projection-only and no truth writeback |
| `action_mode=read_only` | no request, runtime or truth mutation | display/reconciliation only |
| `action_mode=request_only` | typed request may be produced | request is not result |
| `action_mode=execution_capable` | canonical owner may execute | no second runtime/writer; typed output artifact required |

## Boundary Rule / 边界规则

```text
Templates live in workflows.
Instances live in proposals and changes.
Evidence lives in changes and typed artifacts.
```

