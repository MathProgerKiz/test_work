import asyncio
import time

import aiohttp
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.core.celery_app import celery_app
from app.core.config import settings
from app.repositories.index_price import IndexPriceRepository
from app.service.deribit_client import DeribitClient


async def fetch_and_save_prices():
    timestamp = int(time.time()) // 60 * 60
    timeout = aiohttp.ClientTimeout(total=10)

    async with aiohttp.ClientSession(timeout=timeout) as http_session:
        deribit = DeribitClient(http_session)

        btc_price, eth_price = await asyncio.gather(
            deribit.get_index_price("btc_usd"),
            deribit.get_index_price("eth_usd"),
        )

    engine = create_async_engine(settings.database_url, pool_pre_ping=True)
    try:
        session_factory = async_sessionmaker(engine, expire_on_commit=False)
        async with session_factory.begin() as db_session:
            repository = IndexPriceRepository(db_session)

            await repository.create_index_price(
                ticker="btc_usd",
                price=btc_price,
                timestamp=timestamp,
            )
            await repository.create_index_price(
                ticker="eth_usd",
                price=eth_price,
                timestamp=timestamp,
            )
    finally:
        await engine.dispose()


@celery_app.task(
    name="app.tasks.fetch_and_save_prices",
    autoretry_for=(aiohttp.ClientError, asyncio.TimeoutError),
    retry_backoff=True,
    retry_jitter=True,
    retry_kwargs={"max_retries": 3},
)
def fetch_and_save_prices_task():
    asyncio.run(fetch_and_save_prices())
