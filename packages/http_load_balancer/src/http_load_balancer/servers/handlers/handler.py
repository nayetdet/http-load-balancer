import socket
from collections.abc import Callable

Handler = Callable[[socket.socket, bytes], bool]
