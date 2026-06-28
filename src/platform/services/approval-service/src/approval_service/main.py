from aep_common.app import create_platform_app
from fastapi import FastAPI

from approval_service.config import Settings

settings = Settings()


def create_app() -> FastAPI:
    return create_platform_app(settings)


app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "approval_service.main:app",
        host=settings.host,
        port=settings.port,
        reload=False,
    )
