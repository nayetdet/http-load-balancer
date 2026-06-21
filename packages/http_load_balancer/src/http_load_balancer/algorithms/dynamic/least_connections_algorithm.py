from http_load_balancer.algorithms.base_algorithm import BaseAlgorithm
from http_load_balancer.schemas.connection_schema import ConnectionSchema
from http_load_balancer.schemas.target_schema import TargetSchema

class LeastConnectionsAlgorithm(BaseAlgorithm):
    @classmethod
    def next_target(cls, _: ConnectionSchema) -> TargetSchema:
        targets: list[TargetSchema] = cls.targets()
        return min(
            enumerate(targets),
            key=lambda item: (cls.target_stats(item[1].key()).connections, item[0])
        )[1]
