from aep_common.app import create_platform_app
from fastapi import FastAPI

from metadata_engine.api.platform_objects import router as platform_objects_router
from metadata_engine.config import Settings

settings = Settings()


def create_app() -> FastAPI:
    app = create_platform_app(settings)
    app.include_router(platform_objects_router)
    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "metadata_engine.main:app",
        host=settings.host,
        port=settings.port,
        reload=False,
    )
