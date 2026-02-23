from fastapi import FastAPI

from app.api.routes import router as coach_router
from app.core.config import settings
from app.models.responses import HealthResponse

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="V1 multi-agent backend for personal training and nutrition coaching.",
)


@app.get("/health", response_model=HealthResponse, tags=["system"])
def health() -> HealthResponse:
    return HealthResponse(status="ok", app=settings.app_name, environment=settings.app_env)


app.include_router(coach_router)
