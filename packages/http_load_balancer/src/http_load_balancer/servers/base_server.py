from __future__ import annotations

import socket
import threading
from http_load_balancer.settings import settings
from http_load_balancer.servers.handlers.handler import Handler

class BaseServer:
    def __init__(
        self,
        host: str = settings.proxy_host,
        port: int = settings.proxy_port,
        backlog: int = settings.backlog,
        buffer_size: int = settings.buffer_size
    ) -> None:
        self._host = host
        self._port = port
        self._backlog = backlog
        self._buffer_size = buffer_size
        self._handlers: list[Handler] = self._load_handlers()

    def serve(self) -> threading.Thread:
        def run() -> None:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
                server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                server.bind((self._host, self._port))
                server.listen(self._backlog)
                while True:
                    client_socket, _ = server.accept()
                    threading.Thread(
                        target=self._handle_connection,
                        args=(client_socket,),
                        daemon=True
                    ).start()

        thread = threading.Thread(target=run, daemon=True)
        thread.start()
        return thread

    def _load_handlers(self) -> list[Handler]:
        handlers: list[Handler] = []
        handler_names: set[str] = set()
        for cls in reversed(type(self).__mro__):
            for name, attribute in cls.__dict__.items():
                if name in handler_names or not getattr(attribute, "_is_server_handler", False):
                    continue

                handler_names.add(name)
                handlers.append(getattr(self, name))

        return handlers

    def _handle_connection(self, client_socket: socket.socket) -> None:
        with client_socket:
            request = client_socket.recv(self._buffer_size)
            if not request:
                return

            for handler in self._handlers:
                if handler(client_socket, request):
                    return
