from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24  # 24h

    github_client_id: str = ""
    github_client_secret: str = ""
    github_redirect_uri: str = "http://localhost:8000/auth/github/callback"
    frontend_url: str = "http://localhost:4200"

    ollama_url: str = "http://localhost:11434"
    ollama_model: str = "codellama:7b"  # choisi suite au benchmark comparatif

    class Config:
        env_file = ".env"


settings = Settings()
