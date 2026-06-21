from http import HTTPStatus

class HTTPUtils:
    @staticmethod
    def build_empty_response(status: HTTPStatus) -> bytes:
        return f"HTTP/1.1 {status.value} {status.phrase}\r\nContent-Length: 0\r\nConnection: close\r\n\r\n".encode()
