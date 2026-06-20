from abc import ABC, abstractmethod
from http_load_balancer_from_scratch.core.kubernetes_client import KubernetesClient
from http_load_balancer_from_scratch.schemas.route_schema import RouteSchema

class BaseAlgorithm(ABC):
    @abstractmethod
    def next_route(self) -> RouteSchema:
        ...

    @staticmethod
    def routes() -> list[RouteSchema]:
        return KubernetesClient.routes()
