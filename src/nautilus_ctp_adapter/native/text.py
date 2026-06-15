from __future__ import annotations

import ctypes


def decode_ctp_text_ptr(ptr: int | None) -> str:
    """Decode null-terminated text returned by the native CTP bridge."""
    if not ptr:
        return ""
    raw = ctypes.string_at(ptr)
    if not raw:
        return ""
    for encoding in ("utf-8", "gb18030"):
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="replace")
