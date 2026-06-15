from __future__ import annotations

import ctypes

from nautilus_ctp_adapter.native.md_ctypes import _decode_ptr_text as decode_md_text
from nautilus_ctp_adapter.native.td_ctypes import _decode_ptr_text as decode_td_text
from nautilus_ctp_adapter.native.text import decode_ctp_text_ptr


def _ptr_for(raw: bytes) -> tuple[int, object]:
    buffer = ctypes.create_string_buffer(raw + b"\x00")
    return ctypes.addressof(buffer), buffer


def test_decode_ctp_text_ptr_accepts_empty_pointer() -> None:
    assert decode_ctp_text_ptr(None) == ""
    assert decode_ctp_text_ptr(0) == ""


def test_decode_ctp_text_ptr_preserves_utf8_text() -> None:
    ptr, buffer = _ptr_for("rb2610 order accepted".encode("utf-8"))

    assert decode_ctp_text_ptr(ptr) == "rb2610 order accepted"
    assert buffer.raw.endswith(b"\x00")


def test_decode_ctp_text_ptr_falls_back_to_gb18030_ctp_text() -> None:
    ptr, buffer = _ptr_for("报单已拒绝".encode("gb18030"))

    assert decode_ctp_text_ptr(ptr) == "报单已拒绝"
    assert decode_td_text(ptr) == "报单已拒绝"
    assert decode_md_text(ptr) == "报单已拒绝"
    assert buffer.raw.endswith(b"\x00")
