from loguru import logger
from http_load_balancer.servers.base_server import BaseServer
from http_load_balancer.core.target_manager import TargetManager
from http_load_balancer.servers.proxy_server import ProxyServer
from http_load_balancer.settings import settings

def main() -> None:
    TargetManager.reload()
    proxy_server: BaseServer = ProxyServer(
        host=settings.proxy_host,
        port=settings.proxy_port,
        backlog=settings.backlog,
        buffer_size=settings.buffer_size
    )

    logger.info("Proxy running on {}:{} with {}", settings.proxy_host, settings.proxy_port, TargetManager.algorithm().__name__)
    proxy_server.serve()
