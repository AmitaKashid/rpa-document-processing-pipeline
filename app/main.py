from fastapi import FastAPI

from app.api.routes import router
from app.core.config import settings
from app.core.logging import configure_logging
from app.storage.audit_repository import init_db

configure_logging()
init_db()

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="Professional document-processing, data-validation, exception-routing, and RPA handoff pipeline.",
)
app.include_router(router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
