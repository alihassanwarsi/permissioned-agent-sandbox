from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    groq_api_key: str | None = None
    groq_model: str = "openai/gpt-oss-120b"

    tavily_api_key: str | None = None
    
    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()