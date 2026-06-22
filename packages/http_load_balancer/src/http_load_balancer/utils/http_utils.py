from http import HTTPStatus

class HTTPUtils:
    @staticmethod
    def response(status: HTTPStatus, body: bytes = b"", headers: dict[str, str] | None = None) -> bytes:
        return (
            f"HTTP/1.1 {status.value} {status.phrase}\r\n"
            f"{''.join(f'{key}: {value}\r\n' for key, value in headers.items()) if headers is not None else ''}"
            f"Content-Length: {len(body)}\r\n"
            "Connection: close\r\n\r\n"
        ).encode("utf-8") + body

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

            _, value = line.split(b":", 1)
            try:
                return int(value.strip())
            except ValueError:
                return 0
        return 0

    @staticmethod
    def headers_end(request: bytes) -> int:
        return request.find(b"\r\n\r\n")
