#![allow(non_snake_case)]

use std::ffi::{c_char, c_void};
#[cfg(not(ctp_vendor_bridge))]
use std::ffi::CStr;

const NOT_IMPLEMENTED_CODE: i32 = -9000;
const INVALID_HANDLE_CODE: i32 = -9001;
#[cfg(not(ctp_vendor_bridge))]
const SCAFFOLD_ERROR_MSG: &[u8] =
    b"repo-owned ctp_native scaffold only; live vendor bridge not implemented\0";

#[repr(C)]
pub struct NativeLoginResponse {
    pub FrontId: i32,
    pub SessionId: i32,
    pub MaxOrderRef: i64,
    pub ErrorId: i32,
    pub ErrorMsg: *const c_char,
}

#[repr(C)]
pub struct NativeTick {
    pub symbol: *const c_char,
    pub last: f64,
    pub bid: f64,
    pub ask: f64,
    pub ts_epoch_us: i64,
    pub bid_size: i32,
    pub ask_size: i32,
    pub volume: i32,
    pub open_interest: f64,
}

#[repr(C)]
pub struct NativeInstrument {
    pub symbol: *const c_char,
    pub exchange: *const c_char,
    pub exchange_inst_id: *const c_char,
    pub product_id: *const c_char,
    pub tick_size: f64,
    pub volume_multiple: i32,
    pub lot_size: i32,
    pub instrument_name: *const c_char,
    pub expire_date: *const c_char,
    pub product_class: u8,
    pub strike_price: f64,
    pub underlying_instr_id: *const c_char,
    pub options_type: u8,
    pub ts_epoch_us: i64,
    pub open_date: *const c_char,
    pub create_date: *const c_char,
}

#[repr(C)]
pub struct NativeExec {
    pub order_id: *const c_char,
    pub symbol: *const c_char,
    pub price: f64,
    pub qty: i32,
    pub side: i32,
    pub status: i32,
    pub ts_epoch_us: i64,
    pub order_ref: *const c_char,
    pub front_id: i32,
    pub session_id: i32,
    pub direction: i32,
    pub offset_flag: i32,
    pub hedge_flag: i32,
    pub is_trade: i32,
    pub trade_price: f64,
    pub trade_volume: i32,
    pub error_msg: *const c_char,
    pub leaves_qty: i32,
}

#[repr(C)]
pub struct NativePosition {
    pub symbol: *const c_char,
    pub broker_id: *const c_char,
    pub investor_id: *const c_char,
    pub pos_direction: i32,
    pub hedge_flag: i32,
    pub date_type: i32,
    pub position: i32,
    pub yd_position: i32,
    pub today_position: i32,
    pub position_cost: f64,
    pub open_cost: f64,
    pub exchange_margin: f64,
    pub use_margin: f64,
    pub position_profit: f64,
    pub ts_epoch_us: i64,
}

#[repr(C)]
pub struct NativeTradingAccount {
    pub broker_id: *const c_char,
    pub account_id: *const c_char,
    pub balance: f64,
    pub available: f64,
    pub withdraw_quota: f64,
    pub curr_margin: f64,
    pub frozen_margin: f64,
    pub commission: f64,
    pub frozen_commission: f64,
    pub position_profit: f64,
    pub close_profit: f64,
    pub currency_id: *const c_char,
    pub ts_epoch_us: i64,
}

type MdOnLoginCallback = Option<extern "C" fn(*const NativeLoginResponse)>;
type MdOnFrontDisconnectedCallback = Option<extern "C" fn(i32)>;
type MdOnTickCallback = Option<extern "C" fn(*const NativeTick)>;

type TdOnLoginCallback = Option<extern "C" fn(*const NativeLoginResponse)>;
type TdOnFrontDisconnectedCallback = Option<extern "C" fn(i32)>;
type TdOnExecCallback = Option<extern "C" fn(*const NativeExec)>;
type TdOnInstrumentCallback = Option<extern "C" fn(*const NativeInstrument, i32, i32)>;
type TdOnPositionCallback = Option<extern "C" fn(*const NativePosition, i32, i32)>;
type TdOnAccountCallback = Option<extern "C" fn(*const NativeTradingAccount)>;

#[cfg(not(ctp_vendor_bridge))]
#[derive(Default)]
struct MdSessionHandle {
    _flow_path: Option<String>,
    _front: Option<String>,
    login_callback: MdOnLoginCallback,
    tick_callback: MdOnTickCallback,
    front_disconnected_callback: MdOnFrontDisconnectedCallback,
}

#[cfg(not(ctp_vendor_bridge))]
#[derive(Default)]
struct TdSessionHandle {
    _flow_path: Option<String>,
    _front: Option<String>,
    login_callback: TdOnLoginCallback,
    exec_callback: TdOnExecCallback,
    front_disconnected_callback: TdOnFrontDisconnectedCallback,
    instrument_callback: TdOnInstrumentCallback,
    position_callback: TdOnPositionCallback,
    account_callback: TdOnAccountCallback,
}

#[cfg(not(ctp_vendor_bridge))]
fn decode_text(ptr: *const c_char) -> Option<String> {
    if ptr.is_null() {
        return None;
    }
    let value = unsafe { CStr::from_ptr(ptr) };
    Some(value.to_string_lossy().into_owned())
}

#[cfg(not(ctp_vendor_bridge))]
fn scaffold_error_message() -> *const c_char {
    SCAFFOLD_ERROR_MSG.as_ptr().cast()
}

#[cfg(not(ctp_vendor_bridge))]
fn scaffold_login_response() -> NativeLoginResponse {
    NativeLoginResponse {
        FrontId: 0,
        SessionId: 0,
        MaxOrderRef: 0,
        ErrorId: NOT_IMPLEMENTED_CODE,
        ErrorMsg: scaffold_error_message(),
    }
}

#[cfg(ctp_vendor_bridge)]
extern "C" {
    fn repo_ctp_md_create(flow_path: *const c_char) -> *mut c_void;
    fn repo_ctp_md_dispose(handle: *mut c_void);
    fn repo_ctp_md_init(handle: *mut c_void, front: *const c_char) -> i32;
    fn repo_ctp_md_login(
        handle: *mut c_void,
        broker_id: *const c_char,
        user_id: *const c_char,
        password: *const c_char,
    ) -> i32;
    fn repo_ctp_md_subscribe(handle: *mut c_void, symbols: *mut c_void, symbol_count: i32) -> i32;
    fn repo_ctp_md_unsubscribe(handle: *mut c_void, symbols: *mut c_void, symbol_count: i32) -> i32;
    fn repo_ctp_md_set_callback(handle: *mut c_void, callback: MdOnTickCallback);
    fn repo_ctp_md_set_login_callback(handle: *mut c_void, callback: MdOnLoginCallback);
    fn repo_ctp_md_set_front_disconnected_callback(
        handle: *mut c_void,
        callback: MdOnFrontDisconnectedCallback,
    );

    fn repo_ctp_td_create(flow_path: *const c_char) -> *mut c_void;
    fn repo_ctp_td_dispose(handle: *mut c_void);
    fn repo_ctp_td_init(handle: *mut c_void, front: *const c_char) -> i32;
    fn repo_ctp_td_authenticate(
        handle: *mut c_void,
        app_id: *const c_char,
        auth_code: *const c_char,
        product_info: *const c_char,
    ) -> i32;
    fn repo_ctp_td_login(
        handle: *mut c_void,
        broker_id: *const c_char,
        user_id: *const c_char,
        password: *const c_char,
    ) -> i32;
    fn repo_ctp_td_confirm_settlement(handle: *mut c_void) -> i32;
    fn repo_ctp_td_qry_instrument(handle: *mut c_void, symbol: *const c_char) -> i32;
    fn repo_ctp_td_qry_position(handle: *mut c_void) -> i32;
    fn repo_ctp_td_qry_account(handle: *mut c_void) -> i32;
    fn repo_ctp_td_set_callback(handle: *mut c_void, callback: TdOnExecCallback);
    fn repo_ctp_td_set_login_callback(handle: *mut c_void, callback: TdOnLoginCallback);
    fn repo_ctp_td_set_front_disconnected_callback(
        handle: *mut c_void,
        callback: TdOnFrontDisconnectedCallback,
    );
    fn repo_ctp_td_set_instrument_callback(handle: *mut c_void, callback: TdOnInstrumentCallback);
    fn repo_ctp_td_set_position_callback(handle: *mut c_void, callback: TdOnPositionCallback);
    fn repo_ctp_td_set_account_callback(handle: *mut c_void, callback: TdOnAccountCallback);
    fn repo_ctp_td_order_send(
        handle: *mut c_void,
        order_id: *const c_char,
        symbol: *const c_char,
        price: f64,
        qty: i32,
        side: i32,
        order_type: i32,
        comb_offset: *const c_char,
        comb_hedge: *const c_char,
        time_condition: i32,
        volume_condition: i32,
        contingent_condition: i32,
        stop_price: f64,
        force_close_reason: i32,
        min_volume: i32,
    ) -> i32;
    fn repo_ctp_td_order_action(
        handle: *mut c_void,
        broker_id: *const c_char,
        investor_id: *const c_char,
        instrument_id: *const c_char,
        order_ref: *const c_char,
        front_id: i32,
        session_id: i32,
        exchange_id: *const c_char,
        order_sys_id: *const c_char,
        action_flag: i32,
    ) -> i32;
}

#[cfg(ctp_vendor_bridge)]
#[no_mangle]
pub extern "C" fn MdCreate(flow_path: *const c_char) -> *mut c_void {
    unsafe { repo_ctp_md_create(flow_path) }
}

#[cfg(not(ctp_vendor_bridge))]
#[no_mangle]
pub extern "C" fn MdCreate(flow_path: *const c_char) -> *mut c_void {
    let handle = MdSessionHandle {
        _flow_path: decode_text(flow_path),
        ..MdSessionHandle::default()
    };
    Box::into_raw(Box::new(handle)).cast()
}

#[cfg(ctp_vendor_bridge)]
#[no_mangle]
pub extern "C" fn MdDispose(handle: *mut c_void) {
    unsafe { repo_ctp_md_dispose(handle) };
}

#[cfg(not(ctp_vendor_bridge))]
#[no_mangle]
pub extern "C" fn MdDispose(handle: *mut c_void) {
    if handle.is_null() {
        return;
    }
    unsafe {
        drop(Box::from_raw(handle.cast::<MdSessionHandle>()));
    }
}

#[cfg(ctp_vendor_bridge)]
#[no_mangle]
pub extern "C" fn MdInit(handle: *mut c_void, front: *const c_char) -> i32 {
    unsafe { repo_ctp_md_init(handle, front) }
}

#[cfg(not(ctp_vendor_bridge))]
#[no_mangle]
pub extern "C" fn MdInit(handle: *mut c_void, front: *const c_char) -> i32 {
    let Some(state) = (unsafe { handle.cast::<MdSessionHandle>().as_mut() }) else {
        return INVALID_HANDLE_CODE;
    };
    state._front = decode_text(front);
    NOT_IMPLEMENTED_CODE
}

#[cfg(ctp_vendor_bridge)]
#[no_mangle]
pub extern "C" fn MdLogin(
    handle: *mut c_void,
    broker_id: *const c_char,
    user_id: *const c_char,
    password: *const c_char,
) -> i32 {
    unsafe { repo_ctp_md_login(handle, broker_id, user_id, password) }
}

#[cfg(not(ctp_vendor_bridge))]
#[no_mangle]
pub extern "C" fn MdLogin(
    handle: *mut c_void,
    _broker_id: *const c_char,
    _user_id: *const c_char,
    _password: *const c_char,
) -> i32 {
    let Some(state) = (unsafe { handle.cast::<MdSessionHandle>().as_mut() }) else {
        return INVALID_HANDLE_CODE;
    };
    if let Some(callback) = state.login_callback {
        let response = scaffold_login_response();
        callback(&response);
    }
    NOT_IMPLEMENTED_CODE
}

#[cfg(ctp_vendor_bridge)]
#[no_mangle]
pub extern "C" fn MdSubscribe(handle: *mut c_void, symbols: *mut c_void, symbol_count: i32) -> i32 {
    unsafe { repo_ctp_md_subscribe(handle, symbols, symbol_count) }
}

#[cfg(not(ctp_vendor_bridge))]
#[no_mangle]
pub extern "C" fn MdSubscribe(
    handle: *mut c_void,
    _symbols: *mut c_void,
    _symbol_count: i32,
) -> i32 {
    if handle.is_null() {
        return INVALID_HANDLE_CODE;
    }
    NOT_IMPLEMENTED_CODE
}

#[cfg(ctp_vendor_bridge)]
#[no_mangle]
pub extern "C" fn MdUnsubscribe(handle: *mut c_void, symbols: *mut c_void, symbol_count: i32) -> i32 {
    unsafe { repo_ctp_md_unsubscribe(handle, symbols, symbol_count) }
}

#[cfg(not(ctp_vendor_bridge))]
#[no_mangle]
pub extern "C" fn MdUnsubscribe(
    handle: *mut c_void,
    _symbols: *mut c_void,
    _symbol_count: i32,
) -> i32 {
    if handle.is_null() {
        return INVALID_HANDLE_CODE;
    }
    NOT_IMPLEMENTED_CODE
}

#[cfg(ctp_vendor_bridge)]
#[no_mangle]
pub extern "C" fn MdSetCallback(handle: *mut c_void, callback: MdOnTickCallback) {
    unsafe { repo_ctp_md_set_callback(handle, callback) };
}

#[cfg(not(ctp_vendor_bridge))]
#[no_mangle]
pub extern "C" fn MdSetCallback(handle: *mut c_void, callback: MdOnTickCallback) {
    if let Some(state) = unsafe { handle.cast::<MdSessionHandle>().as_mut() } {
        state.tick_callback = callback;
    }
}

#[cfg(ctp_vendor_bridge)]
#[no_mangle]
pub extern "C" fn MdSetLoginCallback(handle: *mut c_void, callback: MdOnLoginCallback) {
    unsafe { repo_ctp_md_set_login_callback(handle, callback) };
}

#[cfg(not(ctp_vendor_bridge))]
#[no_mangle]
pub extern "C" fn MdSetLoginCallback(handle: *mut c_void, callback: MdOnLoginCallback) {
    if let Some(state) = unsafe { handle.cast::<MdSessionHandle>().as_mut() } {
        state.login_callback = callback;
    }
}

#[cfg(ctp_vendor_bridge)]
#[no_mangle]
pub extern "C" fn MdSetFrontDisconnectedCallback(
    handle: *mut c_void,
    callback: MdOnFrontDisconnectedCallback,
) {
    unsafe { repo_ctp_md_set_front_disconnected_callback(handle, callback) };
}

#[cfg(not(ctp_vendor_bridge))]
#[no_mangle]
pub extern "C" fn MdSetFrontDisconnectedCallback(
    handle: *mut c_void,
    callback: MdOnFrontDisconnectedCallback,
) {
    if let Some(state) = unsafe { handle.cast::<MdSessionHandle>().as_mut() } {
        state.front_disconnected_callback = callback;
    }
}

#[cfg(ctp_vendor_bridge)]
#[no_mangle]
pub extern "C" fn TdCreate(flow_path: *const c_char) -> *mut c_void {
    unsafe { repo_ctp_td_create(flow_path) }
}

#[cfg(not(ctp_vendor_bridge))]
#[no_mangle]
pub extern "C" fn TdCreate(flow_path: *const c_char) -> *mut c_void {
    let handle = TdSessionHandle {
        _flow_path: decode_text(flow_path),
        ..TdSessionHandle::default()
    };
    Box::into_raw(Box::new(handle)).cast()
}

#[cfg(ctp_vendor_bridge)]
#[no_mangle]
pub extern "C" fn TdDispose(handle: *mut c_void) {
    unsafe { repo_ctp_td_dispose(handle) };
}

#[cfg(not(ctp_vendor_bridge))]
#[no_mangle]
pub extern "C" fn TdDispose(handle: *mut c_void) {
    if handle.is_null() {
        return;
    }
    unsafe {
        drop(Box::from_raw(handle.cast::<TdSessionHandle>()));
    }
}

#[cfg(ctp_vendor_bridge)]
#[no_mangle]
pub extern "C" fn TdInit(handle: *mut c_void, front: *const c_char) -> i32 {
    unsafe { repo_ctp_td_init(handle, front) }
}

#[cfg(not(ctp_vendor_bridge))]
#[no_mangle]
pub extern "C" fn TdInit(handle: *mut c_void, front: *const c_char) -> i32 {
    let Some(state) = (unsafe { handle.cast::<TdSessionHandle>().as_mut() }) else {
        return INVALID_HANDLE_CODE;
    };
    state._front = decode_text(front);
    NOT_IMPLEMENTED_CODE
}

#[cfg(ctp_vendor_bridge)]
#[no_mangle]
pub extern "C" fn TdAuthenticate(
    handle: *mut c_void,
    app_id: *const c_char,
    auth_code: *const c_char,
    product_info: *const c_char,
) -> i32 {
    unsafe { repo_ctp_td_authenticate(handle, app_id, auth_code, product_info) }
}

#[cfg(not(ctp_vendor_bridge))]
#[no_mangle]
pub extern "C" fn TdAuthenticate(
    handle: *mut c_void,
    _app_id: *const c_char,
    _auth_code: *const c_char,
    _product_info: *const c_char,
) -> i32 {
    if handle.is_null() {
        return INVALID_HANDLE_CODE;
    }
    NOT_IMPLEMENTED_CODE
}

#[cfg(ctp_vendor_bridge)]
#[no_mangle]
pub extern "C" fn TdLogin(
    handle: *mut c_void,
    broker_id: *const c_char,
    user_id: *const c_char,
    password: *const c_char,
) -> i32 {
    unsafe { repo_ctp_td_login(handle, broker_id, user_id, password) }
}

#[cfg(not(ctp_vendor_bridge))]
#[no_mangle]
pub extern "C" fn TdLogin(
    handle: *mut c_void,
    _broker_id: *const c_char,
    _user_id: *const c_char,
    _password: *const c_char,
) -> i32 {
    let Some(state) = (unsafe { handle.cast::<TdSessionHandle>().as_mut() }) else {
        return INVALID_HANDLE_CODE;
    };
    if let Some(callback) = state.login_callback {
        let response = scaffold_login_response();
        callback(&response);
    }
    NOT_IMPLEMENTED_CODE
}

#[cfg(ctp_vendor_bridge)]
#[no_mangle]
pub extern "C" fn TdConfirmSettlement(handle: *mut c_void) -> i32 {
    unsafe { repo_ctp_td_confirm_settlement(handle) }
}

#[cfg(not(ctp_vendor_bridge))]
#[no_mangle]
pub extern "C" fn TdConfirmSettlement(handle: *mut c_void) -> i32 {
    if handle.is_null() {
        return INVALID_HANDLE_CODE;
    }
    NOT_IMPLEMENTED_CODE
}

#[cfg(ctp_vendor_bridge)]
#[no_mangle]
pub extern "C" fn TdOrderSend(
    handle: *mut c_void,
    order_id: *const c_char,
    symbol: *const c_char,
    price: f64,
    qty: i32,
    side: i32,
    order_type: i32,
    comb_offset: *const c_char,
    comb_hedge: *const c_char,
    time_condition: i32,
    volume_condition: i32,
    contingent_condition: i32,
    stop_price: f64,
    force_close_reason: i32,
    min_volume: i32,
) -> i32 {
    unsafe {
        repo_ctp_td_order_send(
            handle, order_id, symbol, price, qty, side, order_type,
            comb_offset, comb_hedge, time_condition, volume_condition,
            contingent_condition, stop_price, force_close_reason, min_volume,
        )
    }
}

#[cfg(not(ctp_vendor_bridge))]
#[no_mangle]
pub extern "C" fn TdOrderSend(
    handle: *mut c_void,
    _order_id: *const c_char,
    _symbol: *const c_char,
    _price: f64,
    _qty: i32,
    _side: i32,
    _order_type: i32,
    _comb_offset: *const c_char,
    _comb_hedge: *const c_char,
    _time_condition: i32,
    _volume_condition: i32,
    _contingent_condition: i32,
    _stop_price: f64,
    _force_close_reason: i32,
    _min_volume: i32,
) -> i32 {
    if handle.is_null() {
        return INVALID_HANDLE_CODE;
    }
    NOT_IMPLEMENTED_CODE
}

#[cfg(ctp_vendor_bridge)]
#[no_mangle]
pub extern "C" fn TdOrderAction(
    handle: *mut c_void,
    broker_id: *const c_char,
    investor_id: *const c_char,
    instrument_id: *const c_char,
    order_ref: *const c_char,
    front_id: i32,
    session_id: i32,
    exchange_id: *const c_char,
    order_sys_id: *const c_char,
    action_flag: i32,
) -> i32 {
    unsafe {
        repo_ctp_td_order_action(
            handle, broker_id, investor_id, instrument_id,
            order_ref, front_id, session_id, exchange_id,
            order_sys_id, action_flag,
        )
    }
}

#[cfg(not(ctp_vendor_bridge))]
#[no_mangle]
pub extern "C" fn TdOrderAction(
    handle: *mut c_void,
    _broker_id: *const c_char,
    _investor_id: *const c_char,
    _instrument_id: *const c_char,
    _order_ref: *const c_char,
    _front_id: i32,
    _session_id: i32,
    _exchange_id: *const c_char,
    _order_sys_id: *const c_char,
    _action_flag: i32,
) -> i32 {
    if handle.is_null() {
        return INVALID_HANDLE_CODE;
    }
    NOT_IMPLEMENTED_CODE
}

#[cfg(ctp_vendor_bridge)]
#[no_mangle]
pub extern "C" fn TdQryInstrument(handle: *mut c_void, symbol: *const c_char) -> i32 {
    unsafe { repo_ctp_td_qry_instrument(handle, symbol) }
}

#[cfg(not(ctp_vendor_bridge))]
#[no_mangle]
pub extern "C" fn TdQryInstrument(handle: *mut c_void, _symbol: *const c_char) -> i32 {
    if handle.is_null() {
        return INVALID_HANDLE_CODE;
    }
    NOT_IMPLEMENTED_CODE
}

#[cfg(ctp_vendor_bridge)]
#[no_mangle]
pub extern "C" fn TdQryPosition(handle: *mut c_void) -> i32 {
    unsafe { repo_ctp_td_qry_position(handle) }
}

#[cfg(not(ctp_vendor_bridge))]
#[no_mangle]
pub extern "C" fn TdQryPosition(handle: *mut c_void) -> i32 {
    if handle.is_null() {
        return INVALID_HANDLE_CODE;
    }
    NOT_IMPLEMENTED_CODE
}

#[cfg(ctp_vendor_bridge)]
#[no_mangle]
pub extern "C" fn TdQryAccount(handle: *mut c_void) -> i32 {
    unsafe { repo_ctp_td_qry_account(handle) }
}

#[cfg(not(ctp_vendor_bridge))]
#[no_mangle]
pub extern "C" fn TdQryAccount(handle: *mut c_void) -> i32 {
    if handle.is_null() {
        return INVALID_HANDLE_CODE;
    }
    NOT_IMPLEMENTED_CODE
}

#[no_mangle]
pub extern "C" fn TdQryInstrumentStatus(handle: *mut c_void) -> i32 {
    if handle.is_null() {
        return INVALID_HANDLE_CODE;
    }
    NOT_IMPLEMENTED_CODE
}

#[cfg(ctp_vendor_bridge)]
#[no_mangle]
pub extern "C" fn TdSetCallback(handle: *mut c_void, callback: TdOnExecCallback) {
    unsafe { repo_ctp_td_set_callback(handle, callback) };
}

#[cfg(not(ctp_vendor_bridge))]
#[no_mangle]
pub extern "C" fn TdSetCallback(handle: *mut c_void, callback: TdOnExecCallback) {
    if let Some(state) = unsafe { handle.cast::<TdSessionHandle>().as_mut() } {
        state.exec_callback = callback;
    }
}

#[cfg(ctp_vendor_bridge)]
#[no_mangle]
pub extern "C" fn TdSetLoginCallback(handle: *mut c_void, callback: TdOnLoginCallback) {
    unsafe { repo_ctp_td_set_login_callback(handle, callback) };
}

#[cfg(not(ctp_vendor_bridge))]
#[no_mangle]
pub extern "C" fn TdSetLoginCallback(handle: *mut c_void, callback: TdOnLoginCallback) {
    if let Some(state) = unsafe { handle.cast::<TdSessionHandle>().as_mut() } {
        state.login_callback = callback;
    }
}

#[cfg(ctp_vendor_bridge)]
#[no_mangle]
pub extern "C" fn TdSetFrontDisconnectedCallback(
    handle: *mut c_void,
    callback: TdOnFrontDisconnectedCallback,
) {
    unsafe { repo_ctp_td_set_front_disconnected_callback(handle, callback) };
}

#[cfg(not(ctp_vendor_bridge))]
#[no_mangle]
pub extern "C" fn TdSetFrontDisconnectedCallback(
    handle: *mut c_void,
    callback: TdOnFrontDisconnectedCallback,
) {
    if let Some(state) = unsafe { handle.cast::<TdSessionHandle>().as_mut() } {
        state.front_disconnected_callback = callback;
    }
}

#[cfg(ctp_vendor_bridge)]
#[no_mangle]
pub extern "C" fn TdSetInstrumentCallback(handle: *mut c_void, callback: TdOnInstrumentCallback) {
    unsafe { repo_ctp_td_set_instrument_callback(handle, callback) };
}

#[cfg(not(ctp_vendor_bridge))]
#[no_mangle]
pub extern "C" fn TdSetInstrumentCallback(handle: *mut c_void, callback: TdOnInstrumentCallback) {
    if let Some(state) = unsafe { handle.cast::<TdSessionHandle>().as_mut() } {
        state.instrument_callback = callback;
    }
}

#[cfg(ctp_vendor_bridge)]
#[no_mangle]
pub extern "C" fn TdSetPositionCallback(handle: *mut c_void, callback: TdOnPositionCallback) {
    unsafe { repo_ctp_td_set_position_callback(handle, callback) };
}

#[cfg(not(ctp_vendor_bridge))]
#[no_mangle]
pub extern "C" fn TdSetPositionCallback(handle: *mut c_void, callback: TdOnPositionCallback) {
    if let Some(state) = unsafe { handle.cast::<TdSessionHandle>().as_mut() } {
        state.position_callback = callback;
    }
}

#[cfg(ctp_vendor_bridge)]
#[no_mangle]
pub extern "C" fn TdSetAccountCallback(handle: *mut c_void, callback: TdOnAccountCallback) {
    unsafe { repo_ctp_td_set_account_callback(handle, callback) };
}

#[cfg(not(ctp_vendor_bridge))]
#[no_mangle]
pub extern "C" fn TdSetAccountCallback(handle: *mut c_void, callback: TdOnAccountCallback) {
    if let Some(state) = unsafe { handle.cast::<TdSessionHandle>().as_mut() } {
        state.account_callback = callback;
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::ptr::null;
    #[cfg(not(ctp_vendor_bridge))]
    use std::ffi::CStr;
    #[cfg(not(ctp_vendor_bridge))]
    use std::sync::{Mutex, OnceLock};

    #[cfg(not(ctp_vendor_bridge))]
    #[derive(Debug, Clone, PartialEq, Eq)]
    struct LoginSnapshot {
        error_id: i32,
        error_message: String,
        front_id: i32,
        session_id: i32,
        max_order_ref: i64,
    }

    #[cfg(not(ctp_vendor_bridge))]
    fn md_login_capture() -> &'static Mutex<Option<LoginSnapshot>> {
        static CAPTURE: OnceLock<Mutex<Option<LoginSnapshot>>> = OnceLock::new();
        CAPTURE.get_or_init(|| Mutex::new(None))
    }

    #[cfg(not(ctp_vendor_bridge))]
    fn td_login_capture() -> &'static Mutex<Option<LoginSnapshot>> {
        static CAPTURE: OnceLock<Mutex<Option<LoginSnapshot>>> = OnceLock::new();
        CAPTURE.get_or_init(|| Mutex::new(None))
    }

    #[cfg(not(ctp_vendor_bridge))]
    extern "C" fn capture_md_login(resp: *const NativeLoginResponse) {
        let response = unsafe { &*resp };
        let message = if response.ErrorMsg.is_null() {
            String::new()
        } else {
            unsafe { CStr::from_ptr(response.ErrorMsg) }
                .to_string_lossy()
                .into_owned()
        };
        *md_login_capture().lock().expect("md login capture poisoned") = Some(LoginSnapshot {
            error_id: response.ErrorId,
            error_message: message,
            front_id: response.FrontId,
            session_id: response.SessionId,
            max_order_ref: response.MaxOrderRef,
        });
    }

    #[cfg(not(ctp_vendor_bridge))]
    extern "C" fn capture_td_login(resp: *const NativeLoginResponse) {
        let response = unsafe { &*resp };
        let message = if response.ErrorMsg.is_null() {
            String::new()
        } else {
            unsafe { CStr::from_ptr(response.ErrorMsg) }
                .to_string_lossy()
                .into_owned()
        };
        *td_login_capture().lock().expect("td login capture poisoned") = Some(LoginSnapshot {
            error_id: response.ErrorId,
            error_message: message,
            front_id: response.FrontId,
            session_id: response.SessionId,
            max_order_ref: response.MaxOrderRef,
        });
    }

    #[test]
    fn invalid_handle_contract_is_frozen() {
        assert_eq!(MdInit(std::ptr::null_mut(), null()), INVALID_HANDLE_CODE);
        assert_eq!(MdSubscribe(std::ptr::null_mut(), std::ptr::null_mut(), 0), INVALID_HANDLE_CODE);
        assert_eq!(MdUnsubscribe(std::ptr::null_mut(), std::ptr::null_mut(), 0), INVALID_HANDLE_CODE);
        assert_eq!(TdInit(std::ptr::null_mut(), null()), INVALID_HANDLE_CODE);
        assert_eq!(TdAuthenticate(std::ptr::null_mut(), null(), null(), null()), INVALID_HANDLE_CODE);
        assert_eq!(TdConfirmSettlement(std::ptr::null_mut()), INVALID_HANDLE_CODE);
        assert_eq!(TdQryInstrument(std::ptr::null_mut(), null()), INVALID_HANDLE_CODE);
        assert_eq!(TdQryPosition(std::ptr::null_mut()), INVALID_HANDLE_CODE);
        assert_eq!(TdQryAccount(std::ptr::null_mut()), INVALID_HANDLE_CODE);
        assert_eq!(TdQryInstrumentStatus(std::ptr::null_mut()), INVALID_HANDLE_CODE);
        assert_eq!(TdOrderSend(
            std::ptr::null_mut(),
            null(),
            null(),
            0.0,
            0,
            0,
            0,
            null(),
            null(),
            0,
            0,
            0,
            0.0,
            0,
            0,
        ), INVALID_HANDLE_CODE);
        assert_eq!(
            TdOrderAction(std::ptr::null_mut(), null(), null(), null(), null(), 0, 0, null(), null(), 0),
            INVALID_HANDLE_CODE
        );
    }

    #[cfg(not(ctp_vendor_bridge))]
    #[test]
    fn md_scaffold_error_contract_is_frozen() {
        let handle = MdCreate(null());
        assert!(!handle.is_null());
        MdSetLoginCallback(handle, Some(capture_md_login));
        assert_eq!(MdInit(handle, null()), NOT_IMPLEMENTED_CODE);
        assert_eq!(MdSubscribe(handle, std::ptr::null_mut(), 0), NOT_IMPLEMENTED_CODE);
        assert_eq!(MdUnsubscribe(handle, std::ptr::null_mut(), 0), NOT_IMPLEMENTED_CODE);
        assert_eq!(MdLogin(handle, null(), null(), null()), NOT_IMPLEMENTED_CODE);

        let response = md_login_capture()
            .lock()
            .expect("md login capture poisoned")
            .take()
            .expect("expected md login callback response");
        assert_eq!(
            response,
            LoginSnapshot {
                error_id: NOT_IMPLEMENTED_CODE,
                error_message: "repo-owned ctp_native scaffold only; live vendor bridge not implemented".to_string(),
                front_id: 0,
                session_id: 0,
                max_order_ref: 0,
            }
        );
        MdDispose(handle);
    }

    #[cfg(not(ctp_vendor_bridge))]
    #[test]
    fn td_scaffold_error_contract_is_frozen() {
        let handle = TdCreate(null());
        assert!(!handle.is_null());
        TdSetLoginCallback(handle, Some(capture_td_login));
        assert_eq!(TdInit(handle, null()), NOT_IMPLEMENTED_CODE);
        assert_eq!(TdAuthenticate(handle, null(), null(), null()), NOT_IMPLEMENTED_CODE);
        assert_eq!(TdConfirmSettlement(handle), NOT_IMPLEMENTED_CODE);
        assert_eq!(TdQryInstrument(handle, null()), NOT_IMPLEMENTED_CODE);
        assert_eq!(TdQryPosition(handle), NOT_IMPLEMENTED_CODE);
        assert_eq!(TdQryAccount(handle), NOT_IMPLEMENTED_CODE);
        assert_eq!(TdQryInstrumentStatus(handle), NOT_IMPLEMENTED_CODE);
        assert_eq!(TdLogin(handle, null(), null(), null()), NOT_IMPLEMENTED_CODE);

        let response = td_login_capture()
            .lock()
            .expect("td login capture poisoned")
            .take()
            .expect("expected td login callback response");
        assert_eq!(
            response,
            LoginSnapshot {
                error_id: NOT_IMPLEMENTED_CODE,
                error_message: "repo-owned ctp_native scaffold only; live vendor bridge not implemented".to_string(),
                front_id: 0,
                session_id: 0,
                max_order_ref: 0,
            }
        );
        TdDispose(handle);
    }
}