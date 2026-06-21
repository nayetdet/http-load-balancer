from __future__ import annotations

import requests
from loguru import logger
from http_target_discovery.providers.base_provider import BaseProvider
from http_target_discovery.settings import settings

class SynchronizationManager:
    _session: requests.Session | None = None
    _last_seen: tuple[tuple[str, int, int], ...] | None = None
    _last_sent: tuple[tuple[str, int, int], ...] | None = None

    @classmethod
    def synchronize(cls, provider: type[BaseProvider]) -> None:
        try:
            targets = tuple(sorted((target.ip, target.port, target.weight) for target in provider.targets()))
        except Exception:
            logger.exception("Failed to discover targets")
            return

        session = cls._session
        if session is None:
            raise RuntimeError("SynchronizationManager._session must be set before synchronize()")

        if cls._last_seen != targets:
            logger.info("Target set changed: {}", targets)

        if cls._last_sent != targets:
            try:
                response = session.post(
                    url=settings.lb_reload_url,
                    json={
                        "targets": [
                            {"ip": ip, "port": port, "weight": weight}
                            for ip, port, weight in targets
                        ]
                    },
                    timeout=settings.request_timeout_seconds
                )

                response.raise_for_status()
            except (requests.RequestException, OSError):
                logger.exception("Failed to reload load balancer")
            else:
                cls._last_sent = targets
                logger.info("Reloaded load balancer with {} targets", len(targets))

        cls._last_seen = targets

    @classmethod
    def close(cls) -> None:
        session = cls._session
        if session is not None:
            session.close()
            cls._session = None
