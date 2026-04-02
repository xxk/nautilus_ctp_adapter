import json
from pathlib import Path

from nautilus_ctp_adapter import __version__
from nautilus_ctp_adapter.adapters.ctp import CtpAdapterConfig, CtpExecutionClient
from nautilus_ctp_adapter.adapters.ctp.factory import build_ctp_stack
from nautilus_ctp_adapter.native.loader import (
    BOOTSTRAP_MANAGED_DLLS,
    REQUIRED_NATIVE_DLLS,
    candidate_managed_paths,
    candidate_native_paths,
)
from nautilus_ctp_adapter.native.md_ctypes import CtpMdApi
from nautilus_ctp_adapter.native.td_ctypes import CtpTdApi
from nautilus_ctp_adapter.native.manifest import (
    OPTIONAL_COMPAT_DLLS,
    REPO_OWNED_CTP_NATIVE_EXPORTS,
    describe_native_pack,
)
from nautilus_ctp_adapter.runtime import (
    CtpMarketRuntime,
    CtpOrderState,
    CtpRuntimeBridge,
    CtpRuntimeCommand,
    CtpRuntimeCommandKind,
    CtpRuntimeEvent,
    CtpRuntimeEventKind,
    CtpSessionRuntime,
    CtpSessionState,
    CtpTradingRuntime,
)


def test_package_imports() -> None:
    assert __version__ == "0.1.0"


def test_factory_builds_minimal_stack() -> None:
    stack = build_ctp_stack(CtpAdapterConfig())
    assert isinstance(stack["runtime_bridge"], CtpRuntimeBridge)
    assert "instrument_provider" in stack
    assert "data_client" in stack
    assert "execution_client" in stack
    assert stack["data_client"].runtime_bridge is stack["runtime_bridge"]
    assert stack["execution_client"].runtime_bridge is stack["runtime_bridge"]


def test_runtime_models_are_platform_neutral() -> None:
    command = CtpRuntimeCommand(kind=CtpRuntimeCommandKind.CONNECT)
    event = CtpRuntimeEvent(kind=CtpRuntimeEventKind.CONNECTED)
    bridge = CtpRuntimeBridge()
    bridge.push_event(event)

    assert command.kind is CtpRuntimeCommandKind.CONNECT
    assert bridge.next_event() == event


def test_runtime_bridge_submit_and_drain_contract() -> None:
    bridge = CtpRuntimeBridge()
    command_1 = CtpRuntimeCommand(kind=CtpRuntimeCommandKind.CONNECT, request_id="req-1")
    command_2 = CtpRuntimeCommand(kind=CtpRuntimeCommandKind.QUERY_ACCOUNT, request_id="req-2")
    event_1 = CtpRuntimeEvent(kind=CtpRuntimeEventKind.CONNECTED, request_id="req-1")
    event_2 = CtpRuntimeEvent(kind=CtpRuntimeEventKind.ACCOUNT, request_id="req-2")

    bridge.submit_command(command_1)
    bridge.submit_command(command_2)
    bridge.push_event(event_1)
    bridge.push_event(event_2)

    assert bridge.pending_command_count == 2
    assert bridge.pending_event_count == 2
    assert bridge.drain_submitted_commands(limit=1) == [command_1]
    assert bridge.pending_command_count == 1
    assert bridge.drain_events(limit=1) == [event_1]
    assert bridge.pending_event_count == 1
    assert bridge.drain_submitted_commands() == [command_2]
    assert bridge.drain_events() == [event_2]
    assert bridge.pending_command_count == 0
    assert bridge.pending_event_count == 0


def test_session_and_market_runtime_track_minimal_state() -> None:
    session = CtpSessionRuntime()
    market = CtpMarketRuntime()

    connect = CtpRuntimeCommand(kind=CtpRuntimeCommandKind.CONNECT)
    subscribe = CtpRuntimeCommand(
        kind=CtpRuntimeCommandKind.SUBSCRIBE_MARKET_DATA,
        venue_symbol="rb2512",
        exchange_id="SHFE",
    )
    connected = CtpRuntimeEvent(kind=CtpRuntimeEventKind.CONNECTED)
    logged_in = CtpRuntimeEvent(kind=CtpRuntimeEventKind.LOGIN_SUCCEEDED)

    session.on_command(connect)
    market.on_command(subscribe)
    session.on_event(connected)
    session.on_event(logged_in)

    assert session.state is CtpSessionState.LOGGED_IN
    assert session.is_connected is True
    assert market.subscription_count == 1
    assert market.is_subscribed("rb2512", "SHFE") is True


def test_trading_runtime_tracks_order_state_transitions() -> None:
    trading = CtpTradingRuntime()
    submit = CtpRuntimeCommand(
        kind=CtpRuntimeCommandKind.SUBMIT_ORDER,
        client_order_id="ord-1",
    )
    working = CtpRuntimeEvent(
        kind=CtpRuntimeEventKind.ORDER,
        client_order_id="ord-1",
    )
    filled = CtpRuntimeEvent(
        kind=CtpRuntimeEventKind.TRADE,
        client_order_id="ord-1",
    )

    trading.on_command(submit)
    assert trading.state_for("ord-1") is CtpOrderState.PENDING_SUBMIT

    trading.on_event(working)
    assert trading.state_for("ord-1") is CtpOrderState.WORKING

    trading.on_event(filled)
    assert trading.state_for("ord-1") is CtpOrderState.FILLED
    assert trading.tracked_order_count == 1


def test_bridge_updates_trading_runtime_automatically() -> None:
    bridge = CtpRuntimeBridge()

    bridge.submit_command(
        CtpRuntimeCommand(
            kind=CtpRuntimeCommandKind.SUBMIT_ORDER,
            client_order_id="ord-2",
        )
    )
    assert bridge.trading.state_for("ord-2") is CtpOrderState.PENDING_SUBMIT

    bridge.push_event(
        CtpRuntimeEvent(
            kind=CtpRuntimeEventKind.ORDER,
            client_order_id="ord-2",
        )
    )
    assert bridge.trading.state_for("ord-2") is CtpOrderState.WORKING


def test_ctp_config_loads_repo_example(tmp_path: Path) -> None:
    source = Path(__file__).resolve().parents[1] / "cfgs" / "ctp.live.example.json"
    payload = json.loads(source.read_text(encoding="utf-8"))
    payload["Password"] = "secret"
    local_path = tmp_path / "ctp.live.local.json"
    local_path.write_text(json.dumps(payload), encoding="utf-8")

    config = CtpAdapterConfig.from_json_file(local_path)

    assert config.user_id == "025292"
    assert config.md_front == "tcp://md-front.example:51213"
    assert config.td_front == "tcp://td-front.example:51205"
    assert config.instruments == ["rb2610"]
    assert config.execution_guardrails.enabled is True
    assert config.execution_guardrails.allowed_instruments == ["c2609"]
    assert config.execution_guardrails.max_order_qty == 1
    assert config.execution_guardrails.max_net_position == 5
    assert config.execution_guardrails.max_submit_per_minute == 10
    assert config.execution_guardrails.price_mode == "best_level_1"
    assert config.validate() == []


def test_ctp_config_accepts_myvnpy_connect_ctp_shape() -> None:
    payload = {
        "用户名": "025292",
        "密码": "secret",
        "经纪商代码": "0155",
        "交易服务器": "106.75.173.28:51205",
        "行情服务器": "106.75.173.28:51213",
        "产品名称": "client_iq_3.6.2",
        "授权编码": "RFLEXUGHCKIKWGPC",
        "柜台环境": "实盘",
        "service": "iQuant",
        "instruments": ["rb2610"],
    }

    config = CtpAdapterConfig.from_dict(payload)

    assert config.user_id == "025292"
    assert config.broker_id == "0155"
    assert config.auth_code == "RFLEXUGHCKIKWGPC"
    assert config.app_id == "client_iq_3.6.2"
    assert config.product_info == "iQuant"
    assert config.md_front == "tcp://106.75.173.28:51213"
    assert config.td_front == "tcp://106.75.173.28:51205"
    assert config.validate() == []


def test_execution_precheck_enforces_real_account_guardrails() -> None:
    config = CtpAdapterConfig.from_dict(
        {
            "UserID": "025292",
            "BrokerID": "0155",
            "Password": "secret",
            "Pricer": "tcp://md-front.example:51213",
            "Host": "tcp://td-front.example:51205",
            "Instruments": ["rb2610"],
            "ExecutionGuardrails": {
                "Enabled": True,
                "AllowedInstruments": ["c2609"],
                "MaxOrderQty": 1,
                "MaxNetPosition": 5,
                "MaxSubmitPerMinute": 10,
                "PriceMode": "best_level_1",
            },
        }
    )
    client = CtpExecutionClient(config)

    rejected = client.precheck_debug_order(
        instrument_id="rb2610",
        side="BUY",
        quantity=2,
        projected_net_position=6,
        submit_count_last_minute=10,
        best_bid=3200.0,
        best_ask=3201.0,
    )

    assert rejected.allowed is False
    assert any("instrument rb2610" in item for item in rejected.violations)
    assert any("quantity 2" in item for item in rejected.violations)
    assert any("projected_net_position 6" in item for item in rejected.violations)
    assert any("submit_count_last_minute 10" in item for item in rejected.violations)


def test_execution_precheck_uses_best_level_1_price() -> None:
    config = CtpAdapterConfig.from_dict(
        {
            "UserID": "025292",
            "BrokerID": "0155",
            "Password": "secret",
            "Pricer": "tcp://md-front.example:51213",
            "Host": "tcp://td-front.example:51205",
            "Instruments": ["rb2610"],
            "ExecutionGuardrails": {
                "Enabled": True,
                "AllowedInstruments": ["c2609"],
                "MaxOrderQty": 1,
                "MaxNetPosition": 5,
                "MaxSubmitPerMinute": 10,
                "PriceMode": "best_level_1",
            },
        }
    )
    client = CtpExecutionClient(config)

    buy = client.precheck_debug_order(
        instrument_id="c2609",
        side="BUY",
        quantity=1,
        projected_net_position=5,
        submit_count_last_minute=9,
        best_bid=1820.0,
        best_ask=1821.0,
    )
    sell = client.precheck_debug_order(
        instrument_id="c2609",
        side="SELL",
        quantity=1,
        projected_net_position=4,
        submit_count_last_minute=9,
        best_bid=1819.0,
        best_ask=1820.0,
    )

    assert buy.allowed is True
    assert buy.selected_price == 1821.0
    assert sell.allowed is True
    assert sell.selected_price == 1819.0


def test_native_loader_candidates_cover_repo_owned_pack() -> None:
    root = Path(__file__).resolve().parents[1]
    native_paths = candidate_native_paths(root)
    managed_paths = candidate_managed_paths(root)

    assert root / "vendor" / "ctp" / "bin" in native_paths
    assert root / "vendor" / "ctp" / "bin" in managed_paths
    assert "ctp_native.dll" in REQUIRED_NATIVE_DLLS
    assert "CTPProviderSwig.dll" in BOOTSTRAP_MANAGED_DLLS


def test_native_manifest_tracks_repo_owned_abi_and_pack_layout() -> None:
    root = Path(__file__).resolve().parents[1]
    manifest = describe_native_pack(root)
    export_symbols = [item.symbol for item in REPO_OWNED_CTP_NATIVE_EXPORTS]

    assert manifest["vendor_dir"] == root / "vendor" / "ctp"
    assert manifest["bin_dir"] == root / "vendor" / "ctp" / "bin"
    assert "ctp_native.dll" in manifest["required_native_dlls"]
    assert "thosttraderapi.dll" in manifest["optional_compat_dlls"]
    assert "MdCreate" in export_symbols
    assert "TdOrderSend" in export_symbols
    assert "MdSetLoginCallback" in manifest["repo_owned_exports"]
    assert OPTIONAL_COMPAT_DLLS == ("thostmduserapi.dll", "thosttraderapi.dll")


def test_ctypes_md_api_loads_repo_owned_md_exports() -> None:
    root = Path(__file__).resolve().parents[1]
    api = CtpMdApi.load(root)
    flow_path = root / "var" / "test_md_api_flow"
    flow_path.mkdir(parents=True, exist_ok=True)
    handle = api.create(flow_path)
    try:
        assert handle > 0
    finally:
        api.dispose(handle)


def test_ctypes_td_api_loads_repo_owned_td_exports() -> None:
    root = Path(__file__).resolve().parents[1]
    api = CtpTdApi.load(root)
    flow_path = root / "var" / "test_td_api_flow"
    flow_path.mkdir(parents=True, exist_ok=True)
    handle = api.create(flow_path)
    try:
        assert handle > 0
    finally:
        api.dispose(handle)


def test_data_client_bootstrap_submits_md_connect_and_subscribe_commands() -> None:
    config = CtpAdapterConfig.from_dict(
        {
            "BrokerID": "0155",
            "UserID": "025292",
            "Password": "secret",
            "AppID": "client_iq_3.6.2",
            "AuthCode": "RFLEXUGHCKIKWGPC",
            "Pricer": "tcp://106.75.173.28:51213",
            "Host": "tcp://106.75.173.28:51205",
            "Instruments": ["rb2610"],
        }
    )
    stack = build_ctp_stack(config)
    data_client = stack["data_client"]
    bridge = stack["runtime_bridge"]

    state = data_client.bootstrap_market_data_mainline()
    commands = bridge.drain_submitted_commands()

    assert state.started is True
    assert state.connect_request_id == "md-connect-1"
    assert state.subscribe_request_ids == ["md-subscribe-2"]
    assert len(commands) == 2
    assert commands[0].kind is CtpRuntimeCommandKind.CONNECT
    assert commands[0].payload["channel"] == "md"
    assert commands[0].payload["front"] == "tcp://106.75.173.28:51213"
    assert commands[1].kind is CtpRuntimeCommandKind.SUBSCRIBE_MARKET_DATA
    assert commands[1].venue_symbol == "rb2610"


def test_data_client_live_callbacks_push_bridge_events() -> None:
    config = CtpAdapterConfig.from_dict(
        {
            "BrokerID": "0155",
            "UserID": "025292",
            "Password": "secret",
            "Pricer": "tcp://106.75.173.28:51213",
            "Host": "tcp://106.75.173.28:51205",
            "Instruments": ["rb2610"],
        }
    )
    stack = build_ctp_stack(config)
    data_client = stack["data_client"]
    bridge = stack["runtime_bridge"]
    state: dict[str, object] = {}

    class LoginResponse:
        success = True
        error_id = 0
        error_message = ""
        front_id = 1
        session_id = 2
        max_order_ref = 3

    class Tick:
        symbol = "rb2610"
        last = 3127.0
        bid = 3126.0
        ask = 3127.0
        ts_epoch_us = 1775094554636325

    data_client._on_md_login_callback(LoginResponse(), state)
    data_client._on_md_tick_callback(Tick(), state)
    events = bridge.drain_events()

    assert [event.kind for event in events] == [
        CtpRuntimeEventKind.LOGIN_SUCCEEDED,
        CtpRuntimeEventKind.TICK,
    ]
    assert events[1].venue_symbol == "rb2610"
    assert events[1].payload["last"] == "3127.0"


def test_execution_client_live_callbacks_push_bridge_events() -> None:
    config = CtpAdapterConfig.from_dict(
        {
            "BrokerID": "0155",
            "UserID": "025292",
            "Password": "secret",
            "AppID": "client_iq_3.6.2",
            "AuthCode": "RFLEXUGHCKIKWGPC",
            "ProductInfo": "iQuant",
            "Pricer": "tcp://106.75.173.28:51213",
            "Host": "tcp://106.75.173.28:51205",
            "Instruments": ["rb2610"],
        }
    )
    stack = build_ctp_stack(config)
    execution_client = stack["execution_client"]
    bridge = stack["runtime_bridge"]
    state: dict[str, object] = {"disconnects": []}

    class LoginResponse:
        success = True
        error_id = 0
        error_message = ""
        front_id = 11
        session_id = 22
        max_order_ref = 1

    execution_client._on_td_login_callback(LoginResponse(), state)
    execution_client._on_td_disconnect(4097, state)
    events = bridge.drain_events()

    assert [event.kind for event in events] == [
        CtpRuntimeEventKind.LOGIN_SUCCEEDED,
        CtpRuntimeEventKind.DISCONNECTED,
    ]
    assert events[0].payload["channel"] == "td"
    assert events[1].message == "td_disconnected:4097"
