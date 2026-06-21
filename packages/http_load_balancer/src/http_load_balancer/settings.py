from pydantic_settings import BaseSettings, SettingsConfigDict
from http_load_balancer.enums.algorithm_strategy import AlgorithmStrategy

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # Algorithms
    ALGORITHM: AlgorithmStrategy = AlgorithmStrategy.ROUND_ROBIN

    # Kubernetes
    KUBERNETES_DEPLOYMENT_NAME: str
    KUBERNETES_DEPLOYMENT_APP_NAME: str
    KUBERNETES_NAMESPACE: str = "default"

settings = Settings()
