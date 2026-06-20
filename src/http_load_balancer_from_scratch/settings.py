from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # Kubernetes
    KUBERNETES_DEPLOYMENT_NAME: str
    KUBERNETES_DEPLOYMENT_APP_NAME: str
    KUBERNETES_NAMESPACE: str = "default"

settings = Settings()
