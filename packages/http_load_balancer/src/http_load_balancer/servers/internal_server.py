from __future__ import annotations

import json
import socket
from http import HTTPMethod, HTTPStatus
from http_load_balancer.core.target_manager import TargetManager
from http_load_balancer.schemas.routing_schema import RoutingSchema
from http_load_balancer.servers.base_server import BaseServer
from http_load_balancer.servers.handlers.http_handler import http_handler
from http_load_balancer.utils.http_utils import HTTPUtils
from http_load_balancer.settings import settings

class InternalServer(BaseServer):
    def __init__(
        self,
        host: str = settings.host,
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

    @http_handler(path="/targets", method=HTTPMethod.GET)
    def get_targets(self, client_socket: socket.socket, request: bytes) -> None:
        try:
            algorithm_strategy = TargetManager.algorithm_strategy()
        except RuntimeError:
            client_socket.sendall(HTTPUtils.response(HTTPStatus.SERVICE_UNAVAILABLE))
            return

        routing_payload = RoutingSchema(
            version=TargetManager._version,
            algorithm_strategy=algorithm_strategy,
            targets=sorted(TargetManager.targets(), key=lambda target: (target.ip, target.port))
        )

        client_socket.sendall(
            HTTPUtils.response(
                status=HTTPStatus.OK,
                body=json.dumps(routing_payload.model_dump(mode="json")).encode("utf-8"),
                headers={
                    "Content-Type": "application/json"
                }
            )
        )

    @http_handler(path="/targets", method=HTTPMethod.PUT)
    def update_targets(self, client_socket: socket.socket, request: bytes) -> None:
        try:
            payload = RoutingSchema.model_validate(json.loads(body.decode("utf-8")) if (body := HTTPUtils.body(request)) else {})
        except Exception:
            client_socket.sendall(HTTPUtils.response(HTTPStatus.BAD_REQUEST))
            return

        TargetManager.reload(payload)
        client_socket.sendall(HTTPUtils.response(HTTPStatus.OK))

    @http_handler()
    def not_found(self, client_socket: socket.socket, request: bytes) -> None:
        client_socket.sendall(HTTPUtils.response(HTTPStatus.NOT_FOUND))
