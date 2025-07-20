from fastapi import FastAPI
from fastapi import Request
from fastapi.responses import JSONResponse
from app.api.routes import router as contact_router
from app.core.config import Config
from app.core.exceptions import AppException
from mangum import Mangum


def create_app() -> FastAPI:
    app = FastAPI(title=Config.APP_NAME)
    app.include_router(contact_router)

    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException):
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

    return app

app = create_app()
handler = Mangum(app)
