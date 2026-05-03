from __future__ import annotations

import json
from pathlib import Path


def write_json_payload(*, path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def resolve_flow_mode(*, flow_path: Path | None) -> str:
    return "explicit_override" if flow_path is not None else "default_shared_flow"


def resolve_session_label(*, session_label: str | None, flow_path: Path | None) -> str:
    if session_label is not None:
        normalized = session_label.strip()
        if not normalized:
            raise ValueError("session_label cannot be blank")
        return normalized
    return "isolated-flow" if flow_path is not None else "shared-flow"


def resolve_export_path(
    *,
    output_json: Path | None,
    evidence_root: Path | None,
    session_label: str,
    default_file_name: str,
) -> Path | None:
    if output_json is not None and evidence_root is not None:
        raise ValueError("output_json conflicts with evidence_root; choose one export target")
    if output_json is not None:
        return output_json
    if evidence_root is None:
        return None
    return evidence_root / session_label / default_file_name


def build_export_metadata(
    *,
    export_path: Path | None,
    evidence_root: Path | None,
    session_label: str,
    explicit_path: bool,
) -> dict[str, object] | None:
    if export_path is None:
        return None
    return {
        "path": str(export_path),
        "written": True,
        "session_label": session_label,
        "evidence_root": None if evidence_root is None else str(evidence_root),
        "explicit_path": explicit_path,
    }