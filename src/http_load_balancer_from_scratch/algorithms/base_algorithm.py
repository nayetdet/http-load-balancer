from abc import ABC, abstractmethod
from http_load_balancer_from_scratch.core.target_manager import TargetManager
from http_load_balancer_from_scratch.schemas.connection_schema import ConnectionSchema
from http_load_balancer_from_scratch.schemas.target_stats_schema import TargetStatsSchema
from http_load_balancer_from_scratch.schemas.target_schema import TargetSchema

class BaseAlgorithm(ABC):
    @classmethod
    @abstractmethod
    def next_target(cls, connection: ConnectionSchema) -> TargetSchema:
        ...

    @staticmethod
    def targets() -> list[TargetSchema]:
        from http_load_balancer_from_scratch.core.kubernetes_manager import KubernetesManager
        return KubernetesManager.targets()

    @staticmethod
    def target_stats(target_key: str) -> TargetStatsSchema:
        return TargetManager.get_stats(target_key)
