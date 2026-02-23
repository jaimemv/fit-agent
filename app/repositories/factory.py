from app.core.config import Settings
from app.repositories.base import Repository
from app.repositories.memory import InMemoryRepository
from app.repositories.sqlite import SQLiteRepository


def build_repository(settings: Settings) -> Repository:
    if settings.storage_backend == "sqlite":
        return SQLiteRepository(db_path=settings.sqlite_path)
    return InMemoryRepository()
