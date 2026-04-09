#include "ctp_bridge.hpp"

#include "ThostFtdcMdApi.h"
#include "ThostFtdcTraderApi.h"
#include "ThostFtdcUserApiDataType.h"

#include <chrono>
#include <cctype>
#include <cstdint>
#include <cstring>
#include <mutex>
#include <string>
#include <unordered_map>

namespace {

constexpr std::int32_t INVALID_HANDLE_CODE = -9001;

struct SessionIdentity {
    std::int32_t front_id = 0;
    std::int32_t session_id = 0;
};

struct MdSession;
class MdSpiImpl;
struct TdSession;
class TdSpiImpl;

struct MdSession {
    std::mutex mutex;
    CThostFtdcMdApi* api = nullptr;
    MdSpiImpl* spi = nullptr;
    std::string flow_path;
    std::string front;
    std::string broker_id;
    std::string user_id;
    std::string password;
    bool initialized = false;
    bool connected = false;
    bool login_requested = false;
    bool login_dispatched = false;
    std::int32_t next_request_id = 1;
    MdOnLoginCallback login_callback = nullptr;
    MdOnTickCallback tick_callback = nullptr;
    MdOnFrontDisconnectedCallback disconnect_callback = nullptr;
};

struct TdSession {
    std::mutex mutex;
    CThostFtdcTraderApi* api = nullptr;
    TdSpiImpl* spi = nullptr;
    std::string flow_path;
    std::string front;
    std::string broker_id;
    std::string user_id;
    std::string password;
    std::string app_id;
    std::string auth_code;
    std::string product_info;
    bool initialized = false;
    bool connected = false;
    bool auth_requested = false;
    bool auth_dispatched = false;
    bool authenticated = false;
    bool login_requested = false;
    bool login_dispatched = false;
    bool logged_in = false;
    std::int32_t next_request_id = 1;
    std::int32_t login_front_id = 0;
    std::int32_t login_session_id = 0;
    std::int64_t login_max_order_ref = 0;
    TdOnLoginCallback login_callback = nullptr;
    TdOnExecCallback exec_callback = nullptr;
    TdOnFrontDisconnectedCallback disconnect_callback = nullptr;
    TdOnInstrumentCallback instrument_callback = nullptr;
    TdOnPositionCallback position_callback = nullptr;
    TdOnAccountCallback account_callback = nullptr;
    std::unordered_map<std::string, SessionIdentity> identity_by_order_ref;
    std::unordered_map<std::string, SessionIdentity> identity_by_order_sys_id;
};

std::string trim_text(std::string value) {
    auto begin = value.begin();
    while (begin != value.end() && std::isspace(static_cast<unsigned char>(*begin)) != 0) {
        ++begin;
    }
    auto end = value.end();
    while (end != begin && std::isspace(static_cast<unsigned char>(*(end - 1))) != 0) {
        --end;
    }
    return std::string(begin, end);
}

std::string normalized_text(const char* value) {
    if (value == nullptr) {
        return {};
    }
    return trim_text(std::string(value));
}

template <std::size_t N>
void copy_ctp_text(char (&destination)[N], const std::string& value) {
    std::memset(destination, 0, N);
    if (value.empty()) {
        return;
    }
    const std::size_t count = value.size() < (N - 1) ? value.size() : (N - 1);
    std::memcpy(destination, value.data(), count);
}

std::int64_t now_epoch_us() {
    using namespace std::chrono;
    return duration_cast<microseconds>(system_clock::now().time_since_epoch()).count();
}

bool is_all_digits(const std::string& value) {
    if (value.empty()) {
        return false;
    }
    for (char ch : value) {
        if (!std::isdigit(static_cast<unsigned char>(ch))) {
            return false;
        }
    }
    return true;
}

std::int64_t parse_i64_text(const std::string& value) {
    if (!is_all_digits(value)) {
        return 0;
    }
    try {
        return std::stoll(value);
    } catch (...) {
        return 0;
    }
}

int normalize_enum_value(char value) {
    if (value >= '0' && value <= '9') {
        return value - '0';
    }
    return static_cast<unsigned char>(value);
}

bool parse_date_yyyymmdd(const std::string& value, int& year, unsigned& month, unsigned& day) {
    if (value.size() != 8 || !is_all_digits(value)) {
        return false;
    }
    year = std::stoi(value.substr(0, 4));
    month = static_cast<unsigned>(std::stoi(value.substr(4, 2)));
    day = static_cast<unsigned>(std::stoi(value.substr(6, 2)));
    return true;
}

bool parse_time_hhmmss(const std::string& value, int& hour, int& minute, int& second) {
    if (value.size() < 8) {
        return false;
    }
    if (!std::isdigit(static_cast<unsigned char>(value[0])) || !std::isdigit(static_cast<unsigned char>(value[1]))
        || value[2] != ':' || !std::isdigit(static_cast<unsigned char>(value[3]))
        || !std::isdigit(static_cast<unsigned char>(value[4])) || value[5] != ':'
        || !std::isdigit(static_cast<unsigned char>(value[6])) || !std::isdigit(static_cast<unsigned char>(value[7]))) {
        return false;
    }
    hour = std::stoi(value.substr(0, 2));
    minute = std::stoi(value.substr(3, 2));
    second = std::stoi(value.substr(6, 2));
    return true;
}

std::int64_t compose_epoch_us(const std::string& date_value, const std::string& time_value, int millisec) {
    int year_value = 0;
    unsigned month_value = 0;
    unsigned day_value = 0;
    int hour = 0;
    int minute = 0;
    int second = 0;
    if (!parse_date_yyyymmdd(date_value, year_value, month_value, day_value)
        || !parse_time_hhmmss(time_value, hour, minute, second)) {
        return now_epoch_us();
    }

    using namespace std::chrono;
    const sys_days day_point = std::chrono::year{year_value} / std::chrono::month{month_value} / std::chrono::day{day_value};
    const auto timestamp = day_point + hours{hour} + minutes{minute} + seconds{second} + milliseconds{millisec};
    return duration_cast<microseconds>(timestamp.time_since_epoch()).count();
}

std::int64_t compose_epoch_us_from_fields(const char* primary_date, const char* fallback_date, const char* time_value, int millisec) {
    const std::string primary = normalized_text(primary_date);
    const std::string date_text = primary.empty() ? normalized_text(fallback_date) : primary;
    return compose_epoch_us(date_text, normalized_text(time_value), millisec);
}

std::int32_t rsp_error_id(const CThostFtdcRspInfoField* rsp_info) {
    return rsp_info == nullptr ? 0 : rsp_info->ErrorID;
}

std::string rsp_error_message(const CThostFtdcRspInfoField* rsp_info) {
    return rsp_info == nullptr ? std::string() : normalized_text(rsp_info->ErrorMsg);
}

class MdSpiImpl final : public CThostFtdcMdSpi {
public:
    explicit MdSpiImpl(MdSession* session) : session_(session) {}

    void Detach() {
        std::scoped_lock lock(mutex_);
        session_ = nullptr;
    }

    void OnFrontConnected() override;
    void OnFrontDisconnected(int reason) override;
    void OnRspUserLogin(CThostFtdcRspUserLoginField* rsp_user_login, CThostFtdcRspInfoField* rsp_info, int request_id, bool is_last) override;
    void OnRtnDepthMarketData(CThostFtdcDepthMarketDataField* depth_market_data) override;

private:
    MdSession* session() {
        std::scoped_lock lock(mutex_);
        return session_;
    }

    std::mutex mutex_;
    MdSession* session_;
};

class TdSpiImpl final : public CThostFtdcTraderSpi {
public:
    explicit TdSpiImpl(TdSession* session) : session_(session) {}

    void Detach() {
        std::scoped_lock lock(mutex_);
        session_ = nullptr;
    }

    void OnFrontConnected() override;
    void OnFrontDisconnected(int reason) override;
    void OnRspAuthenticate(CThostFtdcRspAuthenticateField* rsp_authenticate, CThostFtdcRspInfoField* rsp_info, int request_id, bool is_last) override;
    void OnRspUserLogin(CThostFtdcRspUserLoginField* rsp_user_login, CThostFtdcRspInfoField* rsp_info, int request_id, bool is_last) override;
    void OnRspQryInstrument(CThostFtdcInstrumentField* instrument, CThostFtdcRspInfoField* rsp_info, int request_id, bool is_last) override;
    void OnRspQryInvestorPosition(CThostFtdcInvestorPositionField* position, CThostFtdcRspInfoField* rsp_info, int request_id, bool is_last) override;
    void OnRspQryTradingAccount(CThostFtdcTradingAccountField* account, CThostFtdcRspInfoField* rsp_info, int request_id, bool is_last) override;
    void OnRtnOrder(CThostFtdcOrderField* order) override;
    void OnRtnTrade(CThostFtdcTradeField* trade) override;

private:
    TdSession* session() {
        std::scoped_lock lock(mutex_);
        return session_;
    }

    std::mutex mutex_;
    TdSession* session_;
};

struct MdLoginRequest {
    CThostFtdcMdApi* api = nullptr;
    std::string broker_id;
    std::string user_id;
    std::string password;
    std::int32_t request_id = 0;
    bool ready = false;
};

MdLoginRequest prepare_md_login(MdSession* session) {
    std::scoped_lock lock(session->mutex);
    if (session->api == nullptr || !session->connected || !session->login_requested || session->login_dispatched) {
        return {};
    }
    session->login_dispatched = true;
    return {
        session->api,
        session->broker_id,
        session->user_id,
        session->password,
        session->next_request_id++,
        true,
    };
}

std::int32_t send_md_login_if_ready(MdSession* session) {
    const MdLoginRequest request = prepare_md_login(session);
    if (!request.ready) {
        return 0;
    }
    CThostFtdcReqUserLoginField login{};
    copy_ctp_text(login.BrokerID, request.broker_id);
    copy_ctp_text(login.UserID, request.user_id);
    copy_ctp_text(login.Password, request.password);
    return request.api->ReqUserLogin(&login, request.request_id);
}

struct TdAuthRequest {
    CThostFtdcTraderApi* api = nullptr;
    std::string broker_id;
    std::string user_id;
    std::string product_info;
    std::string auth_code;
    std::string app_id;
    std::int32_t request_id = 0;
    bool ready = false;
};

struct TdLoginRequest {
    CThostFtdcTraderApi* api = nullptr;
    std::string broker_id;
    std::string user_id;
    std::string password;
    std::int32_t request_id = 0;
    bool ready = false;
};

TdAuthRequest prepare_td_auth(TdSession* session) {
    std::scoped_lock lock(session->mutex);
    const bool needs_auth = session->auth_requested && (!session->auth_code.empty() || !session->app_id.empty());
    if (session->api == nullptr || !session->connected || !needs_auth || session->authenticated || session->auth_dispatched
        || session->broker_id.empty() || session->user_id.empty()) {
        return {};
    }
    session->auth_dispatched = true;
    return {
        session->api,
        session->broker_id,
        session->user_id,
        session->product_info,
        session->auth_code,
        session->app_id,
        session->next_request_id++,
        true,
    };
}

TdLoginRequest prepare_td_login(TdSession* session) {
    std::scoped_lock lock(session->mutex);
    const bool needs_auth = session->auth_requested && (!session->auth_code.empty() || !session->app_id.empty());
    if (session->api == nullptr || !session->connected || !session->login_requested || session->login_dispatched || session->logged_in
        || session->broker_id.empty() || session->user_id.empty()) {
        return {};
    }
    if (needs_auth && !session->authenticated) {
        return {};
    }
    session->login_dispatched = true;
    return {
        session->api,
        session->broker_id,
        session->user_id,
        session->password,
        session->next_request_id++,
        true,
    };
}

std::int32_t send_td_auth_or_login_if_ready(TdSession* session) {
    if (const TdAuthRequest auth_request = prepare_td_auth(session); auth_request.ready) {
        CThostFtdcReqAuthenticateField authenticate{};
        copy_ctp_text(authenticate.BrokerID, auth_request.broker_id);
        copy_ctp_text(authenticate.UserID, auth_request.user_id);
        copy_ctp_text(authenticate.UserProductInfo, auth_request.product_info);
        copy_ctp_text(authenticate.AuthCode, auth_request.auth_code);
        copy_ctp_text(authenticate.AppID, auth_request.app_id);
        return auth_request.api->ReqAuthenticate(&authenticate, auth_request.request_id);
    }

    if (const TdLoginRequest login_request = prepare_td_login(session); login_request.ready) {
        CThostFtdcReqUserLoginField login{};
        copy_ctp_text(login.BrokerID, login_request.broker_id);
        copy_ctp_text(login.UserID, login_request.user_id);
        copy_ctp_text(login.Password, login_request.password);
        return login_request.api->ReqUserLogin(&login, login_request.request_id);
    }
    return 0;
}

SessionIdentity current_td_identity_locked(const TdSession& session) {
    return {session.login_front_id, session.login_session_id};
}

void remember_td_order_identity_locked(TdSession& session, const std::string& order_ref, const std::string& order_sys_id, SessionIdentity identity) {
    if (!order_ref.empty()) {
        session.identity_by_order_ref[order_ref] = identity;
    }
    if (!order_sys_id.empty()) {
        session.identity_by_order_sys_id[order_sys_id] = identity;
    }
}

SessionIdentity resolve_td_order_identity_locked(const TdSession& session, const std::string& order_ref, const std::string& order_sys_id) {
    if (!order_sys_id.empty()) {
        if (const auto found = session.identity_by_order_sys_id.find(order_sys_id); found != session.identity_by_order_sys_id.end()) {
            return found->second;
        }
    }
    if (!order_ref.empty()) {
        if (const auto found = session.identity_by_order_ref.find(order_ref); found != session.identity_by_order_ref.end()) {
            return found->second;
        }
    }
    return current_td_identity_locked(session);
}

void MdSpiImpl::OnFrontConnected() {
    if (MdSession* session_ptr = session()) {
        {
            std::scoped_lock lock(session_ptr->mutex);
            session_ptr->connected = true;
        }
        static_cast<void>(send_md_login_if_ready(session_ptr));
    }
}

void MdSpiImpl::OnFrontDisconnected(int reason) {
    if (MdSession* session_ptr = session()) {
        MdOnFrontDisconnectedCallback callback = nullptr;
        {
            std::scoped_lock lock(session_ptr->mutex);
            session_ptr->connected = false;
            session_ptr->login_dispatched = false;
            callback = session_ptr->disconnect_callback;
        }
        if (callback != nullptr) {
            callback(reason);
        }
    }
}

void MdSpiImpl::OnRspUserLogin(CThostFtdcRspUserLoginField* rsp_user_login, CThostFtdcRspInfoField* rsp_info, int request_id, bool is_last) {
    static_cast<void>(request_id);
    if (!is_last) {
        return;
    }
    if (MdSession* session_ptr = session()) {
        const std::int32_t error_id = rsp_error_id(rsp_info);
        const std::string error_message = rsp_error_message(rsp_info);
        const std::int32_t front_id = rsp_user_login == nullptr ? 0 : rsp_user_login->FrontID;
        const std::int32_t session_id = rsp_user_login == nullptr ? 0 : rsp_user_login->SessionID;
        const std::int64_t max_order_ref = rsp_user_login == nullptr ? 0 : parse_i64_text(normalized_text(rsp_user_login->MaxOrderRef));
        MdOnLoginCallback callback = nullptr;
        {
            std::scoped_lock lock(session_ptr->mutex);
            session_ptr->login_dispatched = false;
            callback = session_ptr->login_callback;
        }
        if (callback != nullptr) {
            const NativeLoginResponse response{
                front_id,
                session_id,
                max_order_ref,
                error_id,
                error_message.empty() ? nullptr : error_message.c_str(),
            };
            callback(&response);
        }
    }
}

void MdSpiImpl::OnRtnDepthMarketData(CThostFtdcDepthMarketDataField* depth_market_data) {
    if (depth_market_data == nullptr) {
        return;
    }
    if (MdSession* session_ptr = session()) {
        MdOnTickCallback callback = nullptr;
        {
            std::scoped_lock lock(session_ptr->mutex);
            callback = session_ptr->tick_callback;
        }
        if (callback == nullptr) {
            return;
        }

        const std::string symbol = normalized_text(depth_market_data->InstrumentID);
        const NativeTick tick{
            symbol.c_str(),
            depth_market_data->LastPrice,
            depth_market_data->BidPrice1,
            depth_market_data->AskPrice1,
            compose_epoch_us_from_fields(depth_market_data->ActionDay, depth_market_data->TradingDay, depth_market_data->UpdateTime, depth_market_data->UpdateMillisec),
            depth_market_data->BidVolume1,
            depth_market_data->AskVolume1,
            depth_market_data->Volume,
            static_cast<double>(depth_market_data->OpenInterest),
        };
        callback(&tick);
    }
}

void TdSpiImpl::OnFrontConnected() {
    if (TdSession* session_ptr = session()) {
        {
            std::scoped_lock lock(session_ptr->mutex);
            session_ptr->connected = true;
        }
        static_cast<void>(send_td_auth_or_login_if_ready(session_ptr));
    }
}

void TdSpiImpl::OnFrontDisconnected(int reason) {
    if (TdSession* session_ptr = session()) {
        TdOnFrontDisconnectedCallback callback = nullptr;
        {
            std::scoped_lock lock(session_ptr->mutex);
            session_ptr->connected = false;
            session_ptr->authenticated = false;
            session_ptr->auth_dispatched = false;
            session_ptr->login_dispatched = false;
            session_ptr->logged_in = false;
            callback = session_ptr->disconnect_callback;
        }
        if (callback != nullptr) {
            callback(reason);
        }
    }
}

void TdSpiImpl::OnRspAuthenticate(CThostFtdcRspAuthenticateField* rsp_authenticate, CThostFtdcRspInfoField* rsp_info, int request_id, bool is_last) {
    static_cast<void>(rsp_authenticate);
    static_cast<void>(request_id);
    if (!is_last) {
        return;
    }
    if (TdSession* session_ptr = session()) {
        const std::int32_t error_id = rsp_error_id(rsp_info);
        const std::string error_message = rsp_error_message(rsp_info);
        TdOnLoginCallback callback = nullptr;
        {
            std::scoped_lock lock(session_ptr->mutex);
            session_ptr->auth_dispatched = false;
            session_ptr->authenticated = error_id == 0;
            callback = session_ptr->login_callback;
        }
        if (error_id == 0) {
            static_cast<void>(send_td_auth_or_login_if_ready(session_ptr));
            return;
        }
        if (callback != nullptr) {
            const NativeLoginResponse response{
                0,
                0,
                0,
                error_id,
                error_message.empty() ? nullptr : error_message.c_str(),
            };
            callback(&response);
        }
    }
}

void TdSpiImpl::OnRspUserLogin(CThostFtdcRspUserLoginField* rsp_user_login, CThostFtdcRspInfoField* rsp_info, int request_id, bool is_last) {
    static_cast<void>(request_id);
    if (!is_last) {
        return;
    }
    if (TdSession* session_ptr = session()) {
        const std::int32_t error_id = rsp_error_id(rsp_info);
        const std::string error_message = rsp_error_message(rsp_info);
        const std::int32_t front_id = rsp_user_login == nullptr ? 0 : rsp_user_login->FrontID;
        const std::int32_t session_id = rsp_user_login == nullptr ? 0 : rsp_user_login->SessionID;
        const std::int64_t max_order_ref = rsp_user_login == nullptr ? 0 : parse_i64_text(normalized_text(rsp_user_login->MaxOrderRef));
        TdOnLoginCallback callback = nullptr;
        {
            std::scoped_lock lock(session_ptr->mutex);
            session_ptr->login_dispatched = false;
            session_ptr->logged_in = error_id == 0;
            if (error_id == 0) {
                session_ptr->login_front_id = front_id;
                session_ptr->login_session_id = session_id;
                session_ptr->login_max_order_ref = max_order_ref;
            }
            callback = session_ptr->login_callback;
        }
        if (callback != nullptr) {
            const NativeLoginResponse response{
                front_id,
                session_id,
                max_order_ref,
                error_id,
                error_message.empty() ? nullptr : error_message.c_str(),
            };
            callback(&response);
        }
    }
}

void TdSpiImpl::OnRspQryInstrument(CThostFtdcInstrumentField* instrument, CThostFtdcRspInfoField* rsp_info, int request_id, bool is_last) {
    static_cast<void>(rsp_info);
    if (TdSession* session_ptr = session()) {
        TdOnInstrumentCallback callback = nullptr;
        {
            std::scoped_lock lock(session_ptr->mutex);
            callback = session_ptr->instrument_callback;
        }
        if (callback == nullptr || instrument == nullptr) {
            return;
        }
        const std::string symbol = normalized_text(instrument->InstrumentID);
        const std::string exchange = normalized_text(instrument->ExchangeID);
        const std::string exchange_inst_id = normalized_text(instrument->ExchangeInstID);
        const std::string product_id = normalized_text(instrument->ProductID);
        const std::string instrument_name = normalized_text(instrument->InstrumentName);
        const std::string expire_date = normalized_text(instrument->ExpireDate);
        const std::string underlying_instr_id = normalized_text(instrument->UnderlyingInstrID);
        const std::string open_date = normalized_text(instrument->OpenDate);
        const std::string create_date = normalized_text(instrument->CreateDate);
        const NativeInstrument snapshot{
            symbol.c_str(),
            exchange.c_str(),
            exchange_inst_id.c_str(),
            product_id.c_str(),
            instrument->PriceTick,
            instrument->VolumeMultiple,
            instrument->MinLimitOrderVolume > 0 ? instrument->MinLimitOrderVolume : 1,
            instrument_name.c_str(),
            expire_date.c_str(),
            static_cast<std::uint8_t>(normalize_enum_value(instrument->ProductClass)),
            instrument->StrikePrice,
            underlying_instr_id.c_str(),
            static_cast<std::uint8_t>(normalize_enum_value(instrument->OptionsType)),
            now_epoch_us(),
            open_date.c_str(),
            create_date.c_str(),
        };
        callback(&snapshot, request_id, is_last ? 1 : 0);
    }
}

void TdSpiImpl::OnRspQryInvestorPosition(CThostFtdcInvestorPositionField* position, CThostFtdcRspInfoField* rsp_info, int request_id, bool is_last) {
    static_cast<void>(rsp_info);
    static_cast<void>(request_id);
    static_cast<void>(is_last);
    if (position == nullptr) {
        return;
    }
    if (TdSession* session_ptr = session()) {
        TdOnPositionCallback callback = nullptr;
        {
            std::scoped_lock lock(session_ptr->mutex);
            callback = session_ptr->position_callback;
        }
        if (callback == nullptr) {
            return;
        }
        const std::string symbol = normalized_text(position->InstrumentID);
        const std::string broker_id = normalized_text(position->BrokerID);
        const std::string investor_id = normalized_text(position->InvestorID);
        const NativePosition snapshot{
            symbol.c_str(),
            broker_id.c_str(),
            investor_id.c_str(),
            normalize_enum_value(position->PosiDirection),
            normalize_enum_value(position->HedgeFlag),
            normalize_enum_value(position->PositionDate),
            position->Position,
            position->YdPosition,
            position->TodayPosition,
            position->PositionCost,
            position->OpenCost,
            position->ExchangeMargin,
            position->UseMargin,
            position->PositionProfit,
            now_epoch_us(),
        };
        callback(&snapshot);
    }
}

void TdSpiImpl::OnRspQryTradingAccount(CThostFtdcTradingAccountField* account, CThostFtdcRspInfoField* rsp_info, int request_id, bool is_last) {
    static_cast<void>(rsp_info);
    static_cast<void>(request_id);
    static_cast<void>(is_last);
    if (account == nullptr) {
        return;
    }
    if (TdSession* session_ptr = session()) {
        TdOnAccountCallback callback = nullptr;
        {
            std::scoped_lock lock(session_ptr->mutex);
            callback = session_ptr->account_callback;
        }
        if (callback == nullptr) {
            return;
        }
        const std::string broker_id = normalized_text(account->BrokerID);
        const std::string account_id = normalized_text(account->AccountID);
        const std::string currency_id = normalized_text(account->CurrencyID);
        const NativeTradingAccount snapshot{
            broker_id.c_str(),
            account_id.c_str(),
            account->Balance,
            account->Available,
            account->WithdrawQuota,
            account->CurrMargin,
            account->FrozenMargin,
            account->Commission,
            account->FrozenCommission,
            account->PositionProfit,
            account->CloseProfit,
            currency_id.c_str(),
            now_epoch_us(),
        };
        callback(&snapshot);
    }
}

void TdSpiImpl::OnRtnOrder(CThostFtdcOrderField* order) {
    if (order == nullptr) {
        return;
    }
    if (TdSession* session_ptr = session()) {
        TdOnExecCallback callback = nullptr;
        SessionIdentity fallback_identity{};
        const std::string order_ref = normalized_text(order->OrderRef);
        const std::string order_sys_id = normalized_text(order->OrderSysID);
        {
            std::scoped_lock lock(session_ptr->mutex);
            callback = session_ptr->exec_callback;
            fallback_identity = current_td_identity_locked(*session_ptr);
            remember_td_order_identity_locked(
                *session_ptr,
                order_ref,
                order_sys_id,
                SessionIdentity{order->FrontID, order->SessionID});
        }
        if (callback == nullptr) {
            return;
        }
        const std::string symbol = normalized_text(order->InstrumentID);
        const std::string status_message = normalized_text(order->StatusMsg);
        const std::string order_id = order_sys_id.empty() ? order_ref : order_sys_id;
        const std::string update_time = normalized_text(order->UpdateTime).empty() ? normalized_text(order->InsertTime) : normalized_text(order->UpdateTime);
        const NativeExec snapshot{
            order_id.c_str(),
            symbol.c_str(),
            order->LimitPrice,
            order->VolumeTotalOriginal,
            normalize_enum_value(order->Direction),
            normalize_enum_value(order->OrderStatus),
            compose_epoch_us(normalized_text(order->InsertDate).empty() ? normalized_text(order->TradingDay) : normalized_text(order->InsertDate), update_time, 0),
            order_ref.c_str(),
            order->FrontID == 0 ? fallback_identity.front_id : order->FrontID,
            order->SessionID == 0 ? fallback_identity.session_id : order->SessionID,
            normalize_enum_value(order->Direction),
            normalize_enum_value(order->CombOffsetFlag[0]),
            normalize_enum_value(order->CombHedgeFlag[0]),
            0,
            0.0,
            0,
            status_message.empty() ? nullptr : status_message.c_str(),
            order->VolumeTotal,
        };
        callback(&snapshot);
    }
}

void TdSpiImpl::OnRtnTrade(CThostFtdcTradeField* trade) {
    if (trade == nullptr) {
        return;
    }
    if (TdSession* session_ptr = session()) {
        TdOnExecCallback callback = nullptr;
        const std::string order_ref = normalized_text(trade->OrderRef);
        const std::string order_sys_id = normalized_text(trade->OrderSysID);
        SessionIdentity identity{};
        {
            std::scoped_lock lock(session_ptr->mutex);
            callback = session_ptr->exec_callback;
            identity = resolve_td_order_identity_locked(*session_ptr, order_ref, order_sys_id);
        }
        if (callback == nullptr) {
            return;
        }
        const std::string symbol = normalized_text(trade->InstrumentID);
        const std::string order_id = order_sys_id.empty() ? order_ref : order_sys_id;
        const NativeExec snapshot{
            order_id.c_str(),
            symbol.c_str(),
            trade->Price,
            trade->Volume,
            normalize_enum_value(trade->Direction),
            0,
            compose_epoch_us(normalized_text(trade->TradeDate).empty() ? normalized_text(trade->TradingDay) : normalized_text(trade->TradeDate), normalized_text(trade->TradeTime), 0),
            order_ref.c_str(),
            identity.front_id,
            identity.session_id,
            normalize_enum_value(trade->Direction),
            normalize_enum_value(trade->OffsetFlag),
            normalize_enum_value(trade->HedgeFlag),
            1,
            trade->Price,
            trade->Volume,
            nullptr,
            0,
        };
        callback(&snapshot);
    }
}

template <typename Session>
Session* checked_handle(void* handle) {
    return handle == nullptr ? nullptr : static_cast<Session*>(handle);
}

}  // namespace

extern "C" void* repo_ctp_md_create(const char* flow_path) {
    auto* session = new MdSession();
    session->flow_path = normalized_text(flow_path);
    session->api = CThostFtdcMdApi::CreateFtdcMdApi(session->flow_path.c_str(), false, false);
    session->spi = new MdSpiImpl(session);
    return session;
}

extern "C" void repo_ctp_md_dispose(void* handle) {
    auto* session = checked_handle<MdSession>(handle);
    if (session == nullptr) {
        return;
    }
    if (session->spi != nullptr) {
        session->spi->Detach();
    }
    if (session->api != nullptr) {
        session->api->RegisterSpi(nullptr);
        session->api->Release();
        session->api = nullptr;
    }
    delete session->spi;
    delete session;
}

extern "C" std::int32_t repo_ctp_md_init(void* handle, const char* front) {
    auto* session = checked_handle<MdSession>(handle);
    if (session == nullptr) {
        return INVALID_HANDLE_CODE;
    }
    std::scoped_lock lock(session->mutex);
    if (session->api == nullptr || session->spi == nullptr) {
        return -1;
    }
    session->front = normalized_text(front);
    if (!session->initialized) {
        session->api->RegisterSpi(session->spi);
        if (!session->front.empty()) {
            session->api->RegisterFront(const_cast<char*>(session->front.c_str()));
        }
        session->api->Init();
        session->initialized = true;
    }
    return 0;
}

extern "C" std::int32_t repo_ctp_md_login(void* handle, const char* broker_id, const char* user_id, const char* password) {
    auto* session = checked_handle<MdSession>(handle);
    if (session == nullptr) {
        return INVALID_HANDLE_CODE;
    }
    {
        std::scoped_lock lock(session->mutex);
        session->broker_id = normalized_text(broker_id);
        session->user_id = normalized_text(user_id);
        session->password = normalized_text(password);
        session->login_requested = true;
    }
    return send_md_login_if_ready(session);
}

extern "C" std::int32_t repo_ctp_md_subscribe(void* handle, void* symbols, std::int32_t symbol_count) {
    auto* session = checked_handle<MdSession>(handle);
    if (session == nullptr) {
        return INVALID_HANDLE_CODE;
    }
    std::scoped_lock lock(session->mutex);
    if (session->api == nullptr || symbols == nullptr || symbol_count <= 0) {
        return session->api == nullptr ? -1 : 0;
    }
    return session->api->SubscribeMarketData(static_cast<char**>(symbols), symbol_count);
}

extern "C" std::int32_t repo_ctp_md_unsubscribe(void* handle, void* symbols, std::int32_t symbol_count) {
    auto* session = checked_handle<MdSession>(handle);
    if (session == nullptr) {
        return INVALID_HANDLE_CODE;
    }
    std::scoped_lock lock(session->mutex);
    if (session->api == nullptr || symbols == nullptr || symbol_count <= 0) {
        return session->api == nullptr ? -1 : 0;
    }
    return session->api->UnSubscribeMarketData(static_cast<char**>(symbols), symbol_count);
}

extern "C" void repo_ctp_md_set_callback(void* handle, MdOnTickCallback callback) {
    if (auto* session = checked_handle<MdSession>(handle)) {
        std::scoped_lock lock(session->mutex);
        session->tick_callback = callback;
    }
}

extern "C" void repo_ctp_md_set_login_callback(void* handle, MdOnLoginCallback callback) {
    if (auto* session = checked_handle<MdSession>(handle)) {
        std::scoped_lock lock(session->mutex);
        session->login_callback = callback;
    }
}

extern "C" void repo_ctp_md_set_front_disconnected_callback(void* handle, MdOnFrontDisconnectedCallback callback) {
    if (auto* session = checked_handle<MdSession>(handle)) {
        std::scoped_lock lock(session->mutex);
        session->disconnect_callback = callback;
    }
}

extern "C" void* repo_ctp_td_create(const char* flow_path) {
    auto* session = new TdSession();
    session->flow_path = normalized_text(flow_path);
    session->api = CThostFtdcTraderApi::CreateFtdcTraderApi(session->flow_path.c_str());
    session->spi = new TdSpiImpl(session);
    return session;
}

extern "C" void repo_ctp_td_dispose(void* handle) {
    auto* session = checked_handle<TdSession>(handle);
    if (session == nullptr) {
        return;
    }
    if (session->spi != nullptr) {
        session->spi->Detach();
    }
    if (session->api != nullptr) {
        session->api->RegisterSpi(nullptr);
        session->api->Release();
        session->api = nullptr;
    }
    delete session->spi;
    delete session;
}

extern "C" std::int32_t repo_ctp_td_init(void* handle, const char* front) {
    auto* session = checked_handle<TdSession>(handle);
    if (session == nullptr) {
        return INVALID_HANDLE_CODE;
    }
    std::scoped_lock lock(session->mutex);
    if (session->api == nullptr || session->spi == nullptr) {
        return -1;
    }
    session->front = normalized_text(front);
    if (!session->initialized) {
        session->api->RegisterSpi(session->spi);
        session->api->SubscribePrivateTopic(THOST_TERT_QUICK);
        session->api->SubscribePublicTopic(THOST_TERT_QUICK);
        if (!session->front.empty()) {
            session->api->RegisterFront(const_cast<char*>(session->front.c_str()));
        }
        session->api->Init();
        session->initialized = true;
    }
    return 0;
}

extern "C" std::int32_t repo_ctp_td_authenticate(void* handle, const char* app_id, const char* auth_code, const char* product_info) {
    auto* session = checked_handle<TdSession>(handle);
    if (session == nullptr) {
        return INVALID_HANDLE_CODE;
    }
    {
        std::scoped_lock lock(session->mutex);
        session->app_id = normalized_text(app_id);
        session->auth_code = normalized_text(auth_code);
        session->product_info = normalized_text(product_info);
        session->auth_requested = true;
    }
    return send_td_auth_or_login_if_ready(session);
}

extern "C" std::int32_t repo_ctp_td_login(void* handle, const char* broker_id, const char* user_id, const char* password) {
    auto* session = checked_handle<TdSession>(handle);
    if (session == nullptr) {
        return INVALID_HANDLE_CODE;
    }
    {
        std::scoped_lock lock(session->mutex);
        session->broker_id = normalized_text(broker_id);
        session->user_id = normalized_text(user_id);
        session->password = normalized_text(password);
        session->login_requested = true;
    }
    return send_td_auth_or_login_if_ready(session);
}

extern "C" std::int32_t repo_ctp_td_confirm_settlement(void* handle) {
    auto* session = checked_handle<TdSession>(handle);
    if (session == nullptr) {
        return INVALID_HANDLE_CODE;
    }
    std::string broker_id;
    std::string investor_id;
    CThostFtdcTraderApi* api = nullptr;
    std::int32_t request_id = 0;
    {
        std::scoped_lock lock(session->mutex);
        if (session->api == nullptr || !session->logged_in) {
            return -1;
        }
        api = session->api;
        broker_id = session->broker_id;
        investor_id = session->user_id;
        request_id = session->next_request_id++;
    }
    CThostFtdcSettlementInfoConfirmField confirm{};
    copy_ctp_text(confirm.BrokerID, broker_id);
    copy_ctp_text(confirm.InvestorID, investor_id);
    return api->ReqSettlementInfoConfirm(&confirm, request_id);
}

extern "C" std::int32_t repo_ctp_td_qry_instrument(void* handle, const char* symbol) {
    auto* session = checked_handle<TdSession>(handle);
    if (session == nullptr) {
        return INVALID_HANDLE_CODE;
    }
    CThostFtdcTraderApi* api = nullptr;
    std::int32_t request_id = 0;
    const std::string instrument_id = normalized_text(symbol);
    {
        std::scoped_lock lock(session->mutex);
        if (session->api == nullptr || !session->logged_in) {
            return -1;
        }
        api = session->api;
        request_id = session->next_request_id++;
    }
    CThostFtdcQryInstrumentField query{};
    copy_ctp_text(query.InstrumentID, instrument_id);
    return api->ReqQryInstrument(&query, request_id);
}

extern "C" std::int32_t repo_ctp_td_qry_position(void* handle) {
    auto* session = checked_handle<TdSession>(handle);
    if (session == nullptr) {
        return INVALID_HANDLE_CODE;
    }
    CThostFtdcTraderApi* api = nullptr;
    std::string broker_id;
    std::string investor_id;
    std::int32_t request_id = 0;
    {
        std::scoped_lock lock(session->mutex);
        if (session->api == nullptr || !session->logged_in) {
            return -1;
        }
        api = session->api;
        broker_id = session->broker_id;
        investor_id = session->user_id;
        request_id = session->next_request_id++;
    }
    CThostFtdcQryInvestorPositionField query{};
    copy_ctp_text(query.BrokerID, broker_id);
    copy_ctp_text(query.InvestorID, investor_id);
    return api->ReqQryInvestorPosition(&query, request_id);
}

extern "C" std::int32_t repo_ctp_td_qry_account(void* handle) {
    auto* session = checked_handle<TdSession>(handle);
    if (session == nullptr) {
        return INVALID_HANDLE_CODE;
    }
    CThostFtdcTraderApi* api = nullptr;
    std::string broker_id;
    std::string investor_id;
    std::int32_t request_id = 0;
    {
        std::scoped_lock lock(session->mutex);
        if (session->api == nullptr || !session->logged_in) {
            return -1;
        }
        api = session->api;
        broker_id = session->broker_id;
        investor_id = session->user_id;
        request_id = session->next_request_id++;
    }
    CThostFtdcQryTradingAccountField query{};
    copy_ctp_text(query.BrokerID, broker_id);
    copy_ctp_text(query.InvestorID, investor_id);
    copy_ctp_text(query.AccountID, investor_id);
    return api->ReqQryTradingAccount(&query, request_id);
}

extern "C" void repo_ctp_td_set_callback(void* handle, TdOnExecCallback callback) {
    if (auto* session = checked_handle<TdSession>(handle)) {
        std::scoped_lock lock(session->mutex);
        session->exec_callback = callback;
    }
}

extern "C" void repo_ctp_td_set_login_callback(void* handle, TdOnLoginCallback callback) {
    if (auto* session = checked_handle<TdSession>(handle)) {
        std::scoped_lock lock(session->mutex);
        session->login_callback = callback;
    }
}

extern "C" void repo_ctp_td_set_front_disconnected_callback(void* handle, TdOnFrontDisconnectedCallback callback) {
    if (auto* session = checked_handle<TdSession>(handle)) {
        std::scoped_lock lock(session->mutex);
        session->disconnect_callback = callback;
    }
}

extern "C" void repo_ctp_td_set_instrument_callback(void* handle, TdOnInstrumentCallback callback) {
    if (auto* session = checked_handle<TdSession>(handle)) {
        std::scoped_lock lock(session->mutex);
        session->instrument_callback = callback;
    }
}

extern "C" void repo_ctp_td_set_position_callback(void* handle, TdOnPositionCallback callback) {
    if (auto* session = checked_handle<TdSession>(handle)) {
        std::scoped_lock lock(session->mutex);
        session->position_callback = callback;
    }
}

extern "C" void repo_ctp_td_set_account_callback(void* handle, TdOnAccountCallback callback) {
    if (auto* session = checked_handle<TdSession>(handle)) {
        std::scoped_lock lock(session->mutex);
        session->account_callback = callback;
    }
}