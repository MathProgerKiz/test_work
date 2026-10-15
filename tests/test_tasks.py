import asyncio
import os
import unittest
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, call, patch

with patch.dict(
    os.environ,
    {
        "DATABASE_URL": "postgresql+psycopg://user:pass@localhost/test",
        "CELERY_BROKER_URL": "redis://localhost:6379/0",
        "CELERY_RESULT_BACKEND": "redis://localhost:6379/1",
    },
):
    from app import tasks


class FetchAndSavePricesTests(unittest.TestCase):
    def test_engine_is_disposed_after_success_and_database_error(self):
        engines = [MagicMock(), MagicMock()]
        for engine in engines:
            engine.dispose = AsyncMock()

        session_factory = MagicMock()
        session_factory.begin.return_value.__aenter__.return_value = MagicMock()
        repository = MagicMock()
        repository.create_index_price = AsyncMock(
            side_effect=[None, None, RuntimeError("database write failed")]
        )
        deribit = MagicMock()
        deribit.get_index_price = AsyncMock(return_value=Decimal("1.00"))

        with (
            patch("app.tasks.aiohttp.ClientSession"),
            patch("app.tasks.DeribitClient", return_value=deribit),
            patch("app.tasks.IndexPriceRepository", return_value=repository),
            patch(
                "app.tasks.create_async_engine", side_effect=engines
            ) as create_engine,
            patch(
                "app.tasks.async_sessionmaker", return_value=session_factory
            ) as maker,
            patch("app.tasks.time.time", side_effect=[125, 130]),
        ):
            asyncio.run(tasks.fetch_and_save_prices())
            with self.assertRaisesRegex(RuntimeError, "database write failed"):
                asyncio.run(tasks.fetch_and_save_prices())

        self.assertEqual(create_engine.call_count, 2)
        self.assertEqual(
            maker.call_args_list,
            [
                call(engines[0], expire_on_commit=False),
                call(engines[1], expire_on_commit=False),
            ],
        )
        engines[0].dispose.assert_awaited_once()
        engines[1].dispose.assert_awaited_once()
        self.assertEqual(
            [
                call.kwargs["timestamp"]
                for call in repository.create_index_price.call_args_list
            ],
            [120, 120, 120],
        )
