from fastapi import FastAPI

from app.api.router import api_v1_router
from app.core.config import settings


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        openapi_url=f'{settings.API_V1_STR}/openapi.json',
        docs_url='/docs',
        contact={
            'name': settings.CONTACT_NAME,
            'email': settings.CONTACT_EMAIL,
        },

    )
    app.include_router(
        api_v1_router,
        prefix=settings.API_V1_STR,
        tags=['v1'],
    )
    return app


app = create_app()
