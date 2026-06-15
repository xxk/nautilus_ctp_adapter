from __future__ import annotations

from pathlib import Path

import pytest

from scripts import ctp025292_runtime_pack_materialize as materialize_module
from scripts.ctp025292_runtime_pack_materialize import build_runtime_pack_summary


def _write_source_dlls(source_bin: Path, *, md: bytes = b"ctp025292-md", td: bytes = b"ctp025292-td") -> None:
    source_bin.mkdir(parents=True, exist_ok=True)
    (source_bin / "thostmduserapi_se.dll").write_bytes(md)
    (source_bin / "thosttraderapi_se.dll").write_bytes(td)


def test_candidate_source_is_inventory_only_and_not_materialized(tmp_path: Path) -> None:
    source_bin = tmp_path / "vnpy_ctp" / "api"
    target_bin = tmp_path / "runtime_packs" / "ctp-live-025292-md" / "bin"
    _write_source_dlls(source_bin)

    payload = build_runtime_pack_summary(
        source_bin=source_bin,
        target_bin=target_bin,
        source_kind="candidate_untrusted",
        materialize=True,
    )

    assert payload["success"] is False
    assert payload["status"] == "blocked"
    assert "runtime_source_not_operator_trusted_for_025292" in payload["issues"]
    assert "materialize_rejected_due_to_source_issues" in payload["issues"]
    assert not (target_bin / "thostmduserapi_se.dll").exists()


def test_operator_trusted_source_materializes_pack_with_manifest(tmp_path: Path) -> None:
    source_bin = tmp_path / "trusted" / "ctp025292"
    target_bin = tmp_path / "runtime_packs" / "ctp-live-025292-md" / "bin"
    _write_source_dlls(source_bin)

    payload = build_runtime_pack_summary(
        source_bin=source_bin,
        target_bin=target_bin,
        source_kind="operator_trusted_025292",
        materialize=True,
    )

    assert payload["success"] is True
    assert payload["status"] == "materialized"
    assert (target_bin / "thostmduserapi_se.dll").exists()
    assert (target_bin / "thosttraderapi_se.dll").exists()
    manifest = (target_bin / "_synced_from.txt").read_text(encoding="utf-8")
    assert "runtime_pack_id=ctp-live-025292-md" in manifest
    assert "loader_isolation=fresh_worker_process_per_runtime_pack" in manifest


def test_openctp_hash_is_rejected_even_if_operator_marks_trusted(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    source_bin = tmp_path / "openctp" / "bin"
    _write_source_dlls(source_bin, md=b"fake-openctp-md", td=b"fake-openctp-td")
    fake_openctp_hashes = {
        name: materialize_module._file_sha256(source_bin / name)
        for name in ("thostmduserapi_se.dll", "thosttraderapi_se.dll")
    }
    monkeypatch.setattr(materialize_module, "KNOWN_OPENCTP_TTS_DLL_SHA256", fake_openctp_hashes)

    payload = build_runtime_pack_summary(
        source_bin=source_bin,
        target_bin=tmp_path / "target",
        source_kind="operator_trusted_025292",
        materialize=True,
    )

    assert payload["success"] is False
    assert "source_dll_known_openctp_tts:thostmduserapi_se.dll" in payload["issues"]
    assert "source_dll_known_openctp_tts:thosttraderapi_se.dll" in payload["issues"]
    assert "materialize_rejected_due_to_source_issues" in payload["issues"]
