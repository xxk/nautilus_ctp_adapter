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

use ctp_native::ffi::{self, NativeLoginResponse, NativeTick};
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

#[derive(Default)]
struct MdLiveCallbackRegistry {
    active_handle: usize,
    login_callback: Option<Py<PyAny>>,
    tick_callback: Option<Py<PyAny>>,
    disconnect_callback: Option<Py<PyAny>>,
}

static MD_LIVE_CALLBACKS: OnceLock<Mutex<MdLiveCallbackRegistry>> = OnceLock::new();

fn md_live_callbacks() -> &'static Mutex<MdLiveCallbackRegistry> {
    MD_LIVE_CALLBACKS.get_or_init(|| Mutex::new(MdLiveCallbackRegistry::default()))
}

fn with_md_live_callbacks<T>(f: impl FnOnce(&mut MdLiveCallbackRegistry) -> T) -> T {
    let mut guard = md_live_callbacks()
        .lock()
        .expect("md live callback registry mutex poisoned");
    f(&mut guard)
}

fn reset_md_live_registry_for_handle(registry: &mut MdLiveCallbackRegistry, handle: usize) {
    if registry.active_handle != 0 && registry.active_handle != handle {
        registry.login_callback = None;
        registry.tick_callback = None;
        registry.disconnect_callback = None;
    }
    registry.active_handle = handle;
}

fn clear_md_live_callbacks(handle: usize) {
    with_md_live_callbacks(|registry| {
        if registry.active_handle == handle {
            registry.active_handle = 0;
            registry.login_callback = None;
            registry.tick_callback = None;
            registry.disconnect_callback = None;
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

fn clone_disconnect_callback() -> Option<Py<PyAny>> {
    with_md_live_callbacks(|registry| {
        registry
            .disconnect_callback
            .as_ref()
            .map(|callback| Python::with_gil(|py| callback.clone_ref(py)))
    })
}

fn decode_ptr_text(ptr: *const c_char) -> String {
    if ptr.is_null() {
        return String::new();
    }
    unsafe { CStr::from_ptr(ptr) }
        .to_string_lossy()
        .into_owned()
}

fn to_cstring(label: &str, value: &str) -> PyResult<CString> {
    CString::new(value).map_err(|_| PyValueError::new_err(format!("{label} must not contain NUL bytes")))
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

// ──────────────────────────────────────────────
// Internal MD live session (C2 mainline)
// ──────────────────────────────────────────────

#[pyclass(module = "ctp_runtime._ctp_runtime", name = "CtpMdLiveSession", unsendable)]
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

    fn set_front_disconnected_callback(
        &mut self,
        py: Python<'_>,
        callback: Py<PyAny>,
    ) -> PyResult<()> {
        if self.disposed {
            return Err(PyRuntimeError::new_err("CtpMdLiveSession already disposed"));
        }
        if !callback.bind(py).is_callable() {
            return Err(PyValueError::new_err("disconnect callback must be callable"));
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

    fn login(&mut self, broker: &str, user: &str, password: &str) -> PyResult<i32> {
        if self.disposed {
            return Ok(INVALID_HANDLE);
        }
        let broker_c = to_cstring("broker", broker)?;
        let user_c = to_cstring("user", user)?;
        let password_c = to_cstring("password", password)?;
        Ok(ffi::MdLogin(
            self.handle_ptr(),
            broker_c.as_ptr(),
            user_c.as_ptr(),
            password_c.as_ptr(),
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
    m.add_class::<CtpMdSession>()?;
    m.add_class::<CtpTdSession>()?;
    m.add_class::<NativeLoginResponseViewPy>()?;
    m.add_class::<NativeTickViewPy>()?;
    m.add("SCAFFOLD_NOT_IMPLEMENTED", SCAFFOLD_NOT_IMPLEMENTED)?;
    m.add("INVALID_HANDLE", INVALID_HANDLE)?;
    Ok(())
}
