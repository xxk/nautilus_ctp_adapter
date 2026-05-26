# Proposal Template Usage

`docs/proposals/_template/` 采用 base + fragments + profiles 的轻量组合口径：

1. `base/`：每个 proposal 都会复制的必需文件。
2. `fragments/`：可按需附加的片段文件。
3. `profiles/`：常见片段组合。
4. `meta/fragment_registry.yaml`：机器可读 fragment 列表。

推荐命令：

```bash
python scripts/new_proposal.py --root . --id <proposal-id> --profile multi_phase
```

只做预检、不写文件：

```bash
python scripts/new_proposal.py --root . --id <proposal-id> --profile multi_phase --check-only
```

手工追加 fragment：

```bash
python scripts/new_proposal.py --root . --id <proposal-id> --fragments design,review_lane
```

规则：

1. `README.md`、`phase-plan.md`、`acceptance.md` 是 proposal 最小闭环，不得删除。
2. proposal 顶部 `**状态**` 必须投影自 `phase-plan.md` 中的 `AI-PHASE-STATUS.overall_status`。
3. 如果 proposal 产生稳定架构或长期 owner 规则，closeout 前必须回流到 `docs/adr/` 或 `docs/architecture/`。# Proposal Template Usage

`docs/proposals/_template/` follows a small C+ pattern adapted from DSLResearch:

1. `base/` contains the required files copied into every proposal.
2. `fragments/` contains optional add-on documents.
3. `profiles/` contains reusable fragment combinations.
4. `meta/fragment_registry.yaml` is the machine-readable fragment map used by the scaffold and docs gate.

Preferred entry:

```bash
python scripts/new_proposal.py --root . --id <proposal-id> --profile multi_phase
```

Rules:

1. Keep stable design conclusions in `docs/architecture/` or `docs/adr/`, not inside proposals forever.
2. Proposal status lives in `phase-plan.md` `AI-PHASE-STATUS.overall_status`; README top status is only a projection.
3. Proposal acceptance must cite trusted artifact roots or executable entrypoints, not only test-only evidence.