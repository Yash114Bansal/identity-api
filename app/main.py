from fastapi import FastAPI
from app.api.routes import router as contact_router
from app.core.config import Config


def create_app() -> FastAPI:
    app = FastAPI(title=Config.APP_NAME)
    app.include_router(contact_router)
    return app

app = create_app()
