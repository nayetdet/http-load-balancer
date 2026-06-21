from pydantic import BaseModel

class TargetSchema(BaseModel):
    ip: str
    port: int
    weight: int = 1

    def key(self) -> str:
        return f"{self.ip}:{self.port}"
