from __future__ import annotations

import socket
from collections.abc import Callable
from functools import wraps
from http import HTTPMethod
from typing import cast
from http_load_balancer.servers.handlers.handler import Handler

def http_handler(
    path: str | None = None,
    method: HTTPMethod | None = None
) -> Callable[[Callable[[object, socket.socket, bytes], None]], Handler]:
    normalized_method: str | None = method.value if method else None
    normalized_path: str | None = path if path else None

    def decorator(fn: Callable[[object, socket.socket, bytes], None]) -> Handler:
        @wraps(fn)
        def wrapper(self: object, client_socket: socket.socket, request: bytes) -> bool:
            if normalized_method is not None or normalized_path is not None:
                request_line: str = request.split(b"\r\n", 1)[0].decode("ascii", errors="ignore")
                parts: list[str] = request_line.split(" ")
                request_method: str = parts[0].upper() if parts and parts[0] else ""
                request_path: str = parts[1] if len(parts) > 1 else ""

                if normalized_method is not None and request_method != normalized_method:
                    return False
                if normalized_path is not None and request_path != normalized_path:
                    return False

            fn(self, client_socket, request)
            return True

        setattr(wrapper, "_is_server_handler", True)
        setattr(wrapper, "_http_path", normalized_path)
        setattr(wrapper, "_http_method", normalized_method)
        return cast(Handler, wrapper)

    return decorator
