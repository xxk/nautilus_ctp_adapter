from __future__ import annotations

import json
from pathlib import Path

from scripts import ctp025292_runtime_pack_discover as discover_module
from scripts.ctp025292_runtime_pack_discover import discover_runtime_packs


def _write_pair(path: Path, *, md: bytes = b"md", td: bytes = b"td") -> dict[str, str]:
    path.mkdir(parents=True, exist_ok=True)
    (path / "thostmduserapi_se.dll").write_bytes(md)
    (path / "thosttraderapi_se.dll").write_bytes(td)
    return {
        filename: discover_module._file_sha256(path / filename)
        for filename in ("thostmduserapi_se.dll", "thosttraderapi_se.dll")
    }


def test_discovery_rejects_known_openctp_hashes(tmp_path: Path, monkeypatch) -> None:
    source = tmp_path / "openctp" / "bin"
    hashes = _write_pair(source, md=b"openctp-md", td=b"openctp-td")
    monkeypatch.setattr(discover_module, "KNOWN_OPENCTP_TTS_DLL_SHA256", hashes)

    payload = discover_runtime_packs([tmp_path])

    assert payload["success"] is False
    assert payload["candidate_count"] == 1
    candidate = payload["candidates"][0]
    assert candidate["classification"] == "known_openctp_tts_rejected"
    assert "candidate_known_openctp_tts" in candidate["issues"]


def test_discovery_keeps_unmarked_candidate_untrusted(tmp_path: Path) -> None:
    source = tmp_path / "vnpy_ctp" / "api"
    _write_pair(source, md=b"candidate-md", td=b"candidate-td")

    payload = discover_runtime_packs([tmp_path])

    assert payload["success"] is False
    assert payload["candidate_count"] == 1
    candidate = payload["candidates"][0]
    assert candidate["classification"] == "candidate_untrusted"
    assert "trust_marker_missing" in candidate["issues"]


def test_discovery_accepts_matching_operator_trust_marker(tmp_path: Path) -> None:
    source = tmp_path / "trusted" / "ctp025292" / "bin"
    hashes = _write_pair(source, md=b"trusted-md", td=b"trusted-td")
    (source / "_ctp025292_runtime_pack.json").write_text(
        json.dumps(
            {
                "runtime_pack_id": "ctp-live-025292-md",
                "source_kind": "operator_trusted_025292",
                "dlls": {
                    name: {"sha256": digest}
                    for name, digest in hashes.items()
                },
            }
        ),
        encoding="utf-8",
    )

    payload = discover_runtime_packs([tmp_path])

    assert payload["success"] is True
    assert payload["trusted_candidate_count"] == 1
    assert payload["candidates"][0]["classification"] == "operator_trusted_025292"
