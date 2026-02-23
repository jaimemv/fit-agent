import os
from typing import Literal

from pydantic import BaseModel


class Settings(BaseModel):
    app_name: str = os.getenv("APP_NAME", "fit-agents-v1")
    app_env: str = os.getenv("APP_ENV", "dev")
    storage_backend: Literal["memory", "sqlite"] = os.getenv("APP_STORAGE", "memory")
    sqlite_path: str = os.getenv("SQLITE_PATH", "./data/fit_agents.db")


settings = Settings()
