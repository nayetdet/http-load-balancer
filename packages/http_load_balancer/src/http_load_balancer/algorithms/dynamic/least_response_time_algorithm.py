from http_load_balancer.algorithms.base_algorithm import BaseAlgorithm
from http_load_balancer.schemas import ConnectionSchema, TargetSchema

class LeastResponseTimeAlgorithm(BaseAlgorithm):
    @classmethod
    def next_target(cls, _: ConnectionSchema) -> TargetSchema:
        targets: list[TargetSchema] = cls.targets()
        return min(
            enumerate(targets),
            key=lambda item: (cls.target_stats(item[1].key()).response_time, item[0])
        )[1]
