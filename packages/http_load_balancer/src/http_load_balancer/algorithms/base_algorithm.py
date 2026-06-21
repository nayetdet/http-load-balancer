from abc import ABC, abstractmethod
from http_load_balancer.core.target_manager import TargetManager
from http_load_balancer.schemas.connection_schema import ConnectionSchema
from http_load_balancer.schemas.target_stats_schema import TargetStatsSchema
from http_load_balancer.schemas.target_schema import TargetSchema

class BaseAlgorithm(ABC):
    @classmethod
    @abstractmethod
    def next_target(cls, connection: ConnectionSchema) -> TargetSchema:
        ...

    @staticmethod
    def targets() -> list[TargetSchema]:
        from http_load_balancer.core.kubernetes_manager import KubernetesManager
        return KubernetesManager.targets()

    @staticmethod
    def target_stats(target_key: str) -> TargetStatsSchema:
        return TargetManager.get_stats(target_key)
