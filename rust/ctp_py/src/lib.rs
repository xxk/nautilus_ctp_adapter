//! # ctp_runtime — PyO3 bridge for the CTP adapter
//!
//! This module exposes the Rust-owned CTP runtime to Python adapters via PyO3.
//!
//! Public `CtpMdSession` / `CtpTdSession` remain the C1 scaffold contract.
//! C2 introduces an internal `CtpMdLiveSession` used by the Python data-client
//! mainline to route MD smoke through the Rust-owned runtime without breaking
//! the previously accepted scaffold API shape.

use std::ffi::{c_char, c_void, CStr, CString};
use std::sync::{Mutex, OnceLock};

use ctp_native::ffi::{
    self, NativeExec, NativeInstrument, NativeLoginResponse, NativePosition, NativeTick,
    NativeTradingAccount,
};
use encoding_rs::GB18030;
use pyo3::exceptions::{PyRuntimeError, PyValueError};
use pyo3::prelude::*;
use pyo3::types::PyAny;

/// Return code: method not yet wired to live runtime (C1 scaffold).
const SCAFFOLD_NOT_IMPLEMENTED: i32 = -9000;

/// Return code: invalid or expired session handle.
const INVALID_HANDLE: i32 = -9001;

#[pyclass(module = "ctp_runtime._ctp_runtime", name = "_NativeLoginResponseView")]
struct NativeLoginResponseViewPy {
    #[pyo3(get)]
    success: bool,
    #[pyo3(get)]
    error_id: i32,
    #[pyo3(get)]
    error_message: String,
    #[pyo3(get)]
    front_id: i32,
    #[pyo3(get)]
    session_id: i32,
    #[pyo3(get)]
    max_order_ref: i64,
}

#[pyclass(module = "ctp_runtime._ctp_runtime", name = "_NativeTickView")]
struct NativeTickViewPy {
    #[pyo3(get)]
    symbol: String,
    #[pyo3(get)]
    last: f64,
    #[pyo3(get)]
    bid: f64,
    #[pyo3(get)]
    ask: f64,
    #[pyo3(get)]
    ts_epoch_us: i64,
    #[pyo3(get)]
    bid_size: i32,
    #[pyo3(get)]
    ask_size: i32,
    #[pyo3(get)]
    volume: i32,
    #[pyo3(get)]
    open_interest: f64,
}

#[pyclass(module = "ctp_runtime._ctp_runtime", name = "_NativeInstrumentView")]
struct NativeInstrumentViewPy {
    #[pyo3(get)]
    symbol: String,
    #[pyo3(get)]
    exchange: String,
    #[pyo3(get)]
    exchange_inst_id: String,
    #[pyo3(get)]
    product_id: String,
    #[pyo3(get)]
    tick_size: f64,
    #[pyo3(get)]
    volume_multiple: i32,
    #[pyo3(get)]
    lot_size: i32,
    #[pyo3(get)]
    instrument_name: String,
    #[pyo3(get)]
    expire_date: String,
    #[pyo3(get)]
    product_class: u8,
    #[pyo3(get)]
    strike_price: f64,
    #[pyo3(get)]
    underlying_instr_id: String,
    #[pyo3(get)]
    options_type: u8,
    #[pyo3(get)]
    ts_epoch_us: i64,
    #[pyo3(get)]
    open_date: String,
    #[pyo3(get)]
    create_date: String,
}

#[pyclass(module = "ctp_runtime._ctp_runtime", name = "_NativeExecView")]
struct NativeExecViewPy {
    #[pyo3(get)]
    order_id: String,
    #[pyo3(get)]
    symbol: String,
    #[pyo3(get)]
    price: f64,
    #[pyo3(get)]
    qty: i32,
    #[pyo3(get)]
    side: i32,
    #[pyo3(get)]
    status: i32,
    #[pyo3(get)]
    ts_epoch_us: i64,
    #[pyo3(get)]
    order_ref: String,
    #[pyo3(get)]
    front_id: i32,
    #[pyo3(get)]
    session_id: i32,
    #[pyo3(get)]
    direction: i32,
    #[pyo3(get)]
    offset_flag: i32,
    #[pyo3(get)]
    hedge_flag: i32,
    #[pyo3(get)]
    is_trade: bool,
    #[pyo3(get)]
    trade_price: f64,
    #[pyo3(get)]
    trade_volume: i32,
    #[pyo3(get)]
    error_msg: String,
    #[pyo3(get)]
    leaves_qty: i32,
    #[pyo3(get)]
    callback_source: String,
    #[pyo3(get)]
    submit_request_offset_flag: i32,
    #[pyo3(get)]
    submit_request_offset_source: String,
    #[pyo3(get)]
    response_request_id: i32,
    #[pyo3(get)]
    response_is_last: bool,
    #[pyo3(get)]
    response_error_id: i32,
}

#[pyclass(module = "ctp_runtime._ctp_runtime", name = "_NativePositionView")]
struct NativePositionViewPy {
    #[pyo3(get)]
    symbol: String,
    #[pyo3(get)]
    exchange_id: String,
    #[pyo3(get)]
    broker_id: String,
    #[pyo3(get)]
    investor_id: String,
    #[pyo3(get)]
    pos_direction: i32,
    #[pyo3(get)]
    hedge_flag: i32,
    #[pyo3(get)]
    date_type: i32,
    #[pyo3(get)]
    position: i32,
    #[pyo3(get)]
    yd_position: i32,
    #[pyo3(get)]
    today_position: i32,
    #[pyo3(get)]
    position_cost: f64,
    #[pyo3(get)]
    open_cost: f64,
    #[pyo3(get)]
    exchange_margin: f64,
    #[pyo3(get)]
    use_margin: f64,
    #[pyo3(get)]
    position_profit: f64,
    #[pyo3(get)]
    ts_epoch_us: i64,
}

#[pyclass(
    module = "ctp_runtime._ctp_runtime",
    name = "_NativeTradingAccountView"
)]
struct NativeTradingAccountViewPy {
    #[pyo3(get)]
    broker_id: String,
    #[pyo3(get)]
    account_id: String,
    #[pyo3(get)]
    balance: f64,
    #[pyo3(get)]
    available: f64,
    #[pyo3(get)]
    withdraw_quota: f64,
    #[pyo3(get)]
    curr_margin: f64,
    #[pyo3(get)]
    frozen_margin: f64,
    #[pyo3(get)]
    commission: f64,
    #[pyo3(get)]
    frozen_commission: f64,
    #[pyo3(get)]
    position_profit: f64,
    #[pyo3(get)]
    close_profit: f64,
    #[pyo3(get)]
    currency_id: String,
    #[pyo3(get)]
    ts_epoch_us: i64,
}

#[derive(Default)]
struct MdLiveCallbackRegistry {
    active_handle: usize,
    login_callback: Option<Py<PyAny>>,
    tick_callback: Option<Py<PyAny>>,
    connected_callback: Option<Py<PyAny>>,
    disconnect_callback: Option<Py<PyAny>>,
}

#[derive(Default)]
struct TdLiveCallbackRegistry {
    active_handle: usize,
    login_callback: Option<Py<PyAny>>,
    disconnect_callback: Option<Py<PyAny>>,
    exec_callback: Option<Py<PyAny>>,
    instrument_callback: Option<Py<PyAny>>,
    position_callback: Option<Py<PyAny>>,
    account_callback: Option<Py<PyAny>>,
}

static MD_LIVE_CALLBACKS: OnceLock<Mutex<MdLiveCallbackRegistry>> = OnceLock::new();
static TD_LIVE_CALLBACKS: OnceLock<Mutex<TdLiveCallbackRegistry>> = OnceLock::new();

fn md_live_callbacks() -> &'static Mutex<MdLiveCallbackRegistry> {
    MD_LIVE_CALLBACKS.get_or_init(|| Mutex::new(MdLiveCallbackRegistry::default()))
}

fn td_live_callbacks() -> &'static Mutex<TdLiveCallbackRegistry> {
    TD_LIVE_CALLBACKS.get_or_init(|| Mutex::new(TdLiveCallbackRegistry::default()))
}

fn with_md_live_callbacks<T>(f: impl FnOnce(&mut MdLiveCallbackRegistry) -> T) -> T {
    let mut guard = md_live_callbacks()
        .lock()
        .expect("md live callback registry mutex poisoned");
    f(&mut guard)
}

fn with_td_live_callbacks<T>(f: impl FnOnce(&mut TdLiveCallbackRegistry) -> T) -> T {
    let mut guard = td_live_callbacks()
        .lock()
        .expect("td live callback registry mutex poisoned");
    f(&mut guard)
}

fn reset_md_live_registry_for_handle(registry: &mut MdLiveCallbackRegistry, handle: usize) {
    if registry.active_handle != 0 && registry.active_handle != handle {
        registry.login_callback = None;
        registry.tick_callback = None;
        registry.connected_callback = None;
        registry.disconnect_callback = None;
    }
    registry.active_handle = handle;
}

fn reset_td_live_registry_for_handle(registry: &mut TdLiveCallbackRegistry, handle: usize) {
    if registry.active_handle != 0 && registry.active_handle != handle {
        registry.login_callback = None;
        registry.disconnect_callback = None;
        registry.exec_callback = None;
        registry.instrument_callback = None;
        registry.position_callback = None;
        registry.account_callback = None;
    }
    registry.active_handle = handle;
}

fn clear_md_live_callbacks(handle: usize) {
    with_md_live_callbacks(|registry| {
        if registry.active_handle == handle {
            registry.active_handle = 0;
            registry.login_callback = None;
            registry.tick_callback = None;
            registry.connected_callback = None;
            registry.disconnect_callback = None;
        }
    });
}

fn clear_td_live_callbacks(handle: usize) {
    with_td_live_callbacks(|registry| {
        if registry.active_handle == handle {
            registry.active_handle = 0;
            registry.login_callback = None;
            registry.disconnect_callback = None;
            registry.exec_callback = None;
            registry.instrument_callback = None;
            registry.position_callback = None;
            registry.account_callback = None;
        }
    });
}

fn clone_login_callback() -> Option<Py<PyAny>> {
    with_md_live_callbacks(|registry| {
        registry
            .login_callback
            .as_ref()
            .map(|callback| Python::with_gil(|py| callback.clone_ref(py)))
    })
}

fn clone_tick_callback() -> Option<Py<PyAny>> {
    with_md_live_callbacks(|registry| {
        registry
            .tick_callback
            .as_ref()
            .map(|callback| Python::with_gil(|py| callback.clone_ref(py)))
    })
}

fn clone_connected_callback() -> Option<Py<PyAny>> {
    with_md_live_callbacks(|registry| {
        registry
            .connected_callback
            .as_ref()
            .map(|callback| Python::with_gil(|py| callback.clone_ref(py)))
    })
}

fn clone_disconnect_callback() -> Option<Py<PyAny>> {
    with_md_live_callbacks(|registry| {
        registry
            .disconnect_callback
            .as_ref()
            .map(|callback| Python::with_gil(|py| callback.clone_ref(py)))
    })
}

fn clone_td_login_callback() -> Option<Py<PyAny>> {
    with_td_live_callbacks(|registry| {
        registry
            .login_callback
            .as_ref()
            .map(|callback| Python::with_gil(|py| callback.clone_ref(py)))
    })
}

fn clone_td_disconnect_callback() -> Option<Py<PyAny>> {
    with_td_live_callbacks(|registry| {
        registry
            .disconnect_callback
            .as_ref()
            .map(|callback| Python::with_gil(|py| callback.clone_ref(py)))
    })
}

fn clone_td_exec_callback() -> Option<Py<PyAny>> {
    with_td_live_callbacks(|registry| {
        registry
            .exec_callback
            .as_ref()
            .map(|callback| Python::with_gil(|py| callback.clone_ref(py)))
    })
}

fn clone_td_instrument_callback() -> Option<Py<PyAny>> {
    with_td_live_callbacks(|registry| {
        registry
            .instrument_callback
            .as_ref()
            .map(|callback| Python::with_gil(|py| callback.clone_ref(py)))
    })
}

fn clone_td_position_callback() -> Option<Py<PyAny>> {
    with_td_live_callbacks(|registry| {
        registry
            .position_callback
            .as_ref()
            .map(|callback| Python::with_gil(|py| callback.clone_ref(py)))
    })
}

fn clone_td_account_callback() -> Option<Py<PyAny>> {
    with_td_live_callbacks(|registry| {
        registry
            .account_callback
            .as_ref()
            .map(|callback| Python::with_gil(|py| callback.clone_ref(py)))
    })
}

fn decode_ptr_text(ptr: *const c_char) -> String {
    if ptr.is_null() {
        return String::new();
    }
    let bytes = unsafe { CStr::from_ptr(ptr) }.to_bytes();
    if let Ok(value) = std::str::from_utf8(bytes) {
        return value.to_owned();
    }
    let (decoded, _, had_errors) = GB18030.decode(bytes);
    if !had_errors {
        return decoded.into_owned();
    }
    String::from_utf8_lossy(bytes).into_owned()
}

fn to_cstring(label: &str, value: &str) -> PyResult<CString> {
    CString::new(value)
        .map_err(|_| PyValueError::new_err(format!("{label} must not contain NUL bytes")))
}

#[cfg(test)]
mod tests {
    use super::decode_ptr_text;
    use std::ffi::CString;
    use std::ptr;

    #[test]
    fn decode_ptr_text_accepts_null_pointer() {
        assert_eq!(decode_ptr_text(ptr::null()), "");
    }

    #[test]
    fn decode_ptr_text_preserves_utf8() {
        let value = CString::new("rb2610 order accepted").expect("valid c string");

        assert_eq!(decode_ptr_text(value.as_ptr()), "rb2610 order accepted");
    }

    #[test]
    fn decode_ptr_text_falls_back_to_gb18030() {
        let value = CString::new(vec![
            0xb1, 0xa8, 0xb5, 0xa5, 0xd2, 0xd1, 0xbe, 0xdc, 0xbe, 0xf8,
        ])
        .expect("valid c string");

        assert_eq!(decode_ptr_text(value.as_ptr()), "报单已拒绝");
    }
}

extern "C" fn md_login_callback_trampoline(resp_ptr: *const NativeLoginResponse) {
    if resp_ptr.is_null() {
        return;
    }
    let callback: Option<Py<PyAny>> = clone_login_callback();
    let Some(callback) = callback else {
        return;
    };
    let response = unsafe { &*resp_ptr };
    Python::with_gil(|py| {
        let payload = NativeLoginResponseViewPy {
            success: response.ErrorId == 0,
            error_id: response.ErrorId,
            error_message: decode_ptr_text(response.ErrorMsg),
            front_id: response.FrontId,
            session_id: response.SessionId,
            max_order_ref: response.MaxOrderRef,
        };
        let payload = match Py::new(py, payload) {
            Ok(value) => value,
            Err(err) => {
                err.print(py);
                return;
            }
        };
        if let Err(err) = callback.bind(py).call1((payload,)) {
            err.print(py);
        }
    });
}

extern "C" fn md_tick_callback_trampoline(tick_ptr: *const NativeTick) {
    if tick_ptr.is_null() {
        return;
    }
    let callback: Option<Py<PyAny>> = clone_tick_callback();
    let Some(callback) = callback else {
        return;
    };
    let tick = unsafe { &*tick_ptr };
    Python::with_gil(|py| {
        let payload = NativeTickViewPy {
            symbol: decode_ptr_text(tick.symbol),
            last: tick.last,
            bid: tick.bid,
            ask: tick.ask,
            ts_epoch_us: tick.ts_epoch_us,
            bid_size: tick.bid_size,
            ask_size: tick.ask_size,
            volume: tick.volume,
            open_interest: tick.open_interest,
        };
        let payload = match Py::new(py, payload) {
            Ok(value) => value,
            Err(err) => {
                err.print(py);
                return;
            }
        };
        if let Err(err) = callback.bind(py).call1((payload,)) {
            err.print(py);
        }
    });
}

extern "C" fn md_front_connected_callback_trampoline() {
    let callback: Option<Py<PyAny>> = clone_connected_callback();
    let Some(callback) = callback else {
        return;
    };
    Python::with_gil(|py| {
        if let Err(err) = callback.bind(py).call0() {
            err.print(py);
        }
    });
}

extern "C" fn md_front_disconnected_callback_trampoline(reason: i32) {
    let callback: Option<Py<PyAny>> = clone_disconnect_callback();
    let Some(callback) = callback else {
        return;
    };
    Python::with_gil(|py| {
        if let Err(err) = callback.bind(py).call1((reason,)) {
            err.print(py);
        }
    });
}

extern "C" fn td_login_callback_trampoline(resp_ptr: *const NativeLoginResponse) {
    if resp_ptr.is_null() {
        return;
    }
    let callback: Option<Py<PyAny>> = clone_td_login_callback();
    let Some(callback) = callback else {
        return;
    };
    let response = unsafe { &*resp_ptr };
    Python::with_gil(|py| {
        let payload = NativeLoginResponseViewPy {
            success: response.ErrorId == 0,
            error_id: response.ErrorId,
            error_message: decode_ptr_text(response.ErrorMsg),
            front_id: response.FrontId,
            session_id: response.SessionId,
            max_order_ref: response.MaxOrderRef,
        };
        let payload = match Py::new(py, payload) {
            Ok(value) => value,
            Err(err) => {
                err.print(py);
                return;
            }
        };
        if let Err(err) = callback.bind(py).call1((payload,)) {
            err.print(py);
        }
    });
}

extern "C" fn td_front_disconnected_callback_trampoline(reason: i32) {
    let callback: Option<Py<PyAny>> = clone_td_disconnect_callback();
    let Some(callback) = callback else {
        return;
    };
    Python::with_gil(|py| {
        if let Err(err) = callback.bind(py).call1((reason,)) {
            err.print(py);
        }
    });
}

extern "C" fn td_exec_callback_trampoline(exec_ptr: *const NativeExec) {
    if exec_ptr.is_null() {
        return;
    }
    let callback: Option<Py<PyAny>> = clone_td_exec_callback();
    let Some(callback) = callback else {
        return;
    };
    let exec_view = unsafe { &*exec_ptr };
    Python::with_gil(|py| {
        let payload = NativeExecViewPy {
            order_id: decode_ptr_text(exec_view.order_id),
            symbol: decode_ptr_text(exec_view.symbol),
            price: exec_view.price,
            qty: exec_view.qty,
            side: exec_view.side,
            status: exec_view.status,
            ts_epoch_us: exec_view.ts_epoch_us,
            order_ref: decode_ptr_text(exec_view.order_ref),
            front_id: exec_view.front_id,
            session_id: exec_view.session_id,
            direction: exec_view.direction,
            offset_flag: exec_view.offset_flag,
            hedge_flag: exec_view.hedge_flag,
            is_trade: exec_view.is_trade != 0,
            trade_price: exec_view.trade_price,
            trade_volume: exec_view.trade_volume,
            error_msg: decode_ptr_text(exec_view.error_msg),
            leaves_qty: exec_view.leaves_qty,
            callback_source: decode_ptr_text(exec_view.callback_source),
            submit_request_offset_flag: exec_view.submit_request_offset_flag,
            submit_request_offset_source: decode_ptr_text(exec_view.submit_request_offset_source),
            response_request_id: exec_view.response_request_id,
            response_is_last: exec_view.response_is_last != 0,
            response_error_id: exec_view.response_error_id,
        };
        let payload = match Py::new(py, payload) {
            Ok(value) => value,
            Err(err) => {
                err.print(py);
                return;
            }
        };
        if let Err(err) = callback.bind(py).call1((payload,)) {
            err.print(py);
        }
    });
}

extern "C" fn td_instrument_callback_trampoline(
    inst_ptr: *const NativeInstrument,
    req_id: i32,
    is_last: i32,
) {
    if inst_ptr.is_null() {
        return;
    }
    let callback: Option<Py<PyAny>> = clone_td_instrument_callback();
    let Some(callback) = callback else {
        return;
    };
    let instrument = unsafe { &*inst_ptr };
    Python::with_gil(|py| {
        let payload = NativeInstrumentViewPy {
            symbol: decode_ptr_text(instrument.symbol),
            exchange: decode_ptr_text(instrument.exchange),
            exchange_inst_id: decode_ptr_text(instrument.exchange_inst_id),
            product_id: decode_ptr_text(instrument.product_id),
            tick_size: instrument.tick_size,
            volume_multiple: instrument.volume_multiple,
            lot_size: instrument.lot_size,
            instrument_name: decode_ptr_text(instrument.instrument_name),
            expire_date: decode_ptr_text(instrument.expire_date),
            product_class: instrument.product_class,
            strike_price: instrument.strike_price,
            underlying_instr_id: decode_ptr_text(instrument.underlying_instr_id),
            options_type: instrument.options_type,
            ts_epoch_us: instrument.ts_epoch_us,
            open_date: decode_ptr_text(instrument.open_date),
            create_date: decode_ptr_text(instrument.create_date),
        };
        let payload = match Py::new(py, payload) {
            Ok(value) => value,
            Err(err) => {
                err.print(py);
                return;
            }
        };
        if let Err(err) = callback.bind(py).call1((payload, req_id, is_last != 0)) {
            err.print(py);
        }
    });
}

extern "C" fn td_position_callback_trampoline(
    position_ptr: *const NativePosition,
    req_id: i32,
    is_last: i32,
) {
    let callback: Option<Py<PyAny>> = clone_td_position_callback();
    let Some(callback) = callback else {
        return;
    };
    Python::with_gil(|py| {
        let payload = if position_ptr.is_null() {
            None
        } else {
            let position = unsafe { &*position_ptr };
            let payload = NativePositionViewPy {
                symbol: decode_ptr_text(position.symbol),
                exchange_id: decode_ptr_text(position.exchange_id),
                broker_id: decode_ptr_text(position.broker_id),
                investor_id: decode_ptr_text(position.investor_id),
                pos_direction: position.pos_direction,
                hedge_flag: position.hedge_flag,
                date_type: position.date_type,
                position: position.position,
                yd_position: position.yd_position,
                today_position: position.today_position,
                position_cost: position.position_cost,
                open_cost: position.open_cost,
                exchange_margin: position.exchange_margin,
                use_margin: position.use_margin,
                position_profit: position.position_profit,
                ts_epoch_us: position.ts_epoch_us,
            };
            match Py::new(py, payload) {
                Ok(value) => Some(value),
                Err(err) => {
                    err.print(py);
                    return;
                }
            }
        };
        if let Err(err) = callback.bind(py).call1((payload, req_id, is_last != 0)) {
            err.print(py);
        }
    });
}

extern "C" fn td_account_callback_trampoline(account_ptr: *const NativeTradingAccount) {
    if account_ptr.is_null() {
        return;
    }
    let callback: Option<Py<PyAny>> = clone_td_account_callback();
    let Some(callback) = callback else {
        return;
    };
    let account = unsafe { &*account_ptr };
    Python::with_gil(|py| {
        let payload = NativeTradingAccountViewPy {
            broker_id: decode_ptr_text(account.broker_id),
            account_id: decode_ptr_text(account.account_id),
            balance: account.balance,
            available: account.available,
            withdraw_quota: account.withdraw_quota,
            curr_margin: account.curr_margin,
            frozen_margin: account.frozen_margin,
            commission: account.commission,
            frozen_commission: account.frozen_commission,
            position_profit: account.position_profit,
            close_profit: account.close_profit,
            currency_id: decode_ptr_text(account.currency_id),
            ts_epoch_us: account.ts_epoch_us,
        };
        let payload = match Py::new(py, payload) {
            Ok(value) => value,
            Err(err) => {
                err.print(py);
                return;
            }
        };
        if let Err(err) = callback.bind(py).call1((payload,)) {
            err.print(py);
        }
    });
}

// ──────────────────────────────────────────────
// Internal MD live session (C2 mainline)
// ──────────────────────────────────────────────

#[pyclass(
    module = "ctp_runtime._ctp_runtime",
    name = "CtpMdLiveSession",
    unsendable
)]
pub struct CtpMdLiveSession {
    flow_path: String,
    handle: usize,
    disposed: bool,
}

#[pymethods]
impl CtpMdLiveSession {
    #[new]
    fn new(flow_path: &str) -> PyResult<Self> {
        let flow_path_c = to_cstring("flow_path", flow_path)?;
        let handle = ffi::MdCreate(flow_path_c.as_ptr()) as usize;
        if handle == 0 {
            return Err(PyRuntimeError::new_err(
                "failed to create repo-owned Rust MD session handle",
            ));
        }
        Ok(Self {
            flow_path: flow_path.to_owned(),
            handle,
            disposed: false,
        })
    }

    fn set_login_callback(&mut self, py: Python<'_>, callback: Py<PyAny>) -> PyResult<()> {
        if self.disposed {
            return Err(PyRuntimeError::new_err("CtpMdLiveSession already disposed"));
        }
        if !callback.bind(py).is_callable() {
            return Err(PyValueError::new_err("login callback must be callable"));
        }
        let handle = self.handle;
        with_md_live_callbacks(|registry| {
            reset_md_live_registry_for_handle(registry, handle);
            registry.login_callback = Some(callback);
        });
        ffi::MdSetLoginCallback(self.handle_ptr(), Some(md_login_callback_trampoline));
        Ok(())
    }

    fn set_tick_callback(&mut self, py: Python<'_>, callback: Py<PyAny>) -> PyResult<()> {
        if self.disposed {
            return Err(PyRuntimeError::new_err("CtpMdLiveSession already disposed"));
        }
        if !callback.bind(py).is_callable() {
            return Err(PyValueError::new_err("tick callback must be callable"));
        }
        let handle = self.handle;
        with_md_live_callbacks(|registry| {
            reset_md_live_registry_for_handle(registry, handle);
            registry.tick_callback = Some(callback);
        });
        ffi::MdSetCallback(self.handle_ptr(), Some(md_tick_callback_trampoline));
        Ok(())
    }

    fn set_front_connected_callback(
        &mut self,
        py: Python<'_>,
        callback: Py<PyAny>,
    ) -> PyResult<()> {
        if self.disposed {
            return Err(PyRuntimeError::new_err("CtpMdLiveSession already disposed"));
        }
        if !callback.bind(py).is_callable() {
            return Err(PyValueError::new_err("connected callback must be callable"));
        }
        let handle = self.handle;
        with_md_live_callbacks(|registry| {
            reset_md_live_registry_for_handle(registry, handle);
            registry.connected_callback = Some(callback);
        });
        ffi::MdSetFrontConnectedCallback(
            self.handle_ptr(),
            Some(md_front_connected_callback_trampoline),
        );
        Ok(())
    }

    fn set_front_disconnected_callback(
        &mut self,
        py: Python<'_>,
        callback: Py<PyAny>,
    ) -> PyResult<()> {
        if self.disposed {
            return Err(PyRuntimeError::new_err("CtpMdLiveSession already disposed"));
        }
        if !callback.bind(py).is_callable() {
            return Err(PyValueError::new_err(
                "disconnect callback must be callable",
            ));
        }
        let handle = self.handle;
        with_md_live_callbacks(|registry| {
            reset_md_live_registry_for_handle(registry, handle);
            registry.disconnect_callback = Some(callback);
        });
        ffi::MdSetFrontDisconnectedCallback(
            self.handle_ptr(),
            Some(md_front_disconnected_callback_trampoline),
        );
        Ok(())
    }

    fn init(&mut self, front: &str) -> PyResult<i32> {
        if self.disposed {
            return Ok(INVALID_HANDLE);
        }
        let front_c = to_cstring("front", front)?;
        Ok(ffi::MdInit(self.handle_ptr(), front_c.as_ptr()))
    }

    #[pyo3(signature = (broker, user, password, product_info=None, interface_product_info=None, protocol_info=None, mac_address=None, client_ip_address=None, login_remark=None))]
    fn login(
        &mut self,
        broker: &str,
        user: &str,
        password: &str,
        product_info: Option<&str>,
        interface_product_info: Option<&str>,
        protocol_info: Option<&str>,
        mac_address: Option<&str>,
        client_ip_address: Option<&str>,
        login_remark: Option<&str>,
    ) -> PyResult<i32> {
        if self.disposed {
            return Ok(INVALID_HANDLE);
        }
        let broker_c = to_cstring("broker", broker)?;
        let user_c = to_cstring("user", user)?;
        let password_c = to_cstring("password", password)?;
        let product_info_c = to_cstring("product_info", product_info.unwrap_or(""))?;
        let interface_product_info_c = to_cstring(
            "interface_product_info",
            interface_product_info.unwrap_or(""),
        )?;
        let protocol_info_c = to_cstring("protocol_info", protocol_info.unwrap_or(""))?;
        let mac_address_c = to_cstring("mac_address", mac_address.unwrap_or(""))?;
        let client_ip_address_c = to_cstring("client_ip_address", client_ip_address.unwrap_or(""))?;
        let login_remark_c = to_cstring("login_remark", login_remark.unwrap_or(""))?;
        Ok(ffi::MdLoginWithCompatibility(
            self.handle_ptr(),
            broker_c.as_ptr(),
            user_c.as_ptr(),
            password_c.as_ptr(),
            product_info_c.as_ptr(),
            interface_product_info_c.as_ptr(),
            protocol_info_c.as_ptr(),
            mac_address_c.as_ptr(),
            client_ip_address_c.as_ptr(),
            login_remark_c.as_ptr(),
        ))
    }

    fn subscribe(&mut self, symbols: Vec<String>) -> PyResult<i32> {
        if self.disposed {
            return Ok(INVALID_HANDLE);
        }
        if symbols.is_empty() {
            return Ok(ffi::MdSubscribe(self.handle_ptr(), std::ptr::null_mut(), 0));
        }
        let encoded: Vec<CString> = symbols
            .iter()
            .map(|symbol| to_cstring("symbol", symbol))
            .collect::<PyResult<_>>()?;
        let mut raw: Vec<*mut c_char> = encoded
            .iter()
            .map(|symbol| symbol.as_ptr().cast_mut())
            .collect();
        Ok(ffi::MdSubscribe(
            self.handle_ptr(),
            raw.as_mut_ptr().cast::<c_void>(),
            raw.len() as i32,
        ))
    }

    fn dispose(&mut self) {
        if self.disposed {
            return;
        }
        clear_md_live_callbacks(self.handle);
        ffi::MdDispose(self.handle_ptr());
        self.handle = 0;
        self.disposed = true;
    }

    fn __repr__(&self) -> String {
        format!(
            "CtpMdLiveSession(flow_path={:?}, disposed={})",
            self.flow_path, self.disposed
        )
    }
}

impl CtpMdLiveSession {
    fn handle_ptr(&self) -> *mut c_void {
        self.handle as *mut c_void
    }
}

impl Drop for CtpMdLiveSession {
    fn drop(&mut self) {
        if self.disposed || self.handle == 0 {
            return;
        }
        clear_md_live_callbacks(self.handle);
        ffi::MdDispose(self.handle_ptr());
        self.handle = 0;
        self.disposed = true;
    }
}

// ──────────────────────────────────────────────
// Internal TD live session (C3 mainline)
// ──────────────────────────────────────────────

#[pyclass(
    module = "ctp_runtime._ctp_runtime",
    name = "CtpTdLiveSession",
    unsendable
)]
pub struct CtpTdLiveSession {
    flow_path: String,
    handle: usize,
    disposed: bool,
}

#[pymethods]
impl CtpTdLiveSession {
    #[new]
    fn new(flow_path: &str) -> PyResult<Self> {
        let flow_path_c = to_cstring("flow_path", flow_path)?;
        let handle = ffi::TdCreate(flow_path_c.as_ptr()) as usize;
        if handle == 0 {
            return Err(PyRuntimeError::new_err(
                "failed to create repo-owned Rust TD session handle",
            ));
        }
        Ok(Self {
            flow_path: flow_path.to_owned(),
            handle,
            disposed: false,
        })
    }

    fn set_login_callback(&mut self, py: Python<'_>, callback: Py<PyAny>) -> PyResult<()> {
        if self.disposed {
            return Err(PyRuntimeError::new_err("CtpTdLiveSession already disposed"));
        }
        if !callback.bind(py).is_callable() {
            return Err(PyValueError::new_err("login callback must be callable"));
        }
        let handle = self.handle;
        with_td_live_callbacks(|registry| {
            reset_td_live_registry_for_handle(registry, handle);
            registry.login_callback = Some(callback);
        });
        ffi::TdSetLoginCallback(self.handle_ptr(), Some(td_login_callback_trampoline));
        Ok(())
    }

    fn set_front_disconnected_callback(
        &mut self,
        py: Python<'_>,
        callback: Py<PyAny>,
    ) -> PyResult<()> {
        if self.disposed {
            return Err(PyRuntimeError::new_err("CtpTdLiveSession already disposed"));
        }
        if !callback.bind(py).is_callable() {
            return Err(PyValueError::new_err(
                "disconnect callback must be callable",
            ));
        }
        let handle = self.handle;
        with_td_live_callbacks(|registry| {
            reset_td_live_registry_for_handle(registry, handle);
            registry.disconnect_callback = Some(callback);
        });
        ffi::TdSetFrontDisconnectedCallback(
            self.handle_ptr(),
            Some(td_front_disconnected_callback_trampoline),
        );
        Ok(())
    }

    fn set_exec_callback(&mut self, py: Python<'_>, callback: Py<PyAny>) -> PyResult<()> {
        if self.disposed {
            return Err(PyRuntimeError::new_err("CtpTdLiveSession already disposed"));
        }
        if !callback.bind(py).is_callable() {
            return Err(PyValueError::new_err("exec callback must be callable"));
        }
        let handle = self.handle;
        with_td_live_callbacks(|registry| {
            reset_td_live_registry_for_handle(registry, handle);
            registry.exec_callback = Some(callback);
        });
        ffi::TdSetCallback(self.handle_ptr(), Some(td_exec_callback_trampoline));
        Ok(())
    }

    fn set_instrument_callback(&mut self, py: Python<'_>, callback: Py<PyAny>) -> PyResult<()> {
        if self.disposed {
            return Err(PyRuntimeError::new_err("CtpTdLiveSession already disposed"));
        }
        if !callback.bind(py).is_callable() {
            return Err(PyValueError::new_err(
                "instrument callback must be callable",
            ));
        }
        let handle = self.handle;
        with_td_live_callbacks(|registry| {
            reset_td_live_registry_for_handle(registry, handle);
            registry.instrument_callback = Some(callback);
        });
        ffi::TdSetInstrumentCallback(self.handle_ptr(), Some(td_instrument_callback_trampoline));
        Ok(())
    }

    fn set_position_callback(&mut self, py: Python<'_>, callback: Py<PyAny>) -> PyResult<()> {
        if self.disposed {
            return Err(PyRuntimeError::new_err("CtpTdLiveSession already disposed"));
        }
        if !callback.bind(py).is_callable() {
            return Err(PyValueError::new_err("position callback must be callable"));
        }
        let handle = self.handle;
        with_td_live_callbacks(|registry| {
            reset_td_live_registry_for_handle(registry, handle);
            registry.position_callback = Some(callback);
        });
        ffi::TdSetPositionCallback(self.handle_ptr(), Some(td_position_callback_trampoline));
        Ok(())
    }

    fn set_account_callback(&mut self, py: Python<'_>, callback: Py<PyAny>) -> PyResult<()> {
        if self.disposed {
            return Err(PyRuntimeError::new_err("CtpTdLiveSession already disposed"));
        }
        if !callback.bind(py).is_callable() {
            return Err(PyValueError::new_err("account callback must be callable"));
        }
        let handle = self.handle;
        with_td_live_callbacks(|registry| {
            reset_td_live_registry_for_handle(registry, handle);
            registry.account_callback = Some(callback);
        });
        ffi::TdSetAccountCallback(self.handle_ptr(), Some(td_account_callback_trampoline));
        Ok(())
    }

    fn init(&mut self, front: &str) -> PyResult<i32> {
        if self.disposed {
            return Ok(INVALID_HANDLE);
        }
        let front_c = to_cstring("front", front)?;
        Ok(ffi::TdInit(self.handle_ptr(), front_c.as_ptr()))
    }

    fn authenticate(&mut self, appid: &str, auth_code: &str, product_info: &str) -> PyResult<i32> {
        if self.disposed {
            return Ok(INVALID_HANDLE);
        }
        let appid_c = to_cstring("appid", appid)?;
        let auth_code_c = to_cstring("auth_code", auth_code)?;
        let product_info_c = to_cstring("product_info", product_info)?;
        Ok(ffi::TdAuthenticate(
            self.handle_ptr(),
            appid_c.as_ptr(),
            auth_code_c.as_ptr(),
            product_info_c.as_ptr(),
        ))
    }

    fn login(&mut self, broker: &str, user: &str, password: &str) -> PyResult<i32> {
        if self.disposed {
            return Ok(INVALID_HANDLE);
        }
        let broker_c = to_cstring("broker", broker)?;
        let user_c = to_cstring("user", user)?;
        let password_c = to_cstring("password", password)?;
        Ok(ffi::TdLogin(
            self.handle_ptr(),
            broker_c.as_ptr(),
            user_c.as_ptr(),
            password_c.as_ptr(),
        ))
    }

    fn confirm_settlement(&mut self) -> PyResult<i32> {
        if self.disposed {
            return Ok(INVALID_HANDLE);
        }
        Ok(ffi::TdConfirmSettlement(self.handle_ptr()))
    }

    fn qry_instrument(&mut self, symbol: &str) -> PyResult<i32> {
        if self.disposed {
            return Ok(INVALID_HANDLE);
        }
        let symbol_c = to_cstring("symbol", symbol)?;
        Ok(ffi::TdQryInstrument(self.handle_ptr(), symbol_c.as_ptr()))
    }

    fn qry_position(&mut self) -> PyResult<i32> {
        if self.disposed {
            return Ok(INVALID_HANDLE);
        }
        Ok(ffi::TdQryPosition(self.handle_ptr()))
    }

    fn qry_account(&mut self) -> PyResult<i32> {
        if self.disposed {
            return Ok(INVALID_HANDLE);
        }
        Ok(ffi::TdQryAccount(self.handle_ptr()))
    }

    #[allow(clippy::too_many_arguments)]
    fn order_send(
        &mut self,
        order_id: &str,
        symbol: &str,
        request_id: i32,
        price: f64,
        qty: i32,
        side: i32,
        order_type: i32,
        comb_offset: &str,
        comb_hedge: &str,
        time_condition: i32,
        volume_condition: i32,
        contingent_condition: i32,
        stop_price: f64,
        force_close_reason: i32,
        min_volume: i32,
    ) -> PyResult<i32> {
        if self.disposed {
            return Ok(INVALID_HANDLE);
        }
        let order_id_c = to_cstring("order_id", order_id)?;
        let symbol_c = to_cstring("symbol", symbol)?;
        let comb_offset_c = to_cstring("comb_offset", comb_offset)?;
        let comb_hedge_c = to_cstring("comb_hedge", comb_hedge)?;
        Ok(ffi::TdOrderSend(
            self.handle_ptr(),
            order_id_c.as_ptr(),
            symbol_c.as_ptr(),
            request_id,
            price,
            qty,
            side,
            order_type,
            comb_offset_c.as_ptr(),
            comb_hedge_c.as_ptr(),
            time_condition,
            volume_condition,
            contingent_condition,
            stop_price,
            force_close_reason,
            min_volume,
        ))
    }

    #[allow(clippy::too_many_arguments)]
    fn order_action(
        &mut self,
        broker_id: &str,
        investor_id: &str,
        instrument_id: &str,
        order_ref: &str,
        front_id: i32,
        session_id: i32,
        exchange_id: &str,
        order_sys_id: &str,
        action_flag: i32,
    ) -> PyResult<i32> {
        if self.disposed {
            return Ok(INVALID_HANDLE);
        }
        let broker_id_c = to_cstring("broker_id", broker_id)?;
        let investor_id_c = to_cstring("investor_id", investor_id)?;
        let instrument_id_c = to_cstring("instrument_id", instrument_id)?;
        let order_ref_c = to_cstring("order_ref", order_ref)?;
        let exchange_id_c = to_cstring("exchange_id", exchange_id)?;
        let order_sys_id_c = to_cstring("order_sys_id", order_sys_id)?;
        Ok(ffi::TdOrderAction(
            self.handle_ptr(),
            broker_id_c.as_ptr(),
            investor_id_c.as_ptr(),
            instrument_id_c.as_ptr(),
            order_ref_c.as_ptr(),
            front_id,
            session_id,
            exchange_id_c.as_ptr(),
            order_sys_id_c.as_ptr(),
            action_flag,
        ))
    }

    fn dispose(&mut self) {
        if self.disposed {
            return;
        }
        clear_td_live_callbacks(self.handle);
        ffi::TdDispose(self.handle_ptr());
        self.handle = 0;
        self.disposed = true;
    }

    fn __repr__(&self) -> String {
        format!(
            "CtpTdLiveSession(flow_path={:?}, disposed={})",
            self.flow_path, self.disposed
        )
    }
}

impl CtpTdLiveSession {
    fn handle_ptr(&self) -> *mut c_void {
        self.handle as *mut c_void
    }
}

impl Drop for CtpTdLiveSession {
    fn drop(&mut self) {
        if self.disposed || self.handle == 0 {
            return;
        }
        clear_td_live_callbacks(self.handle);
        ffi::TdDispose(self.handle_ptr());
        self.handle = 0;
        self.disposed = true;
    }
}

// ──────────────────────────────────────────────
// MD session
// ──────────────────────────────────────────────

/// Market-data session lifecycle bridge.
///
/// In C1 all methods return `SCAFFOLD_NOT_IMPLEMENTED`.
/// Real CTP connectivity is wired in C2.
#[pyclass]
pub struct CtpMdSession {
    front: String,
    broker: String,
    user: String,
    password: String,
    disposed: bool,
}

#[pymethods]
impl CtpMdSession {
    /// Create a new MD session handle (scaffold).
    #[new]
    fn new(front: &str, broker: &str, user: &str, password: &str) -> Self {
        CtpMdSession {
            front: front.to_owned(),
            broker: broker.to_owned(),
            user: user.to_owned(),
            password: password.to_owned(),
            disposed: false,
        }
    }

    /// Initialise the MD API and connect to the front server.
    /// Returns 0 on success, negative error code on failure.
    fn init(&mut self) -> i32 {
        if self.disposed {
            return INVALID_HANDLE;
        }
        SCAFFOLD_NOT_IMPLEMENTED
    }

    /// Send a login request.
    fn login(&mut self) -> i32 {
        if self.disposed {
            return INVALID_HANDLE;
        }
        SCAFFOLD_NOT_IMPLEMENTED
    }

    /// Subscribe to market-data for the given symbol list.
    fn subscribe(&mut self, _symbols: Vec<String>) -> i32 {
        if self.disposed {
            return INVALID_HANDLE;
        }
        SCAFFOLD_NOT_IMPLEMENTED
    }

    /// Release the native handle.
    fn dispose(&mut self) {
        self.disposed = true;
    }

    fn __repr__(&self) -> String {
        format!(
            "CtpMdSession(front={:?}, broker={:?}, user={:?}, disposed={})",
            self.front, self.broker, self.user, self.disposed
        )
    }
}

// ──────────────────────────────────────────────
// TD session
// ──────────────────────────────────────────────

/// Trading-desk session lifecycle bridge.
///
/// In C1 all methods return `SCAFFOLD_NOT_IMPLEMENTED`.
/// Real CTP connectivity is wired in C3.
#[pyclass]
pub struct CtpTdSession {
    front: String,
    broker: String,
    user: String,
    password: String,
    appid: String,
    auth_code: String,
    disposed: bool,
}

#[pymethods]
impl CtpTdSession {
    /// Create a new TD session handle (scaffold).
    #[new]
    fn new(
        front: &str,
        broker: &str,
        user: &str,
        password: &str,
        appid: &str,
        auth_code: &str,
    ) -> Self {
        CtpTdSession {
            front: front.to_owned(),
            broker: broker.to_owned(),
            user: user.to_owned(),
            password: password.to_owned(),
            appid: appid.to_owned(),
            auth_code: auth_code.to_owned(),
            disposed: false,
        }
    }

    /// Initialise the TD API and connect to the front server.
    fn init(&mut self) -> i32 {
        if self.disposed {
            return INVALID_HANDLE;
        }
        SCAFFOLD_NOT_IMPLEMENTED
    }

    /// Send an authenticate request (appid + auth_code).
    fn authenticate(&mut self) -> i32 {
        if self.disposed {
            return INVALID_HANDLE;
        }
        SCAFFOLD_NOT_IMPLEMENTED
    }

    /// Send a login request.
    fn login(&mut self) -> i32 {
        if self.disposed {
            return INVALID_HANDLE;
        }
        SCAFFOLD_NOT_IMPLEMENTED
    }

    /// Query instrument catalogue.
    fn query_instruments(&mut self) -> i32 {
        if self.disposed {
            return INVALID_HANDLE;
        }
        SCAFFOLD_NOT_IMPLEMENTED
    }

    /// Query trading account.
    fn query_account(&mut self) -> i32 {
        if self.disposed {
            return INVALID_HANDLE;
        }
        SCAFFOLD_NOT_IMPLEMENTED
    }

    /// Query open positions.
    fn query_positions(&mut self) -> i32 {
        if self.disposed {
            return INVALID_HANDLE;
        }
        SCAFFOLD_NOT_IMPLEMENTED
    }

    /// Release the native handle.
    fn dispose(&mut self) {
        self.disposed = true;
    }

    fn __repr__(&self) -> String {
        format!(
            "CtpTdSession(front={:?}, broker={:?}, user={:?}, disposed={})",
            self.front, self.broker, self.user, self.disposed
        )
    }
}

// ──────────────────────────────────────────────
// Module registration
// ──────────────────────────────────────────────

#[pymodule]
fn _ctp_runtime(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<CtpMdLiveSession>()?;
    m.add_class::<CtpTdLiveSession>()?;
    m.add_class::<CtpMdSession>()?;
    m.add_class::<CtpTdSession>()?;
    m.add_class::<NativeLoginResponseViewPy>()?;
    m.add_class::<NativeTickViewPy>()?;
    m.add_class::<NativeInstrumentViewPy>()?;
    m.add_class::<NativeExecViewPy>()?;
    m.add_class::<NativePositionViewPy>()?;
    m.add_class::<NativeTradingAccountViewPy>()?;
    m.add("SCAFFOLD_NOT_IMPLEMENTED", SCAFFOLD_NOT_IMPLEMENTED)?;
    m.add("INVALID_HANDLE", INVALID_HANDLE)?;
    Ok(())
}
