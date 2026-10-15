from contextlib import asynccontextmanager
from dishka.integrations.fastapi import setup_dishka

from dishka import make_async_container
from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from app.api.v1 import index_price_api
from app.core.dependency import AppProvider

container = make_async_container(AppProvider())


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await container.close()


app = FastAPI(
    title="Test Work API",
    description="API for reading BTC and ETH index prices collected from Deribit.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    swagger_ui_parameters={
        "displayRequestDuration": True,
        "filter": True,
    },
    lifespan=lifespan,
)

setup_dishka(
    container=container,
    app=app,
)


@app.get("/", include_in_schema=False)
async def swagger_redirect() -> RedirectResponse:
    return RedirectResponse(url=app.docs_url)


app.include_router(index_price_api.router, prefix="/api/v1")
