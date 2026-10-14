from contextlib import asynccontextmanager
from dishka.integrations.fastapi import setup_dishka

from dishka import make_async_container
from fastapi import FastAPI
from app.core.dependency import AppProvider
from app.api.v1 import index_price_api


container = make_async_container(AppProvider())


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await container.close()


app = FastAPI(
    title="Test Work API",
    lifespan=lifespan,
)

setup_dishka(
    container=container,
    app=app,
)


app.include_router(index_price_api.router, prefix="/api/v1")
