from __future__ import annotations

import ctypes
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from .loader import add_windows_dll_directories, find_native_pack_dir, find_repo_owned_native_dll
from .text import decode_ctp_text_ptr


@dataclass(slots=True)
class NativeTdLoginResponseView:
    success: bool
    error_id: int
    error_message: str
    front_id: int
    session_id: int
    max_order_ref: int


@dataclass(slots=True)
class NativeInstrumentView:
    symbol: str
    exchange: str
    exchange_inst_id: str
    product_id: str
    tick_size: float
    volume_multiple: int
    lot_size: int
    instrument_name: str
    expire_date: str
    product_class: int
    strike_price: float
    underlying_instr_id: str
    options_type: int
    ts_epoch_us: int
    open_date: str
    create_date: str


@dataclass(slots=True)
class NativeExecView:
    order_id: str
    symbol: str
    price: float
    qty: int
    side: int
    status: int
    ts_epoch_us: int
    order_ref: str
    front_id: int
    session_id: int
    direction: int
    offset_flag: int
    hedge_flag: int
    is_trade: bool
    trade_price: float
    trade_volume: int
    error_msg: str
    leaves_qty: int
    callback_source: str = ""
    submit_request_offset_flag: int = -1
    submit_request_offset_source: str = ""
    response_request_id: int = -1
    response_is_last: bool = False
    response_error_id: int = 0


@dataclass(slots=True)
class NativePositionView:
    symbol: str
    broker_id: str
    investor_id: str
    pos_direction: int
    hedge_flag: int
    date_type: int
    position: int
    yd_position: int
    today_position: int
    position_cost: float
    open_cost: float
    exchange_margin: float
    use_margin: float
    position_profit: float
    ts_epoch_us: int
    exchange_id: str = ""


@dataclass(slots=True)
class NativeTradingAccountView:
    broker_id: str
    account_id: str
    balance: float
    available: float
    withdraw_quota: float
    curr_margin: float
    frozen_margin: float
    commission: float
    frozen_commission: float
    position_profit: float
    close_profit: float
    currency_id: str
    ts_epoch_us: int


class _NativeLoginResponse(ctypes.Structure):
    _fields_ = [
        ("FrontId", ctypes.c_int),
        ("SessionId", ctypes.c_int),
        ("MaxOrderRef", ctypes.c_longlong),
        ("ErrorId", ctypes.c_int),
        ("ErrorMsg", ctypes.c_void_p),
    ]


class _NativeInstrument(ctypes.Structure):
    _fields_ = [
        ("symbol", ctypes.c_void_p),
        ("exchange", ctypes.c_void_p),
        ("exchange_inst_id", ctypes.c_void_p),
        ("product_id", ctypes.c_void_p),
        ("tick_size", ctypes.c_double),
        ("volume_multiple", ctypes.c_int),
        ("lot_size", ctypes.c_int),
        ("instrument_name", ctypes.c_void_p),
        ("expire_date", ctypes.c_void_p),
        ("product_class", ctypes.c_ubyte),
        ("strike_price", ctypes.c_double),
        ("underlying_instr_id", ctypes.c_void_p),
        ("options_type", ctypes.c_ubyte),
        ("ts_epoch_us", ctypes.c_longlong),
        ("open_date", ctypes.c_void_p),
        ("create_date", ctypes.c_void_p),
    ]


class _NativeExec(ctypes.Structure):
    _fields_ = [
        ("order_id", ctypes.c_void_p),
        ("symbol", ctypes.c_void_p),
        ("price", ctypes.c_double),
        ("qty", ctypes.c_int),
        ("side", ctypes.c_int),
        ("status", ctypes.c_int),
        ("ts_epoch_us", ctypes.c_longlong),
        ("order_ref", ctypes.c_void_p),
        ("front_id", ctypes.c_int),
        ("session_id", ctypes.c_int),
        ("direction", ctypes.c_int),
        ("offset_flag", ctypes.c_int),
        ("hedge_flag", ctypes.c_int),
        ("is_trade", ctypes.c_int),
        ("trade_price", ctypes.c_double),
        ("trade_volume", ctypes.c_int),
        ("error_msg", ctypes.c_void_p),
        ("leaves_qty", ctypes.c_int),
        ("callback_source", ctypes.c_void_p),
        ("submit_request_offset_flag", ctypes.c_int),
        ("submit_request_offset_source", ctypes.c_void_p),
        ("response_request_id", ctypes.c_int),
        ("response_is_last", ctypes.c_int),
        ("response_error_id", ctypes.c_int),
    ]


class _NativePosition(ctypes.Structure):
    _fields_ = [
        ("symbol", ctypes.c_void_p),
        ("exchange_id", ctypes.c_void_p),
        ("broker_id", ctypes.c_void_p),
        ("investor_id", ctypes.c_void_p),
        ("pos_direction", ctypes.c_int),
        ("hedge_flag", ctypes.c_int),
        ("date_type", ctypes.c_int),
        ("position", ctypes.c_int),
        ("yd_position", ctypes.c_int),
        ("today_position", ctypes.c_int),
        ("position_cost", ctypes.c_double),
        ("open_cost", ctypes.c_double),
        ("exchange_margin", ctypes.c_double),
        ("use_margin", ctypes.c_double),
        ("position_profit", ctypes.c_double),
        ("ts_epoch_us", ctypes.c_longlong),
    ]


class _NativeTradingAccount(ctypes.Structure):
    _fields_ = [
        ("broker_id", ctypes.c_void_p),
        ("account_id", ctypes.c_void_p),
        ("balance", ctypes.c_double),
        ("available", ctypes.c_double),
        ("withdraw_quota", ctypes.c_double),
        ("curr_margin", ctypes.c_double),
        ("frozen_margin", ctypes.c_double),
        ("commission", ctypes.c_double),
        ("frozen_commission", ctypes.c_double),
        ("position_profit", ctypes.c_double),
        ("close_profit", ctypes.c_double),
        ("currency_id", ctypes.c_void_p),
        ("ts_epoch_us", ctypes.c_longlong),
    ]


TdOnLoginCallback = ctypes.CFUNCTYPE(None, ctypes.POINTER(_NativeLoginResponse))
TdOnFrontDisconnectedCallback = ctypes.CFUNCTYPE(None, ctypes.c_int)
TdOnExecCallback = ctypes.CFUNCTYPE(None, ctypes.POINTER(_NativeExec))
TdOnInstrumentCallback = ctypes.CFUNCTYPE(None, ctypes.POINTER(_NativeInstrument), ctypes.c_int, ctypes.c_int)
TdOnPositionCallback = ctypes.CFUNCTYPE(None, ctypes.POINTER(_NativePosition))
TdOnAccountCallback = ctypes.CFUNCTYPE(None, ctypes.POINTER(_NativeTradingAccount))


def _decode_ptr_text(ptr: int | None) -> str:
    return decode_ctp_text_ptr(ptr)


class CtpTdApi:
    """Repository-owned Python ctypes boundary for TD auth/login readiness smoke."""

    def __init__(self, dll: object) -> None:
        self._dll = dll
        self._bind_signatures()
        self._callback_refs: list[object] = []

    @classmethod
    def load(cls, base_dir: str | Path) -> "CtpTdApi":
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

    def order_send(
        self,
        handle: int,
        *,
        order_id: str,
        symbol: str,
        request_id: int,
        price: float,
        qty: int,
        side: int,
        order_type: int,
        comb_offset: str,
        comb_hedge: str,
        time_condition: int,
        volume_condition: int,
        contingent_condition: int,
        stop_price: float,
        force_close_reason: int,
        min_volume: int,
    ) -> int:
        return int(
            self._dll.TdOrderSend(
                ctypes.c_void_p(handle),
                order_id.encode("utf-8"),
                symbol.encode("utf-8"),
                ctypes.c_int(request_id),
                ctypes.c_double(price),
                ctypes.c_int(qty),
                ctypes.c_int(side),
                ctypes.c_int(order_type),
                comb_offset.encode("utf-8"),
                comb_hedge.encode("utf-8"),
                ctypes.c_int(time_condition),
                ctypes.c_int(volume_condition),
                ctypes.c_int(contingent_condition),
                ctypes.c_double(stop_price),
                ctypes.c_int(force_close_reason),
                ctypes.c_int(min_volume),
            )
        )

    def order_action(
        self,
        handle: int,
        *,
        broker_id: str,
        investor_id: str,
        instrument_id: str,
        order_ref: str,
        front_id: int,
        session_id: int,
        exchange_id: str,
        order_sys_id: str,
        action_flag: int,
    ) -> int:
        return int(
            self._dll.TdOrderAction(
                ctypes.c_void_p(handle),
                broker_id.encode("utf-8"),
                investor_id.encode("utf-8"),
                instrument_id.encode("utf-8"),
                order_ref.encode("utf-8"),
                ctypes.c_int(front_id),
                ctypes.c_int(session_id),
                exchange_id.encode("utf-8"),
                order_sys_id.encode("utf-8"),
                ctypes.c_int(action_flag),
            )
        )

    def qry_instrument(self, handle: int, symbol: str) -> int:
        return int(self._dll.TdQryInstrument(ctypes.c_void_p(handle), symbol.encode("utf-8")))

    def qry_position(self, handle: int) -> int:
        return int(self._dll.TdQryPosition(ctypes.c_void_p(handle)))

    def qry_account(self, handle: int) -> int:
        return int(self._dll.TdQryAccount(ctypes.c_void_p(handle)))

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

    def set_instrument_callback(
        self,
        handle: int,
        callback: Callable[[NativeInstrumentView, int, bool], None],
    ) -> object:
        def _wrapped(inst_ptr: ctypes.POINTER(_NativeInstrument), req_id: int, is_last: int) -> None:
            inst = inst_ptr.contents
            callback(
                NativeInstrumentView(
                    symbol=_decode_ptr_text(inst.symbol),
                    exchange=_decode_ptr_text(inst.exchange),
                    exchange_inst_id=_decode_ptr_text(inst.exchange_inst_id),
                    product_id=_decode_ptr_text(inst.product_id),
                    tick_size=float(inst.tick_size),
                    volume_multiple=int(inst.volume_multiple),
                    lot_size=int(inst.lot_size),
                    instrument_name=_decode_ptr_text(inst.instrument_name),
                    expire_date=_decode_ptr_text(inst.expire_date),
                    product_class=int(inst.product_class),
                    strike_price=float(inst.strike_price),
                    underlying_instr_id=_decode_ptr_text(inst.underlying_instr_id),
                    options_type=int(inst.options_type),
                    ts_epoch_us=int(inst.ts_epoch_us),
                    open_date=_decode_ptr_text(inst.open_date),
                    create_date=_decode_ptr_text(inst.create_date),
                ),
                int(req_id),
                bool(is_last),
            )

        callback_ref = TdOnInstrumentCallback(_wrapped)
        self._callback_refs.append(callback_ref)
        self._dll.TdSetInstrumentCallback(ctypes.c_void_p(handle), callback_ref)
        return callback_ref

    def set_exec_callback(
        self,
        handle: int,
        callback: Callable[[NativeExecView], None],
    ) -> object:
        def _wrapped(exec_ptr: ctypes.POINTER(_NativeExec)) -> None:
            exec_view = exec_ptr.contents
            callback(
                NativeExecView(
                    order_id=_decode_ptr_text(exec_view.order_id),
                    symbol=_decode_ptr_text(exec_view.symbol),
                    price=float(exec_view.price),
                    qty=int(exec_view.qty),
                    side=int(exec_view.side),
                    status=int(exec_view.status),
                    ts_epoch_us=int(exec_view.ts_epoch_us),
                    order_ref=_decode_ptr_text(exec_view.order_ref),
                    front_id=int(exec_view.front_id),
                    session_id=int(exec_view.session_id),
                    direction=int(exec_view.direction),
                    offset_flag=int(exec_view.offset_flag),
                    hedge_flag=int(exec_view.hedge_flag),
                    is_trade=bool(exec_view.is_trade),
                    trade_price=float(exec_view.trade_price),
                    trade_volume=int(exec_view.trade_volume),
                    error_msg=_decode_ptr_text(exec_view.error_msg),
                    leaves_qty=int(exec_view.leaves_qty),
                    callback_source=_decode_ptr_text(exec_view.callback_source),
                    submit_request_offset_flag=int(exec_view.submit_request_offset_flag),
                    submit_request_offset_source=_decode_ptr_text(
                        exec_view.submit_request_offset_source
                    ),
                    response_request_id=int(exec_view.response_request_id),
                    response_is_last=bool(exec_view.response_is_last),
                    response_error_id=int(exec_view.response_error_id),
                )
            )

        callback_ref = TdOnExecCallback(_wrapped)
        self._callback_refs.append(callback_ref)
        self._dll.TdSetCallback(ctypes.c_void_p(handle), callback_ref)
        return callback_ref

    def set_position_callback(
        self,
        handle: int,
        callback: Callable[[NativePositionView], None],
    ) -> object:
        def _wrapped(pos_ptr: ctypes.POINTER(_NativePosition)) -> None:
            pos = pos_ptr.contents
            callback(
                NativePositionView(
                    symbol=_decode_ptr_text(pos.symbol),
                    exchange_id=_decode_ptr_text(pos.exchange_id),
                    broker_id=_decode_ptr_text(pos.broker_id),
                    investor_id=_decode_ptr_text(pos.investor_id),
                    pos_direction=int(pos.pos_direction),
                    hedge_flag=int(pos.hedge_flag),
                    date_type=int(pos.date_type),
                    position=int(pos.position),
                    yd_position=int(pos.yd_position),
                    today_position=int(pos.today_position),
                    position_cost=float(pos.position_cost),
                    open_cost=float(pos.open_cost),
                    exchange_margin=float(pos.exchange_margin),
                    use_margin=float(pos.use_margin),
                    position_profit=float(pos.position_profit),
                    ts_epoch_us=int(pos.ts_epoch_us),
                )
            )

        callback_ref = TdOnPositionCallback(_wrapped)
        self._callback_refs.append(callback_ref)
        self._dll.TdSetPositionCallback(ctypes.c_void_p(handle), callback_ref)
        return callback_ref

    def set_account_callback(
        self,
        handle: int,
        callback: Callable[[NativeTradingAccountView], None],
    ) -> object:
        def _wrapped(account_ptr: ctypes.POINTER(_NativeTradingAccount)) -> None:
            account = account_ptr.contents
            callback(
                NativeTradingAccountView(
                    broker_id=_decode_ptr_text(account.broker_id),
                    account_id=_decode_ptr_text(account.account_id),
                    balance=float(account.balance),
                    available=float(account.available),
                    withdraw_quota=float(account.withdraw_quota),
                    curr_margin=float(account.curr_margin),
                    frozen_margin=float(account.frozen_margin),
                    commission=float(account.commission),
                    frozen_commission=float(account.frozen_commission),
                    position_profit=float(account.position_profit),
                    close_profit=float(account.close_profit),
                    currency_id=_decode_ptr_text(account.currency_id),
                    ts_epoch_us=int(account.ts_epoch_us),
                )
            )

        callback_ref = TdOnAccountCallback(_wrapped)
        self._callback_refs.append(callback_ref)
        self._dll.TdSetAccountCallback(ctypes.c_void_p(handle), callback_ref)
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
        self._dll.TdOrderSend.argtypes = [
            ctypes.c_void_p,
            ctypes.c_char_p,
            ctypes.c_char_p,
            ctypes.c_int,
            ctypes.c_double,
            ctypes.c_int,
            ctypes.c_int,
            ctypes.c_int,
            ctypes.c_char_p,
            ctypes.c_char_p,
            ctypes.c_int,
            ctypes.c_int,
            ctypes.c_int,
            ctypes.c_double,
            ctypes.c_int,
            ctypes.c_int,
        ]
        self._dll.TdOrderSend.restype = ctypes.c_int
        self._dll.TdOrderAction.argtypes = [
            ctypes.c_void_p,
            ctypes.c_char_p,
            ctypes.c_char_p,
            ctypes.c_char_p,
            ctypes.c_char_p,
            ctypes.c_int,
            ctypes.c_int,
            ctypes.c_char_p,
            ctypes.c_char_p,
            ctypes.c_int,
        ]
        self._dll.TdOrderAction.restype = ctypes.c_int
        self._dll.TdQryInstrument.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
        self._dll.TdQryInstrument.restype = ctypes.c_int
        self._dll.TdQryPosition.argtypes = [ctypes.c_void_p]
        self._dll.TdQryPosition.restype = ctypes.c_int
        self._dll.TdQryAccount.argtypes = [ctypes.c_void_p]
        self._dll.TdQryAccount.restype = ctypes.c_int
        self._dll.TdSetCallback.argtypes = [ctypes.c_void_p, TdOnExecCallback]
        self._dll.TdSetLoginCallback.argtypes = [ctypes.c_void_p, TdOnLoginCallback]
        self._dll.TdSetFrontDisconnectedCallback.argtypes = [ctypes.c_void_p, TdOnFrontDisconnectedCallback]
        self._dll.TdSetInstrumentCallback.argtypes = [ctypes.c_void_p, TdOnInstrumentCallback]
        self._dll.TdSetPositionCallback.argtypes = [ctypes.c_void_p, TdOnPositionCallback]
        self._dll.TdSetAccountCallback.argtypes = [ctypes.c_void_p, TdOnAccountCallback]
