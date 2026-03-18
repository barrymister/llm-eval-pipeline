from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    mlflow_tracking_uri: str = "http://localhost:5000"
    ollama_base_url: str = "http://localhost:11434"
    anthropic_api_key: str = ""
    default_models: str = "gemma3:12b,mistral-small3.2"

    model_config = {"env_file": ".env"}

    @property
    def default_model_list(self) -> list[str]:
        return [m.strip() for m in self.default_models.split(",") if m.strip()]


settings = Settings()
