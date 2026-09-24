from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    project_name: str = "Real-Time Local Information Engine"
    version: str = "0.1.0"

settings = Settings()
