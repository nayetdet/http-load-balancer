from __future__ import annotations

import socket
from http import HTTPMethod, HTTPStatus
from http_load_balancer.core.target_manager import TargetManager
from http_load_balancer.servers.base_server import BaseServer
from http_load_balancer.servers.handlers.http_handler import http_handler
from http_load_balancer.settings import settings
from http_load_balancer.utils.http_utils import HTTPUtils

class InternalServer(BaseServer):
    def __init__(
        self,
        host: str = settings.internal_host,
        port: int = settings.internal_port,
        backlog: int = settings.backlog,
        buffer_size: int = settings.buffer_size
    ) -> None:
        super().__init__(
            host=host,
            port=port,
            backlog=backlog,
            buffer_size=buffer_size
        )

    @http_handler(path="/reload", method=HTTPMethod.POST, status=HTTPStatus.OK)
    def handle_reload_request(self, client_socket: socket.socket, request: bytes) -> None:
        TargetManager.reload()

    @http_handler()
    def handle_not_found_request(self, client_socket: socket.socket, request: bytes) -> None:
        client_socket.sendall(HTTPUtils.build_empty_response(HTTPStatus.NOT_FOUND))
