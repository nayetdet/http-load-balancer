from pydantic_settings import BaseSettings, SettingsConfigDict
from http_load_balancer.enums import AlgorithmStrategy

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="LB_",
        extra="ignore"
    )

    HOST: str = "127.0.0.1"
    PORT: int = 8080
    BUFFER_SIZE: int = 4096
    BACKLOG: int = 128
    ALGORITHM: AlgorithmStrategy = AlgorithmStrategy.ROUND_ROBIN

settings = Settings()
