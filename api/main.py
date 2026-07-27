"""
AIShield API entrypoint.

Phase 0: health check only, proves the service boots and is containerizable.
Phase 3 will add /predict once the model layer exists.
"""
from fastapi import FastAPI

from configs.settings import settings
from src.utils.logger import get_logger

logger = get_logger(__name__)

app = FastAPI(
    title=settings.app_name,
    description="Real-time fraud detection microservice",
    version="0.1.0",
)


@app.get("/health", tags=["system"])
def health_check() -> dict:
    """Liveness/readiness probe target for Kubernetes."""
    return {"status": "ok", "app": settings.app_name, "environment": settings.environment}


@app.get("/", tags=["system"])
def root() -> dict:
    return {"message": f"{settings.app_name} API is running. See /docs for endpoints."}


logger.info("AIShield API initialized (environment=%s)", settings.environment)
