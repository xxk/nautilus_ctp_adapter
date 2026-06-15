#pragma once

#include <cstdint>

extern "C" {

struct NativeLoginResponse {
    std::int32_t FrontId;
    std::int32_t SessionId;
    std::int64_t MaxOrderRef;
    std::int32_t ErrorId;
    const char* ErrorMsg;
};

struct NativeTick {
    const char* symbol;
    double last;
    double bid;
    double ask;
    std::int64_t ts_epoch_us;
    std::int32_t bid_size;
    std::int32_t ask_size;
    std::int32_t volume;
    double open_interest;
};

struct NativeInstrument {
    const char* symbol;
    const char* exchange;
    const char* exchange_inst_id;
    const char* product_id;
    double tick_size;
    std::int32_t volume_multiple;
    std::int32_t lot_size;
    const char* instrument_name;
    const char* expire_date;
    std::uint8_t product_class;
    double strike_price;
    const char* underlying_instr_id;
    std::uint8_t options_type;
    std::int64_t ts_epoch_us;
    const char* open_date;
    const char* create_date;
};

struct NativeExec {
    const char* order_id;
    const char* symbol;
    double price;
    std::int32_t qty;
    std::int32_t side;
    std::int32_t status;
    std::int64_t ts_epoch_us;
    const char* order_ref;
    std::int32_t front_id;
    std::int32_t session_id;
    std::int32_t direction;
    std::int32_t offset_flag;
    std::int32_t hedge_flag;
    std::int32_t is_trade;
    double trade_price;
    std::int32_t trade_volume;
    const char* error_msg;
    std::int32_t leaves_qty;
    const char* callback_source;
    std::int32_t submit_request_offset_flag;
    const char* submit_request_offset_source;
    std::int32_t response_request_id;
    std::int32_t response_is_last;
    std::int32_t response_error_id;
};

struct NativePosition {
    const char* symbol;
    const char* exchange_id;
    const char* broker_id;
    const char* investor_id;
    std::int32_t pos_direction;
    std::int32_t hedge_flag;
    std::int32_t date_type;
    std::int32_t position;
    std::int32_t yd_position;
    std::int32_t today_position;
    double position_cost;
    double open_cost;
    double exchange_margin;
    double use_margin;
    double position_profit;
    std::int64_t ts_epoch_us;
};

struct NativeTradingAccount {
    const char* broker_id;
    const char* account_id;
    double balance;
    double available;
    double withdraw_quota;
    double curr_margin;
    double frozen_margin;
    double commission;
    double frozen_commission;
    double position_profit;
    double close_profit;
    const char* currency_id;
    std::int64_t ts_epoch_us;
};

using MdOnLoginCallback = void (*)(const NativeLoginResponse* response);
using MdOnFrontDisconnectedCallback = void (*)(std::int32_t reason);
using MdOnTickCallback = void (*)(const NativeTick* tick);

using TdOnLoginCallback = void (*)(const NativeLoginResponse* response);
using TdOnFrontDisconnectedCallback = void (*)(std::int32_t reason);
using TdOnExecCallback = void (*)(const NativeExec* exec_view);
using TdOnInstrumentCallback = void (*)(const NativeInstrument* instrument, std::int32_t request_id, std::int32_t is_last);
using TdOnPositionCallback = void (*)(const NativePosition* position, std::int32_t request_id, std::int32_t is_last);
using TdOnAccountCallback = void (*)(const NativeTradingAccount* account);

void* repo_ctp_md_create(const char* flow_path);
void repo_ctp_md_dispose(void* handle);
std::int32_t repo_ctp_md_init(void* handle, const char* front);
std::int32_t repo_ctp_md_login(void* handle, const char* broker_id, const char* user_id, const char* password);
std::int32_t repo_ctp_md_subscribe(void* handle, void* symbols, std::int32_t symbol_count);
std::int32_t repo_ctp_md_unsubscribe(void* handle, void* symbols, std::int32_t symbol_count);
void repo_ctp_md_set_callback(void* handle, MdOnTickCallback callback);
void repo_ctp_md_set_login_callback(void* handle, MdOnLoginCallback callback);
void repo_ctp_md_set_front_disconnected_callback(void* handle, MdOnFrontDisconnectedCallback callback);

void* repo_ctp_td_create(const char* flow_path);
void repo_ctp_td_dispose(void* handle);
std::int32_t repo_ctp_td_init(void* handle, const char* front);
std::int32_t repo_ctp_td_authenticate(void* handle, const char* app_id, const char* auth_code, const char* product_info);
std::int32_t repo_ctp_td_login(void* handle, const char* broker_id, const char* user_id, const char* password);
std::int32_t repo_ctp_td_confirm_settlement(void* handle);
std::int32_t repo_ctp_td_qry_instrument(void* handle, const char* symbol);
std::int32_t repo_ctp_td_qry_position(void* handle);
std::int32_t repo_ctp_td_qry_account(void* handle);
void repo_ctp_td_set_callback(void* handle, TdOnExecCallback callback);
void repo_ctp_td_set_login_callback(void* handle, TdOnLoginCallback callback);
void repo_ctp_td_set_front_disconnected_callback(void* handle, TdOnFrontDisconnectedCallback callback);
void repo_ctp_td_set_instrument_callback(void* handle, TdOnInstrumentCallback callback);
void repo_ctp_td_set_position_callback(void* handle, TdOnPositionCallback callback);
void repo_ctp_td_set_account_callback(void* handle, TdOnAccountCallback callback);

std::int32_t repo_ctp_td_order_send(
    void* handle,
    const char* order_id,
    const char* symbol,
    std::int32_t request_id,
    double price,
    std::int32_t qty,
    std::int32_t side,
    std::int32_t order_type,
    const char* comb_offset,
    const char* comb_hedge,
    std::int32_t time_condition,
    std::int32_t volume_condition,
    std::int32_t contingent_condition,
    double stop_price,
    std::int32_t force_close_reason,
    std::int32_t min_volume);

std::int32_t repo_ctp_td_order_action(
    void* handle,
    const char* broker_id,
    const char* investor_id,
    const char* instrument_id,
    const char* order_ref,
    std::int32_t front_id,
    std::int32_t session_id,
    const char* exchange_id,
    const char* order_sys_id,
    std::int32_t action_flag);

}
