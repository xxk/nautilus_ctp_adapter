import asyncio
import json
from pathlib import Path

from scripts.ctp_controlled_reconnect_harness import build_proxy_config_payload
from scripts.ctp_controlled_front_proxy import (
    ControlledFrontProxy,
    FrontProxyConfig,
    FrontProxyState,
    build_redacted_proxy_status,
)


def test_proxy_status_redacts_remote_front_and_tracks_state() -> None:
    config = FrontProxyConfig(
        channel="td",
        listen_host="127.0.0.1",
        listen_port=39001,
        remote_front="tcp://trading.openctp.cn:30001",
    )
    state = FrontProxyState(config=config, accepting=True, connection_count=2, drop_count=1)

    status = build_redacted_proxy_status(state)

    assert status == {
        "channel": "td",
        "listen": "127.0.0.1:39001",
        "remote_front_fingerprint": "b763f35d90f7",
        "accepting": True,
        "connection_count": 2,
        "drop_count": 1,
    }
    assert "trading.openctp.cn" not in str(status)
    assert "30001" not in str(status)


def test_controlled_proxy_can_drop_and_restore_connections() -> None:
    async def scenario() -> None:
        received: list[bytes] = []

        async def handle_echo(
            reader: asyncio.StreamReader,
            writer: asyncio.StreamWriter,
        ) -> None:
            data = await reader.read(16)
            received.append(data)
            writer.write(data)
            await writer.drain()
            writer.close()
            await writer.wait_closed()

        echo_server = await asyncio.start_server(handle_echo, "127.0.0.1", 0)
        echo_port = echo_server.sockets[0].getsockname()[1]
        proxy = ControlledFrontProxy(
            FrontProxyConfig(
                channel="md",
                listen_host="127.0.0.1",
                listen_port=0,
                remote_front=f"tcp://127.0.0.1:{echo_port}",
            )
        )
        await proxy.start()
        proxy_port = proxy.listen_port

        reader, writer = await asyncio.open_connection("127.0.0.1", proxy_port)
        writer.write(b"ping")
        await writer.drain()
        assert await reader.read(4) == b"ping"
        writer.close()
        await writer.wait_closed()

        proxy.drop_connections()
        proxy.restore_accepting()

        assert received == [b"ping"]
        assert proxy.state.drop_count == 1
        await proxy.stop()
        echo_server.close()
        await echo_server.wait_closed()

    asyncio.run(scenario())


def test_proxy_config_payload_rewrites_only_fronts_and_preserves_guardrails(
    tmp_path: Path,
) -> None:
    source = tmp_path / "source.json"
    source.write_text(
        json.dumps(
            {
                "BrokerID": "9999",
                "UserID": "19053",
                "Password": "secret",
                "Pricer": "tcp://trading.openctp.cn:30011",
                "Host": "tcp://trading.openctp.cn:30001",
                "ExecutionGuardrails": {"AllowLiveOrderSmoke": False},
            }
        ),
        encoding="utf-8",
    )

    payload = build_proxy_config_payload(source, md_port=39011, td_port=39001)

    assert payload["Pricer"] == "tcp://127.0.0.1:39011"
    assert payload["Host"] == "tcp://127.0.0.1:39001"
    assert payload["ExecutionGuardrails"]["AllowLiveOrderSmoke"] is False
    assert payload["Password"] == "secret"
