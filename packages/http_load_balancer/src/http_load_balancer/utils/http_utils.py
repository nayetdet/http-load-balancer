from http import HTTPStatus

class HTTPUtils:
    @staticmethod
    def empty_response(status: HTTPStatus) -> bytes:
        return f"HTTP/1.1 {status.value} {status.phrase}\r\nContent-Length: 0\r\nConnection: close\r\n\r\n".encode()

    @staticmethod
    def body(request: bytes) -> bytes:
        separator: bytes = b"\r\n\r\n"
        if separator not in request:
            return b""
        return request.split(separator, 1)[1]

    @staticmethod
    def content_length(headers: bytes) -> int:
        for line in headers.split(b"\r\n")[1:]:
            if not line.lower().startswith(b"content-length:"):
                continue

            _, raw_value = line.split(b":", 1)
            try:
                return int(raw_value.strip())
            except ValueError:
                return 0

        return 0

    @staticmethod
    def headers_end(request: bytes) -> int:
        return request.find(b"\r\n\r\n")
