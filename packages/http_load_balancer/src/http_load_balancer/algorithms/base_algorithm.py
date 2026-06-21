from abc import ABC, abstractmethod
from http_load_balancer.core import TargetStatsManager
from http_load_balancer.schemas import ConnectionSchema, TargetSchema, TargetStatsSchema

class BaseAlgorithm(ABC):
    @classmethod
    @abstractmethod
    def next_target(cls, connection: ConnectionSchema) -> TargetSchema:
        ...

    @staticmethod
    def targets() -> list[TargetSchema]:
        from http_load_balancer.core import TargetManager
        return TargetManager.targets()

    @staticmethod
    def target_stats(target_key: str) -> TargetStatsSchema:
        return TargetStatsManager.stats(target_key)
