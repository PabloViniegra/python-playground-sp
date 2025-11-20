from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Python Playground API"
    debug: bool = True
    api_prefix: str = "/api"

    database_url: str
    database_url_async: str

    secret_key: str
    algorithm: str = "HS256"

    code_execution_timeout: int = 5
    code_execution_memory_limit: int = 128
    max_concurrent_executions: int = 10

    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:4321"]

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()  # type: ignore[call-arg]
