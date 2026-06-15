from __future__ import annotations

import asyncio
import hashlib
from dataclasses import dataclass
from urllib.parse import urlparse


@dataclass(frozen=True)
class FrontProxyConfig:
    channel: str
    listen_host: str
    listen_port: int
    remote_front: str


@dataclass
class FrontProxyState:
    config: FrontProxyConfig
    accepting: bool = True
    connection_count: int = 0
    drop_count: int = 0


def _front_fingerprint(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:12]


def build_redacted_proxy_status(state: FrontProxyState) -> dict[str, object]:
    return {
        "channel": state.config.channel,
        "listen": f"{state.config.listen_host}:{state.config.listen_port}",
        "remote_front_fingerprint": _front_fingerprint(state.config.remote_front),
        "accepting": state.accepting,
        "connection_count": state.connection_count,
        "drop_count": state.drop_count,
    }


def _parse_tcp_front(front: str) -> tuple[str, int]:
    parsed = urlparse(front)
    if parsed.scheme != "tcp" or not parsed.hostname or not parsed.port:
        raise ValueError(f"unsupported_front={front}")
    return parsed.hostname, int(parsed.port)


class ControlledFrontProxy:
    def __init__(self, config: FrontProxyConfig) -> None:
        self.state = FrontProxyState(config=config)
        self._server: asyncio.AbstractServer | None = None
        self._writers: set[asyncio.StreamWriter] = set()

    @property
    def listen_port(self) -> int:
        if self._server is None or not self._server.sockets:
            return self.state.config.listen_port
        return int(self._server.sockets[0].getsockname()[1])

    async def start(self) -> None:
        self._server = await asyncio.start_server(
            self._handle_client,
            self.state.config.listen_host,
            self.state.config.listen_port,
        )

    async def stop(self) -> None:
        self.drop_connections()
        if self._server is not None:
            self._server.close()
            await self._server.wait_closed()
            self._server = None

    def drop_connections(self) -> None:
        self.state.accepting = False
        self.state.drop_count += 1
        for writer in list(self._writers):
            writer.close()

    def restore_accepting(self) -> None:
        self.state.accepting = True

    async def _handle_client(
        self,
        client_reader: asyncio.StreamReader,
        client_writer: asyncio.StreamWriter,
    ) -> None:
        self._writers.add(client_writer)
        self.state.connection_count += 1
        if not self.state.accepting:
            await self._close_writer(client_writer)
            self._writers.discard(client_writer)
            return
        host, port = _parse_tcp_front(self.state.config.remote_front)
        remote_reader, remote_writer = await asyncio.open_connection(host, port)
        self._writers.add(remote_writer)
        try:
            await asyncio.gather(
                self._pipe(client_reader, remote_writer),
                self._pipe(remote_reader, client_writer),
            )
        finally:
            await self._close_writer(client_writer)
            await self._close_writer(remote_writer)
            self._writers.discard(client_writer)
            self._writers.discard(remote_writer)

    async def _pipe(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        while True:
            data = await reader.read(65536)
            if not data:
                break
            writer.write(data)
            await writer.drain()

    async def _close_writer(self, writer: asyncio.StreamWriter) -> None:
        writer.close()
        try:
            await writer.wait_closed()
        except OSError:
            pass
