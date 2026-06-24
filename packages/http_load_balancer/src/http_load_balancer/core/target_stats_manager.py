from collections import defaultdict
from threading import Lock
from http_load_balancer.schemas.target_stats_schema import TargetStatsSchema
from http_load_balancer.settings import settings

class TargetStatsManager:
    _lock = Lock()
    _stats: defaultdict[str, TargetStatsSchema] = defaultdict(TargetStatsSchema)

    @classmethod
    def all_stats(cls) -> dict[str, TargetStatsSchema]:
        with cls._lock:
            return {
                target_key: stats.model_copy(deep=True)
                for target_key, stats in cls._stats.items()
            }

    @classmethod
    def stats(cls, target_key: str) -> TargetStatsSchema:
        with cls._lock:
            return cls._stats.get(target_key, TargetStatsSchema()).model_copy(deep=True)

    @classmethod
    def increment_connections(cls, target_key: str) -> None:
        with cls._lock:
            cls._stats[target_key].connections += 1

    @classmethod
    def decrement_connections(cls, target_key: str) -> None:
        with cls._lock:
            stats = cls._stats[target_key]
            stats.connections = max(0, stats.connections - 1)

    @classmethod
    def update_response_time(cls, target_key: str, response_time: float) -> None:
        with cls._lock:
            stats: TargetStatsSchema = cls._stats[target_key]
            stats.response_time = (
                response_time
                if stats.response_time <= 0
                else stats.response_time * (1 - settings.response_time_alpha) + response_time * settings.response_time_alpha
            )

    @classmethod
    def update(cls, stats: dict[str, TargetStatsSchema] | None = None) -> None:
        with cls._lock:
            cls._stats = defaultdict(
                TargetStatsSchema,
                {
                    target_key: target_stats.model_copy(deep=True)
                    for target_key, target_stats in (stats or {}).items()
                }
            )
