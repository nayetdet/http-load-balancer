from __future__ import annotations

import yaml
from threading import Lock
from typing import TYPE_CHECKING
from loguru import logger
from http_load_balancer.algorithms.base_algorithm import BaseAlgorithm
from http_load_balancer.core.target_stats_manager import TargetStatsManager
from http_load_balancer.schemas.target_schema import TargetSchema

if TYPE_CHECKING:
    from http_load_balancer.enums.algorithm_strategy import AlgorithmStrategy
    from http_load_balancer.schemas.routing_schema import RoutingSchema

class TargetManager:
    _lock = Lock()
    _version: int = 1
    _algorithm_strategy: AlgorithmStrategy | None = None
    _targets: set[TargetSchema] = set()

    @classmethod
    def targets(cls) -> set[TargetSchema]:
        with cls._lock:
            return {target.model_copy(deep=True) for target in cls._targets}

    @classmethod
    def algorithm_strategy(cls) -> AlgorithmStrategy:
        with cls._lock:
            if cls._algorithm_strategy is None:
                raise RuntimeError("TargetManager must be initialized before algorithm strategy lookup")
            return cls._algorithm_strategy

    @classmethod
    def algorithm(cls) -> type[BaseAlgorithm]:
        return cls.algorithm_strategy().algorithm

    @classmethod
    def update(cls, payload: RoutingSchema | None = None) -> None:
        try:
            from http_load_balancer.settings import settings
            from http_load_balancer.schemas.routing_schema import RoutingSchema

            routing: RoutingSchema = payload if payload is not None else RoutingSchema()
            settings.settings_file_path.write_text(
                yaml.safe_dump(routing.model_dump(mode="json"), sort_keys=False),
                encoding="utf-8"
            )

            with cls._lock:
                cls._version = routing.version
                cls._targets = {target.model_copy(deep=True) for target in routing.targets}
                cls._algorithm_strategy = routing.algorithm_strategy
                TargetStatsManager.update()
        except Exception:
            logger.exception("Failed to update routing payload")
        else:
            logger.info("Routing payload updated")

    @classmethod
    def reload(cls, *_: object) -> None:
        try:
            from http_load_balancer.settings import settings
            from http_load_balancer.schemas.routing_schema import RoutingSchema

            routing: RoutingSchema = RoutingSchema.model_validate(yaml.safe_load(settings.settings_file_path.read_text(encoding="utf-8")) or {})
            with cls._lock:
                cls._version = routing.version
                cls._targets = {target.model_copy(deep=True) for target in routing.targets}
                cls._algorithm_strategy = routing.algorithm_strategy
                TargetStatsManager.update()
        except Exception:
            logger.exception("Failed to reload routing payload")
        else:
            logger.info("Routing payload reloaded")
