from __future__ import annotations

import requests
from loguru import logger
from requests import Response
from pydantic import ValidationError
from http_target_discovery.providers.base_provider import BaseProvider
from http_target_discovery.schemas.target_schema import TargetSchema
from http_target_discovery.schemas.routing_schema import RoutingSchema
from http_target_discovery.settings import settings

class SynchronizationManager:
    _session: requests.Session | None = None
    _last_seen: tuple[tuple[str, int, int], ...] | None = None
    _last_sent: tuple[tuple[str, int, int], ...] | None = None

    @classmethod
    def session(cls) -> requests.Session:
        session: requests.Session | None = cls._session
        if session is None:
            session = cls._session = requests.Session()
        return session

    @classmethod
    def synchronize(cls, provider: type[BaseProvider]) -> None:
        session: requests.Session = cls.session()
        try:
            provider_targets: list[TargetSchema] = list(provider.targets())
        except Exception:
            logger.exception("Failed to discover targets")
            return

        routing: RoutingSchema = RoutingSchema()
        try:
            routing_response: Response = session.get(settings.lb_targets_url, timeout=settings.request_timeout_seconds)
            routing_response.raise_for_status()
            routing = RoutingSchema.model_validate(routing_response.json())
        except (requests.RequestException, OSError, ValidationError):
            logger.exception("Failed to fetch current routing payload")

        target_weights_by_key: dict[str, int] = {target.key(): target.weight for target in routing.targets}
        targets: list[TargetSchema] = [
            target.model_copy(update={"weight": target_weights_by_key.get(target.key(), target.weight)})
            for target in provider_targets
        ]

        if routing.targets and not any(target.key() in target_weights_by_key for target in provider_targets):
            targets = [
                target.model_copy(
                    update={
                        "weight": (
                            routing.targets[target_index].weight
                            if target_index < len(routing.targets)
                            else target.weight
                        )
                    }
                )
                for target_index, target in enumerate(provider_targets)
            ]

        targets_snapshot: tuple[tuple[str, int, int], ...] = tuple(sorted((target.ip, target.port, target.weight) for target in targets))
        if targets_snapshot != cls._last_seen:
            logger.info("Target set changed: {}", targets_snapshot)

        if targets_snapshot != cls._last_sent:
            try:
                reload_response: Response = session.put(
                    url=settings.lb_targets_url,
                    json=routing.model_copy(update={"targets": targets}).model_dump(mode="json"),
                    timeout=settings.request_timeout_seconds
                )

                reload_response.raise_for_status()
            except (requests.RequestException, OSError):
                logger.exception("Failed to reload load balancer")
            else:
                cls._last_sent = targets_snapshot
                logger.info("Reloaded load balancer with {} targets", len(targets_snapshot))

        cls._last_seen = targets_snapshot

    @classmethod
    def close(cls) -> None:
        session = cls._session
        if session is not None:
            session.close()
            cls._session = None
