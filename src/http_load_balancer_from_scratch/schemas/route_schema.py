from pydantic import BaseModel

class RouteSchema(BaseModel):
    ip: str
    port: int
