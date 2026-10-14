import asyncio
import time

import aiohttp

from app.core.celery_app import celery_app
from app.core.db import get_session
from app.repositories.index_price import IndexPriceRepository
from app.service.deribit_client import DeribitClient



async def fetch_and_save_prices():
    timeout = aiohttp.ClientTimeout(total=10)

    async with aiohttp.ClientSession(timeout=timeout) as http_session:
        deribit = DeribitClient(http_session)

        btc_price, eth_price = await asyncio.gather(
            deribit.get_index_price("btc_usd"),
            deribit.get_index_price("eth_usd"),
        )

    timestamp = int(time.time())

    async with get_session() as db_session:
        repository = IndexPriceRepository(db_session)

        await repository.create(
            ticker="btc_usd",
            price=btc_price,
            timestamp=timestamp,
        )
        await repository.create(
            ticker="eth_usd",
            price=eth_price,
            timestamp=timestamp,
        )

        await db_session.commit()


@celery_app.task(name="app.tasks.prices.fetch_and_save_prices")
def fetch_and_save_prices_task():
    asyncio.run(fetch_and_save_prices())