import asyncio
import os
import unittest
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch

from sqlalchemy.dialects import postgresql


with patch.dict(
    os.environ,
    {
        "DATABASE_URL": "postgresql+psycopg://user:pass@localhost/test",
        "CELERY_BROKER_URL": "redis://localhost:6379/0",
        "CELERY_RESULT_BACKEND": "redis://localhost:6379/1",
    },
):
    from app.repositories.index_price import IndexPriceRepository


class IndexPriceRepositoryTests(unittest.TestCase):
    def test_duplicate_price_returns_existing_row(self):
        existing = object()
        db = MagicMock()
        db.scalars = AsyncMock(
            side_effect=[
                MagicMock(first=MagicMock(return_value=None)),
                MagicMock(first=MagicMock(return_value=existing)),
            ]
        )

        result = asyncio.run(
            IndexPriceRepository(db).create_index_price(
                "btc_usd", Decimal("123.45678912"), 120
            )
        )

        self.assertIs(result, existing)
        self.assertEqual(db.scalars.await_count, 2)
        statement = db.scalars.await_args_list[0].args[0]
        sql = str(statement.compile(dialect=postgresql.dialect()))
        self.assertIn(
            "ON CONFLICT ON CONSTRAINT uq_index_prices_ticker_timestamp DO NOTHING",
            sql,
        )
        self.assertEqual(statement.compile().params["price"], Decimal("123.45678912"))
