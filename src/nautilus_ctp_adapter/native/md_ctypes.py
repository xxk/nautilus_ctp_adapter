from __future__ import annotations

import ctypes
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from .loader import add_windows_dll_directories, find_native_pack_dir, find_repo_owned_native_dll
from .text import decode_ctp_text_ptr


@dataclass(slots=True)
class NativeLoginResponseView:
    success: bool
    error_id: int
    error_message: str
    front_id: int
    session_id: int
    max_order_ref: int


@dataclass(slots=True)
class NativeTickView:
    symbol: str
    last: float
    bid: float
    ask: float
    ts_epoch_us: int
    bid_size: int
    ask_size: int
    volume: int
    open_interest: float


class _NativeTick(ctypes.Structure):
    _fields_ = [
        ("symbol", ctypes.c_void_p),
        ("last", ctypes.c_double),
        ("bid", ctypes.c_double),
        ("ask", ctypes.c_double),
        ("ts_epoch_us", ctypes.c_longlong),
        ("bid_size", ctypes.c_int),
        ("ask_size", ctypes.c_int),
        ("volume", ctypes.c_int),
        ("open_interest", ctypes.c_double),
    ]


class _NativeLoginResponse(ctypes.Structure):
    _fields_ = [
        ("FrontId", ctypes.c_int),
        ("SessionId", ctypes.c_int),
        ("MaxOrderRef", ctypes.c_longlong),
        ("ErrorId", ctypes.c_int),
        ("ErrorMsg", ctypes.c_void_p),
    ]


MdOnLoginCallback = ctypes.CFUNCTYPE(None, ctypes.POINTER(_NativeLoginResponse))
MdOnFrontDisconnectedCallback = ctypes.CFUNCTYPE(None, ctypes.c_int)
MdOnTickCallback = ctypes.CFUNCTYPE(None, ctypes.POINTER(_NativeTick))


def _decode_ptr_text(ptr: int | None) -> str:
    return decode_ctp_text_ptr(ptr)


class CtpMdApi:
    """Repository-owned Python ctypes boundary for MD-only smoke/bootstrap."""

    def __init__(self, dll: object) -> None:
        self._dll = dll
        self._bind_signatures()
        self._callback_refs: list[object] = []

    @classmethod
    def load(cls, base_dir: str | Path) -> "CtpMdApi":
        root = Path(base_dir)
        native_dll = find_repo_owned_native_dll(root)
        if native_dll is None:
            raise FileNotFoundError(f"unable to locate repo-owned ctp_native.dll under {root}")
        native_dir = find_native_pack_dir(root)
        dll_dirs = [native_dll.parent]
        if native_dir is not None and native_dir != native_dll.parent:
            dll_dirs.append(native_dir)
        add_windows_dll_directories(*dll_dirs)
        dll = ctypes.CDLL(str(native_dll))
        return cls(dll)

    def create(self, flow_path: str | Path) -> int:
        return int(self._dll.MdCreate(str(flow_path).encode("utf-8")))

    def dispose(self, handle: int) -> None:
        self._dll.MdDispose(ctypes.c_void_p(handle))

    def init(self, handle: int, front: str) -> int:
        return int(self._dll.MdInit(ctypes.c_void_p(handle), front.encode("utf-8")))

    def login(self, handle: int, broker_id: str, user_id: str, password: str) -> int:
        return int(
            self._dll.MdLogin(
                ctypes.c_void_p(handle),
                broker_id.encode("utf-8"),
                user_id.encode("utf-8"),
                password.encode("utf-8"),
            )
        )

    def subscribe(self, handle: int, instruments: list[str]) -> int:
        encoded = [item.encode("utf-8") for item in instruments]
        instrument_array = (ctypes.c_char_p * len(encoded))(*encoded)
        return int(
            self._dll.MdSubscribe(
                ctypes.c_void_p(handle),
                ctypes.cast(instrument_array, ctypes.c_void_p),
                len(encoded),
            )
        )

    def set_login_callback(
        self,
        handle: int,
        callback: Callable[[NativeLoginResponseView], None],
    ) -> object:
        def _wrapped(resp_ptr: ctypes.POINTER(_NativeLoginResponse)) -> None:
            resp = resp_ptr.contents
            callback(
                NativeLoginResponseView(
                    success=int(resp.ErrorId) == 0,
                    error_id=int(resp.ErrorId),
                    error_message=_decode_ptr_text(resp.ErrorMsg),
                    front_id=int(resp.FrontId),
                    session_id=int(resp.SessionId),
                    max_order_ref=int(resp.MaxOrderRef),
                )
            )

        callback_ref = MdOnLoginCallback(_wrapped)
        self._callback_refs.append(callback_ref)
        self._dll.MdSetLoginCallback(ctypes.c_void_p(handle), callback_ref)
        return callback_ref

    def set_tick_callback(
        self,
        handle: int,
        callback: Callable[[NativeTickView], None],
    ) -> object:
        def _wrapped(tick_ptr: ctypes.POINTER(_NativeTick)) -> None:
            tick = tick_ptr.contents
            callback(
                NativeTickView(
                    symbol=_decode_ptr_text(tick.symbol),
                    last=float(tick.last),
                    bid=float(tick.bid),
                    ask=float(tick.ask),
                    ts_epoch_us=int(tick.ts_epoch_us),
                    bid_size=int(tick.bid_size),
                    ask_size=int(tick.ask_size),
                    volume=int(tick.volume),
                    open_interest=float(tick.open_interest),
                )
            )

        callback_ref = MdOnTickCallback(_wrapped)
        self._callback_refs.append(callback_ref)
        self._dll.MdSetCallback(ctypes.c_void_p(handle), callback_ref)
        return callback_ref

    def set_front_disconnected_callback(self, handle: int, callback: Callable[[int], None]) -> object:
        callback_ref = MdOnFrontDisconnectedCallback(lambda reason: callback(int(reason)))
        self._callback_refs.append(callback_ref)
        self._dll.MdSetFrontDisconnectedCallback(ctypes.c_void_p(handle), callback_ref)
        return callback_ref

    def _bind_signatures(self) -> None:
        self._dll.MdCreate.argtypes = [ctypes.c_char_p]
        self._dll.MdCreate.restype = ctypes.c_void_p
        self._dll.MdDispose.argtypes = [ctypes.c_void_p]
        self._dll.MdInit.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
        self._dll.MdInit.restype = ctypes.c_int
        self._dll.MdLogin.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p]
        self._dll.MdLogin.restype = ctypes.c_int
        self._dll.MdSubscribe.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_int]
        self._dll.MdSubscribe.restype = ctypes.c_int
        self._dll.MdSetCallback.argtypes = [ctypes.c_void_p, MdOnTickCallback]
        self._dll.MdSetLoginCallback.argtypes = [ctypes.c_void_p, MdOnLoginCallback]
        self._dll.MdSetFrontDisconnectedCallback.argtypes = [ctypes.c_void_p, MdOnFrontDisconnectedCallback]
