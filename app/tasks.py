import asyncio
import time

import aiohttp
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.exc import SQLAlchemyError

from app.core.celery_app import celery_app
from app.core.config import DatabaseSettings
from app.repositories.index_price import IndexPriceRepository
from app.service.deribit_client import DeribitClient, DeribitClientError


def minute_start(timestamp: int | float) -> int:
    return int(timestamp) // 60 * 60


async def fetch_and_save_prices(timestamp: int | None = None):
    collection_timestamp = minute_start(time.time() if timestamp is None else timestamp)
    timeout = aiohttp.ClientTimeout(total=10)

    async with aiohttp.ClientSession(timeout=timeout) as http_session:
        deribit = DeribitClient(http_session)

        btc_price, eth_price = await asyncio.gather(
            deribit.get_index_price("btc_usd"),
            deribit.get_index_price("eth_usd"),
        )

    database_url = DatabaseSettings().database_url
    engine = create_async_engine(database_url, pool_pre_ping=True)
    try:
        session_factory = async_sessionmaker(engine, expire_on_commit=False)
        async with session_factory.begin() as db_session:
            repository = IndexPriceRepository(db_session)

            await repository.create_index_price(
                ticker="btc_usd",
                price=btc_price,
                timestamp=collection_timestamp,
            )
            await repository.create_index_price(
                ticker="eth_usd",
                price=eth_price,
                timestamp=collection_timestamp,
            )
    finally:
        await engine.dispose()


@celery_app.task(
    name="app.tasks.fetch_and_save_prices",
    bind=True,
)
def fetch_and_save_prices_task(self, timestamp: int | None = None):
    collection_timestamp = minute_start(time.time() if timestamp is None else timestamp)
    try:
        asyncio.run(fetch_and_save_prices(collection_timestamp))
    except (
        aiohttp.ClientError,
        asyncio.TimeoutError,
        DeribitClientError,
        SQLAlchemyError,
    ) as exc:
        countdown = min(2**self.request.retries, 30)
        raise self.retry(
            exc=exc,
            kwargs={"timestamp": collection_timestamp},
            countdown=countdown,
            max_retries=3,
        ) from exc
