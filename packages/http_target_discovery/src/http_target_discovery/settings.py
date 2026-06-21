from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="DISCOVERY_",
        extra="ignore",
    )

    # Docker
    docker_target_label: str = "http-load-balancer.target"

    # Kubernetes
    kubernetes_deployment_app_name: str
    kubernetes_namespace: str = "default"

settings = Settings()
