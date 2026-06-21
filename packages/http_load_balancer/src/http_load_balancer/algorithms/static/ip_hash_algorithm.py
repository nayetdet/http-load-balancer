import hashlib
from http_load_balancer.algorithms.base_algorithm import BaseAlgorithm
from http_load_balancer.schemas import ConnectionSchema, TargetSchema

class IPHashAlgorithm(BaseAlgorithm):
    @classmethod
    def next_target(cls, connection: ConnectionSchema) -> TargetSchema:
        targets: list[TargetSchema] = cls.targets()
        digest: bytes = hashlib.sha256(connection.client_ip.encode("utf-8")).digest()
        index: int = int.from_bytes(digest[:8], "big") % len(targets)
        return targets[index]
