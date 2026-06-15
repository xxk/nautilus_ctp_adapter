from __future__ import annotations

import json
from pathlib import Path

from scripts import ctp025292_runtime_pack_trust_marker as marker_module
from scripts.ctp025292_runtime_pack_discover import discover_runtime_packs
from scripts.ctp025292_runtime_pack_trust_marker import build_trust_marker_preview


def _write_pair(path: Path, *, md: bytes = b"md", td: bytes = b"td") -> dict[str, str]:
    path.mkdir(parents=True, exist_ok=True)
    (path / "thostmduserapi_se.dll").write_bytes(md)
    (path / "thosttraderapi_se.dll").write_bytes(td)
    return {
        filename: marker_module._file_sha256(path / filename)
        for filename in ("thostmduserapi_se.dll", "thosttraderapi_se.dll")
    }


def test_preview_without_operator_ack_does_not_write_marker(tmp_path: Path) -> None:
    source = tmp_path / "candidate"
    _write_pair(source)

    payload = build_trust_marker_preview(source_bin=source, operator_ack=False, write=True)

    assert payload["success"] is False
    assert "operator_ack_missing" in payload["issues"]
    assert "write_rejected_due_to_marker_issues" in payload["issues"]
    assert not (source / "_ctp025292_runtime_pack.json").exists()


def test_operator_ack_writes_marker_and_discovery_accepts_it(tmp_path: Path) -> None:
    source = tmp_path / "trusted" / "bin"
    hashes = _write_pair(source, md=b"trusted-md", td=b"trusted-td")

    payload = build_trust_marker_preview(source_bin=source, operator_ack=True, write=True)

    assert payload["success"] is True
    marker = json.loads((source / "_ctp025292_runtime_pack.json").read_text(encoding="utf-8"))
    assert marker["runtime_pack_id"] == "ctp-live-025292-md"
    assert marker["source_kind"] == "operator_trusted_025292"
    for filename, digest in hashes.items():
        assert marker["dlls"][filename]["sha256"] == digest
    discovery = discover_runtime_packs([tmp_path])
    assert discovery["success"] is True
    assert discovery["trusted_candidate_count"] == 1


def test_known_openctp_hash_rejected_even_with_operator_ack(tmp_path: Path, monkeypatch) -> None:
    source = tmp_path / "openctp"
    hashes = _write_pair(source, md=b"openctp-md", td=b"openctp-td")
    monkeypatch.setattr(marker_module, "KNOWN_OPENCTP_TTS_DLL_SHA256", hashes)

    payload = build_trust_marker_preview(source_bin=source, operator_ack=True, write=True)

    assert payload["success"] is False
    assert "source_dll_known_openctp_tts:thostmduserapi_se.dll" in payload["issues"]
    assert "source_dll_known_openctp_tts:thosttraderapi_se.dll" in payload["issues"]
    assert not (source / "_ctp025292_runtime_pack.json").exists()
