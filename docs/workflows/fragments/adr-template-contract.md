# ADR Template Contract Fragment / ADR 模板契约片段

ADR creation and ADR-shape edits are governance work. They must follow the template contract instead of hand-written free-form decision notes.

## Scope / 适用范围

This fragment applies when a work item creates a new ADR or materially changes an ADR's title, decision, owner boundary, landing map, or successor proposal boundary.

## Contract / 契约

1. The ADR must start from `docs/adr/ADR模板_ADR Template.md` or preserve the same required contract after pruning.
2. The frontmatter should include `status`, `date`, `decision-makers`, `owner`, `adr_id`, `decision_status`, and `landing_status`; legacy ADRs may omit `date` / `decision-makers` until touched.
3. The opening metadata block must include ADR type, decision status, landing status, landing summary, coverage summary, scope, decision question, current tendency, and final decision.
4. Standard and governance ADRs must include owner/canonical-entry impact, canonical naming check, design kernel, decision coverage and landing matrix, successor proposal boundary, ADR-level acceptance only, and ADR closeout distillation.
5. Filename slug, H1, current tendency, decision summary, design kernel, and successor proposal boundary must use one consistent core term family.
6. ADRs must not carry implementation acceptance truth. Commands, run output, transient artifact paths, screenshots, UI text, latest/debug paths, stdout, or chat text remain proposal/change evidence, not ADR truth.
7. ADR `decision_status`, frontmatter `status`, opening metadata, and final decision wording must not contradict each other.

## Workflow Boundary / 工作流边界

Workflow decides that ADR creation is a governance work item and therefore must use this fragment. The executable gate decides whether a concrete ADR passes.

