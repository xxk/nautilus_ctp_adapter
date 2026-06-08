"""check_adr_docs: check ADR index discoverability and modern ADR shape."""
from __future__ import annotations

import argparse
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

FRONTMATTER_PATTERN = re.compile(r"\A---\s*\n(?P<body>.*?)\n---\s*(?:\n|\Z)", re.DOTALL)
FRONTMATTER_KV_PATTERN = re.compile(r"^(?P<key>[A-Za-z0-9_.-]+):\s*(?P<value>.*)$")

ADR_ID_PATTERN = re.compile(r"ADR(?P<num>\d{3})", re.IGNORECASE)
OPENING_LABELS = (
    "日期：",
    "ADR 类型：",
    "决策状态：",
    "落地状态：",
    "落地摘要：",
    "覆盖摘要：",
    "适用范围：",
    "决策问题：",
    "当前倾向：",
    "最终决策：",
)
REQUIRED_FRONTMATTER_KEYS = (
    "status",
    "owner",
    "adr_id",
    "decision_status",
    "landing_status",
)
TEMPLATE_FRONTMATTER_KEYS = REQUIRED_FRONTMATTER_KEYS + ("date", "decision-makers")
STANDARD_OR_GOVERNANCE_SNIPPETS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("Owner / Canonical Entry Impact", ("Owner / Canonical Entry Impact",)),
    ("Canonical Naming Check", ("概念判重 / Canonical Naming Check",)),
    ("Design Kernel", ("Design Kernel / 设计内核",)),
    ("Decision Coverage And Landing Matrix", ("Decision Coverage And Landing Matrix", "决策覆盖与落地矩阵")),
    ("Successor Boundary", ("Successor Proposal Boundary", "Successor Change Boundary", "后续 Proposal 边界", "后续 Change Boundary")),
    ("ADR-Level Acceptance Only", ("ADR-Level Acceptance Only / 仅限 ADR 级验收", "ADR-Level Acceptance Only")),
    ("ADR Closeout Distillation", ("ADR Closeout Distillation", "ADR closeout 沉淀")),
)
FORBIDDEN_EVIDENCE_BLOCKS = (
    "```bash",
    "```sh",
    "```powershell",
    "```console",
)


def parse_frontmatter(text: str) -> dict[str, str]:
    match = FRONTMATTER_PATTERN.match(text)
    if match is None:
        return {}
    metadata: dict[str, str] = {}
    for line in match.group("body").splitlines():
        kv = FRONTMATTER_KV_PATTERN.match(line.strip())
        if kv is None:
            continue
        metadata[kv.group("key")] = kv.group("value").strip().strip('"').strip("'")
    return metadata


def normalize_status(value: str) -> str:
    normalized = value.strip().strip("`").strip('"').strip("'").lower().replace("_", "-")
    if normalized in {"待评审", "待决策"}:
        return "proposed"
    if normalized in {"已接受", "生效"}:
        return "accepted"
    return normalized


def extract_line_value(text: str, label: str) -> str | None:
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith(f"- {label}"):
            return stripped[len(f"- {label}") :].strip()
        if stripped.startswith(label):
            return stripped[len(label) :].strip()
    return None


def discover_adr_files(root: Path, adr_id: str | None = None) -> list[Path]:
    adr_dir = root / "docs" / "adr"
    if not adr_dir.exists():
        return []
    files = [
        path
        for path in sorted(adr_dir.glob("*.md"))
        if path.name != "README.md" and "模板" not in path.name and "Template" not in path.name
    ]
    if adr_id is None:
        return files
    normalized_target = normalize_adr_id(adr_id)
    return [path for path in files if normalize_adr_id(extract_adr_id(path, path.read_text(encoding="utf-8"))) == normalized_target]


def normalize_adr_id(value: str) -> str:
    value = value.strip().strip('"').strip("'")
    match = ADR_ID_PATTERN.search(value)
    if match is not None:
        return f"ADR{int(match.group('num')):03d}"
    digits = re.sub(r"\D", "", value)
    if digits:
        return f"ADR{int(digits):03d}"
    return value


def extract_adr_id(path: Path, text: str) -> str:
    metadata = parse_frontmatter(text)
    if metadata.get("adr_id"):
        return normalize_adr_id(metadata["adr_id"])
    match = ADR_ID_PATTERN.search(path.name)
    if match is not None:
        return f"ADR{int(match.group('num')):03d}"
    return path.stem


def validate_template(root: Path) -> list[str]:
    template_path = root / "docs" / "adr" / "ADR模板_ADR Template.md"
    if not template_path.exists():
        return ["docs/adr/ADR模板_ADR Template.md does not exist"]

    errors: list[str] = []
    text = template_path.read_text(encoding="utf-8")
    metadata = parse_frontmatter(text)
    for key in TEMPLATE_FRONTMATTER_KEYS:
        if not metadata.get(key, "").strip():
            errors.append(f"docs/adr/ADR模板_ADR Template.md template frontmatter missing `{key}`")
    for label in OPENING_LABELS:
        if label not in text:
            errors.append(f"docs/adr/ADR模板_ADR Template.md template opening metadata missing `{label}`")
    for label, alternatives in STANDARD_OR_GOVERNANCE_SNIPPETS:
        if not any(snippet in text for snippet in alternatives):
            errors.append(f"docs/adr/ADR模板_ADR Template.md template missing `{label}`")
    return errors


def validate_one_adr(path: Path, root: Path, index_text: str) -> list[str]:
    relative_path = path.relative_to(root).as_posix()
    text = path.read_text(encoding="utf-8")
    metadata = parse_frontmatter(text)
    adr_id = extract_adr_id(path, text)
    errors: list[str] = []

    if adr_id not in index_text:
        errors.append(f"{relative_path}: ADR index does not reference `{adr_id}`")

    for key in REQUIRED_FRONTMATTER_KEYS:
        if not metadata.get(key, "").strip():
            errors.append(f"{relative_path}: frontmatter missing `{key}`")

    for label in OPENING_LABELS:
        if label not in text:
            errors.append(f"{relative_path}: opening metadata missing `{label}`")

    h1_count = sum(1 for line in text.splitlines() if line.startswith("# "))
    if h1_count != 1:
        errors.append(f"{relative_path}: expected exactly one H1, found {h1_count}")

    decision_status = normalize_status(metadata.get("decision_status", ""))
    frontmatter_status = normalize_status(metadata.get("status", ""))
    if decision_status and frontmatter_status:
        compatible = (
            frontmatter_status.startswith(decision_status)
            or (frontmatter_status == "待评审" and decision_status == "proposed")
            or (frontmatter_status.startswith("superseded") and decision_status == "superseded")
            or (frontmatter_status.startswith("deprecated") and decision_status in {"archived", "superseded"})
        )
        if not compatible:
            errors.append(
                f"{relative_path}: frontmatter `status` and `decision_status` disagree: "
                f"{metadata.get('status')} vs {metadata.get('decision_status')}"
            )

    opening_decision = normalize_status(extract_line_value(text, "决策状态：") or "")
    if opening_decision and decision_status and opening_decision != decision_status:
        errors.append(f"{relative_path}: opening `决策状态` and frontmatter `decision_status` disagree")

    opening_landing = normalize_status(extract_line_value(text, "落地状态：") or "")
    landing_status = normalize_status(metadata.get("landing_status", ""))
    if opening_landing and landing_status and opening_landing != landing_status:
        errors.append(f"{relative_path}: opening `落地状态` and frontmatter `landing_status` disagree")

    final_decision = (extract_line_value(text, "最终决策：") or "").lower()
    if decision_status in {"draft", "proposed"} and any(token in final_decision for token in ("accepted", "已接受")):
        errors.append(f"{relative_path}: proposed/draft ADR must not claim accepted final decision")
    if decision_status == "accepted" and any(token in final_decision for token in ("待决策", "pending")):
        errors.append(f"{relative_path}: accepted ADR final decision must not remain pending")

    adr_type = (extract_line_value(text, "ADR 类型：") or "").lower()
    if "standard" in adr_type or "governance" in adr_type:
        for label, alternatives in STANDARD_OR_GOVERNANCE_SNIPPETS:
            if not any(snippet in text for snippet in alternatives):
                errors.append(f"{relative_path}: standard/governance ADR missing `{label}`")

    lowered_text = text.lower()
    for snippet in FORBIDDEN_EVIDENCE_BLOCKS:
        if snippet in lowered_text:
            errors.append(f"{relative_path}: ADR must not carry implementation evidence block `{snippet}`")

    return errors


def validate_adr_docs(root: Path, adr_id: str | None = None) -> list[str]:
    errors = validate_template(root)
    index_path = root / "docs" / "adr" / "README.md"
    if not index_path.exists():
        return [*errors, "docs/adr/README.md does not exist"]
    index_text = index_path.read_text(encoding="utf-8")

    adr_files = discover_adr_files(root, adr_id=adr_id)
    if adr_id is not None and not adr_files:
        errors.append(f"ADR not found: {adr_id}")
        return errors

    for adr_path in adr_files:
        errors.extend(validate_one_adr(adr_path, root, index_text))
    return errors


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="check_adr_docs")
    parser.add_argument("--root", type=Path, default=REPO_ROOT, help="Repository root")
    parser.add_argument("--adr-id", help="Optional ADR id, for example ADR003 or 003")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    root = args.root.resolve()
    errors = validate_adr_docs(root, adr_id=args.adr_id)
    if errors:
        for error in errors:
            print(f"ADR_DOCS_FAILED: {error}")
        print(f"ADR_DOCS_CHECK_FAIL: {len(errors)} issues")
        return 1
    suffix = f": adr={normalize_adr_id(args.adr_id)}" if args.adr_id else ""
    print(f"ADR_DOCS_CHECK_OK{suffix}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
