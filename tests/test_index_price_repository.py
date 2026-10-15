from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.dialects import postgresql

from app.repositories.index_price import IndexPriceRepository


@pytest.mark.asyncio
async def test_duplicate_price_returns_existing_row():
    existing = object()
    db = MagicMock()
    db.scalars = AsyncMock(
        side_effect=[
            MagicMock(first=MagicMock(return_value=None)),
            MagicMock(first=MagicMock(return_value=existing)),
        ]
    )

    result = await IndexPriceRepository(db).create_index_price(
        "btc_usd", Decimal("123.45678912"), 120
    )

    assert result is existing
    assert db.scalars.await_count == 2
    statement = db.scalars.await_args_list[0].args[0]
    sql = str(statement.compile(dialect=postgresql.dialect()))
    assert (
        "ON CONFLICT ON CONSTRAINT uq_index_prices_ticker_timestamp DO NOTHING" in sql
    )
    assert statement.compile().params["price"] == Decimal("123.45678912")


@pytest.mark.asyncio
async def test_price_list_is_unlimited_by_default():
    db = MagicMock()
    db.scalars = AsyncMock(return_value=MagicMock(all=MagicMock(return_value=[])))
    repository = IndexPriceRepository(db)

    await repository.get_list_index_prices("btc_usd")
    all_rows_query = db.scalars.await_args.args[0]
    assert "LIMIT" not in str(all_rows_query.compile(dialect=postgresql.dialect()))

    await repository.get_list_index_prices("btc_usd", limit=25, offset=5)
    page_query = db.scalars.await_args.args[0]
    assert "LIMIT" in str(page_query.compile(dialect=postgresql.dialect()))
    assert page_query.compile().params["param_1"] == 25
