from http_load_balancer.schemas import TargetSchema

class TargetManager:
    @classmethod
    def targets(cls) -> list[TargetSchema]:
        return []
