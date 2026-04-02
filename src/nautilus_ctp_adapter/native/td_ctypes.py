from __future__ import annotations

import ctypes
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from .loader import add_windows_dll_directories, find_native_pack_dir


@dataclass(slots=True)
class NativeTdLoginResponseView:
    success: bool
    error_id: int
    error_message: str
    front_id: int
    session_id: int
    max_order_ref: int


class _NativeLoginResponse(ctypes.Structure):
    _fields_ = [
        ("FrontId", ctypes.c_int),
        ("SessionId", ctypes.c_int),
        ("MaxOrderRef", ctypes.c_longlong),
        ("ErrorId", ctypes.c_int),
        ("ErrorMsg", ctypes.c_void_p),
    ]


TdOnLoginCallback = ctypes.CFUNCTYPE(None, ctypes.POINTER(_NativeLoginResponse))
TdOnFrontDisconnectedCallback = ctypes.CFUNCTYPE(None, ctypes.c_int)


def _decode_ptr_text(ptr: int | None) -> str:
    if not ptr:
        return ""
    return ctypes.string_at(ptr).decode("utf-8", errors="ignore")


class CtpTdApi:
    """Repository-owned Python ctypes boundary for TD auth/login readiness smoke."""

    def __init__(self, dll: object) -> None:
        self._dll = dll
        self._bind_signatures()
        self._callback_refs: list[object] = []

    @classmethod
    def load(cls, base_dir: str | Path) -> "CtpTdApi":
        root = Path(base_dir)
        native_dir = find_native_pack_dir(root)
        if native_dir is None:
            raise FileNotFoundError(f"unable to locate native pack under {root}")
        add_windows_dll_directories(native_dir)
        dll = ctypes.CDLL(str(native_dir / "ctp_native.dll"))
        return cls(dll)

    def create(self, flow_path: str | Path) -> int:
        return int(self._dll.TdCreate(str(flow_path).encode("utf-8")))

    def dispose(self, handle: int) -> None:
        self._dll.TdDispose(ctypes.c_void_p(handle))

    def init(self, handle: int, front: str) -> int:
        return int(self._dll.TdInit(ctypes.c_void_p(handle), front.encode("utf-8")))

    def authenticate(self, handle: int, app_id: str, auth_code: str, product_info: str) -> int:
        return int(
            self._dll.TdAuthenticate(
                ctypes.c_void_p(handle),
                app_id.encode("utf-8"),
                auth_code.encode("utf-8"),
                product_info.encode("utf-8"),
            )
        )

    def login(self, handle: int, broker_id: str, user_id: str, password: str) -> int:
        return int(
            self._dll.TdLogin(
                ctypes.c_void_p(handle),
                broker_id.encode("utf-8"),
                user_id.encode("utf-8"),
                password.encode("utf-8"),
            )
        )

    def confirm_settlement(self, handle: int) -> int:
        return int(self._dll.TdConfirmSettlement(ctypes.c_void_p(handle)))

    def set_login_callback(
        self,
        handle: int,
        callback: Callable[[NativeTdLoginResponseView], None],
    ) -> object:
        def _wrapped(resp_ptr: ctypes.POINTER(_NativeLoginResponse)) -> None:
            resp = resp_ptr.contents
            callback(
                NativeTdLoginResponseView(
                    success=int(resp.ErrorId) == 0,
                    error_id=int(resp.ErrorId),
                    error_message=_decode_ptr_text(resp.ErrorMsg),
                    front_id=int(resp.FrontId),
                    session_id=int(resp.SessionId),
                    max_order_ref=int(resp.MaxOrderRef),
                )
            )

        callback_ref = TdOnLoginCallback(_wrapped)
        self._callback_refs.append(callback_ref)
        self._dll.TdSetLoginCallback(ctypes.c_void_p(handle), callback_ref)
        return callback_ref

    def set_front_disconnected_callback(self, handle: int, callback: Callable[[int], None]) -> object:
        callback_ref = TdOnFrontDisconnectedCallback(lambda reason: callback(int(reason)))
        self._callback_refs.append(callback_ref)
        self._dll.TdSetFrontDisconnectedCallback(ctypes.c_void_p(handle), callback_ref)
        return callback_ref

    def _bind_signatures(self) -> None:
        self._dll.TdCreate.argtypes = [ctypes.c_char_p]
        self._dll.TdCreate.restype = ctypes.c_void_p
        self._dll.TdDispose.argtypes = [ctypes.c_void_p]
        self._dll.TdInit.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
        self._dll.TdInit.restype = ctypes.c_int
        self._dll.TdAuthenticate.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p]
        self._dll.TdAuthenticate.restype = ctypes.c_int
        self._dll.TdLogin.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p]
        self._dll.TdLogin.restype = ctypes.c_int
        self._dll.TdConfirmSettlement.argtypes = [ctypes.c_void_p]
        self._dll.TdConfirmSettlement.restype = ctypes.c_int
        self._dll.TdSetLoginCallback.argtypes = [ctypes.c_void_p, TdOnLoginCallback]
        self._dll.TdSetFrontDisconnectedCallback.argtypes = [ctypes.c_void_p, TdOnFrontDisconnectedCallback]
