from __future__ import annotations

import socket
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from http_load_balancer.servers.base_server import BaseServer
from http_load_balancer.servers.base_server import server_handler


class BaseServerHandlersTest(unittest.TestCase):
    def test_handlers_run_in_order_until_one_handles_request(self) -> None:
        calls: list[str] = []
        request = b"GET /health HTTP/1.1\r\nHost: example.com\r\n\r\n"

        class TestServer(BaseServer):
            @server_handler
            def first_handler(self, client_socket: socket.socket, incoming_request: bytes) -> bool:
                calls.append(f"first:{incoming_request.decode()}")
                return False

            @server_handler
            def second_handler(self, client_socket: socket.socket, incoming_request: bytes) -> bool:
                calls.append(f"second:{incoming_request.decode()}")
                client_socket.sendall(b"HTTP/1.1 204 No Content\r\nContent-Length: 0\r\n\r\n")
                return True

        server = TestServer(buffer_size=1024)

        server_socket, client_socket = socket.socketpair()
        try:
            client_socket.sendall(request)
            server._handle_connection(server_socket)
            response = client_socket.recv(1024)
            self.assertEqual(response, b"HTTP/1.1 204 No Content\r\nContent-Length: 0\r\n\r\n")
            self.assertEqual(
                calls,
                [
                    f"first:{request.decode()}",
                    f"second:{request.decode()}",
                ],
            )
        finally:
            server_socket.close()
            client_socket.close()


if __name__ == "__main__":
    unittest.main()
